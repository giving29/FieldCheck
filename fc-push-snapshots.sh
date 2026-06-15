set -e
cd ~/Desktop/fieldcheck-proxy
F=${1:?usage: bash fc-push-snapshots.sh athletes.json [release-tag] [dev]}
TAG=${2:-FCBase89}
ENV=${3:-prod}
if [ ! -f "$F" ]; then echo "ABORT: $F not found"; exit 1; fi
if [ ! -f .fc_snapshot_key ]; then echo "ABORT: .fc_snapshot_key missing"; exit 1; fi
W="https://fieldcheck-proxy.sridhar-nallani.workers.dev"
if [ "$ENV" = "dev" ]; then W="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"; fi
python3 - "$F" "$TAG" << 'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
items = d if isinstance(d, list) else d.get('athletes') or d.get('results') or []
out = []
for it in items:
    nm = it.get('name') or it.get('player') or it.get('athlete')
    cp = it.get('composite', it.get('score'))
    tr = it.get('tier', '')
    try: cp = float(cp)
    except: continue
    if nm and cp > 0: out.append({'name': str(nm).strip(), 'composite': round(cp, 2), 'tier': str(tr)})
assert out, 'no valid athletes parsed'
blob = json.dumps(out)
assert 'FILL' not in blob and 'Test Athlete' not in blob, 'ABORT: placeholder/test data in batch'
json.dump({'release': sys.argv[2], 'athletes': out}, open('/tmp/fc_push_payload.json', 'w'))
print('payload: %d athletes, release %s' % (len(out), sys.argv[2]))
PYEOF
echo "pushing to $ENV ..."
curl -s -X POST "$W/movement/snapshot" -H "Content-Type: application/json" -H "X-FC-KEY: $(cat .fc_snapshot_key)" --data-binary @/tmp/fc_push_payload.json
echo ""
echo "feed after push:"
curl -s "$W/movement/feed" | head -c 400
echo ""
