

import json
import re
from typing import Dict, Any, Tuple
from urllib.parse import urlparse

class RuleEngine:
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        """Initialize the rule engine with blacklist and patterns."""
        self.knowledge_base_path = knowledge_base_path
        self.blacklist = set()
        self.safe_domains = set()
        self.load_knowledge_base()
        
        # Suspicious URL patterns
        self.suspicious_patterns = [
            r'temp-.*\.(com|io|net)',
            r'anonymous.*\.(com|io|org)',
            r'stealth.*\.(com|io|net)',
            r'leak.*\.(com|io|net)',
            r'upload.*anonymous',
            r'quick.*ai.*\.(com|io)',
            r'.*-gpt.*\.(com|io|net)',
            r'ai-writer.*\.(com|io)',
        ]
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                for pattern in self.suspicious_patterns]
    
    def load_knowledge_base(self):
        """Load knowledge base and populate blacklist and safe domains."""
        try:
            with open(self.knowledge_base_path, 'r') as f:
                kb = json.load(f)
            
            # Add suspicious patterns to blacklist
            if 'suspicious_patterns' in kb:
                self.blacklist.update(kb['suspicious_patterns'])
            
            # Add safe domains (for whitelisting)
            if 'safe_saas' in kb:
                self.safe_domains.update(kb['safe_saas'])
                
        except FileNotFoundError:
            print(f"Warning: Knowledge base file {self.knowledge_base_path} not found")
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {self.knowledge_base_path}")
    
    def check_blacklist(self, domain: str) -> Tuple[bool, str]:
        """Check if domain is in blacklist."""
        if domain.lower() in self.blacklist:
            return True, f"Domain {domain} found in blacklist"
        return False, ""
    
    def check_file_size(self, upload_size_bytes: int, threshold_mb: int = 10) -> Tuple[bool, str]:
        """Check if upload size exceeds threshold."""
        threshold_bytes = threshold_mb * 1024 * 1024
        if upload_size_bytes > threshold_bytes:
            size_mb = upload_size_bytes / (1024 * 1024)
            return True, f"Large upload detected: {size_mb:.2f}MB > {threshold_mb}MB"
        return False, ""
    
    def check_suspicious_patterns(self, domain: str, url: str) -> Tuple[bool, str]:
        """Check for suspicious patterns in domain or URL."""
        full_url = f"{domain}{url}"
        
        for pattern in self.compiled_patterns:
            if pattern.search(domain) or pattern.search(full_url):
                return True, f"Suspicious pattern detected: {pattern.pattern}"
        
        return False, ""
    
    def check_unknown_domain(self, domain: str) -> Tuple[bool, str]:
        """Check if domain is completely unknown (not in safe list)."""
        # Simple heuristic: if not in safe domains and looks suspicious
        if domain.lower() not in self.safe_domains:
            # Additional checks for unknown domains
            suspicious_keywords = ['temp', 'anonymous', 'leak', 'export', 'stealth']
            domain_lower = domain.lower()
            
            for keyword in suspicious_keywords:
                if keyword in domain_lower:
                    return True, f"Unknown domain with suspicious keyword: {keyword}"
        
        return False, ""
    
    def analyze(self, log_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze log event using rule-based checks.
        
        Returns:
        {
            'rule_score': float (0-1),
            'rule_alerts': list of triggered rules,
            'rule_explanations': list of explanations
        }
        """
        domain = log_event.get('domain', '')
        url = log_event.get('url', '')
        upload_size = log_event.get('upload_size_bytes', 0)
        
        alerts = []
        explanations = []
        score = 0.0
        
        # Check 1: Blacklist
        is_blacklisted, explanation = self.check_blacklist(domain)
        if is_blacklisted:
            alerts.append('blacklist_hit')
            explanations.append(explanation)
            score += 0.8  # High score for blacklist hit
        
        # Check 2: Large file uploads
        is_large_upload, explanation = self.check_file_size(upload_size)
        if is_large_upload:
            alerts.append('large_upload')
            explanations.append(explanation)
            score += 0.5  # Medium score for large uploads
        
        # Check 3: Suspicious patterns
        is_suspicious, explanation = self.check_suspicious_patterns(domain, url)
        if is_suspicious:
            alerts.append('suspicious_pattern')
            explanations.append(explanation)
            score += 0.6  # Medium-high score for suspicious patterns
        
        # Check 4: Unknown domain
        is_unknown, explanation = self.check_unknown_domain(domain)
        if is_unknown:
            alerts.append('unknown_domain')
            explanations.append(explanation)
            score += 0.3  # Low-medium score for unknown domains
        
        # Cap score at 1.0
        final_score = min(score, 1.0)
        
        return {
            'rule_score': final_score,
            'rule_alerts': alerts,
            'rule_explanations': explanations
        }

# Test function
def test_rule_engine():
    """Test the rule engine with sample data."""
    engine = RuleEngine()
    
    # Test cases
    test_logs = [
        {
            'domain': 'github.com',
            'url': '/user/repo',
            'upload_size_bytes': 1024
        },
        {
            'domain': 'stealth-gpt.io',
            'url': '/api/upload',
            'upload_size_bytes': 15 * 1024 * 1024  # 15MB
        },
        {
            'domain': 'temp-file-share.com',
            'url': '/upload',
            'upload_size_bytes': 2 * 1024 * 1024
        }
    ]
    
    for i, log in enumerate(test_logs, 1):
        result = engine.analyze(log)
        print(f"\nTest {i}: {log['domain']}")
        print(f"Score: {result['rule_score']}")
        print(f"Alerts: {result['rule_alerts']}")
        print(f"Explanations: {result['rule_explanations']}")

if __name__ == "__main__":
    test_rule_engine()