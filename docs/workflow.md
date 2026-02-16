# Workflow Guide

## Game Integration Flow

### Three-Phase Cycle

**1. PREPARATION PHASE** (Outside game)
   - Pause game at Assignment Phase
   - Sync game state: `tias parse --date YYYY-M-D`
   - Generate context: `tias inject --date YYYY-M-D`
   - Launch LLM: `tias run --date YYYY-M-D`
   - Consult advisors via KoboldCpp chat
   - Advisors analyze state, recommend strategy
   - User decides final strategy

**2. ASSIGNMENT PHASE** (In-game)
   - Assign councilor missions per advisor recommendations
   - Confirm assignments
   - Advance to Resolution Phase

**3. RESOLUTION PHASE** (In-game)
   - Missions execute automatically
   - No LLM interaction during resolution
   - Observe outcomes

**4. NEXT ASSIGNMENT PHASE**
   - Return to Preparation Phase
   - Re-sync game state (new savegame)
   - Repeat cycle

## Command Chaining

### Basic Pipeline

```bash
# Full pipeline (parse + inject + run)
tias parse --date 2027-7-14 && \
tias inject --date 2027-7-14 && \
tias run --date 2027-7-14
```

### Conditional Execution

```bash
# Only continue if previous command succeeds
tias clean && tias build && echo "Build successful"

# Run even if previous fails (PowerShell)
tias clean; tias build

# Stop on first error (Bash)
set -e
tias clean
tias build
tias parse --date 2027-7-14
```

### Common Chains

```bash
# Clean rebuild
tias clean && tias build

# Quick context update (skip parse)
tias inject --date 2027-7-14 && tias run --date 2027-7-14

# Validation + build
tias validate && tias build

# Full pipeline with quality tier
tias parse --date 2027-7-14 && \
tias inject --date 2027-7-14 && \
tias run --date 2027-7-14 --quality nuclear
```

## Data Sync Workflow

### Quick Sync (After Each Turn)

```bash
# 1. Save game with descriptive date
# Example: Resistsave00005_2027-8-14.gz

# 2. Parse + inject + run in one go
tias parse --date 2027-8-14 && \
tias inject --date 2027-8-14 && \
tias run --date 2027-8-14
```

### Full Rebuild (After Game Updates)

```bash
# Clean + rebuild + parse + inject
tias clean && \
tias build && \
tias parse --date YYYY-M-D && \
tias inject --date YYYY-M-D
```

## Typical Session

### Initial Setup (One Time)

```bash
# Install package
pip install -e .

# Interactive configuration
tias install

# Build game templates
tias build
```

### Per-Turn Workflow

```bash
# 1. Play game, reach Assignment Phase, save
# Filename: Resistsave00042_2028-3-7.gz

# 2. Full pipeline
tias parse --date 2028-3-7 && \
tias inject --date 2028-3-7 && \
tias run --date 2028-3-7

# 3. Chat with advisors in KoboldCpp
# Example prompts:
# - "Chuck, recommend covert ops priorities this turn"
# - "CODEX, evaluate our strategic position"
# - "Valentina, which faction is most vulnerable to infiltration?"

# 4. Execute strategy in-game

# 5. Advance to next turn, repeat
```

## Date Format Flexibility

All date-based commands support multiple formats:

```bash
# ISO format with/without leading zeros
tias parse --date 2027-7-14
tias parse --date 2027-07-14

# European format
tias parse --date 14/7/2027
tias parse --date 14/07/2027

# All equivalent
```

## Context Management

### Inspecting Context

```bash
# View generated context
cat generated/mistral_context.txt

# Count lines
wc -l generated/mistral_context.txt

# View first 20 lines
head -n 20 generated/mistral_context.txt
```

**What's included:**
- Advisor list with domains
- Key hab sites (Luna, Mars) with resource ranges
- Launch windows (Mars, NEAs)
- (Extensible: add factions, councilors, control points)

### Regenerating Context

```bash
# Quick regeneration (same savegame)
tias inject --date 2027-7-14

# After new savegame
tias parse --date 2027-7-15 && tias inject --date 2027-7-15
```

## Multiple Campaigns

### Managing Multiple Saves

```bash
# Campaign A (Resistance, 2027)
tias parse --date 2027-7-14 && tias inject --date 2027-7-14

# Campaign B (Academy, 2028)  
tias parse --date 2028-2-3 && tias inject --date 2028-2-3

# Databases persist:
# build/savegame_2027_7_14.db
# build/savegame_2028_2_3.db
```

### Switching Campaigns

Context file reflects last `inject` command:

```bash
# Switch to Campaign A
tias inject --date 2027-7-14 && tias run --date 2027-7-14

# Switch to Campaign B
tias inject --date 2028-2-3 && tias run --date 2028-2-3
```

## Quality Tier Selection

```bash
# Fast iteration (Mistral 7B Q4)
tias run --date 2027-7-14 --quality base

# Better quality (Qwen 14B Q4)
tias run --date 2027-7-14 --quality nuclear

# Maximum quality (Qwen 72B Q2)
tias run --date 2027-7-14 --quality ludicrous

# Use default from .env if omitted
tias run --date 2027-7-14
```

## Debugging Workflow

### Verbose Logging

```bash
# INFO level logging
tias -v parse --date 2027-7-14

# DEBUG level logging
tias -vv build
```

Logs: `logs/terractl.log` (append mode, persists across runs)

### Verify Pipeline

```bash
# 1. Check templates DB
ls -lh build/game_templates.db
# Should be ~5MB

# 2. Check savegame DB
ls -lh build/savegame_*.db
# Should be ~13MB per savegame

# 3. Check context file
wc -l generated/mistral_context.txt
# Should be 50-100 lines (expandable)

# 4. Validate configuration
tias validate

# 5. Check performance
tias perf
```

### Common Issues

**Missing savegame:**
```
FileNotFoundError: No savegame found matching *_YYYY-M-D.gz
```
Fix: Verify date format matches actual savegame filename

**Outdated context:**
Symptom: Advisors reference old game state
Fix: Re-run `inject` after parsing new savegame

**Import errors after update:**
```bash
pip uninstall tias
pip install -e .
```

## Performance Optimization

### Monitor Performance

```bash
# View performance stats
tias perf

# Performance log location
cat logs/performance.log
```

### Quick Operations

```bash
# Skip parse if savegame unchanged
tias inject --date 2027-7-14 && tias run --date 2027-7-14

# Clean + build in one chain
tias clean && tias build
```

## Scripting and Automation

### Bash Script Example

```bash
#!/bin/bash
# update-context.sh

DATE="$1"
if [ -z "$DATE" ]; then
    echo "Usage: $0 YYYY-M-D"
    exit 1
fi

echo "Updating context for $DATE..."
tias parse --date "$DATE" && \
tias inject --date "$DATE" && \
echo "Context ready! Launching KoboldCpp..." && \
tias run --date "$DATE"
```

### PowerShell Script Example

```powershell
# update-context.ps1
param($Date)

if (-not $Date) {
    Write-Error "Usage: .\update-context.ps1 YYYY-M-D"
    exit 1
}

Write-Host "Updating context for $Date..."
tias parse --date $Date
if ($LASTEXITCODE -eq 0) {
    tias inject --date $Date
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Context ready! Launching KoboldCpp..."
        tias run --date $Date
    }
}
```

## Advanced: Custom Context

To extend context with additional game data:

1. Edit `src/inject/command.py`
2. Add SQL queries to extract data from savegame DB
3. Append to context file
4. Rebuild: `pip install -e .`
5. Generate: `tias inject --date YYYY-M-D`

Example additions:
- Faction standings
- Councilor roster  
- Control point distribution
- Tech tree progress
- Resource stockpiles

See [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md) for implementation details.

## Best Practices

1. **Always chain commands** - Use `&&` to stop on errors
2. **Save frequently** - Create savegames at every Assignment Phase
3. **Consistent naming** - Use date format in savegame names
4. **Check logs** - Review `logs/terractl.log` after errors
5. **Monitor performance** - Run `tias perf` periodically
6. **Validate config** - Run `tias validate` after changes
7. **Clean builds** - Use `tias clean && tias build` after game updates

---

For complete command reference, see [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)
