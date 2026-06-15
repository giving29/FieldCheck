set -e
cd ~/Desktop/fieldcheck-proxy
R=h1_draft2026_results.json
if [ ! -f "$R" ]; then
cat > $R << 'JSONEOF'
{
  "resolved_event": "2026 NBA Draft, June 24-25, 2026",
  "results": [
    { "athlete": "AJ Dybantsa", "actual": "FILL e.g. Pick 1, Washington" },
    { "athlete": "Darryn Peterson", "actual": "FILL" },
    { "athlete": "Cameron Boozer", "actual": "FILL" },
    { "athlete": "Caleb Wilson", "actual": "FILL" },
    { "athlete": "Mikel Brown Jr", "actual": "FILL" },
    { "athlete": "Nate Ament", "actual": "FILL" }
  ]
}
JSONEOF
echo "Created $R - fill 'actual' with real picks (open -e $R), then rerun this script."
exit 0
fi
python3 - << 'PYEOF'
import json, re, glob, datetime
res = json.load(open('h1_draft2026_results.json'))
blob = json.dumps(res)
assert 'FILL' not in blob, 'ABORT: fill actual picks first'
sealed = json.load(open(sorted(glob.glob('h1_draft2026.SEALED.*.json'))[-1]))
actual = {r['athlete']: r['actual'] for r in res['results']}
def pick_num(s):
    m = re.search(r'[Pp]ick\s*(\d+)', s)
    return int(m.group(1)) if m else None
def grade(pred, act):
    p = pred.lower(); n = pick_num(act); a = act.lower()
    if 'round 1' in p:
        in_r1 = (n is not None and n <= 30) or 'round 1' in a or 'first round' in a
        m = re.search(r'picks\s*1[\u2013-](\d+)', p)
        if m:
            hi = int(m.group(1))
            if n is None: return 'UNRESOLVED'
            if n <= hi: return 'HIT'
            return 'PARTIAL' if n <= 30 else 'MISS'
        return 'HIT' if in_r1 else 'MISS'
    return 'UNRESOLVED'
rows = []; hits = parts = miss = 0
for p in sealed['predictions']:
    a = actual.get(p['athlete'], 'NOT FOUND')
    g = grade(p['prediction'], a)
    hits += g == 'HIT'; parts += g == 'PARTIAL'; miss += g == 'MISS'
    rows.append((p['athlete'], p['prediction'], a, g))
    print('%-18s | %-28s | %-26s | %s' % (p['athlete'], p['prediction'], a, g))
print('')
print('SCORE: %d HIT / %d PARTIAL / %d MISS of %d' % (hits, parts, miss, len(rows)))
ts = datetime.datetime.utcnow().isoformat() + 'Z'
open('SEAL_REGISTRY.txt','a').write('%s | RESOLVED | h1:draft2026 | %dH/%dP/%dM\n' % (ts, hits, parts, miss))
html = ['<!-- H1 DRAFT2026 RESOLUTION %s -->' % ts]
html.append('<div style="border:1px solid rgba(124,155,110,.4);background:rgba(124,155,110,.08);border-radius:8px;padding:22px 24px;margin:10px 0 26px">')
html.append('<div style="font-family:JetBrains Mono,monospace;font-size:10px;font-weight:700;letter-spacing:2.4px;text-transform:uppercase;color:#7C9B6E;margin-bottom:10px">RESOLVED \u00b7 H1 \u00b7 2026 NBA DRAFT \u00b7 %dH / %dP / %dM</div>' % (hits, parts, miss))
for r in rows:
    color = {'HIT':'#7C9B6E','PARTIAL':'#EEC067','MISS':'#C97B6B'}.get(r[3], '#999')
    html.append('<div style="display:grid;grid-template-columns:150px 1fr 1fr 70px;gap:10px;padding:8px 0;border-top:1px solid rgba(248,244,237,.1);font-size:12.5px"><b>%s</b><span style="color:rgba(245,241,232,.7)">%s</span><span style="color:rgba(245,241,232,.7)">%s</span><b style="color:%s">%s</b></div>' % (r[0], r[1], r[2], color, r[3]))
html.append('<p style="font-size:12px;color:rgba(245,241,232,.6);margin:10px 0 0">Sealed June 11 2026 \u00b7 SHA efb0edd7f44ed87bcf0437c9531689fc3153f1fbe3e2b0688480614a37f55fe6 \u00b7 misses become calibration cases in the next release.</p></div>')
open('H1_RESOLUTION_BLOCK.html','w').write('\n'.join(html))
print('')
print('Wrote H1_RESOLUTION_BLOCK.html - paste to Claude for the splice blocks')
PYEOF
