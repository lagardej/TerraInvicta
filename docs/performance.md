# Performance Guide

## Performance Targets

| Command | Target | Typical | Threshold | Description |
|---------|--------|---------|-----------|-------------|
| clean | <0.1s | ~0.05s | 0.1s | Directory removal |
| build | <1.0s | ~0.8s | 1.0s | Template + DB creation |
| parse | <0.5s | ~0.3s | 0.5s | Savegame decompression + SQL |
| inject | <0.02s | ~0.01s | 0.02s | Context generation |
| validate | <0.5s | ~0.2s | 0.5s | Path checking |
| install | N/A | ~5s | N/A | Interactive user input |
| run | N/A | N/A | N/A | External process (KoboldCpp) |

**Performance tracking:** All commands decorated with `@timed_command` automatically log execution time.

## Monitoring Performance

### View Statistics

```bash
# Display performance report
tias perf
```

**Output includes:**
- Command execution count
- Min/Avg/Max times
- P95 percentile (95th percentile)
- Failure count
- Threshold violations (marked with !)

**Example output:**
```
Command Performance:
Command      Count    Min        Avg        Max        P95        Failures
----------------------------------------------------------------------------
 build       12       0.752      0.823      0.941      0.920      0
 parse       45       0.287      0.314      0.425      0.389      0
!inject      52       0.009      0.025      0.063      0.045      1
 validate    8        0.178      0.213      0.267      0.254      0
```

### Performance Log

Location: `logs/performance.log`

**Format:** CSV (timestamp, command, elapsed, status)
```csv
2026-02-17T10:23:45.123456,build,0.823,SUCCESS
2026-02-17T10:24:12.456789,parse,0.314,SUCCESS
2026-02-17T10:24:13.789012,inject,0.012,SUCCESS
```

**Analyze manually:**
```bash
# View recent performance
tail -20 logs/performance.log

# Count executions per command
cut -d',' -f2 logs/performance.log | sort | uniq -c

# Average time for build command
grep "build" logs/performance.log | cut -d',' -f3 | awk '{sum+=$1; n++} END {print sum/n}'
```

## Performance Optimization

### Build Command

**Bottlenecks:**
- JSON parsing (52 templates)
- SQLite insertions
- Localization merging

**Optimizations:**
- Batch SQL inserts
- Single transaction per table
- Skip malformed templates (7/58 invalid in game files)

**If slow (>1.5s):**
```bash
# Check disk I/O
# Use SSD for build/ directory

# Check template count
ls build/templates/*.json | wc -l
# Should be ~52

# Rebuild with timing
tias -vv clean && tias -vv build
```

### Parse Command

**Bottlenecks:**
- Gzip decompression
- JSON parsing (13MB uncompressed)
- SQLite insertion

**Optimizations:**
- Stream decompression (don't load entire file)
- Single transaction for all inserts
- Minimal SQL schema

**If slow (>1.0s):**
```bash
# Check savegame size
ls -lh "$GAME_SAVES_DIR"/*.gz
# Typical: 2-3MB compressed

# Check extraction
gunzip -c savegame.gz | wc -l
# Should complete quickly
```

### Inject Command

**Bottlenecks:**
- SQLite queries
- Launch window calculations
- File I/O

**Optimizations:**
- Pre-calculated synodic periods
- Efficient date arithmetic
- Buffered file writing

**If slow (>0.1s):**
```bash
# Check database size
ls -lh build/game_templates.db
# Should be ~5MB

# Check query performance
sqlite3 build/game_templates.db "EXPLAIN QUERY PLAN SELECT * FROM hab_sites"
```

## System Performance

### Hardware Recommendations

**Minimum:**
- CPU: 4 cores @ 3.0GHz
- RAM: 16GB
- Storage: HDD (acceptable)
- GPU: Integrated (KoboldCpp only, not TIAS)

**Recommended:**
- CPU: 8+ cores @ 3.5GHz
- RAM: 32GB
- Storage: NVMe SSD
- GPU: Dedicated GPU for KoboldCpp

### OS-Specific Notes

**Linux (Recommended):**
- Native performance
- Better Vulkan support
- Lower overhead
- 10-20% faster than WSL

**Windows:**
- Native Windows performance is good
- Avoid WSL for TIAS (Python overhead)
- Use PowerShell or CMD

**WSL:**
- Works but adds ~10-15% overhead
- File I/O through translation layer
- Not recommended for production

## LLM Response Time

**Not measured by TIAS** (external process), but expected:

| Quality Tier | Model | Tokens/sec | 250 token response |
|--------------|-------|------------|-------------------|
| base | Mistral 7B Q4 | 80-120 | 2-3s |
| max | Mistral 7B Q6 | 70-100 | 2.5-3.5s |
| nuclear | Qwen 14B Q4 | 50-80 | 3-5s |
| ridiculous | Qwen 32B Q4 | 30-50 | 5-8s |
| ludicrous | Qwen 72B Q2 | 15-30 | 8-16s |

**Factors affecting LLM speed:**
- GPU VRAM (more = faster)
- GPU layers offloaded (more = faster)
- Context size (larger = slower)
- Quantization level (lower bits = faster)

## Optimization Tips

### General

1. **Use SSD** for `build/` directory
2. **Clean regularly** to avoid stale data
3. **Validate config** after changes
4. **Monitor logs** for warnings

### Build Pipeline

```bash
# Fast rebuild (parallel safe)
tias clean && tias build

# Full rebuild with validation
tias clean && tias build && tias validate

# Check performance after
tias perf
```

### Parse Pipeline

```bash
# Quick parse + inject
tias parse --date 2027-7-14 && tias inject --date 2027-7-14

# Skip parse if savegame unchanged
tias inject --date 2027-7-14
```

### Batch Operations

Process multiple dates efficiently:

```bash
# Bash
for date in 2027-7-14 2027-8-1 2027-9-15; do
  tias parse --date $date && tias inject --date $date
done

# PowerShell
$dates = @('2027-7-14', '2027-8-1', '2027-9-15')
foreach ($date in $dates) {
  tias parse --date $date
  if ($?) { tias inject --date $date }
}
```

## Troubleshooting Performance Issues

### Slow Build Command

**Symptoms:** Build takes >2s

**Diagnosis:**
```bash
# Check game installation
tias validate

# Check disk I/O
# Windows: Performance Monitor
# Linux: iostat -x 1

# Rebuild with verbose logging
tias -vv clean && tias -vv build
```

**Solutions:**
- Move project to SSD
- Check antivirus exclusions
- Reduce logging level in .env

### Slow Parse Command

**Symptoms:** Parse takes >1s

**Diagnosis:**
```bash
# Check savegame size
ls -lh "$GAME_SAVES_DIR"/*.gz

# Test decompression
time gunzip -c savegame.gz > /dev/null
```

**Solutions:**
- Verify SSD for game saves
- Check disk space
- Rebuild database: `tias clean && tias build`

### Memory Usage

**Typical memory usage:**
- clean: <50MB
- build: 100-200MB (JSON parsing)
- parse: 200-300MB (decompression)
- inject: <100MB
- validate: <50MB

**If memory issues:**
```bash
# Check Python memory
# Linux: ps aux | grep python
# Windows: Task Manager

# Check for memory leaks
pip install memory_profiler
python -m memory_profiler bin/tias.py build
```

## Performance Regression Testing

### Baseline Performance

Establish baseline after optimization:

```bash
# Record baseline
tias clean && tias build && tias perf > baseline.txt

# After changes, compare
tias clean && tias build && tias perf > current.txt
diff baseline.txt current.txt
```

### Automated Testing

```bash
# Run full pipeline with timing
time (tias clean && tias build && tias parse --date 2027-7-14 && tias inject --date 2027-7-14)

# Expected total: <3s for full pipeline
```

## Future Optimizations

Potential improvements:
- [ ] Parallel template processing
- [ ] Database connection pooling
- [ ] Incremental builds (only changed files)
- [ ] Memory-mapped file I/O
- [ ] Cached launch window calculations
- [ ] Binary format for intermediate data

## Performance FAQ

**Q: Why is build slower on first run?**
A: OS file caching. Subsequent runs are faster due to cached reads.

**Q: Should I clean before every build?**
A: Only if templates are corrupted or game updated. Otherwise unnecessary.

**Q: Does -v/-vv slow down commands?**
A: Yes, slightly (~5-10%). Avoid for production/benchmarking.

**Q: Can I run commands in parallel?**
A: Yes, but avoid parallel writes to same database. Parse different dates in parallel is safe.

**Q: What's the slowest operation?**
A: Parse command (decompresses 13MB JSON). Still well under 0.5s target.

---

For complete command reference, see [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)
