#!/bin/bash
# fc-ship-FCBase59.sh · Agent everywhere (3 more pages)
set -e
G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; B='\033[0;36m'; W='\033[1;37m'; N='\033[0m'
ROOT="$HOME/Desktop/fieldcheck-proxy"
DL="$HOME/Downloads"
TS=$(date +%Y%m%d-%H%M%S)
BAK="$ROOT/backups/FCBase59_$TS"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase59 . Phase 9.3 . Agent everywhere (predictions/coverage/versus)${N}"
echo -e "${W}  Started: $(date)${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

cd "$ROOT"

# Backup
echo -e "${B}[1/6]${N} Backup"
mkdir -p "$BAK"
cp -a "$ROOT/worker.js" "$BAK/"
for f in fieldcheck-predictions.html fieldcheck-coverage.html fieldcheck-versus.html; do
  [ -f "$ROOT/frontend/$f" ] && cp -a "$ROOT/frontend/$f" "$BAK/" && echo -e "  ${G}OK${N}  $f"
done
echo -e "  ${W}Backup:${N} $BAK"

# Move from Downloads
echo -e "\n${B}[2/6]${N} Move from Downloads"
for f in worker.js fieldcheck-predictions.html fieldcheck-coverage.html fieldcheck-versus.html; do
  [ -f "$DL/$f" ] || { echo -e "  ${R}FAIL${N}: $f missing"; exit 1; }
done
cp "$DL/worker.js" "$ROOT/worker.js"
for f in fieldcheck-predictions.html fieldcheck-coverage.html fieldcheck-versus.html; do
  cp "$DL/$f" "$ROOT/frontend/$f"
  echo -e "  ${G}OK${N}  $f ($(wc -c < $ROOT/frontend/$f | tr -d ' ') bytes)"
done
echo -e "  ${G}OK${N}  worker.js ($(wc -c < $ROOT/worker.js | tr -d ' ') bytes)"

# Validate
echo -e "\n${B}[3/6]${N} Validate"
node --check "$ROOT/worker.js" 2>&1 && echo -e "  ${G}OK${N}  worker.js syntax"
echo -n "  buildPredictionsSystemPrompt: "; [ "$(grep -c 'function buildPredictionsSystemPrompt' "$ROOT/worker.js")" = "1" ] && echo -e "${G}OK${N}" || exit 1
echo -n "  buildCoverageSystemPrompt:    "; [ "$(grep -c 'function buildCoverageSystemPrompt' "$ROOT/worker.js")" = "1" ] && echo -e "${G}OK${N}" || exit 1
echo -n "  buildComparisonSystemPrompt:  "; [ "$(grep -c 'function buildComparisonSystemPrompt' "$ROOT/worker.js")" = "1" ] && echo -e "${G}OK${N}" || exit 1
for f in fieldcheck-predictions.html fieldcheck-coverage.html fieldcheck-versus.html; do
  echo -n "  $f pill: "; [ "$(grep -c 'fc-agent-pill' "$ROOT/frontend/$f")" -ge "5" ] && echo -e "${G}OK${N}" || exit 1
done

# Deploy DEV
echo -e "\n${B}[4/6]${N} Deploy worker DEV"
wrangler deploy --env dev 2>&1 | tail -3

# Smoke test
echo -e "\n${B}[5/6]${N} Smoke test"
DEV="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
sleep 3
echo -n "  /agent POST mode=predictions... "
RESP=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"question":"How are predictions verified?","athlete":"FieldCheck predictions","sport":null,"mode":"predictions","verdict_data":{}}' \
  --max-time 15 "$DEV/agent" 2>&1 | head -c 100)
echo "$RESP" | tr -d ' \n\t' | grep -q '"type":"start"' && echo -e "${G}OK${N}" || echo -e "${Y}WARN${N} (may need a moment to propagate)"

# Deploy frontend dev + pause
echo -e "\n${B}[6/6]${N} Deploy frontend DEV + verify"
cd "$ROOT/frontend"
netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase59 agent on predictions/coverage/versus" 2>&1 | tail -5
cd "$ROOT"

echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify dev:${N}"
echo
echo -e "  /predictions  → agent asks about sealed ledger"
echo -e "    https://fieldcheck-dev--fieldcheck-app.netlify.app/predictions"
echo
echo -e "  /coverage     → agent asks about coverage scope"
echo -e "    https://fieldcheck-dev--fieldcheck-app.netlify.app/coverage"
echo
echo -e "  /versus       → agent does cross-athlete comparison"
echo -e "    https://fieldcheck-dev--fieldcheck-app.netlify.app/versus?a=Cooper+Flagg&b=LeBron+James"
echo
echo -e "  /methodology  → agent still works (regression check)"
echo -e "  /verdict      → agent still works (regression check)"
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo -e "${Y}  Skipping prod. Dev has FCBase59, prod still on FCBase58.${N}"
  exit 0
fi

# Prod
echo -e "\n${W}DEPLOY TO PROD${N}"
wrangler deploy 2>&1 | tail -3
cd "$ROOT/frontend"
netlify deploy --prod --dir=. --message="FCBase59 agent everywhere" 2>&1 | tail -3
cd "$ROOT"

# Freeze
F="$ROOT/freezes/FCBase59_$TS"
mkdir -p "$F/frontend"
cp "$ROOT/worker.js" "$F/"
for f in fieldcheck-predictions.html fieldcheck-coverage.html fieldcheck-versus.html; do
  cp "$ROOT/frontend/$f" "$F/frontend/"
done

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase59 SHIPPED${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "  Prod: https://fieldcheck-app.netlify.app/"
echo -e "  Agent now on: /verdict, /methodology, /predictions, /coverage, /versus"
echo -e "  Freeze: $F"
echo
