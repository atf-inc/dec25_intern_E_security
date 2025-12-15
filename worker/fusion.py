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