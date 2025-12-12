
import os
import time
import json
import csv
import argparse
import random
from datetime import datetime, timezone

try:
    import requests
except Exception:
    print("Missing dependency: requests. Install with pip install requests.")
    raise


COLLECTOR_URL = os.getenv("COLLECTOR_URL", "http://localhost:8000/ingest")
API_KEY = os.getenv("INGEST_API_KEY", None)

# Normal / safe domains
NORMAL_DOMAINS = [
    ("google.com", "/search?q=python", "GET", 0),
    ("stackoverflow.com", "/questions/123", "GET", 0),
    ("jira.company.com", "/browse/PRJ-101", "GET", 0),
    ("github.com", "/repos/example", "GET", 0),
    ("internal-wiki.company.com", "/page/42", "GET", 0),
]


SHADOW_IT_DOMAINS = [
    ("dropbox.com", "/upload", "POST", 15_000_000),
    ("wetransfer.com", "/send", "POST", 20_000_000),
    ("mega.nz", "/file/upload", "POST", 25_000_000),
    ("mediafire.com", "/upload", "POST", 10_000_000),
    ("pcloud.com", "/upload", "POST", 12_000_000),
    ("sendspace.com", "/upload", "POST", 8_000_000),
    ("file.io", "/upload", "POST", 6_000_000),
    ("transfer.sh", "/upload", "POST", 7_000_000),
    ("notion.so", "/api/v1/pages", "POST", 0),
    ("evernote.com", "/note/upload", "POST", 0),
    ("pastebin.com", "/post", "POST", 0),
    ("gist.github.com", "/gists", "POST", 0),
    ("discord.com", "/api/v9/channels/123/messages", "POST", 0),
]

# Shadow AI — known AI platforms + plausible fake AI domains for demo
SHADOW_AI_DOMAINS = [
    ("perplexity.ai", "/search", "GET", 0),
    ("poe.com", "/api/query", "POST", 1_000_000),
    ("you.com", "/api/gen", "POST", 2_000_000),
    ("writesonic.com", "/api/v1/generate", "POST", 4_000_000),
    ("jasper.ai", "/app/write", "POST", 5_000_000),
    ("copy.ai", "/api/generate", "POST", 3_000_000),
    ("rytr.me", "/api/v1/write", "POST", 2_500_000),
    ("textcortex.com", "/api/generate", "POST", 3_500_000),
    ("hotpot.ai", "/image/generate", "POST", 6_000_000),
    ("starryai.com", "/v1/generate", "POST", 4_500_000),
    ("nightcafe.studio", "/api/create", "POST", 4_000_000),
    # Fake / demo-only suspicious AI domains
    ("stealth-gpt-writer.com", "/api/v1/context", "POST", 5_000_000),
    ("chat.super-unknown-ai.io", "/api/generate", "POST", 5_242_880),
    ("supernova-ai-gen.io", "/api/v1/submit", "POST", 6_000_000),
    ("ghostscript-ai.app", "/v1/write", "POST", 3_700_000),
    ("data-leak-analyzer.ai", "/analyze", "POST", 2_200_000),
]

USERS = [
    "alice@company.com",
    "bob@company.com",
    "charlie@company.com",
    "dinesh@company.com",
    "esha@company.com",
]

# ---------------------------
# Helper functions
# ---------------------------
def build_event(user_id, domain, url, method, upload_size):
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "domain": domain,
        "url": url,
        "method": method,
        "upload_size_bytes": upload_size
    }

def send_to_collector(event):
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    try:
        r = requests.post(COLLECTOR_URL, json=event, headers=headers, timeout=5)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

# ---------------------------
# Main generator loop
# ---------------------------
def generate_once():
    # choose category with weights: mostly normal, some shadow IT, fewer shadow AI
    category = random.choices(["normal", "shadow_it", "shadow_ai"], weights=[75,20,5])[0]
    if category == "normal":
        domain, url, method, size = random.choice(NORMAL_DOMAINS)
    elif category == "shadow_it":
        domain, url, method, size = random.choice(SHADOW_IT_DOMAINS)
    else:
        domain, url, method, size = random.choice(SHADOW_AI_DOMAINS)

    user = random.choice(USERS)
    evt = build_event(user, domain, url, method, size)
    return evt, category

def write_jsonl(path, events):
    with open(path, "a", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

def write_csv(path, events):
    header = ["ts", "user_id", "domain", "url", "method", "upload_size_bytes"]
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        for e in events:
            writer.writerow({
                "ts": e["ts"],
                "user_id": e["user_id"],
                "domain": e["domain"],
                "url": e["url"],
                "method": e["method"],
                "upload_size_bytes": e["upload_size_bytes"]
            })

# ---------------------------
# CLI / Entrypoint
# ---------------------------
def main():
    p = argparse.ArgumentParser(description="Synthetic log generator for ShadowGuard AI")
    p.add_argument("--mode", choices=["send", "file", "csv"], default="file",
                   help="send = POST to collector, file = write JSONL, csv = write CSV")
    p.add_argument("--count", type=int, default=0, help="number of events to generate (0 = infinite for send/file modes)")
    p.add_argument("--rate", type=float, default=1.0, help="events per second (only applies to send mode and file when count=0)")
    p.add_argument("--out", type=str, default="simulated_logs.jsonl", help="output path for file/csv modes")
    args = p.parse_args()

    print("Synthetic Log Generator")
    print("Collector URL:", COLLECTOR_URL)
    if API_KEY:
        print("Using INGEST_API_KEY auth (from env)")

    events_buffer = []
    sent = 0
    try:
        while True:
            evt, category = generate_once()
            sent += 1

            if args.mode == "send":
                status, txt = send_to_collector(evt)
                print(f"[POST] {evt['domain']:30s} category={category:8s} status={status}")
            elif args.mode == "file":
                events_buffer.append(evt)
                # flush as we go to avoid large memory usage
                if len(events_buffer) >= 50:
                    write_jsonl(args.out, events_buffer)
                    print(f"Wrote {len(events_buffer)} events to {args.out}")
                    events_buffer = []
                else:
                    # occasional print
                    print(f"[FILE-BUF] {evt['domain']:30s} category={category:8s}")
            elif args.mode == "csv":
                events_buffer.append(evt)
                if len(events_buffer) >= 50:
                    write_csv(args.out, events_buffer)
                    print(f"Wrote {len(events_buffer)} events to {args.out} (csv)")
                    events_buffer = []
                else:
                    print(f"[CSV-BUF] {evt['domain']:30s} category={category:8s}")

            # termination condition
            if args.count and sent >= args.count:
                break

            # pacing
            if args.mode == "send":
                time.sleep(max(0, 1.0 / args.rate))
            else:
                # file/csv modes: if count==0, produce quickly; otherwise small sleep so file readable
                if args.count == 0:
                    time.sleep(max(0, 1.0 / args.rate))
                else:
                    time.sleep(0.01)

    finally:
        # flush remaining buffer
        if args.mode == "file" and events_buffer:
            write_jsonl(args.out, events_buffer)
            print(f"Final write {len(events_buffer)} events to {args.out}")
        if args.mode == "csv" and events_buffer:
            write_csv(args.out, events_buffer)
            print(f"Final write {len(events_buffer)} events to {args.out}")

        print("Generator finished. Total events produced:", sent)

if __name__ == "__main__":
    main()