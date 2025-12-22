# Embedding API Testing Guide

This directory contains test scripts to validate the self-hosted embedding model running on a GCP VM instance.

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- Access to the GCP VM running the embedding model

## Getting the Embedding API URL

### Step 1: Navigate to GCP Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project from the dropdown

### Step 2: Find Your VM Instance

1. Navigate to **Compute Engine** → **VM instances**
   - Direct URL: `https://console.cloud.google.com/compute/instances`
2. Locate your embedding model VM (mxbai-embed-large-v1, new ones can be added as well for better compute power)

### Step 3: Get the External IP

1. Find the **External IP** column in the VM instances table
2. Copy the IP address (e.g., `<YOUR_VM_IP>`)

> ⚠️ **Note**: If External IP shows "None", your VM might be using internal networking only. You'll need to:
> - Add an external IP, OR
> - Access from within the same VPC network using the Internal IP

### Step 4: Construct the URL

The embedding API URL format is:
```
http://<EXTERNAL_IP>:8000/embed
```

Example:
```
http://<YOUR_VM_IP>:8000/embed
```

## Running the Tests

### Option 1: Using Environment Variable (Recommended)

```bash
# Set the environment variable and run
EMBEDDING_API_URL=http://<YOUR_VM_IP>:8000/embed python3 test.py
```

### Option 2: Export and Run

```bash
# Export the variable
export EMBEDDING_API_URL=http://<YOUR_VM_IP>:8000/embed

# Run the test
python3 test.py
```

### Option 3: Using .env File

Add to your `.env` file in the project root:
```
EMBEDDING_API_URL=http://<YOUR_VM_IP>:8000/embed
```

Then run from the project root:
```bash
cd testing && python3 test.py
```

## Test Suite Overview

The test script runs three tests:

| Test | Description |
|------|-------------|
| **Health Check** | Verifies the embedding service is running and responsive |
| **Embedding Generation** | Tests that embeddings are generated correctly (1024 dimensions) |
| **Latency Benchmark** | Measures average response time across 5 requests |

## Expected Output

```
==================================================
EMBEDDING API TEST SUITE
==================================================
API URL: http://<YOUR_VM_IP>:8000/embed

[TEST] Health Check
----------------------------------------
  Status: healthy
  Model: mxbai-embed-large-v1
  ✅ Health check PASSED

[TEST] Embedding Generation
----------------------------------------
  Input: 'chatgpt openai artificial intelligence'
  Response time: 4833ms
  Embedding length: 1024
  ✅ Embedding generation PASSED

[TEST] Latency Benchmark (5 requests)
----------------------------------------
  Average latency: 930ms
  ✅ Latency benchmark PASSED

==================================================
TEST SUMMARY
==================================================
All tests passed!
```

## Troubleshooting

### Connection Refused / Timeout

1. **Check if VM is running**: Go to GCP Console → Compute Engine → VM instances
2. **Check firewall rules**: Ensure port `8000` is open for ingress
   - Go to VPC Network → Firewall → Create rule allowing TCP:8000
3. **Check if embedding service is running on VM**:
   ```bash
   gcloud compute ssh YOUR_VM_NAME --command "curl localhost:8000/health"
   ```

### Wrong Embedding Dimensions

- Ensure the VM is running `mxbai-embed-large-v1` model (should return 1024 dimensions)

### High Latency (>5 seconds)

- Consider upgrading to a higher CPU/GPU VM instance
- Check VM resource utilization in GCP Console → Monitoring

## Switching VM Instances

If you deploy a new VM (e.g., with GPU or higher CPU), simply update the `EMBEDDING_API_URL`:

```bash
# Old CPU instance
EMBEDDING_API_URL=http://<YOUR_VM_IP>:8000/embed

# New GPU instance (example)
EMBEDDING_API_URL=http://<NEW_VM_IP>:8000/embed
```

**No code changes required** - the URL is fully configurable via environment variable.
