# Session: Web Interface Feasibility — Council Chat + Reporting
**Date:** 2026-02-26
**Status:** Complete (feasibility only, no implementation)

## Scope
Feasibility assessment for a v3 web interface: browser-based council chat with AI agents,
and reporting/dashboard pages for timeline metrics (countries controlled, MC, habs, tier progression).

## Conclusion
Feasible. Deferred to v3. V2 agentic transform is current priority.

## Design Notes (for v3 reference)

### Reporting
- Campaign-level DB (`campaign.db`) accumulates metrics across savegame snapshots
- Schema: `timeline` table — date, faction, countries_controlled, mc_total, habs_controlled, space_stations, tier
- Extraction slot: inside `tias stage`, after parse, before context assembly — writes one row per run
- Frontend: Chart.js or Plotly via CDN, no build step

### Web App
- Stack: FastAPI + uvicorn, plain JS frontend (no npm/build pipeline)
- Entry: `tias serve --date DATE`
- Routes: `/chat` (council), `/reports` (dashboards), `/state` (tier/advisor status)
- Chat endpoint: thin proxy to existing OpenAI-compatible LLM backend (no LLM changes)
- CODEX: persistent sidebar, not in conversation thread
- Tier indicator: visual badge at T1/T2/T3 thresholds
- Advisor addressing: click portrait replaces `@wale` syntax
- Spectator injection: Wale's `spectator_probability: 0.5` surfaced visually

### Effort (when v3 starts)
- Campaign DB + extraction: 1-2 days
- FastAPI server skeleton: 1 day
- Chat endpoint: 1 day
- Reports page: 1-2 days
- Council chat UI (functional): 2-3 days
- MVP total: ~1 week

### Constraints unchanged
- <5s response time — UI layer only, LLM backend untouched
- Streaming responses to browser better for perceived latency than KoboldCpp UI

## Decisions
- No implementation this session
- Add to FEATURES.md v3 section (not done — user declined changes)
- Revisit after v2 agentic transform is complete
