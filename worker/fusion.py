

import uuid
from typing import Dict, Any, List
from datetime import datetime
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskFusion:
    def __init__(self, weights: Dict[str, float] = None, risk_threshold: float = 0.75):
        """
        Initialize risk fusion engine.
        
        Args:
            weights: Dictionary with weights for each engine {'rule': 0.3, 'semantic': 0.5, 'behavior': 0.2}
            risk_threshold: Threshold above which an alert is triggered (0-1)
        """
        # Default weights (can be tuned based on business requirements)
        self.weights = weights or {
            'rule': 0.30,      # 30% - Rule-based checks
            'semantic': 0.50,  # 50% - AI semantic analysis (most important)
            'behavior': 0.20   # 20% - Behavioral patterns
        }
        
        self.risk_threshold = risk_threshold
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(f"Weights sum to {weight_sum}, normalizing to 1.0")
            for key in self.weights:
                self.weights[key] /= weight_sum
    
    def _calculate_weighted_score(self, rule_score: float, semantic_score: float, behavior_score: float) -> float:
        """Calculate weighted final score."""
        weighted_score = (
            self.weights['rule'] * rule_score +
            self.weights['semantic'] * semantic_score +
            self.weights['behavior'] * behavior_score
        )
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, weighted_score))
    
    def _generate_explanation(self, rule_result: Dict[str, Any], semantic_result: Dict[str, Any], 
                            behavior_result: Dict[str, Any], final_score: float) -> str:
        """Generate human-readable explanation for the risk assessment."""
        explanations = []
        
        # Rule engine explanations
        if rule_result.get('rule_score', 0) > 0:
            rule_alerts = rule_result.get('rule_alerts', [])
            if 'blacklist_hit' in rule_alerts:
                explanations.append("Domain found in blacklist")
            if 'large_upload' in rule_alerts:
                explanations.append("Large file upload detected")
            if 'suspicious_pattern' in rule_alerts:
                explanations.append("Suspicious domain pattern")
        
        # Semantic engine explanations
        semantic_explanation = semantic_result.get('semantic_explanation', '')
        if semantic_explanation and semantic_result.get('semantic_score', 0) > 0.5:
            explanations.append(semantic_explanation)
        
        # Behavior engine explanations
        behavior_alerts = behavior_result.get('behavior_alerts', [])
        if 'first_time_visit' in behavior_alerts:
            explanations.append("First time accessing this domain")
        if 'frequency_anomaly' in behavior_alerts:
            explanations.append("Unusual access frequency")
        if 'unusual_timing' in behavior_alerts:
            explanations.append("Access outside normal hours")
        
        # Combine explanations
        if explanations:
            main_explanation = '; '.join(explanations)
        else:
            main_explanation = "Low risk activity detected"
        
        # Add score context
        risk_level = self._get_risk_level(final_score)
        return f"{main_explanation} (Risk: {risk_level}, Score: {final_score:.2f})"
    
    def _get_risk_level(self, score: float) -> str:
        """Convert numerical score to risk level string."""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _should_alert(self, final_score: float) -> bool:
        """Determine if an alert should be generated based on the final score."""
        return final_score >= self.risk_threshold
    
    def _create_alert_payload(self, source_event: Dict[str, Any], rule_result: Dict[str, Any],
                            semantic_result: Dict[str, Any], behavior_result: Dict[str, Any],
                            final_score: float, explanation: str) -> Dict[str, Any]:
        """Create standardized alert payload for Redis publication."""
        
        alert_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Extract key information for alert summary
        domain = source_event.get('domain', 'unknown')
        user_id = source_event.get('user_id', 'unknown')
        detected_category = semantic_result.get('detected_category', 'unknown')
        risk_level = self._get_risk_level(final_score)
        
        alert_payload = {
            'alert_id': alert_id,
            'timestamp': timestamp,
            'source_event': source_event,
            'risk_assessment': {
                'final_score': final_score,
                'risk_level': risk_level,
                'should_alert': True,
                'explanation': explanation
            },
            'component_scores': {
                'rule_score': rule_result.get('rule_score', 0),
                'semantic_score': semantic_result.get('semantic_score', 0),
                'behavior_score': behavior_result.get('behavior_score', 0)
            },
            'detailed_analysis': {
                'rule_engine': rule_result,
                'semantic_engine': semantic_result,
                'behavior_engine': behavior_result
            },
            'metadata': {
                'user_id': user_id,
                'domain': domain,
                'detected_category': detected_category,
                'weights_used': self.weights,
                'threshold_used': self.risk_threshold
            }
        }
        
        return alert_payload
    
    def analyze(self, source_event: Dict[str, Any], rule_result: Dict[str, Any],
                semantic_result: Dict[str, Any], behavior_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform risk fusion analysis combining all engine results.
        
        Args:
            source_event: Original log event
            rule_result: Output from rule engine
            semantic_result: Output from semantic engine
            behavior_result: Output from behavior engine
            
        Returns:
            Dictionary with fusion analysis results and optional alert payload
        """
        try:
            # Extract scores from each engine
            rule_score = rule_result.get('rule_score', 0.0)
            semantic_score = semantic_result.get('semantic_score', 0.0)
            behavior_score = behavior_result.get('behavior_score', 0.0)
            
            # Calculate weighted final score
            final_score = self._calculate_weighted_score(rule_score, semantic_score, behavior_score)
            
            # Generate explanation
            explanation = self._generate_explanation(rule_result, semantic_result, behavior_result, final_score)
            
            # Determine if alert should be triggered
            should_alert = self._should_alert(final_score)
            
            # Create base result
            fusion_result = {
                'final_score': final_score,
                'risk_level': self._get_risk_level(final_score),
                'should_alert': should_alert,
                'explanation': explanation,
                'component_scores': {
                    'rule': rule_score,
                    'semantic': semantic_score,
                    'behavior': behavior_score
                },
                'weights_applied': self.weights
            }
            
            # If alert should be triggered, create alert payload
            if should_alert:
                alert_payload = self._create_alert_payload(
                    source_event, rule_result, semantic_result, behavior_result,
                    final_score, explanation
                )
                fusion_result['alert_payload'] = alert_payload
            
            return fusion_result
            
        except Exception as e:
            logger.error(f"Error in risk fusion analysis: {e}")
            return {
                'final_score': 0.5,
                'risk_level': 'UNKNOWN',
                'should_alert': False,
                'explanation': f'Analysis failed: {str(e)}',
                'component_scores': {'rule': 0, 'semantic': 0, 'behavior': 0},
                'weights_applied': self.weights,
                'error': str(e)
            }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Update fusion weights (useful for tuning)."""
        weight_sum = sum(new_weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(f"New weights sum to {weight_sum}, normalizing to 1.0")
            for key in new_weights:
                new_weights[key] /= weight_sum
        
        self.weights = new_weights
        logger.info(f"Updated fusion weights: {self.weights}")
    
    def update_threshold(self, new_threshold: float):
        """Update risk threshold."""
        self.risk_threshold = max(0.0, min(1.0, new_threshold))
        logger.info(f"Updated risk threshold to {self.risk_threshold}")

# Test function
def test_risk_fusion():
    """Test the risk fusion engine with sample data."""
    fusion_engine = RiskFusion()
    
    # Sample inputs from different engines
    source_event = {
        'ts': '2025-12-12T14:30:00Z',
        'user_id': 'alice@company.com',
        'domain': 'stealth-ai-writer.io',
        'url': '/api/upload',
        'method': 'POST',
        'upload_size_bytes': 15728640  # 15MB
    }
    
    rule_result = {
        'rule_score': 0.6,
        'rule_alerts': ['suspicious_pattern', 'large_upload'],
        'rule_explanations': ['Suspicious pattern detected', 'Large upload: 15.00MB > 10MB']
    }
    
    semantic_result = {
        'semantic_score': 0.85,
        'semantic_explanation': 'High similarity to AI tools (0.85)',
        'detected_category': 'ai_tools',
        'category_similarities': {'ai_tools': 0.85, 'safe_saas': 0.2}
    }
    
    behavior_result = {
        'behavior_score': 0.4,
        'behavior_alerts': ['first_time_visit'],
        'behavior_explanations': ['First time visit to stealth-ai-writer.io'],
        'is_first_visit': True
    }
    
    # Run fusion analysis
    result = fusion_engine.analyze(source_event, rule_result, semantic_result, behavior_result)
    
    print("=== Risk Fusion Test Results ===")
    print(f"Final Score: {result['final_score']:.3f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Should Alert: {result['should_alert']}")
    print(f"Explanation: {result['explanation']}")
    print(f"Component Scores: {result['component_scores']}")
    
    if 'alert_payload' in result:
        print("\n=== Alert Payload Generated ===")
        alert = result['alert_payload']
        print(f"Alert ID: {alert['alert_id']}")
        print(f"User: {alert['metadata']['user_id']}")
        print(f"Domain: {alert['metadata']['domain']}")
        print(f"Category: {alert['metadata']['detected_category']}")

if __name__ == "__main__":
    test_risk_fusion()