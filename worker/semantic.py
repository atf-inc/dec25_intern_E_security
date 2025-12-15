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
        self.offline_keywords = {
            "generative_ai": ["ai", "gpt", "chat", "claude", "bard"],
            "file_storage": ["drive", "dropbox", "box", "icloud"],
            "anonymous_services": ["proton", "tutanota", "temp", "hide"]
        }

    def _compute_similarities_offline(self, domain: str) -> Dict[str, float]:
        sims = {}
        d = domain.lower()

        for cat, keys in self.offline_keywords.items():
            sims[cat] = 0.8 if any(k in d for k in keys) else 0.1

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

    def _calculate_risk_score(self, sims: Dict[str, float]) -> Tuple[float, str]:
        top_cat = max(sims, key=sims.get)
        score = sims[top_cat]

        if top_cat == "generative_ai":
            return 0.9, f"High-confidence AI service ({score:.2f})"
        if top_cat == "anonymous_services":
            return 0.6, f"Anonymous service ({score:.2f})"
        if top_cat == "file_storage":
            return 0.2, f"File storage ({score:.2f})"

        return 0.3, "Unknown"

    # ---------------- PUBLIC API ----------------

    def analyze(self, domain: str) -> Dict[str, Any]:
        if self.offline_mode:
            sims = self._compute_similarities_offline(domain)
        else:
            text = self._domain_to_text(domain)
            emb = self._get_embedding_with_retry([text])[0]
            sims = self._compute_similarities(emb)

        risk, reason = self._calculate_risk_score(sims)

        return {
            "domain": domain,
            "risk_score": risk,
            "top_category": max(sims, key=sims.get),
            "similarities": sims,
            "explanation": reason
        }


# ---------------- TEST ----------------

def test_detector():
    detector = OpenRouterSimilarityDetector()

    test_domains = [
        "unknown-site.net",
        "claude.ai",
        "large language model prompt"
    ]

    for domain in test_domains:
        result = detector.analyze(domain)

        print("\n" + "=" * 50)
        print(f"Domain        : {result['domain']}")
        print(f"Top Category  : {result['top_category']}")
        print(f"Risk Score   : {result['risk_score']}")
        print("Similarities :")

        for cat, sim in result["similarities"].items():
            print(f"  - {cat:20s}: {sim:.2f}")

        print(f"Explanation  : {result['explanation']}")




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