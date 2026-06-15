#!/bin/bash
P=0; F=0
PX="https://fieldcheck-proxy.sridhar-nallani.workers.dev"
ST="https://fieldcheck-app.netlify.app"
echo "── FieldCheck QA ──"
for f in worker.js index.html mypath.html trust.html news.html pricing.html wire.html; do
  [ -f "$f" ] && { echo "✓ $f"; P=$((P+1)); } || { echo "✗ MISSING $f"; F=$((F+1)); }
done
node --check worker.js 2>&1 && { echo "✓ worker.js syntax"; P=$((P+1)); } || { echo "✗ worker.js syntax"; F=$((F+1)); }
grep -nE "^[[:space:]]+—" worker.js && { echo "✗ orphan em-dash"; F=$((F+1)); } || { echo "✓ no orphan em-dash"; P=$((P+1)); }
for ep in /health /badge.js /trending /nil/calibration /calendar; do
  c=$(curl -s -o /dev/null -w "%{http_code}" "$PX$ep")
  [ "$c" = "200" ] && { echo "✓ worker $ep ($c)"; P=$((P+1)); } || { echo "✗ worker $ep ($c)"; F=$((F+1)); }
done
for pg in / /mypath.html /trust.html /news.html /pricing.html /wire.html; do
  c=$(curl -s -o /dev/null -w "%{http_code}" "$ST$pg")
  [ "$c" = "200" ] && { echo "✓ site $pg ($c)"; P=$((P+1)); } || { echo "✗ site $pg ($c)"; F=$((F+1)); }
done
echo "── Pass: $P  Fail: $F ──"
[ $F -gt 0 ] && exit 1 || exit 0
