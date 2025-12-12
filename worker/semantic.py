
import json
import numpy as np
from typing import Dict, Any, List, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticEngine:
    def __init__(self, knowledge_base_path: str = "knowledge_base.json", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic engine.
        
        Args:
            knowledge_base_path: Path to knowledge base JSON
            model_name: Name of the sentence transformer model to use
        """
        self.knowledge_base_path = knowledge_base_path
        self.model_name = model_name
        self.model = None
        self.category_embeddings = {}
        self.categories = {}
        
        # Initialize model and embeddings
        self._load_model()
        self._load_knowledge_base()
        self._generate_category_embeddings()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_knowledge_base(self):
        """Load knowledge base categories."""
        try:
            with open(self.knowledge_base_path, 'r') as f:
                self.categories = json.load(f)
            logger.info(f"Loaded {len(self.categories)} categories from knowledge base")
        except FileNotFoundError:
            logger.error(f"Knowledge base file {self.knowledge_base_path} not found")
            self.categories = {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {self.knowledge_base_path}")
            self.categories = {}
    
    def _generate_category_embeddings(self):
        """Generate embeddings for all categories in the knowledge base."""
        if not self.model or not self.categories:
            logger.warning("Model or categories not loaded, skipping embedding generation")
            return
        
        logger.info("Generating category embeddings...")
        
        for category_name, domains in self.categories.items():
            if not domains:  # Skip empty categories
                continue
                
            # Create text representations for domains
            domain_texts = [self._domain_to_text(domain) for domain in domains]
            
            # Generate embeddings
            embeddings = self.model.encode(domain_texts)
            
            # Store average embedding for the category
            avg_embedding = np.mean(embeddings, axis=0)
            self.category_embeddings[category_name] = {
                'embedding': avg_embedding,
                'individual_embeddings': embeddings,
                'domains': domains
            }
            
            logger.info(f"Generated embeddings for category '{category_name}' with {len(domains)} domains")
    
    def _domain_to_text(self, domain: str) -> str:
        """
        Convert domain to descriptive text for better embedding quality.
        
        Args:
            domain: Domain name (e.g., 'chatgpt.com')
            
        Returns:
            Descriptive text for embedding
        """
        # Remove common suffixes
        clean_domain = domain.replace('.com', '').replace('.io', '').replace('.org', '').replace('.net', '')
        
        # Replace hyphens and dots with spaces
        text = clean_domain.replace('-', ' ').replace('.', ' ')
        
        # Add context based on domain patterns
        if 'chat' in text.lower() or 'gpt' in text.lower() or 'ai' in text.lower():
            text += " artificial intelligence chat assistant"
        elif 'github' in text.lower() or 'git' in text.lower():
            text += " code repository development"
        elif 'slack' in text.lower() or 'teams' in text.lower():
            text += " team communication messaging"
        elif 'drive' in text.lower() or 'dropbox' in text.lower() or 'box' in text.lower():
            text += " file sharing cloud storage"
        
        return text
    
    def _compute_similarity_scores(self, query_embedding: np.ndarray) -> Dict[str, float]:
        """
        Compute cosine similarity between query and all categories.
        
        Args:
            query_embedding: Embedding vector for the query domain
            
        Returns:
            Dictionary mapping category names to similarity scores
        """
        similarities = {}
        
        for category_name, category_data in self.category_embeddings.items():
            category_embedding = category_data['embedding'].reshape(1, -1)
            query_reshaped = query_embedding.reshape(1, -1)
            
            similarity = cosine_similarity(query_reshaped, category_embedding)[0][0]
            similarities[category_name] = float(similarity)
        
        return similarities
    
    def _calculate_risk_score(self, similarities: Dict[str, float]) -> Tuple[float, str]:
        """
        Calculate semantic risk score based on similarities.
        
        Args:
            similarities: Dictionary of category similarities
            
        Returns:
            Tuple of (risk_score, explanation)
        """
        # Get the highest similarity and its category
        if not similarities:
            return 0.5, "No category matches found"
        
        max_category = max(similarities, key=similarities.get)
        max_similarity = similarities[max_category]
        
        # Risk calculation logic:
        # - High similarity to ai_tools or suspicious_patterns = High risk
        # - High similarity to safe_saas = Low risk
        # - High similarity to file_sharing = Medium risk (depends on context)
        # - Low similarity to all categories = Medium risk (unknown)
        
        if max_category == 'ai_tools' and max_similarity > 0.7:
            risk_score = min(max_similarity * 1.2, 1.0)  # Boost AI tools risk
            explanation = f"High similarity to AI tools ({max_similarity:.2f})"
            
        elif max_category == 'suspicious_patterns' and max_similarity > 0.6:
            risk_score = min(max_similarity * 1.3, 1.0)  # Boost suspicious patterns
            explanation = f"High similarity to suspicious patterns ({max_similarity:.2f})"
            
        elif max_category == 'safe_saas' and max_similarity > 0.7:
            risk_score = max(0.1, 1.0 - max_similarity)  # Low risk for safe SaaS
            explanation = f"High similarity to safe SaaS ({max_similarity:.2f})"
            
        elif max_category == 'file_sharing' and max_similarity > 0.7:
            risk_score = 0.5  # Medium risk for file sharing
            explanation = f"High similarity to file sharing ({max_similarity:.2f})"
            
        else:
            # Unknown or low similarity to all categories
            if max_similarity < 0.3:
                risk_score = 0.6  # Medium-high risk for completely unknown
                explanation = f"Unknown domain pattern (max similarity: {max_similarity:.2f})"
            else:
                risk_score = max_similarity * 0.7  # Scale down medium similarities
                explanation = f"Moderate similarity to {max_category} ({max_similarity:.2f})"
        
        return risk_score, explanation
    
    def analyze(self, log_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze log event using semantic similarity.
        
        Args:
            log_event: Dictionary containing 'domain', 'url', etc.
            
        Returns:
            Dictionary with semantic analysis results
        """
        if not self.model:
            logger.error("Model not loaded")
            return {
                'semantic_score': 0.0,
                'semantic_explanation': 'Model not loaded',
                'category_similarities': {},
                'detected_category': 'unknown'
            }
        
        try:
            domain = log_event.get('domain', '')
            url = log_event.get('url', '')
            
            # Create text representation
            domain_text = self._domain_to_text(domain)
            
            # Add URL context if it contains interesting patterns
            if url and any(keyword in url.lower() for keyword in ['upload', 'api', 'chat', 'export']):
                domain_text += f" {url.replace('/', ' ')}"
            
            # Generate embedding for the query
            query_embedding = self.model.encode([domain_text])[0]
            
            # Compute similarities
            similarities = self._compute_similarity_scores(query_embedding)
            
            # Calculate risk score
            risk_score, explanation = self._calculate_risk_score(similarities)
            
            # Determine detected category
            detected_category = max(similarities, key=similarities.get) if similarities else 'unknown'
            
            return {
                'semantic_score': risk_score,
                'semantic_explanation': explanation,
                'category_similarities': similarities,
                'detected_category': detected_category,
                'query_text': domain_text
            }
            
        except Exception as e:
            logger.error(f"Error in semantic analysis: {e}")
            return {
                'semantic_score': 0.5,
                'semantic_explanation': f'Analysis failed: {str(e)}',
                'category_similarities': {},
                'detected_category': 'error'
            }

# Test function
def test_semantic_engine():
    """Test the semantic engine with sample data."""
    try:
        engine = SemanticEngine()
        
        test_logs = [
            {
                'domain': 'github.com',
                'url': '/user/repo'
            },
            {
                'domain': 'stealth-ai-writer.io',
                'url': '/api/chat'
            },
            {
                'domain': 'super-gpt-clone.com',
                'url': '/upload'
            },
            {
                'domain': 'unknown-service.net',
                'url': '/data/export'
            }
        ]
        
        for i, log in enumerate(test_logs, 1):
            print(f"\nTest {i}: {log['domain']}")
            result = engine.analyze(log)
            print(f"Score: {result['semantic_score']:.3f}")
            print(f"Explanation: {result['semantic_explanation']}")
            print(f"Category: {result['detected_category']}")
            print(f"Similarities: {result['category_similarities']}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_semantic_engine()