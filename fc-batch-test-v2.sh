#!/usr/bin/env bash
# ═════════════════════════════════════════════════════════════════════════════
# fc-batch-test-v2.sh · V022.30 · 110-athlete battery · POST endpoint version
# ═════════════════════════════════════════════════════════════════════════════
# v2 changes vs v1:
#   - Uses POST /verdict/player with JSON body (correct endpoint shape)
#   - Sends {name, sport, schoolHint, skipCache:true} - matches worker contract
#   - Richer HTML report: brutal_honest per athlete + adapter coverage matrix
#     + decision_grade_read for Player/Coach/Scout/Parent visible per athlete
#   - Surfaces ADAPTER FAILURE gaps explicitly (which sources failed for which
#     athletes → tells us where to invest in V022.31+)
#   - All four personas visible inline so Sridhar can scan-review
# ═════════════════════════════════════════════════════════════════════════════

set -euo pipefail

BASE_URL="${FC_BASE_URL:-https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev}"
ROSTER_FILE="${FC_ROSTER:-./roster_100.json}"
RESULTS_DIR="${FC_RESULTS_DIR:-./fc-batch-test-results-v2}"
REPORT_FILE="${FC_REPORT:-./fc-batch-test-report-v2.html}"
TIMEOUT_SECONDS="${FC_TIMEOUT:-180}"
PARALLEL_JOBS="${FC_PARALLEL:-3}"

if [ ! -f "$ROSTER_FILE" ]; then
  for candidate in \
    "$HOME/Desktop/fieldcheck-proxy/roster_100.json" \
    "$HOME/Downloads/roster_100.json" \
    "/home/claude/v022.30/roster/roster_100.json" \
    "/mnt/user-data/outputs/roster_100.json"; do
    if [ -f "$candidate" ]; then ROSTER_FILE="$candidate"; break; fi
  done
fi

if [ ! -f "$ROSTER_FILE" ]; then
  echo "ERROR: roster_100.json not found. Set FC_ROSTER or place in workspace." >&2
  exit 1
fi

mkdir -p "$RESULTS_DIR"

echo "▸ FieldCheck V022.30 batch test harness · v2 · POST endpoint"
echo "▸ BASE_URL    = $BASE_URL"
echo "▸ ENDPOINT    = POST /verdict/player"
echo "▸ ROSTER      = $ROSTER_FILE"
echo "▸ RESULTS     = $RESULTS_DIR"
echo "▸ REPORT      = $REPORT_FILE"
echo "▸ PARALLEL    = $PARALLEL_JOBS jobs · timeout ${TIMEOUT_SECONDS}s per athlete"
echo ""

# ── EXTRACT ATHLETE LIST ──────────────────────────────────────────────────────
EXTRACT_SCRIPT=$(cat <<'PYEOF'
import json, sys, re
with open(sys.argv[1]) as f: d = json.load(f)
for bucket in d.get('buckets', []):
    bid = bucket['bucket_id']
    for ath in bucket.get('athletes', []):
        name = ath.get('name', '')
        sport = ath.get('sport') or bucket.get('sport') or 'mens-basketball'
        school = ath.get('school', '')
        safe = re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')[:40]
        print('\t'.join((bid, name, sport, school, safe)))
PYEOF
)

ATHLETES=$(python3 -c "$EXTRACT_SCRIPT" "$ROSTER_FILE")
TOTAL=$(echo "$ATHLETES" | wc -l | tr -d ' ')
echo "▸ TOTAL ATHLETES = $TOTAL"
echo ""

# ── FETCH FUNCTION · POST /verdict/player ─────────────────────────────────────
fetch_athlete() {
  local bid="$1" name="$2" sport="$3" school="$4" safe="$5"
  local outfile="$RESULTS_DIR/${bid}__${safe}.json"
  local url="${BASE_URL}/verdict/player"

  # Build JSON body using python (handles escaping reliably)
  local body
  body=$(python3 -c "
import json, sys
b = {'name': sys.argv[1], 'sport': sys.argv[2], 'skipCache': True}
hint = sys.argv[3].strip()
# Don't send schoolHint for placeholder/adversarial cases
if hint and hint.lower() not in ('varies', 'unknown', 'common name test', '') and not hint.lower().startswith('adversarial'):
    b['schoolHint'] = hint
print(json.dumps(b))
" "$name" "$sport" "$school")

  local t0 t1
  t0=$(date +%s)
  local http_code
  http_code=$(curl -sS -w "%{http_code}" -o "$outfile" --max-time "$TIMEOUT_SECONDS" \
    -X POST -H "Content-Type: application/json" \
    -d "$body" \
    "$url" 2>/dev/null || echo "TIMEOUT")
  t1=$(date +%s)
  local elapsed=$((t1 - t0))
  printf "  [%s] %-32s %3ss  http=%s\n" "$bid" "${name:0:32}" "$elapsed" "$http_code"

  python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f: d = json.load(f)
except Exception:
    d = {'_raw_load_error': True}
if not isinstance(d, dict): d = {'_non_object_response': True, '_value': d}
d['_batch_meta'] = {'bucket_id': sys.argv[2], 'name': sys.argv[3], 'sport': sys.argv[4], 'school': sys.argv[5], 'http': sys.argv[6], 'elapsed_s': int(sys.argv[7])}
with open(sys.argv[1], 'w') as f: json.dump(d, f)
" "$outfile" "$bid" "$name" "$sport" "$school" "$http_code" "$elapsed" 2>/dev/null || true
}

export -f fetch_athlete
export BASE_URL RESULTS_DIR TIMEOUT_SECONDS

# ── RUN BATTERY (parallel, throttled) ─────────────────────────────────────────
START=$(date +%s)
echo "$ATHLETES" | while IFS=$'\t' read -r bid name sport school safe; do
  fetch_athlete "$bid" "$name" "$sport" "$school" "$safe" &
  if [ "$(jobs -r | wc -l)" -ge "$PARALLEL_JOBS" ]; then
    sleep 0.5
  fi
done
wait
END=$(date +%s)
TOTAL_ELAPSED=$((END - START))
echo ""
echo "▸ All requests done in ${TOTAL_ELAPSED}s · generating insights report..."
echo ""

# ── GENERATE INSIGHTS REPORT ──────────────────────────────────────────────────
python3 <<EOF > "$REPORT_FILE"
import json, os, sys, html, re, glob
from collections import Counter, defaultdict

ROSTER = "$ROSTER_FILE"
RESULTS_DIR = "$RESULTS_DIR"

with open(ROSTER) as f: roster = json.load(f)

results = {}
for fp in glob.glob(os.path.join(RESULTS_DIR, "*.json")):
    base = os.path.basename(fp)[:-5]
    try:
        with open(fp) as f: results[base] = json.load(f)
    except Exception as e:
        results[base] = {"_load_error": str(e)}

def safe_name(name): return re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')[:40]

def evaluate_athlete(ath, bucket, response):
    """Returns (status, checks_list, summary_dict)"""
    checks = []
    summary = {
        'composite': None, 'school': None, 'school_source': None,
        'career_stage': None, 'tier': None, 'percentile': None,
        'verdict': None, 'bbref_status': None, 'bh_confidence': None,
        'bh_ok': False, 'sources_succeeded_count': 0, 'sources_failed_count': 0
    }
    if not response or '_raw_load_error' in response or '_load_error' in response:
        return ('SKIP', [{'check': 'response_loadable', 'status': 'fail', 'detail': 'no response JSON'}], summary)
    meta = response.get('_batch_meta', {})
    http = meta.get('http', '?')
    if http != '200':
        return ('SKIP', [{'check': 'http_200', 'status': 'fail', 'detail': f'HTTP {http}'}], summary)

    enc = response.get('encyclopedia') or {}
    facts = enc.get('facts') or {}
    ident = facts.get('identity') or {}
    syn = enc.get('synthesis') or {}
    pp = enc.get('position_pool_benchmark') or {}
    bh = enc.get('brutal_honest') or {}
    sources = ((enc.get('scout_dossier') or {}).get('sources') or {})
    dossier_meta = response.get('scout_dossier_meta') or {}

    summary['composite'] = response.get('composite') or (syn.get('overall_score'))
    summary['school'] = ident.get('current_school')
    summary['school_source'] = ident.get('current_school_source')
    summary['career_stage'] = ident.get('career_stage')
    summary['tier'] = pp.get('tier')
    summary['percentile'] = pp.get('overall_percentile')
    summary['verdict'] = response.get('verdict')
    summary['bh_confidence'] = bh.get('confidence')
    summary['bh_ok'] = bh.get('ok') is True
    summary['sources_succeeded_count'] = len(dossier_meta.get('sources_succeeded') or [])
    summary['sources_failed_count'] = len(dossier_meta.get('sources_failed') or [])

    # bbref status (key signal for Patch A validation)
    bbref = sources.get('bbref_pro') or {}
    if not bbref:
        bbref_meta = next((s for s in (dossier_meta.get('sources_failed') or []) if s.get('source') == 'bbref_pro'), None)
        if bbref_meta:
            summary['bbref_status'] = f"failed: {bbref_meta.get('error', '?')[:30]}"
    elif bbref.get('error') == 'name_mismatch_v022.30':
        summary['bbref_status'] = 'V022.30 rejected (correct for adversarial)'
    elif bbref.get('ok'):
        summary['bbref_status'] = f"ok · validated={bbref.get('identity_validated')} · hof={bbref.get('is_hof')}"
    else:
        summary['bbref_status'] = f"not ok: {bbref.get('error', '?')[:30]}"

    # Litmus checks
    expected_school = (ath.get('school') or '').strip()
    actual_school = summary['school'] or ''
    if expected_school and 'varies' not in expected_school.lower() and 'common name' not in expected_school.lower() and 'adversarial' not in expected_school.lower() and expected_school != 'unknown':
        # Loose match: tokens
        exp_tokens = set(re.findall(r'\w+', expected_school.lower()))
        act_tokens = set(re.findall(r'\w+', actual_school.lower()))
        common = exp_tokens & act_tokens
        if len(common) >= 2 or (len(common) >= 1 and len(exp_tokens) <= 2):
            checks.append({'check': 'school_match', 'status': 'pass', 'detail': f'{actual_school[:40]} matches'})
        elif not actual_school:
            checks.append({'check': 'school_resolved', 'status': 'null', 'detail': f'expected≈{expected_school[:40]} got null'})
        else:
            checks.append({'check': 'school_match', 'status': 'fail', 'detail': f'expected≈{expected_school[:30]} got={actual_school[:30]}'})

    rng = ath.get('expected_composite_range') or [None, None]
    comp = summary['composite']
    if comp is not None and rng[0] is not None and rng[1] is not None:
        if rng[0] <= comp <= rng[1]:
            checks.append({'check': 'composite_band', 'status': 'pass', 'detail': f'in [{rng[0]}-{rng[1]}]'})
        elif abs(comp - rng[0]) <= 0.5 or abs(comp - rng[1]) <= 0.5:
            checks.append({'check': 'composite_band', 'status': 'near', 'detail': f'expected [{rng[0]}-{rng[1]}] got {comp}'})
        else:
            checks.append({'check': 'composite_band', 'status': 'fail', 'detail': f'expected [{rng[0]}-{rng[1]}] got {comp}'})
    elif comp is None and ath.get('expected_band') == 'SPARSE':
        checks.append({'check': 'sparse_null_ok', 'status': 'pass', 'detail': 'null composite correct for SPARSE'})
    elif comp is None:
        checks.append({'check': 'composite_present', 'status': 'null', 'detail': 'composite=null'})

    expected_pool = ath.get('expected_pool') or ''
    if expected_pool and expected_pool != 'varies':
        if summary['tier'] and summary['tier'].lower() == expected_pool.lower():
            checks.append({'check': 'pool_tier', 'status': 'pass', 'detail': f'tier={summary["tier"]}'})
        elif summary['tier']:
            checks.append({'check': 'pool_tier', 'status': 'fail', 'detail': f'expected {expected_pool} got {summary["tier"]}'})

    # legend_pro for amateurs is RED
    cs = (summary['career_stage'] or '').lower()
    if expected_pool in ('hs', 'd1', 'd2', 'd3', 'juco') and cs in ('legend_pro', 'prime_pro', 'retired_pro'):
        checks.append({'check': 'no_legend_pro_for_amateur', 'status': 'fail', 'detail': f'career_stage={cs} for amateur'})
    elif cs:
        checks.append({'check': 'career_stage_set', 'status': 'pass', 'detail': f'={cs}'})

    if summary['bh_ok']:
        checks.append({'check': 'brutal_honest', 'status': 'pass', 'detail': f'conf={summary["bh_confidence"]}'})
    else:
        checks.append({'check': 'brutal_honest', 'status': 'fail', 'detail': 'missing'})

    fails = sum(1 for c in checks if c['status'] == 'fail')
    nears = sum(1 for c in checks if c['status'] in ('near', 'null'))
    if fails == 0 and nears == 0: status = 'GREEN'
    elif fails == 0: status = 'YELLOW'
    else: status = 'RED'
    return (status, checks, summary)

# Build report data
report_rows = []
adapter_failures = Counter()
adapter_successes = Counter()
status_count = Counter()

for bucket in roster['buckets']:
    bid = bucket['bucket_id']
    for ath in bucket['athletes']:
        key = f"{bid}__{safe_name(ath['name'])}"
        resp = results.get(key, {})
        status, checks, summ = evaluate_athlete(ath, bucket, resp)
        enc = (resp.get('encyclopedia') or {})
        bh = enc.get('brutal_honest') or {}
        dossier_meta = resp.get('scout_dossier_meta') or {}
        for s in (dossier_meta.get('sources_failed') or []):
            adapter_failures[s.get('source', '?')] += 1
        for s in (dossier_meta.get('sources_succeeded') or []):
            adapter_successes[s] += 1
        report_rows.append({
            'bucket_id': bid, 'bucket_name': bucket['name'],
            'athlete': ath, 'response_key': key,
            'status': status, 'checks': checks, 'summary': summ,
            'brutal_honest': bh,
        })
        status_count[status] += 1

total = len(report_rows)
green = status_count.get('GREEN', 0); yellow = status_count.get('YELLOW', 0)
red = status_count.get('RED', 0); skip = status_count.get('SKIP', 0)
pct = lambda n: round(100 * n / total) if total else 0

# Adapter coverage analysis
all_adapters = set(adapter_failures.keys()) | set(adapter_successes.keys())
adapter_coverage = []
for a in sorted(all_adapters):
    s = adapter_successes.get(a, 0); f = adapter_failures.get(a, 0)
    pct_ok = round(100 * s / (s + f)) if (s + f) else 0
    adapter_coverage.append({'adapter': a, 'success': s, 'fail': f, 'pct_ok': pct_ok})
adapter_coverage.sort(key=lambda x: x['pct_ok'])

# Emit HTML
print('<!DOCTYPE html><html><head><meta charset="UTF-8"><title>FC V022.30 · Insights Report</title>')
print('<style>')
print('body{font-family:-apple-system,BlinkMacSystemFont,"Inter",sans-serif;background:#07060a;color:#f5f4f0;padding:24px;line-height:1.6}')
print('.wrap{max-width:1400px;margin:0 auto}')
print('h1{font-family:"Fraunces",Georgia,serif;font-size:34px;font-weight:600;letter-spacing:-0.02em;margin-bottom:6px}')
print('h2{font-family:"Fraunces",serif;font-size:22px;color:#d9b44c;margin:32px 0 14px;border-bottom:1px solid #2a2730;padding-bottom:8px}')
print('h3{font-family:"Fraunces",serif;font-size:16px;color:#d9b44c;margin:16px 0 8px}')
print('.subhdr{color:#a8a59c;margin-bottom:18px;font-size:13.5px}')
print('.summary{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:24px}')
print('.summary-card{padding:18px;background:#1a1820;border:1px solid #2a2730;border-radius:8px}')
print('.summary-card .num{font-size:32px;font-weight:600;font-family:"Fraunces",serif}')
print('.summary-card .lbl{color:#a8a59c;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;margin-top:4px}')
print('.summary-card.green .num{color:#5fb878} .summary-card.yellow .num{color:#d9b44c} .summary-card.red .num{color:#d97757} .summary-card.skip .num{color:#6f6d65}')
print('table{width:100%;border-collapse:collapse;font-size:12px;margin-bottom:24px}')
print('th{background:rgba(217,180,76,0.05);text-align:left;padding:8px;border-bottom:1px solid #d9b44c;font-size:10.5px;letter-spacing:0.05em;text-transform:uppercase;color:#a8a59c}')
print('td{padding:8px;border-bottom:1px solid #2a2730;vertical-align:top;color:#a8a59c}')
print('td.name{color:#f5f4f0;font-weight:500;width:180px;font-size:13px}')
print('td.status{font-weight:600;font-family:"JetBrains Mono",monospace;width:80px;font-size:11px}')
print('td.status.GREEN{color:#5fb878} td.status.YELLOW{color:#d9b44c} td.status.RED{color:#d97757} td.status.SKIP{color:#6f6d65}')
print('.metrics{font-family:"JetBrains Mono",monospace;font-size:11px;line-height:1.55;color:#a8a59c}')
print('.metrics b{color:#f5f4f0}')
print('.metrics .v{color:#5fb878} .metrics .x{color:#d97757} .metrics .y{color:#d9b44c}')
print('.bh-block{padding:10px 12px;background:rgba(139,109,200,0.06);border-left:3px solid #8b6dc8;border-radius:4px;margin:6px 0;font-size:11.5px;line-height:1.6}')
print('.bh-block .label{color:#8b6dc8;font-family:monospace;font-size:10px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:3px}')
print('.bh-block .body{color:#f5f4f0}')
print('.persona-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}')
print('.persona{padding:8px 10px;background:#0e0d12;border-radius:4px;font-size:11px;line-height:1.5}')
print('.persona-tag{color:#8b6dc8;font-family:monospace;font-size:9.5px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:3px}')
print('.adversarial-flag{display:inline-block;background:rgba(217,119,87,0.15);color:#d97757;font-size:9.5px;padding:1px 5px;border-radius:3px;font-family:monospace;margin-left:6px;vertical-align:middle}')
print('.bucket-section{margin-bottom:36px}')
print('.coverage-table td.pct-low{color:#d97757;font-weight:600}')
print('.coverage-table td.pct-mid{color:#d9b44c;font-weight:600}')
print('.coverage-table td.pct-high{color:#5fb878;font-weight:600}')
print('details{margin:8px 0}')
print('details summary{cursor:pointer;color:#d9b44c;font-family:monospace;font-size:11px;padding:4px 0}')
print('</style></head><body><div class="wrap">')
print('<h1>FieldCheck V022.30 · Insights Report</h1>')
print(f'<div class="subhdr">{total} athletes · 110-name battery · POST /verdict/player · skipCache=true</div>')

# Summary cards
print('<div class="summary">')
print(f'<div class="summary-card green"><div class="num">{green}</div><div class="lbl">GREEN ({pct(green)}%)</div></div>')
print(f'<div class="summary-card yellow"><div class="num">{yellow}</div><div class="lbl">YELLOW ({pct(yellow)}%)</div></div>')
print(f'<div class="summary-card red"><div class="num">{red}</div><div class="lbl">RED ({pct(red)}%)</div></div>')
print(f'<div class="summary-card skip"><div class="num">{skip}</div><div class="lbl">SKIP ({pct(skip)}%)</div></div>')
print(f'<div class="summary-card"><div class="num" style="color:#f5f4f0">{total}</div><div class="lbl">TOTAL</div></div>')
print('</div>')

# Adapter coverage matrix
print('<h2>★ Adapter Coverage Matrix · where the gaps are</h2>')
print('<div class="subhdr">Per-adapter success rate across all 110 athletes. Sorted by reliability (worst first). Where the data moat needs investment.</div>')
print('<table class="coverage-table"><thead><tr><th>Adapter</th><th>✓ Success</th><th>✗ Failed</th><th>% OK</th><th>Coverage assessment</th></tr></thead><tbody>')
for c in adapter_coverage:
    pct_class = 'pct-low' if c['pct_ok'] < 40 else ('pct-mid' if c['pct_ok'] < 70 else 'pct-high')
    assessment = ''
    if c['pct_ok'] < 30: assessment = 'CRITICAL GAP · adapter is broken or hostile-fetched · investigate'
    elif c['pct_ok'] < 60: assessment = 'WEAK · adapter intermittently fetches · gate or replace'
    elif c['pct_ok'] < 85: assessment = 'OK · adapter works but coverage gaps exist'
    else: assessment = 'STRONG · reliable signal source'
    print(f'<tr><td><b>{html.escape(c["adapter"])}</b></td><td>{c["success"]}</td><td>{c["fail"]}</td><td class="{pct_class}">{c["pct_ok"]}%</td><td>{assessment}</td></tr>')
print('</tbody></table>')

# Tier-level summary
print('<h2>★ Verdict Distribution by Tier</h2>')
tier_status = defaultdict(lambda: Counter())
for row in report_rows:
    expected_pool = row['athlete'].get('expected_pool', 'unknown')
    tier_status[expected_pool][row['status']] += 1
print('<table><thead><tr><th>Expected tier</th><th>GREEN</th><th>YELLOW</th><th>RED</th><th>SKIP</th><th>Total</th></tr></thead><tbody>')
for tier_key in ['hs', 'd1', 'd2', 'd3', 'juco', 'pro', 'varies']:
    if tier_key not in tier_status: continue
    counts = tier_status[tier_key]
    tot = sum(counts.values())
    print(f'<tr><td><b>{tier_key}</b></td><td>{counts.get("GREEN",0)}</td><td>{counts.get("YELLOW",0)}</td><td>{counts.get("RED",0)}</td><td>{counts.get("SKIP",0)}</td><td>{tot}</td></tr>')
print('</tbody></table>')

# Per-bucket athlete details
print('<h2>★ Per-Athlete Insights · all 110</h2>')
print('<div class="subhdr">Each athlete shows: status · core metrics · brutally honest interpretation · 4-persona decision read</div>')

current_bucket = None
for row in report_rows:
    if row['bucket_id'] != current_bucket:
        if current_bucket is not None: print('</tbody></table></div>')
        current_bucket = row['bucket_id']
        print(f'<div class="bucket-section"><h3>{html.escape(row["bucket_id"])} · {html.escape(row["bucket_name"])}</h3>')
        print('<table><thead><tr><th width="220">Athlete</th><th width="80">Status</th><th width="280">Core metrics</th><th>Brutal honest read</th></tr></thead><tbody>')

    ath = row['athlete']
    summ = row['summary']
    bh = row['brutal_honest']
    adversarial = ath.get('adversarial_risk', '')
    name_html = html.escape(ath['name'])
    if 'CRITICAL' in adversarial.upper() or 'EXTREME' in adversarial.upper() or 'CANONICAL' in adversarial.upper():
        name_html += f'<span class="adversarial-flag">{html.escape(adversarial[:50])}</span>'

    expected = f"want pool={ath.get('expected_pool','?')} · composite [{(ath.get('expected_composite_range') or ['?','?'])[0]}–{(ath.get('expected_composite_range') or ['?','?'])[1]}]"

    # Core metrics block
    def fmt(label, val, expected_val=None, ok_fn=None):
        cls = ''
        if ok_fn is not None and val is not None:
            cls = 'v' if ok_fn(val) else 'x'
        elif val is None:
            cls = 'y'
        return f'<div><b>{label}:</b> <span class="{cls}">{html.escape(str(val) if val is not None else "—")}</span></div>'

    metrics_html = '<div class="metrics">'
    metrics_html += fmt('school', summ['school'])
    metrics_html += fmt('source', summ['school_source'])
    metrics_html += fmt('career_stage', summ['career_stage'])
    metrics_html += fmt('tier', summ['tier'])
    metrics_html += fmt('percentile', summ['percentile'])
    metrics_html += fmt('verdict', summ['verdict'])
    metrics_html += fmt('composite', summ['composite'])
    metrics_html += fmt('bbref', summ['bbref_status'])
    metrics_html += f'<div><b>sources:</b> {summ["sources_succeeded_count"]} ok · {summ["sources_failed_count"]} fail</div>'
    metrics_html += f'<div style="color:#6f6d65;margin-top:4px;font-size:10px">{html.escape(expected)}</div>'
    metrics_html += '</div>'

    # Brutal honest block
    bh_html = ''
    if bh and bh.get('ok'):
        bh_html += f'<div class="bh-block"><div class="label">FieldCheck says · confidence={html.escape(str(bh.get("confidence","?")))}</div>'
        bh_html += f'<div class="body">{html.escape((bh.get("fieldcheck_says") or "")[:380])}</div></div>'
        asym = bh.get('the_asymmetry') or ''
        if asym:
            bh_html += f'<div class="bh-block" style="border-left-color:#d9b44c"><div class="label" style="color:#d9b44c">The asymmetry</div>'
            bh_html += f'<div class="body">{html.escape(asym[:260])}</div></div>'
        dgr = bh.get('decision_grade_read') or {}
        if dgr:
            bh_html += '<div class="persona-grid">'
            for ptag, plabel in [('for_player','PLAYER'), ('for_coach','COACH'), ('for_scout','SCOUT'), ('for_parent','PARENT')]:
                ptxt = dgr.get(ptag, '')
                if ptxt:
                    bh_html += f'<div class="persona"><div class="persona-tag">★ {plabel}</div><div>{html.escape(ptxt[:170])}</div></div>'
            bh_html += '</div>'
        # Failed litmus checks if any
        failed = [c for c in row['checks'] if c['status'] == 'fail']
        if failed:
            bh_html += '<details><summary>⚠ Litmus failures (' + str(len(failed)) + ')</summary>'
            for c in failed:
                bh_html += f'<div style="font-family:monospace;font-size:10.5px;color:#d97757;padding:2px 0">[{c["status"]}] {html.escape(c["check"])}: {html.escape(c["detail"][:160])}</div>'
            bh_html += '</details>'
    else:
        bh_html = '<div style="color:#6f6d65;font-style:italic">brutal_honest not generated (likely SKIP or adapter failure)</div>'

    print(f'<tr><td class="name">{name_html}<br><span style="color:#6f6d65;font-size:10.5px">{html.escape((ath.get("school") or "")[:60])}</span></td>')
    print(f'<td class="status {row["status"]}">{row["status"]}</td>')
    print(f'<td>{metrics_html}</td>')
    print(f'<td>{bh_html}</td></tr>')

print('</tbody></table></div>')

# Footer
import time
print(f'<div style="margin-top:32px;padding-top:16px;border-top:1px solid #2a2730;color:#6f6d65;font-size:11px;font-family:monospace;text-align:center">FC V022.30 · insights report v2 · generated {time.strftime("%Y-%m-%d %H:%M:%S")} · {total} athletes</div>')
print('</div></body></html>')
EOF

echo ""
echo "▸ Report generated: $REPORT_FILE"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo " FieldCheck V022.30 · Batch Test v2 Complete"
echo " Total elapsed: ${TOTAL_ELAPSED}s"
echo " Report:        $REPORT_FILE"
echo " Open with:     open $REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════════════"
