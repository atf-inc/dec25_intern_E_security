import json
import numpy as np
import os
import requests
import time
from typing import Dict, Any, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity

# Load .env safely
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass


class OpenRouterSimilarityDetector:
    def _init_(self,
        knowledge_base_path: str = "knowledge_base.json",
        api_key: str = None,
        cache_embeddings: bool = True,
        max_retries: int = 3
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.knowledge_base_path = knowledge_base_path
        self.cache_embeddings = cache_embeddings
        self.max_retries = max_retries

        self.categories = {}
        self.category_embeddings = {}
        self.embedding_cache_path = "embedding_cache.json"
        self.offline_mode = False

        if cache_embeddings:
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
                print("Loaded cached embeddings")
        except Exception:
            print("No embedding cache found")

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
        try:
            with open(self.knowledge_base_path, "r") as f:
                self.categories = json.load(f)
        except FileNotFoundError:
            self.categories = {
                "generative_ai": [
                    "chat.openai.com",
                    "bard.google.com",
                    "claude.ai",
                    "perplexity.ai",
                    "midjourney.com"
                ],
                "file_storage": [
                    "dropbox.com",
                    "drive.google.com",
                    "onedrive.live.com",
                    "box.com",
                    "icloud.com"
                ],
                "anonymous_services": [
                    "protonmail.com",
                    "tutanota.com",
                    "guerrillamail.com",
                    "tempmail.com",
                    "hide.me"
                ]
            }
            with open(self.knowledge_base_path, "w") as f:
                json.dump(self.categories, f, indent=2)

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
        text = text.replace(".com", "").replace(".io", "").replace(".org", "").replace(".net", "")
        text = text.replace("-", " ").replace(".", " ")

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
            print(f"Generated embedding for {category}")
        self._save_embedding_cache()

    # ---------------- OFFLINE ----------------

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

    # ---------------- SIMILARITY ----------------

    def _compute_similarities(self, query_embedding: np.ndarray) -> Dict[str, float]:
        sims = {}
        q = query_embedding.reshape(1, -1)
        for cat, data in self.category_embeddings.items():
            c = data["embedding"].reshape(1, -1)
            sims[cat] = float(cosine_similarity(q, c)[0][0])
        return sims

    def _calculate_risk_score(self, sims: Dict[str, float]) -> Tuple[float, str]:
        cat = max(sims, key=sims.get)
        score = sims[cat]

        if cat == "generative_ai":
            return 0.9, f"High-confidence AI service ({score:.2f})"
        if cat == "anonymous_services":
            return 0.6, f"Anonymous service ({score:.2f})"
        if cat == "file_storage":
            return 0.2, f"File storage ({score:.2f})"

        return 0.3, "Unknown"

    # ---------------- PUBLIC ----------------

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
    print("🔍 Testing Risk Detector")
    print("=" * 50)

    detector = OpenRouterSimilarityDetector()

    test_domains = [
        "chat.openai.com",
        "dropbox.com",
        "protonmail.com",
        "unknown-site.net",
        "claude.ai"
    ]

    for domain in test_domains:
        result = detector.analyze(domain)
        print(f"\n{domain}")
        for cat, sim in result["similarities"].items():
            print(f"  {cat}: {sim:.2f}")
        print(f"→ Category: {result['top_category']} | Risk: {result['risk_score']}")
        print(f"→ Reason: {result['explanation']}")


if _name_ == "_main_":
    test_detector()