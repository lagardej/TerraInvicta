# Tier System Design Note
# Status: DESIGN — not yet implemented
# Last updated: 2026-02-19

## Overview

5-tier progression replacing the original 3-tier system.
Original problem: 3 tiers mapped 10%/10%/80% of gameplay — actors had nothing useful to say for most of the campaign.
5-tier system maps to DEFCON levels for emotional resonance.

Tier gate: 4/5 conditions met (consistent across all tiers).

---

## Tier Names (T1-T2 locked, T3-T5 working drafts)

| Tier | DEFCON | Name | Status |
|---|---|---|---|
| 1 | 5 | The Terrestrial Foundation | LOCKED |
| 2 | 4 | The Inner System Industrialist | LOCKED |
| 3 | 3 | The Interplanetary Contender | WORKING DRAFT |
| 4 | 2 | Total War Footing | WORKING DRAFT |
| 5 | 1 | The Terminal Offensive | WORKING DRAFT |

---

## Conditions

### Tier 1 — The Terrestrial Foundation
*Transitioning from secret society to global shadow government.*

| # | Condition | Detectable? |
|---|---|---|
| 1 | Recruit 5 Agents (Clandestine Cells unlocked) | ✓ |
| 2 | Control 1 Major Nuclear Power (USA, China, or EU) | ✓ |
| 3 | Reach 0.5 Boost/day | ✓ |
| 4 | Reach 1.5k Research/month | ✓ |
| 5 | Fill 15–25 Mission Control | ✓ |

Required research: Arrival Economics, Advanced Chemical Rocketry, Space Mining and Refining
Key projects: Clandestine Cells, Arrival Markets, Outpost Mining Complex

---

### Tier 2 — The Inner System Industrialist
*Moving production from Earth's gravity well into the Inner Planets.*

| # | Condition | Detectable? |
|---|---|---|
| 1 | 4+ Mars Mines (positive Water/Volatiles/Metals income) | ✓ |
| 2 | 1 Shipyard + 1 Spacedock in Earth or Mars orbit | ⚠ module name unconfirmed |
| 3 | Reach 4k Research/month | ✓ |
| 4 | Launch first contact fleet (4+ Missile Escorts or Monitors) | ✓ |
| 5 | Reach 40–60 Mission Control | ✓ |

Required research: Solid Core Fission Systems, High Energy Electrostatics, Mission to Mars
Key projects: Grid Drive, Layered Defense Array, Nuclear Fission Pile

---

### Tier 3 — The Interplanetary Contender (WORKING DRAFT)
*The Jupiter Rush and transition to full 6-person Council.*

| # | Condition | Detectable? |
|---|---|---|
| 1 | 6th Agent unlocked (Covert Operations researched) | ✓ |
| 2 | Base in Outer Planets (Jupiter or Saturn moons) | ✓ |
| 3 | Fleet reaches 20–40 kps | ⚠ calculable, needs verification |
| 4 | Space-based economy active (Nanofactories/Tourism) | ⚠ needs definition |
| 5 | Reach 10k Research/month | ✓ |

Required research: Industrialization of Space, Mission to Jupiter, Visible Light/Green Lasers
Key projects: Covert Operations, Construction Module, Fission/Fusion Platform

---

### Tier 4 — Total War Footing (WORKING DRAFT)
*Managing total war and consolidating Earth into Superstates.*

| # | Condition | Detectable? |
|---|---|---|
| 1 | 1+ Mega-Nation formed (e.g. United North America) | ⚠ federation size check |
| 2 | All major mining hubs protected by 4+ Layered Defense Arrays | ⚠ needs definition |
| 3 | Fleet reaches 80–150 kps | ⚠ needs verification |
| 4 | Total War triggered (Alien Hate at max) | ✗ state unknown |
| 5 | Reach 25k Research/month | ✓ |

Required research: High Temperature Superconductors, Fusion Power, Great Nations
Key projects: Inertial Confinement Fusion, Plasma Weapons T1, Ring Core

---

### Tier 5 — The Terminal Offensive (WORKING DRAFT)
*Closing the Gate and dismantling the alien presence.*

| # | Condition | Detectable? |
|---|---|---|
| 1 | Kill an Alien Mothership or Assault Carrier | ✗ kill events not in savegame |
| 2 | Reach the Outer Heliopause (Kuiper Belt/Wormhole) | ✗ location state unknown |
| 3 | Torch drive unlocked (Protium Torch or Neutron Flux Torch) | ⚠ research state |
| 4 | 6 Counselors with 25 in primary stats and 100% Loyalty | ✓ |
| 5 | Final Faction Research Goal active/completed | ✗ faction goal state unknown |

Required research: Antimatter/Exotic Matter, Heavy Fusion, Quantum Encryption
Key projects: The Gate (faction specific), UV Phasers or T3 Coilguns, Titan/Dreadnought Hulls

---

## Implementation Notes

- Current code uses 3-tier system (stage/command.py) — not replaced until T1-T5 conditions verified
- T3-T5 conditions need late-game save verification before committing
- Undetectable conditions (✗) need alternative proxy metrics or removal
- Jun-ho uses required/recommended research lists to flag lagging tech
- "Space-based economy" (T3 C4) needs concrete savegame field before implementation
