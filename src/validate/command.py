"""
Validate command - Verify configuration and paths
"""

import os
from pathlib import Path

from src.core.core import load_env, get_project_root
from src.perf.performance import timed_command


@timed_command
def cmd_validate(args):
    """Validate configuration and paths"""
    print("Terra Invicta Advisory System - Configuration Validation")
    print("=" * 60)

    project_root = get_project_root()
    errors = []
    warnings = []

    # Check .env exists
    env_file = project_root / ".env"
    if not env_file.exists():
        errors.append(".env file not found. Run: tias.py install")
        print("\n[FAIL] .env file missing")
        print("  Run: python tias.py install")
        return 1

    print("[OK] .env file found")

    # Load and validate .env
    try:
        env = load_env()
    except SystemExit:
        return 1

    # Validate game installation
    print("\nValidating game installation...")
    game_dir = Path(os.path.expanduser(env.get('GAME_INSTALL_DIR', '')))
    if not game_dir.exists():
        errors.append(f"Game directory not found: {game_dir}")
        print(f"  [FAIL] Not found: {game_dir}")
    else:
        templates_dir = game_dir / "TerraInvicta_Data/StreamingAssets/Templates"
        if not templates_dir.exists():
            errors.append(f"Templates directory not found: {templates_dir}")
            print(f"  [FAIL] Templates not found")
        else:
            print(f"  [OK] Game found: {game_dir}")

    # Validate saves directory
    print("\nValidating saves directory...")
    saves_dir = Path(os.path.expanduser(env.get('GAME_SAVES_DIR', '')))
    if not saves_dir.exists():
        errors.append(f"Saves directory not found: {saves_dir}")
        print(f"  [FAIL] Not found: {saves_dir}")
    else:
        savegames = list(saves_dir.glob('*.gz'))
        if not savegames:
            warnings.append(f"No savegames found in {saves_dir}")
            print(f"  [WARN] No savegames found")
        else:
            print(f"  [OK] Saves found: {len(savegames)} savegames")

    # Validate KoboldCpp
    print("\nValidating KoboldCpp...")
    kobold_dir = Path(os.path.expanduser(env.get('KOBOLDCPP_DIR', '')))
    if not kobold_dir.exists():
        errors.append(f"KoboldCpp directory not found: {kobold_dir}")
        print(f"  [FAIL] Not found: {kobold_dir}")
    else:
        kobold_exe = kobold_dir / "koboldcpp.exe"
        if not kobold_exe.exists():
            kobold_exe = kobold_dir / "koboldcpp"
        if not kobold_exe.exists():
            errors.append(f"KoboldCpp executable not found in {kobold_dir}")
            print(f"  [FAIL] Executable not found")
        else:
            print(f"  [OK] KoboldCpp found: {kobold_exe}")

    # Validate model  
    print("\nValidating model...")
    model_base_path = Path(os.path.expanduser(env.get('KOBOLDCPP_MODEL_BASE', '')))
    if not model_base_path.exists():
        errors.append(f"Base model file not found: {model_base_path}")
        print(f"  [FAIL] Not found: {model_base_path}")
    else:
        model_size = model_base_path.stat().st_size / 1024 / 1024 / 1024
        print(f"  [OK] Base model found: {model_base_path} ({model_size:.1f}GB)")

    # Check .gitignore
    print("\nValidating .gitignore...")
    gitignore_file = project_root / ".gitignore"
    if not gitignore_file.exists():
        warnings.append(".gitignore not found - .env might be committed")
        print(f"  [WARN] .gitignore not found")
    else:
        with open(gitignore_file) as f:
            gitignore_content = f.read()
        if '.env' not in gitignore_content and '*.env' not in gitignore_content:
            warnings.append(".env not in .gitignore - secrets might be committed")
            print(f"  [WARN] .env not in .gitignore")
        else:
            print(f"  [OK] .env properly ignored")

    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"[FAIL] Validation failed with {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    elif warnings:
        print(f"[OK] Validation passed with {len(warnings)} warning(s)")
        for warning in warnings:
            print(f"  - {warning}")
        return 0
    else:
        print("[OK] All checks passed!")
        print("\nReady to use:")
        print("  python tias.py build")
        print("  python tias.py parse --date YYYY-M-D")
        print("  python tias.py run --date YYYY-M-D")
        return 0
