import json
import re
from typing import Dict, Any, Tuple
from pathlib import Path


class RuleEngine:
    def __init__(
        self,
        anchors_path: str = "../config/anchors",
        blacklist_path: str = "../config/blacklist.json"
    ):
        self.anchors_path = Path(anchors_path)
        self.blacklist_path = Path(blacklist_path)

        self.blacklist = set()
        self.safe_domains = set()

        self._load_blacklist()

        self.suspicious_patterns = [
            r'temp-.*\.(com|io|net)',
            r'anonymous.*\.(com|io|org)',
            r'stealth.*\.(com|io|net)',
            r'leak.*\.(com|io|net)',
            r'.*-gpt\.(com|io|net)',
            r'ai-writer.*\.(com|io)',
        ]

        self.compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.suspicious_patterns
        ]

    def _load_blacklist(self):
        try:
            with open(self.blacklist_path, "r", encoding="utf-8") as f:
                domains = json.load(f)

            if isinstance(domains, list):
                self.blacklist.update(d.lower() for d in domains)

        except FileNotFoundError:
            print(f"⚠ Blacklist not found: {self.blacklist_path}")

        except json.JSONDecodeError:
            print("⚠ Invalid blacklist JSON format")

    def check_blacklist(self, domain: str) -> Tuple[bool, str]:
        if domain.lower() in self.blacklist:
            return True, f"Blacklisted domain detected: {domain}"
        return False, ""

    def check_file_size(self, size: int, threshold_mb: int = 10) -> Tuple[bool, str]:
        if size > threshold_mb * 1024 * 1024:
            return True, f"Large upload: {size / (1024 * 1024):.2f} MB"
        return False, ""

    def check_suspicious_patterns(self, domain: str, url: str) -> Tuple[bool, str]:
        full = domain + url
        for pattern in self.compiled_patterns:
            if pattern.search(domain) or pattern.search(full):
                return True, f"Suspicious pattern matched: {pattern.pattern}"
        return False, ""

    def check_unknown_domain(self, domain: str) -> Tuple[bool, str]:
        keywords = ["temp", "anonymous", "leak", "stealth"]
        for k in keywords:
            if k in domain.lower():
                return True, f"Unknown domain with keyword: {k}"
        return False, ""

    def analyze(self, log: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.0
        alerts = []
        reasons = []

        domain = log.get("domain", "")
        url = log.get("url", "")
        size = log.get("upload_size_bytes", 0)

        hit, msg = self.check_blacklist(domain)
        if hit:
            alerts.append("blacklist_hit")
            reasons.append(msg)
            score += 0.8

        hit, msg = self.check_file_size(size)
        if hit:
            alerts.append("large_upload")
            reasons.append(msg)
            score += 0.5

        hit, msg = self.check_suspicious_patterns(domain, url)
        if hit:
            alerts.append("suspicious_pattern")
            reasons.append(msg)
            score += 0.6

        hit, msg = self.check_unknown_domain(domain)
        if hit:
            alerts.append("unknown_domain")
            reasons.append(msg)
            score += 0.3

        return {
            "rule_score": min(score, 1.0),
            "rule_alerts": alerts,
            "rule_explanations": reasons
        }


def test_rule_engine():
    engine = RuleEngine()

    logs = [
        {"domain": "github.com", "url": "/repo", "upload_size_bytes": 1000},
        {"domain": "wetransfer.com", "url": "/upload", "upload_size_bytes": 20 * 1024 * 1024},
        {"domain": "stealth-gpt.io", "url": "/api/upload", "upload_size_bytes": 5 * 1024 * 1024},
    ]

    for log in logs:
        result = engine.analyze(log)
        print("\nDomain:", log["domain"])
        print("Score:", result["rule_score"])
        print("Alerts:", result["rule_alerts"])
        print("Reasons:", result["rule_explanations"])


if __name__ == "__main__":
    test_rule_engine()
