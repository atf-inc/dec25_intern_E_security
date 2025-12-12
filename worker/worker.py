# TODO: Description of this file
# Status: Not Started
"""
ShadowGuard AI Worker - Main Detection Engine
Orchestrates Rule Engine, Semantic Engine, Behavior Engine, and Risk Fusion
Processes logs from Redis and publishes alerts
"""

import redis
import json
import time
import logging
import signal
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Import detection engines
from rules import RuleEngine
from semantic import SemanticEngine  
from behavior import BehaviorEngine
from fusion import RiskFusion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ShadowGuardWorker:
    def __init__(self, redis_host: str = "redis", redis_port: int = 6379):
        """
        Initialize the ShadowGuard AI Worker.
        
        Args:
            redis_host: Redis server hostname (default "redis" for Docker)
            redis_port: Redis server port
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        
        # Redis channels based on your PRD
        self.input_channel = "logs_input"      # Channel to read logs from collector
        self.alert_channel = "alerts"          # Channel to publish alerts for dashboard
        
        # Redis connections
        self.redis_client = None
        self.pubsub = None
        
        # Detection engines
        self.rule_engine = None
        self.semantic_engine = None
        self.behavior_engine = None
        self.fusion_engine = None
        
        # Worker statistics
        self.running = False
        self.processed_count = 0
        self.alert_count = 0
        self.start_time = None
        
        # Graceful shutdown handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def initialize(self):
        """Initialize all worker components."""
        logger.info("=" * 50)
        logger.info("🚀 Starting ShadowGuard AI Worker Initialization")
        logger.info("=" * 50)
        
        self.start_time = datetime.now()
        
        try:
            # Step 1: Connect to Redis
            self._connect_redis()
            
            # Step 2: Initialize all detection engines
            self._initialize_engines()
            
            # Step 3: Final validation
            self._validate_initialization()
            
            logger.info("✅ Worker initialization completed successfully!")
            logger.info(f"🔍 Ready to process logs from channel: {self.input_channel}")
            logger.info(f"🚨 Will publish alerts to channel: {self.alert_channel}")
            
        except Exception as e:
            logger.error(f"❌ Worker initialization failed: {e}")
            raise
    
    def _connect_redis(self):
        """Establish Redis connection and set up pub/sub."""
        logger.info("📡 Connecting to Redis...")
        
        try:
            # Main Redis client for publishing alerts
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=0,  # Use default DB for pub/sub
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")
            
            # Set up pub/sub for listening to logs
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(self.input_channel)
            
            # Consume the subscription confirmation message
            msg = self.pubsub.get_message(timeout=1)
            if msg and msg['type'] == 'subscribe':
                logger.info(f"✅ Subscribed to logs channel: {self.input_channel}")
            
        except redis.ConnectionError as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            logger.error("💡 Make sure Redis is running and accessible")
            raise
        except Exception as e:
            logger.error(f"❌ Redis setup error: {e}")
            raise
    
    def _initialize_engines(self):
        """Initialize all detection engines with progress tracking."""
        logger.info("🧠 Loading AI Detection Engines...")
        
        # Engine 1: Rule Engine (Fast)
        try:
            logger.info("  📋 Loading Rule Engine...")
            self.rule_engine = RuleEngine()
            logger.info("  ✅ Rule Engine ready")
        except Exception as e:
            logger.error(f"  ❌ Rule Engine failed: {e}")
            raise
        
        # Engine 2: Semantic Engine (May take time for model download)
        try:
            logger.info("  🤖 Loading Semantic Engine (AI model)...")
            logger.info("     ⏳ Downloading model if first run (~200MB, 30 seconds)...")
            self.semantic_engine = SemanticEngine()
            logger.info("  ✅ Semantic Engine ready")
        except Exception as e:
            logger.error(f"  ❌ Semantic Engine failed: {e}")
            logger.error("     💡 Check internet connection for model download")
            raise
        
        # Engine 3: Behavior Engine
        try:
            logger.info("  👤 Loading Behavior Engine...")
            self.behavior_engine = BehaviorEngine(
                redis_host=self.redis_host,
                redis_port=self.redis_port,
                redis_db=2  # Separate DB for behavior data
            )
            logger.info("  ✅ Behavior Engine ready")
        except Exception as e:
            logger.error(f"  ❌ Behavior Engine failed: {e}")
            raise
        
        # Engine 4: Risk Fusion Engine
        try:
            logger.info("  ⚖️ Loading Risk Fusion Engine...")
            self.fusion_engine = RiskFusion(
                weights={'rule': 0.30, 'semantic': 0.50, 'behavior': 0.20},
                risk_threshold=0.75
            )
            logger.info("  ✅ Risk Fusion Engine ready")
        except Exception as e:
            logger.error(f"  ❌ Risk Fusion Engine failed: {e}")
            raise
    
    def _validate_initialization(self):
        """Validate all components are properly initialized."""
        components = [
            (self.redis_client, "Redis Client"),
            (self.pubsub, "Redis Pub/Sub"),
            (self.rule_engine, "Rule Engine"),
            (self.semantic_engine, "Semantic Engine"),
            (self.behavior_engine, "Behavior Engine"),
            (self.fusion_engine, "Fusion Engine")
        ]
        
        for component, name in components:
            if component is None:
                raise Exception(f"{name} not properly initialized")
        
        logger.info("✅ All components validated successfully")
    
    def _process_log_event(self, log_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single log event through the 4-stage detection pipeline.
        
        Args:
            log_data: Dictionary containing log event from collector
            
        Returns:
            Alert payload if alert should be generated, None otherwise
        """
        try:
            # Validate required fields
            required_fields = ['ts', 'user_id', 'domain', 'url', 'method']
            missing_fields = [f for f in required_fields if f not in log_data]
            
            if missing_fields:
                logger.warning(f"Missing required fields: {missing_fields}")
                return None
            
            domain = log_data['domain']
            user_id = log_data['user_id']
            timestamp = log_data['ts']
            
            logger.debug(f"🔍 Processing: {user_id} -> {domain}")
            
            # STAGE 1: Rule Engine Analysis
            start_time = time.time()
            rule_result = self.rule_engine.analyze(log_data)
            rule_time = (time.time() - start_time) * 1000
            
            logger.debug(f"📋 Rule score: {rule_result['rule_score']:.3f} ({rule_time:.1f}ms)")
            
            # STAGE 2: Semantic Engine Analysis (AI)
            start_time = time.time()
            semantic_result = self.semantic_engine.analyze(log_data)
            semantic_time = (time.time() - start_time) * 1000
            
            logger.debug(f"🤖 Semantic score: {semantic_result['semantic_score']:.3f} ({semantic_time:.1f}ms)")
            
            # STAGE 3: Behavior Engine Analysis
            start_time = time.time()
            behavior_result = self.behavior_engine.analyze(log_data)
            behavior_time = (time.time() - start_time) * 1000
            
            logger.debug(f"👤 Behavior score: {behavior_result['behavior_score']:.3f} ({behavior_time:.1f}ms)")
            
            # STAGE 4: Risk Fusion
            start_time = time.time()
            fusion_result = self.fusion_engine.analyze(
                log_data, rule_result, semantic_result, behavior_result
            )
            fusion_time = (time.time() - start_time) * 1000
            
            final_score = fusion_result['final_score']
            should_alert = fusion_result['should_alert']
            risk_level = fusion_result['risk_level']
            
            # Log processing result
            total_time = rule_time + semantic_time + behavior_time + fusion_time
            
            logger.info(
                f"🎯 {domain} | {user_id} | Score: {final_score:.3f} | "
                f"Risk: {risk_level} | Alert: {'YES' if should_alert else 'NO'} | "
                f"Time: {total_time:.1f}ms"
            )
            
            # Return alert payload if alert should be generated
            if should_alert:
                return fusion_result.get('alert_payload')
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error processing log event: {e}")
            logger.error(f"   Log data: {log_data}")
            return None
    
    def _publish_alert(self, alert_payload: Dict[str, Any]):
        """Publish alert to Redis alert channel for dashboard consumption."""
        try:
            # Add worker metadata to alert
            alert_payload['worker_metadata'] = {
                'worker_id': f"worker-{int(time.time())}",
                'processed_at': datetime.utcnow().isoformat() + 'Z',
                'processing_stats': {
                    'total_processed': self.processed_count,
                    'total_alerts': self.alert_count + 1
                }
            }
            
            # Serialize and publish
            alert_json = json.dumps(alert_payload, indent=2)
            result = self.redis_client.publish(self.alert_channel, alert_json)
            
            # Extract alert info for logging
            alert_id = alert_payload.get('alert_id', 'unknown')
            domain = alert_payload.get('metadata', {}).get('domain', 'unknown')
            user = alert_payload.get('metadata', {}).get('user_id', 'unknown')
            score = alert_payload.get('risk_assessment', {}).get('final_score', 0)
            explanation = alert_payload.get('risk_assessment', {}).get('explanation', '')
            
            logger.warning(f"🚨 ALERT PUBLISHED: {alert_id}")
            logger.warning(f"   Domain: {domain}")
            logger.warning(f"   User: {user}")
            logger.warning(f"   Score: {score:.3f}")
            logger.warning(f"   Reason: {explanation}")
            logger.warning(f"   Subscribers notified: {result}")
            
            self.alert_count += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to publish alert: {e}")
    
    def _handle_message(self, message):
        """Handle incoming Redis message from logs_input channel."""
        try:
            if message['type'] != 'message':
                return
            
            # Parse log data from collector
            try:
                log_data = json.loads(message['data'])
            except json.JSONDecodeError:
                logger.error("❌ Invalid JSON in log message")
                return
            
            # Process through detection pipeline
            alert_payload = self._process_log_event(log_data)
            
            # Publish alert if generated
            if alert_payload:
                self._publish_alert(alert_payload)
            
            self.processed_count += 1
            
            # Log progress periodically
            if self.processed_count % 50 == 0:
                uptime = datetime.now() - self.start_time if self.start_time else None
                logger.info(f"📊 Processed {self.processed_count} logs, "
                          f"generated {self.alert_count} alerts "
                          f"(uptime: {uptime})")
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
    def run(self):
        """Main worker loop - listen for logs and process them."""
        if not all([self.redis_client, self.rule_engine, self.semantic_engine, 
                   self.behavior_engine, self.fusion_engine]):
            logger.error("❌ Worker not properly initialized")
            return False
        
        logger.info("=" * 50)
        logger.info("🟢 ShadowGuard AI Worker STARTED")
        logger.info("=" * 50)
        logger.info(f"📡 Listening: {self.input_channel}")
        logger.info(f"📤 Publishing: {self.alert_channel}")
        logger.info("🔄 Processing logs... (Ctrl+C to stop)")
        
        self.running = True
        
        try:
            # Main processing loop
            while self.running:
                try:
                    # Get message with timeout to allow graceful shutdown
                    message = self.pubsub.get_message(timeout=1.0)
                    
                    if message:
                        self._handle_message(message)
                    
                except redis.ConnectionError:
                    logger.error("❌ Lost connection to Redis, attempting to reconnect...")
                    time.sleep(5)
                    try:
                        self._connect_redis()
                        logger.info("✅ Reconnected to Redis")
                    except Exception as e:
                        logger.error(f"❌ Reconnection failed: {e}")
                        break
                
        except KeyboardInterrupt:
            logger.info("⏹️ Received shutdown signal")
        except Exception as e:
            logger.error(f"❌ Worker error: {e}")
        finally:
            self.stop()
            
        return True
    
    def stop(self):
        """Stop the worker gracefully."""
        if not self.running:
            return
            
        logger.info("🔄 Stopping ShadowGuard AI Worker...")
        
        self.running = False
        
        # Close Redis connections
        if self.pubsub:
            try:
                self.pubsub.close()
                logger.info("✅ Closed Redis pub/sub connection")
            except Exception as e:
                logger.error(f"❌ Error closing pub/sub: {e}")
        
        if self.redis_client:
            try:
                self.redis_client.close()
                logger.info("✅ Closed Redis client connection")
            except Exception as e:
                logger.error(f"❌ Error closing Redis client: {e}")
        
        # Final statistics
        uptime = datetime.now() - self.start_time if self.start_time else None
        logger.info("=" * 50)
        logger.info("📊 FINAL STATISTICS")
        logger.info(f"⏱️ Uptime: {uptime}")
        logger.info(f"📝 Logs processed: {self.processed_count}")
        logger.info(f"🚨 Alerts generated: {self.alert_count}")
        logger.info(f"📈 Alert rate: {(self.alert_count/max(self.processed_count,1)*100):.1f}%")
        logger.info("🛑 ShadowGuard AI Worker STOPPED")
        logger.info("=" * 50)

def test_worker():
    """Test the worker with sample data (offline mode)."""
    logger.info("🧪 Testing ShadowGuard Worker (Offline Mode)")
    
    # Create worker but don't connect to Redis for testing
    worker = ShadowGuardWorker()
    
    # Initialize only the detection engines
    try:
        worker._initialize_engines()
        logger.info("✅ All detection engines loaded for testing")
    except Exception as e:
        logger.error(f"❌ Engine initialization failed: {e}")
        return
    
    # Test with sample logs
    test_logs = [
        {
            'ts': '2025-12-12T10:30:00Z',
            'user_id': 'alice@company.com',
            'domain': 'github.com',
            'url': '/user/repo',
            'method': 'GET',
            'upload_size_bytes': 1024
        },
        {
            'ts': '2025-12-12T14:30:00Z',
            'user_id': 'bob@company.com',
            'domain': 'stealth-ai-writer.io',
            'url': '/api/chat',
            'method': 'POST',
            'upload_size_bytes': 5242880
        },
        {
            'ts': '2025-12-12T23:45:00Z',
            'user_id': 'charlie@company.com',
            'domain': 'temp-file-share.com',
            'url': '/upload/anonymous',
            'method': 'POST',
            'upload_size_bytes': 15728640
        }
    ]
    
    logger.info("🔍 Processing test logs...")
    
    alerts = []
    for i, log in enumerate(test_logs, 1):
        logger.info(f"\n--- Test {i}: {log['domain']} ---")
        
        alert = worker._process_log_event(log)
        if alert:
            alerts.append(alert)
            print(f"🚨 ALERT: {alert['alert_id']}")
            print(f"   Risk: {alert['risk_assessment']['final_score']:.3f}")
            print(f"   Reason: {alert['risk_assessment']['explanation']}")
    
    logger.info(f"\n🎯 Test Results: {len(alerts)} alerts generated from {len(test_logs)} logs")
    
    if alerts:
        logger.info("✅ Detection pipeline working correctly!")
    else:
        logger.warning("⚠️ No alerts generated - check thresholds")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode (no Redis required)
        test_worker()
    else:
        # Production mode (requires Redis)
        worker = ShadowGuardWorker()
        try:
            worker.initialize()
            success = worker.run()
            sys.exit(0 if success else 1)
        except Exception as e:
            logger.error(f"❌ Worker failed to start: {e}")
            sys.exit(1)