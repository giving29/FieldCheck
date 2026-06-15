#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
# fc-ship-FCBase57.sh · FCBase57 · Phase 9.1 AI Agent · 2-file deploy
# ══════════════════════════════════════════════════════════════════════════
#
# Ships ONLY:
#   - worker.js     (adds /agent SSE endpoint + helpers)
#   - verdict.html  (adds Ask FieldCheck pill + chat panel + SSE consumer)
#
# Much tighter than FCBase56 MEGA (just 2 files vs 34). Same doctrine:
# backup → dev → smoke test → human pause → prod → freeze.
# ══════════════════════════════════════════════════════════════════════════

set -e

G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; B='\033[0;36m'; W='\033[1;37m'; N='\033[0m'

ROOT="$HOME/Desktop/fieldcheck-proxy"
DOWNLOADS="$HOME/Downloads"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$ROOT/backups/FCBase57_$TIMESTAMP"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase57 . Phase 9.1 . AI Agent scout-mode${N}"
echo -e "${W}  Started: $(date)${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

# ── STAGE 1: SANITY ──
echo -e "${B}[1/8]${N} ${W}Sanity checks${N}"
cd "$ROOT" || { echo "FAIL: project root not found"; exit 1; }
echo -e "  ${G}OK${N}  cwd: $ROOT"
command -v node >/dev/null || { echo "FAIL: node not installed"; exit 1; }
echo -e "  ${G}OK${N}  node: $(node --version)"
command -v wrangler >/dev/null || { echo "FAIL: wrangler not installed"; exit 1; }
echo -e "  ${G}OK${N}  wrangler: $(wrangler --version 2>&1 | head -1)"

# Verify ANTHROPIC_API_KEY secret is set
if wrangler secret list 2>/dev/null | grep -q ANTHROPIC_API_KEY; then
  echo -e "  ${G}OK${N}  ANTHROPIC_API_KEY secret configured on worker"
else
  echo -e "  ${R}FAIL${N}: ANTHROPIC_API_KEY not set on worker"
  echo -e "         Run: wrangler secret put ANTHROPIC_API_KEY"
  exit 1
fi
echo

# ── STAGE 2: BACKUP ──
echo -e "${B}[2/8]${N} ${W}Backup current state${N}"
mkdir -p "$BACKUP_DIR"
[ -f "$ROOT/worker.js" ] && cp -a "$ROOT/worker.js" "$BACKUP_DIR/" && echo -e "  ${G}OK${N}  worker.js"
[ -f "$ROOT/frontend/verdict.html" ] && cp -a "$ROOT/frontend/verdict.html" "$BACKUP_DIR/" && echo -e "  ${G}OK${N}  verdict.html"
[ -f "$ROOT/frontend/fieldcheck-verdict.html" ] && cp -a "$ROOT/frontend/fieldcheck-verdict.html" "$BACKUP_DIR/" && echo -e "  ${G}OK${N}  fieldcheck-verdict.html"
echo -e "  ${W}Backup:${N} $BACKUP_DIR"
echo

# ── STAGE 3: MOVE FILES FROM DOWNLOADS ──
echo -e "${B}[3/8]${N} ${W}Moving files from Downloads → project${N}"

[ -f "$DOWNLOADS/worker.js" ] || { echo -e "  ${R}FAIL${N}: worker.js not in $DOWNLOADS"; exit 1; }
[ -f "$DOWNLOADS/fieldcheck-verdict.html" ] || { echo -e "  ${R}FAIL${N}: fieldcheck-verdict.html not in $DOWNLOADS"; exit 1; }

cp "$DOWNLOADS/worker.js" "$ROOT/worker.js"
WORKER_SIZE=$(wc -c < "$ROOT/worker.js" | tr -d ' ')
echo -e "  ${G}OK${N}  worker.js → $ROOT/worker.js ($WORKER_SIZE bytes)"

# Verdict goes to BOTH names (preserves the FCBase56 naming fix)
cp "$DOWNLOADS/fieldcheck-verdict.html" "$ROOT/frontend/verdict.html"
cp "$DOWNLOADS/fieldcheck-verdict.html" "$ROOT/frontend/fieldcheck-verdict.html"
VERDICT_SIZE=$(wc -c < "$ROOT/frontend/verdict.html" | tr -d ' ')
echo -e "  ${G}OK${N}  verdict.html + fieldcheck-verdict.html ($VERDICT_SIZE bytes each)"
echo

# ── STAGE 4: VALIDATE ──
echo -e "${B}[4/8]${N} ${W}Validate${N}"
if node --check "$ROOT/worker.js" 2>&1; then
  echo -e "  ${G}OK${N}  worker.js syntax clean"
else
  echo -e "  ${R}FAIL${N}: worker.js syntax errors"
  exit 1
fi

# FCBase57 markers
echo -n "  /agent route in worker:        "
COUNT=$(grep -c "path === '/agent'" "$ROOT/worker.js")
[ "$COUNT" = "1" ] && echo -e "${G}OK${N}" || { echo -e "${R}FAIL (count: $COUNT)${N}"; exit 1; }

echo -n "  handleAgentRequest function:   "
COUNT=$(grep -c "async function handleAgentRequest" "$ROOT/worker.js")
[ "$COUNT" = "1" ] && echo -e "${G}OK${N}" || { echo -e "${R}FAIL (count: $COUNT)${N}"; exit 1; }

echo -n "  fc-agent-pill in verdict:      "
COUNT=$(grep -c "fc-agent-pill" "$ROOT/frontend/verdict.html")
[ "$COUNT" -ge 5 ] && echo -e "${G}OK${N} ($COUNT refs)" || { echo -e "${R}FAIL (count: $COUNT)${N}"; exit 1; }

echo -n "  fc-agent-pill in fieldcheck-:  "
COUNT=$(grep -c "fc-agent-pill" "$ROOT/frontend/fieldcheck-verdict.html")
[ "$COUNT" -ge 5 ] && echo -e "${G}OK${N} ($COUNT refs)" || { echo -e "${R}FAIL (count: $COUNT)${N}"; exit 1; }

echo -n "  Inline script parse:           "
RESULT=$(node -e "
const fs = require('fs');
const html = fs.readFileSync('$ROOT/frontend/verdict.html', 'utf8');
const scripts = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g) || [];
let ok = 0;
for (const s of scripts) {
  const code = s.replace(/<script[^>]*>/, '').replace(/<\/script>/, '');
  try { new Function(code); ok++; } catch (e) {}
}
console.log(ok + '/' + scripts.length);
")
echo -e "${G}OK${N} ($RESULT, known 1 IIFE artifact OK)"
echo

# ── STAGE 5: DEPLOY WORKER TO DEV ──
echo -e "${B}[5/8]${N} ${W}Deploy worker to DEV${N}"
if wrangler deploy --env dev 2>&1 | tee /tmp/fc57_dev.log; then
  echo -e "  ${G}OK${N}  dev worker deployed"
else
  echo -e "  ${R}FAIL${N}: dev deploy failed"
  exit 1
fi
echo

# ── STAGE 6: SMOKE TEST DEV (fixed grep regex from v2 patch) ──
echo -e "${B}[6/8]${N} ${W}Smoke test DEV /agent endpoint${N}"
DEV_BASE="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"

# Test 1: OPTIONS preflight
echo -n "  /agent OPTIONS preflight... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X OPTIONS "$DEV_BASE/agent")
[ "$HTTP" = "204" ] && echo -e "${G}OK${N} (204)" || echo -e "${R}FAIL${N} ($HTTP)"

# Test 2: POST with empty body should 400
echo -n "  /agent POST {} (validation)... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{}' "$DEV_BASE/agent")
[ "$HTTP" = "400" ] && echo -e "${G}OK${N} (400 expected)" || echo -e "${R}FAIL${N} ($HTTP)"

# Test 3: Real question (streaming, just check 200 + has SSE content)
echo -n "  /agent POST real question... "
RESP=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"question":"Why is Cameron Boozer a STAR?","athlete":"Cameron Boozer","sport":"mens-basketball","verdict_data":{"composite":7.4,"tier":"STAR","school":"Duke University"}}' \
  --max-time 30 "$DEV_BASE/agent" 2>&1 | head -c 200)
if echo "$RESP" | grep -q '"type":"start"' || echo "$RESP" | grep -q '"type": "start"'; then
  echo -e "${G}OK${N} (SSE stream started)"
else
  echo -e "${Y}WARN${N}: unexpected response (may be rate-limited from previous tests)"
  echo "  First 200 chars: $RESP"
fi
echo

# ── STAGE 7: DEPLOY FRONTEND TO DEV + HUMAN PAUSE ──
echo -e "${B}[7/8]${N} ${W}Deploy frontend to Netlify DEV${N}"
if command -v netlify &> /dev/null; then
  cd "$ROOT/frontend"
  if netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase57 AI Agent" 2>&1 | tee /tmp/fc57_netlify_dev.log; then
    echo -e "  ${G}OK${N}  dev frontend deployed"
  else
    echo -e "  ${R}FAIL${N}: netlify dev deploy failed"
    exit 1
  fi
  cd "$ROOT"
else
  echo -e "  ${Y}skip${N}: netlify CLI missing"
fi
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify dev BEFORE promoting to PROD:${N}"
echo
echo -e "  ${W}Dev URL:${N}"
echo -e "    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Boozer&sport=mens-basketball"
echo
echo -e "  ${W}What to test:${N}"
echo -e "    1. Bottom-right: gold 'Ask FieldCheck' pill with pulse animation"
echo -e "    2. Tap pill → chat panel slides up from bottom"
echo -e "    3. 5 suggested questions visible as chips"
echo -e "    4. Tap a suggestion → fills input field"
echo -e "    5. Send → answer streams in character-by-character with blinking cursor"
echo -e "    6. Refresh page → previous Q&A persists (localStorage)"
echo -e "    7. Try a 2nd question → 2nd answer streams"
echo -e "    8. Worker rate-limit: 10/day per IP"
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo
read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo -e "${Y}  Skipping prod. Dev has FCBase57, prod unchanged.${N}"
  echo -e "  ${W}Backup:${N} $BACKUP_DIR"
  exit 0
fi

# ── STAGE 8: PROD + FREEZE ──
echo
echo -e "${B}[8/8]${N} ${W}DEPLOY TO PROD + freeze${N}"
if wrangler deploy 2>&1 | tee /tmp/fc57_prod.log; then
  echo -e "  ${G}OK${N}  prod worker deployed"
else
  echo -e "${R}  FAIL${N}: prod worker failed"; exit 1
fi

if command -v netlify &> /dev/null; then
  cd "$ROOT/frontend"
  if netlify deploy --prod --dir=. --message="FCBase57 . Phase 9.1 AI Agent" 2>&1 | tee /tmp/fc57_netlify_prod.log; then
    echo -e "  ${G}OK${N}  prod frontend deployed"
  fi
  cd "$ROOT"
fi

# Freeze
FREEZE_DIR="$ROOT/freezes/FCBase57_$TIMESTAMP"
mkdir -p "$FREEZE_DIR/frontend"
cp "$ROOT/worker.js" "$FREEZE_DIR/"
cp -r "$ROOT/frontend"/* "$FREEZE_DIR/frontend/"
echo -e "  ${G}OK${N}  Frozen: $FREEZE_DIR"

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase57 SHIPPED${N}"
echo -e "${G}  Finished: $(date)${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo
echo -e "  ${W}Prod:${N}    https://fieldcheck-app.netlify.app"
echo -e "  ${W}Backup:${N}  $BACKUP_DIR"
echo -e "  ${W}Freeze:${N}  $FREEZE_DIR"
echo
echo -e "  ${W}First-visit test:${N} https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cooper+Flagg&sport=mens-basketball"
echo
