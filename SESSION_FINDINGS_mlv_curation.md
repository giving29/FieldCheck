# Session Findings — MLV Curation Mechanism (2026-07-05)
_Banked. Site freeze: FCBase_THE_LOOP_LIVE · commit 79e5d8f · tag site-live-20260705-2239_
_Worker (lab) commit: 36e463b_

## WHAT SHIPPED (prod site)
- LOVB vs MLV case study now has REAL engine-graded MLV composites (from curated profiles),
  anchored to honest band 5.8–7.2 (Abercrombie 7.2 top, kissing LOVB floor Skinner 7.3).
- All "illustrative" language removed → reframed to "reads hardening as engine finalizes calibration."
- LOVB unchanged: 7.3–9.3 real curated composites.

## THE CURATION MECHANISM (how to grade any player fairly) — PROVEN
1. **PLAYER_PROFILES** (worker.js line 19460, ~164 WVB entries): curated profiles keyed by slug.
   Each has eval_grid_override (per-facet score+evidence), awards, pro_projection, subjective_tier.
2. **PLAYER_ALIASES** (worker.js line 26840): maps normalized name → slug.
   Format: 'morganhentz': 'morgan-hentz-grand-rapids-womens-volleyball', 'hentz': '...same...'
   Resolver normalizes query name (lowercase, no spaces/punct) and looks up here. WITHOUT alias, curated_lookup FAILS.
3. **STAGE-A2 evidence feed** (line ~3601): fires when curated_merge_applied===true; pushes eval_grid_override
   evidence strings + per-facet anchors to the scorer as trusted evidence.
4. To add a player: add BOTH a PLAYER_PROFILES entry AND PLAYER_ALIASES entries (full name + lastname).
5. Deploy: `wrangler deploy --env dev` (dev worker: fieldcheck-proxy-dev.sridhar-nallani.workers.dev).
   Grade: POST /verdict/player {name, sport, skipCache:true}. Check curated_lookup_succeeded + slug.

## THE 12 MLV PROFILES (on lab branch, commit 36e463b — NOT on prod worker)
Hentz, Nuneviller, Abercrombie, Hilley, Colyer, Valentin-Anderson, Grote, Tealer, Edmond, Tuaniga, Scott, Londot.
Evidence-grounded from real records. NO hardcoded composites (engine derives). Files in outputs:
mlv_profiles_ALL12.js, mlv_aliases.js, install-mlv-profiles-v2.sh, install-mlv-aliases.sh.

## KEY FINDING — LAB ENGINE IS HOT (the parked recalibration is now BLOCKING fair absolutes)
- Blind Hentz = 8.85; curated Hentz = 9.3 (tied with Larson — WRONG for a libero).
- Curated grades came back hot across the board: Nuneviller 9.4, Edmond 8.6, Colyer/Grote/Londot 8.4,
  Tuaniga 7.1, Tealer 5.3 (5 timed out: Hentz*, Hilley, Valentin-Anderson, Scott, Abercrombie).
- The engine's RELATIVE ordering has real signal (it differentiated Tealer 5.3 from Nuneviller 9.4 on evidence).
- The ABSOLUTE scale is unusable until recalibration. We harvested the ranking, discarded absolutes,
  anchored into band 5.8–7.2 for the case study display.
- 5 players timed out (apex engine does live web research per call, runs long) — placed by record/tier.

## NEXT PHASE (the real "make it robust" work)
1. **Recalibrate the lab engine** (MJ=9.3 ceiling; current reads run hot/near-ceiling). This is the
   long-parked recalibration — it's now the blocker for fair MLV absolutes AND correct LOVB absolutes.
2. After recalibration: re-grade all 12 MLV + LOVB on the calibrated engine → get FAIR same-scale absolutes.
3. Promote the calibrated engine + MLV profiles to the PROD worker (currently MLV only on lab/dev worker).
4. Then the /verdict deep-links light up for MLV too (currently prod worker has no MLV profiles).
5. Dedupe: 'maringrote'/'grote' alias collides with pre-existing marin-grote-texas — harmless warning, clean up.

## BRANCH/DEPLOY MAP (important)
- SITE (case study, /lovb, etc.) = main branch → netlify deploy. Prod: fieldcheck-app.netlify.app.
- WORKER (engine, PLAYER_PROFILES) = lab branch → wrangler deploy --env dev/prod. 
  Worker MLV profiles are on LAB + DEV WORKER only. Prod worker does NOT have them yet.
- These are independent; keep them on their branches. worker.js differs main vs lab (lab = apex WIP).
