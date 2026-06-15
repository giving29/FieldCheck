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
