# FieldCheck Engine Recalibration — Scope for the Uncapped UTR Scale (LAB)
_The parked #3. This is a dedicated lab session, done fresh — NOT an end-of-session quick edit._
_Grounding: FIELDCHECK_SCALE_MODEL_V2.md (uncapped model) + DECISIONS.md (settled numbers)._

## THE GOAL
Recalibrate the grading engine (worker.js on `lab`) from the OLD bounded model
(10 = unreachable, GOAT ≈ 9.3 ceiling) to the NEW uncapped UTR model
(no ceiling; GOATs land where they naturally land; tough grading preserved).

## WHY IT'S BLOCKED / HARD
- Current engine runs HOT and BOUNDED: curated Hentz came back 9.3 (tied Larson) — wrong.
- The absolute scale is unusable; only relative ordering has signal today.
- Uncapping without recalibrating would just push everyone toward a fake-high ceiling.
- This is real algorithm work on a 3MB worker — needs focus, not a rushed pass.

## THE WORK (in order, next lab session)
1. **Define the uncapped anchor set.** Pick ~10 cross-sport GOATs and where they SHOULD land
   on the uncapped scale (Jordan, Larson, Messi, etc.) — the calibration targets. Decide the
   density: how tight is the top band (UTR keeps top-100 near 16), how much headroom above the GOAT.
2. **Rewrite the composite/scaling logic** in worker.js so the number is open-ended, not clamped at 10.
   Preserve the tough grading (every point earned; most athletes low; 8+ rare).
3. **Re-grade the anchor set on dev-worker**, confirm GOATs land at their targets and the
   spread is honest (a libero ≠ tied with a 4x Olympian OH).
4. **Re-grade the curated marquees** (LOVB + MLV + the 12 MLV profiles) → get fair uncapped absolutes.
5. **Update the case study + any scale-showing pages** with the new absolutes (currently anchored/illustrative).
6. **Promote lab → prod worker** only after the anchor set + curated set validate.
7. Then /verdict deep-links show uncapped numbers for everyone, and the MLV profiles work on prod.

## VALIDATION GATES (don't promote until all pass)
- GOAT anchor set lands at targets (±0.2)
- No position inversion (libero not tied with elite OH; setter not above GOAT)
- Tough grading intact (median amateur stays low; 8+ stays rare)
- LOVB still stacks above MLV (the case study thesis must survive recalibration)
- curated_lookup_succeeded across all marquees on dev-worker

## FILES / COMMANDS (from prior lab sessions)
- Engine: worker.js on `lab` branch. Deploy dev: `wrangler deploy --env dev`
- Dev worker: fieldcheck-proxy-dev.sridhar-nallani.workers.dev
- Grade: POST /verdict/player {name, sport, skipCache:true} → encyclopedia.eval_grid.composite
- MLV profiles + aliases already injected on lab (commit 36e463b)
- Batch graders exist: grade_all_mlv.sh, regrade_missing.sh (in the script archive)

## NOTE
This is the single highest-leverage remaining FieldCheck work — it's what makes the
uncapped model REAL (not just canon + copy). But it's a focused lab session. Do it fresh.
