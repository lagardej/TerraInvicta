"""
Run command - Launch KoboldCpp with selected model quality
"""

import logging
import os
import subprocess
from pathlib import Path

from src.core.core import load_env


def cmd_run(args):
    """Launch KoboldCpp"""
    # Import inject here to avoid circular dependency
    from inject.command import cmd_inject

    # Generate context first
    cmd_inject(args)

    env = load_env()
    kobold_dir = env.get('KOBOLDCPP_DIR')

    # Determine model based on quality tier
    quality = args.quality if hasattr(args, 'quality') and args.quality else env.get('KOBOLDCPP_QUALITY', 'base')
    quality_upper = quality.upper()
    model_key = f'KOBOLDCPP_MODEL_{quality_upper}'
    model_path = env.get(model_key)

    if not model_path:
        logging.error(f"No model configured for quality '{quality}'")
        logging.error(f"Add {model_key} to .env")
        return 1

    port = env.get('KOBOLDCPP_PORT', '5001')
    gpu_backend = env.get('KOBOLDCPP_GPU_BACKEND', 'clblast')
    gpu_layers = env.get('KOBOLDCPP_GPU_LAYERS', '35')
    context_size = env.get('KOBOLDCPP_CONTEXT_SIZE', '16384')
    threads = env.get('KOBOLDCPP_THREADS', '8')

    if not kobold_dir or not model_path:
        logging.error("KOBOLDCPP_DIR or model path not set in .env")
        return 1

    # Expand ~ paths for Linux
    kobold_dir = os.path.expanduser(kobold_dir)
    model_path = os.path.expanduser(model_path)

    kobold_exe = Path(kobold_dir) / "koboldcpp.exe"
    if not kobold_exe.exists():
        kobold_exe = Path(kobold_dir) / "koboldcpp"  # Linux

    # Build command with GPU backend selection
    cmd = [
        str(kobold_exe),
        "--model", model_path,
        "--port", port,
        "--contextsize", context_size,
        "--threads", threads
    ]

    # Add GPU backend
    if gpu_backend == 'clblast':
        cmd.append("--useclblast")
    elif gpu_backend == 'vulkan':
        cmd.append("--usevulkan")
    elif gpu_backend == 'cublas':
        cmd.append("--usecublas")

    # Add GPU layers
    if gpu_layers:
        cmd.extend(["--gpulayers", gpu_layers])

    logging.info(f"Starting KoboldCpp on port {port}")
    logging.info(f"Quality: {quality} ({Path(model_path).name})")
    logging.info(f"GPU: {gpu_backend}, Layers: {gpu_layers}, Context: {context_size}")
    print(f"\nLaunching KoboldCpp (Quality: {quality})")
    print(f"  Model: {Path(model_path).name}")
    print(f"  GPU: {gpu_backend}, {gpu_layers} layers")
    print(f"  Port: {port}\n")

    subprocess.run(cmd, cwd=kobold_dir)
