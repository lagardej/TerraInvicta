# Terra Invicta Advisory System - Feature Roadmap

This file tracks design ideas and features to be implemented.

**Last Updated:** 2026-02-15

---

## Implementation Status

### ✅ Completed (Session 3)

**Unified Build System**
- Single `terractl.py` script (1060 lines, 7 commands)
- SQLite-based data pipeline (game_templates.db + savegame_*.db)
- <1s full pipeline (build + parse + inject)
- OS-specific configuration (.env.linux.dist, .env.win.dist)
- Interactive install with path auto-detection
- Safety checks (Python 3.11+, .gitignore protection, validate command)

**Data Pipeline**
- Game templates → SQLite (5MB, queryable)
- Savegames → SQLite (13MB, dated snapshots)
- Context generation → generated/mistral_context.txt (4KB, inspectable)
- File-based context for debuggability (rejected in-memory streaming)

---

## Tier-Specific Prompts

**Status:** Planned  
**Priority:** High (blocks tier system)  
**Complexity:** Medium

**Current State:**
- Actor specs define tier 1/2/3 scope in TOML
- No actual prompt files created yet
- Context generation is generic

**Goal:**
Create tier-aware prompt templates that enforce knowledge boundaries.

**Structure:**
```
src/prompts/
├── tier1.txt    # Basic operations template
├── tier2.txt    # Strategic operations template
├── tier3.txt    # Global operations template
└── actor_overlays/
    ├── chuck.txt
    ├── valentina.txt
    └── ... (7 files)
```

**Each prompt includes:**
- Tier-specific knowledge scope (what they CAN discuss)
- Tier restrictions (what they CANNOT discuss)
- Actor personality overlay (injected on top of tier template)
- Response style and tone
- Example queries and responses

**Implementation:**
1. Extract tier scopes from actor TOML specs
2. Create tier templates with variable knowledge boundaries
3. Build process validates prompts against actor specs
4. Runtime combines: tier template + actor overlay + game context
5. Update `cmd_inject()` to use tier-aware templates

**Rationale:**
- Separate tier knowledge from actor personality
- Reusable tier templates across all actors
- Actor overlays are small deltas on top of tier baseline
- Easier to maintain than 21 separate prompts (7 actors × 3 tiers)

---

## CODEX Script-Based Tier Evaluation

**Status:** Planned  
**Priority:** High (blocks tier progression)  
**Complexity:** Medium

**Current State:**
- CODEX role defined in actor specs
- Manual tier setting in .env (CURRENT_TIER=1)
- No automatic tier calculation

**Goal:**
Implement deterministic tier readiness calculation based on game state.

**Tier Unlock Conditions:**

**Tier 2 (60-70%):** Meet 2 of 5 conditions
1. Operative on Luna or Mars mine
2. Operative on Earth shipyard
3. 10+ MC
4. Control 3+ space stations
5. Member of 3+ nation federation

**Tier 3 (70%+):** Meet 3 of 6 conditions
1. Control orbital ring or space elevator
2. Fleet in Jupiter system or beyond
3. 25+ MC
4. Control 10+ habs
5. Federation of 5+ major powers
6. Councilor-level mission success rate >80%

**Implementation:**
```python
# New command: python terractl.py evaluate --date YYYY-M-D

def cmd_evaluate(args):
    """Evaluate tier readiness from savegame"""
    # Parse savegame DB
    # Calculate conditions met
    # Compute readiness percentage
    # Output: generated/tier_state.json
    # Update CURRENT_TIER in .env if threshold crossed
```

**Output Format:**
```json
{
  "date": "2027-7-14",
  "current_tier": 1,
  "readiness": 0.45,
  "tier2_conditions": {
    "luna_mars_mine": true,
    "earth_shipyard": false,
    "mc_10plus": true,
    "stations_3plus": false,
    "federation_3plus": false
  },
  "tier2_met": 2,
  "tier2_needed": 2,
  "tier2_unlocked": true,
  "recommendation": "Tier 2 available - strategic operations now accessible"
}
```

**Features:**
- Script-based calculation (~0.01s, not LLM)
- Deterministic (same savegame = same result)
- Structured output (no hallucination)
- Auto-updates .env CURRENT_TIER
- Shows progress toward next tier

---

## Domain Routing Automation

**Status:** Planned  
**Priority:** Medium  
**Complexity:** Medium

**Current State:**
- Actor specs define domain keywords in TOML
- No automatic routing implementation
- User manually selects advisor

**Goal:**
Implement automatic advisor selection based on query content.

**Approach:**

**Phase 1: Simple keyword matching**
```python
def route_query(query: str, actors: dict) -> list[str]:
    """Select 1-2 advisors based on query keywords"""
    scores = {}
    for name, spec in actors.items():
        domain = spec['domain_primary']
        keywords = spec.get('domain_keywords', [])
        score = sum(1 for kw in keywords if kw.lower() in query.lower())
        if score > 0:
            scores[name] = score
    
    # Return top 1-2 advisors
    sorted_advisors = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [name for name, _ in sorted_advisors[:2]]
```

**Phase 2: Embedding-based (future)**
- Use sentence embeddings for semantic similarity
- Match query against domain descriptions
- Better handling of synonyms and related concepts

**User Override:**
- `@chuck what's your take on this?` → Force Chuck response
- `@valentina @lin discuss this` → Multi-advisor conversation
- No @ prefix → Auto-route based on content

**Multi-Domain Handling:**
- Single domain detected → 1 advisor responds
- Multiple domains → 2 advisors respond (conversation format)
- No clear domain → CODEX responds (meta-level routing)

---

## Context Extraction Extensions

**Status:** Planned  
**Priority:** Medium  
**Complexity:** Low-Medium

**Current State:**
- Context includes: actors, Luna/Mars hab sites
- ~4KB total
- Many gamestate keys unused

**Goal:**
Extract comprehensive game state for advisor queries.

**Additional Data to Extract:**

**From game_templates.db:**
- All hab sites (not just Luna/Mars)
- Tech tree with prerequisites
- Councilor traits with effects
- Space bodies with orbital parameters
- Station/platform templates

**From savegame_*.db:**
- Faction standings and control points
- Councilor roster with traits/stats/missions
- Space fleets with composition and location
- Nation control and federation membership
- Current research progress
- Resource stockpiles
- Active missions

**Implementation:**
- Extend `cmd_inject()` with additional queries
- Organize by advisor domain (e.g., Chuck sees covert ops data)
- Keep total context under 16K tokens (current: 4KB ≈ 1K tokens)
- Allow 10-15KB for full extraction

**Selective Loading (future):**
- Only load data relevant to current query
- Cache full context, inject subset per query
- Reduces token usage for simple questions

---

## Performance Monitoring

**Status:** Planned  
**Priority:** Low  
**Complexity:** Low

**Goal:**
Track actual system performance vs design targets.

**Metrics to Track:**
- Build time (target: <1s)
- Parse time (target: <0.5s)
- Inject time (target: <0.02s)
- Full pipeline time (target: <2s)
- Context size (target: <16KB)
- Token generation rate (target: >30 tok/s)

**Implementation:**
```python
# Add to terractl.py

import time

def timed_command(func):
    """Decorator to time command execution"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logging.info(f"Command completed in {elapsed:.2f}s")
        return result
    return wrapper

@timed_command
def cmd_build(args):
    # existing implementation
    pass
```

**Logging:**
- Append timing data to logs/performance.log
- Track trends over time
- Alert if exceeding thresholds

---

## Conversation Examples

**Status:** Planned  
**Priority:** Low  
**Complexity:** Low

**Goal:**
Document example conversations showing system behavior.

**Location:** `docs/examples/`

**Files:**
```
docs/examples/
├── tier1_basic.md       # Tier 1 conversations
├── tier2_strategic.md   # Tier 2 conversations
├── tier3_global.md      # Tier 3 conversations
├── multi_advisor.md     # Multiple advisors discussing
├── spectator.md         # Spectator reactions
└── edge_cases.md        # Error handling, boundary cases
```

**Each example includes:**
- User query
- Selected advisor(s)
- Full response
- Notes on tier boundaries, personality, domain routing

**Purpose:**
- Development reference
- Prompt engineering validation
- User documentation
- Quality assurance baseline

---

## Validation & Quality Assurance

**Status:** Idea  
**Priority:** Low  
**Complexity:** High

**Concept:**
Meta-layer that validates advisor responses for quality.

**Validation Checks:**
- In-character consistency (personality matches actor spec)
- Tier boundary compliance (no knowledge leakage)
- Factual accuracy vs game data (numbers match templates/savegame)
- Domain appropriateness (advisor stayed in their domain)
- Response length (concise vs verbose per spec)

**Potential Implementation:**

**Option 1: Second LLM pass (expensive)**
- Generate response with primary LLM
- Validate with secondary LLM call
- Pro: Flexible, catches subtle issues
- Con: 2x latency, 2x cost

**Option 2: Rule-based validation (cheap)**
- Check response against hard rules
- Regex for forbidden terms (tier leakage)
- Fact-check numbers against DB
- Pro: Fast, deterministic
- Con: Limited, can't catch nuance

**Option 3: Prompt engineering (free)**
- Strengthen prompts to prevent issues
- Use examples and negative examples
- Iterate on prompts until quality is consistent
- Pro: No runtime cost
- Con: Takes more upfront work

**Recommendation:** Start with Option 3, add Option 2 if needed, avoid Option 1 unless critical.

---

## Auto-Correction of Malformed Game Templates

**Status:** Idea  
**Priority:** Low  
**Complexity:** Low

**Context:**  
Terra Invicta ships ~7 malformed JSON template files. They are currently skipped during `tias build` and excluded from `game_templates.db`. Since we have no control over the source files, correction must happen in-memory at build time.

**Goal:**  
Parse and recover malformed game templates automatically, without modifying source files.

**Known Issues in Terra Invicta JSON:**
- Trailing commas in arrays/objects
- C-style `//` comments
- Possibly unquoted keys

**Approach:**  
Use a lenient JSON parser as fallback when `json.load()` fails.

```python
# Option 1: jsonc-parser (handles comments + trailing commas)
pip install jsonc-parser

# Option 2: json5 (superset of JSON)
pip install json5

# Option 3: regex pre-processing (no dependency)
import re

def repair_json(text: str) -> str:
    # Remove // comments
    text = re.sub(r'//[^\n]*', '', text)
    # Remove trailing commas before ] or }
    text = re.sub(r',\s*([\]\}])', r'\1', text)
    return text
```

**Implementation in `build_templates()`:**
```python
try:
    template_data = json.load(f)
except json.JSONDecodeError:
    f.seek(0)
    template_data = json.loads(repair_json(f.read()))  # Fallback
```

**Notes:**
- Option 3 (regex) preferred - no new dependency
- Only triggered as fallback, no impact on valid files
- Should recover all 7 known malformed templates
- Adds recovered count to build summary output

---

## Advanced Features (Lower Priority)

### Real-Time Savegame Monitoring
- Watch saves directory for new .gz files
- Auto-parse and inject on change
- Notify when new context available
- Complexity: Medium, Priority: Low

### Web Interface
- Browser-based chat with advisors
- Visual context inspection
- Tier progression dashboard
- Complexity: High, Priority: Low

### Multi-Campaign Management
- Track multiple campaigns simultaneously
- Switch between campaigns easily
- Compare campaigns side-by-side
- Complexity: Medium, Priority: Low

### Voice Integration
- TTS for advisor responses (different voices per actor)
- STT for voice queries
- Immersive RP experience
- Complexity: High, Priority: Low

---

## Technical Debt & Refactoring

**None identified.** Current architecture is clean:
- Single 1060-line script (manageable)
- Clear separation of concerns (commands)
- Comprehensive safety checks
- Good documentation

**Future considerations:**
- If terractl.py exceeds 2000 lines, consider splitting
- If command count exceeds 10, create command modules
- Keep performance <1s for core pipeline

---

## Notes

- Features listed by implementation status, then priority
- Complexity estimates: Low (1-2 days), Medium (3-5 days), High (1-2 weeks)
- Tier system (prompts + evaluation) is critical path
- Context extraction can be incremental
- Quality assurance via prompting preferred over validation overhead
- New features discovered during development should be added here
