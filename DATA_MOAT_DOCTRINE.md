# FieldCheck — The Data Moat Doctrine
*The north-star spine. Everything (engine, agents, roadmap, pitch) refers back here.*
*Supersedes the framing in BREAKTHROUGH_CLIPS_MOAT.md by absorbing it: clips become Layer 4 of a four-layer refinery. Companion to FIELDCHECK_BIBLE.md (tenets) and DECISIONS.md (log).*

---

## 0. The one line

> FieldCheck is a **refinery** that ingests the world's scattered athletic signal — public data, scraps, existing video, and player uploads — and outputs the one thing nobody else has: **calibrated, honest reads at scale.** Agents fill the refinery and spend its output; reinforcement loops make it compound. Data is the moat. Agents are how we fill it and spend it. Loops are why it gets better every day.

NCSA sells a database your kid sits in plus a salesperson who calls your anxious parent. We replace the database with a refinery and the salesperson with a team of agents — grounded in a read that can't be bought.

---

## 1. The reframe: a refinery, not a collection

We are not "collecting clips." We are running a refinery. Uploads are one feedstock; the larger feedstock is the world's existing, un-mined athletic exhaust. Three things compound, and each is a moat layer:

- **Coverage** — how many athletes we can read. Comes from ingesting *everything*.
- **Calibration** — how *right* the reads are. Comes from the loops.
- **Utility** — what the reads *do* for people. Comes from the agents.

A competitor must beat us on all three at once, and they reinforce each other. That simultaneity is the structural moat. Critically, our incumbents *structurally cannot* run two of the three: they're pay-to-play (so they can't be honest, which kills calibration credibility) and human-driven (so they can't scale agents). And none of them have graded amateur film, so any agent they build stands on nothing.

---

## 2. The four feedstock layers (acquisition funnel: widest → narrowest)

| Layer | Source | What it gives | Owned? | Cold-start role |
|---|---|---|---|---|
| **L1 — Structured public** | stats sites, box scores, schedules, recruiting boards, prep data, rosters, portals, federation results | a row for *millions* of athletes before we've seen them play | No | Seeds raw **coverage** |
| **L2 — The scraps** | local write-ups, school athletics pages, brackets, all-conference lists, interviews, social posts, public hudl links | **context + invisible-four signal** ("captain," "came back from 0–2," "played hurt") | No | Connective tissue; where agents extract facet signal from prose |
| **L3 — Existing video in the wild** | years of game film, highlight channels, tournament streams, school accounts | the **latent goldmine** — invisible-four lives only on film; unowned and ungraded by anyone | No (read, not host) | Coverage explosion on the traits that matter |
| **L4 — Player uploads** | clips players give us | highest-quality, consented, labeled, **proprietary by construction**; the incentive flywheel | **Yes** | The durable, ever-fresh, defensible top |

**The insight:** L1–L3 solve cold-start coverage *without players showing up first*. That powers the most potent acquisition hook imaginable — we read an athlete who's never heard of us, then show up and say **"we already see you."** L4 is the owned, consented, freshest layer that no one can copy. NCSA has only a weak L4 (paid profiles). We have all four.

---

## 3. The five refinement loops (why it learns, not just grows)

Data + agents without loops is a snapshot. The loops make it learn. Several are loops our incumbents *cannot* run.

- **Loop A — Cross-source agreement (self-supervision).** When L1 stats, L2 write-ups, and L3 film agree, confidence rises; when they disagree, flag for a closer look. Free labels from convergence; the model learns to weight sources.
- **Loop B — Outcome calibration (the truth signal). ★ the deepest moat.** Commits, minutes, all-conference, level reached, draft, portal moves — *reality* eventually scores our read. This tunes the engine **and** becomes provable credibility: "a FieldCheck 7.4 reaches D1 at X%." Pay-to-play sites can never claim this — their numbers are for sale. Requires time + coverage + honesty, all three. Start logging outcomes the moment we have any.
- **Loop C — Human-in-the-loop corrections.** A coach/athlete/scout disagreeing with a read = high-value labeled data. Sharpens calibration *and* deepens relationship.
- **Loop D — Upload incentive flywheel.** Honest reads → athletes want in → uploads → better reads. The acquisition loop (the original Clips Moat).
- **Loop E — Agent-usage signal.** Which moments coaches watch, which cuts get shared, which outreach gets replies → tells us which reads *matter* → feeds what to surface. **Agents are sensors, not just consumers** — every interaction generates new data that returns to the loops.

Five independent reasons to improve every day. The compounding is the point.

---

## 4. The agent constellation (agents everywhere)

The rule: **anywhere a human currently does recruiting labor, FieldCheck puts an agent — and every agent runs on the refinery.** Two sides.

### Acquisition-side (fill the refinery)
- **The Ingestion Agents** — scraper/reader/film-miner. Turn L1–L3 exhaust into graded rows under the no-inflation firewall. This is the "get to the right player number" engine. *(New front. Not built.)*

### Athlete-side utility (spend the output, drive uploads)
- **The Scout** — the verdict. 8 facets vs the GOAT; the invisible four. *(Built; engine recalibrating on `lab`.)*
- **The Editor** — Highlight Agent. Watches film, surfaces the moments others skip, builds three cuts (Coach / Story / Facet-Proof). *(Built; live vision pipeline wired, on dev.)*
- **The Strategist** — the recruiting-fit agent. Given verdict + academics + preferences, builds a real **reach / match / safety** target list with the *why* per fit (division level, position need, roster gaps, academics, region). This is the exact expensive human job NCSA sells, free and grounded in an honest read. *(Not built — highest-leverage next.)*
- **The Messenger** — outreach. Personalizes coach contact per target, tracks what was sent, nudges follow-ups, knows contact-period rules. *(Send Kit is the seed; full version forces the backend.)*
- **The Coach** — development. Turns the read into a plan ("mental-strength reset is your gap — 3 drills, re-grade in 8 weeks"). Retention engine **and** the re-upload/re-grade cadence (UTR-style). *(Not built; high stickiness.)*

### Coach-side (the demand that monetizes)
- **The Discovery Agent** — college coaches query the graded dataset ("OHs, 2026, 6'2"+, competitiveness 7+, Midwest, academically eligible for us"). Closes the marketplace. **Coaches pay; athletes stay free; the no-payola firewall holds.** *(Not built.)*

### Parent-side
- **The Copilot** — plain-language honesty: what's real, what's next, what NCSA won't tell you. The emotional anti-NCSA wedge — reduce the anxiety they monetize. *(Not built; light, threaded throughout.)*

---

## 5. The fusion flywheel (how it all closes)

```
   Ingestion agents (mine L1–L3)
            │  +  Player uploads (L4)
            ▼
   ┌─────────────────────────┐
   │   THE GRADED DATASET     │  ← coverage
   │   (honest reads at scale)│
   └─────────────────────────┘
            ▲            │
   Loops A–E (refine)    │  exposed through
   calibration + truth   ▼
            │     Utility agents (Scout, Editor, Strategist,
            │     Messenger, Coach) · Discovery · Parent Copilot
            │            │
            └──── usage + outcomes feed back ────┘
```

Agents on the acquisition side fill the refinery; loops refine it; agents on the utility side make it valuable and harvest fresh signal that returns to the loops. Closed flywheel. **Data is the moat; agents fill and spend it; loops compound it.**

---

## 6. Why this beats NCSA (the teardown, kept)

NCSA charges $1,200–3,000+/yr, sells hard to anxious parents, and families still do the homework themselves; coaches distrust the rankings; cancellations are ugly. Our wedge, now sharpened by the doctrine:

- **Honest read** (unfakeable in a market of vanity 4-stars) — only possible *because* we don't sell rankings (Loop B credibility).
- **Coverage they can't match** — L1–L3 lets us read athletes who never paid, never signed up. "We already see you."
- **Agents do the labor they charge humans for** — Strategist = the headshot list; Messenger = the outreach; Coach = the development plan. Free.
- **The firewall is the brand:** the moment FieldCheck charges to be listed or inflates a grade, it becomes NCSA. Athletes free forever; coaches/orgs pay; no payola. (Six constraints unchanged.)

---

## 7. Constraints & firewall (the honesty discipline = the moat)

The moat is honest *refinement*. Constraints are features because they're hard:

- **No-inflation firewall on ingestion.** L1–L3 carry hype and bias; ingestion agents must extract signal *under the same no-inflation discipline* or we reintroduce the garbage we differentiate against.
- **Sourcing must be defensible.** ToS/scraping limits (L1–L2) and copyright on existing video (L3) are real. We **read** film to grade; we don't rehost it. Legal posture is part of the architecture, not an afterthought.
- **Calibration before claims.** We only publish "FieldCheck predicts at X%" once Loop B has the outcomes to back it. Never fake the credibility — that *is* the credibility.
- **Free-tier permanent, no payola, six constraints unchanged.**

---

## 8. Roadmap alignment — the 16 phases, re-read with the data moat as driver

The original 0–15 plan was a **feature** roadmap. The doctrine reorganizes it into **two fronts + a spine**, and forces three structural moves (below the table).

| Phase (original) | Re-read through the doctrine | Front | Status |
|---|---|---|---|
| **0–4.x** Engine / grading / Bayesian / Flagg | **The Scout** + engine calibration. The core read. | Utility | ✓ built; recalibrating on `lab`, `main` stable |
| **5** Amateur Stickiness (identity card, shareable polygon, peer-compare, schedule, push) | **The Card** + **L4 upload stickiness** (Loop D). Verdict-identity, shareable. | Utility / L4 | Card built (Studio), shipping to prod; peer-compare/schedule/push pending |
| **6** Coach/Parent + Hudl-highlight + ~~16-voices~~ | **The Editor** (Hudl-highlight = Highlight Agent) + **The Coach** + **Parent Copilot**. *Note: "16 voices" is retired narrative — now 8 facets vs GOAT.* | Utility | Editor built + live-wired (dev); Coach/Parent agents pending |
| **7** Backend | **The refinery infra**: upload-at-scale, Messenger store, **Loop B outcome logging**, auth. The light-backend (Supabase) decision. | Spine | Pending — unblocks Messenger + calibration |
| **8** Performance | Cross-cutting; serves every agent surface. | Spine | Ongoing |
| **9** AI Agent (was "fwd from 13") | **PROMOTED: no longer one phase — it's the architecture.** Strategist, Messenger, Discovery, Ingestion, etc. all live here conceptually. | Both | Reframed as the through-line |
| **10** Club / Franchise | **The Discovery Agent** (coach-side query) + org surfaces + **monetization**. | Coach-side | Pending |
| **11** Mobile | Delivery surface for all agents (Studio is already mobile-first). | Utility | Ongoing |
| **12** Soccer (+ more sports) | **Coverage expansion** = more L1–L3 data layers, more of the dataset. | Refinery | Pending |
| **13** Video + Gems (was DEFERRED) | **PROMOTED TO CORE.** L3 film-mining + the Editor + the vision pipeline. The data-moat reframe makes this central, not deferred. | Refinery | Un-deferred; vision pipeline now built (dev) |
| **14** Pricing (PAUSED) | Monetize the **coach/org side** (Discovery); athlete side stays free **by design** (firewall). Stays "paused" on athletes permanently. | Coach-side | Intentionally athlete-free |
| **15** API + Partners | Expose dataset/agents to partners (LOVB, leagues) — **data network effects**. | Refinery | Pending |

**The three structural moves the reconciliation forces:**
1. **Ph13 (Video) un-deferred → core.** It was parked as a feature; as L3 film-mining it's a pillar of the moat.
2. **Ph9 (AI Agent) stops being a phase → becomes the architecture.** Agents are the whole second axis, not a milestone.
3. **A new front + spine the original 16 didn't name:** **Ingestion agents (L1–L3 coverage)** and the **Calibration loop (Loop B)** — the "right player number" engine and the credibility proof. These are now first-class.

### The two fronts (how to actually sequence)
- **Front 1 — Utility agents.** Scout ✓, Editor ✓ → **Strategist (next)** → Messenger → Coach. Makes today's athletes succeed; drives L4 uploads. Needs little/no new infra to start.
- **Front 2 — The refinery.** L1 ingestion (coverage) → L3 film-mining → Loops, anchored by **Loop B outcome logging from day one**. The durable moat; the "get to the right player number."

They feed each other and run in parallel: Utility drives uploads while Ingestion builds coverage; Loop B starts logging the instant any outcome exists.

---

## 9. Where we are / what's next

**Built & converging (shipping to prod now):** Scout (engine), Editor (Highlight Agent + live vision on dev), the Card, Send Kit seed, Top-100 board, clips-moat mechanism (Loop D), login/session, LOVB surface.

**Recommended next build:** **The Strategist** (Front 1) — most differentiated, guts NCSA's softest point, needs no new infra, and generates the target list the Messenger needs — **in parallel with** standing up **L1 ingestion + the Loop B outcome-logging spine** (Front 2), because that's the moat we care most about and the sooner outcomes log, the sooner the unfakeable "we predict, they sell" proof exists.

---

## 10. Tenets to fold into FIELDCHECK_BIBLE.md

- **T — Refinery, not collection.** We ingest the world's athletic exhaust (L1 public, L2 scraps, L3 existing video, L4 uploads) and refine it into honest reads. Uploads are one layer, not the whole moat.
- **T — Coverage × Calibration × Utility.** The moat is all three at once; a rival must beat all three simultaneously. Never trade one for another.
- **T — Honesty is the calibration.** We publish "FieldCheck predicts at X%" only when Loop B backs it. Faking credibility destroys the only thing pay-to-play can't copy.
- **T — Agents are sensors.** Every agent interaction generates data that returns to the loops. Build agents to capture signal, not just serve answers.
- **T — Agents everywhere, on the moat.** Anywhere a human does recruiting labor, put an agent; every agent must run on the refinery, or it's just a chatbot.
- **T — Read film, don't rehost it.** L3 is mined for grading signal under defensible sourcing; the firewall and legal posture are architecture.
- **T — "We already see you."** L1–L3 coverage lets us read athletes who never paid — the acquisition hook no incumbent has.
