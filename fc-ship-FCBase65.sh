#!/bin/bash
# fc-ship-FCBase65.sh · Trust page cross-linking (3 files)
set -e
G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; W='\033[1;37m'; N='\033[0m'
ROOT="$HOME/Desktop/fieldcheck-proxy"
DL="$HOME/Downloads"
TS=$(date +%Y%m%d-%H%M%S)
BAK="$ROOT/backups/FCBase65_$TS"
FILES="fieldcheck-agent-transparency.html fieldcheck-whats-new.html fieldcheck-methodology.html"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase65 . Trust page cross-linking${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

cd "$ROOT"
mkdir -p "$BAK"
for f in $FILES; do
  [ -f "$DL/$f" ] || { echo -e "  ${R}FAIL${N}: $f missing in Downloads"; exit 1; }
  cp -a "$ROOT/frontend/$f" "$BAK/" 2>/dev/null
  cp "$DL/$f" "$ROOT/frontend/$f"
  echo -e "  ${G}OK${N}  $f"
done
echo -e "  ${W}Backup:${N} $BAK"

# Deploy DEV
cd "$ROOT/frontend"
echo -e "\n${W}Deploy DEV${N}"
netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase65 trust cross-links" 2>&1 | tail -3
cd "$ROOT"

echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify on dev: open /agent-transparency, /whats-new, /methodology${N}"
echo -e "${Y}  Each footer should show all 4 trust pages (the page itself + 3 others)${N}"
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then exit 0; fi

cd "$ROOT/frontend"
netlify deploy --prod --dir=. --message="FCBase65 trust cross-links" 2>&1 | tail -3
cd "$ROOT"

F="$ROOT/freezes/FCBase65_$TS"
mkdir -p "$F/frontend"
for f in $FILES; do cp "$ROOT/frontend/$f" "$F/frontend/"; done

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase65 SHIPPED · 4 trust pages now symmetrically cross-linked${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
