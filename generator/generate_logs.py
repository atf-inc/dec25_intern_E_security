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
