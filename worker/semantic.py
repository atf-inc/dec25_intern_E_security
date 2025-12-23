"""
Improved Semantic Analysis Engine
Key improvements:
1. Uses actual similarity scores (not fixed category risks)
2. Domain-level caching (ignores URL paths for cache key)
3. Async-ready architecture for batch processing
4. Confidence-weighted risk scoring
5. SINGLE SOURCE OF TRUTH: Uses config/anchors.json for ALL category definitions
"""

import json
import numpy as np
import os
import requests
import time
from typing import Dict, Any, List, Tuple, Optional
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass


# Content consumption patterns
INFORMATIONAL_DOMAINS = [
    "nytimes.com", "wsj.com", "reuters.com", "bloomberg.com", "cnn.com", "bbc.com",
    "wikipedia.org", "britannica.com", "stackoverflow.com", "github.com", 
    "google.com", "bing.com", "duckduckgo.com"
]

INFORMATIONAL_PATH_PATTERNS = [
    "/docs", "/wiki", "/manual", "/guide", "/help", "/faq"
]

SEARCH_PATTERNS = ["/search", "/q/", "?q=", "?query="]


class ImprovedSemanticDetector:
    """
    Confidence-weighted semantic analysis with aggressive caching.
    ALL category definitions come from config/anchors.json
    """
    
    def __init__(
        self,
        api_key: str = None,
        cache_embeddings: bool = True,
        max_retries: int = 2,
        confidence_threshold: float = 0.75,
        anchors_path: str = None,
        category_risk_path: str = None
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.cache_embeddings = cache_embeddings
        self.max_retries = max_retries
        self.confidence_threshold = confidence_threshold
        
        # Paths configuration
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if anchors_path is None:
            anchors_path = os.path.join(script_dir, "..", "config", "anchors.json")
        
        self.anchors_path = os.path.normpath(anchors_path)
        
        self.categories: Dict[str, List[str]] = {}
        self.category_embeddings: Dict[str, Dict[str, Any]] = {}
        
        self.embedding_cache_path = "embedding_cache.json"
        self.offline_mode = False
        self._domain_cache = {}  # Domain-only cache (no URL)
        
        if self.cache_embeddings:
            self._load_embedding_cache()
        
        self._load_knowledge_base()
        
        try:
            self._generate_category_embeddings()
        except Exception as e:
            print(f"⚠ API failed, switching to offline mode: {e}")
            self.offline_mode = True
    
    # ==================== CACHE ====================
    
    def _load_embedding_cache(self):
        """Load pre-computed category embeddings"""
        try:
            with open(self.embedding_cache_path, "r") as f:
                cache = json.load(f)
                for cat, data in cache.items():
                    data["embedding"] = np.array(data["embedding"])
                self.category_embeddings = cache
                print(f"✅ Loaded {len(cache)} cached category embeddings")
        except Exception:
            print("ℹ No embedding cache found")
    
    def _save_embedding_cache(self):
        """Save category embeddings to disk"""
        if not self.cache_embeddings:
            return
        
        cache = {
            k: {
                "embedding": v["embedding"].tolist(),
                "domains": v["domains"]
            }
            for k, v in self.category_embeddings.items()
        }
        
        with open(self.embedding_cache_path, "w") as f:
            json.dump(cache, f)
    
    # ==================== KNOWLEDGE BASE ====================
    
    def _load_knowledge_base(self):
        """
        Load anchor domains and risk mappings from config files.
        This is the SINGLE SOURCE OF TRUTH for all category definitions.
        """
        # Load anchors (domain categories)
        try:
            with open(self.anchors_path, "r") as f:
                self.categories = json.load(f)
            print(f"✅ Loaded {len(self.categories)} categories from {self.anchors_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load anchors.json: {e}")
        
        # Load category risk mappings (optional - will use defaults if not present)
        try:
            with open(self.category_risk_path, "r") as f:
                self.category_risks = json.load(f)
            print(f"✅ Loaded risk mappings for {len(self.category_risks)} categories")
        except FileNotFoundError:
            # Generate default risk mappings based on category names
            print(f"ℹ No category_risks.json found, using default risk heuristics")
            self.category_risks = self._generate_default_risks()
        except Exception as e:
            print(f"⚠ Error loading category risks: {e}, using defaults")
            self.category_risks = self._generate_default_risks()
    
    def _generate_default_risks(self) -> Dict[str, float]:
        """
        Generate default risk scores based on category names.
        This is a fallback when category_risks.json doesn't exist.
        """
        risk_keywords = {
            # High risk (0.8-0.95)
            "anonymous": 0.85,
            "file_transfer": 0.90,
            "exfiltration": 0.95,
            
            # Medium-high risk (0.7-0.8)
            "ai": 0.90,
            "chatbot": 0.90,
            "generative": 0.90,
            "coding": 0.90,
            "transcription": 0.90,
            "cloud_storage": 0.90,
            "unapproved": 0.90,
            
            # Medium risk (0.5-0.7)
            "collaboration": 0.60,
            "messaging": 0.60,
            "productivity": 0.65,
            "media": 0.60,
            "content_creation": 0.60,
            
            # Lower risk (0.4-0.5)
            "consumer": 0.45,
            "saas": 0.45,
        }
        
        default_risks = {}
        
        for category in self.categories.keys():
            # Start with moderate default
            risk = 0.60
            
            # Check for risk keywords in category name
            cat_lower = category.lower()
            for keyword, keyword_risk in risk_keywords.items():
                if keyword in cat_lower:
                    risk = max(risk, keyword_risk)
            
            default_risks[category] = risk
        
        return default_risks
    
    # ==================== EMBEDDINGS ====================
    
    def _normalize_domain(self, domain: str) -> str:
        """Extract clean domain from URL-like strings"""
        if "://" in domain:
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path
        
        domain = domain.lower().strip()
        
        if domain.startswith("www."):
            domain = domain[4:]
        
        domain = domain.split(":")[0]
        domain = domain.split("/")[0]
        
        return domain
    
    def _get_embedding_from_gcp(self, texts: List[str]) -> np.ndarray:
        """Get embeddings from self-hosted GCP VM"""
        embedding_api_url = os.getenv("EMBEDDING_API_URL")
        if not embedding_api_url:
            raise ValueError("EMBEDDING_API_URL not set")
        
        embeddings = []
        for text in texts:
            response = requests.post(
                embedding_api_url,
                params={"text": text},
                timeout=10
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"GCP Embedding API error: {response.text}")
            
            embedding = response.json()
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def _get_embedding_from_openrouter(self, texts: List[str]) -> np.ndarray:
        """Fallback: OpenRouter embeddings"""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY missing")
        
        response = requests.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "thenlper/gte-base",
                "input": texts
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise RuntimeError(response.text)
        
        data = response.json()["data"]
        return np.array([d["embedding"] for d in data])
    
    def _get_embedding(self, texts: List[str]) -> np.ndarray:
        """Get embeddings with GCP primary, OpenRouter fallback"""
        try:
            return self._get_embedding_from_gcp(texts)
        except Exception as gcp_error:
            print(f"⚠️ GCP failed: {gcp_error}, falling back to OpenRouter")
            return self._get_embedding_from_openrouter(texts)
    
    def _get_embedding_with_retry(self, texts: List[str]) -> np.ndarray:
        """Retry logic with exponential backoff"""
        for i in range(self.max_retries):
            try:
                return self._get_embedding(texts)
            except Exception as e:
                if i == self.max_retries - 1:
                    raise
                time.sleep((i + 1) * 1)
        
        raise RuntimeError("Embedding failed after retries")
    
    def _domain_to_text(self, domain: str) -> str:
        """Convert domain to semantic text for embedding"""
        text = domain.lower()
        text = (
            text.replace(".com", "")
                .replace(".io", "")
                .replace(".org", "")
                .replace(".net", "")
                .replace("-", " ")
                .replace(".", " ")
        )
        
        # Add context keywords for better matching
        if any(x in text for x in ["chat", "gpt", "ai", "claude", "bard"]):
            text += " artificial intelligence conversational assistant"
        elif any(x in text for x in ["drive", "dropbox", "box", "cloud"]):
            text += " file storage cloud sharing upload"
        elif any(x in text for x in ["proton", "tutanota", "temp", "anonymous"]):
            text += " anonymous private secure communication"
        
        return text
    
    def _generate_category_embeddings(self):
        """Generate embeddings for anchor categories (one-time setup)"""
        for category, domains in self.categories.items():
            if category in self.category_embeddings:
                continue
            
            texts = [self._domain_to_text(d) for d in domains]
            emb = self._get_embedding_with_retry(texts)
            
            self.category_embeddings[category] = {
                "embedding": np.mean(emb, axis=0),
                "domains": domains
            }
            
            print(f"✅ Generated embedding for {category}")
        
        self._save_embedding_cache()
    
    # ==================== SIMILARITY ====================
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def _compute_similarities(self, query_embedding: np.ndarray) -> Dict[str, float]:
        """Compute similarities against all category embeddings"""
        sims = {}
        
        for cat, data in self.category_embeddings.items():
            sims[cat] = self._cosine_similarity(
                query_embedding,
                data["embedding"]
            )
        
        return sims
    
    def _compute_similarities_offline(self, domain: str) -> Dict[str, float]:
        """Offline fallback: exact/suffix matching against anchors"""
        sims = {}
        domain = domain.lower().strip()
        
        for category, domains in self.categories.items():
            is_match = False
            for d in domains:
                d = d.lower().strip()
                if domain == d or domain.endswith("." + d):
                    is_match = True
                    break
            
            sims[category] = 0.92 if is_match else 0.08
        
        return sims
    
    # ==================== RISK CALCULATION ====================
    
    def _calculate_confidence_weighted_risk(
        self, 
        sims: Dict[str, float]
    ) -> Tuple[float, str, str]:
        """
        Calculate risk using actual similarity confidence and anchors-based categories.
        
        Returns:
            (risk_score, explanation, top_category)
        """
        if not sims:
            return 0.5, "No similarity data", "unknown"
        
        top_cat = max(sims, key=sims.get)
        confidence = sims[top_cat]
        
        # Get base risk from loaded category_risks (from config or defaults)
        base_risk = self.category_risks.get(top_cat, 0.60)
        
        # Weight risk by confidence
        if confidence >= self.confidence_threshold:
            # High confidence match
            final_risk = base_risk * confidence
            explanation = f"High-confidence {top_cat} match (similarity: {confidence:.2f})"
        elif confidence >= 0.60:
            # Medium confidence - reduce risk
            final_risk = base_risk * 0.6 * confidence
            explanation = f"Possible {top_cat} (moderate similarity: {confidence:.2f})"
        else:
            # Low confidence - minimal risk
            final_risk = 0.3 * confidence
            explanation = f"Low-confidence match (similarity: {confidence:.2f})"
        
        return final_risk, explanation, top_cat
    
    # ==================== CONTENT CONSUMPTION ====================
    
    @staticmethod
    def is_content_consumption(domain: str, url: str = "") -> bool:
        """Detect read-only informational access"""
        if not domain:
            return False
        
        lower_domain = domain.lower()
        
        if any(lower_domain == d or lower_domain.endswith("." + d) 
               for d in INFORMATIONAL_DOMAINS):
            return True
        
        if not url:
            return False
        
        lower_url = url.lower()
        
        if any(pattern in lower_url for pattern in SEARCH_PATTERNS):
            return True
        
        if any(pattern in lower_url for pattern in INFORMATIONAL_PATH_PATTERNS):
            return True
        
        return False
    
    # ==================== PUBLIC API ====================
    
    def analyze(self, domain: str, url: str = "") -> Dict[str, Any]:
        """
        Analyze domain risk with confidence-weighted scoring.
        Uses anchors.json as source of truth for all categories.
        """
        clean_domain = self._normalize_domain(domain)
        
        # Check domain-level cache
        if clean_domain in self._domain_cache:
            cached = self._domain_cache[clean_domain].copy()
            if ImprovedSemanticDetector.is_content_consumption(clean_domain, url):
                cached.update({
                    "risk_score": 0.1,
                    "top_category": "content_consumption",
                    "category_type": "informational",
                    "explanation": "Read-only informational content"
                })
            return cached
        
        # Content consumption fast path
        if ImprovedSemanticDetector.is_content_consumption(clean_domain, url):
            result = {
                "domain": clean_domain,
                "risk_score": 0.1,
                "top_category": "content_consumption",
                "category_type": "informational",
                "similarities": {},
                "explanation": "Read-only informational content",
                "confidence": 1.0
            }
            self._domain_cache[clean_domain] = result
            return result
        
        # Perform semantic analysis
        if self.offline_mode:
            sims = self._compute_similarities_offline(clean_domain)
        else:
            try:
                text = self._domain_to_text(clean_domain)
                emb = self._get_embedding_with_retry([text])[0]
                sims = self._compute_similarities(emb)
            except Exception as e:
                print(f"⚠ Embedding failed for '{clean_domain}', using offline: {e}")
                sims = self._compute_similarities_offline(clean_domain)
        
        # Calculate confidence-weighted risk
        risk, explanation, top_cat = self._calculate_confidence_weighted_risk(sims)
        
        result = {
            "domain": clean_domain,
            "risk_score": risk,
            "top_category": top_cat,
            "category_type": top_cat,  # Same as top_category now (from anchors)
            "similarities": sims,
            "explanation": explanation,
            "confidence": sims[top_cat] if sims else 0.0
        }
        
        # Cache by domain only
        self._domain_cache[clean_domain] = result
        
        return result


# ==================== TEST ====================

def test_improved_detector():
    """Test with various scenarios"""
    detector = ImprovedSemanticDetector()
    
    print(f"\n📋 Loaded Categories from anchors.json:")
    for cat, domains in detector.categories.items():
        risk = detector.category_risks.get(cat, 0.6)
        print(f"  - {cat}: {len(domains)} domains (base risk: {risk:.2f})")
    
    test_cases = [
        ("claude.ai", "/chat", "Known AI - should be high risk + high confidence"),
        ("unknown-ai-tool.com", "/api/chat", "Unknown AI - medium risk + low confidence"),
        ("google.com", "/search?q=test", "Search - should be safe"),
        ("wetransfer.com", "/upload", "Known file transfer - high risk"),
        ("github.com", "/repo/main", "Dev platform - moderate risk"),
    ]
    
    print("\n" + "="*70)
    print("IMPROVED SEMANTIC DETECTOR TEST")
    print("="*70 + "\n")
    
    for domain, url, description in test_cases:
        result = detector.analyze(domain, url)
        
        print(f"\n{description}")
        print(f"Domain: {domain}{url}")
        print(f"Risk Score: {result['risk_score']:.3f}")
        print(f"Confidence: {result.get('confidence', 0):.3f}")
        print(f"Category: {result['top_category']}")
        print(f"Explanation: {result['explanation']}")
        print("-" * 70)


if __name__ == "__main__":
    test_improved_detector()
