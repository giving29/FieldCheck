#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# test-amateurs.sh · Verify scout dossier on current HS + College amateurs
# Reads amateur-watchlist.json, runs /verdict/player on each, reports
# sources_succeeded per athlete. The VC demo readiness check.
#
# Usage:
#   bash test-amateurs.sh                    → all 71 amateurs
#   bash test-amateurs.sh hs                 → HS only (15)
#   bash test-amateurs.sh d1                 → D1 only (48)
#   bash test-amateurs.sh mens-basketball    → mens-basketball only
#   bash test-amateurs.sh --first=10         → just the first 10
# ──────────────────────────────────────────────────────────────────────────

MODE="${1:-all}"
WL="${HOME}/Desktop/fieldcheck-proxy/amateur-watchlist.json"
PROD="https://fieldcheck-proxy.sridhar-nallani.workers.dev"
DEV="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
WORKER="${WORKER:-$PROD}"

if [ ! -f "$WL" ]; then
  echo "ERROR: watchlist not at $WL"
  echo "Run: cp ~/Downloads/amateur-watchlist.json ~/Desktop/fieldcheck-proxy/"
  exit 1
fi

echo ""
echo "Testing amateurs against $WORKER"
echo ""

python3 - "$WL" "$MODE" "$WORKER" << 'PYEOF'
import json, sys, urllib.request, urllib.parse, time

watchlist_path, mode, worker = sys.argv[1], sys.argv[2], sys.argv[3]

with open(watchlist_path) as f:
    data = json.load(f)

athletes = data['athletes']

# Filter
if mode == 'hs':
    athletes = [a for a in athletes if a['level'] == 'HS']
elif mode == 'd1':
    athletes = [a for a in athletes if a['level'] == 'D1']
elif mode in ['mens-basketball', 'womens-basketball', 'football', 'baseball', 'womens-volleyball', 'mens-soccer']:
    athletes = [a for a in athletes if a['sport'] == mode]
elif mode.startswith('--first='):
    n = int(mode.split('=')[1])
    athletes = athletes[:n]

print(f'Testing {len(athletes)} amateurs')
print(f'─' * 105)
print(f'{"NAME":<25} {"SPORT":<22} {"LVL":<6} {"EXP TIER":<10} {"GOT TIER":<10} {"COMPOSITE":<10} {"SOURCES":<14} {"TIME":<8}')
print(f'─' * 105)

pass_count = 0
partial_count = 0
fail_count = 0

for a in athletes:
    payload = json.dumps({
        'name': a['name'],
        'sport': a['sport'],
        'schoolHint': a.get('school')
    }).encode('utf-8')
    
    req = urllib.request.Request(
        f'{worker}/verdict/player',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp_text = r.read().decode('utf-8')
        elapsed = int(time.time() - t0)
        d = json.loads(resp_text)
        
        eg = d.get('encyclopedia', {}).get('eval_grid', {})
        tier = eg.get('subjective_tier') or eg.get('tier') or 'NONE'
        composite = eg.get('composite', '—')
        
        meta = d.get('scout_dossier_meta', {})
        srcs = meta.get('sources_succeeded', [])
        srcs_str = f"{len(srcs)}/{meta.get('total_count', 9)}"
        
        cache = 'c' if d.get('cache_hit') else 'f'
        
        if tier != 'NONE' and tier != 'INSUFFICIENT_DATA':
            pass_count += 1
            status = '✓'
        elif tier == 'INSUFFICIENT_DATA' and len(srcs) > 0:
            partial_count += 1
            status = '~'
        else:
            fail_count += 1
            status = '✗'
        
        print(f"{status} {a['name']:<23} {a['sport']:<22} {a['level']:<6} {a['expected_tier']:<10} {tier:<10} {str(composite):<10} {srcs_str:<14} {elapsed}s{cache}")
    except Exception as e:
        elapsed = int(time.time() - t0)
        fail_count += 1
        print(f"✗ {a['name']:<23} {a['sport']:<22} {a['level']:<6} {a['expected_tier']:<10} {'TIMEOUT':<10} {'—':<10} {'—':<14} {elapsed}s")
    
    time.sleep(0.5)  # gentle rate limit

print(f'─' * 105)
print(f'')
print(f'PASS:    {pass_count}/{len(athletes)} ({100*pass_count//max(1,len(athletes))}%)')
print(f'PARTIAL: {partial_count}/{len(athletes)} (insufficient_data but some sources hit)')
print(f'FAIL:    {fail_count}/{len(athletes)} (no sources or timeout)')
print(f'')
print(f'VC demo readiness: {pass_count + partial_count}/{len(athletes)} ({100*(pass_count + partial_count)//max(1,len(athletes))}%) generated something useful')
PYEOF
