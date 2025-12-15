"""
Real-time Behavior Analysis Monitor
Listens to Redis events and runs behavior analysis
"""

import redis
import json
import os
from behavior import BehaviorEngine

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass

# Use environment variable or fall back to localhost
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

print("\n" + "="*70)
print("BEHAVIOR ANALYSIS MONITOR")
print("="*70 + "\n")

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

# Initialize behavior engine
behavior_engine = BehaviorEngine(host=REDIS_HOST, port=REDIS_PORT)
print("✅ Behavior Engine initialized\n")

print("="*70)
print("🔄 Listening for events on 'events' channel...")
print("   Press Ctrl+C to stop\n")

# Subscribe to events
pubsub = redis_client.pubsub()
pubsub.subscribe("events")

event_count = 0
first_visit_count = 0
repeat_visit_count = 0

try:
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                event = json.loads(message['data'])
                user_id = event.get("user_id") or event.get("user")
                domain = event.get("domain")
                
                if not user_id or not domain:
                    continue
                
                # Analyze with behavior engine
                result = behavior_engine.analyze(user_id, domain)
                
                event_count += 1
                if result['is_first_visit']:
                    first_visit_count += 1
                    emoji = "🆕"
                else:
                    repeat_visit_count += 1
                    emoji = "🔁"
                
                # Print result
                print(f"{emoji} Event #{event_count}: {user_id} → {domain}")
                print(f"   Score: {result['behavior_score']:.2f} | First Visit: {result['is_first_visit']} | {result['reason']}")
                
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"❌ Error: {e}")
                
except KeyboardInterrupt:
    print(f"\n\n{'='*70}")
    print("🛑 STOPPED")
    print("="*70)
    print(f"\nStatistics:")
    print(f"  Total Events:    {event_count}")
    print(f"  First Visits:    {first_visit_count}")
    print(f"  Repeat Visits:   {repeat_visit_count}")
    print(f"\n{'='*70}\n")
finally:
    pubsub.close()




