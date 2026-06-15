set -e
cd ~/Desktop/fieldcheck-proxy
F=${1:-h1_draft2026.json}
if [ ! -f "$F" ]; then echo "ABORT: $F not found - create the batch file first"; exit 1; fi
python3 - "$F" << 'PYEOF'
import json, hashlib, sys, datetime
f = sys.argv[1]
data = json.load(open(f))
assert isinstance(data.get('predictions'), list) and len(data['predictions']) >= 1, 'predictions[] required'
for p in data['predictions']:
    for k in ['athlete','sport','composite','tier','prediction','resolver','resolve_by']:
        assert k in p, 'missing field %s in %s' % (k, p.get('athlete','?'))
    assert float(p['composite']) > 0, 'ABORT: composite is 0.0 for %s - fill real verdicts first' % p['athlete']
    blob = json.dumps(p)
    assert 'FILL' not in blob, 'ABORT: FILL placeholder still present in %s' % p['athlete']
data['sealed_at_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
data['horizon'] = data.get('horizon','H1')
data['batch'] = data.get('batch','draft2026')
canonical = json.dumps(data, sort_keys=True, separators=(',',':'))
sha = hashlib.sha256(canonical.encode()).hexdigest()
sealed = f.replace('.json','') + '.SEALED.' + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M') + '.json'
open(sealed,'w').write(canonical)
open('SEAL_REGISTRY.txt','a').write('%s | %s:%s | %d predictions | SHA256 %s\n' % (data['sealed_at_utc'], data['horizon'], data['batch'], len(data['predictions']), sha))
print('SEALED FILE:', sealed)
print('SHA256:', sha)
print('KV_CMD: npx wrangler kv key put --binding=FIELDCHECK_KV "pred:%s:%s" --path "%s" --remote' % (data['horizon'].lower(), data['batch'], sealed))
PYEOF
echo ""
echo "Run the KV_CMD line printed above to publish the sealed batch to KV, then:"
echo "  tar -czf freezes/PRED_SEAL_$(date +%Y%m%d_%H%M).tar.gz *.SEALED.*.json SEAL_REGISTRY.txt"
