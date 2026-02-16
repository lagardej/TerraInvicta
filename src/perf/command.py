"""
Perf command - Display performance statistics
"""

from collections import defaultdict

from src.core.core import get_project_root


def cmd_perf(args):
    """Display performance statistics"""
    print("Terra Invicta Advisory System - Performance Report")
    print("=" * 60)

    project_root = get_project_root()
    perf_log = project_root / "logs" / "performance.log"

    if not perf_log.exists():
        print("\nNo performance data available.")
        print("Performance tracking started automatically with this version.")
        return

    # Parse performance log
    stats = defaultdict(list)
    failures = defaultdict(int)

    with open(perf_log) as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 4:
                continue

            timestamp, command, elapsed, status = parts[:4]
            elapsed = float(elapsed)

            stats[command].append(elapsed)
            if status == "FAILED":
                failures[command] += 1

    if not stats:
        print("\nNo performance data available.")
        return

    # Display statistics
    print("\nCommand Performance:")
    print(f"{'Command':<12} {'Count':<8} {'Min':<10} {'Avg':<10} {'Max':<10} {'P95':<10} {'Failures'}")
    print("-" * 75)

    for command in sorted(stats.keys()):
        times = sorted(stats[command])
        count = len(times)
        min_time = min(times)
        avg_time = sum(times) / count
        max_time = max(times)
        p95_idx = int(count * 0.95)
        p95_time = times[p95_idx] if p95_idx < count else max_time
        fails = failures.get(command, 0)

        # Highlight slow commands
        warning = "!" if avg_time > 1.0 else " "

        print(
            f"{warning}{command:<11} {count:<8} {min_time:<10.3f} {avg_time:<10.3f} {max_time:<10.3f} {p95_time:<10.3f} {fails}")

    # Performance targets
    print("\n" + "=" * 60)
    print("Performance Targets:")
    print("  build:    <1.0s   (template + DB creation)")
    print("  parse:    <0.5s   (savegame decompression + DB insert)")
    print("  inject:   <0.02s  (context generation)")
    print("  validate: <0.5s   (path checking)")
    print("\nThreshold violations marked with !")
