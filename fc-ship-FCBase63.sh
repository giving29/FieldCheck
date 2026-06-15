#!/bin/bash
# fc-ship-FCBase63.sh · /whats-new feed page
set -e
G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; W='\033[1;37m'; N='\033[0m'
ROOT="$HOME/Desktop/fieldcheck-proxy"
DL="$HOME/Downloads"
TS=$(date +%Y%m%d-%H%M%S)
BAK="$ROOT/backups/FCBase63_$TS"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase63 . /whats-new feed page${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

cd "$ROOT"
mkdir -p "$BAK"
[ -f "$ROOT/frontend/_redirects" ] && cp -a "$ROOT/frontend/_redirects" "$BAK/"
echo -e "  ${G}OK${N}  Backup: $BAK"

# Move
[ -f "$DL/fieldcheck-whats-new.html" ] || { echo -e "  ${R}FAIL${N}: fieldcheck-whats-new.html missing"; exit 1; }
cp "$DL/fieldcheck-whats-new.html" "$ROOT/frontend/fieldcheck-whats-new.html"
echo -e "  ${G}OK${N}  fieldcheck-whats-new.html ($(wc -c < $ROOT/frontend/fieldcheck-whats-new.html | tr -d ' ') bytes)"

# Add /whats-new clean URL
if ! grep -q "/whats-new" "$ROOT/frontend/_redirects" 2>/dev/null; then
  if grep -q "^/\*" "$ROOT/frontend/_redirects" 2>/dev/null; then
    sed -i.bak '/^\/\*/i\
/whats-new  /fieldcheck-whats-new.html  200
' "$ROOT/frontend/_redirects"
    rm -f "$ROOT/frontend/_redirects.bak"
  else
    echo "/whats-new  /fieldcheck-whats-new.html  200" >> "$ROOT/frontend/_redirects"
  fi
  echo -e "  ${G}OK${N}  Added /whats-new clean URL"
fi

# Deploy DEV
cd "$ROOT/frontend"
echo -e "\n${W}Deploy DEV${N}"
netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase63 whats-new feed" 2>&1 | tail -3
cd "$ROOT"

echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify: https://fieldcheck-dev--fieldcheck-app.netlify.app/whats-new${N}"
echo -e "${Y}  10 ship cards today + earlier eras collapsed below${N}"
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then exit 0; fi

cd "$ROOT/frontend"
netlify deploy --prod --dir=. --message="FCBase63 whats-new feed" 2>&1 | tail -3
cd "$ROOT"

F="$ROOT/freezes/FCBase63_$TS"
mkdir -p "$F/frontend"
cp "$ROOT/frontend/fieldcheck-whats-new.html" "$F/frontend/"
cp "$ROOT/frontend/_redirects" "$F/frontend/"

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase63 SHIPPED · /whats-new live${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "  Live: https://fieldcheck-app.netlify.app/whats-new"
