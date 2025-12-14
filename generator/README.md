# Generator Service

The Generator service creates synthetic network traffic logs for testing and development purposes. It simulates both legitimate and Shadow IT traffic patterns to validate detection capabilities.

## Overview

The generator produces realistic security logs with configurable ratios of:
- **Normal Events**: Legitimate corporate traffic (e.g., internal tools, approved services)
- **Shadow IT Events**: Unauthorized cloud services based on anchor categories
- **Blacklist Events**: Explicitly prohibited services

## Features

- ✅ Configurable event ratios (shadow IT, blacklist, normal)
- ✅ Realistic timestamp generation within configurable time ranges
- ✅ Simulated user pool with departments and risk profiles
- ✅ Batch generation with configurable delays
- ✅ Health check integration with collector service
- ✅ Detailed statistics and logging
- ✅ Sample mode for testing without sending

## Configuration Files

The generator loads configuration from `../config/`:
- **`anchors.json`**: Shadow IT service categories (generative_ai, file_storage, anonymous_services)
- **`blacklist.json`**: Explicitly prohibited services
- **`whitelist.json`**: Approved services (optional)

## Usage

### Basic Usage

Generate and send logs to the collector:

```bash
python3 generate_logs.py --url http://localhost:8000/logs
```

### Generate Sample Logs (Dry Run)

Preview logs without sending them:

```bash
python3 generate_logs.py --sample 5
```

### One-Time Batch Generation

Generate a specific number of logs and exit:

```bash
python3 generate_logs.py --url http://localhost:8000/logs --once --batch-size 20
```

### Continuous Generation

Generate logs continuously with custom settings:

```bash
python3 generate_logs.py \
  --url http://localhost:8000/logs \
  --num-logs 100 \
  --batch-size 10 \
  --delay 0.5 \
  --shadow-ratio 0.3 \
  --blacklist-ratio 0.1
```

## Command-Line Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--url` | `-u` | `http://localhost:8000/logs` | Collector service URL |
| `--num-logs` | `-n` | `unlimited` | Total number of logs to generate |
| `--batch-size` | `-b` | `50` | Number of logs per batch |
| `--delay` | `-d` | `1.0` | Delay between batches (seconds) |
| `--users` | | `10` | Number of simulated users |
| `--shadow-ratio` | | `0.3` | Ratio of shadow IT events (0.0-1.0) |
| `--blacklist-ratio` | | `0.1` | Ratio of blacklisted events (0.0-1.0) |
| `--sample` | | `0` | Print N sample logs without sending |
| `--once` | | `false` | Generate logs once and exit |
| `--verbose` | `-v` | `false` | Enable verbose logging |

## Log Schema

Each generated log contains:

```json
{
  "ts": "2025-12-14T12:00:00+00:00",
  "user_id": "U001@company.com",
  "domain": "chatgpt.com",
  "url": "/api/v1/chat",
  "method": "POST",
  "upload_size_bytes": 35781157
}
```

## Examples

### Testing with Docker Collector

```bash
# Start collector service
cd ..
docker-compose up -d redis collector

# Generate test logs
cd generator
python3 generate_logs.py \
  --url http://localhost:8000/logs \
  --num-logs 50 \
  --batch-size 10 \
  --delay 0.5
```

### High-Volume Testing

```bash
python3 generate_logs.py \
  --url http://localhost:8000/logs \
  --batch-size 100 \
  --delay 0.1 \
  --users 50
```

### Custom Event Distribution

```bash
# More shadow IT events for testing detection
python3 generate_logs.py \
  --url http://localhost:8000/logs \
  --shadow-ratio 0.5 \
  --blacklist-ratio 0.2 \
  --num-logs 100
```

## Output

The generator provides real-time statistics:

```
2025-12-14 12:19:56 - INFO - Loaded anchors: ['generative_ai', 'file_storage', 'anonymous_services']
2025-12-14 12:19:56 - INFO - Loaded 10 blacklisted services
2025-12-14 12:19:56 - INFO - Starting continuous log generation...
2025-12-14 12:19:56 - INFO - Batch sent: 10/10 | Total: 10 | Shadow IT: 3 | Blacklist: 1
2025-12-14 12:19:57 - INFO - Batch sent: 10/10 | Total: 20 | Shadow IT: 6 | Blacklist: 2
```

## Dependencies

- `requests>=2.31.0` - HTTP client for sending logs to collector

Install dependencies:
```bash
pip install -r requirements.txt
```

## Files

- `generate_logs.py` - Main log generation script
- `requirements.txt` - Python dependencies
- `README.md` - This documentation
