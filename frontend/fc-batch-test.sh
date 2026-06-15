#!/usr/bin/env bash
# ═════════════════════════════════════════════════════════════════════════════
# fc-batch-test.sh · V022.30 · 110-athlete battery runner
# ═════════════════════════════════════════════════════════════════════════════
# Usage:
#   1. Deploy V022.30 worker to dev first (./fc-stage.sh deploy)
#   2. Run: ./fc-batch-test.sh
#   3. Open: fc-batch-test-report.html in browser
#
# What it does:
#   - Loads /home/claude or ~/Desktop/fieldcheck-proxy/roster_100.json (110 athletes)
#   - For each athlete: GET {BASE_URL}/verdict?name=X&sport=Y&school=Z
#   - Saves raw response to results/<bucket_id>__<safe_name>.json
#   - Generates HTML report with green/yellow/red per athlete per litmus check
#   - Outputs summary: total · passed · yellow · red · skipped
# ═════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_URL="${FC_BASE_URL:-https://fieldcheck-proxy.sridhar-nallani.workers.dev}"
ROSTER_FILE="${FC_ROSTER:-./roster_100.json}"
RESULTS_DIR="${FC_RESULTS_DIR:-./fc-batch-test-results}"
REPORT_FILE="${FC_REPORT:-./fc-batch-test-report.html}"
TIMEOUT_SECONDS="${FC_TIMEOUT:-90}"
PARALLEL_JOBS="${FC_PARALLEL:-3}"  # 3 simultaneous to avoid rate-limiting worker

# Find roster if default doesn't exist
if [ ! -f "$ROSTER_FILE" ]; then
  for candidate in \
    "$HOME/Desktop/fieldcheck-proxy/roster_100.json" \
    "$HOME/Downloads/roster_100.json" \
    "/home/claude/v022.30/roster/roster_100.json" \
    "/mnt/user-data/outputs/roster_100.json"; do
    if [ -f "$candidate" ]; then
      ROSTER_FILE="$candidate"
      break
    fi
  done
fi

if [ ! -f "$ROSTER_FILE" ]; then
  echo "ERROR: roster_100.json not found. Set FC_ROSTER env or place file in ~/Desktop/fieldcheck-proxy/" >&2
  exit 1
fi

mkdir -p "$RESULTS_DIR"

echo "▸ FieldCheck V022.30 batch test harness"
echo "▸ BASE_URL    = $BASE_URL"
echo "▸ ROSTER      = $ROSTER_FILE"
echo "▸ RESULTS     = $RESULTS_DIR"
echo "▸ REPORT      = $REPORT_FILE"
echo "▸ PARALLEL    = $PARALLEL_JOBS"
echo ""

# ── EXTRACT ATHLETE LIST FROM ROSTER ──────────────────────────────────────────
# Use python (preferred) or jq fallback
EXTRACT_SCRIPT=$(cat <<'PYEOF'
import json, sys, urllib.parse, os, re
with open(sys.argv[1]) as f:
    d = json.load(f)
rows = []
for bucket in d.get('buckets', []):
    bid = bucket['bucket_id']
    for ath in bucket.get('athletes', []):
        name = ath.get('name', '')
        sport = ath.get('sport') or bucket.get('sport') or 'mens-basketball'
        school = ath.get('school', '')
        safe = re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')[:40]
        rows.append((bid, name, sport, school, safe))
for r in rows:
    print('\t'.join(r))
PYEOF
)

if ! python3 -c "import json" 2>/dev/null; then
  echo "ERROR: python3 required for batch test harness" >&2
  exit 1
fi

ATHLETES=$(python3 -c "$EXTRACT_SCRIPT" "$ROSTER_FILE")
TOTAL=$(echo "$ATHLETES" | wc -l | tr -d ' ')
echo "▸ TOTAL ATHLETES = $TOTAL"
echo ""

# ── FETCH FUNCTION ────────────────────────────────────────────────────────────
fetch_athlete() {
  local bid="$1" name="$2" sport="$3" school="$4" safe="$5"
  local outfile="$RESULTS_DIR/${bid}__${safe}.json"
  local name_enc school_enc sport_enc
  name_enc=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$name")
  school_enc=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$school")
  sport_enc=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$sport")
  local url="${BASE_URL}/verdict?name=${name_enc}&sport=${sport_enc}&school=${school_enc}"
  local t0 t1
  t0=$(date +%s)
  local http_code
  http_code=$(curl -sS -w "%{http_code}" -o "$outfile" --max-time "$TIMEOUT_SECONDS" "$url" 2>/dev/null || echo "TIMEOUT")
  t1=$(date +%s)
  local elapsed=$((t1 - t0))
  printf "  [%s] %-30s %ss  http=%s  → %s\n" "$bid" "${name:0:30}" "$elapsed" "$http_code" "$outfile"
  # Append metadata
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

# ── RUN BATTERY (parallel) ────────────────────────────────────────────────────
START=$(date +%s)
echo "$ATHLETES" | while IFS=$'\t' read -r bid name sport school safe; do
  fetch_athlete "$bid" "$name" "$sport" "$school" "$safe" &
  # Throttle parallel jobs
  if [ $(jobs -r | wc -l) -ge $PARALLEL_JOBS ]; then
    wait -n
  fi
done
wait
END=$(date +%s)
TOTAL_ELAPSED=$((END - START))
echo ""
echo "▸ All requests done in ${TOTAL_ELAPSED}s · generating report..."
echo ""

# ── GENERATE REPORT ───────────────────────────────────────────────────────────
python3 <<EOF > "$REPORT_FILE"
import json, os, sys, html, re, glob

ROSTER = "$ROSTER_FILE"
RESULTS_DIR = "$RESULTS_DIR"

with open(ROSTER) as f:
    roster = json.load(f)

# Load all results
results = {}
for fp in glob.glob(os.path.join(RESULTS_DIR, "*.json")):
    base = os.path.basename(fp)[:-5]  # strip .json
    try:
        with open(fp) as f:
            results[base] = json.load(f)
    except Exception as e:
        results[base] = {"_load_error": str(e)}

def safe_name(name):
    return re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')[:40]

def evaluate_athlete(ath, bucket, response):
    """Returns (status, checks_list, summary_text)
       status: GREEN | YELLOW | RED | SKIP
    """
    checks = []
    if not response or '_raw_load_error' in response or '_load_error' in response:
        return ('SKIP', [{'check': 'response_loadable', 'status': 'fail', 'detail': 'could not load response JSON'}], 'No response')

    meta = response.get('_batch_meta', {})
    http = meta.get('http', '?')
    if http != '200':
        return ('SKIP', [{'check': 'http_200', 'status': 'fail', 'detail': f'HTTP {http}'}], f'HTTP {http}')

    enc = response.get('encyclopedia') or {}
    facts = enc.get('facts') or {}
    ident = facts.get('identity') or {}

    # CHECK 1: identity validated for known-name-collision athletes
    expected_school = ath.get('school') or ''
    actual_school = ident.get('current_school') or ''
    school_match = None
    if expected_school and expected_school != 'unknown' and 'varies' not in expected_school.lower() and 'common name test' not in expected_school.lower() and 'adversarial' not in expected_school.lower():
        if actual_school and actual_school.lower() in expected_school.lower() or expected_school.lower() in (actual_school or '').lower():
            school_match = 'pass'
        elif not actual_school:
            school_match = 'null'  # yellow
        else:
            school_match = 'fail'
        checks.append({
            'check': 'current_school',
            'status': school_match,
            'detail': f'expected≈"{expected_school[:40]}" got="{actual_school[:40]}"'
        })

    # CHECK 2: composite in expected band
    composite = response.get('composite')
    rng = ath.get('expected_composite_range') or [None, None]
    composite_match = None
    if composite is not None and rng[0] is not None and rng[1] is not None:
        if rng[0] <= composite <= rng[1]:
            composite_match = 'pass'
        elif abs(composite - (rng[0] if composite < rng[0] else rng[1])) <= 0.5:
            composite_match = 'near'  # yellow
        else:
            composite_match = 'fail'
        checks.append({
            'check': 'composite_in_band',
            'status': composite_match,
            'detail': f'expected [{rng[0]}-{rng[1]}] got {composite}'
        })
    elif composite is None and ath.get('expected_band') == 'SPARSE':
        checks.append({'check': 'composite_sparse_ok', 'status': 'pass', 'detail': 'null composite correct for SPARSE band'})
    elif composite is None:
        checks.append({'check': 'composite_present', 'status': 'fail', 'detail': 'composite is null but expected band is ' + str(ath.get('expected_band'))})

    # CHECK 3: tier classification
    expected_pool = ath.get('expected_pool') or ''
    pool_bench = enc.get('position_pool_benchmark') or {}
    actual_tier = pool_bench.get('tier', '')
    if expected_pool and expected_pool != 'varies':
        if actual_tier and actual_tier.lower() == expected_pool.lower():
            checks.append({'check': 'pool_tier', 'status': 'pass', 'detail': f'tier={actual_tier}'})
        else:
            checks.append({'check': 'pool_tier', 'status': 'fail', 'detail': f'expected {expected_pool} got {actual_tier}'})

    # CHECK 4: legend_pro NOT applied to amateurs
    career_stage = (ident.get('career_stage') or enc.get('career_stage') or '').lower()
    if expected_pool in ('hs', 'd1', 'd2', 'd3', 'juco') and career_stage in ('legend_pro', 'prime_pro', 'retired_pro'):
        checks.append({'check': 'no_legend_pro_for_amateur', 'status': 'fail', 'detail': f'career_stage={career_stage} for amateur'})
    elif expected_pool == 'pro' and career_stage in ('legend_pro', 'prime_pro', 'retired_pro', 'early_pro'):
        checks.append({'check': 'pro_career_stage', 'status': 'pass', 'detail': f'career_stage={career_stage}'})
    elif career_stage:
        checks.append({'check': 'career_stage_set', 'status': 'pass', 'detail': f'career_stage={career_stage}'})

    # CHECK 5: bbref_pro identity validation worked
    dossier = (enc.get('scout_dossier') or {}).get('sources') or {}
    bbref = dossier.get('bbref_pro') or {}
    if bbref.get('ok') and bbref.get('identity_validated') is True:
        checks.append({'check': 'bbref_identity_validated', 'status': 'pass', 'detail': bbref.get('identity_validation', {}).get('matched_title', '')[:40]})
    elif bbref.get('error') == 'name_mismatch_v022.30':
        # CORRECT failure mode for adversarial cases
        if ath.get('adversarial_risk', '').upper().find('CRITICAL') >= 0 or ath.get('expected_pool') != 'pro':
            checks.append({'check': 'bbref_correctly_rejected', 'status': 'pass', 'detail': 'V022.30 name_mismatch gate fired correctly'})
        else:
            checks.append({'check': 'bbref_unexpectedly_rejected', 'status': 'fail', 'detail': 'bbref rejected for legitimate pro'})

    # CHECK 6: brutally honest layer present
    bh = enc.get('brutal_honest') or {}
    if bh.get('ok'):
        checks.append({'check': 'brutal_honest_present', 'status': 'pass', 'detail': f'confidence={bh.get("confidence")}, anchors={len(bh.get("evidence_anchors", []))}'})
    else:
        checks.append({'check': 'brutal_honest_present', 'status': 'fail', 'detail': str(bh.get('error', 'missing'))[:80]})

    # Aggregate status
    fails = sum(1 for c in checks if c['status'] == 'fail')
    nears = sum(1 for c in checks if c['status'] in ('near', 'null'))
    if fails == 0 and nears == 0:
        return ('GREEN', checks, f'{len(checks)} checks all passed')
    elif fails == 0:
        return ('YELLOW', checks, f'{nears} near/null')
    else:
        return ('RED', checks, f'{fails} failed · {nears} near')

# Build report data
report_rows = []
green = yellow = red = skip = 0
for bucket in roster['buckets']:
    bid = bucket['bucket_id']
    for ath in bucket['athletes']:
        key = f"{bid}__{safe_name(ath['name'])}"
        resp = results.get(key, {})
        status, checks, summary = evaluate_athlete(ath, bucket, resp)
        report_rows.append({
            'bucket_id': bid,
            'bucket_name': bucket['name'],
            'athlete': ath,
            'response_key': key,
            'status': status,
            'checks': checks,
            'summary': summary
        })
        if status == 'GREEN': green += 1
        elif status == 'YELLOW': yellow += 1
        elif status == 'RED': red += 1
        else: skip += 1

total = len(report_rows)
pct_green = round(100 * green / total) if total else 0
pct_yellow = round(100 * yellow / total) if total else 0
pct_red = round(100 * red / total) if total else 0
pct_skip = round(100 * skip / total) if total else 0

# Emit HTML
print('<!DOCTYPE html><html><head><meta charset="UTF-8"><title>FC V022.30 · Batch Test Report</title>')
print('<style>')
print('body{font-family:-apple-system,BlinkMacSystemFont,"Inter",sans-serif;background:#07060a;color:#f5f4f0;padding:24px;line-height:1.6}')
print('.wrap{max-width:1200px;margin:0 auto}')
print('h1{font-family:"Fraunces",Georgia,serif;font-size:32px;font-weight:600;letter-spacing:-0.02em;margin-bottom:6px}')
print('.subhdr{color:#a8a59c;margin-bottom:24px;font-size:13.5px}')
print('.summary{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:24px}')
print('.summary-card{padding:18px;background:#1a1820;border:1px solid #2a2730;border-radius:8px}')
print('.summary-card .num{font-size:32px;font-weight:600;font-family:"Fraunces",serif}')
print('.summary-card .lbl{color:#a8a59c;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;margin-top:4px}')
print('.summary-card.green .num{color:#5fb878} .summary-card.yellow .num{color:#d9b44c} .summary-card.red .num{color:#d97757} .summary-card.skip .num{color:#6f6d65}')
print('.bucket-section{margin-bottom:32px}')
print('.bucket-h{font-family:"Fraunces",serif;font-size:18px;border-bottom:1px solid #2a2730;padding-bottom:8px;margin-bottom:12px;color:#d9b44c}')
print('table{width:100%;border-collapse:collapse;font-size:12px;margin-bottom:18px}')
print('th{background:rgba(217,180,76,0.05);text-align:left;padding:8px;border-bottom:1px solid #d9b44c;font-size:10px;letter-spacing:0.05em;text-transform:uppercase;color:#a8a59c}')
print('td{padding:8px;border-bottom:1px solid #2a2730;vertical-align:top;color:#a8a59c}')
print('td.name{color:#f5f4f0;font-weight:500;width:200px}')
print('td.status{font-weight:600;font-family:"JetBrains Mono",monospace;width:90px}')
print('td.status.GREEN{color:#5fb878} td.status.YELLOW{color:#d9b44c} td.status.RED{color:#d97757} td.status.SKIP{color:#6f6d65}')
print('.checks-list{font-family:"JetBrains Mono",monospace;font-size:11px;line-height:1.5}')
print('.checks-list .check{color:#5fb878}')
print('.checks-list .check.fail{color:#d97757}')
print('.checks-list .check.near, .checks-list .check.null{color:#d9b44c}')
print('.checks-list .check.pass{color:#5fb878}')
print('.adversarial-flag{display:inline-block;background:rgba(217,119,87,0.15);color:#d97757;font-size:10px;padding:2px 6px;border-radius:3px;font-family:monospace;margin-left:8px}')
print('</style></head><body><div class="wrap">')
print(f'<h1>FieldCheck V022.30 · Batch Test Report</h1>')
print(f'<div class="subhdr">{total} athletes across {len(roster["buckets"])} buckets · generated at $(date "+%Y-%m-%d %H:%M:%S")</div>')

print('<div class="summary">')
print(f'<div class="summary-card green"><div class="num">{green}</div><div class="lbl">GREEN ({pct_green}%)</div></div>')
print(f'<div class="summary-card yellow"><div class="num">{yellow}</div><div class="lbl">YELLOW ({pct_yellow}%)</div></div>')
print(f'<div class="summary-card red"><div class="num">{red}</div><div class="lbl">RED ({pct_red}%)</div></div>')
print(f'<div class="summary-card skip"><div class="num">{skip}</div><div class="lbl">SKIP/NO RESP ({pct_skip}%)</div></div>')
print(f'<div class="summary-card"><div class="num" style="color:#f5f4f0">{total}</div><div class="lbl">TOTAL</div></div>')
print('</div>')

current_bucket = None
for row in report_rows:
    if row['bucket_id'] != current_bucket:
        if current_bucket is not None:
            print('</tbody></table></div>')
        current_bucket = row['bucket_id']
        print(f'<div class="bucket-section">')
        print(f'<div class="bucket-h">{html.escape(row["bucket_id"])} · {html.escape(row["bucket_name"])}</div>')
        print('<table><thead><tr><th>Athlete</th><th>Status</th><th>Expected</th><th>Checks</th></tr></thead><tbody>')
    ath = row['athletes' if False else 'athlete']
    adversarial = ath.get('adversarial_risk', '')
    name_html = html.escape(ath['name'])
    if 'CRITICAL' in adversarial.upper() or 'EXTREME' in adversarial.upper():
        name_html += f'<span class="adversarial-flag">{html.escape(adversarial[:40])}</span>'
    print(f'<tr><td class="name">{name_html}<br><span style="color:#6f6d65;font-size:10px">{html.escape(ath.get("school", "")[:50])}</span></td>')
    print(f'<td class="status {row["status"]}">{row["status"]}</td>')
    rng = ath.get('expected_composite_range') or [None, None]
    pool = ath.get('expected_pool', '')
    band = ath.get('expected_band', '')
    print(f'<td>{html.escape(str(band))}<br><span style="color:#6f6d65;font-size:10px">composite [{rng[0]}-{rng[1]}] · pool {pool}</span></td>')
    checks_html = '<div class="checks-list">'
    for c in row['checks']:
        checks_html += f'<div class="check {c["status"]}">[{c["status"].upper()}] {html.escape(c["check"])}: {html.escape(str(c["detail"])[:120])}</div>'
    checks_html += '</div>'
    print(f'<td>{checks_html}</td></tr>')
print('</tbody></table></div>')
print('</div></body></html>')
EOF

echo ""
echo "▸ Report generated: $REPORT_FILE"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo " FieldCheck V022.30 · Batch Test Complete"
echo " Total elapsed: ${TOTAL_ELAPSED}s"
echo " Report:        $REPORT_FILE"
echo " Open with:     open $REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════════════"
