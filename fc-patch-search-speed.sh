#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="fieldcheck-verdict.html"

if [ ! -f "$F" ]; then
  echo "ABORT :: $F not found in $WS"
  exit 1
fi

OLD='Object.assign({},payloadS,{skipCache:true})'
NEW='Object.assign({},payloadS,{skipCache:false})'

if ! grep -qF "$OLD" "$F"; then
  if grep -qF "$NEW" "$F"; then
    echo "Already patched — media supplement uses cache. Nothing to do."
    exit 0
  fi
  echo "ABORT :: anchor not found (code may have changed); not patching"
  exit 1
fi

cp "$F" "$F.bak.$(date +%Y%m%d_%H%M)"
echo "backed up $F"

python3 - <<PY
f="fieldcheck-verdict.html"
s=open(f).read()
s=s.replace("Object.assign({},payloadS,{skipCache:true})","Object.assign({},payloadS,{skipCache:false})",1)
open(f,"w").write(s)
print("patched: media supplement now uses cache (skipCache:false)")
PY

echo ""
echo "DONE. Marquee verdicts no longer regenerate just to fetch media."
echo "Ship to DEV:  bash fc-dev.sh"
