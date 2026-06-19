#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="index.html"

if [ ! -f "$F" ]; then
  echo "ABORT :: $F not found in $WS"
  exit 1
fi

if grep -q "if(!v||!v.trim()){ closeAC(); return; }" "$F"; then
  echo "Already patched — search will not show the top list on empty. Nothing to do."
  exit 0
fi

cp "$F" "$F.bak.$(date +%Y%m%d_%H%M)"
echo "backed up $F"

python3 - <<'PY'
f="index.html"
s=open(f).read()
old="function renderAC(v){\n  if(!_acd)return;\n  acF=getSug(v);"
new="function renderAC(v){\n  if(!_acd)return;\n  if(!v||!v.trim()){ closeAC(); return; }\n  acF=getSug(v);"
if old not in s:
    raise SystemExit("ANCHOR NOT FOUND — renderAC may have changed; not patching")
s=s.replace(old,new,1)
open(f,"w").write(s)
print("patched renderAC — empty input now closes the dropdown")
PY

echo ""
echo "DONE. The top list no longer auto-shows; typing still narrows."
echo "Preview:  open index.html"
echo "Ship to DEV:  bash fc-deploy-dev.sh"
