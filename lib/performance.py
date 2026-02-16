"""
Terra Invicta Advisory System - Performance Monitoring

Decorator and logging utilities for tracking command performance.
"""

import time
import logging
import functools
from pathlib import Path
from datetime import datetime


def timed_command(func):
    """Decorator to time command execution and log performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        command_name = func.__name__.replace('cmd_', '')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # Log to performance log
            log_performance(command_name, elapsed, success=True)
            
            # Console output
            if elapsed > 1.0:
                logging.warning(f"Performance: {command_name} took {elapsed:.2f}s (threshold: 1.0s)")
            else:
                logging.debug(f"Performance: {command_name} completed in {elapsed:.3f}s")
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            log_performance(command_name, elapsed, success=False, error=str(e))
            raise
    
    return wrapper


def log_performance(command: str, elapsed: float, success: bool = True, error: str = None):
    """Append performance metrics to performance log"""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    perf_log = log_dir / "performance.log"
    
    timestamp = datetime.now().isoformat()
    status = "SUCCESS" if success else "FAILED"
    
    with open(perf_log, 'a') as f:
        if error:
            f.write(f"{timestamp},{command},{elapsed:.3f},{status},{error}\n")
        else:
            f.write(f"{timestamp},{command},{elapsed:.3f},{status}\n")
