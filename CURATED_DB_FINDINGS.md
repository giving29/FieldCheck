# 🔑 CURATED DB — THE CANONICAL SOURCE OF TRUTH (definitive findings)
# Discovered end of session Jun 30 2026. THIS IS THE MOST IMPORTANT FILE. Read first next session.

## THE WORKER API IS THE REAL PLAYER DATABASE
Base: https://fieldcheck-proxy.sridhar-nallani.workers.dev
(dev: https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev)

### Endpoint 1 — the INDEX (enumerate everyone)
GET /api/marquee/list
  → { schema_version, total_instant_verdicts, by_sport, slugs, players[274] }
  → each player: { slug, name, school, position, sport, tier }
  → 274 total curated players; 55 are volleyball.
  → NOTE: list gives TIER but NOT composite. Composite requires the per-player call below.

### Endpoint 2 — the FULL RECORD (per player, authoritative)
GET /api/marquee/verdict-instant?slug=<slug>&sport=<sport>
  → 148KB of authoritative data per player. served_from:"edge_cache_curated_db",
    confidence:"curated_authoritative", curated_db_version:"2026.Q2", schema 1.2
  → Key fields:
    - encyclopedia.eval_grid.dimensions.{physical,production,projectability} — nested facet scores
      each with {score, evidence, data_source:"curated"}
    - encyclopedia.eval_grid.composite  ← THE REAL NUMBER (e.g. Harper Murray 7.4, Larson 9.3)
    - pro_projection.{lovb_tier, lovb_summary, international_fit, olympic_pathway_2028}
      ← LOVB projection ALREADY BUILT IN (e.g. Murray lovb_tier:"TOP_PROSPECT")
    - identity, measurables, awards_and_honors, career_history, character_context, trajectory
  → Missing slug returns {ok:false, error:"not_in_marquee_index"}

## SLUG PATTERN (how to resolve any player)
  firstname-lastname-[lovbteam|school]-sport
  LOVB pros: jordan-larson-lovb-nebraska-womens-volleyball, madisen-skinner-lovb-austin-...,
             kelsey-robinson-cook-lovb-atlanta-..., jordan-thompson-lovb-houston-...
  College:   harper-murray-nebraska-womens-volleyball, anna-debeer-louisville-...
  Get exact slugs from /api/marquee/list — do NOT guess.

## REAL COMPOSITES CONFIRMED (replacing ALL stale local values + my hand-authored reads)
  Jordan Larson 9.3 (ELITE+) · Merritt Beason 8.4 (ELITE) · Anna DeBeer 7.4 (STAR) ·
  Madisen Skinner 7.3 (ELITE+) · Harper Murray 7.4 (STAR)
  ⚠️ My hand-authored fc_reveal reads (Larson 7.9 etc.) are WRONG — superseded by DB. Discard as truth.

## TIER HIERARCHY (already in the DB — this IS the anchor structure Sridhar asked for)
  ICON > ELITE+ > ELITE > STAR
  ICONs (the anchors / the yardstick): Kerri Walsh Jennings, Misty May-Treanor, Karch Kiraly,
    Foluke Akinradewo Gunderson.
  ELITE+ LOVB greats: Larson, Skinner, Eggleston, Robinson-Cook, Thompson, Ogbogu, Hancock,
    Logan Tom, Destinee Hooker, Kim Hill.
  → SRIDHAR'S DIRECTIVE: anchor the LOVB greats into the algorithm as calibration references.
    The DB's ICON/ELITE+ tiers + the lab engine's GOAT-anchor doctrine (FCBase116) already
    support this. The greats don't sit ON the scale — they DEFINE it.

## LOVB vs MLV STATUS IN THE DB (the Kevin deliverable)
  - LOVB pros: WELL represented (slugs carry lovb-team: austin/nebraska/houston/atlanta/madison/salt-lake).
  - MLV players: LARGELY ABSENT. Beason shows as "lovb-atlanta" (signed LOVB?), DeBeer as "louisville"
    (college). Morgan Hentz, Jordyn Poulter = "not_in_marquee_index" (genuinely not curated).
  - IMPLICATION: the disparity board is a QUERY over LOVB (data exists) but MLV needs curation
    ADDED TO THE DB (server-side), not authored into stale local files.
  - ⚠️ Some names I assumed MLV (Beason) are actually in LOVB per their slug — VERIFY league
    membership from the DB, don't assume from my earlier research.

## WHAT THIS MEANS FOR THE WHOLE EFFORT
1. The 5 stale local stores in index.html (FX/TRAJ/HERO/PROJ/reveal) = OBSOLETE CACHES. The plan is
   to make surfaces read the curated DB, not reconcile the local junk.
2. The LOVB board is mostly a QUERY+VIEW over the curated DB today.
3. MLV side needs players ADDED to the curated DB (how? find the DB write/curation path — unknown yet).
4. Composites live in per-player calls, not the list — board build = list + N per-player fetches
   (consider caching a static export at deploy time).

## NEXT SESSION — EXACT START
1. Dump full volleyball roster WITH composites: for each of the 55 vb slugs, fetch verdict-instant,
   pull eval_grid.composite + pro_projection.lovb_tier → build the master table.
2. Determine each player's LEAGUE (LOVB via slug / MLV / college) → the disparity dataset.
3. Find how the curated DB is WRITTEN/updated (to add MLV players + Poulter/Hentz). Inspect the
   worker (lab branch? separate repo?) — where does edge_cache_curated_db come from?
4. THEN build the LOVB-vs-MLV board as a view over real composites. Anchor ICONs/ELITE+ as the scale.
