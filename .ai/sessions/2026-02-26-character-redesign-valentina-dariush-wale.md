# Session: Character Redesign — Valentina, Dariush, Wale
**Date:** 2026-02-26
**Status:** Complete

## Scope
Design pass on three actors: Jun-ho → Dariush (full identity swap), Valentina (full redesign),
Wale (relationship section update). Structural decisions on actor directory naming and casting.

---

## Dariush Shirazi (dir: jun-ho)

**Change:** Full identity swap from North Korean to Iranian.

**Identity:**
- Name: Dariush Shirazi (Dariush = classical Persian/Darius; Shirazi = Shiraz origin, educated class)
- Nationality: Iran (defector)
- Age: 47-49 (unchanged)
- Profession: Engineer (game profession; was "Nuclear Physicist" in spec — corrected)
- Traits: Enemy of the State, Pacifist, Physicist, Project Manager, Academic, Family Ties (all retained)

**Background changes:**
- Was: DPRK reactor physicist, defected, family in North Korea, hope = Korean reunification
- Now: Principal architect of Iranian nuclear program, defected after moral collapse over weapons work,
  family still in Iran believing he's on a classified assignment, hope = regime change
- Core tension: pacifist who needs regime change, knows it likely requires violence, refuses to
  contribute, lives with the unresolved contradiction permanently
- Kim Jong-un joke beat dropped entirely — replacement TBD in future session

**New sections written:** Full `## Personality` and `## Stage` at Wale's depth level, including
voice (Persian tells, formal compression under pressure), humor, domain, relationships, limits,
spectator lines, and stage directions.

**Files modified:**
- `resources/actors/jun-ho/spec.toml`
- `resources/actors/jun-ho/persona.md`
- `resources/actors/jun-ho/strings.csv`
- `resources/actors/jun-ho/examples_tier1/2/3.md` (headers only)
- `.ai/foundation.json`

---

## Valentina Mendoza (dir: valentina)

**Change:** Full redesign. Journalist → Hacker. Identity rebuilt from the ground up.

**Identity:**
- Nickname added: "Unity" (reference: Manifesto for Unity + Matrix/Trinity parallel)
- Age: 27-29 → 22-24 (prodigy framing)
- Profession: Journalist → Hacker
- Traits: dropped Pariah, Cynic / kept Conspiracy Theorist, Suspicious, Awareness /
  added Wealthy, Idealist, Computer Scientist
- Domain: Intelligence & Counter-Intelligence (retained), Secondary: System Infiltration,
  Threat Detection, Information Warfare

**Background changes:**
- Was: Investigative journalist who uncovered Servants, career destroyed, vindicated in 2026
- Now: Prodigy hacker since age 12, self-taught, no institutional backing. Pseudonymous
  conspiracy blog (never attributed to real identity) was the outlet for findings she couldn't
  surface otherwise. Broke into systems, found Servants infiltration, posted it, was dismissed,
  was vindicated. Still anonymous outside the Resistance.
- The Resistance found her despite everything she does to stay invisible. She doesn't know how.
  She is still investigating this. It is load-bearing — do not resolve it.
- Wrote the Manifesto for Unity before being recruited — genuine idealism, not profile-building.
  Nemik parallel (Andor).
- Pre-Resistance: did contract work for Wale — entry points, surveillance mapping, social
  engineering, the information half of his operations.
- She recruited Wale into the Resistance. He knows this. The council does not.
- Wealthy from contract work. Does not perform it.
- Trinity archetype throughout.

**Wale/Valentina dynamic additions:**
- Pre-Resistance operational history established
- She handed him a safehouse when the Initiative was closing in
- Father-daughter subtext: 20-year age gap, neither acknowledges it, present in every exchange.
  The trolling = how he checks on her without checking on her.
  The investigating = how she stays close without staying close.
  This is not a dynamic either of them would survive having named.

**New sections written:** Full `## Personality` and `## Stage` from scratch, including voice
(Spanish tells, impatience without aggression, the silence tell), humor, domain, relationships,
limits, spectator lines, stage directions. strings.csv rebuilt — old entries were generic.

**Files modified:**
- `resources/actors/valentina/spec.toml`
- `resources/actors/valentina/persona.md`
- `resources/actors/valentina/strings.csv`
- `resources/actors/valentina/examples_tier1/2/3.md` (headers only)
- `.ai/foundation.json`

---

## Wale Oluwaseun (dir: wale)

**Change:** Valentina relationship section rewritten to reflect new shared history.
Everything else untouched.

**What changed in `[relationships] VALENTINA`:**
- She recruited him. He knows. The council doesn't.
- Pre-Resistance operational trust established (results-based, not ideological)
- Father-daughter subtext added (mirrored in Valentina's file)
- Trolling dynamic reframed as running on top of history, not instead of it

**Files modified:**
- `resources/actors/wale/persona.md`

---

## Structural Decisions (no files changed — pending pipeline session)

### Actor directory naming scheme
Agreed: `actors/<faction>/<profession>_<fullname_nickname>`
- Replaces directory-as-identity with explicit casting
- Directory becomes arbitrary human-chosen label
- Name/identity changes no longer require filesystem renames

### Casting section in stage.md
Added `## CASTING` to `resources/stage.md` with full cast for Resistance faction.
Pipeline reads this to determine actor loading — directory scan replaced by cast list.
`councilor_name` fields all empty TODO — fill when pregen councilors confirmed in live save.

### Actor taxonomy
Two kinds of advisors established:
- **Human-like**: matched to game councilor, personality-driven, savegame-gated availability
- **AI advisors**: `computer_advisor = true` in spec.toml, no personality, always available.
  CODEX = mandatory data archivist (one per faction). 0+ additional domain AI advisors possible.
  Token budget for AI advisors TBD — measure before setting limit.

### Faction directory
`actors/<faction>/` supports multi-campaign. All current actors are `resistance/`.
CODEX is faction-scoped (Resistance calls it CODEX; another faction would have a different name).

### Game professions confirmed (from TICouncilorTemplate)
Full list: Activist, Astronaut, Celebrity, Commando, Diplomat, Evangelist, Executive, Fixer,
Hacker, Investigator, Journalist, Judge, Officer, Politician, Professor, Scientist, Spy,
TechMogul, Tycoon, Operative (confirmed by user), Engineer (confirmed by user)

### Final directory mapping (pending rename session)
| Current dir | Future dir |
|---|---|
| wale | operative_wale_oluwaseun_ankledeep |
| valentina | hacker_valentina_mendoza_unity |
| jun-ho | engineer_dariush_shirazi |
| lin | diplomat_lin_mei-hua |
| jonny | astronaut_jonathan_pratt_jonny |
| katya | officer_katya_bondarenko |
| codex | codex |

---

## Open Items

- `councilor_name` fields in stage.md Casting: fill when pregen councilors confirmed in save
- Dariush: Kim Jong-un joke beat dropped — replacement council dynamic TBD
- Wale: voice section note on using "Unity" nickname — future pass
- Lin background: not yet written (referenced as TBD in multiple relationship sections)
- Jonny background: not yet written
- Katya background: not yet written
- Examples files (tier1/2/3): all still TODO stubs for all three characters
- Pipeline session: casting-driven loading, directory rename, `computer_advisor` flag handling,
  AI advisor token budget measurement
