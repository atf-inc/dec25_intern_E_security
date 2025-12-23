"""
Worker (core of detection system)
The brain of the detection system that orchestrates all analysis engines.
"""

import json
import os
import signal
import sys
import time
import uuid
from datetime import datetime
from typing import Optional
import redis
from behavior import BehaviorEngine
from semantic import ImprovedSemanticDetector
from fusion import ImprovedFusionEngine

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
        self._semantic_engine: Optional[ImprovedSemanticDetector] = None
        self._behavior_engine: Optional[BehaviorEngine] = None
        self._fusion_engine: Optional[ImprovedFusionEngine] = None
        self._processed_count = 0
        self._alert_count = 0

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        sig_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        print(f"\n[SHUTDOWN] Received {sig_name}, stopping worker...")
        self._running = False

    def _connect_redis(self) -> bool:
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
            self._semantic_engine = ImprovedSemanticDetector()
            print("[ENGINE] Semantic Engine ready")

            print("[ENGINE] Initializing Behavior Engine...")
            self._behavior_engine = BehaviorEngine(host=REDIS_HOST, port=REDIS_PORT)
            print("[ENGINE] Behavior Engine ready")

            print("[ENGINE] Initializing Fusion Engine...")
            self._fusion_engine = ImprovedFusionEngine()
            print("[ENGINE] Fusion Engine ready")

            return True
        except Exception as e:
            print(f"[ENGINE] Initialization failed: {e}")
            return False

    def _process_log(self, log_data: dict) -> dict:
        """Process a single log event through all analysis engines."""
        domain = log_data.get("domain", "")
        user_id = log_data.get("user_id", "")
        url = log_data.get("url", "")  # NEW: Extract URL
        method = log_data.get("method", "GET")  # NEW: Extract HTTP method
        upload_size_bytes = log_data.get("upload_size_bytes", 0)  # NEW: Extract upload size

        # Semantic analysis (with URL for content consumption detection)
        semantic_result = self._semantic_engine.analyze(domain, url)

        # Behavior analysis
        behavior_result = self._behavior_engine.analyze(user_id, domain)

        # Fuse results using context-aware FusionEngine
        fused_result = self._fusion_engine.fuse(
            domain=domain,
            user_id=user_id,
            url=url,
            method=method,
            upload_size_bytes=upload_size_bytes,
            behavior_result=behavior_result,
            semantic_result=semantic_result
        )

        return fused_result

    def _format_alert(self, result: dict, log_data: dict, processing_time_ms: float) -> str:
        ts = log_data.get("ts", datetime.now().isoformat())
        upload_size = log_data.get("upload_size_bytes", 0)

        # Use FusionEngine's built-in alert generator
        fusion_alert = self._fusion_engine.generate_alert(result)
        
        # Add additional context
        alert = f"""
Timestamp       : {ts}
Upload Size     : {upload_size:,} bytes
{fusion_alert}
Processing Time : {processing_time_ms:.1f}ms {'[OK]' if processing_time_ms < PERFORMANCE_TARGET_MS else '[SLOW]'}
"""
        return alert

    def _save_alert_to_redis(self, result: dict):
        """Save alert to Redis for backend consumption."""
        try:
            # Handle override vs normal analysis
            if result.get("override"):
                # Blacklisted/Whitelisted domain - use override data
                category = "Blacklisted" if result["final_risk_score"] > 0.5 else "Whitelisted"
                ai_message = result.get("override_reason", "No explanation")
            else:
                # Normal analysis - use semantic data
                category = result.get("semantic_analysis", {}).get("top_category", "unknown")
                ai_message = result.get("semantic_analysis", {}).get("explanation", "No analysis available")
            
            # Format alert for frontend
            alert = {
                "id": str(uuid.uuid4()),
                "risk_score": int(result["final_risk_score"] * 100),
                "user": result["user_id"],
                "department": "Unknown",
                "domain": result["domain"],
                "category": category,
                "status": "new",
                "timestamp": result["timestamp"],
                "ai_message": ai_message
            }
            
            # Push to Redis list
            self._redis.lpush("alerts", json.dumps(alert))
            
            # Trim list to last 1000 alerts to prevent memory issues
            self._redis.ltrim("alerts", 0, 999)
            
            print(f"[REDIS] Saved alert for {result['domain']} (risk: {result['final_risk_score']:.2f})")
            
        except Exception as e:
            print(f"[ERROR] Failed to save alert to Redis: {e}")
            import traceback
            traceback.print_exc()

    def _log_processed(self, result: dict, processing_time_ms: float):
        status = "OK" if processing_time_ms < PERFORMANCE_TARGET_MS else "SLOW"
        print(
            f"[PROCESSED] {result['domain']} | "
            f"user={result['user_id']} | "
            f"risk={result['final_risk_score']:.2f} ({result['risk_level']}) | "
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
        if result["final_risk_score"] > ALERT_THRESHOLD:
            self._alert_count += 1
            print(self._format_alert(result, log_data, processing_time_ms))
            # Save alert to Redis for dashboard
            self._save_alert_to_redis(result)
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

        if not self._connect_redis():
            sys.exit(1)

        if not self._init_engines():
            sys.exit(1)

        if not self._subscribe_to_channel():
            sys.exit(1)

        print("-" * 60)
        print(f"[READY] Listening for events (alert threshold: {ALERT_THRESHOLD})")
        print("-" * 60)

        self._running = True

        try:
            while self._running:
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