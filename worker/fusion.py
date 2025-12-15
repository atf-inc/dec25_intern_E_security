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