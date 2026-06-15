#!/bin/bash
# fc-ship-FCBase62.sh · Footer link backfill (frontend only, no worker)
set -e
G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; W='\033[1;37m'; N='\033[0m'
ROOT="$HOME/Desktop/fieldcheck-proxy"
DL="$HOME/Downloads"
TS=$(date +%Y%m%d-%H%M%S)
BAK="$ROOT/backups/FCBase62_$TS"
FILES="fieldcheck-verdict.html fieldcheck-methodology.html fieldcheck-predictions.html fieldcheck-coverage.html fieldcheck-versus.html"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase62 . Footer link backfill (frontend only)${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

cd "$ROOT"

# Backup + move + validate
echo -e "${W}[1/4]${N} Backup + move"
mkdir -p "$BAK"
for f in $FILES; do
  [ -f "$DL/$f" ] || { echo -e "  ${R}FAIL${N}: $f missing in Downloads"; exit 1; }
  cp -a "$ROOT/frontend/$f" "$BAK/" 2>/dev/null
  cp "$DL/$f" "$ROOT/frontend/$f"
  LINKS=$(grep -c "/agent-transparency" "$ROOT/frontend/$f")
  [ "$LINKS" -ge "1" ] && echo -e "  ${G}OK${N}  $f" || { echo -e "  ${R}FAIL${N}: $f no /agent-transparency link"; exit 1; }
done
# Also handle verdict.html alias
cp "$DL/fieldcheck-verdict.html" "$ROOT/frontend/verdict.html" 2>/dev/null
echo -e "  ${W}Backup:${N} $BAK"

# Deploy DEV
echo -e "\n${W}[2/4]${N} Deploy DEV"
cd "$ROOT/frontend"
netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase62 footer transparency link" 2>&1 | tail -3
cd "$ROOT"

echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify on dev:${N}"
echo -e "  Open any agent page, tap the gold pill, look at the footer text."
echo -e "  Should now say: 'Powered by Claude · 10 questions/day · see the prompt'"
echo -e "  Clicking 'see the prompt' goes to /agent-transparency"
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then exit 0; fi

# Prod
echo -e "\n${W}[3/4]${N} Deploy PROD"
cd "$ROOT/frontend"
netlify deploy --prod --dir=. --message="FCBase62 footer transparency link" 2>&1 | tail -3
cd "$ROOT"

# Freeze
echo -e "\n${W}[4/4]${N} Freeze"
F="$ROOT/freezes/FCBase62_$TS"
mkdir -p "$F/frontend"
for f in $FILES; do cp "$ROOT/frontend/$f" "$F/frontend/"; done

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase62 SHIPPED · all 10 agent pages now cross-link to /agent-transparency${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
