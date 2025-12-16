# TODO: Description of this file
# Status: Not Started
import json
import re
from typing import Dict, Any, Tuple
from pathlib import Path
from urllib.parse import urlparse


class RuleEngine:
    def __init__(self, blacklist_path: str = "../config/blacklist.json"):
        self.blacklist_path = Path(blacklist_path)

        self.blacklist = set()
        self.safe_ports = {80, 443}

        self._load_blacklist()

        # Suspicious domain naming patterns
        self.suspicious_patterns = [
            r"temp-.*\.(com|io|net)",
            r"anonymous.*\.(com|io|org)",
            r"stealth.*\.(com|io|net)",
            r".*-gpt\.(com|io|net)",
            r"ai-writer.*\.(com|io)",
        ]

        self.compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.suspicious_patterns
        ]

        # Suspicious URL path keywords
        self.suspicious_url_keywords = [
            "upload",
            "paste",
            "export",
            "share",
            "context",
            "api",
        ]

    # -------------------- LOAD BLACKLIST --------------------
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

    # -------------------- BLACKLIST --------------------
    def check_blacklist(self, domain: str) -> Tuple[bool, str]:
        if domain.lower() in self.blacklist:
            return True, f"Blacklisted domain detected: {domain}"
        return False, ""

    # -------------------- FILE SIZE --------------------
    def check_file_size(self, size: int, threshold_mb: int = 10) -> Tuple[bool, str]:
        if size > threshold_mb * 1024 * 1024:
            return True, f"Large upload: {size / (1024 * 1024):.2f} MB"
        return False, ""

    # -------------------- DOMAIN PATTERN --------------------
    def check_suspicious_patterns(self, domain: str, url: str) -> Tuple[bool, str]:
        full = domain + url
        for pattern in self.compiled_patterns:
            if pattern.search(domain) or pattern.search(full):
                return True, f"Suspicious pattern matched: {pattern.pattern}"
        return False, ""

    # -------------------- UNKNOWN DOMAIN --------------------
    def check_unknown_domain(self, domain: str) -> Tuple[bool, str]:
        keywords = ["temp", "anonymous", "leak", "stealth", "unknown"]
        for k in keywords:
            if k in domain.lower():
                return True, f"Unknown domain with keyword: {k}"
        return False, ""

    # -------------------- URL PATH --------------------
    def check_unusual_url(self, url: str) -> Tuple[bool, str]:
        lower_url = url.lower()
        for kw in self.suspicious_url_keywords:
            if kw in lower_url:
                return True, f"Suspicious URL path keyword detected: {kw}"
        return False, ""

    # -------------------- UNCOMMON PORT --------------------
    def check_uncommon_port(self, domain: str, url: str) -> Tuple[bool, str]:
        if "://" in url:
            parsed = urlparse(url)
        else:
            parsed = urlparse(f"http://{domain}{url}")

        port = parsed.port
        if port and port not in self.safe_ports:
            return True, f"Uncommon port detected: {port}"
        return False, ""

    # -------------------- MAIN ANALYSIS --------------------
    def analyze(self, log: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.0
        alerts = []
        reasons = []

        domain = log.get("domain", "")
        url = log.get("url", "")
        size = log.get("upload_size_bytes", 0)

        checks = [
            (self.check_blacklist(domain), 0.8, "blacklist_hit"),
            (self.check_file_size(size), 0.5, "large_upload"),
            (self.check_suspicious_patterns(domain, url), 0.6, "suspicious_pattern"),
            (self.check_unknown_domain(domain), 0.3, "unknown_domain"),
            (self.check_unusual_url(url), 0.4, "unusual_url_path"),
            (self.check_uncommon_port(domain, url), 0.4, "uncommon_port"),
        ]

        for (hit, msg), weight, label in checks:
            if hit:
                alerts.append(label)
                reasons.append(msg)
                score += weight

        return {
            "rule_score": min(score, 1.0),
            "rule_alerts": alerts,
            "rule_explanations": reasons,
        }


# ==================== MAIN FUNCTION ====================
def main():
    engine = RuleEngine()

    logs = [
        {
            "domain": "github.com",
            "url": "/repo",
            "upload_size_bytes": 1000,
        },
        {
            "domain": "wetransfer.com",
            "url": "/upload",
            "upload_size_bytes": 20 * 1024 * 1024,
        },
        {
            "domain": "stealth-gpt.io",
            "url": "https://stealth-gpt.io:8080/api/upload",
            "upload_size_bytes": 5 * 1024 * 1024,
        },
        {
            "domain": "chat.super-unknown-ai.io",
            "url": "https://chat.super-unknown-ai.io:9001/api/v1/upload_context",
            "upload_size_bytes": 5 * 1024 * 1024,
        },
    ]

    for log in logs:
        result = engine.analyze(log)

        print("\nDomain:", log["domain"])
        print("Score:", result["rule_score"])
        print("Alerts:", result["rule_alerts"])
        print("Reasons:", result["rule_explanations"])


if __name__ == "__main__":
    main()
