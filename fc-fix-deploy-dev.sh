#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="deploy-dev.sh"

if [ ! -f "$F" ]; then
  echo "ABORT :: $F not found in $WS"
  exit 1
fi

if grep -q "preserve live routes" "$F"; then
  echo "Already patched — $F preserves live _redirects. Nothing to do."
  exit 0
fi

cp "$F" "$F.bak.$(date +%Y%m%d_%H%M)"
echo "backed up $F"

python3 - <<'PY'
f="deploy-dev.sh"
s=open(f).read()
start=s.index("# \u2500\u2500 WRITE CORRECT _REDIRECTS")
end=s.index('ok "_redirects enforced"')+len('ok "_redirects enforced"')
new='''# \u2500\u2500 _REDIRECTS \u00b7 preserve live routes, add dev-only /roadmap \u2500\u2500
hdr "_REDIRECTS"
[ -f "$P/_redirects" ] || fail "_redirects missing \u2014 refusing to deploy without routing"
if ! grep -q '^/roadmap ' "$P/_redirects"; then
  awk 'BEGIN{d=0} /^\\/\\*/ && d==0 {print "/roadmap                  /fieldcheck-roadmap.html          200"; d=1} {print}' "$P/_redirects" > "$P/_redirects.tmp"
  mv "$P/_redirects.tmp" "$P/_redirects"
fi
ok "_redirects preserved (full live routes + dev-only /roadmap)"'''
s=s[:start]+new+s[end:]
open(f,"w").write(s)
print("patched _redirects logic in deploy-dev.sh")
PY

echo ""
echo "DONE. deploy-dev.sh now preserves your live _redirects."
echo "Original saved as $F.bak.*"
echo "Quick check (should show 'preserve live routes'):"
grep -n "preserve live routes" "$F"
