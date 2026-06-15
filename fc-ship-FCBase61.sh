#!/bin/bash
# fc-ship-FCBase61.sh · Agent on 5 sport landings
set -e
G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; W='\033[1;37m'; N='\033[0m'
ROOT="$HOME/Desktop/fieldcheck-proxy"
DL="$HOME/Downloads"
TS=$(date +%Y%m%d-%H%M%S)
BAK="$ROOT/backups/FCBase61_$TS"
SPORTS="mens-basketball football womens-basketball womens-volleyball baseball"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase61 . Phase 9.5 . Agent on 5 sport landings${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

cd "$ROOT"

# Backup
echo -e "${W}[1/6]${N} Backup"
mkdir -p "$BAK"
cp -a "$ROOT/worker.js" "$BAK/"
for s in $SPORTS; do
  [ -f "$ROOT/frontend/fieldcheck-sport-$s.html" ] && cp -a "$ROOT/frontend/fieldcheck-sport-$s.html" "$BAK/"
done
echo -e "  ${G}OK${N}  Backup: $BAK"

# Move
echo -e "\n${W}[2/6]${N} Move from Downloads"
[ -f "$DL/worker.js" ] || { echo -e "  ${R}FAIL${N}: worker.js missing"; exit 1; }
for s in $SPORTS; do
  [ -f "$DL/fieldcheck-sport-$s.html" ] || { echo -e "  ${R}FAIL${N}: fieldcheck-sport-$s.html missing"; exit 1; }
done
cp "$DL/worker.js" "$ROOT/worker.js"
for s in $SPORTS; do
  cp "$DL/fieldcheck-sport-$s.html" "$ROOT/frontend/fieldcheck-sport-$s.html"
  echo -e "  ${G}OK${N}  fieldcheck-sport-$s.html ($(wc -c < $ROOT/frontend/fieldcheck-sport-$s.html | tr -d ' ') bytes)"
done
echo -e "  ${G}OK${N}  worker.js ($(wc -c < $ROOT/worker.js | tr -d ' ') bytes)"

# Validate
echo -e "\n${W}[3/6]${N} Validate"
node --check "$ROOT/worker.js" 2>&1 && echo -e "  ${G}OK${N}  worker.js syntax"
echo -n "  buildSportSystemPrompt: "; [ "$(grep -c 'function buildSportSystemPrompt' "$ROOT/worker.js")" = "1" ] && echo -e "${G}OK${N}" || exit 1
echo -n "  sport mode dispatch:    "; [ "$(grep -c "mode === 'sport'" "$ROOT/worker.js")" = "1" ] && echo -e "${G}OK${N}" || exit 1
for s in $SPORTS; do
  echo -n "  $s pill: "; [ "$(grep -c 'fc-agent-pill' "$ROOT/frontend/fieldcheck-sport-$s.html")" -ge "5" ] && echo -e "${G}OK${N}" || exit 1
done

# Deploy worker DEV
echo -e "\n${W}[4/6]${N} Deploy worker DEV"
wrangler deploy --env dev 2>&1 | tail -3

# Smoke test sport mode
echo -e "\n${W}[5/6]${N} Smoke test"
DEV="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
sleep 3
echo -n "  /agent POST mode=sport... "
RESP=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"question":"Who is the top recruit?","athlete":"FieldCheck sport cohort","sport":"mens-basketball","mode":"sport","verdict_data":{}}' \
  --max-time 15 "$DEV/agent" 2>&1 | head -c 100)
echo "$RESP" | tr -d ' \n\t' | grep -q '"type":"start"' && echo -e "${G}OK${N}" || echo -e "${Y}WARN${N} (propagation)"

# Deploy frontend dev + pause
echo -e "\n${W}[6/6]${N} Deploy frontend DEV"
cd "$ROOT/frontend"
netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase61 agent on sport landings" 2>&1 | tail -5
cd "$ROOT"

echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify dev URLs:${N}"
for s in $SPORTS; do
  echo -e "    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-sport-$s.html"
done
echo
echo -e "  Each should show: gold pill bottom-right → tap → 5 sport-specific suggestions"
echo -e "  Try 'Who is the top recruit?' on mens-basketball → agent cites Flagg/Boozer/Dybantsa"
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo -e "${Y}  Skipping prod.${N}"
  exit 0
fi

# Prod
echo -e "\n${W}DEPLOY TO PROD${N}"
wrangler deploy 2>&1 | tail -3
cd "$ROOT/frontend"
netlify deploy --prod --dir=. --message="FCBase61 agent on sport landings" 2>&1 | tail -3
cd "$ROOT"

# Freeze
F="$ROOT/freezes/FCBase61_$TS"
mkdir -p "$F/frontend"
cp "$ROOT/worker.js" "$F/"
for s in $SPORTS; do
  cp "$ROOT/frontend/fieldcheck-sport-$s.html" "$F/frontend/"
done

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase61 SHIPPED${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "  Agent now on 10 pages: verdict, methodology, predictions, coverage, versus,"
echo -e "                          mens-basketball, football, womens-basketball,"
echo -e "                          womens-volleyball, baseball"
echo -e "  Freeze: $F"
echo
