#!/usr/bin/env python3
"""
ShadowGuard AI - Scenario-based Log Generator

Generates specific scenario logs for demo and testing.

Scenarios:
  shadow_ai  - Triggers semantic detection (Risk > 0.7)
  blacklist  - Triggers blacklist detection (Risk = 1.0)
  whitelist  - Safe domain, no alert expected (Risk = 0.0)

Usage:
  python generate_logs.py --type shadow_ai
  python generate_logs.py --type blacklist
  python generate_logs.py --type whitelist
  python generate_logs.py --type all
"""

import argparse
import sys
from datetime import datetime, timezone

import requests


# =============================================================================
# SCENARIO DEFINITIONS
# =============================================================================

SCENARIOS = {
    "shadow_ai": {
        "name": "Shadow AI Upload",
        "description": "User uploads sensitive data to unapproved AI service",
        "expected": "Semantic Engine flags it (Risk > 0.7)",
        "logs": [
            {
                "user_id": "U001@company.com",
                "domain": "claude.ai",
                "url": "/api/v1/upload_context",
                "method": "POST",
                "upload_size_bytes": 15_000_000,
            },
            {
                "user_id": "U002@company.com",
                "domain": "chat.openai.com",
                "url": "/api/completions",
                "method": "POST",
                "upload_size_bytes": 8_500_000,
            },
            {
                "user_id": "U003@company.com",
                "domain": "unapproved-ai-tool.io",
                "url": "/api/v1/generate",
                "method": "POST",
                "upload_size_bytes": 12_000_000,
            },
        ],
    },
    "blacklist": {
        "name": "Data Exfiltration (Blacklisted)",
        "description": "User uploads data to blacklisted file-sharing service",
        "expected": "Blacklist Engine flags instantly (Risk = 1.0)",
        "logs": [
            {
                "user_id": "U004@company.com",
                "domain": "rapidgator.net",
                "url": "/api/v1/upload",
                "method": "POST",
                "upload_size_bytes": 52_428_800,
            },
            {
                "user_id": "U005@company.com",
                "domain": "anonfiles.com",
                "url": "/upload_file",
                "method": "POST",
                "upload_size_bytes": 104_857_600,
            },
            {
                "user_id": "U006@company.com",
                "domain": "wetransfer.com",
                "url": "/api/v1/transfer",
                "method": "POST",
                "upload_size_bytes": 75_000_000,
            },
        ],
    },
    "whitelist": {
        "name": "False Positive Avoided (Whitelisted)",
        "description": "User accesses approved company domain",
        "expected": "Whitelist overrides detection (Risk = 0.0, NO alert)",
        "logs": [
            {
                "user_id": "U007@company.com",
                "domain": "docs.company.com",
                "url": "/api/v1/documents",
                "method": "POST",
                "upload_size_bytes": 5_000_000,
            },
            {
                "user_id": "U008@company.com",
                "domain": "drive.company.com",
                "url": "/api/v1/upload",
                "method": "POST",
                "upload_size_bytes": 10_000_000,
            },
        ],
    },
}


# =============================================================================
# LOG SENDER
# =============================================================================

class LogSender:
    """Sends logs to the collector service."""

    def __init__(self, collector_url: str, timeout: int = 10):
        self.collector_url = collector_url
        self.timeout = timeout
        self.session = requests.Session()

    def send(self, log: dict) -> bool:
        """Send a single log to the collector."""
        try:
            response = self.session.post(
                self.collector_url,
                json=log,
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Failed to send: {e}")
            return False

    def health_check(self) -> bool:
        """Check if collector is reachable."""
        try:
            health_url = self.collector_url.replace("/logs", "/health")
            response = self.session.get(health_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


# =============================================================================
# SCENARIO RUNNER
# =============================================================================

def run_scenario(scenario_type: str, sender: LogSender) -> bool:
    """Run a specific scenario."""
    if scenario_type not in SCENARIOS:
        print(f"[ERROR] Unknown scenario: {scenario_type}")
        return False

    scenario = SCENARIOS[scenario_type]

    print()
    print("=" * 60)
    print(f"  SCENARIO: {scenario['name']}")
    print("=" * 60)
    print(f"  Description: {scenario['description']}")
    print(f"  Expected: {scenario['expected']}")
    print("-" * 60)

    success_count = 0
    total = len(scenario["logs"])

    for i, log_template in enumerate(scenario["logs"], 1):
        log = {
            **log_template,
            "ts": datetime.now(timezone.utc).isoformat(),
        }

        print()
        print(f"  [{i}/{total}] Sending log...")
        print(f"       User: {log['user_id']}")
        print(f"       Domain: {log['domain']}")
        print(f"       URL: {log['url']}")
        print(f"       Method: {log['method']}")
        print(f"       Size: {log['upload_size_bytes']:,} bytes")

        if sender.send(log):
            print("       Status: SENT")
            success_count += 1
        else:
            print("       Status: FAILED")

    print()
    print("-" * 60)
    print(f"  Result: {success_count}/{total} logs sent successfully")
    print("=" * 60)

    return success_count == total


def run_all_scenarios(sender: LogSender) -> None:
    """Run all scenarios sequentially."""
    print()
    print("#" * 60)
    print("  RUNNING ALL DEMO SCENARIOS")
    print("#" * 60)

    results = {}
    for scenario_type in SCENARIOS:
        success = run_scenario(scenario_type, sender)
        results[scenario_type] = "PASS" if success else "FAIL"

    print()
    print("#" * 60)
    print("  SUMMARY")
    print("#" * 60)
    for scenario_type, result in results.items():
        status_icon = "[OK]" if result == "PASS" else "[FAIL]"
        print(f"  {status_icon} {scenario_type}")
    print("#" * 60)


# =============================================================================
# CLI
# =============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ShadowGuard AI - Scenario-based Log Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scenarios:
  shadow_ai   Triggers semantic detection (Risk > 0.7)
  blacklist   Triggers blacklist detection (Risk = 1.0)
  whitelist   Whitelist override, no alert (Risk = 0.0)
  all         Run all scenarios sequentially

Examples:
  python generate_logs.py --type shadow_ai
  python generate_logs.py --type blacklist
  python generate_logs.py --type whitelist
  python generate_logs.py --type all
  python generate_logs.py --type shadow_ai --url http://your-server:3000/collect/logs
        """,
    )

    parser.add_argument(
        "-t", "--type",
        choices=["shadow_ai", "blacklist", "whitelist", "all"],
        required=True,
        help="Scenario type to run",
    )

    parser.add_argument(
        "-u", "--url",
        default="http://localhost:3000/collect/logs",
        help="Collector URL (default: http://localhost:3000/collect/logs)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview logs without sending",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    print()
    print("=" * 60)
    print("  SHADOWGUARD AI - LOG GENERATOR")
    print("=" * 60)
    print(f"  Collector: {args.url}")
    print(f"  Scenario: {args.type}")

    # Dry run mode
    if args.dry_run:
        print("  Mode: DRY RUN (no logs sent)")
        print("-" * 60)
        
        scenarios_to_show = SCENARIOS.keys() if args.type == "all" else [args.type]
        
        for scenario_type in scenarios_to_show:
            scenario = SCENARIOS[scenario_type]
            print(f"\n  {scenario['name']}:")
            for log in scenario["logs"]:
                print(f"    - {log['domain']} ({log['method']} {log['url']})")
        
        return 0

    sender = LogSender(args.url)

    # Health check
    print()
    print("  Checking collector...")
    if sender.health_check():
        print("  Collector: ONLINE")
    else:
        print("  Collector: OFFLINE (proceeding anyway)")

    # Run scenario(s)
    if args.type == "all":
        run_all_scenarios(sender)
    else:
        run_scenario(args.type, sender)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
