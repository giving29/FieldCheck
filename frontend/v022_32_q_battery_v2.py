#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-Q · 110-AMATEUR BATTERY · v2 · curl-based (urllib SSL fix)
═══════════════════════════════════════════════════════════════════════════
v1 failed because urllib on macOS doesn't trust the SSL cert chain by default.
v2 uses curl via subprocess (same path that worked in earlier smoke tests).
Same evaluation logic. Surfaces errors in stdout.

Run:
  cd ~/Desktop/fieldcheck-proxy
  cp ~/Downloads/v022_32_q_battery_v2.py .
  python3 v022_32_q_battery_v2.py

Env overrides:
  FC_DEV_URL    (default: dev worker)
  FC_ROSTER     (default: ./roster_100.json)
  FC_PARALLEL   (default: 3)
  FC_TIMEOUT_S  (default: 180)  ← per-athlete · worker can take 30-90s cold
═══════════════════════════════════════════════════════════════════════════
"""
import os, sys, json, time, html, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEV_URL  = os.environ.get('FC_DEV_URL',    'https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev')
ROSTER   = Path(os.environ.get('FC_ROSTER', 'roster_100.json'))
PARALLEL = int(os.environ.get('FC_PARALLEL', '3'))
TIMEOUT  = int(os.environ.get('FC_TIMEOUT_S', '180'))
REPORT   = Path(os.environ.get('FC_REPORT', 'fc_v022_32_q_battery_report.html'))

V4_CAPS = {
    'hs': 5.4, 'd3': 6.8, 'd2': 6.8, 'juco': 6.8, 'naia': 6.8,
    'd1': 7.4, 'early_pro': 7.9, 'prime_pro': 9.3, 'retired_pro': 9.6, 'legend_pro': 9.7,
}

# ─── PRE-FLIGHT · single curl to confirm endpoint works ────────────────────
print("▸ Pre-flight: testing endpoint with one curl...")
preflight = subprocess.run(
    [
        'curl', '-sS', '--max-time', '240',
        '-X', 'POST',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'name': 'Tim Duncan', 'sport': 'mens-basketball', 'skipCache': True}),
        f"{DEV_URL}/verdict/player",
    ],
    capture_output=True, text=True
)
if preflight.returncode != 0:
    print(f"✗ Pre-flight curl FAILED · returncode={preflight.returncode}")
    print(f"  stderr: {preflight.stderr[:500]}")
    sys.exit(1)
try:
    pre = json.loads(preflight.stdout)
    print(f"  ✓ Endpoint responsive · Tim Duncan returned composite={pre.get('composite')}")
except Exception as e:
    print(f"✗ Pre-flight response not valid JSON: {str(e)[:200]}")
    print(f"  raw (first 500 chars): {preflight.stdout[:500]}")
    sys.exit(1)
print()

# ─── LOAD ROSTER ───────────────────────────────────────────────────────────
if not ROSTER.exists():
    print(f"✗ roster not found at {ROSTER.absolute()}"); sys.exit(1)
with open(ROSTER) as f:
    roster_data = json.load(f)
athletes = []
for bucket in roster_data.get('buckets', []):
    bid = bucket['bucket_id']
    bname = bucket.get('name', bid)
    for ath in bucket.get('athletes', []):
        athletes.append({
            'bucket_id': bid, 'bucket_name': bname,
            'name': ath.get('name', ''),
            'sport': ath.get('sport') or bucket.get('sport') or 'mens-basketball',
            'school': ath.get('school', ''),
            'expected_pool': ath.get('expected_pool'),
            'expected_composite_range': ath.get('expected_composite_range'),
            'expected_band': ath.get('expected_band'),
            'adversarial_risk': ath.get('adversarial_risk', ''),
        })
total = len(athletes)
print(f"▸ Loaded {total} athletes · DEV={DEV_URL} · PARALLEL={PARALLEL} · TIMEOUT={TIMEOUT}s")
print()


# ─── FETCH ONE ATHLETE via curl subprocess ─────────────────────────────────
def fetch_athlete(ath):
    payload = json.dumps({
        'name': ath['name'], 'sport': ath['sport'],
        'schoolHint': ath['school'], 'skipCache': True,
    })
    t0 = time.time()
    try:
        proc = subprocess.run(
            ['curl', '-sS', '--max-time', str(TIMEOUT),
             '-X', 'POST', '-H', 'Content-Type: application/json',
             '-d', payload, f"{DEV_URL}/verdict/player"],
            capture_output=True, text=True, timeout=TIMEOUT + 10
        )
        elapsed = time.time() - t0
        if proc.returncode != 0:
            return ath, None, f"curl failed: {proc.stderr[:200]}", elapsed
        if not proc.stdout.strip():
            return ath, None, "empty response body", elapsed
        try:
            d = json.loads(proc.stdout)
            return ath, d, None, elapsed
        except json.JSONDecodeError as je:
            return ath, None, f"json decode error: {str(je)[:80]} · body: {proc.stdout[:120]}", elapsed
    except subprocess.TimeoutExpired:
        return ath, None, "timeout", time.time() - t0
    except Exception as e:
        return ath, None, f"{type(e).__name__}: {str(e)[:120]}", time.time() - t0


# ─── EVALUATE ──────────────────────────────────────────────────────────────
def evaluate(ath, response, error):
    if error or not response:
        return {
            'status': 'SKIP',
            'checks': [{'name': 'response_received', 'status': 'fail', 'detail': error or 'no response'}],
            'composite': None, 'tier': None, 'stage': None, 'school': None, 'cap': None, 'raw': None,
            'error': error,
        }
    composite = response.get('composite')
    cv = response.get('composite_v022_31') or {}
    enc = response.get('encyclopedia') or {}
    ident = (enc.get('facts') or {}).get('identity') or {}
    raw, cap, tier, stage = cv.get('raw'), cv.get('cap'), cv.get('tier'), cv.get('stage')
    school = ident.get('current_school')
    expected_pool = ath.get('expected_pool')
    rng = ath.get('expected_composite_range') or [None, None]
    checks = []

    # V4 cap compliance
    if expected_pool in V4_CAPS:
        v4_cap = V4_CAPS[expected_pool]
        if composite is None:
            checks.append({'name': 'v4_cap_compliance', 'status': 'fail', 'detail': f'composite null · expected ≤{v4_cap}'})
        elif composite <= v4_cap + 0.01:
            checks.append({'name': 'v4_cap_compliance', 'status': 'pass', 'detail': f'{composite} ≤ {v4_cap}'})
        else:
            checks.append({'name': 'v4_cap_compliance', 'status': 'fail', 'detail': f'{composite} EXCEEDS {v4_cap}'})

    # composite in band
    if rng[0] is not None and rng[1] is not None and composite is not None:
        if rng[0] <= composite <= rng[1]:
            checks.append({'name': 'composite_in_band', 'status': 'pass', 'detail': f'{composite} in [{rng[0]}-{rng[1]}]'})
        elif abs(composite - (rng[0] if composite < rng[0] else rng[1])) <= 0.5:
            checks.append({'name': 'composite_in_band', 'status': 'near', 'detail': f'{composite} near [{rng[0]}-{rng[1]}]'})
        else:
            checks.append({'name': 'composite_in_band', 'status': 'fail', 'detail': f'{composite} out of [{rng[0]}-{rng[1]}]'})

    # tier match
    if expected_pool and expected_pool != 'varies' and tier:
        if str(tier).lower() == str(expected_pool).lower():
            checks.append({'name': 'tier_match', 'status': 'pass', 'detail': f'tier={tier}'})
        else:
            checks.append({'name': 'tier_match', 'status': 'fail', 'detail': f'expected {expected_pool}, got {tier}'})

    # no pro stage for amateur
    if expected_pool in ('hs', 'd1', 'd2', 'd3', 'juco', 'naia'):
        if stage in ('legend_pro', 'prime_pro', 'retired_pro'):
            checks.append({'name': 'no_pro_stage_for_amateur', 'status': 'fail', 'detail': f'classified as {stage}'})
        else:
            checks.append({'name': 'no_pro_stage_for_amateur', 'status': 'pass', 'detail': f'stage={stage}'})

    # school sanity for amateurs
    expected_school = ath.get('school', '')
    if expected_pool in ('hs', 'd1', 'd2', 'd3', 'juco'):
        if expected_school and expected_school not in ('unknown', 'varies') and school:
            sl, el = str(school).lower(), str(expected_school).lower()
            if sl in el or el in sl:
                checks.append({'name': 'school_match', 'status': 'pass', 'detail': f'{school}'})
            else:
                checks.append({'name': 'school_match', 'status': 'near', 'detail': f'expected ~{expected_school}, got {school}'})
        elif not school:
            checks.append({'name': 'school_resolved', 'status': 'near', 'detail': 'school is null'})

    fails = sum(1 for c in checks if c['status'] == 'fail')
    nears = sum(1 for c in checks if c['status'] == 'near')
    status = 'GREEN' if fails == 0 and nears == 0 else 'YELLOW' if fails == 0 else 'RED'

    return {
        'status': status, 'checks': checks,
        'composite': composite, 'tier': tier, 'stage': stage,
        'school': school, 'cap': cap, 'raw': raw, 'error': None,
    }


# ─── RUN ────────────────────────────────────────────────────────────────────
print(f"▸ Running battery · 110 athletes · ~10-20 min expected...")
print()
results = []
done = 0
t_start = time.time()

with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
    futures = {ex.submit(fetch_athlete, a): a for a in athletes}
    for fut in as_completed(futures):
        ath, resp, err, elapsed = fut.result()
        ev = evaluate(ath, resp, err)
        ev['athlete'] = ath
        ev['elapsed_s'] = round(elapsed, 1)
        results.append(ev)
        done += 1
        sigil = {'GREEN': '✓', 'YELLOW': '~', 'RED': '✗', 'SKIP': '·'}[ev['status']]
        if ev['status'] == 'SKIP':
            err_short = (ev.get('error') or 'unknown')[:60]
            print(f"  [{done:>3}/{total}] {sigil} SKIP   [{ath['bucket_id'][:20]:<20}] {ath['name'][:28]:<28}  ERR: {err_short}  ({elapsed:.1f}s)")
        else:
            comp = ev['composite']
            tier = ev.get('tier') or '?'
            stage = (ev.get('stage') or '?')[:14]
            print(f"  [{done:>3}/{total}] {sigil} {ev['status']:<6} [{ath['bucket_id'][:20]:<20}] {ath['name'][:28]:<28}  comp={comp!s:<5}  tier={tier:<5}  stage={stage:<14}  ({elapsed:.1f}s)")

t_total = time.time() - t_start
print()
print(f"▸ Battery complete in {t_total:.0f}s")
print()

bucket_order = {b['bucket_id']: i for i, b in enumerate(roster_data.get('buckets', []))}
results.sort(key=lambda r: (bucket_order.get(r['athlete']['bucket_id'], 99), r['athlete']['name']))

# ─── STDOUT SUMMARY ────────────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════════════")
print(" AMATEUR-FIRST V4 CALIBRATION COMPLIANCE")
print("═══════════════════════════════════════════════════════════════════════\n")

green = sum(1 for r in results if r['status'] == 'GREEN')
yellow = sum(1 for r in results if r['status'] == 'YELLOW')
red = sum(1 for r in results if r['status'] == 'RED')
skip = sum(1 for r in results if r['status'] == 'SKIP')

print(f"  GREEN:   {green:>3} ({100*green/total:.0f}%)")
print(f"  YELLOW:  {yellow:>3} ({100*yellow/total:.0f}%)")
print(f"  RED:     {red:>3} ({100*red/total:.0f}%)")
print(f"  SKIP:    {skip:>3} ({100*skip/total:.0f}%)\n")

print("V4 CAP COMPLIANCE PER TIER (this is the proof):\n")
tier_stats = {}
for r in results:
    pool = r['athlete'].get('expected_pool')
    if pool not in V4_CAPS: continue
    v4_cap = V4_CAPS[pool]
    composite = r['composite']
    if pool not in tier_stats:
        tier_stats[pool] = {'total': 0, 'within_cap': 0, 'exceeds_cap': 0, 'null': 0, 'cap': v4_cap}
    tier_stats[pool]['total'] += 1
    if composite is None:
        tier_stats[pool]['null'] += 1
    elif composite <= v4_cap + 0.01:
        tier_stats[pool]['within_cap'] += 1
    else:
        tier_stats[pool]['exceeds_cap'] += 1

for pool in ('hs', 'd1', 'd2', 'd3', 'juco', 'naia', 'pro'):
    if pool not in tier_stats: continue
    s = tier_stats[pool]
    t = s['total']
    pct = 100 * s['within_cap'] / t if t else 0
    print(f"  {pool.upper():<6} (V4 cap {s['cap']}): {s['within_cap']}/{t} within cap ({pct:.0f}%) · {s['exceeds_cap']} exceed · {s['null']} null")
print()

# Composite distribution per tier (the new richness)
print("COMPOSITE DISTRIBUTION PER TIER:\n")
for pool in ('hs', 'd1', 'd2', 'd3', 'juco'):
    composites = [r['composite'] for r in results if r['athlete'].get('expected_pool') == pool and r['composite'] is not None]
    if not composites: continue
    composites_sorted = sorted(composites)
    n = len(composites)
    avg = sum(composites) / n
    median = composites_sorted[n // 2]
    print(f"  {pool.upper():<6}: n={n:>2}  min={min(composites):.1f}  median={median:.1f}  avg={avg:.1f}  max={max(composites):.1f}  cap={V4_CAPS[pool]}")
print()

# Top SKIPs by error reason
skip_errors = {}
for r in results:
    if r['status'] != 'SKIP': continue
    e = (r.get('error') or 'unknown')[:60]
    skip_errors[e] = skip_errors.get(e, 0) + 1
if skip_errors:
    print("SKIP REASONS (top):")
    for e, c in sorted(skip_errors.items(), key=lambda x: -x[1])[:5]:
        print(f"  {c:>3}× {e}")
    print()


# ─── HTML REPORT ───────────────────────────────────────────────────────────
def esc(s): return html.escape(str(s)) if s is not None else ''

parts = ['<!DOCTYPE html><html><head><meta charset="UTF-8">',
         '<title>FC V022.32-Q · 110-Battery · V4 Calibration Report</title>',
         '<style>',
         '''body{font-family:-apple-system,BlinkMacSystemFont,"Inter",sans-serif;background:#07060a;color:#f5f4f0;padding:24px;line-height:1.6;margin:0}
.wrap{max-width:1280px;margin:0 auto}
h1{font-family:"Fraunces",Georgia,serif;font-size:36px;font-weight:600;letter-spacing:-0.02em;margin:0 0 6px;color:#fff}
.subhdr{color:#a8a59c;margin-bottom:28px;font-size:14px}
.summary{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:28px}
.card{padding:20px;background:#1a1820;border:1px solid #2a2730;border-radius:8px;text-align:center}
.card .num{font-size:36px;font-weight:600;font-family:"Fraunces",serif;line-height:1}
.card .lbl{color:#a8a59c;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;margin-top:8px}
.card.green .num{color:#5fb878}.card.yellow .num{color:#d9b44c}.card.red .num{color:#d97757}.card.skip .num{color:#6f6d65}
.tier-table{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:28px;background:#0f0d12;border:1px solid #2a2730;border-radius:8px;overflow:hidden}
.tier-table th{background:rgba(217,180,76,0.08);text-align:left;padding:12px 14px;border-bottom:2px solid #d9b44c;font-size:11px;letter-spacing:0.05em;text-transform:uppercase;color:#d9b44c}
.tier-table td{padding:10px 14px;border-bottom:1px solid #2a2730;color:#a8a59c;font-family:"JetBrains Mono",monospace;font-size:12px}
.tier-table td.tier{color:#fff;font-weight:600;font-family:"Fraunces",serif}
.bucket{margin-bottom:36px}
.bucket-h{font-family:"Fraunces",serif;font-size:18px;border-bottom:1px solid #2a2730;padding-bottom:10px;margin-bottom:14px;color:#d9b44c}
table.results{width:100%;border-collapse:collapse;font-size:12.5px;background:#0f0d12;border:1px solid #2a2730;border-radius:6px;overflow:hidden}
table.results th{background:rgba(217,180,76,0.05);text-align:left;padding:10px;border-bottom:1px solid #d9b44c;font-size:10px;letter-spacing:0.05em;text-transform:uppercase;color:#a8a59c}
table.results td{padding:9px 10px;border-bottom:1px solid #2a2730;vertical-align:top;color:#a8a59c}
table.results td.name{color:#f5f4f0;font-weight:500}
table.results td.status{font-weight:600;font-family:"JetBrains Mono",monospace;width:75px}
.status.GREEN{color:#5fb878}.status.YELLOW{color:#d9b44c}.status.RED{color:#d97757}.status.SKIP{color:#6f6d65}
.comp{font-family:"JetBrains Mono",monospace;color:#d9b44c;text-align:right}
.checks{font-family:"JetBrains Mono",monospace;font-size:11px;line-height:1.5}
.check.pass{color:#5fb878}.check.fail{color:#d97757}.check.near{color:#d9b44c}
.adversarial{display:inline-block;background:rgba(217,119,87,0.15);color:#d97757;font-size:10px;padding:1px 6px;border-radius:3px;margin-left:6px}''',
         '</style></head><body><div class="wrap">',
         '<h1>FieldCheck V022.32-Q · 110-Battery · V4 Calibration Report</h1>',
         f'<div class="subhdr">{time.strftime("%Y-%m-%d %H:%M")} · {total} athletes · Tenet 46 V4 doctrine (HS cap 5.4 · D1 cap 7.4 · D2/D3/JUCO cap 6.8 · NBA rookie cap 7.9 · active multi-MVP cap 9.3)</div>',
         '<div class="summary">',
         f'<div class="card green"><div class="num">{green}</div><div class="lbl">GREEN ({100*green//total}%)</div></div>',
         f'<div class="card yellow"><div class="num">{yellow}</div><div class="lbl">YELLOW ({100*yellow//total}%)</div></div>',
         f'<div class="card red"><div class="num">{red}</div><div class="lbl">RED ({100*red//total}%)</div></div>',
         f'<div class="card skip"><div class="num">{skip}</div><div class="lbl">SKIP ({100*skip//total}%)</div></div>',
         f'<div class="card"><div class="num" style="color:#fff">{total}</div><div class="lbl">TOTAL</div></div>',
         '</div>',
         '<h2 style="font-family:Fraunces,serif;color:#d9b44c;font-size:20px;margin:24px 0 12px">V4 Cap Compliance Per Tier</h2>',
         '<table class="tier-table"><thead><tr><th>Tier</th><th>V4 Cap</th><th>Total</th><th>Within Cap</th><th>Exceeds Cap</th><th>Null Composite</th><th>% Compliant</th></tr></thead><tbody>']

for pool in ('hs', 'd1', 'd2', 'd3', 'juco', 'naia', 'pro'):
    if pool not in tier_stats: continue
    s = tier_stats[pool]
    pct = 100 * s['within_cap'] / s['total'] if s['total'] else 0
    color = '#5fb878' if pct >= 95 else '#d9b44c' if pct >= 80 else '#d97757'
    parts.append(f'<tr><td class="tier">{pool.upper()}</td><td>{s["cap"]}</td><td>{s["total"]}</td><td style="color:#5fb878">{s["within_cap"]}</td><td style="color:#d97757">{s["exceeds_cap"]}</td><td style="color:#6f6d65">{s["null"]}</td><td style="color:{color};font-weight:600">{pct:.0f}%</td></tr>')
parts.append('</tbody></table>')

current_bucket = None
for r in results:
    a = r['athlete']
    if a['bucket_id'] != current_bucket:
        if current_bucket is not None:
            parts.append('</tbody></table></div>')
        current_bucket = a['bucket_id']
        parts.append(f'<div class="bucket"><div class="bucket-h">{esc(a["bucket_id"])} · {esc(a["bucket_name"])}</div>')
        parts.append('<table class="results"><thead><tr><th>Athlete</th><th>Status</th><th>Composite</th><th>Cap</th><th>Tier</th><th>Stage</th><th>School</th><th>Checks</th></tr></thead><tbody>')
    adv = a.get('adversarial_risk', '')
    name_html = esc(a['name'])
    if adv and ('CRITICAL' in adv.upper() or 'EXTREME' in adv.upper()):
        name_html += f'<span class="adversarial">{esc(adv[:40])}</span>'
    checks_html = '<div class="checks">'
    for c in r['checks']:
        checks_html += f'<div class="check {c["status"]}">{esc(c["name"])}: {esc(c["detail"])[:80]}</div>'
    checks_html += '</div>'
    parts.append(f'<tr><td class="name">{name_html}<br><span style="color:#6f6d65;font-size:10px">{esc(a.get("school",""))[:45]}</span></td>')
    parts.append(f'<td class="status {r["status"]}">{r["status"]}</td>')
    parts.append(f'<td class="comp">{r["composite"]!s}</td>')
    parts.append(f'<td class="comp" style="color:#6f6d65">{r["cap"]!s}</td>')
    parts.append(f'<td>{esc(r["tier"])}</td>')
    parts.append(f'<td>{esc(r["stage"])}</td>')
    parts.append(f'<td>{esc(r["school"])[:30]}</td>')
    parts.append(f'<td>{checks_html}</td></tr>')
parts.append('</tbody></table></div>')
parts.append('</div></body></html>')

with open(REPORT, 'w') as f:
    f.write('\n'.join(parts))

print(f"▸ HTML report: {REPORT.absolute()}")
print(f"  Open: open {REPORT}")
