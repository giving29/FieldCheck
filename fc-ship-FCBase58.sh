#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
# fc-ship-FCBase58.sh · FCBase58 · Agent obs + methodology mode
# ══════════════════════════════════════════════════════════════════════════
#
# Ships:
#   worker.js                       (adds /agent/stats + mode parameter + counters)
#   fieldcheck-methodology.html     (adds agent chat UI with mode=methodology)
# ══════════════════════════════════════════════════════════════════════════

set -e
G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; B='\033[0;36m'; W='\033[1;37m'; N='\033[0m'

ROOT="$HOME/Desktop/fieldcheck-proxy"
DOWNLOADS="$HOME/Downloads"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$ROOT/backups/FCBase58_$TIMESTAMP"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase58 . Phase 9.2 . Agent observability + methodology mode${N}"
echo -e "${W}  Started: $(date)${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

# Sanity
echo -e "${B}[1/7]${N} Sanity"
cd "$ROOT" || { echo "FAIL"; exit 1; }
echo -e "  ${G}OK${N}  cwd: $ROOT"

# Backup
echo -e "\n${B}[2/7]${N} Backup"
mkdir -p "$BACKUP_DIR"
cp -a "$ROOT/worker.js" "$BACKUP_DIR/" && echo -e "  ${G}OK${N}  worker.js"
cp -a "$ROOT/frontend/fieldcheck-methodology.html" "$BACKUP_DIR/" 2>/dev/null && echo -e "  ${G}OK${N}  fieldcheck-methodology.html"
echo -e "  ${W}Backup:${N} $BACKUP_DIR"

# Move from Downloads
echo -e "\n${B}[3/7]${N} Move from Downloads"
[ -f "$DOWNLOADS/worker.js" ] || { echo -e "  ${R}FAIL${N}: worker.js missing"; exit 1; }
[ -f "$DOWNLOADS/fieldcheck-methodology.html" ] || { echo -e "  ${R}FAIL${N}: fieldcheck-methodology.html missing"; exit 1; }
cp "$DOWNLOADS/worker.js" "$ROOT/worker.js"
cp "$DOWNLOADS/fieldcheck-methodology.html" "$ROOT/frontend/fieldcheck-methodology.html"
echo -e "  ${G}OK${N}  worker.js ($(wc -c < $ROOT/worker.js | tr -d ' ') bytes)"
echo -e "  ${G}OK${N}  fieldcheck-methodology.html ($(wc -c < $ROOT/frontend/fieldcheck-methodology.html | tr -d ' ') bytes)"

# Validate
echo -e "\n${B}[4/7]${N} Validate"
node --check "$ROOT/worker.js" 2>&1 && echo -e "  ${G}OK${N}  worker.js syntax"
echo -n "  /agent/stats route:    "; [ "$(grep -c "path === '/agent/stats'" "$ROOT/worker.js")" = "1" ] && echo -e "${G}OK${N}" || { echo -e "${R}FAIL${N}"; exit 1; }
echo -n "  handleAgentStats fn:   "; [ "$(grep -c "async function handleAgentStats" "$ROOT/worker.js")" = "1" ] && echo -e "${G}OK${N}" || { echo -e "${R}FAIL${N}"; exit 1; }
echo -n "  mode parameter:        "; [ "$(grep -c "mode = 'verdict'" "$ROOT/worker.js")" = "1" ] && echo -e "${G}OK${N}" || { echo -e "${R}FAIL${N}"; exit 1; }
echo -n "  methodology pill:      "; [ "$(grep -c "fc-agent-pill" "$ROOT/frontend/fieldcheck-methodology.html")" -ge "5" ] && echo -e "${G}OK${N}" || { echo -e "${R}FAIL${N}"; exit 1; }
echo -n "  methodology mode:      "; grep -q "mode: 'methodology'" "$ROOT/frontend/fieldcheck-methodology.html" && echo -e "${G}OK${N}" || { echo -e "${R}FAIL${N}"; exit 1; }

# Deploy worker dev
echo -e "\n${B}[5/7]${N} Deploy worker DEV"
wrangler deploy --env dev 2>&1 | tail -5

# Smoke test (with proper whitespace handling)
echo -e "\n${B}[6/7]${N} Smoke test DEV"
DEV_BASE="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
sleep 3  # Worker propagation
echo -n "  /agent/stats GET... "
RESP=$(curl -s "$DEV_BASE/agent/stats")
if echo "$RESP" | tr -d ' \n\t' | grep -q '"generated_at"'; then
  echo -e "${G}OK${N}"
  echo "$RESP" | head -c 300
  echo ""
else
  echo -e "${Y}WARN${N}: unexpected response"
  echo "  $RESP" | head -c 200
fi

# Deploy frontend dev + pause
echo -e "\n${B}[7/7]${N} Deploy frontend DEV + verify"
cd "$ROOT/frontend"
netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase58 agent obs + methodology mode" 2>&1 | tail -8
cd "$ROOT"

echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify dev BEFORE promoting to PROD:${N}"
echo
echo -e "  ${W}Test URLs:${N}"
echo -e "    1. Methodology page with agent (NEW):"
echo -e "       https://fieldcheck-dev--fieldcheck-app.netlify.app/methodology"
echo -e "    2. Verdict page (regression check, should still work):"
echo -e "       https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cooper+Flagg&sport=mens-basketball"
echo -e "    3. Stats endpoint (raw JSON):"
echo -e "       https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev/agent/stats"
echo
echo -e "  ${W}What to check on /methodology:${N}"
echo -e "    - Gold pulse pill bottom-right"
echo -e "    - Tap → chat panel opens"
echo -e "    - 5 methodology-flavored suggested questions (NOT athlete-specific)"
echo -e "    - 'What is the difference between ELITE and STAR?'"
echo -e "    - Answer streams character-by-character"
echo -e "    - Agent stays in 'methodology mode' (explains rules, not athletes)"
echo
echo -e "  ${W}Verdict regression check:${N}"
echo -e "    - Verdict agent still works the same way (athlete-specific)"
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo -e "${Y}  Skipping prod. Dev has FCBase58, prod still on FCBase57.${N}"
  echo -e "  ${W}Backup:${N} $BACKUP_DIR"
  exit 0
fi

# Prod
echo -e "\n${W}DEPLOY TO PROD${N}"
wrangler deploy 2>&1 | tail -3
cd "$ROOT/frontend"
netlify deploy --prod --dir=. --message="FCBase58 agent obs + methodology mode" 2>&1 | tail -3
cd "$ROOT"

# Freeze
FREEZE_DIR="$ROOT/freezes/FCBase58_$TIMESTAMP"
mkdir -p "$FREEZE_DIR/frontend"
cp "$ROOT/worker.js" "$FREEZE_DIR/"
cp "$ROOT/frontend/fieldcheck-methodology.html" "$FREEZE_DIR/frontend/"

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase58 SHIPPED${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "  Prod:   https://fieldcheck-app.netlify.app/methodology"
echo -e "  Stats:  https://fieldcheck-proxy.sridhar-nallani.workers.dev/agent/stats"
echo -e "  Freeze: $FREEZE_DIR"
echo
