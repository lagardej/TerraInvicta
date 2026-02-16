"""
Clean command - Remove build directory
"""

import logging
import shutil
from pathlib import Path
from lib.performance import timed_command
from lib.core import get_project_root


@timed_command
def cmd_clean(args):
    """Remove build directory"""
    project_root = get_project_root()
    build_dir = project_root / "build"
    
    if not build_dir.exists():
        logging.info("Nothing to clean - build directory does not exist")
        print("Nothing to clean")
        return
    
    # Count files
    file_count = sum(1 for _ in build_dir.rglob('*') if _.is_file())
    
    # Remove entire directory
    shutil.rmtree(build_dir)
    
    logging.info("="*60)
    logging.info(f"[OK] Clean complete")
    logging.info(f"  Removed: build/ ({file_count} files)")
    print(f"\n[OK] Clean complete: build/ removed ({file_count} files)")
