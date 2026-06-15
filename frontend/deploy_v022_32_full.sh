#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# V022.32 → V022.32-Q FULL DEPLOY · single source of truth
# ═══════════════════════════════════════════════════════════════════════════
#
# What this does, in order:
#   1. DIAGNOSE · why Steph=9.6 / Caitlin=9.05 (capture raw signals)
#   2. APPLY Patch Q · fixes the misclassification (added to V022.32 patches)
#   3. VALIDATE · node syntax check
#   4. CACHE NUKE · v022.30 / v022.31 / v022.32 slug-unknown keys
#   5. DEPLOY · dev only
#   6. SMOKE · 8 anchor athletes against new caps
#   7. CANONICAL · inject moat extensions section into FC_CANONICAL_STATE_V1.html
#
# Usage:
#   cd ~/Desktop/fieldcheck-proxy
#   cp ~/Downloads/deploy_v022_32_full.sh .
#   chmod +x deploy_v022_32_full.sh
#   ./deploy_v022_32_full.sh diagnose       # step 1 only · paste output before continuing
#   ./deploy_v022_32_full.sh patch          # steps 2-3 · apply Patch Q + validate
#   ./deploy_v022_32_full.sh deploy         # steps 4-5 · cache nuke + dev deploy
#   ./deploy_v022_32_full.sh smoke          # step 6 · validate the 8 anchors
#   ./deploy_v022_32_full.sh canonical      # step 7 · update canonical with moat
#   ./deploy_v022_32_full.sh all            # runs 2-7 sequentially (skip diagnose)
#
# Author note: This was my mistake — deploy commands were scattered across
# the runbook + individual patch headers. Consolidating into ONE script.
# ═══════════════════════════════════════════════════════════════════════════

set -u
cd ~/Desktop/fieldcheck-proxy || { echo "ERROR: cd to fieldcheck-proxy failed"; exit 1; }

DEV_WORKER="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
SUBCOMMAND="${1:-help}"


# ─── DIAGNOSE ───────────────────────────────────────────────────────────────
diagnose_steph_caitlin() {
  echo "═══════════════════════════════════════════════════════════════════════"
  echo " DIAGNOSTIC · why is Steph at 9.6 and Caitlin at 9.05?"
  echo "═══════════════════════════════════════════════════════════════════════"
  echo ""

  for ATHLETE in "Stephen Curry|" "Caitlin Clark|"; do
    NAME=$(echo "$ATHLETE" | cut -d'|' -f1)
    SCHOOL=$(echo "$ATHLETE" | cut -d'|' -f2)
    echo "═══════ $NAME ═══════"
    curl -sS --max-time 180 -X POST -H "Content-Type: application/json" \
      -d "{\"name\":\"$NAME\",\"sport\":\"mens-basketball\",\"schoolHint\":\"$SCHOOL\",\"skipCache\":true}" \
      "${DEV_WORKER}/verdict/player" \
      | python3 -c "
import json, sys
d = json.load(sys.stdin)
cv = d.get('composite_v022_31') or {}
enc = d.get('encyclopedia') or {}
ident = (enc.get('facts') or {}).get('identity') or {}
sources = d.get('sources') or {}
wd = sources.get('wikidata') or {}
bbref = sources.get('bbref_pro') or {}
print(f'  composite:                 {d.get(\"composite\")}')
print(f'  cv.raw:                    {cv.get(\"raw\")}')
print(f'  cv.cap:                    {cv.get(\"cap\")}     ← this is the cap applied')
print(f'  cv.tier:                   {cv.get(\"tier\")}')
print(f'  cv.stage:                  {cv.get(\"stage\")}   ← this drives the cap')
print(f'  cv.cap_applied:            {cv.get(\"cap_applied\")}')
print(f'  career_stage:              {ident.get(\"career_stage\")}')
print(f'  career_stage_signals:      {ident.get(\"career_stage_signals\")}    ← this tells us which cascade entry fired')
print(f'  career_peak:               {ident.get(\"career_peak\")}')
print(f'  wikidata.has_hall_of_fame: {wd.get(\"has_hall_of_fame\")}')
print(f'  wikidata.has_major_award:  {wd.get(\"has_major_award\")}')
print(f'  bbref_pro.ok:              {bbref.get(\"ok\")}')
print(f'  bbref isHOF:               {bbref.get(\"isHOF\")}')
print()
"
  done

  echo "═══════════════════════════════════════════════════════════════════════"
  echo " WHAT TO LOOK FOR:"
  echo "═══════════════════════════════════════════════════════════════════════"
  echo " 1. If cv.stage = 'retired_pro' for Steph → bug: he's active, hasTextHOF likely tripped"
  echo " 2. If cv.cap = 9.6 → confirms retired_pro misclassification"
  echo " 3. career_stage_signals shows which cascade entry fired:"
  echo "    - 'pro+college_keyword' → fell to early_pro (cap 7.9)"
  echo "    - 'prime_pro+college_keyword+multi_mvp_or_champ' → Patch N3 worked"
  echo "    - 'legend+pro_keyword' → isLegendSig path · hasTextHOF tripped"
  echo "    - 'retired+pro' (or similar) → isRetiredSig fired wrongly"
  echo ""
}


# ─── APPLY PATCH Q ──────────────────────────────────────────────────────────
apply_patch_q() {
  echo "═══════════════════════════════════════════════════════════════════════"
  echo " PATCH Q · 4 fixes for Steph/Caitlin misclassification"
  echo "═══════════════════════════════════════════════════════════════════════"

  python3 << 'PYEOF'
import sys, shutil
from pathlib import Path

WORKER = Path("worker.js")
BACKUP = Path("worker.js.pre-V022.32-Q.bak")
if not WORKER.exists():
    print("ERROR: worker.js not found"); sys.exit(1)
shutil.copy2(WORKER, BACKUP)
print(f"✓ Backed up to {BACKUP}")

src = WORKER.read_text()
orig_len = len(src)
applied = 0

def apply(label, old, new):
    global src, applied
    c = src.count(old)
    if c == 0:
        print(f"✗ {label} · OLD NOT FOUND")
        print(f"   tried: {old[:120]}...")
        sys.exit(2)
    if c > 1:
        print(f"✗ {label} · {c} matches AMBIGUOUS"); sys.exit(2)
    src = src.replace(old, new)
    applied += 1
    print(f"✓ {label} (Δ {len(new)-len(old):+d})")


# ─── Q1 · hasPrimeProSig OUTRANKS legend/retired check
#       Before: isLegendSig && isProSig && isLegendValidated → legend_pro
#       After: same check, BUT if hasPrimeProSig AND NOT retired AND NOT inducted → prime_pro
#
#       The bug: Steph projects HOF, text says "future Hall of Famer" → hasTextHOF=true
#       → isLegendValidated=true → isLegendSig→ legend_pro (cap 9.7) WRONG, he's ACTIVE.
#       Fix: Require ACTUAL retirement signal (date + structured) before going legend_pro.

PATCH_Q1_OLD = """      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""

PATCH_Q1_NEW = """      // V022.32 · PATCH Q1 · ACTIVE multi-MVP outranks projected-HOF text.
      // Bug: Steph projects to HOF; text says "future Hall of Famer" → hasTextHOF=true →
      // isLegendValidated=true → fell into legend_pro at 9.6+ cap. He's ACTIVE, should be prime_pro.
      // Fix: hasPrimeProSig (multi-MVP/champion) PLUS no explicit retirement-confirmed = prime_pro.
      const _v22_32_q_explicitlyRetired = isRetiredSig && /(?:retired|former)\\s+(?:nba|wnba|nfl|mlb)\\s+(?:player|star|champion|mvp)/i.test(allText);
      if (hasPrimeProSig && isProSig && !_v22_32_q_explicitlyRetired && !bbrefIsHOF) {
        stage = 'prime_pro';
        stageSignals.push('q1_prime_pro_overrides_text_hof_projection');
      }
      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated && _v22_32_q_explicitlyRetired) {"""

apply("Q1_active_multi_MVP_outranks_projected_HOF", PATCH_Q1_OLD, PATCH_Q1_NEW)


# ─── Q2 · Tighten hasTextHOF to REQUIRE inducted/enshrined verbs
#       Current regex matches "hall of fame inductee" but ALSO matches "hall of fame conversations"
#       (since "conversations" doesn't anchor to "inductee"). Tighten the alternation.

PATCH_Q2_OLD = """      const hasTextHOF = /\\b(naismith memorial basketball hall of fame|naismith hall of fame|nba hall of fame|wnba hall of fame|nfl hall of fame|pro football hall of fame|baseball hall of fame|cooperstown|hall of fame inductee|hof inductee|inducted into the [a-z ]{0,30} hall of fame|inducted into the basketball hall of fame|enshrined in the [a-z ]{0,30} hall of fame|first[- ]ballot hall of famer)\\b/i.test(allText);"""

PATCH_Q2_NEW = """      // V022.32 · PATCH Q2 · TIGHTENED hasTextHOF regex.
      // Previous regex matched "hall of fame inductee" via fuzzy boundary.
      // Tightened: require explicit INDUCTION verbs (inducted/enshrined/elected/installed)
      // OR specific institution names ("Naismith Memorial Basketball Hall of Fame", "Cooperstown").
      // Projected-HOF language ("future Hall of Famer", "hall of fame conversations") MUST NOT MATCH.
      const hasTextHOF = /\\b(naismith memorial basketball hall of fame|naismith memorial basketball hall|naismith basketball hall of fame|baseball hall of fame at cooperstown|inducted into the (?:basketball|football|baseball|naismith|pro football) hall of fame|enshrined in the (?:basketball|football|baseball|naismith|pro football) hall of fame|elected to the (?:basketball|football|baseball|naismith|pro football) hall of fame|hall of fame class of (?:19|20)\\d{2}|hall of fame inductee[,. ]|hof inductee[,. ])\\b/i.test(allText);"""

apply("Q2_tighten_hasTextHOF_require_induction", PATCH_Q2_OLD, PATCH_Q2_NEW)


# ─── Q3 · Caitlin Clark · she's WNBA early-pro · should cap at 7.9
#       The bug: Caitlin at 9.05 means she's hitting prime_pro cap 9.3 via hasPrimeProSig.
#       BUT she's a rookie/2nd year — multi-MVP / multi-champion language doesn't apply YET.
#       The text might say "MVP" referring to college Wooden Award or HS state MVP.
#       Tighten hasPrimeProSig: require WNBA/NBA prefix on MVP/champion mentions.

PATCH_Q3_OLD = """      const hasPrimeProSig = /\\b(2[ -]?time mvp|2x mvp|two[ -]?time mvp|three[ -]?time mvp|3[ -]?time mvp|3x mvp|four[ -]?time mvp|4x mvp|five[ -]?time mvp|5x mvp|2[ -]?time (?:nba |wnba |nfl )?champion|2x (?:nba |wnba |nfl )?champion|three[ -]?time (?:nba |wnba |nfl )?champion|3[ -]?time (?:nba |wnba |nfl )?champion|3x (?:nba |wnba |nfl )?champion|four[ -]?time (?:nba |wnba |nfl )?champion|4x (?:nba |wnba |nfl )?champion|five[ -]?time (?:nba |wnba |nfl )?champion|5[ -]?time (?:nba |wnba |nfl )?champion|6[ -]?time (?:nba |wnba |nfl )?champion|seven[ -]?time (?:nba |wnba |nfl )?champion|[2-9][ -]?time all[- ]star|multi[- ]time all[- ]star|all-nba first team|first[- ]team all-nba|defensive player of the year|finals mvp|kia mvp|nba mvp|wnba mvp|nfl mvp|league mvp|world series mvp|cy young|silver slugger)\\b/i.test(allText);"""

PATCH_Q3_NEW = """      // V022.32 · PATCH Q3 · TIGHTENED hasPrimeProSig regex.
      // Bug: Caitlin Clark hit prime_pro cap 9.3 because text mentioned "MVP" (Wooden Award college MVP).
      // Tightened: ALL MVP/champion matches REQUIRE NBA/WNBA/NFL/MLB prefix or equivalent pro-context.
      // College MVPs (Wooden/Naismith Player of the Year) MUST NOT match.
      const hasPrimeProSig = /\\b(?:2[ -]?time (?:nba|wnba|nfl|mlb) mvp|2x (?:nba|wnba|nfl|mlb) mvp|two[ -]?time (?:nba|wnba|nfl|mlb) mvp|three[ -]?time (?:nba|wnba|nfl|mlb) mvp|3[ -]?time (?:nba|wnba|nfl|mlb) mvp|3x (?:nba|wnba|nfl|mlb) mvp|four[ -]?time (?:nba|wnba|nfl|mlb) mvp|4x (?:nba|wnba|nfl|mlb) mvp|five[ -]?time (?:nba|wnba|nfl|mlb) mvp|5x (?:nba|wnba|nfl|mlb) mvp|2[ -]?time (?:nba|wnba|nfl|mlb) champion|2x (?:nba|wnba|nfl|mlb) champion|three[ -]?time (?:nba|wnba|nfl|mlb) champion|3[ -]?time (?:nba|wnba|nfl|mlb) champion|3x (?:nba|wnba|nfl|mlb) champion|four[ -]?time (?:nba|wnba|nfl|mlb) champion|4x (?:nba|wnba|nfl|mlb) champion|five[ -]?time (?:nba|wnba|nfl|mlb) champion|5[ -]?time (?:nba|wnba|nfl|mlb) champion|6[ -]?time (?:nba|wnba|nfl|mlb) champion|[2-9][ -]?time (?:nba|wnba|nfl|mlb) all[- ]star|multi[- ]time (?:nba|wnba|nfl) all[- ]star|all-nba first team|first[- ]team all-nba|all-wnba first team|first[- ]team all-wnba|nba defensive player of the year|wnba defensive player of the year|nba finals mvp|wnba finals mvp|wnba mvp|kia (?:nba|wnba) mvp|nba mvp award|wnba mvp award|world series mvp|cy young award winner)\\b/i.test(allText);"""

apply("Q3_tighten_hasPrimeProSig_require_pro_prefix", PATCH_Q3_OLD, PATCH_Q3_NEW)


# ─── Q4 · Version banner bump + cacheVersion bump
PATCH_Q4A_OLD = """// FIELDCHECK_WORKER_VERSION = V022.32 · CALIBRATION · TENET 46 V4 universe-blind scale · 3-patch bundle: REF table (HS 3.5/D1 6.2/Pro 7.7, sigma 0.7) + synthesis Haiku V4 anchor + brutal_honest V4 anchor · cacheVersion v022.32 · base V022.31"""

PATCH_Q4A_NEW = """// FIELDCHECK_WORKER_VERSION = V022.32-Q · CALIBRATION + Q-PATCH · prime_pro overrides projected-HOF (Steph fix) + tightened hasTextHOF (induction-required) + tightened hasPrimeProSig (pro-prefix required) (Caitlin fix) · base V022.32"""

apply("Q4A_version_banner_bump", PATCH_Q4A_OLD, PATCH_Q4A_NEW)


PATCH_Q4B_OLD = """          const cacheVersion = 'v022.32';  // V022.32 CALIBRATION · invalidates v022.31 synthesis cache (V4 anchor changes synthesis output)"""

PATCH_Q4B_NEW = """          const cacheVersion = 'v022.32q'; // V022.32-Q · invalidates v022.32 synthesis cache (Q patches change stage detection)"""

apply("Q4B_cacheVersion_bump_to_q", PATCH_Q4B_OLD, PATCH_Q4B_NEW)


WORKER.write_text(src)
print(f"\n✓ Patch Q applied · {applied} patches · Δ +{len(src)-orig_len:,} chars")
PYEOF
}


# ─── VALIDATE ───────────────────────────────────────────────────────────────
validate() {
  echo "═══ JS SYNTAX CHECK ═══"
  node --check worker.js && echo "✓ JS OK" || { echo "✗ JS SYNTAX FAILED"; exit 2; }
}


# ─── CACHE NUKE ─────────────────────────────────────────────────────────────
cache_nuke() {
  echo "═══ CACHE NUKE · all stale unknown-slug keys ═══"
  for v in v022.30 v022.31 v022.32; do
    for k in synth projection prostack trajpath coachvoices audience; do
      wrangler kv key delete --binding=FIELDCHECK_KV --remote \
        "${k}:${v}:mens-basketball:unknown" 2>&1 | tail -1
    done
  done
  echo "✓ Cache cleared"
}


# ─── DEPLOY ─────────────────────────────────────────────────────────────────
deploy() {
  echo "═══ DEPLOY TO DEV ═══"
  ./fc-deploy-dev.sh
}


# ─── SMOKE ──────────────────────────────────────────────────────────────────
smoke_8_anchors() {
  echo "═══════════════════════════════════════════════════════════════════════"
  echo " SMOKE TEST · 8 calibration anchors (post-Patch Q)"
  echo "═══════════════════════════════════════════════════════════════════════"

  declare -a ATHLETES=(
    "Tyran Stokes|Notre Dame HS|hs|prep_amateur|≤5.4"
    "Saniyah Hall|Montverde Academy|hs|prep_amateur|≤5.4"
    "Cameron Boozer|Duke|d1|college_amateur|≤7.4"
    "Cooper Flagg|Duke|pro|early_pro|≤7.9"
    "Caitlin Clark||pro|early_pro or prime_pro|7.5-8.5"
    "Stephen Curry||pro|prime_pro|≤9.3"
    "Tim Duncan||pro|legend_pro or retired_pro|9.6-9.7"
    "Michael Jordan||pro|legend_pro|9.7-9.9"
  )

  for ENTRY in "${ATHLETES[@]}"; do
    IFS='|' read -r NAME SCHOOL TIER_EXPECT STAGE_EXPECT COMP_EXPECT <<< "$ENTRY"
    echo "═══════ $NAME (want: tier=$TIER_EXPECT · stage=$STAGE_EXPECT · composite=$COMP_EXPECT) ═══════"
    curl -sS --max-time 180 -X POST -H "Content-Type: application/json" \
      -d "{\"name\":\"$NAME\",\"sport\":\"mens-basketball\",\"schoolHint\":\"$SCHOOL\",\"skipCache\":true}" \
      "${DEV_WORKER}/verdict/player" \
      | python3 -c "
import json, sys
d = json.load(sys.stdin)
cv = d.get('composite_v022_31') or {}
print(f'  composite:    {d.get(\"composite\")}  raw: {cv.get(\"raw\")}  cap: {cv.get(\"cap\")}  tier: {cv.get(\"tier\")}  stage: {cv.get(\"stage\")}')
"
  done
}


# ─── CANONICAL · INJECT MOAT EXTENSIONS SECTION ─────────────────────────────
inject_moat_into_canonical() {
  echo "═══════════════════════════════════════════════════════════════════════"
  echo " CANONICAL UPDATE · inject moat extensions section into FC_CANONICAL_STATE_V1.html"
  echo "═══════════════════════════════════════════════════════════════════════"

  if [ ! -f "FC_CANONICAL_STATE_V1.html" ]; then
    echo "✗ FC_CANONICAL_STATE_V1.html not found"
    return 1
  fi

  cp FC_CANONICAL_STATE_V1.html FC_CANONICAL_STATE_V1.html.pre-V5.25.bak

  python3 << 'PYEOF'
from pathlib import Path
import sys

canonical = Path("FC_CANONICAL_STATE_V1.html")
src = canonical.read_text()

# Bump V-stamp V5.24 → V5.25
src = src.replace("V5.24", "V5.25", 1)
# Reflect Q patch
src = src.replace("V022.32", "V022.32-Q")  # may match multiple; intentional

# Build the moat extensions section
moat_section = '''
<!-- ═══════════════════════════════════════════════════════════════════════
     V5.25 · MOAT EXTENSIONS ROADMAP (Player Thesis Layer)
     ═══════════════════════════════════════════════════════════════════════
     Added: V022.32-Q ship cycle · 8 extensions identified, 5 built and staged.
     Strategic master doc: MOAT_STRATEGY_MASTER.html
-->
<section id="moat-extensions" style="margin: 32px 0; padding: 24px; background: #161412; border: 1px solid #2A2522; border-radius: 8px;">
  <h2 style="color: #FFC56B; margin-top: 0;">MOAT EXTENSIONS · The Player-Thesis Layer</h2>
  <p style="color: #9D928A; font-size: 13px;">
    Strategic articulation: <strong style="color: #FF5C3A;">"Every existing service tells you what an athlete IS right now. FieldCheck tells you what they could become — and shows the asymmetry public sources missed."</strong>
  </p>

  <h3 style="color: #FF9985;">The three structural failures of the amateur sports market</h3>
  <ol style="color: #F5F1E8;">
    <li><strong>Misaligned customers</strong> · 247Sports/Rivals/On3/ESPN paid by recruiters, not athletes. Athlete is the PRODUCT.</li>
    <li><strong>Description without interpretation</strong> · MaxPreps/Hudl/PerfectGame describe, never interpret against pro projection.</li>
    <li><strong>The 8 facets that matter aren't measured</strong> · character/mindset/coachability/mental_strength absent from public services.</li>
  </ol>

  <h3 style="color: #FF9985;">FieldCheck whitespaces (the moat)</h3>
  <ul style="color: #F5F1E8;">
    <li>Multi-source synthesis with calibrated trust scores (14-adapter scout dossier) · <em>BUILT</em></li>
    <li>8-facet pro-projection framework applied to amateurs (canonical_facets_8) · <em>BUILT</em></li>
    <li>Universe-blind calibration Tenet 46 V4 (single 0-10 scale, gender/age/sport blind) · <em>SHIPPED V022.32</em></li>
  </ul>

  <h3 style="color: #FF9985;">8 moat extensions (priority order)</h3>
  <table style="width: 100%; border-collapse: collapse; color: #F5F1E8; font-size: 13px; margin: 12px 0;">
    <thead><tr style="background: #1F1C1A; color: #FF9985;"><th style="padding: 8px; text-align: left;">#</th><th style="padding: 8px; text-align: left;">Extension</th><th style="padding: 8px; text-align: left;">Status</th><th style="padding: 8px;">Complexity</th></tr></thead>
    <tbody>
      <tr><td style="padding: 6px;">1</td><td>Competition-strength adjustment (opponent quality factor)</td><td style="color: #7AC74F;">Patch built · staged</td><td style="text-align: center;">LOW · 4-6h</td></tr>
      <tr><td style="padding: 6px;">2</td><td>Source-level transparency module ("Show Our Work")</td><td style="color: #FFC56B;">UI built · integration pending</td><td style="text-align: center;">MED · 8-12h</td></tr>
      <tr><td style="padding: 6px;">3</td><td>Historical analog matching (the flagship · "future you" mirror)</td><td style="color: #FFC56B;">Spec + UI built · dataset 15-25h</td><td style="text-align: center;">HIGH</td></tr>
      <tr><td style="padding: 6px;">4</td><td>Quantitative trajectory projection (5 snapshots over 60 months)</td><td style="color: #7AC74F;">Patch built · staged</td><td style="text-align: center;">LOW · 4-6h</td></tr>
      <tr><td style="padding: 6px;">5</td><td>Position-pool refinement (system-aware)</td><td style="color: #9D928A;">Spec only</td><td style="text-align: center;">MED · 6-10h</td></tr>
      <tr><td style="padding: 6px;">6</td><td>Evidence anchors surfaced (verification-of-truth)</td><td style="color: #9D928A;">Spec only</td><td style="text-align: center;">MED · 6-8h</td></tr>
      <tr><td style="padding: 6px;">7</td><td>Decision-moment framing (4-persona refinement)</td><td style="color: #9D928A;">Spec only</td><td style="text-align: center;">LOW · 3-5h</td></tr>
      <tr><td style="padding: 6px;">8</td><td>Longitudinal record (trust flywheel)</td><td style="color: #9D928A;">Spec only · ongoing</td><td style="text-align: center;">HIGH · 10-15h+</td></tr>
    </tbody>
  </table>

  <h3 style="color: #FF9985;">Build sequencing</h3>
  <ul style="color: #F5F1E8;">
    <li><strong style="color: #FFC56B;">Days 1-7:</strong> Ext 1 (competition strength) + Ext 4 (trajectory projection) + 110-battery validation</li>
    <li><strong style="color: #FFC56B;">Days 8-21:</strong> Ext 2 (source transparency UI) + Ext 6 (evidence anchors) + begin Ext 3 dataset</li>
    <li><strong style="color: #FFC56B;">Days 22-45:</strong> Ext 3 (historical analog matching) + Ext 5 (position pool refinement) + Ext 7 (decision moment)</li>
    <li><strong style="color: #FFC56B;">Days 46-90:</strong> Ext 8 (longitudinal record) + scale validation to 500/1000 athletes</li>
  </ul>

  <h3 style="color: #FF9985;">Source files</h3>
  <ul style="color: #6BD4D4; font-family: monospace; font-size: 12px;">
    <li>MOAT_STRATEGY_MASTER.html · the full strategic articulation</li>
    <li>moat_ext1_competition_strength.py · opponent quality factor patch</li>
    <li>moat_ext2_source_transparency.html · "Show Our Work" UI module</li>
    <li>moat_ext3_historical_analog_spec.html · the flagship spec + UI mockup</li>
    <li>moat_ext4_trajectory_projection.py · quantitative trajectory patch</li>
    <li>moat_ext5_trajectory_chart.html · SVG trajectory visualization</li>
  </ul>

  <div style="background: rgba(255, 92, 58, 0.06); border: 1px solid rgba(255, 92, 58, 0.2); padding: 14px 18px; border-radius: 4px; margin-top: 20px; color: #FF9985; font-size: 13px;">
    <strong style="color: #FF5C3A; letter-spacing: 1.5px; text-transform: uppercase; font-size: 10px;">The moat in one paragraph</strong><br>
    FieldCheck is the only honest answer to "what does this player actually project to?" Every existing service gives a partial answer — MaxPreps shows stats, 247 gives stars, On3 gives NIL, Hudl gives film. None synthesize. None honest-anchor. None show busts alongside stars. FieldCheck does all of it: 14-source synthesis, 8-facet projection, universe-blind calibration, brutal-honest interpretation, source-level transparency, historical analog mirrors, quantitative trajectory forecasts. The moat is trust + depth + honesty — built layer by layer, validated at scale, audit-able all the way down. <em>Inflation breaks trust. Honesty IS the moat.</em>
  </div>
</section>
'''

# Inject BEFORE the closing </body> tag (or end of last section if no body close tag)
marker_options = ['</body>', '</main>', '</article>', '<!-- end of canonical -->']
injected = False
for marker in marker_options:
    if marker in src:
        src = src.replace(marker, moat_section + '\n' + marker, 1)
        injected = True
        print(f"✓ Moat section injected before {marker}")
        break

if not injected:
    # Fallback: append to end
    src = src + moat_section
    print("⚠ No </body> found · appended to end of file")

canonical.write_text(src)
print(f"\n✓ Canonical updated · V5.24 → V5.25 · V022.32 → V022.32-Q · moat extensions section added")
print(f"  size: {len(src):,} bytes")
PYEOF
}


# ─── HELP ───────────────────────────────────────────────────────────────────
show_help() {
  cat << 'EOF'
Usage:
  ./deploy_v022_32_full.sh diagnose       # step 1 · Steph/Caitlin signals
  ./deploy_v022_32_full.sh patch          # step 2-3 · apply Patch Q + validate
  ./deploy_v022_32_full.sh deploy         # step 4-5 · cache nuke + dev deploy
  ./deploy_v022_32_full.sh smoke          # step 6 · validate 8 anchors
  ./deploy_v022_32_full.sh canonical      # step 7 · update canonical with moat
  ./deploy_v022_32_full.sh all            # steps 2-7 sequentially

Typical recovery flow (when Steph/Caitlin are wrong):
  1. ./deploy_v022_32_full.sh diagnose          # see WHICH cascade entry fired
  2. ./deploy_v022_32_full.sh patch             # apply Patch Q + validate JS
  3. ./deploy_v022_32_full.sh deploy            # cache nuke + dev deploy
  4. ./deploy_v022_32_full.sh smoke             # validate Steph=9.3, Caitlin=7.5-8.5
  5. ./deploy_v022_32_full.sh canonical         # bump canonical to V5.25 + moat section
EOF
}


# ─── DISPATCH ───────────────────────────────────────────────────────────────
case "$SUBCOMMAND" in
  diagnose)     diagnose_steph_caitlin ;;
  patch)        apply_patch_q && validate ;;
  deploy)       cache_nuke && deploy ;;
  smoke)        smoke_8_anchors ;;
  canonical)    inject_moat_into_canonical ;;
  all)
    apply_patch_q && validate
    [ $? -eq 0 ] && cache_nuke && deploy
    [ $? -eq 0 ] && smoke_8_anchors
    [ $? -eq 0 ] && inject_moat_into_canonical
    ;;
  help|--help|-h|*) show_help ;;
esac
