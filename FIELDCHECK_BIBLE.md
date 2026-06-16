# ███ FIELDCHECK IQ — THE COMPLETE BIBLE ███
# Full project handoff · Jun 16 2026 · self-contained, assumes zero prior memory
# NEW CHAT: paste this ENTIRE file as your first message, then say "continue." Build only from this.

═══════════════════════════════════════════════════════════════════════
# PART A · WHO, WHAT, PHILOSOPHY
═══════════════════════════════════════════════════════════════════════
**Sridhar** = solo founder of **ThinkDifferent Holdings** (renamed from "Be Different Holdings" May 13 2026), a portfolio of AI-native products. Also EVP/CTO at PROG Holdings — **PROG is OUT OF SCOPE for this channel (Tenets 29/30); never mix it in.**

**FieldCheck IQ** = an AI-native athletic intelligence platform. It grades the **99% of amateur athletes nobody covers** (HS, JUCO, D3, D2, D1, club, plus pros for benchmarking), each measured against the **GOAT of their sport** across **8 facets**. Tagline energy: "The honest read on every athlete." Built **amateur-first**.

**Jobs Doctrine** (core philosophy): Einstein-grade depth INSIDE, Apple-simple OUTSIDE. The complexity is hidden; the surface is dead simple.

**Product line context:** FieldCheck sits under an umbrella called **XCheck** ("vetting before commitment"). Other ThinkDifferent products (out of scope here but for context): **ContractGhost** (live at contractghost.com, Stripe $19/mo, bypass `ghost2026`, codebase `~/Downloads/contractghost-simple/app/page.js`, on Vercel) and **Momentum**. Cut products: PitchForge, ReplyGenius, ReceiptBrain, PolicyPilot.

**Sridhar's working style:** Extremely high-energy, fast, ships all night. Says "GO" = ship the next gated step. Wants direct pushback over false agreement. Direct, action-oriented, prefers concise prioritized triage over long docs. Non-technical on terminal mechanics — give exact commands + simple navigation. He decides when work ends ("we ain't stopping till I say it"). Son **Arnav** is a touchstone ("Trust yourself. Be yourself."). Retail/financial-services background (Macy's, Gap/Old Navy, Charlotte Russe, Backcountry, Microsoft). Based San Ramon/San Martin CA.

═══════════════════════════════════════════════════════════════════════
# PART B · MACHINE / ENVIRONMENT
═══════════════════════════════════════════════════════════════════════
- Mac `L19DJL7GKW`. User `sridhar.nallani` is **NOT a sudoer** → sudo requires `su admin.sridhar.nallani` first. Shell is **bash 3.2** (NO `declare -A` associative arrays).
- **Repo = `~/Desktop/fieldcheck-proxy/`** IS the git repo. Remote `git@github.com:giving29/FieldCheck.git`, branch `main`.
- **Publish dir = repo ROOT** (per `.netlify/netlify.toml`), NOT `frontend/`.
- `worker.js` ≈ 2.9M chars (huge — always grep/sed, never cat whole). `freezes/` ≈ 13GB. `backups/`.
- Cloudflare account `bb462e745c15012ac7119a3f0c9fb784`.
- Files to know: `index.html` (THE homepage, served via `/* /index.html 200` catch-all — NEVER break it), `_redirects` (root — routes), `frontend/_redirects` (a SECOND redirects file — caused a stale-/canonical bug once; read BOTH before redirect work).

═══════════════════════════════════════════════════════════════════════
# PART C · TWO ENVIRONMENTS (Tenet 65 — NEVER break the wall)
═══════════════════════════════════════════════════════════════════════
**WORKER (Cloudflare):**
- PROD = `fieldcheck-proxy` → https://fieldcheck-proxy.sridhar-nallani.workers.dev — deploy: bare `npx wrangler deploy` — **ONLY on explicit say-so**
- DEV  = `fieldcheck-proxy-dev` → https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev — deploy: `npx wrangler deploy --env dev` — **all work here first**
- Shared KV `FIELDCHECK_KV` (id 02b386ac…) + D1 `FIELDCHECK_DB` (id 5e8ff85e-edb0-4866-a9a6-5842be84b04f).
- R2: PROD bucket `fieldcheck-clips-prod`, DEV bucket `fieldcheck-clips-dev`, binding `CLIP_BUCKET` (prod binding under top-level `[[r2_buckets]]`, dev under `[env.dev]`).

**SITE (Netlify, site id `03408b50-33ef-4e80-b08f-a648c42eb2b4`):**
- PROD = https://fieldcheck-app.netlify.app — deploy: `netlify deploy --prod --dir . --site 03408b50-33ef-4e80-b08f-a648c42eb2b4` — **ONLY on explicit say-so**
- DEV  = https://fieldcheck-dev--fieldcheck-app.netlify.app — deploy: `netlify deploy --dir . --alias fieldcheck-dev --site 03408b50-33ef-4e80-b08f-a648c42eb2b4` — **all work here first**
- **MUST park the 13GB before any netlify deploy:** `mv freezes /tmp/fz_$$; mv backups /tmp/bk_$$; netlify deploy ...; mv /tmp/fz_$$ freezes; mv /tmp/bk_$$ backups`
- Netlify reads `/_redirects` at publish ROOT.
- **⚠️ DEV ALIAS CACHES HARD** — served-page curl checks LAG fresh content and have false-failed working features ~8× this session. **LOCAL FILE + browser hard-refresh = TRUTH. Served-alias curl = informational, NEVER a blocking gate.**

═══════════════════════════════════════════════════════════════════════
# PART D · ✅ LIVE ON PROD — the CLIP-1 breakthrough (the "Clips Moat")
═══════════════════════════════════════════════════════════════════════
The strategic breakthrough: **clips are the moat-building mechanism, not a feature.** Players volunteer graded amateur performance data (solving cold-start) in exchange for exposure, status, self-knowledge. FC Top 100 = segmented discovery engine. Shareable badges = 2nd flywheel. **The full loop was promoted to PROD Jun 15–16 (freeze-first, gated) and is running now:**

- **Per-user profiles** — device identity `fc_player_id` in localStorage (`fcPlayerId()` helper), name captured on first clip (`fcPlayerName()`/`fcSetName()`), each device = its own player. Worker stores `player-name:{pid}` in KV.
- **Clip capture** → real video in R2. `POST /clips/upload?playerId=&clipId=` (80MB cap, key `clips/{pid}/{cid}.{ext}`); `GET /clips/video/{key}`.
- **8-facet READ** at intake: `POST /clips/add` runs `_fcRead()` (`L4-v1-context`) → maps context (game/drill/gym/park) + text-cue regex → 8 facets → `clip.ai_read{facet_signals,dominant,behavioral_cues,quality}`.
- **The number moves**: `/clips/recompute?playerId=` aggregates clip ai_reads → `weekly_snapshot{composite,facets,deltas,composite_delta}` at KV `snapshot:{pid}:latest` + `:{wk}`. Floor 4.0 → ~8.5. `/clips/list?playerId=` returns clips + snapshot. Profile page `renderSnapshot()` fills `#fcNum`/`#fcDelta`/`#fcLegend`.
- **The Friday number**: weekly cron `0 13 * * 5` in worker `scheduled()`; `players:index` array in KV maintained on `/clips/add`; `_fcRecomputeAll(env)`; manual trigger `/clips/recompute-all`.
- **Segmented Top 100**: `/top100?sport=&age=&pos=&region=` → 100-deep board. Seeded-PRNG (mulberry32, seed = `sport|age|pos|region`) → **distinct varied believable people per segment, stable per segment**, position-aware top-3, real public players blended in by score. Name pools: 50 first / 30 real surnames. Page `loadBoard()` fills board + podium top-3 + badge (all sport-consistent).
- **Shareable badges** (2nd flywheel): tap clip/podium → share card (`#shareModal`, `openShare()`, `doShare()`) → `navigator.share()` + clipboard fallback. "FC Top 100 · #N in {age} {sport}" status card.
- **Pages** (all on prod worker now): `/clips` (your profile), `/add-clip` (record/upload — device-detects desktop→"Upload a video", honest paste-a-link field, robust mobile upload reading bytes immediately via FileReader.readAsArrayBuffer), `/top100`.

**worker.js internals:** dispatch `async fetch(request,env,ctx)`; `function json(obj,status=200)` (~line 63); CLIP-1 block bounded by `// ── CLIP-1 BACKEND (Jun15) ──` … `// ── end CLIP-1 BACKEND ──`; `async scheduled(event,env,ctx)` (~line 33901) dispatches by `if(event.cron==='...')`.

**🔑 PROD ROLLBACK (intact — Sridhar's #1 safety requirement):**
- Worker: `npx wrangler rollback 48bc42b9-7a83-40ce-ae6c-3203996b1d1c` → reverts prod worker to pre-promotion (was FCBase112)
- Disk tarball: `freezes/FCBase112_PROD_LIVE_20260614_2217.tar.gz` (89.9MB, contains worker.js)
- Card: `ROLLBACK_CARD_20260615_2322.txt` (repo root) — all commands
- Files: `git reset --hard`
- ⚠️ The "y-storm" (wrangler interactive prompt auto-fed "y") interrupted the promote's final verify — so the Cooper Flagg engine before/after was NEVER captured. Engine athlete-grading is "fix-on-issue" per Sridhar (not blocking). For future prod worker deploys: ADD NON-INTERACTIVE FLAGS to wrangler.

═══════════════════════════════════════════════════════════════════════
# PART E · ✅ DONE ON DEV (committed; NOT yet promoted to prod)
═══════════════════════════════════════════════════════════════════════
**3 VC DECKS** — source in `frontend/`, BUT publish from ROOT, so each must be `cp frontend/X.html X.html` to actually serve (they dead-linked to homepage before, because route files only existed in frontend):
- `deck-master.html` → `/deck-master` (also `deck.html` + `fieldcheck-deck.html` → `/deck`) = FULL neutral, everything
- `deck-kevin.html` → `/deck-kevin` = Kevin flavor
- `deck-arjun.html` → `/deck-arjun` = Arjun flavor
- `fc-lovb-deck.html` → `/fc-lovb-deck` = LOVB-specific deck (exists, not yet updated with clips moat)
- Deck mechanism: `.tab-btn[data-tab="X"]` click → removes `.active` from all `.tab-btn`+`.panel`, adds to `panel-X`. Panels: problem/product/moat/proof/audience/traction/team/ask. Tab nav order: 01 Problem · 02 Product · 03 Moat · 04 Proof · 05 Who It's For(audience) · 06 Traction · 07 Team · 08 Ask.

**Added to all 3 decks (commit d3fb081):**
- `<!-- CLIPS-MOAT-BLOCK -->` in MOAT panel (after accountability-clock callout): two halves (God-Level Engine = HOW we grade vs GOAT · Clips Moat = WHAT we grade + growth loop) · two flywheels (FLYWHEEL 01 data: clips feed engine · FLYWHEEL 02 status: badges pull players in) · THE WEDGE weekly cadence · "invert who supplies the data" / cold-start.
- "THE MOAT IS ALREADY IN MOTION · LIVE ON PROD" wave in TRACTION panel (replaced old "June 11 wave"): full clips loop · Friday number · segmented Top 100 · shareable badges · per-player profiles · real video storage.

**Deck flavors:**
- **Master** = full neutral (has everything).
- **Kevin** (commit d2ff07f): The Briefing deck "Prepared for Kevin Wong." LANDS ON "The Problem" panel — fixed: a `window.addEventListener("load")` auto-clicked `data-tab="audience"` (panel 05 volleyball wedge); changed to click `data-tab="problem"`. Top strip text changed "start at 05" → "updated this past Friday." Added compact cyan `<!-- KEVIN-UPDATE-BANNER -->` at top of panel-problem (after `<div class="panel-eyebrow">01 · THE PROBLEM</div>`): "★ Update from last Friday — A new lens on the amateur — and it's already live…" with "See the full picture in The Moat →" button → `document.querySelector('.tab-btn[data-tab="moat"]').click()`. Detail stays in The Moat (NO duplication, per Sridhar's design).
- **Arjun** (commit d3fb081): amateur-nuance repositioning. Moat headline → "★ THE AMATEUR DATA NOBODY HAS · AND NOBODY ELSE CAN GET" / "The 99% nobody grades finally get seen — and hand us the data." Body leads with the amateur gap (HS sophomore, D3 starter, JUCO transfer, the kid in a sport ESPN never covers).

**CANONICAL** = `FC_CANONICAL_STATE_V1.html` (root, publishes; route `/canonical`; ~610KB; the SOURCE OF TRUTH). Tabs use `data-pane="X"`, 21 panes: 01 TL;DR · 02 Market&Thesis · 03 Roadmap V4 · 04 Player Thesis v1.7 · 05 8-Facet Polygon · 06 Backend→UI · 07 FC17 Sprints · 08 Verdict Page · 09 Methodology · 10 Hidden Gems v2 · 11 Learning Loop · 12 Pending Decisions · 13 Tenets · 14 Input Backlog · 15 ALL FEATURES · 16 ALL PLAYERS · 17 Data Strategy · 18 Validation Tests · 19 MOAT·Tenet40 · 20 V5 Algorithm · **21 Strategy & Arch (`pane-strategyarch`)** = holds clips-moat strategy + locked decisions + a decisions timeline.
- Pane 21 enriched with `<!-- CANONICAL-LIVE-PROD -->` "★ NOW LIVE ON PROD · Jun 16" block (after the Clips Moat heading) + a Jun 16 timeline row.
- ⚠️ **VERIFY THIS COMMITTED** — it was the last queued build before handoff. Check: `git log --oneline | head && grep -c CANONICAL-LIVE-PROD FC_CANONICAL_STATE_V1.html` → want a commit + count ≥1. If missing, commit it.
- 🔒 RITUAL: never reconstruct the canonical from memory; read it from the repo. Don't re-derive settled numbers — grep DECISIONS.md first.

═══════════════════════════════════════════════════════════════════════
# PART F · THE ENGINE / ALGORITHM (deep internals)
═══════════════════════════════════════════════════════════════════════
**God-Level Algorithm** (FCBase114–121 frontier): 8-facet synthesis engine grading every athlete vs the GOAT of their sport. Proven on Women's Volleyball in dev. Stage C = apex curated athletes break above the 7.4 cap when facet-avg ≥ 8.0 (college < elite-pro < Olympians).

**V5 hybrid algorithm (Tenet 46):** pure prompt = variance-bound; hybrid = prompt scores uncapped raw + **6 deterministic post-synthesis code rules**. Every correction audited in a `v5_corrections[]` trail. Hybrid wins for bright-line behavior (named-entity anchor lists amplify variance via peer-association bias; reasoning instructions beat anchor lookups).

**Reader scale ladder (settled Jun 13):** 10 = once-a-generation (Jordan) · 7+ = HOF trajectory · 5–6 = real track · 4 = good AND ~best HS in country · below 4 = building base. (Old V4 caps HS 5.4 / D1 7.4 were PRE-Kevin-engine caps, NOT the reader ladder.) **Tenet 49: no grade curation, no artificial caps — the engine number IS truth.** Madisen Skinner = 7.3–7.4 engine-derived (not a curated pin).

**8 facets** + 16 analytical voices + 4 perspectives + Bayesian consensus. Tier bands published: ICON · ELITE+ · ELITE · STAR · PROSPECT · SCOUT.

**110-athlete calibration battery:** `roster_100.json` = 110 athletes / 11 buckets (60 HS · 17 D1 · 13 D2 · 10 D3 · 3 JUCO · 7 pro regression+collision). Runner `v022_32_q_battery_v2.py` = curl-based (NEVER python urllib on macOS — SSL fails silently; always subprocess+curl). Battery = primary calibration proof; run FULL before any deploy (Tenet 51).

**Engine disciplines (proof points in decks):** HS evidence-ceiling, cross-level cap (Dent-Smith D2-vs-D1, Alozie HS-to-D1), identity-collision protection (Kimmons/Duncan false-match), one-algorithm-every-level. Cooper Flagg regression once cost 5 sprints (garbage `current_school` string tripping HS-school regex → 5.4 cap) — fixed.

**Six permanent constraints / "free tier forever, no payola"** — the verdict on a kid is never paywalled (structural, not a marketing tier).

═══════════════════════════════════════════════════════════════════════
# PART G · ARCHITECTURE & RELEASE CONVENTION
═══════════════════════════════════════════════════════════════════════
- **Release numbering:** `FCBase{N}_V{nnn}` = frozen rollback target. `FC{N}.S{n}` = incremental sprint. Golden freezes named e.g. `FCBase89_GOLDEN_OWN_NUMBER_COMPLETE` (SHA 2acefec7…), triple-stored. Major recent baselines on disk: FCBase112_PROD_LIVE (the prod anchor), FCBase110_GOLDEN_PHOTO_IDENTITY, FCBase106_GOLDEN, FCBase95_GOLDEN.
- **Stack:** Cloudflare Worker backend · Netlify edge frontend · Bayesian consensus engine · 16-voice LLM pipeline · KV + D1 + R2 · audit trail every verdict.
- **15-phase roadmap (Jun 5 rethink):** Phases 0–4.9 complete. Ph5 = Amateur Stickiness (verdict-identity card, shareable polygon, peer-compare, schedule, push) — **the clips work is essentially Ph5, now LIVE**. Ph6 = Coach/Parent + Hudl + 16-voices. Ph13 = Video Intelligence (deferred). Ph14 Pricing (paused). Ph15 API+Partners.
- **Five-layer model:** Club (amateur orgs) · Franchise (Warriors/Lakers/Knicks) · expands to pro. Nav redesign (Block 14, pre-decided): top nav = VERDICT · PROGRAMS · DRAFT · DISCOVER + How-it-works + Search.

═══════════════════════════════════════════════════════════════════════
# PART H · DOCTRINE / TENETS (how to work — non-negotiable)
═══════════════════════════════════════════════════════════════════════
1. **ONE self-contained bash script per step.** Downloads baked in. Deliver via `present_files` → `/mnt/user-data/outputs/`. Sridhar runs from `~/Downloads/` then pastes output. Build script bodies via python (avoid bash-isms). No `#`/`&&` chains that auto-execute across a paste.
2. **FREEZE first** (Deploy DNA, Tenets 12/50/52): backup→cp→`node --check`→dev→PAUSE→prod→freeze→`git push`. tar to `freezes/` + `.bak`. Idempotent grafts (skip if marker present). Auto-rollback on fail.
3. **GATES: parse JSON, or SINGLE exact-string greps ONLY. NEVER multi-pattern/alternation greps, NEVER grep pretty-printed JSON, NEVER trust the cached dev alias as a blocker.** This false-failed WORKING features ~8× this session (R2 video, deck checks). LOCAL FILE = truth; lean on Sridhar's eyes for the read.
4. **READ the real file + the actually-served route BEFORE editing** (Tenets 58/63). Find the file the platform truly serves (e.g. index.html via catch-all; decks via root not frontend).
5. **Lead every round with the ROADMAP.** Dev-first ALWAYS. Prod ONLY on explicit say-so.
6. **macOS gotchas:** never base64 with positional filename; never python urllib (SSL fails silent → curl/subprocess); success grep `-ge 1`; ship code as separate plain files, never heredoc-embed base64; browser may add "(N)" suffix → `ls -t ~/Downloads/… | head -1`.
7. **Tenet 61 (BINDING):** `git push` on EVERY deploy.
8. **Tenet 65:** two-environment doctrine (dev worker+site / prod worker+site) — never leave dev broken, never deploy to prod without say-so.
9. **Tenet 48:** memory hygiene before context compaction. **Tenet 51:** pre-flight + regression discipline (110-battery full before deploy). **Tenet 53:** multi-source first for data lookups (photo/stats/bio cascade 5–10 sources). **Tenets 29/30:** PROG + Kanverse scope-excluded.
10. **HTML-first output tenet:** roadmap/strategy updates go into existing HTML (fieldcheck-roadmap.html, the canonical) — no new MD docs for content that belongs in HTML.
11. Never touch the proven Home Page. wrangler needs non-interactive flags (the y-storm). Sridhar alone decides when work ends.

═══════════════════════════════════════════════════════════════════════
# PART I · ROADMAP / OPEN WORK
═══════════════════════════════════════════════════════════════════════
✅ LIVE ON PROD: full CLIP-1 breakthrough (profiles · R2 video · 8-facet READ · number moves · Friday cron · segmented Top 100 · shareable badges)
✅ DEV (committed, awaiting prod promo): 3 decks (Master/Kevin/Arjun) + canonical Pane 21 live-on-prod block
▶ OPEN / NEXT:
  • **LOVB / Kevin Wong / "MLB differentiator" thesis** — sharpen `fc-lovb-deck.html` + Kevin's volleyball-wedge framing. ⚠️⚠️ On **Friday last week**, after a Kevin Wong meeting, Sridhar gave **8 points (from the meeting) + 5 of his own = 13 points** that frame this. **That session is NOT retrievable via conversation_search** (likely inside a Claude Project, or unindexed). **FIRST ACTION: ask Sridhar to PASTE the 13 points, OR open the new chat INSIDE the Project where Friday's session lives so search reaches it, OR `grep -rln "Kevin\|LOVB\|MLB\|differentiator" *.html *.md frontend/`. DO NOT reconstruct from memory.** Then WRITE the 13 into the canonical so never lost again. (LOVB = League One Volleyball, launched Jan 2025, 6 teams = pro W-VB "dream rung"; a VB athlete's path ends at LOVB not a draft board; MLB-draft outcomes already in data as comps. Likely thesis to CONFIRM not assume: volleyball→LOVB has no scouting/draft infra & no amateur-data pipeline the way MLB has Baseball America + Perfect Game + the draft — FC can be that entire evaluation layer, AI-native, from day one.)
  • Promote decks + canonical → PROD (gated) when Sridhar approves
  • Engine athlete-grading spot-check on prod (fix-on-issue)
  • MediaRecorder real desktop recording · real platform import (YouTube/IG/TikTok) · cross-device auth
  • Static Top 100 stat header (1.2M graded / +38K this week / 2,400 boards) → make dynamic/believable
PARKED: guardian flow (minor-public approval — existential trust feature) · apex-calibration (Olympians past 7.4) · WVB Tenet-57 corpus sweep · HP redesign · the /canonical stale-file frontend/_redirects override (fix calmly)

═══════════════════════════════════════════════════════════════════════
# PART J · RECENT COMMITS (verify: `git log --oneline | head -12`)
═══════════════════════════════════════════════════════════════════════
83e8ca5 Top 100 podium+badge sync from real board
bf75566 Top 100 PRNG varied generator (distinct people per segment)
64f29b8 Per-user profiles (device identity + name on first clip)
b199eb4 PROMOTE TO PROD complete (worker+site, prod R2 bucket)
bcd2b8d Clip detail + shareable badge (2nd flywheel)
d3fb081 3 decks: Clips Moat + LIVE-on-prod wave
d2ff07f Kevin deck: land on Problem + update banner → Moat
(verify) Canonical Pane 21: NOW LIVE ON PROD block

═══════════════════════════════════════════════════════════════════════
# PART K · FIRST MOVES IN THE NEW CHAT
═══════════════════════════════════════════════════════════════════════
1. Confirm state: `cd ~/Desktop/fieldcheck-proxy && git log --oneline | head -12 && grep -c CANONICAL-LIVE-PROD FC_CANONICAL_STATE_V1.html`
2. If canonical block not committed → commit it.
3. Then ask Sridhar for the LOVB/Kevin 13 points (paste / project / grep) — DO NOT reconstruct.
4. Lead with the roadmap. Ship gated, freeze-first, dev-first, one script at a time. GO when he says GO.
