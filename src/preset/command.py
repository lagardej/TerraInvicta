"""
Preset command - Combine actor contexts and game state into final LLM context
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from src.core.core import get_project_root
from src.core.date_utils import parse_flexible_date
from src.preset.launch_windows import calculate_launch_windows
from src.perf.performance import timed_command


def load_actor_specs(resources_dir: Path) -> dict:
    """Load actor specs from TOML"""
    import tomllib

    actors = {}
    actors_dir = resources_dir / "actors"

    for actor_dir in actors_dir.iterdir():
        if not actor_dir.is_dir() or actor_dir.name.startswith('_'):
            continue

        spec_file = actor_dir / "spec.toml"
        if not spec_file.exists():
            continue

        with open(spec_file, 'rb') as f:
            spec = tomllib.load(f)

        actors[spec['name']] = spec

    return actors


@timed_command
def cmd_preset(args):
    """Combine actor contexts and game state into final LLM context"""
    project_root = get_project_root()

    game_date, iso_date = parse_flexible_date(args.date)

    templates_db  = project_root / "build" / "game_templates.db"
    savegame_db   = project_root / "build" / f"savegame_{iso_date}.db"
    templates_file = project_root / "build" / "templates" / "TISpaceBodyTemplate.json"
    output_file   = project_root / "generated" / "mistral_context.txt"
    output_file.parent.mkdir(exist_ok=True)

    if not templates_db.exists():
        logging.error("Templates DB missing. Run: tias load")
        return 1

    if not savegame_db.exists():
        logging.error(f"Savegame DB missing. Run: tias parse --date {args.date}")
        return 1

    logging.info("Loading actor specs...")
    actors = load_actor_specs(project_root / "resources")

    logging.info("Calculating launch windows...")
    launch_windows = calculate_launch_windows(game_date, templates_file)

    logging.info("Generating context...")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# TERRA INVICTA - LLM CONTEXT\n")
        f.write(f"# Game Date: {game_date.strftime('%Y-%m-%d')}\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

        # Actors
        f.write("# ADVISORS\n")
        for name, spec in actors.items():
            display = spec.get('display_name', name)
            domain = spec.get('domain_primary', 'Unknown')
            f.write(f"{display} - {domain}\n")
        f.write("\n")

        # Hab sites
        conn = sqlite3.connect(templates_db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT h.body, h.displayName,
                   p.water_mean, p.water_width, p.water_min,
                   p.metals_mean, p.metals_width, p.metals_min
            FROM hab_sites h
            JOIN mining_profiles p ON h.miningProfile = p.dataName
            WHERE h.body IN ('Luna', 'Mars')
            ORDER BY h.body, h.displayName
        ''')

        f.write("# KEY HAB SITES\n")
        current_body = None
        for row in cursor.fetchall():
            body, name, wm, ww, wmin, mm, mw, mmin = row
            if body != current_body:
                f.write(f"\n## {body}\n")
                current_body = body
            f.write(f"{name}: W={wm:.0f} M={mm:.0f}\n")

        conn.close()

        # Launch windows
        if launch_windows:
            f.write("\n# LAUNCH WINDOWS\n")
            for target, data in launch_windows.items():
                f.write(f"{target}: Next window {data['next_window']} ")
                f.write(f"({data['days_away']} days, ~{data['days_away'] // 30} months)")
                if 'current_penalty' in data:
                    f.write(f", Current penalty: {data['current_penalty']}%")
                f.write("\n")

    size = output_file.stat().st_size / 1024
    logging.info("=" * 60)
    logging.info(f"[OK] Context preset: {output_file.name}")
    logging.info(f"  Size: {size:.1f}KB")
    logging.info(f"  Actors: {len(actors)}")
    print(f"\n[OK] Preset complete: {output_file} ({size:.1f}KB)")
