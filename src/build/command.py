"""
Build command - Create templates database from game files
"""

import csv
import json
import logging
import sqlite3
from pathlib import Path

from src.core.core import load_env, get_project_root
from src.perf.performance import timed_command


def parse_localization_file(loc_file: Path) -> dict:
    """Parse .en localization file"""
    localizations = {}

    with open(loc_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '=' not in line:
                continue

            key, value = line.split('=', 1)
            parts = key.split('.')

            if len(parts) < 3:
                continue

            field = parts[1]
            data_name = '.'.join(parts[2:])

            if data_name not in localizations:
                localizations[data_name] = {}

            localizations[data_name][field] = value

    return localizations


def merge_localization(data, localizations: dict):
    """Recursively merge localization"""
    if isinstance(data, dict):
        merged = {}
        for key, value in data.items():
            merged[key] = merge_localization(value, localizations)

        data_name = merged.get('dataName')
        if data_name and data_name in localizations:
            loc = localizations[data_name]
            if 'displayName' in loc:
                merged['displayName'] = loc['displayName']
            if 'description' in loc:
                merged['description'] = loc['description']

        return merged

    elif isinstance(data, list):
        return [merge_localization(item, localizations) for item in data]

    else:
        return data


def build_actors(resources_dir: Path, build_dir: Path) -> dict:
    """Build actor JSON files from TOML/CSV"""
    import tomllib

    actors_rsrc = resources_dir / "actors"
    actors_build = build_dir / "actors"
    actors_build.mkdir(exist_ok=True)

    built_files = {}

    for actor_dir in actors_rsrc.iterdir():
        if not actor_dir.is_dir() or actor_dir.name.startswith('_'):
            continue

        spec_file = actor_dir / "spec.toml"
        if not spec_file.exists():
            continue

        logging.info(f"Building {actor_dir.name}...")

        with open(spec_file, 'rb') as f:
            spec = tomllib.load(f)

        # Load background
        bg_file = actor_dir / "background.txt"
        if bg_file.exists():
            with open(bg_file, encoding='utf-8') as f:
                spec['background'] = f.read()

        # Load openers
        openers_file = actor_dir / "openers.csv"
        if openers_file.exists():
            with open(openers_file, encoding='utf-8') as f:
                spec['openers'] = list(csv.DictReader(f))
        else:
            spec['openers'] = []

        # Load reactions
        reactions_file = actor_dir / "reactions.csv"
        if reactions_file.exists():
            with open(reactions_file, encoding='utf-8') as f:
                spec['reactions'] = list(csv.DictReader(f))
        else:
            spec['reactions'] = []

        # Write JSON
        output_file = actors_build / f"{actor_dir.name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)

        built_files[actor_dir.name] = str(output_file)
        logging.info(f"  -> {output_file}")

    return built_files


def _repair_json(text: str) -> str:
    """Best-effort repair of malformed JSON (trailing commas, // comments)"""
    import re
    text = re.sub(r'//[^\n]*', '', text)           # Remove // comments
    text = re.sub(r',\s*([\]\}])', r'\1', text)   # Remove trailing commas
    return text


def build_templates(game_dir: Path, build_dir: Path) -> dict:
    """Build templates with localization"""
    templates_rsrc = game_dir / "TerraInvicta_Data/StreamingAssets/Templates"
    loc_dir = game_dir / "TerraInvicta_Data/StreamingAssets/Localization/en"
    templates_build = build_dir / "templates"
    templates_build.mkdir(exist_ok=True)

    built_files = {}
    skipped = []
    recovered = []

    for template_file in templates_rsrc.glob("*.json"):
        template_name = template_file.stem
        logging.debug(f"  -> {template_name}")

        try:
            with open(template_file, encoding='utf-8') as f:
                template_data = json.load(f)
        except json.JSONDecodeError:
            try:
                with open(template_file, encoding='utf-8') as f:
                    template_data = json.loads(_repair_json(f.read()))
                recovered.append(template_name)
            except (json.JSONDecodeError, Exception):
                skipped.append(template_name)
                continue

        # Load localization
        loc_file = loc_dir / f"{template_name}.en"
        localizations = {}
        if loc_file.exists():
            localizations = parse_localization_file(loc_file)

        # Merge
        merged_data = merge_localization(template_data, localizations)

        # Write
        output_file = templates_build / template_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

        built_files[template_name] = str(output_file)

    if recovered:
        logging.debug(f"Recovered {len(recovered)} malformed templates: {', '.join(recovered)}")
    if skipped:
        logging.warning(f"Skipped {len(skipped)} unrecoverable game templates: {', '.join(skipped)}")

    return built_files


def create_templates_db(build_dir: Path, templates_dir: Path):
    """Create SQLite DB from templates"""
    db_path = build_dir / "game_templates.db"

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tables
    cursor.execute('''CREATE TABLE space_bodies
                      (
                          dataName    TEXT PRIMARY KEY,
                          displayName TEXT,
                          objectType  TEXT,
                          parent      TEXT,
                          mass_kg     TEXT,
                          radius_km   REAL
                      )''')

    cursor.execute('''CREATE TABLE hab_sites
                      (
                          dataName      TEXT PRIMARY KEY,
                          displayName   TEXT,
                          body          TEXT,
                          miningProfile TEXT,
                          water         INT,
                          metals        INT,
                          nobles        INT,
                          fissiles      INT
                      )''')

    cursor.execute('''CREATE TABLE mining_profiles
                      (
                          dataName       TEXT PRIMARY KEY,
                          displayName    TEXT,
                          water_mean     REAL,
                          water_width    REAL,
                          water_min      REAL,
                          metals_mean    REAL,
                          metals_width   REAL,
                          metals_min     REAL,
                          nobles_mean    REAL,
                          nobles_width   REAL,
                          nobles_min     REAL,
                          fissiles_mean  REAL,
                          fissiles_width REAL,
                          fissiles_min   REAL
                      )''')

    cursor.execute('''CREATE TABLE traits
                      (
                          dataName    TEXT PRIMARY KEY,
                          displayName TEXT,
                          description TEXT
                      )''')

    # Load space bodies
    bodies_file = templates_dir / "TISpaceBodyTemplate.json"
    if bodies_file.exists():
        with open(bodies_file, encoding='utf-8') as f:
            bodies = json.load(f)
        for body in bodies:
            cursor.execute('''INSERT INTO space_bodies
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (body.get('dataName'),
                            body.get('displayName', body.get('friendlyName')),
                            body.get('objectType'),
                            body.get('barycenterName'),
                            str(body.get('mass_kg')) if body.get('mass_kg') else None,
                            body.get('equatorialRadius_km')))

    # Load mining profiles
    profiles_file = templates_dir / "TIMiningProfileTemplate.json"
    profiles_map = {}
    if profiles_file.exists():
        with open(profiles_file, encoding='utf-8') as f:
            profiles = json.load(f)
        for profile in profiles:
            cursor.execute('''INSERT INTO mining_profiles
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (profile.get('dataName'),
                            profile.get('displayName', profile.get('friendlyName', profile.get('dataName'))),
                            profile.get('water_mean', 0), profile.get('water_width', 0), profile.get('water_min', 0),
                            profile.get('metals_mean', 0), profile.get('metals_width', 0), profile.get('metals_min', 0),
                            profile.get('nobles_mean', 0), profile.get('nobles_width', 0), profile.get('nobles_min', 0),
                            profile.get('fissiles_mean', 0), profile.get('fissiles_width', 0),
                            profile.get('fissiles_min', 0)))
            profiles_map[profile.get('dataName')] = {
                'water': profile.get('water_mean', 0),
                'metals': profile.get('metals_mean', 0),
                'nobles': profile.get('nobles_mean', 0),
                'fissiles': profile.get('fissiles_mean', 0)
            }

    # Load hab sites
    sites_file = templates_dir / "TIHabSiteTemplate.json"
    if sites_file.exists():
        with open(sites_file, encoding='utf-8') as f:
            sites = json.load(f)
        for site in sites:
            profile_name = site.get('miningProfileName')
            resources = profiles_map.get(profile_name, {})
            cursor.execute('''INSERT INTO hab_sites
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (site.get('dataName'),
                            site.get('displayName', site.get('friendlyName', site.get('dataName'))),
                            site.get('parentBodyName'),
                            profile_name,
                            resources.get('water', 0),
                            resources.get('metals', 0),
                            resources.get('nobles', 0),
                            resources.get('fissiles', 0)))

    # Load traits
    traits_file = templates_dir / "TITraitTemplate.json"
    if traits_file.exists():
        with open(traits_file, encoding='utf-8') as f:
            traits = json.load(f)
        for trait in traits:
            cursor.execute('''INSERT INTO traits
                              VALUES (?, ?, ?)''',
                           (trait.get('dataName'),
                            trait.get('displayName', trait.get('friendlyName')),
                            trait.get('description', '')))

    conn.commit()
    conn.close()

    logging.info(f"OK Created game database: {db_path}")


@timed_command
def cmd_build(args):
    """Build game templates database"""
    env = load_env()

    project_root = get_project_root()
    resources_dir = project_root / "resources"
    build_dir = project_root / "build"
    game_dir = Path(env['GAME_INSTALL_DIR'])

    # Ensure build directory exists
    build_dir.mkdir(exist_ok=True)

    logging.info("Building actors...")
    actor_files = build_actors(resources_dir, build_dir)
    logging.info(f"Built {len(actor_files)} actors")

    logging.info("Building templates...")
    template_files = build_templates(game_dir, build_dir)
    logging.info(f"Built {len(template_files)} templates")

    logging.info("Creating database...")
    create_templates_db(build_dir, build_dir / "templates")

    logging.info("=" * 60)
    logging.info(f"[OK] Build complete: {len(actor_files) + len(template_files)} files")
    logging.info(f"  Actors: {len(actor_files)}")
    logging.info(f"  Templates: {len(template_files)}")
    logging.info(f"  Database: {build_dir / 'game_templates.db'}")
    print(f"\n[OK] Build complete: {len(actor_files) + len(template_files)} files")
