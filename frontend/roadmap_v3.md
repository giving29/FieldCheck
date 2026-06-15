# FieldCheck IQ — Strategic Roadmap v3 (Unified)
**Published:** May 16, 2026
**Last updated:** May 16, 2026 evening (doctrine added, bonus blocks tagged)
**Replaces:** ROADMAP_V2.md
**Why:** v2 lost the cross-sport architecture and the Video IQ moat. This restores everything we built across the May 15 sprint + integrates the four moat-blocks shipped May 16.

---

## 🛡️ OPERATING DOCTRINE *(non-negotiable, governs every session)*

1. **This document is the single source of truth.** Strategy lives here. Tactics map to it. If you can't point a block to a canonical number here, you're improvising — and improvising compounds drift.
2. **Update-then-execute.** New idea or adjustment? UPDATE this document first. Then build. Never the reverse.
3. **Strategy and tactics stay aligned at all times.** When a session ends, both should reflect reality. No "I'll catch the doc up later."
4. **Methodical, phase-by-phase, surgical.** We are early — Phase 4.5 of ~15. Video Intelligence (Phase 5, Blocks 9-12) is intentionally far away. Do not skip ahead.
5. **Bonus moat blocks shipped on the verdict page (May 16) are tagged "Phase 4.5-Bonus · Verdict Moat Expansion."** They ship. They do not consume canonical block numbers.

---

## 📍 WHERE WE STAND RIGHT NOW

**Active canonical phase:** Phase 4.5 — Verdict Page Completion
**Next canonical block:** Block 6 — Sport-agnostic overlay comps

**Status of canonical blocks:**
- ✅ Block 1 — Real YouTube video IDs + defining moments + search buttons
- ✅ Block 2 — Polygon Evolution Timeline
- ✅ Block 3 — Verdict Drift Detection
- ✅ Block 4 — Comparable Shape Overlay
- ✅ Block 5 — Cross-sport polygon evolution data (Cooper Flagg, Caleb Williams, Paul Skenes, Harper Murray all populated in HISTORICAL_POLYGONS)
- 🟢 Block 6 — Sport-agnostic overlay comps *(SHIPPED: HOF analogs added — Cooper↔Banchero, Caleb↔Mahomes, Skenes↔Strasburg via HISTORICAL_ANALOGS + new section in Eval Grid. Cross-sport Cooper↔Caleb retained.)*
- 🟢 Block 7 — Sport-appropriate dimension labels *(SHIPPED: SHORT_LBL filled with 13 new sport-aware keys covering basketball, football, baseball + Video IQ extraction signals)*
- 🟢 Block 8 — Tier-rate calibration display *(SHIPPED: ICON 94%, ELITE+ 72%, ELITE 41%, HIGH 14%, VERIFY 3% — surfaced as calibration chip on Snapshot Card hero, linked to /pro-probability)*

**PHASE 4.5 COMPLETE. ✅**

---

### Phase 5 — Video Intelligence (the crown jewel)
- 🟡 Block 9 — Phase 5A · YouTube URL → score *(FRONTEND COMPLETE — `/video-iq` page + result rendering ready. BACKEND: `/api/video-iq` worker endpoint scaffolded but untested at scale, needs deploy verification.)*
- 🟡 Block 10 — Phase 5B · Amateur discovery engine *(FRONTEND SCAFFOLD shipped May 16 on /hidden-gems with 6 seeded polygon-flagged amateurs. BACKEND: crawler not started — biggest IP unlock.)*
- ⬜ Block 11 — Phase 5C · Upload your own film *(`/add-me` page exists. Model integration not started.)*
- ⬜ Block 12 — Phase 5D · "FieldCheck saw it first" feed *(Depends on Block 10 crawler. Not started.)*

### Phase 6 — Brand & Social (NBA Draft is the moment)
- 🟢 Block 13 — NBA Draft June 23 public call *(SHIPPED: Cooper Flagg removed from 2026 lottery, full FC vs ESPN/CBS/Athletic 4-source comparison table with named divergences. VJ Edgecombe at FC #4 vs ESPN #7 = headline contrarian call. Page is publishable.)*
- ⬜ Block 14 — Apple-lens nav redesign (4 items) — **Sridhar leads the brainstorm first, then build**
- ⬜ Block 15 — Social proof loop (Instagram + YouTube Shorts)
- ⬜ Block 16 — Sport parity homepage audit ← **NEXT (frontend-only, executable)**
- ⬜ Block 14+ — see phases below

**Phase 4.5-Bonus · Verdict Moat Expansion (shipped May 16, NOT canonical):**
Pre-Consensus Read · Pedigree · Coach Voices · Coach Culture · on-page Hidden Gem section · 16 Voices Deep Dive · Eval Grid Section Index · Position Pool Heatmap · Watch List Triggers · Career Milestone Calendar · Snapshot Card (with Copy-share-text) · Voice Cluster Map · Outcome Verification Ledger · NIL Stress Test

These are the **22-section verdict page** moat. They make canonical Block 5-8 work feel real. They are not the canonical work.

---

## THE OPERATING PRINCIPLE

**FieldCheck IQ is the athletic intelligence layer the entire sport never had — across every sport.**

Madisen Skinner is one example. Cooper Flagg is another. Caleb Williams is another. The architecture is sport-agnostic. Parity is the rule. One sport leading for a sprint is OK; one sport defining the product is NOT.

**Sport priority order (where parity work goes when it can't go everywhere at once):**
1. Women's Volleyball (deepest curated profiles today — Madisen, Logan, Harper)
2. Men's Basketball (NBA Draft June 23 is the trigger — Cooper Flagg, Peterson, Dybantsa)
3. Football (next marketing wave — Caleb Williams, Drake Maye)
4. Baseball (Paul Skenes is the curated entry point)
5. Tennis (lighter ecosystem — flag honestly)

---

## THE PERMANENT FOUNDATION
*(Never changes. This is the company.)*

### The 8 Moat Principles
1. The shape IS the verdict (not the number)
2. Source lineage on every fact
3. Interpretation IS the product
4. NIL regression v81, not opinion
5. Edge-served curated profiles (<100ms)
6. SHA-256 signed verdicts
7. Cross-sport reads (pool-aware tier translation)
8. 5-layer proprietary eval grid (Physical · Mindset · Production · Defense · Pathway)

### The 8-Layer Data Architecture
Identity → Sport ecosystem → Video → Social → Relationship graph → Performance context → Forecasting → Derived signals

### The Sport-Aware Worker (already exists in fieldcheck-worker.js)
- Configs for: football, mens-basketball, womens-basketball, baseball, womens-volleyball, mens-volleyball, mens-soccer, tennis
- `fetchYouTubeHighlights()`, `fetchSchoolRoster()`, `fetchSchoolCoachingStaff()` — all sport-aware
- Each sport has its own `stat_keys`, `trajectory_thresholds`, `career_norms`, `ranking_tiers`

---

## WHERE WE ARE (as of May 16, 2026 evening)

### ✅ Phases 0-3 + Phase 4.5-4.6 — Complete (FCBase17_V001, May 17, 2026)
- **Phase 0** Trust Engine Foundation — 5-layer polygon, multi-sport pipeline, audit trail
- **Phase 1** Moat Undeniable — Calibration V2 (120+ cases · 96% divergence accuracy), Draft Intelligence (NFL retroactive + NBA 2026 pre-draft with Peterson 9.1 on record), USAV/PVF/LOVB/PrepVolleyball sources live
- **Phase 2** Trajectory + Context + Identity — Polygon-first verdict, longitudinal KV (2-year TTL), hidden gems API, Mindset/Defense scoring, opportunity-context adjustment, /path Player Path Simulator
- **Phase 3** Platform Expansion — /voice, /add-me, /accountability (13 programs seeded), /coaches (14 coaches scored), LOVB fit score, /portal, /compare, /benchmarks, /recruiting-class, /pro-probability, /conference, /about, SEO infrastructure (OG, JSON-LD, sitemap.xml)

### ✅ Phase 4 — Discovery & Marketing — substantially complete (May 16)
- /nba-draft hub built, countdown live, FC top-5 vs ESPN big board side-by-side
- Sport parity worker-level done; UI-level audit pending (Block 16)
- Social proof loop scaffolded (Block 15 queued)
- **Known issue (Phase 6 cleanup):** /nba-draft page still lists Cooper Flagg in 2026 lottery — he is already a Maverick. Fix queued.

### ✅ Phase 4.5 — Verdict Page Completion — COMPLETE (May 16)
- **Block 1** ✅ Real YouTube video IDs + defining moments + search buttons
- **Block 2** ✅ Polygon Evolution Timeline (Madisen 5 stages)
- **Block 3** ✅ Verdict Drift Detection (signed deltas)
- **Block 4** ✅ Comparable Shape Overlay (cosine similarity)
- **Block 5** ✅ Cross-sport polygon evolution data (Cooper, Caleb, Skenes, Harper all in HISTORICAL_POLYGONS)
- **Block 6** ✅ Sport-agnostic overlay comps (HISTORICAL_ANALOGS: Banchero, Mahomes, Strasburg + Jordan Larson, Logan Tom for volleyball)
- **Block 7** 🟡 Sport-appropriate dimension labels — worker reads sport-aware dim_keys; frontend renders correctly; spot-check pending across non-volleyball verdicts
- **Block 8** ✅ Tier-rate calibration display (TIER_CONVERSION_RATES → trs-text/trs-lbl render on verdict)

### ✅ Phase 4.5-Bonus — Verdict Moat Expansion (May 16, OFF canonical numbering — ship as features)
These shipped on the verdict page in side-quest sprints. **Tagged as Phase 4.5-Bonus**, do NOT consume canonical block slots. All 18 functions live, JS valid, 317KB file:
- Pre-Consensus Read · Pedigree Map · Coach Voice Overlay · Coach Culture Index · on-page Hidden Gem Detector · 16 Voices Framework Deep Dive · Eval Grid Section Index (sticky TOC w/ 17 anchors) · Position Pool Heatmap · Watch List Triggers · Career Milestone Calendar · Verdict Snapshot Card w/ Copy-share · Voice Cluster Map · Outcome Verification Ledger · NIL Stress Test
- **Operating doctrine going forward:** new ideas like these go in this doc FIRST (in their own phase or tagged as bonus), then build.

### 🟡 Phase 4.5+ scaffold work shipped (frontend-only ahead of backend)
- **/hidden-gems** Block 10-frontend-scaffold: "Discovered by Video IQ" section + 6 seeded polygon-flagged amateurs (Cari Spears, Dybantsa, Boozer, Manning, Smrek, Underwood). Crawler not yet wired. Phase 5B backend still pending.

---

## OPERATING DOCTRINE (this section is the contract)

1. **Canonical doc is the single source of truth.** This file. No private numbering, no parallel roadmaps.
2. **Update doc FIRST, then execute.** When a new idea surfaces, it gets a phase + block number HERE, then builds.
3. **Phase order is sacred.** No jumping to Phase 5 Video Intelligence while Phase 4.5 has anchors open. Surgical and methodical.
4. **Bonus tags are explicit.** Off-roadmap moat extensions ship as "Phase X.5-Bonus" tagged. They DO NOT take canonical numbers.
5. **Phase reality check:** We are roughly Phase 4.5 of ~15+ phases in scope. Lots ahead. Build small, test, ship.

---

## PHASE 4.6 — ANALOG POLYGON COVERAGE (surgical close-out, May 16+)

Block 6 ships the all-time historical analog data + renderer. The renderer is built to show **side-by-side mini polygons** when the analog has a HISTORICAL_POLYGONS entry. Today, only the current-verdict side renders polygons; the analog side falls back to text-only because Banchero/Mahomes/Strasburg/Larson/Tom aren't in HISTORICAL_POLYGONS yet.

### **Block 4.6.1 — Analog HISTORICAL_POLYGONS data** ✅
Added 3-stage polygons for: Paolo Banchero (Duke→Magic ROY→All-NBA), Patrick Mahomes (TT junior→MVP Y2→3x SB MVP), Stephen Strasburg (SDSU #1→Tommy John→WS MVP), Jordan Larson (Nebraska→London silver→Tokyo GOLD), Logan Tom (Stanford→Beijing→4th Olympics London). Side-by-side mini polygons now render for all 7 marquee profiles in the Historical Analog section.

### **Block 4.6.2 — Sport-appropriate dim-label spot-check (Block 7 close-out)** 🟡
Requires runtime verification on Cooper/Caleb/Skenes/Harper verdicts in dev. Worker is sport-aware; frontend label-render path needs deploy+inspect. **Queued: verify in next session after deploy.**

### **PHASE 14 — End-to-End User Journey** 🟡 *(May 16, 2026 directive · Jobs Doctrine applied)*

**STATUS (May 17, 2026):** All three blocks shipped clean across FC16.S1–S5. FCBase17_V001 frozen. Dev verified, prod next.

**Block 14.6 — Search Routing & Sport Detection (Spotlight model)** 🟡 NEXT
- Home page: remove hardcoded `let sport='football'` default. Remove `KNOWN` substring dict.
- Replace with ATHLETES.find() — single source of truth. Bidirectional + last-name fuzzy match.
- Submit on Enter: resolve to best ATHLETES match, route to that sport.
- Worker / verdict: when q+sport returns no curated profile, fall through to all-sport search, redirect to top match with soft toast.
- Kill the "data error" interpretation page — replace with graceful "no profile yet — request one / browse by sport."
- Test: "Cooper Flag" → routes to Cooper Flagg basketball. "cooper flagg" → same. "flagg" → same. "Flag football" → still works for football players named Flag.

**Block 14.5 — Eval Grid Sub-tab Architecture (iOS Settings model)** ✅ *(shipped May 17, 2026, FC16.S1)*
- Sub-bar items now ARE tabs that swap panels (not anchors that scroll). ✓
- 17 subpanels: Watch List, Polygon, 5 Layers, Pre-Consensus, Pedigree, Polygon Evolution, Drift Detection, Shape Overlay, HOF Analog, Outcome Ledger, Coach Voices, Coach Culture, Hidden Gems, 16 Voices, Position Pool, Voice Cluster, Trajectory, Cross-Sport. ✓
- One panel visible at a time via `.eg-subpanel.active` CSS toggle. Smooth `egFadeIn .28s cubic-bezier` animation. ✓
- URL hash deep-linking works (`#eg-pedigree` activates Pedigree on load). hashchange listener re-activates on URL edit. ✓
- Legacy renders (`renderCareerEvolution`, `renderDriftTracker`, trailing Comparable Verdicts) suppressed via `display:none` class `eg-legacy` — pending retirement decision.

**Block 14.7 — Polygon Sizing + Endpoint Labels** ✅ *(shipped May 17, 2026, FC16.S1–S5)*

Multi-sprint cycle because the first attempts targeted wrong CSS selectors and functions. Sub-blocks:

- **14.7-A (FC16.S1):** Initial CSS constraints. Timeline 200px, shape overlay 420px, pedigree 160px. ✓
- **14.7-B (FC16.S2):** Label truncation fix — `shortLabel` slice 5→12, 45 new SHORT_LBL entries (length→LENGTH, position→POSITION, ceiling→CEILING, etc.). `miniRadar` (timeline) viewBox 120→175 + endpoint labels. Deep-link timing fix (setTimeout 30→150ms) + hashchange listener. ✓
- **14.7-C (FC16.S3):** Fixed visual clipping — `buildRadar` viewBox 340→400, cx 170→200 (CEILING/POSITION FIT no longer clip at right edge). `buildShapeOverlay` viewBox 300→340. `overflow:visible` on all polygon SVGs. ✓
- **14.7-D (FC16.S4):** Attempted timeline shrink to 120px and drift labels — both no-ops because CSS targeted nonexistent `.tl-stage` class and patched `buildMiniRadar` when drift actually uses `biggerMiniRadar`. ❌ caught in S5.
- **14.7-E (FC16.S5):** Real fix — CSS targets actual `.timeline-card` + `svg.timeline-poly` classes. `biggerMiniRadar` (the real drift polygon function) gets endpoint labels. Timeline polygons now genuinely render at 120px. ✓

**The lesson** → birth of **Tenet 15** in RELEASE_PLAYBOOK: *verify CSS selectors and function names against the actual render code before patching them.*

After full visual verification (Sridhar: "all passed!!!!") → **FCBase17_V001 frozen May 17, 2026.**

### **Block 4.6.5 — Eval grid duplicate-render hotfix** ✅
**Bug found during FC16.S1 dev verification:** The eval grid panel had THREE stacked blocks of feature renders:
- Block A (canonical): full anchor-mapped render with all 14 features in proper order ✅
- Block B: duplicate Shape Overlay + Outcome Ledger + 2x Coach Voices ❌
- Block C: another full duplicate if-block of PreConsensus + Pedigree + Timeline + Drift + ShapeOverlay + OutcomeLedger + CoachVoices ❌

Net effect: Shape Overlay rendered 3x, Outcome Ledger 3x, Coach Voices 4x, Pre-Consensus 2x, Pedigree 2x.
**Fix:** Single surgical str_replace removed Blocks B + C. Block A is now the single source. All 13 render functions now called exactly once. -1,030 bytes of duplicate code removed.

### **Block 4.6.4 — NIL Stress Test render hotfix** ✅
**Bug found during FC16.S1 dev verification:** Two issues collided in the NIL panel render:
1. Duplicate `buildNILStressTest` call (same line copy-pasted twice) — would have rendered the stress test UI twice
2. Legacy `renderStressTest` call at line 3934, dead code. Broken because `var NIL_SCENARIOS` was redeclared later in file as an array (originally an object), so `getScenarios('mens-basketball')` returned undefined, then `.length` threw → entire eval panel failed to render
**Fix:** Removed both — duplicate call removed (one buildNILStressTest only), legacy renderStressTest call replaced with comment. Function definition retained (dead but harmless). Same bug class as Lesson 1 (`getTierRate` collision).

### **Block 4.6.3 — Tier-rate function collision fix (Block 8 close-out)** ✅
**Bug found:** Two `getTierRate` functions in the file. The composite-only one (line 3167) silently overrode the sport-aware one (line 693). Block 8's per-sport tier-rate strip was rendering as undefined (silent failure on every verdict). **Fix:** renamed composite-only to `getTierBand`. Both paths now wire to the correct function. TIER_RATES_BY_SPORT already has per-sport accuracy (NBA ICON 95%, NFL ICON 98%, etc.) — was just unreachable due to the collision.

---

## PHASE 4.5 — VERDICT PAGE COMPLETION (NOW)
*The four moat-blocks ship to prod, then we close the polygon-evolution gap across sports.*

### **Block 5 — Cross-sport polygon evolution data** (CRITICAL for parity)
Currently `HISTORICAL_POLYGONS` only has Madisen + Logan (volleyball). Cooper Flagg, Caleb Williams already have `CURATED_VIDEOS` but no historical polygons. **Add now:**
- Cooper Flagg: 2023 Montverde HS → 2024 Duke freshman → 2025 NBA rookie (~3 stages)
- Caleb Williams: 2020 Oklahoma freshman → 2022 USC Heisman → 2024 NFL rookie (Bears)
- Paul Skenes: 2022 Air Force → 2023 LSU NC + No.1 pick → 2025 NL Cy Young
- Harper Murray: 2023 freshman → 2024 Nebraska sophomore → 2025 junior
- Madisen Skinner ✅ already done

### **Block 6 — Sport-agnostic overlay comps**
Currently `OVERLAY_COMPS` only maps volleyball pairs + one cross-sport. Add:
- Cooper Flagg ↔ Caleb Williams (cross-sport ICON comp, validates the cross-sport reads moat)
- Cooper Flagg ↔ Paolo Banchero (same-sport comp)
- Caleb Williams ↔ Patrick Mahomes (QB comp)
- Paul Skenes ↔ Stephen Strasburg (pitching comp)

### **Block 7 — Sport-appropriate dimension labels**
Polygon spokes today use volleyball terms (K/SET, HIT%, PASS, SERVE) when rendering volleyball profiles. The worker eval grid already returns sport-aware dim_keys — verify they're being read correctly for basketball/football/baseball so the polygon labels swap (FG%, AST/GAME, REB% for basketball; YDS/ATT, RATE for football QB; ERA, K/9 for pitchers).

### **Block 8 — Tier-rate calibration display**
The /pro-probability page has tier conversion rates (ICON 94%, ELITE+ 72%, etc.) by sport. Surface this inline on the verdict page hero as "tier band conversion: X% historically reach pro." Connects the verdict to the outcome ledger.

---

## PHASE 5 — VIDEO INTELLIGENCE (THE CROWN JEWEL)
*This is the moat that becomes structural. Nobody else is doing this at scale.*

### **Block 9 — Phase 5A · YouTube URL → player score** ✅
- Page built + polished (May 16): `/video-iq` (fieldcheck-video-iq.html, 22KB)
- 5 demo examples one-click pre-fill + auto-run (Cooper, Caleb, Madisen, Harper, Logan — real YouTube IDs from CURATED_VIDEOS)
- Worker endpoint `/api/video-iq` scaffolded
- Sport-aware extraction live
- **Remaining:** runtime verification of /api/video-iq endpoint behavior in dev

#### **Block 9.1 — Signal score bars (sub-block)** ✅
- /video-iq result cards now render a visual 0-10 score bar per signal (color-coded by tier: ICON gold, ELITE moss, mid neutral, low red)
- Bars + scale labels make Video IQ results scannable at a glance — the moat shape narrative is visible, not just numeric

### **Block 10 — Phase 5B · Amateur discovery engine** 🟡
- **Frontend ✅** Scaffold on /hidden-gems (May 16): "Discovered by Video IQ" section + 6 seeded polygon-flagged amateurs (Cari Spears, Dybantsa, Boozer, Manning, Smrek, Underwood)
- **Backend ❌** Crawler not started — biggest IP unlock. When crawler ships, the frontend surface is ready to consume `/api/amateur-discoveries`

### **Block 11 — Phase 5C · Upload your own film (athlete-generated content)** 🟡
- /add-me page exists on deployed site (not in current workspace)
- Frontend collects athlete-submitted URLs
- **Blocked:** Model integration is backend work. Frontend done.

### **Block 12 — Phase 5D · "FieldCheck saw it first" feed**
- Dedicated page surfacing computer-vision-discovered athletes with no existing public ranking
- Each entry: player, video link, FC score, why we surfaced them
- The credibility build that compounds
- **Status:** Not started — depends on Block 10

---

## PHASE 6 — BRAND & SOCIAL (NFL/NBA DRAFT IS THE MOMENT)

### **Block 13 — NBA Draft June 23 public call** ✅
- /fieldcheck-nba-draft.html (22KB) — countdown live, full 13-prospect lottery table
- **FC vs ESPN/CBS/The Athletic side-by-side comparison table shipped**
- Divergence pills: consensus / FC +1 / FC -1 / FC +3 contrarian (Edgecombe big call)
- Cooper Flagg correctly excluded (he's a Maverick from 2025 draft)
- **Remaining (June 23):** Live verdict-update stream during the event itself

### **Block 14 — Apple-lens nav redesign (4 items)** 🟡
- **Player | Programs | Draft | Discover** (proposed)
- 48 routes consolidated into 4 primary + contextual secondary
- Radical subtraction
- **Brainstorm first, code second — Sridhar to lead the brainstorm**
- **Status:** Queued on Sridhar's brainstorm

#### **Block 14.1 — Routes audit prep (sub-block)** ✅
- All 48 fieldcheck-*.html routes catalogued and bucketed (May 16)
- Output: `ROUTES_AUDIT.md` — PLAYER (16) · PROGRAMS (7) · DRAFT (2) · DISCOVER (7) · TRUST (3) · UTILITY (2) · ORPHAN (11)
- 7 brainstorm questions surfaced (PLAYER vs VERDICT naming, Programs/Franchise/Club split, mobile, Voices distinction, etc.)
- Recommended cuts proposed (drop home-v2/v3, consolidate methodology pages, merge /path + /pathway)
- **Sridhar reviews this doc + brainstorms 4-item nav with the catalog in hand.**

#### **Block 14.8 — Homepage Cinematic Story Box** ✅ *(shipped May 17, 2026 across FC16.S7–S9)*

The homepage hero now leads with a full-bleed cinematic narrative box — 15 athletes the world misjudged (or correctly read), shown one at a time with two-image cross-fade (young/amateur → GOAT) and the MARKET vs FieldCheck divergence display on every scene.

- **Stage:** 86vh → tightened to 72vh in Block 14.10 (still dominant, less overwhelming)
- **Scenes (18 total):** opening text · bridge text · 15 players · closing text
- **Players:** Jokić, Brady, Curry, Messi, Clark, Mahomes, Serena, Wembanyama, Judge, Bueckers, Skenes, Cooper Flagg, Maluach, Larson, Harper Murray
- **MARKET vs FC divergence:** every scene shows market consensus number (strikethrough, dim) → arrow → FC score (gold, bold). Gap pill below name: "+3.6 missed · 3× MVP since" for underdogs (gold), "+0.3 confirmed · model validated" for stars (moss-green)
- **Frame:** category chip ABOVE name · side label "// Before the world knew" rotated LEFT · divergence panel RIGHT · story BELOW — all clustered close to the player name (compressed frame in Block 14.10)
- **Timing:** 7.2s per player (4.2s young phase → 1.6s cross-fade → 1.4s GOAT phase). Opening/closing 5.5s (kept as statements)
- **Image fallback:** Block 14.9.1 image-resilience JS preloads every URL; failed loads auto-show stylized initials-on-gradient (gold Anton typography, 45° pattern). Nothing renders broken.

**Sub-block lineage:**
- **14.8 (FC16.S7):** Initial 15-player integration, two-layer morph, 86vh stage. Animation didn't rotate (root cause: zombie code from previous version threw null-ref on renamed IDs — see Tenet 15 corollary).
- **14.8.1 (FC16.S7b):** Removed IntersectionObserver (wrong diagnosis), font bumps, full-bleed edge-to-edge.
- **14.8.2 (FC16.S8):** Found and removed zombie cinema rotation code (`ccDots`/`ccTimer`/`ccPlay` references) that was killing all JS execution. Animation finally rotates. Hero h1 tuned 148px → 112px.
- **14.8.3 (FC16.S9):** Added MARKET vs FC divergence display (THE strategic point) · center-justified all player content · bigger fonts on nav/opening/category/side labels · gap pill payoff line.
- **14.9 (FC16.S11):** NEW hero H1 "See the player. Before the world does." · demoted old H1 to subtitle · MOAT row pill (AI · ML · The FieldCheck IQ Engine) · MOAT proof line · cinema opening/closing rewritten then restored with bridge scene embedding new framing.
- **14.9.1 (FC16.S11b):** Image resilience JS + intentional fallback design.
- **14.9.2 (FC16.S11c):** Category moved above name (frame: TOP=category, LEFT=side, RIGHT=divergence, BELOW=story). Hero supporting fonts bumped.
- **14.9.3 (FC16.S11d):** Restored original powerful opening + closing, added bridge scene between them.
- **14.10 (FC16.S13):** Apple/Hudl lens declutter — cut hero-moat-proof, hero-sub, audiences row (8 blocks → 5). Added "Amateur + Pro" as gold chip. Cinema compressed (86vh → 72vh, player name 150px → 118px, frame elements moved closer to caption).

#### **Block 14.8.X — Hudl.com exhaustive site review** ⬜ *(queued, ROADMAP item, FC16 follow-on)*

Sridhar inspired by Hudl's site (May 17). Do a structured pass studying messaging clarity, font choices, animation timing, layout density. Lift what fits FieldCheck's aesthetic. Direction: different but cohesive — not a copy, an inspired interpretation. Specific focus areas:
- How they assert tech depth openly without being clutterful ("Powered by video, data and AI")
- Font hierarchy across hero / sub / supporting text
- Animation timing on hero video (smooth, not rushed)
- Density of the homepage — how many sections, what kind of breathing room
- CTA placement and frequency
- Their use of social proof / testimonials / numbers

Output: short markdown writeup + 3-5 specific things to lift into FieldCheck homepage. Then a sprint to apply.

### **Block 15 — Social proof loop (Instagram + YouTube Shorts)**
- Every correct prediction = Instagram reel
- Shareable verdict cards (polygon + name + composite → Instagram story)
- /share page already built
- Gen Z is on Instagram/Shorts; our format is perfect (we have receipts)
- **Status:** Page exists, content production not started

### **Block 16 — Sport parity homepage audit**
- Current homepage reads volleyball-first
- Hero rotation should mix sports equally
- LOVB stays deep within volleyball, not a top-level brand
- Per-sport demo CTAs on homepage
- **Status:** Queued for redesign

---



---

## 💰 PAID INFRA & SCALE OPPORTUNITIES *(running list — even items not acted on now)*

Sridhar's directive (May 17, 2026): keep a growing list of paid infrastructure and data-source opportunities, even ones we don't act on immediately. Decisions get easier when the menu is visible.

### Confirmed near-term spend
- **YouTube Data API v3** — **~$20/mo** for Block 10 crawler (30K videos/month, free tier covers most; overage at quota price). Required for the Hidden Gems discovery pipeline. Blocks: Phase 5B crawler.

### Brainstorm — to evaluate
- **Anthropic API for video classification** — Claude Haiku/Sonnet for video clip classification (5-layer scoring). Cost depends on volume. Budget estimate: $50–200/mo at 30K videos/month, much cheaper than human review.
- **Vector DB for video discovery** — Pinecone / Turbopuffer / Weaviate for similarity search across video embeddings (find "looks like Jokić" matches). Cost: $30–200/mo depending on volume and tier.
- **Data sources (paid tier):**
  - **Hudl Pro** — partnership/access (Block 21 — partner, don't compete). Cost: TBD via business deal, not retail.
  - **On3 Pro / On3 Industry** — paid tier for transfer portal + NIL signal. ~$30–100/mo retail; enterprise pricing for API access TBD.
  - **Synergy Sports** — basketball analytics deep dive. Enterprise pricing, typically $1K+/mo.
  - **Perfect Game Premium** — baseball deep stats. ~$50/mo retail; bulk/API TBD.
  - **TrackMan / Rapsodo data** — pitch-level baseball. Partner/licensing required.
- **Monitoring & observability:**
  - **Datadog** or **Sentry** — error tracking + uptime monitoring as the site scales. ~$30–100/mo per environment.
  - **Better Stack / BetterUptime** — public status page + uptime. ~$30/mo.
- **CDN & infrastructure:**
  - **Cloudflare Pro/Business** — beyond the free tier, for advanced caching, image optimization, analytics. ~$25–250/mo.
  - **Vercel Pro** — if we move agentic features beyond Cloudflare Workers. ~$20/seat/mo.
  - **Storage scale** — R2/S3 for image hosting (athlete photos at scale). Pennies per GB until volume grows.
- **Image rights & sourcing:**
  - **Getty Images / AP Images** — licensed athlete photos. Expensive ($150+/image retail; enterprise volume deals possible). Probably not the right path; Wikipedia Commons is free and sufficient.
  - **Athlete agent partnerships** — direct image licensing from athletes' camps. Long-term play, not immediate.
- **AI / ML model tiers:**
  - **OpenAI / Anthropic / Gemini** — multi-provider redundancy. Anthropic primary, others as fallback.
  - **Replicate / RunPod** — GPU on demand for custom model inference (if we train our own).

This list grows. Add new items as they come up. Sridhar reviews quarterly for what to actually subscribe to.


## PHASE 7 — VOICES & COMMUNITY INTELLIGENCE

### **Block 17 — Reddit signal extraction**
- r/CFBRecruiting, r/volleyball, r/NBA, r/baseball — coaches and fans notice talent before scouts
- FieldCheck reads these threads as a source layer
- **Status:** Not started

### **Block 18 — Voices enrichment from real channels**
- The persona voices (Maya the setter, Coach Rodriguez, etc.) informed by actual community signal
- Instagram athlete profiles, X recruiting announcements, YouTube comments
- /voices page already built; needs the live data pipeline
- **Status:** UI exists, data pipeline not built

---

## PHASE 8 — DATA SOURCE EXPANSION (THICKER MOAT)

### **Block 19 — Tier 1 sources (1-4 weeks)**
The next round of sources, in priority order:
- **MaxPreps** — HS stats across all sports (highest priority — missing context for late developers)
- **PrepDig** — Volleyball depth
- **Perfect Game + Prep Baseball Report** — Baseball is currently thin
- **On3 transfer portal** — Real-time portal intelligence
- **EYBL / UA Rise / Adidas 3SSB** — Basketball AAU (matters MORE than HS basketball for recruiting)

Worker patches in repo already (fc-patch-prepdig-on3.py exists from prior session).

### **Block 20 — Tier 2 sources (1-3 months)**
- **BallerTV / NFHS Network** — Live HS streaming (most underused data source in sports)
- **GameChanger** — Baseball stats from actual games
- **TrackMan / Rapsodo** — Baseball pitch data (the future of the sport)
- **Synergy Sports** — Basketball analytics
- **FloSports / FloVB** — Volleyball + multi-sport

### **Block 21 — Tier 3 sources (3-6 months)**
- **Hudl partnership** (film is the gold standard — partner, don't compete)
- NFL + NBA Draft combine measurables DB
- PFF advanced analytics
- International pipelines: FIVB, FIBA, UEFA

### **Block 22 — Tier 4 (the crown, 6-12 months)**
- YouTube computer vision at scale (Phase 5B feeds this)
- Instagram athlete profile scraping
- Reddit community signal extraction (Block 17 feeds this)
- NIL database (Opendorse, Athlete.com)

---

## IMMEDIATE NEXT SPRINT (TONIGHT/TOMORROW) *(updated May 17, 2026 mid-AM)*

In strict priority order:

1. **FCBase18_V001 freeze** — locks the homepage cinema/title/MOAT/declutter series (Block 14.8 → 14.10). Run `fc-freeze.sh` once Block 14.10 verifies clean on dev.
2. **FC16.S12 — Real amateur photos** for the 15-player cinematic roster. Web research per player (Wikimedia Commons URLs for young/college photos: Curry-at-Davidson, Brady-at-Michigan, Clark-at-Iowa, Mahomes-at-Texas-Tech, Jokić-as-teen, Messi-as-youth, Williams-junior, Judge-Fresno-State, plus the 5 currently on initials fallback). Image-resilience JS (14.9.1) auto-falls-back; swap is low-risk.
3. **FC16.S14 — Mobile responsiveness audit + polish.** Sridhar reported the cinema box looks "quite off" on phone (May 17, 2026). Goal: site looks awesome on any phone. Focus — cinema stage scaling, divergence panel layout, font scaling, hero MOAT row, touch targets. Test iOS Safari + Chrome Android. Must-do for production polish.
4. **Block 14.8.X — Hudl.com exhaustive site review** (queued ROADMAP item). Structured pass studying their messaging/fonts/animation timing/layout density; output a short writeup + 3-5 lift items.
5. **FC16.S6 — Video IQ polish (Block 9 + 9.1)** — was already queued pre-cinema work. Worker exists; needs frontend polish + deploy verification.
6. **Block 10 — Crawler architecture greenlight** — YouTube Data API v3 → filter views <50K + recent 90d → Claude Haiku classify → composite >7.5 → KV "discoveries:pending:{id}" → Slack webhook → manual approve → publish to /hidden-gems. Cost <$20/mo. Pre-spec'd; needs Sridhar greenlight to start building.

After that: Phase 5B (the amateur discovery engine) is the highest-leverage IP build. Block 11 (Voices live data) and Block 13 (NBA Draft June 23 launch moment) follow.

---

## INTEGRATION DOCTRINE (unchanged from v2)

Every block follows three rules:

1. **Don't break what works.** V017 baseline is sacred. Verdict page Block 1-4 work is sacred. Worker sport configs are sacred.
2. **Same data envelope.** Worker response shape is the contract. New surfaces consume it, never re-derive.
3. **Visual continuity.** Anton headers, gold accents, Cormorant Garamond italics for "the read," JetBrains Mono for data attribution. CX DNA is the design language.

**Deploy doctrine:** dev → verify → prod. Every block. No skipping. Every block gets a frozen baseline tarball (FCBaseXX_VYYY). Every block SHA-256 signed.

---

## THE NORTH STAR

> "FieldCheck IQ is the athletic intelligence layer the entire sport never had."

Every block above either:
(a) Makes that statement more true across MORE sports, OR
(b) Makes that statement defensible against any competitor.

If it doesn't do one of those, it gets cut.

---

## THE BLOCKS WE LOST AND RECOVERED (the painful 4:30am session)

For posterity, so we don't lose them again:
- The 16+ HTML pages built in the May 15 sprint exist in the project directory; they need to be wired into the new homepage nav
- The worker has fetchYouTubeHighlights, fetchSchoolRoster, fetchSchoolCoachingStaff — all sport-aware
- 120+ calibration cases exist across NFL, NBA, MLB, W-Basketball, W-Volleyball
- The data source tiering exists as a plan, not as code (Tier 1 partially started with fc-patch-prepdig-on3.py)
- The Video IQ Phase 5 page + worker scaffolding exists but unverified at scale

**The lesson:** Future sprints freeze the baseline before reorganizing the UI. The verdict page rebuild Sept 16 went off-rails because we lost the V017 → new-build delta. FCBase17_VYYY tarball is created BEFORE any restructuring.

---

**This roadmap is the law until updated again.**


---

## PHASES 9–15 — THE SCOPE BEYOND TODAY (added May 16 per "we're in phase 2 of 15")
*Sketched in `GAME_PLAN.md`. Subject to Sridhar's refinement.*

### Phase 9 — Pricing Activation
- Pro tier $29/mo · Edge tier $99/mo · Free permanent
- Stripe wiring, subscription gates on premium surfaces
- **Trigger:** After Phase 5B crawler ships (crawler = Edge-tier paywall lever)

### Phase 10 — Club & Franchise Tier (was V2 Block 10-11)
- The 5-layer expansion: Amateur → College → Pro → Club → Franchise
- `/club/{org}` (LOVB Austin, Real Madrid academy, EYBL)
- `/franchise/{team}` (Warriors, Lakers, Knicks, Chiefs, Cowboys)
- Pro player → franchise affiliation graph on verdict page

### Phase 11 — Mobile Native App
- iOS first (Apple-lens DNA), Android second
- Camera-roll-to-verdict flow
- Push notifications: drift, hidden gem discoveries, watchlist updates

### Phase 12 — International / Soccer Expansion
- LaLiga, Premier League, Bundesliga (worker soccer config already exists)
- Euroleague + Liga ACB
- Cricket (India market, long-tail moat)

### Phase 13 — AI Agent Layer
- Auto-updating verdicts as game data drops
- Continuous drift detection (worker fires when shape moves > 0.5)
- Outcome verification automation (calibration ledger writes itself)

### Phase 14 — Public API / Developer Platform
- `/api/v1/verdict/{slug}` · `/api/v1/verdict/{slug}/drift` · webhooks
- Embed widget v2
- Edge tier includes API access (revenue lever)

### Phase 15 — Industry Partnerships
- Hudl partnership (film is gold; partner, don't compete)
- NFL/NBA combine measurables DB
- College conference partnerships
- Speaking circuit: MIT Sloan, SXSW Sports, Sportico Live

---

## CROSS-PRODUCT (ThinkDifferent Holdings synergies)

See `GAME_PLAN.md` "Cross-Product" section for the XCheck portfolio integration thesis. Shared auth + billing + brand language across ContractGhost, EdgeCheck, FieldCheck, RentCheck, SchoolCheck, JobCheck. Phase 9+ enables the unified subscription play.
