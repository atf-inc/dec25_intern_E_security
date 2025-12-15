"""
Worker (core of detection system)
The brain of the detection system that orchestrates all analysis engines.
"""

import json
import os
import signal
import sys
import time
from datetime import datetime
from typing import Optional

import redis

from behavior import BehaviorEngine
from semantic import OpenRouterSimilarityDetector

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
EVENTS_CHANNEL = "events"
ALERT_THRESHOLD = 0.7
PERFORMANCE_TARGET_MS = 500


class ShadowGuardWorker:

    def __init__(self):
        self._running = False
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._semantic_engine: Optional[OpenRouterSimilarityDetector] = None
        self._behavior_engine: Optional[BehaviorEngine] = None
        self._processed_count = 0
        self._alert_count = 0

    def _setup_signal_handlers(self):
        """Register handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        sig_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        print(f"\n[SHUTDOWN] Received {sig_name}, stopping worker...")
        self._running = False

    def _connect_redis(self) -> bool:
        """Establish Redis connection with retry logic."""
        max_retries = 5
        retry_delay = 2

        for attempt in range(1, max_retries + 1):
            try:
                print(f"[REDIS] Connecting to {REDIS_HOST}:{REDIS_PORT} (attempt {attempt}/{max_retries})")
                self._redis = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True
                )
                self._redis.ping()
                print(f"[REDIS] Connected successfully")
                return True
            except redis.ConnectionError as e:
                print(f"[REDIS] Connection failed: {e}")
                if attempt < max_retries:
                    print(f"[REDIS] Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2

        print("[REDIS] Failed to connect after all retries")
        return False

    def _subscribe_to_channel(self) -> bool:
        try:
            self._pubsub = self._redis.pubsub()
            self._pubsub.subscribe(EVENTS_CHANNEL)
            print(f"[REDIS] Subscribed to '{EVENTS_CHANNEL}' channel")
            return True
        except redis.RedisError as e:
            print(f"[REDIS] Subscription failed: {e}")
            return False

    def _init_engines(self) -> bool:
        try:
            print("[ENGINE] Initializing Semantic Engine...")
            self._semantic_engine = OpenRouterSimilarityDetector()
            print("[ENGINE] Semantic Engine ready")

            print("[ENGINE] Initializing Behavior Engine...")
            self._behavior_engine = BehaviorEngine(host=REDIS_HOST, port=REDIS_PORT)
            print("[ENGINE] Behavior Engine ready")

            # Future: Initialize Rules Engine here
            # self._rules_engine = RulesEngine()

            return True
        except Exception as e:
            print(f"[ENGINE] Initialization failed: {e}")
            return False

    def _process_log(self, log_data: dict) -> dict:
        """
        Process a single log through all detection engines.
        Returns combined analysis result.
        """
        domain = log_data.get("domain", "")
        user_id = log_data.get("user_id", "")

        # Semantic analysis
        semantic_result = self._semantic_engine.analyze(domain)

        # Behavior analysis
        behavior_result = self._behavior_engine.analyze(user_id, domain)

        # Future: Rules engine analysis
        # rules_result = self._rules_engine.analyze(domain)

        # Combine scores - weighted average
        # Semantic: 60%, Behavior: 40%
        combined_score = (
            semantic_result["risk_score"] * 0.6 +
            behavior_result["behavior_score"] * 0.4
        )

        return {
            "domain": domain,
            "user_id": user_id,
            "combined_risk_score": round(combined_score, 3),
            "semantic": {
                "risk_score": semantic_result["risk_score"],
                "category": semantic_result["top_category"],
                "explanation": semantic_result["explanation"]
            },
            "behavior": {
                "score": behavior_result["behavior_score"],
                "is_first_visit": behavior_result["is_first_visit"],
                "reason": behavior_result["reason"]
            }
        }

    def _format_alert(self, result: dict, log_data: dict, processing_time_ms: float) -> str:
        """Format an alert message for high-risk detections."""
        ts = log_data.get("ts", datetime.now().isoformat())
        upload_size = log_data.get("upload_size_bytes", 0)

        # Alert: High-risk detection
        alert = f"""
Timestamp       : {ts}
User            : {result['user_id']}
Domain          : {result['domain']}
Upload Size     : {upload_size:,} bytes

RISK ASSESSMENT
  Combined Score: {result['combined_risk_score']:.2f} {'[HIGH RISK]' if result['combined_risk_score'] > ALERT_THRESHOLD else ''}
  
  Semantic Analysis:
    - Score     : {result['semantic']['risk_score']:.2f}
    - Category  : {result['semantic']['category']}
    - Reason    : {result['semantic']['explanation']}
  
  Behavior Analysis:
    - Score     : {result['behavior']['score']:.2f}
    - First Visit: {result['behavior']['is_first_visit']}
    - Reason    : {result['behavior']['reason']}

Processing Time : {processing_time_ms:.1f}ms {'[OK]' if processing_time_ms < PERFORMANCE_TARGET_MS else '[SLOW]'}
"""
        return alert

    def _log_processed(self, result: dict, processing_time_ms: float):
        """Log a processed event (non-alert)."""
        status = "OK" if processing_time_ms < PERFORMANCE_TARGET_MS else "SLOW"
        print(
            f"[PROCESSED] {result['domain']} | "
            f"user={result['user_id']} | "
            f"risk={result['combined_risk_score']:.2f} | "
            f"time={processing_time_ms:.1f}ms [{status}]"
        )

    def _handle_message(self, message: dict):
        """Handle a single message from Redis."""
        if message["type"] != "message":
            return

        start_time = time.perf_counter()

        try:
            log_data = json.loads(message["data"])
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return

        domain = log_data.get("domain")
        if not domain:
            print("[WARN] Log missing domain, skipping")
            return

        try:
            result = self._process_log(log_data)
        except Exception as e:
            print(f"[ERROR] Processing failed: {e}")
            return

        processing_time_ms = (time.perf_counter() - start_time) * 1000
        self._processed_count += 1

        # Output based on risk level
        if result["combined_risk_score"] > ALERT_THRESHOLD:
            self._alert_count += 1
            print(self._format_alert(result, log_data, processing_time_ms))
        else:
            self._log_processed(result, processing_time_ms)

    def _cleanup(self):
        """Clean up resources on shutdown."""
        if self._pubsub:
            try:
                self._pubsub.unsubscribe()
                self._pubsub.close()
            except Exception:
                pass

        if self._redis:
            try:
                self._redis.close()
            except Exception:
                pass

        print(f"[STATS] Processed: {self._processed_count} | Alerts: {self._alert_count}")
        print("[SHUTDOWN] Worker stopped")

    def run(self):
        """Main entry point - start the worker."""
        print("=" * 60)
        print("         SHADOWGUARD AI - Detection Worker")
        print("=" * 60)

        self._setup_signal_handlers()

        # Initialize Redis connection
        if not self._connect_redis():
            sys.exit(1)

        # Initialize detection engines
        if not self._init_engines():
            sys.exit(1)

        # Subscribe to events channel
        if not self._subscribe_to_channel():
            sys.exit(1)

        print("-" * 60)
        print(f"[READY] Listening for events (alert threshold: {ALERT_THRESHOLD})")
        print("-" * 60)

        self._running = True

        try:
            while self._running:
                # Use get_message with timeout for responsive shutdown
                message = self._pubsub.get_message(timeout=1.0)
                if message:
                    self._handle_message(message)
        except redis.ConnectionError:
            print("[ERROR] Redis connection lost")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
        finally:
            self._cleanup()


def main():
    worker = ShadowGuardWorker()
    worker.run()


if __name__ == "__main__":
    main()
