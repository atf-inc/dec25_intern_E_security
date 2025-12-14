import argparse
import json
import logging
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)



@dataclass
class GeneratorConfig:
    """Configuration for the log generator."""
    collector_url: str = "http://localhost:8000/logs"
    num_users: int = 10
    logs_per_batch: int = 50
    batch_delay: float = 1.0
    shadow_it_ratio: float = 0.3
    blacklist_ratio: float = 0.1
    config_dir: Path = Path(__file__).parent.parent / "config"



NORMAL_DOMAINS = [
    "docs.company.com",
    "intranet.company.com",
    "hr.company.com",
    "github.company.com",
    "gitlab.company.com",
    "jira.company.com",
    "confluence.company.com",
    "sharepoint.company.com",
]


NORMAL_URLS = [
    "/api/v1/documents",
    "/api/v1/reports",
    "/api/v1/files",
    "/dashboard",
    "/projects",
    "/wiki",
    "/upload",
    "/download",
]


SHADOW_IT_URLS = [
    "/api/v1/upload",
    "/api/v1/chat",
    "/api/v1/generate",
    "/upload_context",
    "/share",
    "/sync",
    "/api/completions",
]


BLACKLIST_URLS = [
    "/api/v1/upload",
    "/api/v1/upload_context",
    "/upload_file",
    "/share_data",
    "/transfer",
    "/api/v1/export",
]


HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"]



class UserPool:
    """Manages simulated users."""
   
    def __init__(self, num_users: int):
        self.users: list[dict] = []
        self._generate_users(num_users)
   
    def _generate_users(self, num_users: int) -> None:
        """Generate a pool of users."""
        departments = ["Engineering", "Sales", "Marketing", "Finance", "HR", "IT", "Legal"]
       
        for i in range(num_users):
            user_id = f"U{str(i + 1).zfill(3)}"
            self.users.append({
                "user_id": user_id,
                "department": random.choice(departments),
                "risk_profile": random.choice(["low", "medium", "high"]),
            })
   
    def get_random_user(self) -> dict:
        return random.choice(self.users)
   
    def get_high_risk_user(self) -> dict:
        high_risk = [u for u in self.users if u["risk_profile"] == "high"]
        return random.choice(high_risk) if high_risk else self.get_random_user()



class ConfigLoader:
    """Loads and manages configuration files."""
   
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.anchors: dict = {}
        self.blacklist: list = []
        self.whitelist: list = []
        self._load_configs()
   
    def _load_configs(self) -> None:
        """Load all configuration files."""
        try:
            anchors_path = self.config_dir / "anchors.json"
            if anchors_path.exists():
                with open(anchors_path) as f:
                    self.anchors = json.load(f)
                logger.info(f"Loaded anchors: {list(self.anchors.keys())}")
           
            blacklist_path = self.config_dir / "blacklist.json"
            if blacklist_path.exists():
                with open(blacklist_path) as f:
                    self.blacklist = json.load(f)
                logger.info(f"Loaded {len(self.blacklist)} blacklisted services")
           
            whitelist_path = self.config_dir / "whitelist.json"
            if whitelist_path.exists():
                with open(whitelist_path) as f:
                    self.whitelist = json.load(f)
                logger.info(f"Loaded {len(self.whitelist)} whitelisted services")
               
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load configs: {e}")
            raise



class LogGenerator:
    """Generates synthetic log events matching the collector schema."""
   
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.config_loader = ConfigLoader(config.config_dir)
        self.user_pool = UserPool(config.num_users)
        self.stats = {"normal": 0, "shadow_it": 0, "blacklist": 0, "total": 0}
   
    def generate_timestamp(self, max_age_hours: int = 24) -> str:
        """Generate a realistic timestamp within the specified time range."""
        now = datetime.now(timezone.utc)
        offset = timedelta(
            hours=random.randint(0, max_age_hours),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        return (now - offset).isoformat()
   
    def generate_normal_event(self) -> dict:
        """Generate a normal/legitimate log event."""
        user = self.user_pool.get_random_user()
        self.stats["normal"] += 1
        self.stats["total"] += 1
       
        return {
            "ts": self.generate_timestamp(),
            "user_id": f"{user['user_id']}@company.com",
            "domain": random.choice(NORMAL_DOMAINS),
            "url": random.choice(NORMAL_URLS),
            "method": random.choice(HTTP_METHODS),
            "upload_size_bytes": random.randint(1024, 10485760),
        }
   
    def generate_shadow_it_event(self) -> dict:
        """Generate a shadow IT log event based on anchors."""
        user = self.user_pool.get_high_risk_user() if random.random() < 0.6 else self.user_pool.get_random_user()
       
        category = random.choice(list(self.config_loader.anchors.keys()))
        services = self.config_loader.anchors[category]
        service = random.choice(services)
       
        domain = service if "." in service else service.lower().replace(" ", "-") + ".io"
       
        self.stats["shadow_it"] += 1
        self.stats["total"] += 1
       
        return {
            "ts": self.generate_timestamp(),
            "user_id": f"{user['user_id']}@company.com",
            "domain": domain,
            "url": random.choice(SHADOW_IT_URLS),
            "method": random.choice(["POST", "PUT", "GET"]),
            "upload_size_bytes": random.randint(10240, 52428800),
        }
   
    def generate_blacklist_event(self) -> dict:
        """Generate a blacklisted service log event."""
        user = self.user_pool.get_high_risk_user()
        service = random.choice(self.config_loader.blacklist)
        domain = service if "." in service else service.lower().replace(" ", "-") + ".com"
       
        self.stats["blacklist"] += 1
        self.stats["total"] += 1
       
        return {
            "ts": self.generate_timestamp(),
            "user_id": f"{user['user_id']}@company.com",
            "domain": domain,
            "url": random.choice(BLACKLIST_URLS),
            "method": random.choice(["POST", "PUT"]),
            "upload_size_bytes": random.randint(52428800, 104857600),
        }
   
    def generate_log(self) -> dict:
        """Generate a single log event based on configured ratios."""
        rand = random.random()
       
        if rand < self.config.blacklist_ratio:
            return self.generate_blacklist_event()
        elif rand < (self.config.blacklist_ratio + self.config.shadow_it_ratio):
            return self.generate_shadow_it_event()
        else:
            return self.generate_normal_event()
   
    def generate_batch(self, count: int) -> list[dict]:
        """Generate a batch of log events."""
        return [self.generate_log() for _ in range(count)]
   
    def get_stats(self) -> dict:
        """Get generation statistics."""
        return self.stats.copy()
   
    def reset_stats(self) -> None:
        """Reset generation statistics."""
        self.stats = {"normal": 0, "shadow_it": 0, "blacklist": 0, "total": 0}



class LogSender:
    """Sends generated logs to the collector service."""
   
    def __init__(self, collector_url: str, timeout: int = 10):
        self.collector_url = collector_url
        self.timeout = timeout
        self.session = requests.Session()
        self.stats = {"success": 0, "failed": 0}
   
    def send_log(self, log: dict) -> bool:
        """Send a single log to the collector."""
        try:
            response = self.session.post(self.collector_url, json=log, timeout=self.timeout)
            response.raise_for_status()
            self.stats["success"] += 1
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to send log: {e}")
            self.stats["failed"] += 1
            return False
   
    def send_batch(self, logs: list[dict]) -> tuple[int, int]:
        """Send a batch of logs. Returns (success_count, failed_count)."""
        success = sum(1 for log in logs if self.send_log(log))
        failed = len(logs) - success
        return success, failed
   
    def check_health(self) -> bool:
        """Check if the collector service is healthy."""
        try:
            health_url = self.collector_url.replace("/logs", "/health")
            response = self.session.get(health_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
   
    def get_stats(self) -> dict:
        return self.stats.copy()



class GeneratorRunner:
    """Main runner for the log generator."""
   
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.generator = LogGenerator(config)
        self.sender = LogSender(config.collector_url)
        self.running = False
   
    def run_once(self, count: int) -> None:
        """Generate and send a specific number of logs."""
        logger.info(f"Generating {count} logs...")
       
        logs = self.generator.generate_batch(count)
        success, failed = self.sender.send_batch(logs)
       
        gen_stats = self.generator.get_stats()
        logger.info(
            f"Generated: {gen_stats['total']} | "
            f"Normal: {gen_stats['normal']} | "
            f"Shadow IT: {gen_stats['shadow_it']} | "
            f"Blacklist: {gen_stats['blacklist']}"
        )
        logger.info(f"Sent: {success} success, {failed} failed")
   
    def run_continuous(self, total_logs: Optional[int] = None) -> None:
        """Run continuous log generation."""
        self.running = True
        logs_sent = 0
       
        logger.info("Starting continuous log generation...")
        logger.info(f"Collector URL: {self.config.collector_url}")
        logger.info(f"Batch size: {self.config.logs_per_batch}")
        logger.info(f"Batch delay: {self.config.batch_delay}s")
       
        # Check collector health
        if not self.sender.check_health():
            logger.warning("Collector health check failed - proceeding anyway")
       
        try:
            while self.running:
                batch = self.generator.generate_batch(self.config.logs_per_batch)
                success, failed = self.sender.send_batch(batch)
                logs_sent += success
               
                logger.info(
                    f"Batch sent: {success}/{len(batch)} | "
                    f"Total: {logs_sent} | "
                    f"Shadow IT: {self.generator.stats['shadow_it']} | "
                    f"Blacklist: {self.generator.stats['blacklist']}"
                )
               
                if total_logs and logs_sent >= total_logs:
                    logger.info(f"Reached target of {total_logs} logs")
                    break
               
                time.sleep(self.config.batch_delay)
               
        except KeyboardInterrupt:
            logger.info("\nStopping log generation...")
    def _print_summary(self) -> None:
        gen_stats = self.generator.get_stats()
        send_stats = self.sender.get_stats()
       
        logger.info("=" * 50)
        logger.info("Generation Summary")
        logger.info("=" * 50)
        logger.info(f"Total generated: {gen_stats['total']}")
        logger.info(f"  - Normal events: {gen_stats['normal']}")
        logger.info(f"  - Shadow IT events: {gen_stats['shadow_it']}")
        logger.info(f"  - Blacklist events: {gen_stats['blacklist']}")
        logger.info(f"Successfully sent: {send_stats['success']}")
        logger.info(f"Failed to send: {send_stats['failed']}")
        logger.info("=" * 50)
   
    def print_sample(self, count: int = 5) -> None:
        logger.info(f"Generating {count} sample logs (not sending):")
        print("-" * 60)
        for _ in range(count):
            log = self.generator.generate_log()
            print(json.dumps(log, indent=2))
            print("-" * 60)



def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Synthetic Log Generator for ShadowGuard AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
   
    parser.add_argument(
        "-u", "--url",
        default="http://localhost:8000/logs",
        help="Collector service URL",
    )
    parser.add_argument(
        "-n", "--num-logs",
        type=int,
        default=None,
        help="Total number of logs to generate (default: unlimited)",
    )
    parser.add_argument(
        "-b", "--batch-size",
        type=int,
        default=50,
        help="Number of logs per batch",
    )
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=1.0,
        help="Delay between batches in seconds",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=10,
        help="Number of simulated users",
    )
    parser.add_argument(
        "--shadow-ratio",
        type=float,
        default=0.3,
        help="Ratio of shadow IT events (0.0-1.0)",
    )
    parser.add_argument(
        "--blacklist-ratio",
        type=float,
        default=0.1,
        help="Ratio of blacklisted events (0.0-1.0)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Print N sample logs without sending",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Generate logs once and exit",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
   
    return parser.parse_args()



def main() -> int:
    """Main entry point."""
    args = parse_args()
   
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
   
    # Validate ratios
    if args.shadow_ratio + args.blacklist_ratio > 1.0:
        logger.error("shadow-ratio + blacklist-ratio must not exceed 1.0")
        return 1
   
    # Create config
    config = GeneratorConfig(
        collector_url=args.url,
        num_users=args.users,
        logs_per_batch=args.batch_size,
        batch_delay=args.delay,
        shadow_it_ratio=args.shadow_ratio,
        blacklist_ratio=args.blacklist_ratio,
    )
   
    runner = GeneratorRunner(config)
   
    if args.sample > 0:
        runner.print_sample(args.sample)
        return 0
   
    if args.once:
        count = args.num_logs or args.batch_size
        runner.run_once(count)
        return 0
   
    runner.run_continuous(total_logs=args.num_logs)
    return 0



if __name__ == "__main__":
    sys.exit(main())