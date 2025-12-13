"""
Synthetic Log Generator for ShadowGuard AI

Generates realistic network traffic logs for testing Shadow IT detection.
Produces both legitimate and suspicious traffic patterns.
"""

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


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class GeneratorConfig:
    """Configuration for the log generator."""
    collector_url: str = "http://localhost:8000/logs"
    num_users: int = 10
    num_devices_per_user: int = 2
    logs_per_batch: int = 50
    batch_delay: float = 1.0
    shadow_it_ratio: float = 0.3  # 30% shadow IT events
    blacklist_ratio: float = 0.1  # 10% blacklisted events
    config_dir: Path = Path(__file__).parent.parent / "config"


# =============================================================================
# Event Templates
# =============================================================================

# Normal/legitimate events that should NOT trigger alerts
NORMAL_EVENTS = [
    # Office applications
    "Opened Microsoft Word",
    "Opened Microsoft Excel",
    "Opened Microsoft PowerPoint",
    "Opened Microsoft Outlook",
    "Opened Microsoft Teams",
    "Joined Teams meeting",
    "Sent email via Outlook",
    "Edited document in Word",
    "Created spreadsheet in Excel",
    
    # Development tools
    "Opened Visual Studio Code",
    "Opened PyCharm",
    "Pushed code to GitHub Enterprise",
    "Pulled code from GitLab",
    "Ran npm build",
    "Executed pytest",
    
    # Internal systems
    "Accessed company intranet",
    "Logged into HR portal",
    "Submitted expense report",
    "Viewed payroll information",
    "Accessed internal wiki",
    "Used company VPN",
    
    # Standard browsing
    "Visited stackoverflow.com",
    "Visited github.com",
    "Visited docs.microsoft.com",
    "Visited company website",
    "Searched on approved search engine",
    
    # File operations
    "Saved file to network drive",
    "Opened file from SharePoint",
    "Downloaded attachment from email",
    "Printed document",
    "Scanned document",
]

# Event templates for shadow IT (anchors-based)
SHADOW_IT_TEMPLATES = {
    "generative_ai": [
        "Visited {service}",
        "Accessed {service}",
        "Sent prompt to {service}",
        "Used AI chatbot interface at {service}",
        "Generated content using {service}",
        "Asked AI to write an essay",
        "Used large language model prompt",
        "Generated images using AI service",
        "Copied code from AI assistant at {service}",
        "Uploaded document to AI service {service}",
    ],
    "file_storage": [
        "Uploaded file to {service}",
        "Downloaded file from {service}",
        "Synced folder with {service}",
        "Shared link via {service}",
        "Accessed {service}",
        "Created shared folder on {service}",
        "Moved company files to {service}",
        "Backed up data to {service}",
    ],
    "anonymous_services": [
        "Sent email via {service}",
        "Created account on {service}",
        "Accessed {service}",
        "Used anonymous browsing via {service}",
        "Registered with temporary email {service}",
        "Enabled VPN connection to {service}",
    ],
}

# Event templates for blacklisted services (high risk)
BLACKLIST_TEMPLATES = [
    "Uploaded file to {service}",
    "Downloaded file from {service}",
    "Visited {service}",
    "Shared data via {service}",
    "Transferred files using {service}",
    "Accessed blocked site {service}",
    "Attempted upload to {service}",
    "Received file from {service}",
]

# Log sources
LOG_SOURCES = [
    "windows_agent",
    "mac_agent",
    "linux_agent",
    "proxy",
    "firewall",
    "endpoint_dlp",
    "network_monitor",
]

# Device types
DEVICE_TYPES = [
    "LAPTOP",
    "DESKTOP",
    "WORKSTATION",
    "MACBOOK",
    "THINKPAD",
]


# =============================================================================
# Data Generation Classes
# =============================================================================

class UserPool:
    """Manages simulated users and their devices."""
    
    def __init__(self, num_users: int, devices_per_user: int):
        self.users: list[dict] = []
        self._generate_users(num_users, devices_per_user)
    
    def _generate_users(self, num_users: int, devices_per_user: int) -> None:
        """Generate a pool of users with associated devices."""
        departments = ["Engineering", "Sales", "Marketing", "Finance", "HR", "IT", "Legal"]
        
        for i in range(num_users):
            user_id = f"U{str(i + 1).zfill(3)}"
            devices = []
            
            for j in range(devices_per_user):
                device_type = random.choice(DEVICE_TYPES)
                device_id = f"{device_type}-{user_id}-{j + 1}"
                devices.append(device_id)
            
            self.users.append({
                "user_id": user_id,
                "devices": devices,
                "department": random.choice(departments),
                "risk_profile": random.choice(["low", "medium", "high"]),
            })
    
    def get_random_user(self) -> dict:
        """Get a random user from the pool."""
        return random.choice(self.users)
    
    def get_high_risk_user(self) -> dict:
        """Get a high-risk user (more likely to generate shadow IT)."""
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
    """Generates synthetic log events."""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.config_loader = ConfigLoader(config.config_dir)
        self.user_pool = UserPool(config.num_users, config.num_devices_per_user)
        self.stats = {
            "normal": 0,
            "shadow_it": 0,
            "blacklist": 0,
            "total": 0,
        }
    
    def generate_timestamp(self, max_age_hours: int = 24) -> str:
        """Generate a realistic timestamp within the specified time range."""
        now = datetime.now(timezone.utc)
        offset = timedelta(
            hours=random.randint(0, max_age_hours),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        timestamp = now - offset
        return timestamp.isoformat()
    
    def generate_normal_event(self) -> dict:
        """Generate a normal/legitimate log event."""
        user = self.user_pool.get_random_user()
        device = random.choice(user["devices"])
        
        self.stats["normal"] += 1
        self.stats["total"] += 1
        
        return {
            "user_id": user["user_id"],
            "device_id": device,
            "event": random.choice(NORMAL_EVENTS),
            "source": random.choice(LOG_SOURCES),
            "timestamp": self.generate_timestamp(),
        }
    
    def generate_shadow_it_event(self) -> dict:
        """Generate a shadow IT log event based on anchors."""
        # High-risk users more likely to generate shadow IT
        user = self.user_pool.get_high_risk_user() if random.random() < 0.6 else self.user_pool.get_random_user()
        device = random.choice(user["devices"])
        
        # Pick a random category from anchors
        category = random.choice(list(self.config_loader.anchors.keys()))
        services = self.config_loader.anchors[category]
        service = random.choice(services)
        
        # Pick a template for this category
        templates = SHADOW_IT_TEMPLATES.get(category, ["Accessed {service}"])
        template = random.choice(templates)
        
        # Generate the event
        event = template.format(service=service)
        
        self.stats["shadow_it"] += 1
        self.stats["total"] += 1
        
        return {
            "user_id": user["user_id"],
            "device_id": device,
            "event": event,
            "source": random.choice(LOG_SOURCES),
            "timestamp": self.generate_timestamp(),
        }
    
    def generate_blacklist_event(self) -> dict:
        """Generate a blacklisted service log event."""
        user = self.user_pool.get_high_risk_user()
        device = random.choice(user["devices"])
        
        service = random.choice(self.config_loader.blacklist)
        template = random.choice(BLACKLIST_TEMPLATES)
        event = template.format(service=service)
        
        self.stats["blacklist"] += 1
        self.stats["total"] += 1
        
        return {
            "user_id": user["user_id"],
            "device_id": device,
            "event": event,
            "source": random.choice(LOG_SOURCES),
            "timestamp": self.generate_timestamp(),
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
