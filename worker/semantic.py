import json
import numpy as np
import os
import requests
import time
from typing import Dict, Any, List, Tuple

# Load .env safely
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass


# Content consumption patterns (no embeddings needed)
INFORMATIONAL_DOMAINS = [
    "nytimes.com", "wsj.com", "reuters.com", "bloomberg.com", "cnn.com", "bbc.com",
    "theguardian.com", "forbes.com", "economist.com", "techcrunch.com", "theverge.com",
    "wikipedia.org", "britannica.com", "dictionary.com", "thesaurus.com",
    "stackoverflow.com", "stackexchange.com", "reddit.com", "medium.com", "dev.to", "hashnode.com",
    "github.com", "gitlab.com", "readthedocs.io", "gitbook.com",
    "google.com", "bing.com", "duckduckgo.com", "yahoo.com"
]

# Path-based informational markers (leading slash prevents matching inside other words)
INFORMATIONAL_PATH_PATTERNS = [
    "/docs", "/wiki", "/manual", "/guide", "/tutorial", "/documentation",
    "/help", "/support", "/faq", "/legal", "/privacy", "/terms"
]

SEARCH_PATTERNS = [
    "/search", "/q/", "?q=", "?query=", "?search=", "&q="
]


class OpenRouterSimilarityDetector:
    def __init__(
        self,
        api_key: str = None,
        cache_embeddings: bool = True,
        max_retries: int = 3
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.cache_embeddings = cache_embeddings
        self.max_retries = max_retries

        self.categories: Dict[str, List[str]] = {}
        self.category_embeddings: Dict[str, Dict[str, Any]] = {}

        self.embedding_cache_path = "embedding_cache.json"
        self.offline_mode = False
        self._result_cache = {}  # NEW: Domain-level analysis cache

        if self.cache_embeddings:
            self._load_embedding_cache()

        self._load_knowledge_base()

        try:
            self._generate_category_embeddings()
        except Exception as e:
            print(f"⚠ API failed, switching to offline mode: {e}")
            self.offline_mode = True
            self._setup_offline_embeddings()

    # ---------------- CACHE ----------------

    def _load_embedding_cache(self):
        try:
            with open(self.embedding_cache_path, "r") as f:
                cache = json.load(f)
                for cat, data in cache.items():
                    data["embedding"] = np.array(data["embedding"])
                self.category_embeddings = cache
                print("✅ Loaded cached embeddings")
        except Exception:
            print("ℹ No embedding cache found")

    def _save_embedding_cache(self):
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

    # ---------------- KNOWLEDGE BASE ----------------

    def _load_knowledge_base(self):
        # Get the absolute path to config/anchors.json relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        anchors_path = os.path.join(script_dir, "..", "config", "anchors.json")
        anchors_path = os.path.normpath(anchors_path)  # Normalize the path
        
        with open(anchors_path, "r") as f:
            self.categories = json.load(f)

        print(f"✅ Loaded anchors from {anchors_path}")

    # ---------------- EMBEDDINGS ----------------

    def _get_embedding(self, texts: List[str]) -> np.ndarray:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing")

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
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(response.text)

        data = response.json()["data"]
        return np.array([d["embedding"] for d in data])

    def _get_embedding_with_retry(self, texts: List[str]) -> np.ndarray:
        for i in range(self.max_retries):
            try:
                return self._get_embedding(texts)
            except Exception:
                time.sleep((i + 1) * 2)

        raise RuntimeError("Embedding failed after retries")

    def _domain_to_text(self, domain: str) -> str:
        text = domain.lower()
        text = (
            text.replace(".com", "")
                .replace(".io", "")
                .replace(".org", "")
                .replace(".net", "")
                .replace("-", " ")
                .replace(".", " ")
        )

        if any(x in text for x in ["chat", "gpt", "ai", "claude", "bard", "perplexity"]):
            text += " artificial intelligence generative ai assistant"
        elif any(x in text for x in ["drive", "dropbox", "box", "icloud", "onedrive"]):
            text += " file storage cloud sharing"
        elif any(x in text for x in ["proton", "tutanota", "temp", "hide"]):
            text += " anonymous private secure service"

        return text

    def _generate_category_embeddings(self):
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

    # ---------------- OFFLINE MODE ----------------

    def _setup_offline_embeddings(self):
        # Deprecated: We now use anchors.json directly
        pass

    def _compute_similarities_offline(self, domain: str) -> Dict[str, float]:
        """
        Compute similarity scores using exact/suffix matching against anchors.
        """
        sims = {}
        domain = domain.lower().strip()
        
        # Normalize domain (remove protocol/www)
        if domain.startswith("http://"):
            domain = domain[7:]
        elif domain.startswith("https://"):
            domain = domain[8:]
        if domain.startswith("www."):
            domain = domain[4:]
        domain = domain.split("/")[0]

        for category, domains in self.categories.items():
            # Check for match in this category
            is_match = False
            for d in domains:
                d = d.lower().strip()
                if domain == d or domain.endswith("." + d):
                    is_match = True
                    break
            
            # High score for match, low for non-match
            sims[category] = 0.95 if is_match else 0.05

        return sims

    # ---------------- NUMPY COSINE ----------------

    def _cosine_similarity_numpy(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def _compute_similarities(self, query_embedding: np.ndarray) -> Dict[str, float]:
        sims = {}

        for cat, data in self.category_embeddings.items():
            sims[cat] = self._cosine_similarity_numpy(
                query_embedding,
                data["embedding"]
            )

        return sims

    # ---------------- RISK LOGIC ----------------

    def _calculate_risk_score(self, sims: Dict[str, float]) -> Tuple[float, str, str]:
        """
        Calculate risk score from similarities.
        
        Returns:
            Tuple of (risk_score, explanation, category_type)
        """
        top_cat = max(sims, key=sims.get)
        score = sims[top_cat]
        
        # Map categories to risk levels and types (Aligned with anchors.json)
        category_mapping = {
            "generative_ai_chatbots": (0.8, "Generative AI chatbot", "ai_tool"),
            "media_content_creation": (0.6, "Content creation tool", "creative_tool"),
            "transcription_productivity": (0.7, "Transcription/productivity service", "productivity"),
            "coding_assistants": (0.7, "Coding assistant", "dev_tool"),
            "unapproved_cloud_storage": (0.7, "Unapproved cloud storage", "file_storage"),
            "messaging_collaboration": (0.6, "Messaging/collaboration tool", "collaboration"),
            "consumer_saas_tools": (0.5, "Consumer SaaS tool", "saas"),
            "file_transfer_anonymous": (0.9, "Anonymous file transfer", "file_transfer"),
            "anonymous_communication": (0.8, "Anonymous communication service", "anonymous")
        }
        
        if top_cat in category_mapping:
            risk, desc, cat_type = category_mapping[top_cat]
            return risk, f"{desc} (similarity: {score:.2f})", cat_type
        
        return 0.4, f"Unknown category (similarity: {score:.2f})", "unknown"

    # ---------------- PUBLIC API ----------------
    
    @staticmethod
    def is_content_consumption(domain: str, url: str = "") -> bool:
        """
        Detect if domain/URL represents content consumption (news, docs, search)
        using precise domain matching and path patterns.
        """
        if not domain:
            return False
            
        lower_domain = domain.lower()
        
        # 1. Exact or subdomain match for trusted informational domains
        if any(lower_domain == d or lower_domain.endswith("." + d) for d in INFORMATIONAL_DOMAINS):
            return True
        
        # Early exit for path/search checks if no URL is provided
        if not url:
            return False
            
        lower_url = url.lower()
            
        # 2. Check for search patterns in the URL path/query
        if any(pattern in lower_url for pattern in SEARCH_PATTERNS):
            return True
            
        # 3. Check for specific informational path markers
        if any(pattern in lower_url for pattern in INFORMATIONAL_PATH_PATTERNS):
            return True
            
        return False

    def analyze(self, domain: str, url: str = "") -> Dict[str, Any]:
        """
        Analyze domain risk using semantic similarity.
        """
        # 1. Check result cache
        if domain in self._result_cache:
            return self._result_cache[domain]

        # 2. Check for content consumption first (fast path)
        # Calling as static method to be consistent with decorator
        if OpenRouterSimilarityDetector.is_content_consumption(domain, url):
            return {
                "domain": domain,
                "risk_score": 0.1,
                "top_category": "content_consumption",
                "category_type": "informational",
                "similarities": {},
                "explanation": "Content consumption domain (news/docs/search)"
            }
        
        # Perform semantic analysis
        if self.offline_mode:
            sims = self._compute_similarities_offline(domain)
        else:
            try:
                text = self._domain_to_text(domain)
                emb = self._get_embedding_with_retry([text])[0]
                sims = self._compute_similarities(emb)
            except Exception as e:
                # Fall back to offline mode if embedding fails
                print(f"⚠ Embedding failed for '{domain}', using offline mode: {e}")
                sims = self._compute_similarities_offline(domain)

        risk, reason, cat_type = self._calculate_risk_score(sims)

        result = {
            "domain": domain,
            "risk_score": risk,
            "top_category": max(sims, key=sims.get) if sims else "unknown",
            "category_type": cat_type,
            "similarities": sims,
            "explanation": reason
        }
        
        # Save to result cache for instant reuse
        self._result_cache[domain] = result
        return result


# ---------------- TEST ----------------

def test_detector():
    detector = OpenRouterSimilarityDetector()

    test_domains = [
        "unknown-site.net",
        "claude.ai",
        "large language model prompt"
    ]

    for domain in test_domains:
        url = "/test/path"
        result = detector.analyze(domain, url)

        print("\n" + "=" * 50)
        print(f"Domain        : {result['domain']}")
        print(f"URL           : {url}")
        print(f"Top Category  : {result['top_category']}")
        print(f"Risk Score    : {result['risk_score']:.2f}")
        print("Similarities  :")

        for cat, sim in result["similarities"].items():
            print(f"  - {cat:20s}: {sim:.2f}")

        print(f"Explanation   : {result['explanation']}")




def consume_from_collector():
    """Consume real-time events from collector via Redis"""
    import redis
    
    # Initialize detector
    detector = OpenRouterSimilarityDetector()
    
    # Redis connection settings (should match collector config)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    
    print(f"🔌 Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}")
    
    try:
        # Create Redis client
        redis_client = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            decode_responses=True
        )
        
        # Test connection
        redis_client.ping()
        print("✅ Connected to Redis successfully")
        
        # Subscribe to events channel
        pubsub = redis_client.pubsub()
        pubsub.subscribe("events")
        
        print("👂 Listening for events on 'events' channel...")
        print("=" * 60)
        
        # Process incoming events
        for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    # Parse the event
                    event_data = json.loads(message["data"])
                    
                    # Extract domain from the log event
                    domain = event_data.get("domain")
                    user_id = event_data.get("user_id")
                    upload_size = event_data.get("upload_size_bytes", 0)
                    
                    if not domain:
                        continue
                    
                    print(f"\n📨 New Event Received:")
                    print(f"   User: {user_id}")
                    print(f"   Domain: {domain}")
                    print(f"   Upload Size: {upload_size} bytes")
                    
                    # Analyze the domain with semantic detector
                    result = detector.analyze(domain)
                    
                    print("\n🔍 Semantic Analysis:")
                    print(f"   Top Category  : {result['top_category']}")
                    print(f"   Risk Score    : {result['risk_score']:.2f}")
                    print(f"   Explanation   : {result['explanation']}")
                    print("   Similarities  :")
                    
                    for cat, sim in result["similarities"].items():
                        print(f"     - {cat:20s}: {sim:.2f}")
                    
                    print("=" * 60)
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse event: {e}")
                except Exception as e:
                    print(f"❌ Error processing event: {e}")
    
    except redis.ConnectionError:
        print("❌ Failed to connect to Redis")
        print(f"   Make sure Redis is running at {REDIS_HOST}:{REDIS_PORT}")
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down consumer...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        # Run in live mode (consume from Redis)
        consume_from_collector()
    else:
        # Run in test mode (hardcoded domains)
        print("ℹ Running in TEST MODE with hardcoded domains")
        print("ℹ Use '--live' flag to consume from collector\n")
        test_detector()