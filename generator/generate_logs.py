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
