## ⭐ NORTH STAR — THE JOBS DOCTRINE *(May 16, 2026 · canonical product philosophy)*

> *"A baby can operate an iPhone."* — That's the bar. Jobs built products his kids could use without instructions. We do the same.

### The Two-Layer Experience

**INSIDE: Einstein-level depth.** The verdict moat — polygon model, 16 voices, pedigree, HOF analog, drift detection, coach culture, hidden gems. We NEVER simplify the substance. The detail under the hood is our differentiator. The rigor is the moat.

**OUTSIDE: Apple-simple UX.** A child could use it. Zero friction to the value. Implementation details invisible. Hide complexity internally, surface clarity to the user.

### The 4 GOLD principles (every UX decision tests against these)

1. **One mental model.** Search just works. The user never thinks "wait, what sport / category / mode is this?" They type intent; the system resolves it.
2. **No dead ends.** Every path resolves — to a result, a disambiguation, or a graceful "we don\'t have this yet." Apple never shows the user a failure they can\'t escape.
3. **Implementation details invisible until contextually needed.** Sport buckets, data schemas, internal IDs, API quirks — all hidden. Surface only what the user needs to act.
4. **Self-healing state.** System fixes user typos, sport mismatches, malformed URLs, broken links — never punishes them. The system is forgiving by default.

### Test before shipping any UX

Before any feature ships, ask: *Could a 10-year-old use this without being taught?* If not — strip a layer. Make it simpler. The depth stays in the OUTPUT. The PATH to that output is effortless.

This doctrine applies to **every ThinkDifferent product** — FieldCheck, ContractGhost, EdgeCheck, all of XCheck portfolio.

---

# FieldCheck IQ — RELEASE PLAYBOOK
**Status:** CANONICAL · the operating doctrine
**Maintained by:** Claude (auto-updated after every release)
**Read by Claude:** BEFORE every patch, BEFORE every deploy, BEFORE every freeze
**Companion:** `ROADMAP_V3.md` (what we're building) · `GAME_PLAN.md` (where we're going)

> The Apple discipline: never lose what we built. Freeze before risk. Test in dev. Move methodically. The moat compounds when we don't break it.

---

## OPERATING TENETS (the "never lose" doctrine)

These are non-negotiable. They are why we are the GOAT with a MOAT.

### 1. **Canonical doc FIRST, then execute**
Any new idea — a feature, a moat extension, a refactor — gets a line in `ROADMAP_V3.md` BEFORE a single character of code is written. Strategy and tactics are always in lockstep. If they diverge, we stop, align, then resume.

### 2. **Freeze before risk**
Before any risky change (worker refactor, big patch, new feature touching multiple files), run `fc-freeze.sh` to create a dated tarball checkpoint. We have rolled back from these before. They are insurance.
- Current confirmed-good baseline: **FCBase17_V001** (May 17, 2026) — sub-tabs + label fixes + polygon sizing
- Tier 2 rollback: **FCBase16_V001** (May 15, 2026) — pre-subtab
- Tier 3 (deeper): FCBase14_V001
- Retired: `fcdeploy.sh` (replaced by `deploy-dev.sh` + `deploy-prod.sh`)

### 3. **ALWAYS dev → verify → prod. Never skip.**
- Step 1: `deploy-dev.sh` (no Downloads needed)
- Step 2: Manual verification in dev with the test cases listed for that sprint
- Step 3: `deploy-prod.sh` (has YES gate — type YES to confirm)
- Skipping the dev step has bitten us before. NEVER again.

### 4. **JS-validate after every patch**
After every code change, run `node --check` on the extracted script content. JS parse errors silently break the page in browsers and we don't see them until users do. Validate locally first.

### 5. **Patch guards: check before applying**
Every patch script starts with a guard: does this change already exist? If yes, abort. Prevents double-patching, accidental override, and silent data corruption.

### 6. **Audit before assuming**
File state changes between sessions (Sridhar might have edited, prior session might have shipped). Before patching, `grep` + `wc -c` + spot-read the relevant section. Don't trust prior-turn context blindly — verify.

### 7. **Surgical patches, not rewrites**
Targeted `str_replace` of known unique strings. Never regenerate whole files unless explicitly creating from scratch. The verdict file is 327KB of layered moat work — every rewrite risks losing pieces.

### 8. **Bonus blocks tagged, never consume canonical slots**
When new moat ideas surface mid-build, they ship as "Phase X.5-Bonus" tagged features. They do NOT take canonical block numbers. This keeps the roadmap honest.

### 9. **Memory is forever; chat context is temporary**
Critical decisions, baselines, doctrine, architecture sketches → memory entries (persists across chats). Working context, in-flight patches, conversational state → chat (ephemeral). Don't confuse them.

### 10. **Sridhar leads strategy; Claude counsels execution**
Sridhar makes brand, scope, pricing, and moat decisions. Claude proactively counsels on what's required before each release. Claude reminds Sridhar of freezes, test cases, doc updates, memory entries — without being asked. He won't always remember to ask.

### 11. **Downloads hygiene — clean session files, keep baselines** *(added May 16 mid-FC16.S1, refined post-deploy)*
**BEFORE downloading a fresh sprint file:** `rm ~/Downloads/{filename}` if any old version exists. Prevents browser from auto-renaming the new download (e.g. `fieldcheck-verdict (1).html`) or you accidentally cp'ing the stale one. **AFTER** the sprint's file is `cp`'d into `~/Desktop/fieldcheck-proxy/`, DELETE the source from `~/Downloads/` again. Prevents wrong-version drift on future deploys. EXCEPTION: baseline tarballs `FCBase*_*.tar.gz` STAY in Downloads — rollback insurance, never deleted. Pattern:
```bash
cp ~/Downloads/fieldcheck-X.html ./fieldcheck-X.html
rm ~/Downloads/fieldcheck-X.html  # clean immediately after cp
# baselines untouched
```

### 12. **Pre-deploy file size + content verification** *(added May 16 after FC16.S1 botched deploy)*
Before every `deploy-dev.sh`, verify the file in the project folder matches the expected sprint size AND grep for a known sprint marker. The `cp` can silently succeed with the wrong source file (e.g., an older fieldcheck-verdict.html lingering in Downloads from a prior session). Pattern:
```bash
# Expected size for the sprint must be known
ls -la ~/Desktop/fieldcheck-proxy/fieldcheck-X.html  # must match expected
grep -c "{known-sprint-marker}" ~/Desktop/fieldcheck-proxy/fieldcheck-X.html  # must be > 0
```
For FC16.S1: verdict = 328,313 bytes · `grep -c Banchero` = 2.

### 14. **Every sprint ships with a numbered test case table** *(added May 16 after FC14.6.1 deploy hit "what am I testing?" gap)*
**Rule:** No deploy goes live without a test case table from Claude. Sridhar should never have to guess what to verify.

**Format (mandatory):**

| # | Action | Expected | Pass criteria |
|---|---|---|---|
| 1 | What to do | What should happen visibly | Concrete check Sridhar can read |

**Rules:**
- 3-6 test cases per sprint (not more — these are smoke tests, not regression suites)
- Each must be **executable in <30 seconds** (no deep menu navigation)
- Each must have a **concrete pass criterion** (URL contains X, text says Y, count = N)
- Include at least one **happy path** (intended behavior) and one **adversarial** (typo, edge case, malformed input)
- Include a **deployment-state check** as test 1 (URL is dev, not prod; cache is clear)
- After ship, Sridhar runs through table, reports pass/fail per row
- Failed row = sprint not done. No promote until all pass.

Add to RELEASE NUMBERING SYSTEM: every FC{N}.S{n} entry has a test case table baked into it.



### 15. **Verify CSS selectors and function names against the ACTUAL render code** *(added May 17 after FC16.S1–S5 cycle burned 4 sprints on selector ghosts)*

Before writing `.foo { ... }` — grep the render code to confirm `class="foo"` actually exists in the output HTML.
Before patching `function bar()` — grep where it's called to confirm it's the function actually being invoked by the path you care about.

**The bug that cost us 4 sprints (May 16–17, 2026):**
- Block 14.7 series targeted `.tl-stage svg` and `.tl-stage .stage-poly` repeatedly. **Neither class ever existed in the rendered HTML.** Real class was `.timeline-card` + `svg.timeline-poly`. Every "shrink the timeline" patch was a CSS no-op.
- Drift Detection polygons — patched `buildMiniRadar` to add labels. Drift actually uses `biggerMiniRadar` (a nested function inside `buildDriftDetection`). Wrong function, twice.

**The fix in workflow terms — before any CSS or function change, verify the target exists:**

```bash
# CSS selector check
grep -E 'class="timeline-card"|class="tl-stage"' verdict.html | head -3

# Function call site check
grep -nE 'biggerMiniRadar\(|buildMiniRadar\(' verdict.html | head -5
```

If the grep returns nothing for the selector you're about to use → STOP. You're targeting a ghost.

**Apply this gate** in the pre-flight checklist (right after the "JS validated?" gate): **selector/function name verified against rendered code?**

---

**Corollary (added May 17, 2026 after the FC16.S8 zombie-code disaster):**

When a sprint **renames IDs or class names** (e.g., Block 14.8 renamed `ccDots`/`ccTimer`/`ccPlay` → `cinDots`/`cinTimer`/`cinPause`), grep for **all uses of the OLD names** before declaring the refactor done:

```bash
# After renaming, hunt for orphans:
grep -nE "ccDots|ccTimer|ccPlay|oldFunctionName" /path/to/file.html | head -10
```

Any match = orphaned reference that will throw at runtime. The FC16.S8 disaster: the rename was clean in the HTML structure, but ~20 lines of zombie JS from the previous version still called `document.getElementById('ccDots').innerHTML = ...`. Runtime threw, ALL JS halted (including the new working code lower in the file). Page looked broken for 12 hours.

**Pre-flight gate for renames specifically:** *grep for old name → must return 0 matches before deploy.*

---

### 16. **Canonical docs live on the dev site as tabs · synced after every baseline freeze** *(added May 17, 2026)*

The three canonical docs — `RELEASE_PLAYBOOK.md`, `ROADMAP_V3.md`, `GAME_PLAN.md` — are rendered as 3 tabs at:
`https://fieldcheck-dev--fieldcheck-app.netlify.app/roadmap` (password: `thinkdifferent2026`)

**The contract:**
- After every baseline freeze (FCBase{N}_V001 tarball created), Claude updates ALL THREE markdown docs AND the rendered hub HTML in the same patch cycle.
- Claude calls it out in chat with a short summary of what changed in each doc — so Sridhar knows when to review the live URL.
- Sridhar may visit the URL between freezes; the docs should always reflect the latest frozen state, never mid-sprint speculation.
- The hub URL itself (the `fieldcheck-roadmap.html` file) is part of the freeze tarball — rolling back to V16 also rolls back the docs view to V16's state. Strategy + execution version-locked together.

**Trigger pattern for Claude:**
```
[freeze sprint runs] → 
[Claude updates the 3 .md files with the sprint's deltas] → 
[Claude rebuilds fieldcheck-roadmap.html to embed the updated .md content] → 
[Claude presents all 4 files + a "🧊 FREEZE LOG — docs synced" callout in chat]
```

The chat callout template (post-freeze):
> 🧊 **FCBase{N}_V001 frozen + docs synced.**
> • Playbook: [bullet list of additions/changes]
> • Roadmap: [bullet list]
> • Game Plan: [bullet list]
> Live at `/roadmap` for review when you have a beat.

This tenet exists because the docs become the **between-session contract**. Memory carries the gist; the docs carry the receipts. They drift apart if not refreshed at freeze time.

---

### 17. **Prototype before integrate — for any UX change with motion, layout, or visual flow** *(added May 17, 2026 after the FC16.S8 → 14.8.3 cinematic-box cycle)*

Before patching a UX change directly into the production page, build a **standalone prototype HTML** that Sridhar can preview in isolation. Iterate to alignment in the prototype. Only THEN integrate into the real page.

**Why this exists:**

The Block 14.8 cinematic-story-box upgrade went through five integration rounds (14.8 → 14.8.1 → 14.8.2 → 14.8.3) because each iteration only revealed visual misalignment AFTER deploying to the live homepage. A standalone prototype would have surfaced the same feedback in one round, not five.

**When this tenet applies (high-leverage UX changes):**
- Any animation timing or sequence change
- Any layout restructure (positioning, dominant box sizing, grid changes)
- Any major typography sweep (size shifts, family changes, emphasis patterns)
- Any visual flow change (cross-fades, scene transitions, motion choreography)
- Any "feel" change (spacing, density, breathing room)

**When this tenet does NOT apply (still patch direct):**
- Pure content/text edits (copy changes, label rewording)
- Single CSS value tweaks (color hex, single padding px)
- Bug fixes (broken JS, null reference, syntax error)
- Documentation, markdown, internal infra

**The pattern:**
```
[Sridhar describes UX intent in chat] →
[Claude builds /mnt/user-data/outputs/fieldcheck-{feature}-prototype.html as a STANDALONE file] →
[Sridhar opens locally OR deploys to /prototype path for visual review] →
[Iterate in prototype: text, sizing, animation, layout] →
[Once aligned: Claude integrates into the real page in ONE surgical patch] →
[Deploy dev → verify live → prod]
```

**Receipt — the FC16.S8 cinematic-box cycle (May 17, 2026):**

1. **14.8 (initial integration)** — 15 players, two-layer young→GOAT morph, 86vh stage. Animation didn't move. Spent two hours debugging.
2. **14.8.1** — Removed IntersectionObserver (initial diagnosis: wrong). Animation still didn't move.
3. **14.8.2** — Found root cause: zombie cinema rotation code from previous version was throwing null-ref errors on renamed IDs (`ccDots`/`ccTimer`/`ccPlay` → `cinDots`/`cinTimer`/`cinPause`). The thrown error halted ALL JS including the new rotation IIFE. Removed zombie.
4. **14.8.3** — Sridhar feedback: market vs FC divergence display missing, fonts too small, positioning wrong. Multiple visual misses across opening/closing/category/divergence.
5. **14.9** — Title locked, MOAT row added, hero restructured, cinema compressed.

Three of the five rounds (14.8.1, 14.8.2, 14.8.3) were debugging on live pages. A standalone prototype rendered locally — where every visual element is visible at first paint — would have caught the missing divergence display, font sizing, and category positioning in ONE review cycle.

**The prototype produced (Tenet 17 artifact):**  
`/mnt/user-data/outputs/fieldcheck-cinema-prototype.html` (24,773 bytes) — built later in the cycle to demonstrate the mechanic in isolation. Sridhar reviewed it standalone in <2 minutes. The integration that followed was clean.

**Add to pre-flight checklist** (right after "selector/function verified?"):  
**prototype review done for motion/layout/major-typography changes?**

---
### 13. **Code blocks are copy-paste-safe: pure executable, no narration** *(added May 17 after zsh choked on instruction-mixed fence)*
Every shell code block Claude writes must paste cleanly into zsh. Mixed fences fail:

**zsh failure modes:**
- `# 1. Clean Downloads` → zsh runs `#` as a command
- `[Click the link]` → zsh interprets `[...]` as a glob pattern
- Smart quotes / em-dashes / arrows → syntax errors

**The pattern:**
- ❌ One mega-fence with `#` headers and bracketed instructions
- ✅ Prose BEFORE each fence ("Now verify size:"), then a fence containing ONLY executable lines

For multi-step flows: one fence per logical step, prose between. Self-check before posting: "would this paste cleanly into zsh?" If any line is narrative — pull it OUT.

---



## POST-MORTEM — FC16.S1–S5 (May 16–17, 2026)

The cycle that became this playbook's most expensive lesson.

**Scope shipped** (5 sprints, 1 freeze):
- **FC16.S1** — Eval Grid sub-tab architecture (Block 14.5) · iOS Settings model · 17 subpanels · hash deep-linking · legacy renders suppressed
- **FC16.S2** — Label truncation fix (slice 5→12 + 45 SHORT_LBL additions) · miniRadar viewBox 175 + endpoint labels · deep-link timing fix · hashchange listener · Summary smart-CTA
- **FC16.S3** — buildRadar viewBox 340→400 (fixed visual clipping of CEILING/POSITION FIT at right edge) · shape overlay viewBox expansion · overflow:visible safety net
- **FC16.S4** — Timeline polygons shrink (targeted wrong CSS class, no-op) · buildMiniRadar label addition (wrong function for drift, no visible effect)
- **FC16.S5** — Real fix: CSS targeting actual `.timeline-card` + `svg.timeline-poly` classes · biggerMiniRadar (the actual drift polygon function) gets endpoint labels
- **Freeze** → FCBase17_V001

**The hard lessons** (now codified as tenets):
1. **Tenet 12 reinforcement** — early sprints in this cycle were declared "deployed" without the curl-verified live marker check. We had ~3 ghost deploys where the local file said FC16.S2 but the live URL was still serving FC16.S1 because `cp ~/Downloads/fieldcheck-verdict.html` grabbed the old cached download from the browser. Without the live curl check, every visual test was meaningless.
2. **Tenet 13 reinforcement** — wasted a step on `grep -c "max-width:160px!important"` because zsh interprets `!important` as history expansion. Switched to single-quoted fences as the default. Every shell command in this doc now uses single quotes.
3. **Tenet 15 birth** — the dominant time sink was selector/function ghosts. `.tl-stage` was patched 3 times before someone realized it never existed in the HTML. `buildMiniRadar` was patched twice before realizing drift uses `biggerMiniRadar`. **Verify target exists before patching it.**

**The deploy chain that finally worked** (FC16.S5):
```
Build file → present_files → 
Sridhar: rm -f ~/Downloads/fieldcheck-verdict*.html → 
Sridhar: download in browser → 
Sridhar: ls -la ~/Downloads/fieldcheck-verdict.html → bytes match expected? → 
Sridhar: cp to ~/Desktop → 
Sridhar: grep marker count → matches expected? → 
Sridhar: ./deploy-dev.sh 2>&1 | tail -5 → "✓ Frontend live on DEV" visible? → 
Sridhar: curl live URL | grep marker → matches expected? →
THEN AND ONLY THEN visually test
```

This is the protocol. Every chain link verified before the next. Anything less is a guess.

---
## RELEASE NUMBERING SYSTEM

Simple, honest, three-level:

```
FCBase{N}_V{nnn}   — Frozen-good baseline. Tarball archived. Rollback target.
FC{N}.S{n}         — Sprint between baselines. Incremental, focused, deployable.
Block X.Y.Z        — The canonical work item being advanced (from ROADMAP_V3)
```

### Examples
- `FCBase16_V001` → current baseline (May 15, 2026)
- `FC16.S1` → next incremental release, ships verdict moat completion
- `FC16.S2` → ships Video IQ polish
- `FC16.S3` → ships Hidden Gems discovery scaffold
- After 3-5 stable sprints of clean work → freeze `FCBase17_V001` as the new baseline

### Sprint vs Baseline — when to promote
Promote to a new baseline (`FCBaseN+1`) when:
- 3+ sprints have shipped cleanly without rollback
- Significant new surface area is now live (a new page, a major feature)
- Sridhar gives the explicit "freeze this" call

Each sprint is a discrete unit. Each baseline is a stable platform.

---

## PRE-RELEASE RITUAL (Claude's pre-flight checklist)

**Before every patch, Claude proactively confirms:**

1. ☐ **Did we update the canonical doc?** (`ROADMAP_V3.md`) — Per Tenet 1
2. ☐ **Is the patch a guard-protected `str_replace` or `create_file`?** — Per Tenet 5
3. ☐ **Did we audit current file state before patching?** — Per Tenet 6
4. ☐ **Is this a risky change?** If YES → has Sridhar run `fc-freeze.sh` to checkpoint?
5. ☐ **JS-validated after patch?** (`node --check` on extracted script content) — Per Tenet 4

**Before every deploy, Claude proactively confirms:**

6. ☐ **Sprint number assigned?** (FC{N}.S{n})
7. ☐ **Test cases written for this sprint?** (See "Deploy Queue" template below)
8. ☐ **Deploy to dev first?** (`deploy-dev.sh`) — NEVER skip
9. ☐ **Dev verified with named test cases before prod?** — Per Tenet 3
10. ☐ **Memory updated?** (If sprint introduces new state, doctrine, or anchors)

**After every successful prod deploy, Claude proactively confirms:**

11. ☐ **ROADMAP_V3 updated to mark sprint shipped?** (Block status ✅)
12. ☐ **Have we crossed the 3-5-sprint threshold to freeze a new baseline?**
13. ☐ **Any new lessons surfaced?** → Update `RELEASE_PLAYBOOK.md` (this doc)

**Claude reads this checklist before every patch. Sridhar should not need to ask.**

---

## CURRENT DEPLOY QUEUE — ready to ship

### 🚀 Deploy 1 · `FC16.S1` — Verdict Moat Completion
**File:** `fieldcheck-verdict.html` (327KB)
**Advances:** Block 6 closeout, Block 4.6.1, Block 4.6.3 (Phase 4.5/4.6)
**What ships:**
- 3 missing volleyball historical analogs added (Madisen → Jordan Larson, Logan → Jordan Larson, Harper → Logan Tom)
- 5 analog HISTORICAL_POLYGONS data sets added (Banchero, Mahomes, Strasburg, Larson, Tom) — side-by-side polygons now render in the Historical Analog section for all 7 marquee profiles
- Critical bug fix: `getTierRate` function collision (composite-only version was silently overriding sport-aware version → Block 8 tier-rate strip was rendering as undefined on every verdict). Renamed composite-only to `getTierBand`.

**Test cases (verify in dev BEFORE prod):**
1. Open `/verdict?q=Cooper+Flagg&sport=mens-basketball` → scroll to "All-time analog" section → confirm Cooper + Paolo Banchero side-by-side mini polygons render (was text-only before)
2. Open `/verdict?q=Caleb+Williams&sport=football` → confirm Caleb + Mahomes side-by-side renders
3. Open `/verdict?q=Madisen+Skinner&sport=womens-volleyball` → confirm Madisen + Jordan Larson side-by-side renders
4. Open any verdict → scroll to main polygon area → confirm tier-rate strip below polygon now renders: "X% of [sport] players at [tier] reach [pro_label]" (was silently broken before)
5. JS console: no errors

**Deploy commands (with Tenet 12 verification baked in):**
```bash
cd ~/Desktop/fieldcheck-proxy

# Step 1: cp + verify size + verify content BEFORE deploy
cp ~/Downloads/fieldcheck-verdict.html ./fieldcheck-verdict.html
ls -la ./fieldcheck-verdict.html              # expect ~328,313 bytes
grep -c "Banchero" ./fieldcheck-verdict.html  # expect 2
# STOP if either check fails — re-download from chat

# Step 2: clean Downloads (Tenet 11)
rm ~/Downloads/fieldcheck-verdict.html

# Step 3: deploy dev
./deploy-dev.sh

# Step 4: open dev URL in INCOGNITO tab (bypass cache), verify the 5 test cases

# Step 5: only if all 5 green
./deploy-prod.sh  # type YES to confirm
```

**Post-deploy:** Claude updates ROADMAP_V3 to mark Block 6 closeout + Block 4.6.1 + 4.6.3 ✅ shipped.

---

### 🚀 Deploy 2 · `FC16.S2` — Video IQ Polish
**File:** `fieldcheck-video-iq.html` (23KB)
**Advances:** Block 9, Block 9.1 (Phase 5A)
**What ships:**
- 5 marquee demo examples with one-click pre-fill + auto-run (Cooper, Caleb, Madisen, Harper, Logan — real YouTube IDs from CURATED_VIDEOS)
- Visual 0-10 score bars on result signal cards, color-coded by tier (ICON gold / ELITE moss / mid neutral / low red)

**Test cases (verify in dev BEFORE prod):**
1. Open `/video-iq` → see the new "Try Video IQ now · one click" section with 5 demo cards
2. Click "Cooper Flagg" demo → URL + sport + name auto-fill → analyze auto-runs → result renders
3. In result: confirm signal cards now show horizontal score bars below the numeric score, colored by tier
4. Test on mobile: demo grid stacks correctly, bars render at narrow widths

**Deploy commands:**
```bash
cd ~/Desktop/fieldcheck-proxy
cp ~/Downloads/fieldcheck-video-iq.html ./fieldcheck-video-iq.html
./deploy-dev.sh
# verify the 4 test cases
./deploy-prod.sh
```

**Post-deploy:** Claude updates ROADMAP_V3 — Block 9 + 9.1 ✅ shipped to prod.

---

### 🚀 Deploy 3 · `FC16.S3` — Hidden Gems Discovery Scaffold
**File:** `fieldcheck-hidden-gems.html` (22KB)
**Advances:** Block 10 frontend (Phase 5B)
**What ships:**
- "Discovered by Video IQ" section below the existing gem grid
- 6 polygon-flagged amateurs seeded (Cari Spears, AJ Dybantsa, Cameron Boozer, Arch Manning, Anna Smrek, Bryce Underwood)
- Each card: consensus rank · FC signal score · why-we-surfaced read · discovery date
- "Try Video IQ now" CTA wired to `/video-iq`
- Honest methodology note: pre-crawler, manually curated. Surface ready for when crawler ships.

**Test cases (verify in dev BEFORE prod):**
1. Open `/hidden-gems` → existing 5 gems render at top (no regression)
2. Scroll down past methodology → confirm new "PHASE 5 · DISCOVERED BY VIDEO IQ · LIVE" section appears
3. Click any of the 6 discovery cards → links to verdict search for that player
4. Click "Try Video IQ now" footer button → lands on `/video-iq`
5. Mobile: discovery grid stacks correctly

**Deploy commands:**
```bash
cd ~/Desktop/fieldcheck-proxy
cp ~/Downloads/fieldcheck-hidden-gems.html ./fieldcheck-hidden-gems.html
./deploy-dev.sh
# verify the 5 test cases
./deploy-prod.sh
```

**Post-deploy:** Claude updates ROADMAP_V3 — Block 10 frontend ✅ shipped to prod.

---

### 🧊 Deploy 4 · `FCBase17_V001` — New Baseline Freeze
**Trigger:** After Deploys 1-3 (FC16.S1, S2, S3) verified clean in prod
**Action:** Freeze the new baseline.

```bash
cd ~/Desktop/fieldcheck-proxy
./fc-freeze.sh
# Creates: fieldcheck-baseline-FCBase17_V001-2026-05-{DD}.tar.gz
```

**Post-freeze actions (Claude executes):**
1. Update memory: new "confirmed-good baseline" entry → FCBase17_V001
2. Update `RELEASE_PLAYBOOK.md` (this doc): bump current baseline + add FCBase16 to "Prior good" list
3. Reset sprint counter: next sprint is FC17.S1

---

## BASELINE HISTORY (rollback targets)

| Baseline | Date | Tier | What it carries |
|---|---|---|---|
| **FCBase17_V001** | May 17, 2026 | **Tier 1 (current)** | Eval Grid sub-tab architecture (Block 14.5) · Polygon sizing through Block 14.7-E · Label truncation fix · Summary smart-CTA · Hash deep-linking · Legacy section suppression |
| FCBase16_V001 | May 15, 2026 | Tier 2 (deeper rollback) | All Phase 1-4 + Phase 4.5 first 4 blocks — pre-subtab |
| FCBase14_V001 | (prior) | Tier 3 (oldest kept) | All Phase 1-4 |
| _retired:_ fcdeploy.sh | — | — | older deploy mechanism, do not use |

After 3-5 clean sprints on top of FCBase17 → freeze **FCBase18_V001**. V17 becomes Tier 2, V16 becomes Tier 3. Never delete tarballs (Tenet 11).

---

## WHEN CLAUDE COUNSELS PROACTIVELY (without being asked)

Sridhar said: *"counsel me as I won't tell you everyone."*

Claude proactively says things like:

> **Before a patch:** "Heads up — this touches the worker pipeline. Want to freeze FCBase16 first via `fc-freeze.sh` before I patch?"

> **Before a deploy:** "Sprint FC16.S1 is ready. Test cases listed in the playbook. Want me to walk through them once before you `deploy-dev.sh`?"

> **After a deploy:** "FC16.S1 verified in prod. That's 1 of 3 sprints toward FCBase17 freeze. Want to ship FC16.S2 next, or pause?"

> **When state diverges:** "Memory says baseline is FCBase16, but I see FCBase17 in your shell history. Should I update memory, or did you freeze without me knowing?"

> **When risk surfaces:** "This patch modifies HISTORICAL_POLYGONS — the data Block 4 and Block 6 both depend on. Risk: cascading breakage. Recommend freeze + dev test before prod."

**This is the Apple-grade discipline. Claude does it without being asked. Sridhar focuses on strategy.**

---

## LESSONS LEARNED LOG (auto-updated as we go)

### Lesson 1 (May 16, 2026): Function name collisions kill silently
Two functions named `getTierRate` with different signatures — second overrode first, Block 8 was silently broken on every verdict for an unknown duration. **Tenet 5 (patch guards) and Tenet 6 (audit before assuming) would have caught this.** Going forward: when introducing a new function, grep for the name first.

### Lesson 2 (May 16, 2026): Side-quest blocks need explicit tagging
14 moat-extension features shipped in side-quests had no canonical numbers, drifting the roadmap from reality. **Tenet 8** added: bonus blocks tagged "Phase X.5-Bonus" with explicit non-canonical status. Doc and reality stay in lockstep.

### Lesson 3 (May 16, 2026): Confidence on settled facts is dangerous
Cooper Flagg was incorrectly listed in the 2026 NBA Draft lottery on the live page — he was drafted #1 in 2025 and is already a Maverick. **Lesson:** for any "current state" claim (rankings, prices, leadership, roster), web-search to verify even when confident. Memory of facts can be stale.

### Lesson 4 (May 16, 2026): Surgical beats rewrite
The verdict file is 327KB of layered moat work. Every full rewrite risks losing pieces. **Pattern locked:** small `str_replace` patches with guards, never regenerate from scratch unless explicitly creating new.

### Lesson 5 (May 16, 2026): Doc-first prevents drift
Phase 4.6 (analog polygon coverage) was added to the canonical doc BEFORE any code was written. Result: clean execution, no scope creep. Pattern works.

### Lesson 6 (May 16, 2026): Downloads hygiene matters
Stale files in `~/Downloads/` create wrong-version risk on future deploys. **Tenet 11** added: clean session files after cp, keep baseline tarballs. Surfaced mid-FC16.S1 deploy.

### Lesson 10 (May 16, 2026): Render orchestrators accumulate copy-paste sediment across sessions
FC16.S1 dev verification surfaced THREE stacked blocks of feature render calls in the eval grid orchestrator. Block A (canonical, anchor-mapped) was correct. Blocks B + C were copy-paste accumulation from prior sessions — likely added incrementally as new features were prototyped, never cleaned up. Symptom: page rendered correctly but with duplicate sections (Shape Overlay 3x, Coach Voices 4x). Bug class: same as Lesson 1 (`getTierRate`) and Lesson 9 (`NIL_SCENARIOS`) — silent accumulation without dedup audit. **Going forward:** when modifying render orchestrator functions, grep `h\+=build` to count call sites BEFORE and AFTER. Every render function should appear exactly once in the orchestrator. Add to pre-flight checklist as "Render audit": `grep -cE "h\+=build[A-Z]" verdict.html | sort | uniq` — every count should be 1.

### Lesson 9 (May 16, 2026): `var` redeclarations cause same-class bug as function collisions
FC16.S1 dev verification surfaced a `TypeError: Cannot read properties of undefined (reading 'length')` in `renderStressTest`. Root cause: `var NIL_SCENARIOS` declared twice in the file — once as an object (sport-keyed), once later as an array. JS `var` redeclaration overwrites silently; second declaration won. The first code path (legacy) then read `NIL_SCENARIOS['mens-basketball']` on an array → `undefined` → `.length` threw. **Same bug class as Lesson 1 (`getTierRate`).** Going forward: when introducing new `var X` declarations, grep for `var X\b` first. The legacy code is now dead but unreferenced — safe.

### Lesson 8 (May 16, 2026): zsh comments in code blocks break copy-paste
Including `# comments` inside zsh copy-paste blocks can fail when comment text contains `~`, `→`, or parens — zsh tries to interpret them as commands. **Pattern locked:** copy-paste blocks for Sridhar have commands ONLY. Annotations live in prose outside the block.

### Lesson 7 (May 16, 2026): `cp` can silently use the wrong source file
FC16.S1 first deploy attempt: the cp succeeded but the source file in Downloads was an 82KB older version from a prior session, not the 328KB FC16.S1 build. Result: deploy went green, but the verdict page rendered without the new features (because they weren't in the file). Caught by view-source search for "Banchero" returning 0/0. **Tenet 12** added: always verify file size and grep for known sprint marker BEFORE `deploy-dev.sh`. Per-sprint expected size is now part of the deploy queue spec.

_(New lessons appended as they surface.)_

---

## STATE TODAY · MAY 16, 2026 · EVENING

- **Current baseline:** FCBase16_V001
- **Next sprint to ship:** FC16.S1 (verdict moat completion)
- **Sprint queue:** S1 → S2 → S3 → freeze FCBase17
- **Operating doctrine:** locked into memory (entries 9, 10, 14, 15, 16)
- **Strategic plan:** `GAME_PLAN.md` (15-phase scope)
- **Canonical roadmap:** `ROADMAP_V3.md`
- **Brainstorm prep:** `ROUTES_AUDIT.md` (Block 14 substrate)

**Ready to deploy FC16.S1 when you give the word.** ✊
