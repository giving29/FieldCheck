# FIELDCHECK IQ — FULL HANDOFF · Jun 16 2026
> New chat: paste this entire file as your first message. It is the complete, current state. Build from it.

═══════════════════════════════════════════════════════════════
## 1 · WHO / ENVIRONMENT
═══════════════════════════════════════════════════════════════
- **Sridhar** = solo founder, ThinkDifferent Holdings. **FieldCheck IQ** = grades the 99% of amateur athletes nobody covers, each vs the **GOAT of their sport** across **8 facets**.
- Mac `L19DJL7GKW`. User `sridhar.nallani` is **NOT a sudoer** (sudo → `su admin.sridhar.nallani` first). bash 3.2 (no `declare -A`).
- **Repo = `~/Desktop/fieldcheck-proxy/`** = the git repo. Remote `git@github.com:giving29/FieldCheck.git`, branch `main`. Every deploy ends with `git push` (Tenet 61).
- **Publish dir = repo ROOT** (per `.netlify/netlify.toml`), NOT `frontend/`. `worker.js` ≈ 2.9M chars. `freezes/` ≈ 13GB, `backups/`.
- Cloudflare account `bb462e745c15012ac7119a3f0c9fb784`.

═══════════════════════════════════════════════════════════════
## 2 · TWO ENVIRONMENTS (Tenet 65 — never break)
═══════════════════════════════════════════════════════════════
**WORKER (Cloudflare):**
- PROD = `fieldcheck-proxy` → https://fieldcheck-proxy.sridhar-nallani.workers.dev — deploy: bare `npx wrangler deploy` (ONLY on explicit say-so)
- DEV  = `fieldcheck-proxy-dev` → https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev — deploy: `npx wrangler deploy --env dev`
- Shared KV `FIELDCHECK_KV` (02b386ac…) + D1 `FIELDCHECK_DB` (5e8ff85e…).
- R2: prod bucket `fieldcheck-clips-prod`, dev bucket `fieldcheck-clips-dev`, binding `CLIP_BUCKET`.

**SITE (Netlify, site id `03408b50-33ef-4e80-b08f-a648c42eb2b4`):**
- PROD = https://fieldcheck-app.netlify.app — deploy: `netlify deploy --prod --dir . --site 03408b50-...` (ONLY on explicit say-so)
- DEV  = https://fieldcheck-dev--fieldcheck-app.netlify.app — deploy: `netlify deploy --dir . --alias fieldcheck-dev --site 03408b50-...` (ALL work here first)
- **Netlify deploy MUST park the 13GB first:** `mv freezes /tmp/fz_$$; mv backups /tmp/bk_$$; netlify deploy ...; mv /tmp/fz_$$ freezes; mv /tmp/bk_$$ backups`
- **DEV ALIAS CACHES HARD** — served-page curl checks lag fresh content. **Local file + browser hard-refresh = truth. Served-alias checks = informational, never blocking.**

═══════════════════════════════════════════════════════════════
## 3 · ✅ LIVE ON PROD — the CLIP-1 breakthrough ("Clips Moat")
═══════════════════════════════════════════════════════════════
Full loop promoted to prod (freeze-first, gated) Jun 15–16. Running now:
- **Per-user profiles** — device identity `fc_player_id` (localStorage) + name on first clip; each device = its own player.
- **Clip capture** → real video in R2 (`fieldcheck-clips-prod`). Endpoints: `POST /clips/upload?playerId=&clipId=` (80MB cap), `GET /clips/video/{key}`.
- **8-facet READ** at intake (`_fcRead`, context+cue mapping) → facet signals on the clip.
- **Number moves** — `POST /clips/add` then `/clips/recompute?playerId=` aggregates clip reads → snapshot (floor 4.0 → ~8.5). `/clips/list?playerId=` returns clips+snapshot.
- **Friday number** — weekly cron `0 13 * * 5` in worker `scheduled()`; `players:index` in KV; `/clips/recompute-all` manual trigger.
- **Segmented Top 100** — `/top100?sport=&age=&pos=&region=` → 100-deep board; seeded-PRNG **varied** people per segment (stable per segment), position-aware #1, real players blend by score.
- **Shareable badges** — 2nd flywheel; `navigator.share()` + clipboard; tap clip/podium → share card.
- Pages: `/clips` (profile), `/add-clip`, `/top100`.

**worker.js internals:** dispatch `async fetch(request,env,ctx)`; `function json(obj,status=200)`; CLIP-1 bounded by `// ── CLIP-1 BACKEND (Jun15) ──` … `// ── end CLIP-1 BACKEND ──`; `async scheduled(event,env,ctx)` dispatches by `event.cron`.

**PROD ROLLBACK (intact — key safety):**
- Worker: `npx wrangler rollback 48bc42b9-7a83-40ce-ae6c-3203996b1d1c` → pre-promotion (FCBase112)
- Disk: `freezes/FCBase112_PROD_LIVE_20260614_2217.tar.gz`
- Card: `ROLLBACK_CARD_20260615_2322.txt` (repo root)
- Files: `git reset --hard`

═══════════════════════════════════════════════════════════════
## 4 · ✅ DONE ON DEV (committed; NOT yet promoted to prod)
═══════════════════════════════════════════════════════════════
**3 VC decks — live in `frontend/` (source) AND copied to ROOT to publish** (root is publish dir; decks dead-linked to home before the copy):
- `deck-master.html` → `/deck-master` (also `deck.html` + `fieldcheck-deck.html` → `/deck`) = FULL neutral, has everything
- `deck-kevin.html` → `/deck-kevin` = Kevin flavor
- `deck-arjun.html` → `/deck-arjun` = Arjun flavor
Deck mechanism: `.tab-btn[data-tab="X"]` click → activates `panel-X`. Panels: problem/product/moat/proof/audience/traction/team/ask.

**Added to all 3 (commit d3fb081):**
- `<!-- CLIPS-MOAT-BLOCK -->` in MOAT panel: two halves (God-Level Engine=HOW vs GOAT · Clips Moat=WHAT+growth) · two flywheels (data + badge-share) · weekly-cadence wedge · invert-who-supplies-the-data / cold-start.
- "THE MOAT IS ALREADY IN MOTION · LIVE ON PROD" wave in TRACTION (replaced old June 11 wave).

**Flavors:**
- Master = full neutral.
- **Kevin** (d2ff07f): lands on **The Problem** (fixed load-time auto-click to audience → now problem); top strip "updated this past Friday"; cyan `<!-- KEVIN-UPDATE-BANNER -->` at top of panel-problem ("A new lens on the amateur — and it's already live…") with "See the full picture in The Moat →" (clicks moat tab). No content duplication — detail stays in The Moat.
- **Arjun** (d3fb081): amateur-nuance — moat headline "THE AMATEUR DATA NOBODY HAS"; "The 99% nobody grades finally get seen."

**Canonical** `FC_CANONICAL_STATE_V1.html` (root, publishes; route `/canonical`; tabs `data-pane="X"`, 21 panes; **Pane 21 = `pane-strategyarch` "Strategy & Arch"** holds the clips-moat strategy + decisions timeline):
- Pane 21 enriched with `<!-- CANONICAL-LIVE-PROD -->` "★ NOW LIVE ON PROD · Jun 16" block + Jun 16 timeline row.
- ⚠️ **VERIFY THIS COMMITTED** (was the last queued build). Check: `git log --oneline | head && grep -c CANONICAL-LIVE-PROD FC_CANONICAL_STATE_V1.html` → expect a commit + count ≥1. If missing, re-commit.

═══════════════════════════════════════════════════════════════
## 5 · DOCTRINE (how to work with Sridhar — non-negotiable)
═══════════════════════════════════════════════════════════════
1. **ONE self-contained bash script per step**; downloads baked in; deliver via `present_files` → `/mnt/user-data/outputs/`; Sridhar runs from `~/Downloads/` then pastes output.
2. **FREEZE first** (tar → `freezes/` + `.bak`). `node --check worker.js` before any worker deploy. Idempotent grafts (skip if marker present). Auto-rollback on fail.
3. **GATES: parse JSON, or SINGLE exact-string greps only. NEVER multi-pattern/alternation greps; NEVER grep pretty-printed JSON; NEVER trust the cached dev alias as a blocker.** (These false-failed WORKING features ~8× — local file is truth, lean on Sridhar's eyes.)
4. **READ the real file + the actually-served route BEFORE editing** (Tenets 58/63).
5. **Lead every round with the ROADMAP.** Dev-first always; prod ONLY on explicit say-so.
6. macOS: never base64 w/ positional filename; never python urllib (SSL fails silent → use curl/subprocess); success grep `-ge 1`; browser may add "(N)" suffix to downloads → `ls -t ~/Downloads/… | head -1`.
7. **wrangler interactive prompts caused a "y-storm" during prod promote** → add non-interactive flags for any future prod worker deploy.
8. Never touch the proven Home Page. Sridhar alone decides when work ends.
9. Tone: high-energy, fast, concise. He says "GO" — ship the next gated step.

═══════════════════════════════════════════════════════════════
## 6 · ROADMAP
═══════════════════════════════════════════════════════════════
✅ LIVE ON PROD: full CLIP-1 breakthrough (profiles · R2 video · 8-facet READ · number moves · Friday cron · Top 100 · badges)
✅ DEV (committed, awaiting prod promo): 3 decks (Master/Kevin/Arjun) + canonical Pane 21 live-on-prod block
▶ OPEN / NEXT:
  - **LOVB / Kevin Wong / "MLB differentiator"** thesis — sharpen LOVB deck (`fc-lovb-deck.html`) + Kevin's volleyball-wedge framing. ⚠️ Friday's session where Sridhar gave **8 points (from Kevin mtg) + 5 of his own = 13** is NOT retrievable here (likely in a Claude Project or unindexed). **Ask Sridhar to paste the 13, OR open new chat inside that Project so search finds it, OR grep repo. DO NOT reconstruct from memory.** Then write them into the canonical so never lost again. (LOVB = League One Volleyball, launched Jan 2025, 6 teams = pro W-VB "dream rung"; MLB-draft outcomes already in data as comps.)
  - Promote decks + canonical → PROD (gated) when Sridhar approves
  - Engine athlete-grading spot-check on prod (fix-on-issue — Cooper Flagg before/after never captured, "y-storm" ate it)
  - MediaRecorder real desktop recording · real platform import · cross-device auth · static Top 100 stat header (1.2M/+38K/2,400) → dynamic
PARKED: guardian flow (minor-public approval) · apex-calibration (Olympians past 7.4) · WVB Tenet-57 corpus sweep · HP redesign

═══════════════════════════════════════════════════════════════
## 7 · RECENT COMMITS (verify: `git log --oneline | head -10`)
═══════════════════════════════════════════════════════════════
b199eb4 PROMOTE TO PROD complete (worker+site, R2 prod bucket)
bcd2b8d clip detail + shareable badge (2nd flywheel)
d3fb081 3 decks: Clips Moat + LIVE-on-prod wave
d2ff07f Kevin deck: land on Problem + update banner → Moat
(verify)  Canonical Pane 21: NOW LIVE ON PROD block
