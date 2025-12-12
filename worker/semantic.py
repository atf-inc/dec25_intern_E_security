import json
import numpy as np
import os
import requests
from typing import Dict, Any, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass

class OpenRouterSimilarityDetector:
    def __init__(self, knowledge_base_path: str = "knowledge_base.json", api_key: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.knowledge_base_path = knowledge_base_path
        self.category_embeddings = {}
        self.categories = {}
        
        self._load_knowledge_base()
        self._generate_category_embeddings()
    
    def _load_knowledge_base(self):
        try:
            with open(self.knowledge_base_path, 'r') as f:
                self.categories = json.load(f)
        except:
            self.categories = {
                "ai_tools": ["chatgpt.com", "openai.com", "claude.ai", "anthropic.com", "bard.google.com"],
                "suspicious_patterns": ["temp-mail.org", "10minutemail.com", "bit.ly", "tinyurl.com"],
                "safe_saas": ["github.com", "slack.com", "discord.com", "notion.so", "google.com"],
                "file_sharing": ["drive.google.com", "dropbox.com", "box.com", "mega.nz"]
            }
    
    def _get_embedding(self, texts: List[str]) -> np.ndarray:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "thenlper/gte-base",
            "input": texts,
            "encoding_format": "float"
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API failed: {response.status_code}")
        
        result = response.json()
        return np.array([item['embedding'] for item in result['data']])
    
    def _domain_to_text(self, domain: str) -> str:
        clean_domain = domain.replace('.com', '').replace('.io', '').replace('.org', '').replace('.net', '')
        text = clean_domain.replace('-', ' ').replace('.', ' ')
        
        if any(x in text.lower() for x in ['chat', 'gpt', 'ai']):
            text += " artificial intelligence chat assistant"
        elif any(x in text.lower() for x in ['github', 'git']):
            text += " code repository development"
        elif any(x in text.lower() for x in ['slack', 'teams']):
            text += " team communication messaging"
        elif any(x in text.lower() for x in ['drive', 'dropbox']):
            text += " file sharing cloud storage"
        
        return text
    
    def _generate_category_embeddings(self):
        for category_name, domains in self.categories.items():
            if not domains:
                continue
            
            domain_texts = [self._domain_to_text(domain) for domain in domains]
            embeddings = self._get_embedding(domain_texts)
            avg_embedding = np.mean(embeddings, axis=0)
            
            self.category_embeddings[category_name] = {
                'embedding': avg_embedding,
                'domains': domains
            }
    
    def _compute_similarities(self, query_embedding: np.ndarray) -> Dict[str, float]:
        similarities = {}
        query_reshaped = query_embedding.reshape(1, -1)
        
        for category_name, category_data in self.category_embeddings.items():
            category_embedding = category_data['embedding'].reshape(1, -1)
            similarity = cosine_similarity(query_reshaped, category_embedding)[0][0]
            similarities[category_name] = float(similarity)
        
        return similarities
    
    def _calculate_risk_score(self, similarities: Dict[str, float]) -> Tuple[float, str]:
        if not similarities:
            return 0.5, "No matches"
        
        max_category = max(similarities, key=similarities.get)
        max_similarity = similarities[max_category]
        
        if max_category == 'ai_tools' and max_similarity > 0.7:
            risk_score = min(max_similarity * 1.2, 1.0)
            explanation = f"AI tools match ({max_similarity:.2f})"
        elif max_category == 'suspicious_patterns' and max_similarity > 0.6:
            risk_score = min(max_similarity * 1.3, 1.0)
            explanation = f"Suspicious pattern ({max_similarity:.2f})"
        elif max_category == 'safe_saas' and max_similarity > 0.7:
            risk_score = max(0.1, 1.0 - max_similarity)
            explanation = f"Safe SaaS ({max_similarity:.2f})"
        else:
            risk_score = max_similarity * 0.7 if max_similarity > 0.3 else 0.6
            explanation = f"{max_category} ({max_similarity:.2f})"
        
        return risk_score, explanation
    
    def analyze(self, domain: str, url: str = "") -> Dict[str, Any]:
        try:
            domain_text = self._domain_to_text(domain)
            if url and any(keyword in url.lower() for keyword in ['upload', 'api', 'chat', 'export']):
                domain_text += f" {url.replace('/', ' ')}"
            
            query_embedding = self._get_embedding([domain_text])[0]
            similarities = self._compute_similarities(query_embedding)
            risk_score, explanation = self._calculate_risk_score(similarities)
            
            return {
                'risk_score': risk_score,
                'explanation': explanation,
                'similarities': similarities,
                'top_category': max(similarities, key=similarities.get) if similarities else 'unknown'
            }
        except Exception as e:
            return {
                'risk_score': 0.5,
                'explanation': f'Analysis failed: {str(e)}',
                'similarities': {},
                'top_category': 'error'
            }

def test_detector():
    detector = OpenRouterSimilarityDetector()
    
    test_domains = [
        "github.com",
        "super-gpt-clone.com", 
        "chatgpt.com",
        "unknown-service.net"
    ]
    
    for domain in test_domains:
        result = detector.analyze(domain)
        print(f"{domain}: {result['risk_score']:.3f} - {result['explanation']}")

if __name__ == "__main__":
    test_detector()