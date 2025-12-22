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
        blacklist_path: str = None,
        whitelist_path: str = None
    ):
        """
        Initialize the fusion engine.
        """
        # Resolve paths relative to the file if not provided
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if blacklist_path is None:
            blacklist_path = os.path.abspath(os.path.join(script_dir, "..", "config", "blacklist.json"))
        if whitelist_path is None:
            whitelist_path = os.path.abspath(os.path.join(script_dir, "..", "config", "whitelist.json"))
        # Normalize weights to sum to 1.0 (guard against division by zero)
        total = behavior_weight + semantic_weight
        if total <= 0:
            self.behavior_weight = 0.5
            self.semantic_weight = 0.5
        else:
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
    
    def _normalize_domain(self, domain: str) -> str:
        """
        Normalize domain by removing protocol, www prefix, port, and path.
        
        Examples:
            https://www.example.com:8080/path → example.com
            http://api.example.com/v1 → api.example.com
        """
        domain = domain.lower().strip()
        
        # Remove protocol
        if domain.startswith("http://"):
            domain = domain[7:]
        elif domain.startswith("https://"):
            domain = domain[8:]
            
        # Remove www prefix
        if domain.startswith("www."):
            domain = domain[4:]
        
        # Remove path components
        domain = domain.split("/")[0]
        
        # Remove port if present (e.g., example.com:8080 → example.com)
        domain = domain.split(":")[0]
        
        return domain

    def _check_explicit_lists(self, domain: str) -> Dict[str, Any]:
        """
        Check if domain is in whitelist or blacklist.
        
        Returns:
            Dict with keys: override, final_risk, risk_level, reason
            - override: True if domain matched a list, False otherwise
            - final_risk: Risk score (0.0 for whitelist, 1.0 for blacklist, None if no match)
            - risk_level: "SAFE", "CRITICAL", or "UNKNOWN" if no match
            - reason: Explanation string
        """
        # Normalize the input domain
        clean_domain = self._normalize_domain(domain)
        
        # Helper to check if domain matches any in list (exact or subdomain)
        def is_match(target_domain: str, domain_list: List[str]) -> bool:
            for item in domain_list:
                item = self._normalize_domain(item)
                # Exact match or subdomain match (e.g., "drive.google.com" ends with "google.com")
                if target_domain == item or target_domain.endswith("." + item):
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
        
        # No match - return consistent structure
        return {
            "override": False,
            "final_risk": None,
            "risk_level": "UNKNOWN",
            "reason": ""
        }

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
    
    def _get_method_multiplier(self, method: str) -> float:
        """
        Get risk multiplier based on HTTP method.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            
        Returns:
            Risk multiplier (0.3 for GET, 1.0 for POST, etc.)
            
        Rationale:
            - GET (0.3): Read-only operations have minimal data exposure risk
            - POST (1.0): Baseline for data submission/upload operations
            - PUT (1.2): Updates/uploads, slightly elevated risk
            - DELETE (0.5): Data removal has lower exposure risk than uploads,
              but higher than reads (could indicate data exfiltration prep)
        """
        multipliers = {
            "GET": 0.3,    # Read-only, 70% risk reduction
            "POST": 1.0,   # Baseline for write operations
            "PUT": 1.2,    # Upload/update, slightly elevated
            "DELETE": 0.5  # Removal, lower data exposure risk
        }
        return multipliers.get(method.upper(), 1.0)
    
    def _get_upload_multiplier(self, method: str, size_bytes: int) -> float:
        """
        Get risk multiplier based on upload size.
        Only applies to POST/PUT requests.
        
        Args:
            method: HTTP method
            size_bytes: Upload size in bytes (can be None)
            
        Returns:
            Risk multiplier (1.0 to 2.0)
        """
        if method.upper() not in ["POST", "PUT"]:
            return 1.0
        
        # Defensive check: handle None or invalid size_bytes
        size_bytes = size_bytes or 0
        
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > 50:
            return 2.0   # Very large upload
        elif size_mb > 10:
            return 1.5   # Large upload
        elif size_mb > 1:
            return 1.2   # Moderate upload
        return 1.0       # Small upload
    
    def _get_behavior_adjustment(self, behavior_result: Dict[str, Any]) -> float:
        """
        Get behavior score adjustment based on visit history.
        
        Args:
            behavior_result: Result from BehaviorEngine.analyze()
            
        Returns:
            Adjustment value (-0.2 to +0.2)
        """
        if behavior_result.get("is_first_visit", False):
            return 0.15   # +15% risk boost for first-time access
        return 0.0        # No adjustment for known domains
    
    def _is_content_consumption(self, domain: str, url: str) -> bool:
        """
        Quick check for content consumption patterns.
        """
        # Normalize domain first (remove protocol, www, port, path)
        clean_domain = self._normalize_domain(domain)
        
        # Rely on the Semantic Engine's precise logic
        try:
            from worker.semantic import OpenRouterSimilarityDetector
            return OpenRouterSimilarityDetector.is_content_consumption(clean_domain, url)
        except (ImportError, ValueError, AttributeError):
            # Very basic fallback that only matches known top search/info domains
            safe_roots = ["google.com", "bing.com", "wikipedia.org", "nytimes.com"]
            return any(clean_domain.endswith(d) for d in safe_roots)
    
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
        Context-aware fusion of behavior and semantic analysis.
        
        Args:
            domain: Domain being analyzed
            user_id: User ID
            url: URL path
            method: HTTP method (GET, POST, PUT, DELETE)
            upload_size_bytes: Upload size in bytes
            behavior_result: Result from BehaviorEngine.analyze()
            semantic_result: Result from OpenRouterSimilarityDetector.analyze()
            
        Returns:
            Final fused risk assessment
        """
        # Content consumption override (highest priority)
        if method.upper() == "GET" and self._is_content_consumption(domain, url):
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "domain": domain,
                "url": url,
                "method": method,
                "upload_size_mb": 0,
                "final_risk_score": 0.0,
                "risk_level": "SAFE",
                "override": True,
                "override_reason": "Read-only access to informational content (news/docs/search)",
                "behavior_score": 0.0,
                "semantic_score": 0.0,
                "fusion_method": "content_consumption_override"
            }
        
        # Check explicit lists (blacklist/whitelist)
        override = self._check_explicit_lists(domain)
        if override["override"]:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "domain": domain,
                "url": url,
                "method": method,
                "upload_size_mb": round(upload_size_bytes / (1024 * 1024), 2),
                "final_risk_score": override["final_risk"],
                "risk_level": override["risk_level"],
                "override": True,
                "override_reason": override["reason"],
                "behavior_score": None,
                "semantic_score": None,
                "fusion_method": "explicit_list_override"
            }
        
        # Extract base scores
        behavior_score = behavior_result.get("behavior_score", 0.0)
        semantic_score = semantic_result.get("risk_score", 0.0)
        
        # Apply context multipliers
        method_multiplier = self._get_method_multiplier(method)
        upload_multiplier = self._get_upload_multiplier(method, upload_size_bytes)
        
        # Context-aware semantic score
        context_semantic_score = semantic_score * method_multiplier * upload_multiplier
        
        # Behavior adjustment
        behavior_adjustment = self._get_behavior_adjustment(behavior_result)
        
        # Final weighted fusion
        fused_score = min(
            (context_semantic_score * self.semantic_weight) + 
            (behavior_score * self.behavior_weight) +
            behavior_adjustment,  # Added directly (not weighted)
            1.0
        )
        
        # Determine risk level
        risk_level = self._calculate_risk_level(fused_score)
        
        # Build comprehensive result
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "domain": domain,
            "url": url,
            "method": method,
            "upload_size_mb": round(upload_size_bytes / (1024 * 1024), 2),
            
            # Final assessment
            "final_risk_score": round(fused_score, 3),
            "risk_level": risk_level,
            "override": False,
            
            # Component scores
            "behavior_score": round(behavior_score, 3),
            "semantic_score": round(semantic_score, 3),
            "context_semantic_score": round(context_semantic_score, 3),
            
            # Multipliers
            "method_multiplier": method_multiplier,
            "upload_multiplier": upload_multiplier,
            
            # Fusion details
            "fusion_method": "context_aware_weighted",
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
                "similarities": semantic_result.get("similarities", {}),
                "explanation": semantic_result.get("explanation", "")
            }
        }

        # DEBUG: Log fusion inputs and outputs for observability
        print(
            "[FUSION DEBUG]",
            f"domain={domain}",
            f"user={user_id}",
            f"method={method}",
            f"upload_mb={result['upload_size_mb']}",
            f"semantic={result['semantic_score']}",
            f"behavior={result['behavior_score']}",
            f"ctx_sem={result['context_semantic_score']}",
            f"m_mult={method_multiplier}",
            f"u_mult={upload_multiplier}",
            f"beh_adj={behavior_adjustment}",
            f"final={result['final_risk_score']}",
            f"level={risk_level}",
        )

        return result

    def generate_alert(self, fused_result: Dict[str, Any]) -> str:
        """
        Generate human-readable, non-accusatory alert message.
        
        Args:
            fused_result: Output from fuse()
            
        Returns:
            Alert message string
        """
        risk = fused_result["risk_level"]
        domain = fused_result["domain"]
        user = fused_result["user_id"]
        score = fused_result["final_risk_score"]
        method = fused_result.get("method", "UNKNOWN")
        upload_mb = fused_result.get("upload_size_mb", 0)
        category = fused_result.get("semantic_analysis", {}).get("category_type", "unknown")
        
        # Risk-based presentation
        if risk == "CRITICAL":
            emoji = "🚨"
            action = "Review immediately and contact user"
        elif risk == "HIGH":
            emoji = "⚠️"
            action = "Review within 24 hours"
        elif risk == "MEDIUM":
            emoji = "⚡"
            action = "Monitor for repeated usage"
        elif risk == "LOW":
            emoji = "ℹ️"
            action = "Log for audit trail"
        else:
            emoji = "✅"
            action = "No action needed"
        
        # Build non-accusatory explanation
        parts = []
        parts.append(f"{emoji} Data Exposure Risk: {risk} ({score:.2f})")
        parts.append(f"User: {user}")
        parts.append(f"Domain: {domain}")
        parts.append(f"Action: {method}")
        
        # Why it triggered (focus on behavior)
        if fused_result.get("override"):
            parts.append(f"\nReason: {fused_result['override_reason']}")
        else:
            parts.append("\nRisk Factors:")
            
            # Method context
            if method in ["POST", "PUT"]:
                if upload_mb > 10:
                    parts.append(f"  - Large data upload ({upload_mb:.1f} MB) to {category}")
                else:
                    parts.append(f"  - Data submission to {category}")
            else:
                parts.append(f"  - Accessed {category}")
            
            # Behavioral context
            if fused_result.get("behavior_analysis", {}).get("is_first_visit", False):
                parts.append("  - First-time access to this service")
            
            # Semantic context
            sem_explanation = fused_result.get("semantic_analysis", {}).get("explanation", "")
            if sem_explanation and "similarity" in sem_explanation.lower():
                parts.append(f"  - {sem_explanation}")
        
        parts.append(f"\nRecommended Action: {action}")
        parts.append("\nNote: This alert indicates potential unintentional data exposure risk, not malicious activity.")
        
        return "\n".join(parts)


    

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
        url = "/dummy/test/path"
        semantic_result = semantic.analyze(domain, url)
        print(f"   Risk Score: {semantic_result['risk_score']:.2f}")
        print(f"   Top Category: {semantic_result['top_category']}")
        print(f"   Explanation: {semantic_result['explanation']}\\n")
        
        # Fuse the results
        print("⚡ Fusion Result:")
        fused = fusion.fuse(
            domain=domain, 
            user_id=user_id, 
            url=url, 
            method="POST", 
            upload_size_bytes=1024, 
            behavior_result=behavior_result, 
            semantic_result=semantic_result
        )
        
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