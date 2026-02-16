# TIAS Developer Reference Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Command Reference](#command-reference)
5. [Common Workflows](#common-workflows)
6. [Development](#development)
7. [Testing](#testing)
8. [Architecture](#architecture)

---

## Quick Start

```bash
# Clone and install
git clone <repo-url>
cd TerraInvicta
pip install -e .

# Setup
tias install

# Basic workflow
tias build
tias parse --date 2027-7-14
tias inject --date 2027-7-14
tias run --date 2027-7-14
```

---

## Project Structure

```
TerraInvicta/
├── src/                    # Source code (Python package)
│   ├── __main__.py        # Entry point (tias command)
│   ├── core/              # Core utilities
│   │   ├── core.py        # Logging, env, paths
│   │   └── date_utils.py  # Date parsing
│   ├── build/             # Build command
│   ├── clean/             # Clean command
│   ├── install/           # Install command
│   ├── parse/             # Parse command
│   ├── inject/            # Inject command
│   │   └── launch_windows.py  # Launch window calculations
│   ├── run/               # Run command
│   ├── validate/          # Validate command
│   └── perf/              # Performance tracking
│       └── performance.py
├── resources/             # Game data (actors, prompts)
│   ├── actors/           # AI advisor definitions
│   └── prompts/          # LLM prompts
├── tests/                # Test suite
├── build/                # Build output (gitignored)
├── generated/            # Generated context files
├── logs/                 # Application logs
├── docs/                 # Documentation
├── setup.py              # Package setup
├── pyproject.toml        # Project metadata
└── .env                  # Configuration (gitignored)
```

**Key Principles:**
- Each command is a self-contained package
- Code in `src/` NEVER imports from sibling packages (except `core`)
- All imports use absolute paths: `from src.core.core import ...`
- Resources in `resources/`, not `src/`

---

## Installation

### First Time Setup

```bash
# Install in editable mode
pip install -e .

# Verify installation
tias --help

# Configure paths and models
tias install
```

### Development Dependencies

```bash
pip install -e ".[dev]"  # Includes pytest, pytest-cov
```

### Uninstall

```bash
pip uninstall tias
```

---

## Command Reference

### Core Commands

#### `tias install`
Interactive setup wizard. Auto-detects paths and creates `.env` file.

```bash
tias install
```

#### `tias clean`
Removes `build/` directory (templates and databases).

```bash
tias clean
```

#### `tias build`
Builds game templates database from Terra Invicta installation.

```bash
tias build
```

**Output:**
- `build/actors/*.json` - Actor definitions
- `build/templates/*.json` - Game templates with localization
- `build/game_templates.db` - SQLite database

#### `tias validate`
Validates configuration and paths.

```bash
tias validate
```

**Checks:**
- `.env` exists
- Game installation found
- Saves directory found
- KoboldCpp found
- Model files exist

#### `tias parse`
Parses savegame into SQLite database.

```bash
tias parse --date 2027-7-14
tias parse --date 2027-07-14      # Also works
tias parse --date 14/07/2027      # Also works
```

**Output:** `build/savegame_2027_7_14.db`

#### `tias inject`
Generates LLM context from game data.

```bash
tias inject --date 2027-7-14
```

**Output:** `generated/mistral_context.txt`

#### `tias run`
Launches KoboldCpp with generated context.

```bash
tias run --date 2027-7-14
tias run --date 2027-7-14 --quality nuclear
```

**Quality tiers:** `base`, `max`, `nuclear`, `ridiculous`, `ludicrous`

#### `tias perf`
Shows performance statistics.

```bash
tias perf
```

---

## Common Workflows

### Full Clean Build

```bash
tias clean && tias build
```

### Complete Pipeline

```bash
# Parse savegame, generate context, launch LLM
tias parse --date 2027-7-14 && \
tias inject --date 2027-7-14 && \
tias run --date 2027-7-14
```

### Quick Context Regeneration

```bash
# Skip parse if savegame hasn't changed
tias inject --date 2027-7-14 && tias run --date 2027-7-14
```

### Testing Different Quality Tiers

```bash
# Test with different models
tias run --date 2027-7-14 --quality base
tias run --date 2027-7-14 --quality nuclear
tias run --date 2027-7-14 --quality ludicrous
```

### Validation Before Build

```bash
tias validate && tias build
```

### Build with Performance Tracking

```bash
tias clean && tias build && tias perf
```

---

## Development

### Design Principles

#### Robustness Principle (Postel's Law)
> *"Be conservative in what you do, be liberal in what you accept from others"*

This applies throughout the codebase:

| Aspect | Be liberal (accepting) | Be conservative (producing) |
|--------|----------------------|-----------------------------|
| **Dates** | Accept `YYYY-M-D`, `YYYY-MM-DD`, `DD/MM/YYYY` | Always output `YYYY_M_D` internally |
| **Paths** | Accept `str` or `Path`, with or without trailing slash | Always output `Path` objects |
| **Env vars** | Accept missing optional vars gracefully | Always validate required vars explicitly |
| **File search** | Match savegames flexibly (glob patterns) | Write filenames with consistent format |

**In practice:**

```python
# ✅ Liberal input: accept multiple date formats
game_date, normalized = parse_flexible_date(args.date)

# ✅ Conservative output: always produce consistent filenames
db_path = project_root / "build" / f"savegame_{normalized}.db"  # always YYYY_M_D

# ✅ Liberal input: accept str or Path
def find_savegame(saves_dir: Path, normalized_date: str) -> Path:
    if isinstance(saves_dir, str):  # accept both
        saves_dir = Path(saves_dir)

# ✅ Liberal input: tolerate missing optional env vars
quality = args.quality or env.get('KOBOLDCPP_QUALITY', 'base')  # fallback chain
```

#### Other Principles

- **One command, one package** - No cross-package imports (except `core`)
- **Explicit over implicit** - Use shell chaining, not compound commands
- **Fail loudly** - Raise errors with helpful messages, don't silently continue
- **Absolute imports** - Always `from src.core.core import ...`

---

### Adding a New Command

1. Create package: `src/newcommand/`
2. Add `__init__.py`
3. Create `command.py` with `cmd_newcommand(args)` function
4. Import in `src/__main__.py`
5. Add to argparse and dispatch dict

**Template:**

```python
# src/newcommand/command.py
"""
Newcommand - Brief description
"""

import logging
from src.core.core import get_project_root
from src.perf.performance import timed_command


@timed_command
def cmd_newcommand(args):
    """Command implementation"""
    project_root = get_project_root()
    
    # Your code here
    
    print("[OK] Command complete")
```

### Import Rules

**Always use absolute imports:**

```python
# ✅ CORRECT
from src.core.core import get_project_root
from src.perf.performance import timed_command

# ❌ WRONG
from core.core import get_project_root
from perf.performance import timed_command
```

### Path Handling

**Always use `get_project_root()`:**

```python
from src.core.core import get_project_root

project_root = get_project_root()
resources = project_root / "resources"
build = project_root / "build"
```

### Logging

```python
import logging

logging.info("Informational message")
logging.warning("Warning message")
logging.error("Error message")
logging.debug("Debug message (only with -vv)")
```

**Verbosity levels:**
- `tias command` - Warnings only
- `tias -v command` - Info + warnings
- `tias -vv command` - Debug + info + warnings

---

## Testing

### All tests:
```bash
pytest
pytest -v
```

### Specific module:
```bash
pytest tests/core/
pytest tests/inject/
```

### Specific file:
```bash
pytest tests/core/test_core.py
pytest tests/core/test_date_utils.py
pytest tests/inject/test_launch_windows.py
```

### With coverage:
```bash
pytest --cov=src
pytest --cov=src --cov-report=html
```

---

## Architecture

### Package Philosophy

Each command package is **independent**:
- One command = one package
- No cross-package imports (except `core`)
- Self-contained functionality

### Core Package

`src/core/` provides shared utilities:
- `core.py` - Logging, environment, paths
- `date_utils.py` - Date parsing
- Performance tracking

### Performance Tracking

All commands decorated with `@timed_command` are automatically tracked:

```python
from src.perf.performance import timed_command

@timed_command
def cmd_mycommand(args):
    # Execution time logged to logs/performance.log
    pass
```

View stats: `tias perf`

### Date Format Support

Use `parse_flexible_date()` for flexible date parsing:

```python
from src.core.date_utils import parse_flexible_date

game_date, normalized = parse_flexible_date(args.date)
# Supports: YYYY-M-D, YYYY-MM-DD, DD/MM/YYYY
```

### Database Schema

**Templates DB:** `build/game_templates.db`
- `space_bodies` - Planets, moons, asteroids
- `hab_sites` - Habitation sites
- `mining_profiles` - Resource profiles
- `traits` - Character traits

**Savegame DB:** `build/savegame_YYYY_M_D.db`
- `campaign` - Campaign metadata
- `gamestates` - Full game state (JSON blobs)

---

## Configuration

### Environment Variables (.env)

```bash
# KoboldCpp
KOBOLDCPP_DIR=/path/to/koboldcpp
KOBOLDCPP_MODEL_BASE=/path/to/model.gguf
KOBOLDCPP_PORT=5001
KOBOLDCPP_GPU_BACKEND=vulkan
KOBOLDCPP_GPU_LAYERS=35

# Terra Invicta
GAME_INSTALL_DIR=/path/to/Terra Invicta
GAME_SAVES_DIR=/path/to/saves

# System
LOG_LEVEL=INFO
```

### Quality Tiers

| Tier | Model | Size | Use Case |
|------|-------|------|----------|
| base | mistral-7b-q4 | ~4GB | Fast iteration |
| max | mistral-7b-q6 | ~6GB | Better quality |
| nuclear | qwen2.5-14b-q4 | ~8GB | High quality |
| ridiculous | qwen2.5-32b-q4 | ~18GB | Production |
| ludicrous | qwen2.5-72b-q2 | ~40GB | Maximum quality |

---

## Troubleshooting

### Import Errors

```bash
# Reinstall in editable mode
pip uninstall tias
pip install -e .
```

### Path Issues

```python
# Always use get_project_root()
from src.core.core import get_project_root
project_root = get_project_root()
```

### Command Not Found

```bash
# Ensure Scripts directory is in PATH (Windows)
echo $env:PATH

# Or use full path
C:\Users\YourName\AppData\Local\Python\pythoncore-3.14-64\Scripts\tias.exe
```

### Module Not Found

Check `__init__.py` exists in all package directories:

```bash
find src -type d -exec ls {}/__init__.py \; 2>/dev/null
```

---

## Contributing

1. Create feature branch
2. Add tests for new functionality
3. Update this guide if adding commands
4. Ensure all tests pass: `pytest tests/`
5. Submit PR

---

## Performance Targets

| Command | Target | Description |
|---------|--------|-------------|
| build | <1.0s | Template + DB creation |
| parse | <0.5s | Savegame decompression |
| inject | <0.02s | Context generation |
| validate | <0.5s | Path checking |

View actual performance: `tias perf`

---

## Resources

- **Logs:** `logs/terractl.log`
- **Performance:** `logs/performance.log`
- **Context:** `generated/mistral_context.txt`
- **Docs:** `docs/`
- **Tests:** `tests/`

---

## License

[Your License Here]

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [repo-url]/issues
- Documentation: `docs/`
