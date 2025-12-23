"""
Improved Fusion Engine
Key improvements:
1. Intent-based scoring (browsing vs exfiltration)
2. Only penalize actual uploads, not GET requests
3. Removed aggressive first-visit penalty
4. Confidence-aware weighting
5. SINGLE SOURCE OF TRUTH: Uses config files for ALL definitions
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass


class ImprovedFusionEngine:
    """
    Context-aware fusion with intent detection.
    ALL definitions come from config files (no hardcoded mappings).
    """
    
    def __init__(
        self,
        behavior_weight: float = 0.2,  # Behavior is secondary signal
        semantic_weight: float = 0.8,  # Semantic is primary signal
        blacklist_path: str = None,
        whitelist_path: str = None
    ):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if blacklist_path is None:
            blacklist_path = os.path.abspath(os.path.join(script_dir, "..", "config", "blacklist.json"))
        if whitelist_path is None:
            whitelist_path = os.path.abspath(os.path.join(script_dir, "..", "config", "whitelist.json"))
        
        # Normalize weights
        total = behavior_weight + semantic_weight
        if total <= 0:
            self.behavior_weight = 0.2
            self.semantic_weight = 0.8
        else:
            self.behavior_weight = behavior_weight / total
            self.semantic_weight = semantic_weight / total
        
        # Load config files
        self.blacklist = self._load_json(blacklist_path)
        self.whitelist = self._load_json(whitelist_path)
        
        print(f"✅ ImprovedFusionEngine initialized:")
        print(f"   - Behavior weight: {self.behavior_weight:.2f}")
        print(f"   - Semantic weight: {self.semantic_weight:.2f}")
        print(f"   - Blacklist: {len(self.blacklist)} domains")
        print(f"   - Whitelist: {len(self.whitelist)} domains")
    
    def _load_json(self, path: str) -> List[str]:
        """Load JSON file safely"""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Warning: Could not load {path}: {e}")
            return []
    
    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain for comparison"""
        domain = domain.lower().strip()
        
        if domain.startswith("http://"):
            domain = domain[7:]
        elif domain.startswith("https://"):
            domain = domain[8:]
        
        if domain.startswith("www."):
            domain = domain[4:]
        
        domain = domain.split("/")[0]
        domain = domain.split(":")[0]
        
        return domain
    
    def _check_explicit_lists(self, domain: str) -> Dict[str, Any]:
        """Check whitelist/blacklist from config files"""
        clean_domain = self._normalize_domain(domain)
        
        def is_match(target: str, domain_list: List[str]) -> bool:
            for item in domain_list:
                item = self._normalize_domain(item)
                if target == item or target.endswith("." + item):
                    return True
            return False
        
        # Whitelist takes precedence
        if is_match(clean_domain, self.whitelist):
            return {
                "override": True,
                "final_risk": 0.0,
                "risk_level": "SAFE",
                "reason": "Domain is whitelisted"
            }
        
        # Blacklist
        if is_match(clean_domain, self.blacklist):
            return {
                "override": True,
                "final_risk": 1.0,
                "risk_level": "CRITICAL",
                "reason": "Domain is blacklisted"
            }
        
        return {
            "override": False,
            "final_risk": None,
            "risk_level": "UNKNOWN",
            "reason": ""
        }
    
    def _calculate_risk_level(self, score: float) -> str:
        """Convert risk score to category"""
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
    
    def _detect_upload_intent(
        self, 
        method: str, 
        url: str, 
        upload_size_bytes: int
    ) -> Dict[str, Any]:
        """
        Detect if this is an actual upload attempt.
        
        Returns:
            {
                "is_upload": bool,
                "confidence": float (0-1),
                "reason": str
            }
        """
        method = method.upper()
        url_lower = url.lower()
        
        # Strong upload signals
        if method in ["POST", "PUT"]:
            # Check URL path for upload indicators
            upload_keywords = [
                "upload", "create", "submit", "paste", "share", 
                "attach", "send", "transfer", "export"
            ]
            
            has_upload_keyword = any(kw in url_lower for kw in upload_keywords)
            has_significant_size = upload_size_bytes > (100 * 1024)  # > 100KB
            
            if has_upload_keyword and has_significant_size:
                return {
                    "is_upload": True,
                    "confidence": 0.95,
                    "reason": f"POST/PUT with upload keyword and {upload_size_bytes/1024:.0f}KB payload"
                }
            elif has_upload_keyword:
                return {
                    "is_upload": True,
                    "confidence": 0.75,
                    "reason": f"POST/PUT with upload keyword"
                }
            elif has_significant_size:
                return {
                    "is_upload": True,
                    "confidence": 0.60,
                    "reason": f"POST/PUT with {upload_size_bytes/1024:.0f}KB payload"
                }
            else:
                # Generic POST (could be API call, form submit, etc.)
                return {
                    "is_upload": False,
                    "confidence": 0.3,
                    "reason": "POST/PUT with minimal data"
                }
        
        # GET requests are not uploads
        return {
            "is_upload": False,
            "confidence": 0.0,
            "reason": f"{method} request (read-only)"
        }
    
    def _calculate_upload_multiplier(
        self, 
        upload_intent: Dict[str, Any], 
        upload_size_bytes: int
    ) -> float:
        """
        Only apply multiplier for confirmed uploads.
        """
        if not upload_intent["is_upload"]:
            return 1.0  # No amplification for non-uploads
        
        size_kb = upload_size_bytes / (1024)
        
        # Scale by upload size
        if size_kb > 50:
            size_mult = 1.8
        elif size_kb > 10:
            size_mult = 1.5
        elif size_kb > 1:
            size_mult = 1.2
        else:
            size_mult = 1.0
        
        # Weight by confidence
        confidence = upload_intent["confidence"]
        return 1.0 + (size_mult - 1.0) * confidence
    
    def _get_behavior_adjustment(self, behavior_result: Dict[str, Any]) -> float:
        """
        Reduced first-visit penalty (from +0.15 to +0.05).
        
        Rationale: First-time access to a risky domain is still concerning,
        but shouldn't be the primary signal. Users legitimately explore new tools.
        """
        if behavior_result.get("is_first_visit", False):
            return 0.05  # Small boost (was 0.15)
        return 0.0
    
    def _apply_confidence_weighting(
        self, 
        semantic_score: float, 
        semantic_result: Dict[str, Any]
    ) -> float:
        """
        Weight semantic score by confidence.
        If confidence is already factored into semantic_score, no adjustment needed.
        """
        # The v2 semantic detector already factors confidence into risk_score
        return semantic_score
    
    def fuse(
        self,
        domain: str,
        user_id: str,
        url: str,
        method: str,
        upload_size_bytes: int,
        behavior_result: Dict[str, Any],
        semantic_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Improved context-aware fusion with intent detection.
        All category definitions come from config files.
        """
        # 1. Check for explicit overrides (from config/blacklist.json, config/whitelist.json)
        override = self._check_explicit_lists(domain)
        if override["override"]:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "domain": domain,
                "url": url,
                "method": method,
                "upload_size_kb": round(upload_size_bytes / (1024), 2),
                "final_risk_score": override["final_risk"],
                "risk_level": override["risk_level"],
                "override": True,
                "override_reason": override["reason"],
                "behavior_score": None,
                "semantic_score": None,
                "fusion_method": "explicit_list_override"
            }
        
        # 2. Detect upload intent
        upload_intent = self._detect_upload_intent(method, url, upload_size_bytes)
        
        # 3. Extract base scores
        behavior_score = behavior_result.get("behavior_score", 0.0)
        semantic_score = semantic_result.get("risk_score", 0.0)
        
        # 4. Apply confidence weighting to semantic score (if needed)
        weighted_semantic = self._apply_confidence_weighting(semantic_score, semantic_result)
        
        # 5. Apply upload multiplier ONLY if actual upload detected
        upload_multiplier = self._calculate_upload_multiplier(upload_intent, upload_size_bytes)
        context_semantic_score = weighted_semantic * upload_multiplier
        
        # 6. Behavior adjustment (minimal now)
        behavior_adjustment = self._get_behavior_adjustment(behavior_result)
        
        # 7. Final fusion
        fused_score = min(
            (context_semantic_score * self.semantic_weight) + 
            (behavior_score * self.behavior_weight) +
            behavior_adjustment,
            1.0
        )
        
        # 8. Determine risk level
        risk_level = self._calculate_risk_level(fused_score)
        
        # 9. Build result
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "domain": domain,
            "url": url,
            "method": method,
            "upload_size_kb": round(upload_size_bytes / (1024), 2),
            
            # Final assessment
            "final_risk_score": round(fused_score, 3),
            "risk_level": risk_level,
            "override": False,
            
            # Component scores
            "behavior_score": round(behavior_score, 3),
            "semantic_score": round(semantic_score, 3),
            "context_semantic_score": round(context_semantic_score, 3),
            
            # Intent detection
            "upload_intent": upload_intent,
            "upload_multiplier": round(upload_multiplier, 2),
            
            # Fusion details
            "fusion_method": "intent_aware_weighted",
            "weights": {
                "semantic": self.semantic_weight,
                "behavior": self.behavior_weight
            },
            
            # Original analysis details
            "behavior_analysis": {
                "is_first_visit": behavior_result.get("is_first_visit", False),
                "reason": behavior_result.get("reason", "")
            },
            "semantic_analysis": {
                "top_category": semantic_result.get("top_category", "unknown"),
                "category_type": semantic_result.get("category_type", "unknown"),
                "confidence": semantic_result.get("confidence", 0.0),
                "explanation": semantic_result.get("explanation", "")
            }
        }
        
        # DEBUG logging
        print(
            f"[FUSION] domain={domain} user={user_id} method={method} "
            f"upload_mb={result['upload_size_kb']:.2f} "
            f"semantic={result['semantic_score']:.3f} "
            f"confidence={result['semantic_analysis']['confidence']:.3f} "
            f"upload_intent={upload_intent['is_upload']} "
            f"upload_mult={upload_multiplier:.2f} "
            f"final={result['final_risk_score']:.3f} "
            f"level={risk_level}"
        )
        
        return result
    
    def generate_alert(self, fused_result: Dict[str, Any]) -> str:
        """Generate human-readable alert"""
        risk = fused_result["risk_level"]
        domain = fused_result["domain"]
        user = fused_result["user_id"]
        score = fused_result["final_risk_score"]
        method = fused_result.get("method", "UNKNOWN")
        upload_mb = fused_result.get("upload_size_kb", 0)
        
        # Get category from semantic analysis (now from anchors.json)
        semantic_analysis = fused_result.get("semantic_analysis", {})
        category = semantic_analysis.get("top_category", "unknown")
        
        upload_intent = fused_result.get("upload_intent", {})
        
        # Risk-based presentation
        config = {
            "CRITICAL": ("🚨", "Block immediately and investigate"),
            "HIGH": ("⚠️", "Review within 1 hour"),
            "MEDIUM": ("⚡", "Monitor for repeated activity"),
            "LOW": ("ℹ️", "Log for audit trail"),
            "SAFE": ("✅", "No action needed")
        }
        emoji, action = config.get(risk, ("📊", "Review"))
        
        # Build alert
        parts = []
        parts.append(f"{emoji} Shadow AI/IT Detection: {risk} ({score:.2f})")
        parts.append(f"User: {user}")
        parts.append(f"Domain: {domain}")
        parts.append(f"Category: {category}")  # Now from anchors.json
        
        # Intent context
        if upload_intent.get("is_upload"):
            parts.append(f"\n⬆️ Upload Detected:")
            parts.append(f"  - Confidence: {upload_intent.get('confidence', 0):.0%}")
            parts.append(f"  - Size: {upload_mb:.2f} MB")
            parts.append(f"  - Reason: {upload_intent.get('reason', 'N/A')}")
        else:
            parts.append(f"\n👁️ Browsing Activity:")
            parts.append(f"  - Method: {method}")
            parts.append(f"  - {upload_intent.get('reason', 'Read-only access')}")
        
        # Risk factors
        parts.append("\nRisk Factors:")
        
        confidence = semantic_analysis.get("confidence", 0.0)
        
        if confidence > 0.75:
            parts.append(f"  - High-confidence match to {category} (confidence: {confidence:.0%})")
        elif confidence > 0.6:
            parts.append(f"  - Moderate match to {category} (confidence: {confidence:.0%})")
        
        if fused_result.get("behavior_analysis", {}).get("is_first_visit"):
            parts.append("  - First-time access to this service")
        
        parts.append(f"\n{action}")
        
        return "\n".join(parts)


# ==================== TEST ====================

class MockBehaviorEngine:
    """Mock for testing"""
    def __init__(self):
        self.visited = set()
    
    def analyze(self, user_id: str, domain: str) -> dict:
        key = f"{user_id}:{domain}"
        is_first = key not in self.visited
        self.visited.add(key)
        
        return {
            "behavior_score": 0.4 if is_first else 0.0,
            "is_first_visit": is_first,
            "reason": "First time" if is_first else "Known domain"
        }


def test_improved_fusion():
    """Test improved fusion with intent detection"""
    print("\n" + "="*70)
    print("IMPROVED FUSION ENGINE TEST")
    print("="*70 + "\n")
    
    # Import the v2 semantic detector (which uses anchors.json)
    try:
        from semantic_v2 import ImprovedSemanticDetector
        semantic = ImprovedSemanticDetector()
    except ImportError:
        print("⚠️  Could not import semantic_v2. Run this test from the worker directory.")
        return
    
    fusion = ImprovedFusionEngine()
    behavior = MockBehaviorEngine()
    
    print(f"\n📋 Using categories from config/anchors.json:")
    for cat in list(semantic.categories.keys())[:5]:
        risk = semantic.category_risks.get(cat, 0.6)
        print(f"  - {cat}: base risk = {risk:.2f}")
    print(f"  ... and {len(semantic.categories) - 5} more\n")
    
    test_cases = [
        {
            "desc": "High-risk AI upload (confirmed)",
            "user_id": "user_001",
            "domain": "claude.ai",
            "url": "/api/v1/upload_context",
            "method": "POST",
            "upload_size_bytes": 15_000_000,  # 15 MB
        },
        {
            "desc": "AI browsing (no upload)",
            "user_id": "user_002",
            "domain": "claude.ai",
            "url": "/chat",
            "method": "GET",
            "upload_size_bytes": 0,
        },
        {
            "desc": "Unknown domain with small POST",
            "user_id": "user_003",
            "domain": "unknown-service.io",
            "url": "/api/send",
            "method": "POST",
            "upload_size_bytes": 50_000,  # 50 KB
        },
        {
            "desc": "Blacklisted file transfer",
            "user_id": "user_004",
            "domain": "wetransfer.com",
            "url": "/transfer/upload",
            "method": "POST",
            "upload_size_bytes": 100_000_000,  # 100 MB
        },
        {
            "desc": "News site browsing",
            "user_id": "user_005",
            "domain": "nytimes.com",
            "url": "/2024/12/article",
            "method": "GET",
            "upload_size_bytes": 0,
        },
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}: {case['desc']}")
        print(f"{'─'*70}")
        
        # Analyze
        semantic_result = semantic.analyze(case["domain"], case["url"])
        behavior_result = behavior.analyze(case["user_id"], case["domain"])
        
        fused = fusion.fuse(
            domain=case["domain"],
            user_id=case["user_id"],
            url=case["url"],
            method=case["method"],
            upload_size_bytes=case["upload_size_bytes"],
            behavior_result=behavior_result,
            semantic_result=semantic_result
        )
        
        print(f"\nSemantic: {fused['semantic_score']:.3f} (confidence: {semantic_result.get('confidence', 0):.3f})")
        print(f"Behavior: {fused['behavior_score']:.3f}")
        print(f"Upload Intent: {fused['upload_intent']['is_upload']} ({fused['upload_intent']['confidence']:.0%})")
        print(f"Upload Multiplier: {fused['upload_multiplier']:.2f}x")
        print(f"\n🎯 Final Risk: {fused['final_risk_score']:.3f} ({fused['risk_level']})")
        
        if fused["final_risk_score"] > 0.7:
            print("\n" + fusion.generate_alert(fused))
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_improved_fusion()