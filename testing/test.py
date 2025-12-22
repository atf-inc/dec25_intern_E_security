#!/usr/bin/env python3
"""
Embedding API Test Script

Tests the self-hosted embedding model.
Use this to verify the embedding VM is working correctly.

Usage:
    EMBEDDING_API_URL=http://your-vm-ip:8000/embed python testing/test.py

Troubleshooting:
    1. Connection refused -> Check if VM is running
    2. Timeout -> Check firewall rule (port 8000)
"""

import os
import sys
import time
import requests

EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL")

if not EMBEDDING_API_URL:
    print("ERROR: EMBEDDING_API_URL environment variable is not set")
    print("Usage: EMBEDDING_API_URL=http://your-vm-ip:8000/embed python test.py")
    exit(1)


def test_health():
    """Test if embedding service is healthy."""
    print("\n[TEST] Health Check")
    print("-" * 40)
    
    health_url = EMBEDDING_API_URL.replace("/embed", "/health")
    try:
        res = requests.get(health_url, timeout=10)
        res.raise_for_status()
        data = res.json()
        print(f"  Status: {data.get('status', 'unknown')}")
        print(f"  Model: {data.get('model', 'unknown')}")
        print("  ✅ Health check PASSED")
        return True
    except requests.exceptions.ConnectionError:
        print("  ❌ FAILED: Connection refused")
        print("  → Check if VM is running")
        return False
    except requests.exceptions.Timeout:
        print("  ❌ FAILED: Request timeout")
        print("  → Check firewall rule for port 8000")
        return False
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_embedding():
    """Test embedding generation."""
    print("\n[TEST] Embedding Generation")
    print("-" * 40)
    
    test_text = "chatgpt openai artificial intelligence"
    
    try:
        start = time.time()
        res = requests.post(
            EMBEDDING_API_URL,
            params={"text": test_text},
            timeout=30
        )
        elapsed = (time.time() - start) * 1000
        
        res.raise_for_status()
        embedding = res.json()
        
        print(f"  Input: '{test_text}'")
        print(f"  Response time: {elapsed:.0f}ms")
        print(f"  Embedding length: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        
        if len(embedding) == 1024:
            print("  ✅ Embedding generation PASSED")
            return True
        else:
            print(f"  ⚠️ WARNING: Expected 1024 dims, got {len(embedding)}")
            return False
            
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_latency():
    """Measure average latency over multiple requests."""
    print("\n[TEST] Latency Benchmark (5 requests)")
    print("-" * 40)
    
    test_texts = [
        "dropbox file sharing",
        "google drive storage",
        "anonymous proxy vpn",
        "slack communication",
        "notion productivity"
    ]
    
    latencies = []
    for i, text in enumerate(test_texts):
        try:
            start = time.time()
            res = requests.post(
                EMBEDDING_API_URL,
                params={"text": text},
                timeout=30
            )
            elapsed = (time.time() - start) * 1000
            latencies.append(elapsed)
            print(f"  [{i+1}] '{text}' → {elapsed:.0f}ms")
        except Exception as e:
            print(f"  [{i+1}] ❌ Failed: {e}")
    
    if latencies:
        avg = sum(latencies) / len(latencies)
        print(f"\n  Average latency: {avg:.0f}ms")
        if avg < 1500:
            print("  ✅ Latency benchmark PASSED")
            return True
        else:
            print("  ⚠️ WARNING: Latency higher than expected")
            return False
    return False


if __name__ == "__main__":
    print("=" * 50)
    print("EMBEDDING API TEST SUITE")
    print("=" * 50)
    print(f"API URL: {EMBEDDING_API_URL}")
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Embedding", test_embedding()))
    results.append(("Latency", test_latency()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed!"))
    sys.exit(0 if all_passed else 1)
