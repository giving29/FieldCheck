#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="index.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if ! grep -q 'href="/fc_canonical_state_v1"' "$F"; then echo "Already repointed. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.howitworks.$(date +%Y%m%d_%H%M)"
echo "backed up $F"
python3 - <<'PY'
f="index.html"; s=open(f).read()
n=s.count('href="/fc_canonical_state_v1"')
s=s.replace('href="/fc_canonical_state_v1"','href="/methodology"')
open(f,"w").write(s)
print("repointed %d home link(s) -> /methodology (How it works + Methodology footer)"%n)
PY
echo ""; echo "Ship to DEV:  bash fc-dev.sh"
