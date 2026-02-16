"""
Terra Invicta Advisory System - Core Utilities

Shared utilities for environment loading, logging, and path management.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime


def setup_logging(verbosity: int):
    """Configure logging based on verbosity level"""
    levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    level = levels.get(verbosity, logging.DEBUG)
    
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "terractl.log"
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler()
        ]
    )


def load_env():
    """Load .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    env = {}
    
    if not env_path.exists():
        logging.error(".env not found. Run: tias.py install")
        sys.exit(1)
    
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env[key.strip()] = value.strip()
    
    return env


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(__file__).parent.parent
