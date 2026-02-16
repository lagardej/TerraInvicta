# Terra Invicta Advisory System

## About This Project

This project is used as a **learning experience for AI-assisted development**.

The workflow is collaborative by design:
- **I take the decisions** - architecture, features, priorities, direction
- **Claude (Anthropic) suggests, corrects, codes, and documents** - implementation, refactoring, best practices

This means the codebase reflects real decisions made through conversation: some things were built wrong and fixed, some were over-engineered and simplified, some were discovered by doing. The git history and `.ai/` directory preserve that process.

If you're reading this as a fellow learner: the mistakes are intentional in the sense that they were real, and the corrections are where the learning happened.

---

LLM-powered advisory system for Terra Invicta campaign gameplay. Provides domain-specific guidance through 6 specialized councilor advisors plus CODEX state evaluator.

## Documentation

- **[Developer Guide](DEVELOPER_GUIDE.md)** - Complete reference for commands, workflows, and development
- **[Features](FEATURES.md)** - Feature list and roadmap
- **[Technical Details](docs/technical.md)** - Architecture and implementation
- **[Workflow Guide](docs/workflow.md)** - User workflows
- **[Performance](docs/performance.md)** - Performance targets and monitoring

## Overview

**Advisors (7 total):**
- **Chuck** - Covert/Asymmetric Operations
- **Valentina** - Intelligence & Counter-Intelligence  
- **Lin** - Earth/Political Strategy
- **Jun-Ho** - Industrial & Energy Systems
- **Jonny** - Orbital Operations & Space Execution
- **Katya** - Military Doctrine & Ground Warfare
- **CODEX** - Data archivist, emotionless state evaluator

**Tier System:**
- Tier 1 (0-60%): Basic operations, individual targets
- Tier 2 (60-70%): Strategic operations, faction-level
- Tier 3 (70%+): Global operations, civilization-scale

## Quick Start

### Prerequisites
- Python 3.11+
- Terra Invicta v1.0.29 (Steam/GOG)
- KoboldCpp + Mistral 7B Q4 model (local LLM)
- AMD GPU: ROCm drivers (Linux) or Vulkan support (Windows/Linux)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd TerraInvicta

# Install in editable mode
pip install -e .

# Verify installation
tias --help
```

### Initial Setup

```bash
# Interactive configuration wizard
tias install
```

This will:
- Auto-detect Terra Invicta installation
- Auto-detect savegame directory
- Configure KoboldCpp path
- Configure model path
- Set GPU backend (vulkan/clblast)
- Create `.env` file

### Build Game Templates

```bash
tias build
```

This extracts and indexes game data from Terra Invicta installation.

### Basic Usage

```bash
# Parse a savegame
tias parse --date 2027-7-14

# Generate LLM context
tias inject --date 2027-7-14

# Launch KoboldCpp with context
tias run --date 2027-7-14

# Or chain them together
tias parse --date 2027-7-14 && \
tias inject --date 2027-7-14 && \
tias run --date 2027-7-14
```

**Date formats supported:**
- `YYYY-M-D` (e.g., `2027-7-14`)
- `YYYY-MM-DD` (e.g., `2027-07-14`)
- `DD/MM/YYYY` (e.g., `14/07/2027`)

## Commands

| Command | Description |
|---------|-------------|
| `tias install` | Interactive setup wizard |
| `tias clean` | Remove build directory |
| `tias build` | Build game templates database |
| `tias validate` | Validate configuration |
| `tias parse --date DATE` | Parse savegame to database |
| `tias inject --date DATE` | Generate LLM context |
| `tias run --date DATE` | Launch KoboldCpp |
| `tias perf` | Show performance statistics |

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for complete command reference.

## Common Workflows

### Full Clean Build
```bash
tias clean && tias build
```

### Complete Pipeline
```bash
tias parse --date 2027-7-14 && \
tias inject --date 2027-7-14 && \
tias run --date 2027-7-14
```

### Quick Context Update
```bash
# Skip parse if savegame unchanged
tias inject --date 2027-7-14 && tias run --date 2027-7-14
```

### Different Quality Tiers
```bash
tias run --date 2027-7-14 --quality base      # Fast (Mistral 7B Q4)
tias run --date 2027-7-14 --quality nuclear   # Better (Qwen 14B Q4)
tias run --date 2027-7-14 --quality ludicrous # Best (Qwen 72B Q2)
```

## Development

### Project Structure

```
TerraInvicta/
├── src/                    # Source code (Python package)
│   ├── __main__.py        # Entry point (tias command)
│   ├── core/              # Core utilities
│   ├── build/             # Build command
│   ├── clean/             # Clean command
│   ├── parse/             # Parse command
│   ├── inject/            # Inject command
│   ├── run/               # Run command
│   ├── validate/          # Validate command
│   └── perf/              # Performance tracking
├── resources/             # Game data
│   ├── actors/           # AI advisor definitions
│   └── prompts/          # LLM prompts
├── tests/                # Test suite
├── docs/                 # Documentation
└── build/                # Build output (gitignored)
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/test_launch_windows.py

# Verbose output
pytest -v
```

### Adding New Advisors

1. Create directory: `resources/actors/newname/`
2. Add files:
   - `spec.toml` - Metadata
   - `background.txt` - Character background
   - `openers.csv` - Conversation openers
   - `reactions.csv` - Response patterns
3. Rebuild: `tias clean && tias build`

See `resources/actors/_template/` for structure.

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# KoboldCpp
KOBOLDCPP_DIR=/path/to/koboldcpp
KOBOLDCPP_MODEL_BASE=/path/to/mistral-7b-q4.gguf
KOBOLDCPP_PORT=5001
KOBOLDCPP_GPU_BACKEND=vulkan

# Terra Invicta
GAME_INSTALL_DIR=/path/to/Terra Invicta
GAME_SAVES_DIR=/path/to/saves

# System
LOG_LEVEL=INFO
```

### Quality Tiers

Configure in `.env`:

```bash
KOBOLDCPP_MODEL_BASE=/path/to/mistral-7b-q4.gguf
KOBOLDCPP_MODEL_MAX=/path/to/mistral-7b-q6.gguf
KOBOLDCPP_MODEL_NUCLEAR=/path/to/qwen2.5-14b-q4.gguf
KOBOLDCPP_MODEL_RIDICULOUS=/path/to/qwen2.5-32b-q4.gguf
KOBOLDCPP_MODEL_LUDICROUS=/path/to/qwen2.5-72b-q2.gguf
```

## Features

### Launch Window Calculations
- Mars transfer windows with accurate penalty calculations (<1% error)
- Near-Earth Asteroid (Sisyphus, Hephaistos) transfer windows
- Synodic period verification

### Performance Monitoring
- Automatic command timing
- Performance log: `logs/performance.log`
- View stats: `tias perf`

### Multi-Tier System
- Tier 1: Basic operational advice
- Tier 2: Strategic faction-level guidance  
- Tier 3: Civilization-scale recommendations

## Troubleshooting

### Import Errors
```bash
pip uninstall tias
pip install -e .
```

### Command Not Found
Ensure Python scripts directory is in PATH:
- Windows: `C:\Users\YourName\AppData\Local\Python\pythoncore-3.14-64\Scripts`
- Linux: `~/.local/bin`

### Performance Issues
Check logs: `logs/performance.log`

Run validation: `tias validate`

## Contributing

1. Create feature branch
2. Add tests for new functionality
3. Update documentation
4. Run tests: `pytest`
5. Submit PR

## License

[Your License Here]

## Support

- **Documentation:** [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **Issues:** GitHub Issues
- **Logs:** `logs/terractl.log`
