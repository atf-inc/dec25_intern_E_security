
import json
import time
from rule_engine import RuleEngine
from semantic_engine import SemanticEngine
from behavior_engine import BehaviorEngine
from risk_fusion import RiskFusion

def test_complete_pipeline():
    """Test the complete detection pipeline with sample logs."""
    
    print("=== ShadowGuard AI Detection Engine Test ===\n")
    
    # Initialize all engines
    print("1. Initializing detection engines...")
    
    try:
        rule_engine = RuleEngine()
        print("   ✓ Rule Engine initialized")
    except Exception as e:
        print(f"   ✗ Rule Engine failed: {e}")
        return
    
    try:
        print("   Loading AI model (this may take a few seconds)...")
        semantic_engine = SemanticEngine()
        print("   ✓ Semantic Engine initialized")
    except Exception as e:
        print(f"   ✗ Semantic Engine failed: {e}")
        return
    
    try:
        behavior_engine = BehaviorEngine()
        print("   ✓ Behavior Engine initialized")
    except Exception as e:
        print(f"   ✗ Behavior Engine failed: {e}")
        return
    
    try:
        fusion_engine = RiskFusion()
        print("   ✓ Risk Fusion Engine initialized")
    except Exception as e:
        print(f"   ✗ Risk Fusion Engine failed: {e}")
        return
    
    print("\n2. Running test scenarios...\n")
    
    # Test scenarios
    test_logs = [
        {
            'name': 'Safe Activity - GitHub',
            'log': {
                'ts': '2025-12-12T10:30:00Z',
                'user_id': 'alice@company.com',
                'domain': 'github.com',
                'url': '/user/repo',
                'method': 'GET',
                'upload_size_bytes': 1024
            }
        },
        {
            'name': 'Suspicious AI Tool',
            'log': {
                'ts': '2025-12-12T14:30:00Z',
                'user_id': 'bob@company.com',
                'domain': 'stealth-ai-writer.io',
                'url': '/api/chat',
                'method': 'POST',
                'upload_size_bytes': 5242880  # 5MB
            }
        },
        {
            'name': 'Large Upload + Suspicious Pattern',
            'log': {
                'ts': '2025-12-12T23:45:00Z',
                'user_id': 'charlie@company.com',
                'domain': 'temp-file-share.com',
                'url': '/upload/anonymous',
                'method': 'POST',
                'upload_size_bytes': 15728640  # 15MB
            }
        },
        {
            'name': 'Unknown Domain - Late Night',
            'log': {
                'ts': '2025-12-12T02:15:00Z',
                'user_id': 'alice@company.com',
                'domain': 'super-gpt-clone.net',
                'url': '/api/upload',
                'method': 'POST',
                'upload_size_bytes': 2097152  # 2MB
            }
        }
    ]
    
    alerts_generated = []
    
    for i, test_case in enumerate(test_logs, 1):
        print(f"--- Test {i}: {test_case['name']} ---")
        log = test_case['log']
        print(f"Domain: {log['domain']} | User: {log['user_id']} | Size: {log['upload_size_bytes']} bytes")
        
        # Run through all engines
        try:
            # Stage 1: Rule Engine
            rule_result = rule_engine.analyze(log)
            
            # Stage 2: Semantic Engine
            semantic_result = semantic_engine.analyze(log)
            
            # Stage 3: Behavior Engine
            behavior_result = behavior_engine.analyze(log)
            
            # Stage 4: Risk Fusion
            fusion_result = fusion_engine.analyze(log, rule_result, semantic_result, behavior_result)
            
            # Display results
            print(f"Scores: Rule={rule_result['rule_score']:.2f}, "
                  f"Semantic={semantic_result['semantic_score']:.2f}, "
                  f"Behavior={behavior_result['behavior_score']:.2f}")
            
            print(f"Final Score: {fusion_result['final_score']:.2f} | "
                  f"Risk Level: {fusion_result['risk_level']} | "
                  f"Alert: {'YES' if fusion_result['should_alert'] else 'NO'}")
            
            print(f"Explanation: {fusion_result['explanation']}")
            
            # If alert generated, add to list
            if fusion_result['should_alert']:
                alerts_generated.append({
                    'test_name': test_case['name'],
                    'domain': log['domain'],
                    'user': log['user_id'],
                    'score': fusion_result['final_score'],
                    'alert_payload': fusion_result.get('alert_payload', {})
                })
            
            print()
            
        except Exception as e:
            print(f"ERROR in test {i}: {e}")
            print()
    
    # Summary
    print("=== Test Summary ===")
    print(f"Total tests: {len(test_logs)}")
    print(f"Alerts generated: {len(alerts_generated)}")
    
    if alerts_generated:
        print("\nAlerts:")
        for alert in alerts_generated:
            print(f"  • {alert['test_name']}: {alert['domain']} (Score: {alert['score']:.2f})")
    
    print("\n=== Pipeline Test Completed ===")

def test_individual_engines():
    """Test each engine individually."""
    
    print("=== Individual Engine Tests ===\n")
    
    sample_log = {
        'ts': '2025-12-12T14:30:00Z',
        'user_id': 'test@company.com',
        'domain': 'stealth-gpt.io',
        'url': '/api/chat',
        'method': 'POST',
        'upload_size_bytes': 5242880
    }
    
    # Test Rule Engine
    print("Testing Rule Engine:")
    try:
        rule_engine = RuleEngine()
        result = rule_engine.analyze(sample_log)
        print(f"  Score: {result['rule_score']}")
        print(f"  Alerts: {result['rule_alerts']}")
        print("  ✓ Rule Engine working\n")
    except Exception as e:
        print(f"  ✗ Rule Engine error: {e}\n")
    
    # Test Semantic Engine
    print("Testing Semantic Engine:")
    try:
        semantic_engine = SemanticEngine()
        result = semantic_engine.analyze(sample_log)
        print(f"  Score: {result['semantic_score']}")
        print(f"  Category: {result['detected_category']}")
        print("  ✓ Semantic Engine working\n")
    except Exception as e:
        print(f"  ✗ Semantic Engine error: {e}\n")
    
    # Test Behavior Engine
    print("Testing Behavior Engine:")
    try:
        behavior_engine = BehaviorEngine()
        result = behavior_engine.analyze(sample_log)
        print(f"  Score: {result['behavior_score']}")
        print(f"  First visit: {result['is_first_visit']}")
        print("  ✓ Behavior Engine working\n")
    except Exception as e:
        print(f"  ✗ Behavior Engine error: {e}\n")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Individual engine tests")
    print("2. Complete pipeline test")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        test_individual_engines()
    
    if choice in ['2', '3']:
        test_complete_pipeline()