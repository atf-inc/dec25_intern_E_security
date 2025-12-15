import json
import os
from typing import Dict, Any, List
from datetime import datetime

# Load .env safely
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass


class FusionEngine:
    """
    Fuses behavior-based and semantic-based risk scores into a final risk assessment.
    
    Uses a weighted combination strategy with configurable weights and thresholds.
    """
    
    def __init__(
        self,
        behavior_weight: float = 0.3,
        semantic_weight: float = 0.7,
        blacklist_path: str = "../config/blacklist.json",
        whitelist_path: str = "../config/whitelist.json"
    ):
        """
        Initialize the fusion engine.
        
        Args:
            behavior_weight: Weight for behavior score (0-1)
            semantic_weight: Weight for semantic score (0-1)
            blacklist_path: Path to blacklist domains
            whitelist_path: Path to whitelist domains
        """
        # Normalize weights to sum to 1.0
        total = behavior_weight + semantic_weight
        self.behavior_weight = behavior_weight / total
        self.semantic_weight = semantic_weight / total
        
        # Load blacklist and whitelist
        self.blacklist = self._load_json(blacklist_path)
        self.whitelist = self._load_json(whitelist_path)
        
        print(f"✅ FusionEngine initialized:")
        print(f"   - Behavior weight: {self.behavior_weight:.2f}")
        print(f"   - Semantic weight: {self.semantic_weight:.2f}")
        print(f"   - Blacklist: {len(self.blacklist)} domains")
        print(f"   - Whitelist: {len(self.whitelist)} domains")
    
    def _load_json(self, path: str) -> List[str]:
        """Load JSON file safely."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Warning: Could not load {path}: {e}")
            return []
    
    def _check_explicit_lists(self, domain: str) -> Dict[str, Any]:
        """
        Check if domain is in whitelist or blacklist.
        
        Returns override score if found, None otherwise.
        """
        # Whitelist takes precedence
        if domain in self.whitelist:
            return {
                "override": True,
                "final_risk": 0.0,
                "risk_level": "SAFE",
                "reason": "Domain is whitelisted"
            }
        
        # Blacklist
        if domain in self.blacklist:
            return {
                "override": True,
                "final_risk": 1.0,
                "risk_level": "CRITICAL",
                "reason": "Domain is blacklisted"
            }
        
        return {"override": False}

    def _calculate_risk_level(self, score: float) -> str:
        """
        Convert risk score to categorical level.
        
        Args:
            score: Risk score (0-1)
            
        Returns:
            Risk level category
        """
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        else:
            return "SAFE"
    def fuse(
        self,
        domain: str,
        user_id: str,
        behavior_result: Dict[str, Any],
        semantic_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fuse behavior and semantic analysis results into final risk assessment.
        
        Args:
            domain: Domain being analyzed
            user_id: User ID
            behavior_result: Result from BehaviorEngine.analyze()
            semantic_result: Result from OpenRouterSimilarityDetector.analyze()
            
        Returns:
            Final fused risk assessment
        """
        # Check explicit lists first
        override = self._check_explicit_lists(domain)
        if override["override"]:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "domain": domain,
                "final_risk_score": override["final_risk"],
                "risk_level": override["risk_level"],
                "override": True,
                "override_reason": override["reason"],
                "behavior_score": None,
                "semantic_score": None,
                "fusion_method": "override"
            }
        
        # Extract scores
        behavior_score = behavior_result.get("behavior_score", 0.0)
        semantic_score = semantic_result.get("risk_score", 0.0)
        
        # Apply weighted fusion
        fused_score = (
            self.behavior_weight * behavior_score +
            self.semantic_weight * semantic_score
        )
        
        # Determine risk level
        risk_level = self._calculate_risk_level(fused_score)
        
        # Build comprehensive result
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "domain": domain,
            
            # Final assessment
            "final_risk_score": round(fused_score, 3),
            "risk_level": risk_level,
            "override": False,
            
            # Component scores
            "behavior_score": round(behavior_score, 3),
            "semantic_score": round(semantic_score, 3),
            
            # Fusion details
            "fusion_method": "weighted",
            "weights": {
                "behavior": self.behavior_weight,
                "semantic": self.semantic_weight
            },
            
            # Original analysis details
            "behavior_analysis": {
                "is_first_visit": behavior_result.get("is_first_visit", False),
                "reason": behavior_result.get("reason", "")
            },
            "semantic_analysis": {
                "top_category": semantic_result.get("top_category", "unknown"),
                "similarities": semantic_result.get("similarities", {}),
                "explanation": semantic_result.get("explanation", "")
            }
        }
        
        return result

    def generate_alert(self, fused_result: Dict[str, Any]) -> str:
        """
        Generate human-readable alert message based on fused result.
        
        Args:
            fused_result: Output from fuse()
            
        Returns:
            Alert message string
        """
        risk = fused_result["risk_level"]
        domain = fused_result["domain"]
        user = fused_result["user_id"]
        score = fused_result["final_risk_score"]
        
        if risk == "CRITICAL":
            emoji = "🚨"
            action = "BLOCK immediately"
        elif risk == "HIGH":
            emoji = "⚠️"
            action = "ALERT security team"
        elif risk == "MEDIUM":
            emoji = "⚡"
            action = "MONITOR closely"
        elif risk == "LOW":
            emoji = "ℹ️"
            action = "LOG for review"
        else:
            emoji = "✅"
            action = "ALLOW"
        
        alert = f"{emoji} {risk} RISK ({score:.2f}): User '{user}' → {domain}\n"
        alert += f"   Action: {action}\n"
        
        if fused_result.get("override"):
            alert += f"   Reason: {fused_result['override_reason']}\n"
        else:
            alert += f"   Behavior: {fused_result['behavior_analysis']['reason']}\n"
            alert += f"   Semantic: {fused_result['semantic_analysis']['explanation']}\n"
        
        return alert

    

# ---------------- TEST ----------------

class MockBehaviorEngine:
    """Mock behavior engine for testing when Redis is not available."""
    
    def __init__(self):
        self.visited = set()
    
    def analyze(self, user_id: str, domain: str) -> dict:
        """Simulate behavior analysis without Redis."""
        key = f"{user_id}:{domain}"
        is_first = key not in self.visited
        self.visited.add(key)
        
        return {
            "behavior_score": 0.5 if is_first else 0.0,
            "is_first_visit": is_first,
            "reason": "First time user has visited this domain" if is_first else "Domain found in user history"
        }


def test_fusion():
    """
    Test the fusion engine with sample data from both engines.
    """
    print("\n" + "="*60)
    print("FUSION ENGINE TEST")
    print("="*60 + "\n")
    
    # Import the other engines
    try:
        from behavior import BehaviorEngine
        from semantic import OpenRouterSimilarityDetector
    except ImportError:
        print("⚠ Could not import behavior or semantic engines")
        print("Make sure behavior.py and semantic.py are in the same directory")
        return
    
    # Initialize all engines
    print("Initializing engines...\n")
    fusion = FusionEngine()
    
    # Try to connect to Redis, fall back to mock if not available
    try:
        behavior = BehaviorEngine(host="localhost")
        print("✅ Behavior Engine connected to Redis")
    except Exception as e:
        print(f"⚠️  Redis not available, using mock behavior engine")
        behavior = MockBehaviorEngine()
    
    semantic = OpenRouterSimilarityDetector()
    
    # Test scenarios
    test_cases = [
        {
            "user_id": "user_001",
            "domain": "claude.ai",
            "description": "Known AI service, first visit"
        },
        {
            "user_id": "user_002",
            "domain": "wetransfer.com",
            "description": "Blacklisted file transfer, repeat visit"
        },
        {
            "user_id": "user_003",
            "domain": "github.com",
            "description": "Legitimate service, repeat visit"
        },
        {
            "user_id": "user_004",
            "domain": "protonmail.com",
            "description": "Anonymous email service, first visit"
        }
    ]
    
    print("\n" + "="*60)
    print("RUNNING TEST CASES")
    print("="*60 + "\n")
    
    for i, test_case in enumerate(test_cases, 1):
        user_id = test_case["user_id"]
        domain = test_case["domain"]
        
        print(f"\n{'─'*60}")
        print(f"Test Case {i}: {test_case['description']}")
        print(f"{'─'*60}")
        print(f"User: {user_id}")
        print(f"Domain: {domain}\n")
        
        # Get behavior analysis
        print("📊 Behavior Analysis:")
        behavior_result = behavior.analyze(user_id, domain)
        print(f"   Score: {behavior_result['behavior_score']:.2f}")
        print(f"   First Visit: {behavior_result['is_first_visit']}")
        print(f"   Reason: {behavior_result['reason']}\n")
        
        # Get semantic analysis
        print("🧠 Semantic Analysis:")
        semantic_result = semantic.analyze(domain)
        print(f"   Risk Score: {semantic_result['risk_score']:.2f}")
        print(f"   Top Category: {semantic_result['top_category']}")
        print(f"   Explanation: {semantic_result['explanation']}\n")
        
        # Fuse the results
        print("⚡ Fusion Result:")
        fused = fusion.fuse(domain, user_id, behavior_result, semantic_result)
        
        print(f"   Final Score: {fused['final_risk_score']:.3f}")
        print(f"   Risk Level: {fused['risk_level']}")
        print(f"   Override: {fused['override']}")
        
        if fused['override']:
            print(f"   Override Reason: {fused['override_reason']}")
        else:
            print(f"   Weighted Combination:")
            print(f"     - Behavior ({fusion.behavior_weight:.1%}): {fused['behavior_score']:.3f}")
            print(f"     - Semantic ({fusion.semantic_weight:.1%}): {fused['semantic_score']:.3f}")
        
        # Generate alert
        print("\n" + fusion.generate_alert(fused))
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_fusion()