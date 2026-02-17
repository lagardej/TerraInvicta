# Terra Invicta Advisory System - Feature Roadmap

This file tracks design ideas and features to be implemented.

**Last Updated:** 2026-02-17

---

## Implementation Status

### ✅ Completed

**Unified Command System (tias)**
- Python package with editable install (`pip install -e .`)
- 9 commands: install, clean, load, validate, parse, stage, preset, play, perf
- Full pipeline: `tias load && tias parse && tias stage && tias preset && tias play`
- SQLite-based data pipeline (game_templates.db + savegame_*.db)
- Flexible date input (YYYY-M-D, YYYY-MM-DD, DD/MM/YYYY)
- Performance tracking with `@timed_command`

**Data Pipeline**
- Game templates → SQLite with localization merge
- Malformed template auto-recovery (_repair_json)
- Savegames → SQLite (dated snapshots)
- Context generation → generated/mistral_context.txt

**Stage Command**
- Per-actor context assembly at current tier
- Reads tier from generated/tier_state.json (fallback: Tier 1)
- Output: generated/context_*.txt (one per actor + system + codex)

---

## Tier-Specific Prompts

**Status:** In Progress
**Priority:** High (blocks tier system)
**Complexity:** Medium

**Current State:**
- Actor specs define tier 1/2/3 scope in TOML
- Stub content files created for all 7 actors (personality.txt, stage.txt, examples_tier*.md)
- `tias stage` assembles context files but content is TODO

**Goal:**
Fill personality.txt, stage.txt, and examples_tier*.md for all actors.

**What's needed per actor:**
- `personality.txt` - Voice, speech patterns, behavioral traits
- `stage.txt` - Actor-specific stage directions and spectator reactions
- `examples_tier1.md` - 3-5 example exchanges at Tier 1 + boundary enforcement
- `examples_tier2.md` - 3-5 example exchanges at Tier 2 + boundary enforcement
- `examples_tier3.md` - 3-5 example exchanges at Tier 3

**Also needed:**
- `resources/prompts/system.txt` - Global council rules and tone
- `resources/prompts/codex_eval.txt` - CODEX session-opening report template

---

## CODEX Script-Based Tier Evaluation

**Status:** Planned
**Priority:** High (blocks tier progression)
**Complexity:** Medium

**Goal:**
Implement `tias evaluate` - deterministic tier readiness calculation from savegame DB.

**Output:** `generated/tier_state.json` (consumed by `tias stage`)

**Tier Unlock Conditions:**

Tier 2 (60-70%): Meet 2 of 5 conditions
1. Operative on Luna or Mars mine
2. Operative on Earth shipyard
3. 10+ MC
4. Control 3+ space stations
5. Member of 3+ nation federation

Tier 3 (70%+): Meet 3 of 6 conditions
1. Control orbital ring or space elevator
2. Fleet in Jupiter system or beyond
3. 25+ MC
4. Control 10+ habs
5. Federation of 5+ major powers
6. Councilor-level mission success rate >80%

---

## Domain Routing Automation

**Status:** Planned
**Priority:** Medium
**Complexity:** Medium

**Goal:** Automatic advisor selection based on query content.

Phase 1: Keyword matching against `domain_keywords` in spec.toml
Phase 2: Embedding-based semantic similarity (future)

User override: `@chuck [question]` forces Chuck to respond.

---

## Context Extraction Extensions

**Status:** Planned
**Priority:** Medium
**Complexity:** Low-Medium

**Goal:** Extend `tias preset` with richer game state data.

**Additional data to extract from savegame_*.db:**
- Faction standings and control points
- Councilor roster with traits/stats/missions
- Space fleets with composition and location
- Nation control and federation membership
- Current research progress
- Resource stockpiles
- Active missions

Keep total context under 16K tokens.

---

## Auto-Correction of Malformed Game Templates

**Status:** Done (implemented in tias load)

Terra Invicta ships ~7 malformed JSON files. The load command now:
1. Tries `json.load()` first
2. Falls back to `_repair_json()` (strips `//` comments, trailing commas)
3. Truly unrecoverable files → single WARNING at end (not one error per file)

---

## Advanced Features (Lower Priority)

### Real-Time Savegame Monitoring
Watch saves directory, auto-parse on new .gz file. Complexity: Medium.

### Web Interface
Browser-based chat with advisors, visual context inspection. Complexity: High.

### Multi-Campaign Management
Track and switch between multiple campaigns. Complexity: Medium.

### Voice Integration
TTS/STT for immersive RP. Complexity: High.

### Validation & Quality Assurance
Meta-layer validating advisor responses for tier compliance, domain accuracy.
Recommendation: Start with prompt engineering (free), add rule-based checks if needed.

### Conversation Examples
Document example conversations per tier in `docs/examples/`. Complexity: Low.

---

## Notes

- Complexity estimates: Low (1-2 days), Medium (3-5 days), High (1-2 weeks)
- Tier system (content + evaluation) is critical path
- Context extraction can be incremental
- Quality assurance via prompting preferred over validation overhead
