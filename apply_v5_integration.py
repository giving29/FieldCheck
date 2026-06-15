#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
APPLY V5 ALGORITHM INTEGRATION
═══════════════════════════════════════════════════════════════════════════
Adds V5 algorithm content to three surfaces:
  1. FC_CANONICAL_STATE_V1.html · new Tab 19 V5 Algorithm
  2. METHODOLOGY_V17_V1.html    · new section 10 V5 Algorithm
  3. v5-algorithm.html          · standalone full design doc

Run from ~/Desktop/fieldcheck-proxy/
Pre-req: v5_algorithm_design_doc_v2.html must exist in ~/Downloads/
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, subprocess
from pathlib import Path

print("═══ V5 ALGORITHM INTEGRATION ═══\n")

HERE = Path('.')
CANON = HERE / 'FC_CANONICAL_STATE_V1.html'
METHOD = HERE / 'METHODOLOGY_V17_V1.html'
STANDALONE_SRC = Path.home() / 'Downloads' / 'v5_algorithm_design_doc_v2.html'
STANDALONE_DST = HERE / 'v5-algorithm.html'
REDIRECTS = HERE / '_redirects'

for p in [CANON, METHOD, STANDALONE_SRC]:
    if not p.exists():
        print(f"FAIL: {p} not found")
        sys.exit(1)

# ═══ V5 CANONICAL PANE CONTENT (matches canonical .pane / .sec aesthetic) ═══

CANON_PANE = '''
<!-- ═══════════════════════════════════════════════════════════ -->
<!-- PANE 19: V5 ALGORITHM                                          -->
<!-- ═══════════════════════════════════════════════════════════ -->
<section class="pane" id="pane-v5algo">
  <div class="pane-h">V5 <b>Algorithm</b></div>
  <div class="pane-sub">// 10 is the only ceiling · evidence rigor is the only limiter · cross-sport · LIVING document · May 26, 2026 nt</div>

  <div class="sec">
    <div class="sec-h">The philosophy <span class="pin gold">crystallized May 26 nt</span></div>
    <div class="sec-desc" style="font-style:italic;border-left:3px solid var(--gold);padding-left:14px;color:var(--t1);font-size:18px;line-height:1.55">"Making every number make sense and measured against the highest non-reachable ceiling of 10 — that's all there is."</div>
    <div class="sec-desc" style="margin-top:14px">UTR-inspired. Single 0-10 score per athlete. Gender, age, sport-blind. No caps. No buckets. No clamps. Each facet scored from evidence measured against theoretical perfection. <b>10 = unreachable. Jordan reference = 9.9.</b> Anchors describe the natural distribution evidence produces, not enforcement boundaries. Phenoms (Kobe/LeBron/KD/Tiger at 17) emerge naturally when evidence is pro-tier at sub-pro age.</div>
    <div class="sec-desc" style="margin-top:14px;padding:14px 16px;background:rgba(78,201,192,0.04);border-left:3px solid var(--teal);border-radius:3px">
      <b style="color:var(--teal)">LIVING DOCUMENT.</b> When the V5 algorithm produces a score that surprises us — and the surprise is informative, not noise — this tab, the methodology page, and the standalone design doc all update together. Strategy + tactics always aligned.
    </div>
    <div class="sec-desc" style="margin-top:14px"><b>Full standalone design doc:</b> <a href="/v5-algorithm" style="color:var(--gold);text-decoration:underline">/v5-algorithm</a> — per-facet evidence ladders, anti-inflation rules, phenom criteria, 16 cross-sport test cases, implementation notes.</div>
  </div>

  <div class="sec">
    <div class="sec-h">The 8 facets · cross-sport theoretical 10 anchors</div>
    <div class="sec-desc">Same 10 ceiling whether basketball, football, baseball, tennis, golf, soccer, volleyball, hockey. Per-facet anchors carry across sports — the theoretical perfect-facet is the same; only the sport context differs.</div>
    <table class="tbl" style="margin-top:14px">
      <thead><tr><th>Facet</th><th>Theoretical 10 anchor · cross-sport</th></tr></thead>
      <tbody>
        <tr><td><b>01 Character</b><br><span style="color:var(--t3);font-size:10px;font-family:'JetBrains Mono',monospace">apex · wt 0.18</span></td><td style="font-size:13px;line-height:1.55">Adult-stress-tested career-complete. All 5 sub-dims max simultaneously. <em>BB: Duncan, Nash · FB: P. Manning, Brees · BB: Jeter, Ripken · Tennis: Federer · Golf: Nicklaus, Palmer · Soccer: post-2018 Messi · VB: May-Treanor, Kiraly · Hockey: Crosby</em></td></tr>
        <tr><td><b>02 Mindset</b></td><td style="font-size:13px;line-height:1.55">Process-driven obsessive prep that defines the sport's standard. <em>BB: Kobe, Jordan · FB: Brady (TB12), P. Manning · Baseball: Jeter, Maddux, Ichiro · Tennis: Nadal, Djokovic · Golf: Tiger peak, Hogan · Soccer: Ronaldo · Hockey: Crosby, Gretzky</em></td></tr>
        <tr><td><b>03 Mental Strength</b></td><td style="font-size:13px;line-height:1.55">Highest-pressure performance every time the stage demands it. <em>BB: Jordan 98 G6, Kobe, Bird · FB: Brady (28-3), Montana · Baseball: Jeter (Mr. Nov), Reggie Jackson · Tennis: Djokovic, Serena, Nadal · Golf: Tiger Masters, Nicklaus '86 · Soccer: Ronaldo UCL, Messi '22 WC · VB: Kiraly 3 golds · Hockey: Messier '94, Roy</em></td></tr>
        <tr><td><b>04 Talent</b></td><td style="font-size:13px;line-height:1.55">Generational raw ability + skill · era-defining. <em>BB: LeBron peak, Jordan, Magic, Wilt · FB: Mahomes peak, L. Taylor, Bo Jackson, J. Rice · Baseball: Trout, Ohtani, Ruth, Mays · Tennis: Federer peak, Sampras, Graf · Golf: Tiger peak, Nicklaus, Sörenstam · Soccer: Messi peak, Ronaldo peak, Pelé, Maradona · Hockey: Gretzky, Lemieux, Orr, McDavid · Track: Bolt</em></td></tr>
        <tr><td><b>05 Physical</b></td><td style="font-size:13px;line-height:1.55">Peak athletic prime perfection · size+strength+speed+vertical+durability all max. <em>BB: LeBron 2012, V. Carter, Giannis · FB: Bo Jackson, Barkley, A. Peterson · Baseball: Trout, A. Judge · Tennis: Serena, Nadal prime · Golf: Tiger peak, D. Johnson · Soccer: Ronaldo prime, Haaland · VB: K. Hill, Kiraly · Track: Bolt, Phelps</em></td></tr>
        <tr><td><b>06 Mental / IQ</b></td><td style="font-size:13px;line-height:1.55">Sees the play before it happens · anticipates two passes/pitches/shots ahead. <em>BB: Bird, Magic, Jokic, Chris Paul, LeBron · FB: P. Manning, Brady, Brees, Montana · Baseball: Maddux, Gwynn, Posey · Tennis: Federer, Djokovic · Golf: Tiger, Nicklaus · Soccer: Xavi, Iniesta, Pirlo, De Bruyne, Modrić · Hockey: Gretzky, Kane, McDavid · VB: Kiraly, K. Walsh Jennings</em></td></tr>
        <tr><td><b>07 Coachability</b></td><td style="font-size:13px;line-height:1.55">Perfect adaptive learner · multi-coach validation across career. <em>BB: Duncan/Popovich, Curry/Kerr, Leonard · FB: Brady/Belichick, P. Manning multi-coach · Baseball: Jeter/Torre, Trout/Scioscia · Tennis: Nadal/T. Nadal→Moyá, Federer/Edberg/Ljubicic · Golf: Tiger early/B. Harmon · Soccer: Messi/Guardiola, Iniesta, Modrić · VB: Kiraly multi-Olympic · Hockey: Crosby, Yzerman</em></td></tr>
        <tr><td><b>08 Competitiveness</b></td><td style="font-size:13px;line-height:1.55">Killer instinct · refuses to lose. <em>BB: Jordan (canonical), Kobe, Bird, Isiah · FB: Brady, R. Lewis, L. Taylor, Favre · Baseball: Jeter, Gibson (Pete Rose w/ character caveat) · Tennis: Djokovic, Serena, McEnroe, Connors · Golf: Tiger peak, Nicklaus, Sörenstam · Soccer: Ronaldo, Maradona, Keane · Hockey: Messier '94, G. Howe, S. Stevens · VB: Kiraly, May-Treanor</em></td></tr>
      </tbody>
    </table>
  </div>

  <div class="sec">
    <div class="sec-h">Phenom doctrine · locked <span class="pin teal">earned by evidence, not awarded by hype</span></div>
    <div class="sec-desc">A phenom is the rare athlete whose evidence at a sub-pro age already justifies higher scores than typical for their category. <b>Requires ALL 4 criteria. If any one missing, athlete is not a phenom — scored against standard evidence ladder for category.</b></div>
    <table class="tbl" style="margin-top:14px">
      <thead><tr><th>Req</th><th>Requirement</th></tr></thead>
      <tbody>
        <tr><td><b>REQ 1</b></td><td><b>Pro-tier evidence at sub-pro age.</b> Not projection. Actual measurable pro-tier evidence demonstrated NOW. The evidence already exists; it's not a forecast.</td></tr>
        <tr><td><b>REQ 2</b></td><td><b>Multi-source corroboration.</b> 3+ independent sources agree. Not 3 sources of the same recruiting service. Single-source phenom claims rejected.</td></tr>
        <tr><td><b>REQ 3</b></td><td><b>Older-competition validation.</b> Dominance against significantly older competitors, not same-age cohort. Same-age dominance does NOT qualify.</td></tr>
        <tr><td><b>REQ 4</b></td><td><b>Sustained across multiple events.</b> Pattern across multiple high-level events, not single-tournament dominance. Sample-of-one heroics do NOT qualify.</td></tr>
      </tbody>
    </table>
    <div class="sec-desc" style="margin-top:14px"><b>Canonical phenom cases:</b> Kobe at 17 (Adidas ABCD vs older All-Americans) · LeBron at 17 (NBA-bound 19yo scrimmages) · KD at 18 (Naismith POY freshman) · Tiger at 17 (3x US Junior + adult amateurs) · P. Mahomes at 21 · Coco Gauff at 15 (Wimbledon QF) · Gretzky at 17 (110pt WHA rookie) · Bo Jackson 22 (dual-sport pro-tier).</div>
  </div>

  <div class="sec">
    <div class="sec-h">Anti-inflation doctrine · what does NOT count as evidence <span class="pin warn">universal</span></div>
    <div class="sec-desc">These signals correlate with score inflation in V4 and prior. V5 explicitly excludes them from facet scoring. Score what the evidence shows NOW — not potential, projection, hype, or market expectation.</div>
    <ul style="margin-top:14px;padding-left:0;list-style:none">
      <li style="padding:8px 14px;margin-bottom:6px;background:rgba(255,92,58,0.04);border-left:3px solid rgba(255,92,58,0.5);border-radius:0 8px 8px 0;font-size:13px;color:var(--t2)"><b style="color:var(--warn)">▲ Recruiting rankings</b> (247/On3/Rivals/ESPN) — these are projection consensus, not evidence. A 5-star ranking does not justify any specific facet score.</li>
      <li style="padding:8px 14px;margin-bottom:6px;background:rgba(255,92,58,0.04);border-left:3px solid rgba(255,92,58,0.5);border-radius:0 8px 8px 0;font-size:13px;color:var(--t2)"><b style="color:var(--warn)">▲ Draft slot / mock draft consensus</b> — #1 overall pick projection is consensus expectation. Rookies do NOT inherit pro-tier scores by draft position.</li>
      <li style="padding:8px 14px;margin-bottom:6px;background:rgba(255,92,58,0.04);border-left:3px solid rgba(255,92,58,0.5);border-radius:0 8px 8px 0;font-size:13px;color:var(--t2)"><b style="color:var(--warn)">▲ NIL deal size</b> — market price for marketing rights, not athletic facet performance. $8M NIL ≠ 8.0 facet score.</li>
      <li style="padding:8px 14px;margin-bottom:6px;background:rgba(255,92,58,0.04);border-left:3px solid rgba(255,92,58,0.5);border-radius:0 8px 8px 0;font-size:13px;color:var(--t2)"><b style="color:var(--warn)">▲ Media narrative / hype</b> — opinion aggregates. Influence market consensus (the polygon shadow overlay) but do NOT score the FieldCheck polygon.</li>
      <li style="padding:8px 14px;margin-bottom:6px;background:rgba(255,92,58,0.04);border-left:3px solid rgba(255,92,58,0.5);border-radius:0 8px 8px 0;font-size:13px;color:var(--t2)"><b style="color:var(--warn)">▲ Family lineage</b> — parent isn't the athlete. Lineage does not transfer evidence.</li>
      <li style="padding:8px 14px;margin-bottom:6px;background:rgba(255,92,58,0.04);border-left:3px solid rgba(255,92,58,0.5);border-radius:0 8px 8px 0;font-size:13px;color:var(--t2)"><b style="color:var(--warn)">▲ Coach quotes during recruitment</b> — sales pitches. Post-arrival quotes count; recruitment quotes don't.</li>
      <li style="padding:8px 14px;margin-bottom:6px;background:rgba(255,92,58,0.04);border-left:3px solid rgba(255,92,58,0.5);border-radius:0 8px 8px 0;font-size:13px;color:var(--t2)"><b style="color:var(--warn)">▲ Single-event heroics</b> — sample-of-one moments. Evidence must show pattern across multiple events at appropriate level.</li>
      <li style="padding:8px 14px;margin-bottom:6px;background:rgba(255,92,58,0.04);border-left:3px solid rgba(255,92,58,0.5);border-radius:0 8px 8px 0;font-size:13px;color:var(--t2)"><b style="color:var(--warn)">▲ Combine measurables without game translation</b> — 40 time/vertical/wingspan alone are inputs to Physical facet but require game-level translation to score above median.</li>
    </ul>
    <div class="sec-desc" style="margin-top:14px;padding:14px 16px;background:rgba(245,184,0,0.06);border-left:3px solid var(--gold);border-radius:3px;font-size:15px"><b style="color:var(--gold)">Default-low principle:</b> when evidence is missing, the facet defaults to 2-3, NOT to average 5. The algorithm earns higher scores; it does not assume them. <b>V4 assumed 5 baseline. V5 assumes low until proven.</b> This is the core fix.</div>
  </div>

  <div class="sec">
    <div class="sec-h">Test corpus · 16 cross-sport cases the V5 algorithm must pass on paper</div>
    <div class="sec-desc">Before any worker.js patch. If the design produces these expected scores on the available evidence, V5 is wired right. If not, the design needs iteration — here, not in code.</div>
    <table class="tbl" style="margin-top:14px">
      <thead><tr><th>Athlete · Sport · Context</th><th>Expected V5</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td><b>Tyran Stokes</b> · mens-bb · HS #1 2026 class</td><td style="color:var(--gold);font-weight:700">4.5–5.4</td><td style="font-size:12px">HS-only evidence. Rankings excluded. No older-comp pro-tier evidence so phenom fails. Top of HS pool.</td></tr>
        <tr><td><b>Cooper Flagg</b> · mens-bb · NBA rookie · #1 pick</td><td style="color:var(--gold);font-weight:700">6.5–7.5</td><td style="font-size:12px">Rookie sample limited. Draft slot excluded. Pro production real but small sample.</td></tr>
        <tr><td><b>Caitlin Clark</b> · womens-bb · WNBA year 2 · ROY yr 1</td><td style="color:var(--gold);font-weight:700">7.0–7.8</td><td style="font-size:12px">Actual pro production for year+. College all-time-great. Year-2 WNBA still developing.</td></tr>
        <tr><td><b>Tim Duncan</b> · mens-bb · retired HOF · 5 rings 2 MVPs</td><td style="color:var(--gold);font-weight:700">9.3–9.6</td><td style="font-size:12px">Career-complete all-time-great. All 5 char sub-dims maxed. Two decades dominance.</td></tr>
        <tr><td><b>Steph Curry</b> · mens-bb · active multi-MVP</td><td style="color:var(--gold);font-weight:700">9.0–9.3</td><td style="font-size:12px">Multi-MVP with rings. Active career still open. Final cal awaits career end.</td></tr>
        <tr><td><b>Michael Jordan</b> · mens-bb · retired GOAT (REFERENCE)</td><td style="color:var(--gold);font-weight:700">9.9</td><td style="font-size:12px">The singular calibration anchor. No human reaches 10 (theoretical perfection).</td></tr>
        <tr><td><b>Patrick Mahomes</b> · football · active 3 SB 2 MVPs pre-30</td><td style="color:var(--gold);font-weight:700">8.8–9.2</td><td style="font-size:12px">Football equivalent of active multi-MVP. Career still developing.</td></tr>
        <tr><td><b>Tom Brady</b> · football · retired 7 SB 3 MVPs</td><td style="color:var(--gold);font-weight:700">9.4–9.7</td><td style="font-size:12px">Football equivalent of retired HOF (Duncan/Jeter tier).</td></tr>
        <tr><td><b>Tiger Woods peak</b> · golf · 15 majors · #1 longest streak</td><td style="color:var(--gold);font-weight:700">9.5–9.8</td><td style="font-size:12px">Generational dominance, multi-major, sport-defining. Near-Jordan band.</td></tr>
        <tr><td><b>Mike Trout peak</b> · baseball · 3 MVPs · best WAR generation</td><td style="color:var(--gold);font-weight:700">9.0–9.4</td><td style="font-size:12px">Multi-MVP. Sport-defining. Injury-curtailed late but peak generational.</td></tr>
        <tr><td><b>Cameron Boozer</b> · mens-bb · Duke fresh · son of Carlos</td><td style="color:var(--gold);font-weight:700">6.0–7.0</td><td style="font-size:12px">HS resume excluded. Family lineage excluded. Freshman D1 in progress.</td></tr>
        <tr><td><b>Kenyon Goodin</b> · mens-bb · D1 soph mid-major 3-star</td><td style="color:var(--gold);font-weight:700">6.0–6.7</td><td style="font-size:12px">2 yrs D1 mid-major. No market consensus = polygon hidden gem signal.</td></tr>
        <tr><td><b>Coco Gauff</b> · tennis · pro · 1 GS · top-5</td><td style="color:var(--gold);font-weight:700">7.5–8.2</td><td style="font-size:12px">Pro production several yrs. 1 GS. Phenom criteria passed at 15, now scored on pro evidence.</td></tr>
        <tr><td><b>Hypothetical Kobe-at-17</b> · phenom test case</td><td style="color:var(--gold);font-weight:700">6.0–7.0</td><td style="font-size:12px">Passes all 4 phenom criteria. Phenom escape, but evidence still sub-pro age.</td></tr>
        <tr><td><b>Tate Ivanyo</b> · corpus contamination test</td><td style="color:var(--gold);font-weight:700">3.5–5.5</td><td style="font-size:12px">Tests corpus hygiene, not algorithm calibration. Match amateur evidence available.</td></tr>
        <tr><td><b>Median HS varsity player</b> · floor case</td><td style="color:var(--gold);font-weight:700">3.0–4.0</td><td style="font-size:12px">HS-only evidence at average level. The 3.5 floor — what evidence at this level produces.</td></tr>
      </tbody>
    </table>
  </div>

  <div class="sec">
    <div class="sec-h">Implementation · from design to worker.js</div>
    <div class="sec-desc">Once approved, worker patches are mechanical: remove cap clamp on composite output, replace synthesis Haiku prompt with V5 structure derived from this design, add per-facet evidence audit to output.</div>
    <ul style="margin-top:14px;padding-left:0;list-style:none">
      <li style="padding:10px 14px;margin-bottom:8px;background:rgba(107,170,90,0.06);border-left:3px solid var(--moss);border-radius:0 8px 8px 0;font-size:13px"><b>P1 · remove cap clamp on composite output</b> (line 11477) — composite reads <code>_v22_31_raw</code> directly. Cap stays in metadata for transparency.</li>
      <li style="padding:10px 14px;margin-bottom:8px;background:rgba(107,170,90,0.06);border-left:3px solid var(--moss);border-radius:0 8px 8px 0;font-size:13px"><b>P2 · replace synthesis prompt</b> with V5 structure — per-facet evidence ladders, anti-inflation list explicit, phenom criteria locked, default-low principle stated.</li>
      <li style="padding:10px 14px;margin-bottom:8px;background:rgba(107,170,90,0.06);border-left:3px solid var(--moss);border-radius:0 8px 8px 0;font-size:13px"><b>P3 · add per-facet evidence audit to output</b> — synthesis returns evidence anchor + quality + anti-inflation check per facet. Powers the polygon CI bands (low-quality evidence → wide CI) and audit trail.</li>
      <li style="padding:10px 14px;margin-bottom:8px;background:rgba(107,170,90,0.06);border-left:3px solid var(--moss);border-radius:0 8px 8px 0;font-size:13px"><b>P4 · banner V022.32-YX → V022.34-V5 + cache bump</b> · invalidates synthesis cache, cold-runs V5 fresh against 16 test corpus.</li>
    </ul>
  </div>

  <div class="sec">
    <div class="sec-h">Postmortem · why V5 v1 produced 9.6-9.8 HS scores <span class="pin warn">May 26 nt · rolled back</span></div>
    <div class="sec-desc">The first attempt removed caps but didn't strengthen evidence requirements. Haiku, freed from enforcement, defaulted to scoring on recruiting hype and projection — exactly what V5 was supposed to eliminate.</div>
    <ul style="margin-top:14px;padding-left:18px;font-size:13px;line-height:1.7;color:var(--t2)">
      <li>Removed "HARD CAP" language without adding stronger evidence floors</li>
      <li>PHENOMS clause too liberal — Haiku treated every top recruit as candidate</li>
      <li>EVIDENCE RIGOR clause existed but lacked specific anti-inflation list</li>
      <li>No explicit per-facet evidence ladder — Haiku inferred bands</li>
      <li>No default-low principle stated — Haiku assumed 5 baseline</li>
      <li>No output audit format — couldn't see WHY scores were what they were</li>
    </ul>
    <div class="sec-desc" style="margin-top:14px;padding:14px 16px;background:rgba(78,201,192,0.04);border-left:3px solid var(--teal);border-radius:3px;font-style:italic"><b style="color:var(--teal)">V5 v2 fixes all six.</b> The design is the prompt. The prompt is the algorithm. No more inferred behavior from loose framing. Full standalone: <a href="/v5-algorithm" style="color:var(--gold)">/v5-algorithm</a></div>
  </div>
</section>
'''

# ═══ V5 METHODOLOGY SECTION CONTENT (matches methodology h2/body-text/callout/facets) ═══

METHOD_SECTION = '''
<section id="v5algo">
  <h2><span class="num">10</span>The <b>V5 algorithm</b> · 10 is the only ceiling</h2>
  <p class="body-text">v1.7 was the framework. V5 is how the algorithm produces every score on that framework. Same 8 facets. Same refinements. Same review panel. What V5 adds is a single explicit principle that governs every number: <em>10 is the only ceiling, and evidence rigor is the only limiter.</em></p>
  <p class="body-text">No caps. No buckets. No clamps. Each facet is scored from 0 to 10, measured against theoretical perfection. <b>10 is unreachable.</b> The reference distribution Michael Jordan sits at <b>9.9</b>; Tim Duncan at career-complete sits at <b>9.3–9.6</b>; a typical HS varsity player sits at <b>3.0–4.0</b>. These are not enforcement boundaries. They are the natural distribution that evidence produces when the algorithm is calibrated rigorously.</p>

  <div class="callout">
    <b>The philosophy:</b> the algorithm scores what the evidence shows NOW. Not potential. Not projection. Not hype. Not what the market expects. UTR has it right — Sinner at 16 was UTR 12+ while normal 16-year-olds were 5-7. The math produced that, not buckets.
  </div>

  <h3>The phenom doctrine</h3>
  <p class="body-text">A phenom is the rare athlete whose evidence at a sub-pro age already justifies higher scores than typical for their category. Kobe at 17. LeBron at 17. KD at 18. Tiger at 17. Coco Gauff at 15. Wayne Gretzky at 17. <b>Phenom status requires ALL four criteria. If any one is missing, the athlete is not a phenom — they are scored against the standard evidence ladder for their category.</b></p>

  <div class="facets">
    <div class="facet">
      <div class="facet-num">// REQ 1</div>
      <div class="facet-name">Pro-tier evidence at sub-pro age</div>
      <div class="facet-desc">Not projection. Actual measurable pro-tier evidence demonstrated NOW. The evidence already exists; it's not a forecast.</div>
    </div>
    <div class="facet">
      <div class="facet-num">// REQ 2</div>
      <div class="facet-name">Multi-source corroboration</div>
      <div class="facet-desc">3+ independent sources agree on the pro-tier evidence. Not 3 sources of the same recruiting service. Single-source phenom claims rejected.</div>
    </div>
    <div class="facet">
      <div class="facet-num">// REQ 3</div>
      <div class="facet-name">Older-competition validation</div>
      <div class="facet-desc">Dominance against significantly older competitors, not same-age cohort. Same-age dominance does not qualify as phenom evidence.</div>
    </div>
    <div class="facet">
      <div class="facet-num">// REQ 4</div>
      <div class="facet-name">Sustained across multiple events</div>
      <div class="facet-desc">Pattern across multiple high-level events, not single-tournament dominance. Sample-of-one heroics do not qualify.</div>
    </div>
  </div>

  <h3>What does NOT count as evidence</h3>
  <p class="body-text">Universal across all 8 facets, across all sports. These signals correlate with score inflation in prior versions. V5 explicitly excludes them from facet scoring.</p>

  <div class="principles">
    <div class="principle"><div class="principle-num">▲</div><div class="principle-body"><div class="principle-h">Recruiting rankings</div><div class="principle-desc">247 composite, On3, Rivals, ESPN — these are <b>projection consensus</b>, not evidence. A 5-star ranking does not justify any specific facet score.</div></div></div>
    <div class="principle"><div class="principle-num">▲</div><div class="principle-body"><div class="principle-h">Draft slot / mock draft consensus</div><div class="principle-desc">#1 overall pick projection is consensus expectation. Rookies do not inherit pro-tier scores by virtue of draft position.</div></div></div>
    <div class="principle"><div class="principle-num">▲</div><div class="principle-body"><div class="principle-h">NIL deal size / brand deals</div><div class="principle-desc">Market price for marketing rights. Tells us nothing about athletic facet performance. $8M NIL ≠ 8.0 facet score.</div></div></div>
    <div class="principle"><div class="principle-num">▲</div><div class="principle-body"><div class="principle-h">Media narrative / hype</div><div class="principle-desc">Opinion aggregates. They influence market consensus (the polygon shadow overlay) but they do NOT score the FieldCheck polygon.</div></div></div>
    <div class="principle"><div class="principle-num">▲</div><div class="principle-body"><div class="principle-h">Family lineage</div><div class="principle-desc">"Son of an NBA player" / "father played in NFL" — the parent isn't the athlete. Lineage does not transfer evidence.</div></div></div>
    <div class="principle"><div class="principle-num">▲</div><div class="principle-body"><div class="principle-h">Coach quotes during recruitment</div><div class="principle-desc">Sales pitches. Independent post-arrival coach quotes count; recruitment quotes don't.</div></div></div>
    <div class="principle"><div class="principle-num">▲</div><div class="principle-body"><div class="principle-h">Single-event heroics</div><div class="principle-desc">One state championship. One AAU tournament. Sample-of-one moments. Evidence must show pattern across multiple events.</div></div></div>
    <div class="principle"><div class="principle-num">▲</div><div class="principle-body"><div class="principle-h">Combine measurables without game translation</div><div class="principle-desc">40 time, vertical, wingspan, serve speed — inputs to Physical facet but require game-level translation to score above median.</div></div></div>
  </div>

  <div class="callout teal">
    <b>Default-low principle:</b> when evidence is missing, the facet defaults to 2-3, NOT to average 5. The algorithm earns higher scores; it does not assume them. <b>This is the core fix from V4.</b>
  </div>

  <h3>Cross-sport · same 10 ceiling</h3>
  <p class="body-text">FieldCheck is all sports. Per-facet theoretical anchors carry across — basketball, football, baseball, tennis, golf, soccer, volleyball, hockey. The theoretical perfect-facet is the same; only the sport context differs. Tim Duncan's Character translates to Derek Jeter's Character translates to Roger Federer's Character — same standard, different sport. Kobe's Mindset translates to Tom Brady's Mindset translates to Tiger Woods's Mindset — same theoretical 10.</p>

  <div class="callout moss">
    <b>Living document.</b> When the V5 algorithm produces a score that surprises us — and the surprise is informative, not noise — this section, the canonical Tab 19, and the standalone design doc all update together. Strategy + tactics always aligned. The full design doc with per-facet evidence ladders, 8 canonical phenom cases across sports, and 16 cross-sport test cases lives at <a href="/v5-algorithm" style="color:var(--gold);text-decoration:underline">/v5-algorithm</a>.
  </div>
</section>
'''


# ═══ STEP 1: backup all files ═══
print("STEP 1 · backups")
shutil.copy(CANON, CANON.with_suffix('.html.pre-v5algo-tab.bak'))
print(f"  canonical backed up · {CANON.stat().st_size:,} B")
shutil.copy(METHOD, METHOD.with_suffix('.html.pre-v5algo-section.bak'))
print(f"  methodology backed up · {METHOD.stat().st_size:,} B")


# ═══ STEP 2: canonical tab 19 nav button ═══
print("\nSTEP 2 · canonical tab nav button (Tab 19 V5 Algorithm)")
c = CANON.read_text()
old_tabs = '''    <button class="tab" data-pane="moat"><span class="num">18</span>MOAT · Tenet 40</button>
  </div>
</nav>'''
new_tabs = '''    <button class="tab" data-pane="moat"><span class="num">18</span>MOAT · Tenet 40</button>
    <button class="tab" data-pane="v5algo"><span class="num">19</span>V5 Algorithm</button>
  </div>
</nav>'''
if old_tabs not in c:
    print("  FAIL: tab nav anchor missing (canonical may already have v5algo tab, or structure changed)")
    sys.exit(1)
if 'data-pane="v5algo"' in c:
    print("  SKIP: v5algo tab already present in canonical (idempotent)")
else:
    c = c.replace(old_tabs, new_tabs, 1)
    print("  ✓ Tab 19 V5 Algorithm button inserted in nav")


# ═══ STEP 3: canonical pane 19 (after MOAT pane close, before footer) ═══
print("\nSTEP 3 · canonical pane 19 content")
moat_pane_close = '''  </div>
</section>

<footer class="ftr">'''
if moat_pane_close not in c:
    print("  FAIL: MOAT pane close anchor not found")
    sys.exit(1)
if 'id="pane-v5algo"' in c:
    print("  SKIP: v5algo pane already present in canonical (idempotent)")
else:
    c = c.replace(moat_pane_close, '  </div>\n</section>\n' + CANON_PANE + '\n<footer class="ftr">', 1)
    print(f"  ✓ pane-v5algo inserted ({len(CANON_PANE):,} chars)")
CANON.write_text(c)
print(f"  canonical now · {CANON.stat().st_size:,} B")


# ═══ STEP 4: methodology TOC entry ═══
print("\nSTEP 4 · methodology TOC entry")
m = METHOD.read_text()
old_toc = '''    <a href="#principles">09 · 6 constraints, unchanged</a>
  </div>
</nav>'''
new_toc = '''    <a href="#principles">09 · 6 constraints, unchanged</a>
    <a href="#v5algo">10 · V5 Algorithm</a>
  </div>
</nav>'''
if old_toc not in m:
    print("  FAIL: methodology TOC anchor missing")
    sys.exit(1)
if '#v5algo' in m:
    print("  SKIP: v5algo TOC entry already present (idempotent)")
else:
    m = m.replace(old_toc, new_toc, 1)
    print("  ✓ TOC entry 10 V5 Algorithm inserted")


# ═══ STEP 5: methodology section (insert AFTER principles </section>, BEFORE CTA) ═══
print("\nSTEP 5 · methodology section content")
# Principles is section 09. We anchor on its closing </section> followed by the CTA opening.
anchor_principles_to_cta = '''</section>


<div class="cta">'''
if anchor_principles_to_cta not in m:
    # try with single blank line
    anchor_principles_to_cta = '''</section>

<div class="cta">'''
if anchor_principles_to_cta not in m:
    print("  FAIL: methodology principles-to-CTA anchor not found")
    print("       expected '</section>' followed by '<div class=\"cta\">'")
    sys.exit(1)
if 'id="v5algo"' in m:
    print("  SKIP: v5algo section already in methodology (idempotent)")
else:
    replacement = '</section>\n\n' + METHOD_SECTION + '\n\n<div class="cta">'
    m = m.replace(anchor_principles_to_cta, replacement, 1)
    print(f"  ✓ section #v5algo inserted before CTA ({len(METHOD_SECTION):,} chars)")
METHOD.write_text(m)
print(f"  methodology now · {METHOD.stat().st_size:,} B")


# ═══ STEP 6: deploy standalone v5-algorithm.html ═══
print("\nSTEP 6 · standalone /v5-algorithm deploy")
shutil.copy(STANDALONE_SRC, STANDALONE_DST)
print(f"  v5-algorithm.html copied · {STANDALONE_DST.stat().st_size:,} B")


# ═══ STEP 7: _redirects update ═══
print("\nSTEP 7 · _redirects route /v5-algorithm")
if REDIRECTS.exists():
    r = REDIRECTS.read_text()
    if '/v5-algorithm' in r and '/v5-algorithm.html' in r:
        print("  SKIP: /v5-algorithm route already in _redirects (idempotent)")
    else:
        # insert at top so it matches before /* fallback
        new_line = '/v5-algorithm  /v5-algorithm.html  200\n'
        r_new = new_line + r
        REDIRECTS.write_text(r_new)
        print(f"  ✓ /v5-algorithm route added to top of _redirects")
else:
    REDIRECTS.write_text('/v5-algorithm  /v5-algorithm.html  200\n/*  /index.html  200\n')
    print(f"  ✓ _redirects created with /v5-algorithm route")


# ═══ STEP 8: verification ═══
print("\nSTEP 8 · grep-verify all 3 surfaces")
c_now = CANON.read_text()
m_now = METHOD.read_text()
checks = [
    ('canonical tab', 'data-pane="v5algo"' in c_now),
    ('canonical pane', 'id="pane-v5algo"' in c_now),
    ('canonical philosophy', '10 is the only ceiling' in c_now),
    ('canonical phenom REQ 1', 'Pro-tier evidence at sub-pro age' in c_now),
    ('canonical test corpus', 'Stokes' in c_now and 'Mahomes' in c_now),
    ('methodology TOC', '#v5algo' in m_now),
    ('methodology section', 'id="v5algo"' in m_now),
    ('methodology philosophy', '10 is the only ceiling' in m_now),
    ('methodology phenom', 'phenom doctrine' in m_now.lower() or 'phenom' in m_now.lower()),
    ('methodology living doc', 'Living document' in m_now),
    ('standalone file', STANDALONE_DST.exists() and STANDALONE_DST.stat().st_size > 30000),
    ('redirects route', '/v5-algorithm' in REDIRECTS.read_text()),
]
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok:
        all_ok = False

if not all_ok:
    print("\n  WARN: some checks failed — review before deploy-dev")
    sys.exit(1)

print("\n═══ V5 ALGORITHM INTEGRATION COMPLETE ═══")
print(f"  Canonical · Tab 19 V5 Algorithm   · {CANON.stat().st_size:,} B")
print(f"  Methodology · Section 10           · {METHOD.stat().st_size:,} B")
print(f"  Standalone · v5-algorithm.html     · {STANDALONE_DST.stat().st_size:,} B")
print(f"  _redirects · /v5-algorithm route   · added")
print(f"\nBackups:")
print(f"  FC_CANONICAL_STATE_V1.html.pre-v5algo-tab.bak")
print(f"  METHODOLOGY_V17_V1.html.pre-v5algo-section.bak")
print(f"\nNEXT: ./fc-deploy-dev.sh")
print(f"      Verify dev: /v5-algorithm · methodology · canonical Tab 19")
print(f"      If clean, ./fc-promote-prod.sh")
print(f"      Then V5 v2 worker patch (V022.34-V5) with battery against 16 test cases")
