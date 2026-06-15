#!/bin/bash
# fc-ship-FCBase64.sh · /outcomes retrospective grading page
set -e
G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; W='\033[1;37m'; N='\033[0m'
ROOT="$HOME/Desktop/fieldcheck-proxy"
DL="$HOME/Downloads"
TS=$(date +%Y%m%d-%H%M%S)
BAK="$ROOT/backups/FCBase64_$TS"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase64 . /outcomes retrospective grading${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

cd "$ROOT"
mkdir -p "$BAK"
[ -f "$ROOT/frontend/_redirects" ] && cp -a "$ROOT/frontend/_redirects" "$BAK/"
echo -e "  ${G}OK${N}  Backup: $BAK"

[ -f "$DL/fieldcheck-outcomes.html" ] || { echo -e "  ${R}FAIL${N}: fieldcheck-outcomes.html missing"; exit 1; }
cp "$DL/fieldcheck-outcomes.html" "$ROOT/frontend/fieldcheck-outcomes.html"
echo -e "  ${G}OK${N}  fieldcheck-outcomes.html ($(wc -c < $ROOT/frontend/fieldcheck-outcomes.html | tr -d ' ') bytes)"

# Clean URL
if ! grep -q "^/outcomes" "$ROOT/frontend/_redirects" 2>/dev/null; then
  if grep -q "^/\*" "$ROOT/frontend/_redirects" 2>/dev/null; then
    sed -i.bak '/^\/\*/i\
/outcomes  /fieldcheck-outcomes.html  200
' "$ROOT/frontend/_redirects"
    rm -f "$ROOT/frontend/_redirects.bak"
  else
    echo "/outcomes  /fieldcheck-outcomes.html  200" >> "$ROOT/frontend/_redirects"
  fi
  echo -e "  ${G}OK${N}  Added /outcomes clean URL"
fi

# Deploy DEV
cd "$ROOT/frontend"
echo -e "\n${W}Deploy DEV${N}"
netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase64 outcomes ledger" 2>&1 | tail -3
cd "$ROOT"

echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify: https://fieldcheck-dev--fieldcheck-app.netlify.app/outcomes${N}"
echo -e "${Y}  6 case cards: 4 hits (Jokic/Giannis/Clark/Luka) + 2 misses (Bennett/Bowie)${N}"
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then exit 0; fi

cd "$ROOT/frontend"
netlify deploy --prod --dir=. --message="FCBase64 outcomes ledger" 2>&1 | tail -3
cd "$ROOT"

F="$ROOT/freezes/FCBase64_$TS"
mkdir -p "$F/frontend"
cp "$ROOT/frontend/fieldcheck-outcomes.html" "$F/frontend/"
cp "$ROOT/frontend/_redirects" "$F/frontend/"

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase64 SHIPPED · /outcomes live${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "  Live: https://fieldcheck-app.netlify.app/outcomes"
