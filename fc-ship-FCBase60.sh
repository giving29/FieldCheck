#!/bin/bash
# fc-ship-FCBase60.sh · Agent transparency page (single new file)
set -e
G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; W='\033[1;37m'; N='\033[0m'
ROOT="$HOME/Desktop/fieldcheck-proxy"
DL="$HOME/Downloads"
TS=$(date +%Y%m%d-%H%M%S)
BAK="$ROOT/backups/FCBase60_$TS"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase60 . Phase 9.4 . Agent transparency page${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

cd "$ROOT"

# Backup _redirects (only file modified, plus we add a brand-new HTML)
mkdir -p "$BAK"
[ -f "$ROOT/frontend/_redirects" ] && cp -a "$ROOT/frontend/_redirects" "$BAK/"
echo -e "  ${G}OK${N}  Backup: $BAK"

# Move new file
[ -f "$DL/fieldcheck-agent-transparency.html" ] || { echo -e "  ${R}FAIL${N}: fieldcheck-agent-transparency.html missing from Downloads"; exit 1; }
cp "$DL/fieldcheck-agent-transparency.html" "$ROOT/frontend/fieldcheck-agent-transparency.html"
SIZE=$(wc -c < "$ROOT/frontend/fieldcheck-agent-transparency.html" | tr -d ' ')
echo -e "  ${G}OK${N}  fieldcheck-agent-transparency.html ($SIZE bytes)"

# Add /agent-transparency clean URL to _redirects if not already there
if ! grep -q "/agent-transparency" "$ROOT/frontend/_redirects" 2>/dev/null; then
  # Insert before the catch-all 404 line
  if grep -q "^/\*" "$ROOT/frontend/_redirects" 2>/dev/null; then
    # Use sed to insert before /*
    sed -i.bak '/^\/\*/i\
/agent-transparency  /fieldcheck-agent-transparency.html  200
' "$ROOT/frontend/_redirects"
    rm -f "$ROOT/frontend/_redirects.bak"
  else
    # Just append
    echo "/agent-transparency  /fieldcheck-agent-transparency.html  200" >> "$ROOT/frontend/_redirects"
  fi
  echo -e "  ${G}OK${N}  Added /agent-transparency clean URL to _redirects"
else
  echo -e "  ${Y}skip${N}: /agent-transparency already in _redirects"
fi

# Validate HTML inline scripts
RESULT=$(node -e "
const fs = require('fs');
const html = fs.readFileSync('$ROOT/frontend/fieldcheck-agent-transparency.html', 'utf8');
const scripts = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g) || [];
let ok = 0;
for (const s of scripts) {
  const code = s.replace(/<script[^>]*>/, '').replace(/<\/script>/, '');
  try { new Function(code); ok++; } catch (e) {}
}
console.log(ok + '/' + scripts.length);
")
echo -e "  ${G}OK${N}  HTML inline scripts: $RESULT"

# Deploy frontend dev
cd "$ROOT/frontend"
echo -e "\n${W}Deploy DEV${N}"
netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase60 agent transparency page" 2>&1 | tail -5
cd "$ROOT"

echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify dev:${N}"
echo
echo -e "  Clean URL:      https://fieldcheck-dev--fieldcheck-app.netlify.app/agent-transparency"
echo -e "  Direct file:    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-agent-transparency.html"
echo
echo -e "  ${W}What to check:${N}"
echo -e "  - 4-stat strip at top (loads from /agent/stats)"
echo -e "  - 5 mode cards with system prompts visible"
echo -e "  - 'Try -> [page]' buttons work and route to live pages"
echo -e "  - 'Audit' section explains how to inspect agent traffic"
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo -e "${Y}  Skipping prod.${N}"
  exit 0
fi

# Prod (no worker changes - frontend only)
cd "$ROOT/frontend"
netlify deploy --prod --dir=. --message="FCBase60 agent transparency" 2>&1 | tail -3
cd "$ROOT"

# Freeze
F="$ROOT/freezes/FCBase60_$TS"
mkdir -p "$F/frontend"
cp "$ROOT/frontend/fieldcheck-agent-transparency.html" "$F/frontend/"
cp "$ROOT/frontend/_redirects" "$F/frontend/"

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase60 SHIPPED${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "  Live: https://fieldcheck-app.netlify.app/agent-transparency"
echo -e "  Freeze: $F"
echo
