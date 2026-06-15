#!/usr/bin/env python3
# FCBase89 dual battery - runs roster against ONE worker URL, writes gate-ready JSON.
# Usage:
#   python3 fc-run-FCBase89-battery.py https://fieldcheck-proxy.sridhar-nallani.workers.dev baseline.json
#   python3 fc-run-FCBase89-battery.py https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev candidate.json
# Env: FC_ROSTER (default roster_100.json) FC_PARALLEL (3) FC_TIMEOUT_S (180)
import os, sys, json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

URL = sys.argv[1].rstrip('/')
OUT = sys.argv[2]
ROSTER = Path(os.environ.get('FC_ROSTER', 'roster_100.json'))
PAR = int(os.environ.get('FC_PARALLEL', '3'))
TMO = int(os.environ.get('FC_TIMEOUT_S', '180'))

raw = json.load(open(ROSTER))
if isinstance(raw, list):
    items = raw
elif isinstance(raw.get('athletes'), list):
    items = raw['athletes']
elif isinstance(raw.get('buckets'), list):
    items = []
    for b in raw['buckets']:
        if isinstance(b, dict):
            lst = next((v for v in b.values() if isinstance(v, list) and v and isinstance(v[0], dict)), [])
            bsport = b.get('sport')
            for a in lst:
                if bsport and not (a.get('sport') or a.get('sport_slug')):
                    a['sport'] = bsport
            items.extend(lst)
        elif isinstance(b, list):
            items.extend(b)
else:
    items = []
ath = []
for it in items:
    if not isinstance(it, dict): continue
    nm = it.get('name') or it.get('player') or it.get('athlete')
    sp = it.get('sport') or it.get('sport_slug') or 'mens-basketball'
    if nm: ath.append((str(nm).strip(), str(sp).strip()))
print('roster: %d athletes -> %s (parallel %d, timeout %ds)' % (len(ath), URL, PAR, TMO))
print('estimated time: up to %d min' % (len(ath) * TMO // (PAR * 60) + 1))

def one(nm, sp):
    payload = json.dumps({'name': nm, 'sport': sp, 'skipCache': True})
    try:
        r = subprocess.run(['curl', '-s', '--max-time', str(TMO), '-X', 'POST',
                            '-H', 'Content-Type: application/json', '-d', payload,
                            URL + '/verdict/player'], capture_output=True, text=True, timeout=TMO + 10)
        d = json.loads(r.stdout)
        comp = d.get('composite')
        if comp is None and isinstance(d.get('result'), dict): comp = d['result'].get('composite')
        if comp is None and isinstance(d.get('verdict'), dict): comp = d['verdict'].get('composite')
        c = float(comp) if comp is not None else None
        def dtier(x):
            if x is None: return ''
            if x >= 9.5: return 'ICON'
            if x >= 9.0: return 'ELITE+'
            if x >= 7.5: return 'ELITE'
            if x >= 7.0: return 'STAR'
            if x >= 5.5: return 'PROSPECT'
            if x >= 3.5: return 'SCOUT'
            return 'DEV'
        return {'name': nm, 'sport': sp, 'composite': c, 'tier': dtier(c)}
    except Exception as e:
        return {'name': nm, 'sport': sp, 'composite': None, 'error': str(e)[:80]}

results, done, t0 = [], 0, time.time()
with ThreadPoolExecutor(max_workers=PAR) as ex:
    futs = {ex.submit(one, nm, sp): nm for nm, sp in ath}
    for f in as_completed(futs):
        r = f.result(); results.append(r); done += 1
        flag = 'OK %.2f' % r['composite'] if r.get('composite') else 'FAIL'
        print('  [%3d/%d] %-30s %s' % (done, len(ath), r['name'][:30], flag), flush=True)

good = [r for r in results if r.get('composite')]
bad = [r for r in results if not r.get('composite')]
json.dump(good, open(OUT, 'w'), indent=1)
print('')
print('wrote %s: %d ok / %d failed / %.1f min' % (OUT, len(good), len(bad), (time.time() - t0) / 60))
if bad:
    print('failed athletes (rerun or accept gap; gate compares intersection):')
    for r in bad[:15]: print('  -', r['name'], r.get('error', ''))
