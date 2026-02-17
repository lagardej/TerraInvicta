"""
Stage command - Assemble actor context files from resources

Reads actor specs, personality files, tier from tier_state.json,
and assembles per-actor context files ready for inject.

This is the core domain logic command:
  resources/ (actors, prompts) + tier_state.json → generated/context_*.txt
"""

import json
import logging
import tomllib
from pathlib import Path

from src.core.core import get_project_root
from src.perf.performance import timed_command


# Fallback tier if tier_state.json not found
DEFAULT_TIER = 1


def load_tier(generated_dir: Path) -> int:
    """Load current tier from tier_state.json, fallback to DEFAULT_TIER"""
    tier_file = generated_dir / "tier_state.json"

    if not tier_file.exists():
        logging.warning(
            f"tier_state.json not found, using Tier {DEFAULT_TIER}. "
            f"Run: tias evaluate (not yet implemented)"
        )
        return DEFAULT_TIER

    with open(tier_file, encoding='utf-8') as f:
        state = json.load(f)

    tier = state.get('current_tier', DEFAULT_TIER)
    logging.info(f"Current tier: {tier} (from tier_state.json)")
    return tier


def load_actor(actor_dir: Path) -> dict:
    """Load all files for one actor into a dict"""
    spec_file = actor_dir / "spec.toml"
    if not spec_file.exists():
        return {}

    with open(spec_file, 'rb') as f:
        actor = tomllib.load(f)

    # Load optional text files - empty string if missing
    for filename, key in [
        ('background.txt',  'background'),
        ('personality.txt', 'personality'),
        ('stage.txt',       'stage_directions'),
    ]:
        filepath = actor_dir / filename
        actor[key] = filepath.read_text(encoding='utf-8').strip() if filepath.exists() else ''

    # Load tier-specific examples
    for tier in (1, 2, 3):
        filepath = actor_dir / f"examples_tier{tier}.md"
        actor[f'examples_tier{tier}'] = filepath.read_text(encoding='utf-8').strip() if filepath.exists() else ''

    return actor


def assemble_actor_context(actor: dict, tier: int) -> str:
    """Assemble a single actor's context file for the given tier"""
    name = actor.get('display_name', actor.get('name', 'Unknown'))
    domain = actor.get('domain_primary', '')
    tier_scope = actor.get(f'tier_{tier}_scope', '')
    can_discuss = actor.get(f'tier_{tier}_can_discuss', '')
    cannot_discuss = actor.get(f'tier_{tier}_cannot_discuss', '')
    error_domain = actor.get('error_domain_mismatch', '')
    error_tier = actor.get(f'error_out_of_tier_{tier}', '')
    background = actor.get('background', '')
    personality = actor.get('personality', '')
    stage_directions = actor.get('stage_directions', '')
    examples = actor.get(f'examples_tier{tier}', '')

    lines = [f"## {name}"]

    if domain:
        lines += [f"Domain: {domain}", ""]

    if background:
        lines += ["### Background", background, ""]

    if personality:
        lines += ["### Personality", personality, ""]

    if tier_scope:
        lines += [f"### Tier {tier} Scope", tier_scope, ""]

    if can_discuss:
        lines += ["### Can Discuss", can_discuss, ""]

    if cannot_discuss:
        lines += ["### Cannot Discuss", cannot_discuss, ""]

    if error_tier:
        lines += ["### Out of Tier Response", error_tier, ""]

    if error_domain:
        lines += ["### Out of Domain Response", error_domain, ""]

    if stage_directions:
        lines += ["### Stage Directions", stage_directions, ""]

    if examples:
        lines += [f"### Example Exchanges (Tier {tier})", examples, ""]

    return "\n".join(lines)


def assemble_system_context(prompts_dir: Path, tier: int) -> str:
    """Assemble the global system prompt"""
    system_file = prompts_dir / "system.txt"
    if not system_file.exists():
        logging.warning("resources/prompts/system.txt not found - skipping system context")
        return ''

    content = system_file.read_text(encoding='utf-8').strip()
    return f"# SYSTEM\nTier: {tier}\n\n{content}"


def assemble_codex_context(prompts_dir: Path) -> str:
    """Assemble the CODEX evaluation template"""
    codex_file = prompts_dir / "codex_eval.txt"
    if not codex_file.exists():
        logging.warning("resources/prompts/codex_eval.txt not found - skipping CODEX context")
        return ''

    return codex_file.read_text(encoding='utf-8').strip()


@timed_command
def cmd_stage(args):
    """Assemble actor context files from resources at current tier"""
    project_root = get_project_root()
    resources_dir = project_root / "resources"
    generated_dir = project_root / "generated"
    generated_dir.mkdir(exist_ok=True)

    # Determine current tier
    tier = load_tier(generated_dir)

    # Load and assemble system context
    prompts_dir = resources_dir / "prompts"
    system_ctx = assemble_system_context(prompts_dir, tier)
    if system_ctx:
        out = generated_dir / "context_system.txt"
        out.write_text(system_ctx, encoding='utf-8')
        logging.info(f"  -> {out.name}")

    # Load and assemble CODEX context
    codex_ctx = assemble_codex_context(prompts_dir)
    if codex_ctx:
        out = generated_dir / "context_codex.txt"
        out.write_text(codex_ctx, encoding='utf-8')
        logging.info(f"  -> {out.name}")

    # Load and assemble each actor
    actors_dir = resources_dir / "actors"
    assembled = []
    skipped = []

    for actor_dir in sorted(actors_dir.iterdir()):
        if not actor_dir.is_dir() or actor_dir.name.startswith('_'):
            continue

        actor = load_actor(actor_dir)
        if not actor:
            skipped.append(actor_dir.name)
            continue

        context = assemble_actor_context(actor, tier)
        out = generated_dir / f"context_{actor_dir.name}.txt"
        out.write_text(context, encoding='utf-8')
        assembled.append(actor_dir.name)
        logging.info(f"  -> {out.name}")

    if skipped:
        logging.warning(f"Skipped actors (no spec.toml): {', '.join(skipped)}")

    print(f"\n[OK] Stage complete: Tier {tier}, {len(assembled)} actors")
    print(f"     {', '.join(assembled)}")
