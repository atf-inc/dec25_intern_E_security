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
