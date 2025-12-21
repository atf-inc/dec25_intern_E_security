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


if __name__ == "__main__":
    print("=" * 50)
    print("EMBEDDING API TEST")
    print("=" * 50)
    print(f"API URL: {EMBEDDING_API_URL}")
    
    test_health()
