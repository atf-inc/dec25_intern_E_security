#!/usr/bin/env python3
"""
Test script for context-aware risk scoring.
Tests key scenarios to validate false positive reduction.
"""

import json
import requests
import time

COLLECTOR_URL = "http://localhost:8000/logs"

# Test scenarios
test_cases = [
    {
        "name": "News Site GET (Should NOT Alert)",
        "log": {
            "ts": "2025-12-19T14:00:00Z",
            "user_id": "test_user@company.com",
            "domain": "nytimes.com",
            "url": "/article/world-news",
            "method": "GET",
            "upload_size_bytes": 0
        },
        "expected": "SAFE (no alert)"
    },
    {
        "name": "Times of India GET (Should NOT Alert)",
        "log": {
            "ts": "2025-12-19T14:01:00Z",
            "user_id": "test_user@company.com",
            "domain": "timesofindia.indiatimes.com",
            "url": "/world/article-12345",
            "method": "GET",
            "upload_size_bytes": 0
        },
        "expected": "SAFE (content consumption)"
    },
    {
        "name": "StackOverflow GET (Should NOT Alert)",
        "log": {
            "ts": "2025-12-19T14:02:00Z",
            "user_id": "test_user@company.com",
            "domain": "stackoverflow.com",
            "url": "/questions/12345",
            "method": "GET",
            "upload_size_bytes": 0
        },
        "expected": "SAFE (docs/learning)"
    },
    {
        "name": "Google Search GET (Should NOT Alert)",
        "log": {
            "ts": "2025-12-19T14:03:00Z",
            "user_id": "test_user@company.com",
            "domain": "google.com",
            "url": "/search?q=python+tutorial",
            "method": "GET",
            "upload_size_bytes": 0
        },
        "expected": "SAFE (search query)"
    },
    {
        "name": "ChatGPT Small POST (Lower Risk)",
        "log": {
            "ts": "2025-12-19T14:04:00Z",
            "user_id": "test_user@company.com",
            "domain": "chatgpt.com",
            "url": "/c/abc123",
            "method": "POST",
            "upload_size_bytes": 500000  # 500 KB
        },
        "expected": "MEDIUM (small upload to AI)"
    },
    {
        "name": "ChatGPT Large POST (SHOULD Alert)",
        "log": {
            "ts": "2025-12-19T14:05:00Z",
            "user_id": "test_user@company.com",
            "domain": "chatgpt.com",
            "url": "/c/def456",
            "method": "POST",
            "upload_size_bytes": 15728640  # 15 MB
        },
        "expected": "HIGH or CRITICAL (large upload to AI)"
    },
    {
        "name": "WeTransfer Large Upload (SHOULD Alert)",
        "log": {
            "ts": "2025-12-19T14:06:00Z",
            "user_id": "test_user@company.com",
            "domain": "wetransfer.com",
            "url": "/upload",
            "method": "POST",
            "upload_size_bytes": 104857600  # 100 MB
        },
        "expected": "CRITICAL (blacklisted + large upload)"
    },
    {
        "name": "GitHub GET (Should be SAFE)",
        "log": {
            "ts": "2025-12-19T14:07:00Z",
            "user_id": "test_user@company.com",
            "domain": "github.com",
            "url": "/repo/code",
            "method": "GET",
            "upload_size_bytes": 0
        },
        "expected": "SAFE (whitelisted + GET)"
    }
]


def send_test_log(test_case: dict):
    """Send a test log to the collector."""
    print(f"\n{'='*70}")
    print(f"Test: {test_case['name']}")
    print(f"Expected: {test_case['expected']}")
    print(f"{'='*70}")
    
    log = test_case["log"]
    print(f"Sending: {log['method']} to {log['domain']}")
    print(f"Upload Size: {log['upload_size_bytes'] / (1024*1024):.2f} MB")
    
    try:
        response = requests.post(
            COLLECTOR_URL,
            json=log,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Log sent successfully")
        else:
            print(f"⚠️  Status: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending log: {e}")
    
    # Wait for processing
    time.sleep(0.5)


def main():
    print("\n" + "="*70)
    print("CONTEXT-AWARE RISK SCORING TEST SUITE")
    print("="*70)
    
    print("\nThis script tests the context-aware risk scoring system.")
    print("Monitor the worker logs with: docker compose logs -f worker")
    print("\nPress Enter to start testing...")
    input()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\nTest {i}/{len(test_cases)}")
        send_test_log(test_case)
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "="*70)
    print("ALL TESTS SENT")
    print("="*70)
    print("\nCheck worker logs to verify:")
    print("1. News sites should NOT appear in alerts")
    print("2. Large uploads to AI tools SHOULD alert")
    print("3. Alert messages should be non-accusatory")
    print("\nCommand: docker compose logs worker | grep -i 'data exposure'")


if __name__ == "__main__":
    main()
