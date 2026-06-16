# FIELDCHECK · SETTLED DECISIONS LEDGER

> **PURPOSE.** This file holds *settled* decisions. When a number or rule is here, that IS the answer.
> The only open question is ever the *mechanism* that produces it — NEVER the value.
> **If live output disagrees with this file, the OUTPUT is the bug, not this file.**
>
> **PROTOCOL (binding on Claude):** Before proposing any grade/number/rule for anything listed here,
> READ THIS FILE FIRST. Do not re-derive, re-argue, or "improve" a settled value. If Sridhar says
> "we already decided this," the answer is here — find it, don't reconstruct it from memory.

---

## CALIBRATION — SETTLED NUMBERS (do not re-derive)

| Athlete | Number | Band / Mechanism | Settled | Notes |
|---|---|---|---|---|
| Madisen Skinner | **7.3** | college_amateur / d1 → R3 compression (ceiling 7.4) on raw ~8.7 | Jun 13 2026 | NOT pro band. prime_pro→R4(9.3) leaves 8.7 uncompressed = WRONG. |

---

## DOCTRINE — SETTLED RULES (do not re-litigate)

1. **NO ARTIFICIAL CAPS.** Numbers fall NATURALLY to the right level via the real compression path
   (V5 R-rules). Never hardcode a grade, never clamp to force a number. The engine's number IS truth.
2. **Curated marquee athletes are graded in their AMATEUR/COLLEGE band, not the pro band.**
   (This is what makes Madisen's honest number 7.3, via R3.) Facts (bio/awards/photos) stay curated;
   only the GRADE is computed.
3. **SCALE (governs all):** 10=ceiling · 7+=HOF trajectory, rarest air · 6=real track · 5=solid · 4=good.
   Every point is enormous. Numbers should be LOW and EARNED. 8+ extremely tough. >9.0 near-perfection,
   almost no one. (Tenet 49/57)
4. **PROD IS FROZEN** during stability/calibration work unless Sridhar explicitly says ship.
   Only prod change in the Jun12-13 arc was FCBase95 (phantom-match fix).
5. **When output ≠ a settled number:** the output is the bug. Fix the mechanism; never argue a fresh
   number for a settled one. READ TRANSCRIPTS / this file before re-driving.

---

## STABILITY MECHANISM — WHAT'S IN THE ENGINE (DEV)

- **L1 (FCBase99):** temperature:0 on all 19 Anthropic calls. Kills value-variance. KEEP.
- **L2 (FCBase100):** stage pin for curated profiles. KEPT but REPLACED by band fix below.
- **L2b (FCBase101):** tier-pin-to-pro + zero-guard. **REGRESSION — reverted.** Forced 8.7, more Nones.
- **L3 (FCBase102):** verdict-lock cache (KV verdict-lock:v1:{slug}, 180d, lock-first-good, ?refresh).
  WORKS mechanically. Optional: use to pin exact value once band is right.
- **FCBase106 (BAND FIX):** curated profiles resolve college_amateur/d1 → R3 compresses naturally.
  **Madisen 7.3 ×5 stable (7.30–7.33).** This is the current good DEV state.
- Known: canonical_facets_8 returns all-null ~1/3 of fresh calls (line ~8543 bridge, synth pass
  deferred). Verdict-lock masks it. BACKLOG: reduce null-facet rate.

---

## HOW TO USE THIS FILE
- Add a row/line ONLY when Sridhar confirms a decision is settled.
- Never silently change a settled value. If it must change, Sridhar says so explicitly and we date the change.
- Claude greps this file at the start of any calibration/number work.

---

## BATTERY READING — FCBase106 (Jun 13, SETTLED)

**"90% RED" on the battery is a STALE-DASHBOARD ARTIFACT, not engine failure.** Read the DISTRIBUTION, not the RED count. The engine grades correctly and harshly:
- HS: median 5.3 / avg 5.0 (cap 5.4) — harsh, in-band ✓
- D1: median 6.0, all marquees 7.2–7.33 UNDER 7.4 cap, DIFFERENTIATED (not pancaked) ✓
- D2: median 6.7 (cap 6.8) ✓ · D3: median 4.0 ✓

**Breakdown of the RED count (all explained, ~0 real grade bugs):**
- "EXCEED" rows (14) = flagged vs OLD CURATED expected value, NOT vs cap. Every d1 athlete (Stokes 7.24, JSJ 7.24, C.Williams 7.25, Brandon 7.33…) is UNDER the 7.4 cap. NOT real problems — this is 6.3 working.
- "null" rows (~37–55) = known facet-reliability issue (canonical_facets_8 all-null ~1/3 calls). FIX = verdict-lock (L3): lock a good roll, never serve null. Known, has a solution.
- "expected" rows (~67) = battery answer-key calibrated to OLD curated numbers. FIX = recalibrate the key to de-curated numbers (battery-key recalibration task), NOT the engine.

**Genuine punch-list from the whole battery (tiny):**
1. Recalibrate battery answer-key to de-curated numbers (so dashboard tells truth).
2. Null-facet reliability → verdict-lock to hold good rolls.
3. ~1 classification edge case: Alijah Arenas graded pro/early_pro but is HS — same prime_pro misclassification as Madisen; apply the band-fix pattern.

**RULE: never panic at the battery RED% again — read the per-tier distribution medians first. They are the proof. Phase 6.3 (no-hardcode harsh natural composites) is PROVEN by this battery.**

---

## SCALE LADDER (Sridhar confirmed Jun 13, SETTLED — supersedes old V4 caps)

The reader-facing ladder, in honest de-curated numbers:
- **10** = once-a-generation apex; a handful ever (Jordan = 10).
- **7+** = Hall-of-Fame trajectory, the rarest air. Past 7 = a HOF path almost no one reaches.
- **5–6** = on a real track; solid, climbing to the next level.
- **4** = good — AND roughly the **best high-schooler in the country**. A 4 is already extraordinary.
- **below 4** = building the base, getting on film.

**CRITICAL:** the old V4 cap numbers (HS 5.4 / D1 7.4) are the PRE-Kevin-reset engine caps and are NOT the reader ladder. Best HS ≈ **4**, NOT 5.4. When showing a kid the scale, use THIS ladder. The 1.1 reframe card (RECLAIM_11_CARD_V2) renders on these numbers.

---

## VERDICT-LOCK L3 (FCBase107, Jun 13, SETTLED — DEV)

Rebuilt the verdict-lock on the marquee/instant path (it was rolled back with the FCBase105 good-ground restore). Uses existing kvGet/kvPut + KV namespace FIELDCHECK_KV.
- **Read** before handlePlayerVerdict: if locked verdict exists with composite>=3.5 and no ?refresh → serve instantly.
- **Write** after assembly: cache only GOOD verdicts (composite>=3.5, non-null). Null/thin rolls serve through but never cache → next load retries until good.
- **?refresh** bypasses read + recomputes + overwrites lock.
- **NO grading change** — only caches the good number. Key = verdict-lock:v1:{slug}:{sport}, 3yr TTL.
- **PROVEN:** Madisen primed via ?refresh → 7.31, then ×5 served identical 7.31 (was wobbling 7.30-7.33 + ~1/3 null). Every page now stable + instant.
- Marquee path = /api/marquee/verdict-instant (handler ~line 37332). This is the path the WVB index + verdict pages hit.
- NOTE: the 110-battery uses POST /verdict/player with skipCache:true — it does NOT hit the marquee lock, so battery still shows raw compute (thin rows remain in battery view). The lock fixes the USER-FACING pages, which is what matters for launch/demo. A separate /verdict/player lock can be added later if we want battery-path stability too.

---

## ALIJAH ARENAS — RESOLVED (Jun 14, NOT a bug)

Verified via web search: Alijah Arenas (HE — Gilbert Arenas's son) signed with USC as a 5-star in HS class of 2025, played 2025-26 freshman season (injury-shortened), withdrew from 2026 NBA Draft, RETURNING to USC for 2026-27 (sophomore). Engine resolves him correctly: composite 5.8, tier d1, stage college_amateur, cap 7.4, school USC — HONEST and under cap. The old memory note ("Alijah = HS junior, misclassified as pro, needs band-fix") was STALE/WRONG. No fix needed. The battery YELLOW was a stale-expected-band artifact, not a real grade error. LESSON: verify present-day athlete facts via search before assuming a classification bug.

---

## PHOTO SYSTEM (FCBase108-110, Jun 14, SETTLED — DEV) · Tenet 53 + Tenet 41

The scalable multi-source photo system (Sridhar: "wiki is just ONE source, run through ~50, it's a wide world"):
- **Many sources** (Tenet 53): curated bio (directus) · school/league official (huskers, lovb, usav) · MaxPreps · On3 · 247 · ESPN · NCAA · PrepHoops · Hudl · conference · og:image from any page · Wikimedia · sanity/CDNs. Wikipedia is ONE entry, not the default.
- **Identity guard** (Tenet 41): every photo verified to be THIS athlete before use. Curated bio added FIRST (verified). Open-web images name-gated (source/page/filename must contain athlete name tokens — same guard Wikipedia already used). HEAD-test for liveness on non-trusted hosts.
- **Cache discipline:** photo-cache READ skipped on skipCache/refresh (recompute fresh, no stale wrong photo). Cache WRITE only stores verified photos (never re-poison). 30-day TTL.
- **BUG FIXED:** Madisen/Harper were getting Asjia O'Neal's photo (teammate contamination — all on usavolleyball.org, open-web added unvalidated + poisoned cache). Now each athlete gets their OWN distinct verified face: Madisen=sanity, Harper=huskers, Asjia=directus, Dybantsa=wikimedia — 4 sources, 4 correct.
- LESSON: breadth WITHOUT identity-guard = confident wrong faces (worse than blank). Need both: many sources + per-athlete verification. "Wrong face on the page" is the #1 launch-demo sketchy risk (Kevin).

---

## TENET 61 · GITHUB-SYNC-ON-EVERY-DEPLOY (Jun 14, PERMANENT — prime-time security)

Code lives in THREE places, each covering a different failure:
- **LOCAL** `~/Desktop/fieldcheck-proxy` — working copy + freeze tarballs = fast rollback.
- **GITHUB** `git@github.com:giving29/FieldCheck.git` — offsite version history = laptop-loss / corruption net.
- **MEMORY + DECISIONS.md** — the decisions/reasoning (NOT a code backup).

**THE WORKING FOLDER IS THE GIT REPO.** `~/Desktop/fieldcheck-proxy` is itself the repo (remote=origin giving29/FieldCheck, branch main). Edit, deploy, AND push from ONE folder — no copy step, kills drift. The old `~/Documents/field-check/FieldCheck` clone is retired.

**BINDING RULE:** EVERY dev push AND every prod push ENDS with a git push. The deploy script's final step (after the freeze) is always:
```
cd ~/Desktop/fieldcheck-proxy && git add . && git commit -m "FCBase___ — what changed" && git push
```
`.gitignore` keeps secrets + tarballs + baks + dead dirs out. NEVER commit secrets (worker reads env 398× = safe; only 9 directus read-only image tokens present = low-risk CDN URLs). Each clean ship = local freeze + git push, so code + reasoning both live offsite.

---
## 2026-06-15 · REDIRECTS LIVE IN `/_redirects`, NOT `.netlify/netlify.toml` (root cause of the June-15 day-loss)
- **Netlify serves redirects from `/_redirects` at the publish root** (and root `netlify.toml`). It does NOT read `.netlify/netlify.toml`. All June-15 edits to `.netlify/netlify.toml` were on an IGNORED file.
- Symptom: every clean URL (`/gems`, `/coaches`, `/clips`, …) served the HOME page, because the live `/_redirects` was only `/* /index.html 200`.
- **Fix (committed 1396aca):** rebuilt `/_redirects` from the git-good toml (commit **369579c**, 43 rules) → converted to `_redirects` line format → added `/clips`,`/add-clip`,`/top100` → `/*` catch-all LAST. Verified all 8 nav links by `<title>` before commit.
- **Authority going forward:** `/_redirects` is the source of truth for routing. The 45 clean-URL rules + catch-all live there. `.netlify/netlify.toml` is not read by Netlify.
- **Recovery anchor:** good redirect set is in git `369579c:.netlify/netlify.toml`; current correct routing is committed in `1396aca:_redirects`.
- Deploy mechanics confirmed: publish dir = repo root (13GB); park `freezes/`+`backups/` to `/tmp` before `netlify deploy --prod --dir . --site 03408b50-...`, restore after. `.netlifyignore` does NOT work.

---
## 2026-06-15 · PARKED · APEX-CALIBRATION (curated Olympians clamp at 7.4) — diagnosed, not yet solved
- **Symptom:** Logan Tom & Jordan Larson (3× Olympians, GOAT-tier) clamp at composite 7.4 — same as college-band Madisen. They should break above 7.4 to their true apex numbers.
- **Diagnosed cause (Jun15, confirmed by facet read):** Tom's facet_avg = **7.72**, below the 8.0 apex-release gate. Individual facets (talent 8.2, competitiveness 8.1, but physical 7.1, coachability 7.4) don't reflect her curated record. Her `eval_grid_override` is apex (career_arc 10, size/reach 9.5, kills 9.5 → mapped anchor avg **9.34**), but **the scorer (Sonnet) weighs web scouting prose over the hand-verified curated anchors** — so physical stays 7.1 despite a curated 9.5 size/reach.
- **Tried (committed, safe, no regressions):** (a) FCBase·bug2 — A.2 reads curated awards/eval_grid_override defensively (760258f); (b) FCBase·bug2b — per-facet curated anchors pushed as heavy-weight evidence (63b3d23). Neither moved her facets; LLM read them but didn't raise scores.
- **Real fix (next phase):** change the synthesis PROMPT so curated anchors are treated as a FLOOR the scorer cannot go below without direct contradicting web evidence (not just "weight heavily"). OR apply curated facet anchors deterministically in CODE post-synthesis (like the v5 corrections), bypassing LLM reluctance. This is the "data + thousands of experiments" calibration phase — needs the 110-battery, its own focused session.
- **Status:** PARKED. Engine healthy & committed. Cooper fixed (5.4→7.4). Madisen 7.4 / Harper 7.1 / HS 3.4 all correct. No regressions. Apex-release mechanism proven in isolation (anchor avg 9.34); wiring it through scorer is the open work.
- **Mapping logic (tested, reusable):** eval_grid_override dims → 8 facets: talent←kills/hitting/athleticism; physical←size/reach/athleticism/durability; competitiveness←career_arc/serving; mental_strength←career_arc/character; mental_iq←passing/scheme_fit; coachability←scheme_fit/character; mindset←character/durability; character←character. Lives in worker.js BUG2B-FIX block (~line 3528).

---
## 2026-06-15 · PARKED · REWIRE ALL 3 VC DECKS WITH THE CLIPS MOAT (Sridhar, do when more is built)
- **Task:** update all three decks to weave in the new Clips Moat + God-Level engine breakthrough — Master Deck, Kevin's deck (/deck-kevin), Arjun's deck (/deck-arjun).
- **Framing rule (important):** go back to the ORIGINAL Kevin deck baseline — do NOT add "since our call" / "as we discussed" / progress-update language. Just present the awesome new stuff as the current state of the thesis, as if it always was the pitch. Clean, not a changelog.
- **What to weave in:** the Clips Moat (players volunteer the world's largest proprietary GRADED amateur dataset; incentive alignment exposure↔data; cold-start solved by inverting who supplies data) · the two-halves system (God-Level engine = HOW we grade vs the GOAT; Clips = WHAT we grade + growth loop) · 5 locked decisions (weekly cadence, 30s rail, segmented Top 100, sport-specific talent + universal behavioral facets, private-default) · the data-monopoly VC line ("1M/1B/10B graded clips growing at X/week — no one has graded amateur perf data at this scale") · two flywheels (data + badge-share growth).
- **Decks live at:** /deck (master), /deck-kevin (4 sections: gap/proof/WVB wedge/where this goes), /deck-arjun (5 sections: thesis/live today/stickiness loop/revenue/moat). Talk-track: SRIDHAR-TALK-TRACK-KEVIN-ARJUN.html. Source the new content from FC_CANONICAL_STATE_V1.html Pane 21 (Strategy & Arch) + BREAKTHROUGH_CLIPS_MOAT.md.
- **Status:** PARKED until more of the breakthrough is built (Sridhar's call — "park it till we get through more amazeness").
