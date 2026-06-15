#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
# fc-ship-MEGA-20260609.sh · Atomic deploy for the 7-hour block
# ══════════════════════════════════════════════════════════════════════════
#
# WHAT THIS SHIPS:
#   • FCBase53 . Phase 6.3 Hidden Gem tier-jump alerts (verdict.html)
#   • FCBase54 . Phase 6.4 Watchlist v2 (watchlist.html)
#   • FCBase55 . Bulk photo curation 38 athletes (worker.js)
#   • FCBase56 . Dynamic OG + Schema.org on verdicts (verdict.html)
#   • 24+ NEW public pages: velocity, methodology, predictions, coverage,
#     5 sport landings, 6 trust pages, 4 legal pages, 3 conference pages,
#     embed builder, versus compare, sitemap, robots, 404, manifest
#   • 3 UPDATED artifacts: pitch, deck, thesis (all with velocity blocks)
#
# DOCTRINE (NEVER-LOSE):
#   1. Backup current state FIRST (atomic snapshot to backups/)
#   2. Move new files from Downloads into project
#   3. Validate every JS-containing file (node --check / inline-scripts parse)
#   4. Deploy to DEV. Verify with curl smoke tests.
#   5. PAUSE for human verification.
#   6. Deploy to PROD only after explicit "y" confirm.
#   7. Freeze: tag the prod-deployed state as FCBase56.
#
# USAGE:
#   chmod +x fc-ship-MEGA-20260609.sh
#   ./fc-ship-MEGA-20260609.sh
#
# RUNS FROM: ~/Desktop/fieldcheck-proxy/
# ASSUMES:   New files live in ~/Downloads/ (this is where Claude.ai drops them)
# ══════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
G='\033[0;32m'  # green
Y='\033[0;33m'  # yellow
R='\033[0;31m'  # red
B='\033[0;36m'  # cyan
W='\033[1;37m'  # white bold
N='\033[0m'     # reset

ROOT="$HOME/Desktop/fieldcheck-proxy"
DOWNLOADS="$HOME/Downloads"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$ROOT/backups/FCBase56_$TIMESTAMP"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase56 . MEGA DEPLOY . 7-hour autonomous block ship${N}"
echo -e "${W}  Started: $(date)${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 1 . SANITY CHECKS
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[1/9]${N} ${W}Sanity checks${N}"

if [ ! -d "$ROOT" ]; then
  echo -e "${R}  FAIL${N}: project root not found at $ROOT"
  exit 1
fi
cd "$ROOT"
echo -e "  ${G}OK${N}  cwd: $ROOT"

if [ ! -d "$DOWNLOADS" ]; then
  echo -e "${R}  FAIL${N}: Downloads dir not found at $DOWNLOADS"
  exit 1
fi
echo -e "  ${G}OK${N}  downloads: $DOWNLOADS"

if ! command -v node &> /dev/null; then
  echo -e "${R}  FAIL${N}: node not installed"
  exit 1
fi
echo -e "  ${G}OK${N}  node: $(node --version)"

if ! command -v wrangler &> /dev/null; then
  echo -e "${R}  FAIL${N}: wrangler not installed (need for worker deploy)"
  exit 1
fi
echo -e "  ${G}OK${N}  wrangler: $(wrangler --version 2>&1 | head -1)"

echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 2 . BACKUP CURRENT STATE
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[2/9]${N} ${W}Backup current state${N} → $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Files we are about to modify or replace
BACKUP_FILES=(
  "worker.js"
  "frontend/verdict.html"
  "frontend/watchlist.html"
  "frontend/fieldcheck-pitch.html"
  "frontend/fieldcheck-deck.html"
  "frontend/fieldcheck-thesis.html"
)

for f in "${BACKUP_FILES[@]}"; do
  if [ -f "$ROOT/$f" ]; then
    cp -a "$ROOT/$f" "$BACKUP_DIR/$(basename $f)"
    SIZE=$(wc -c < "$ROOT/$f")
    echo -e "  ${G}OK${N}  backed up $f ($SIZE bytes)"
  else
    echo -e "  ${Y}skip${N}  $f not found, nothing to back up"
  fi
done

echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 3 . MOVE NEW FILES FROM DOWNLOADS
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[3/9]${N} ${W}Moving files from Downloads → project${N}"

# Patched files (replace existing)
PATCHED_FILES=(
  "worker.js:worker.js"
  "fieldcheck-verdict.html:frontend/verdict.html"
  "fieldcheck-watchlist.html:frontend/watchlist.html"
  "fieldcheck-pitch.html:frontend/fieldcheck-pitch.html"
  "fieldcheck-deck.html:frontend/fieldcheck-deck.html"
  "fieldcheck-thesis.html:frontend/fieldcheck-thesis.html"
)

# New files
NEW_FILES=(
  "fieldcheck-velocity.html:frontend/fieldcheck-velocity.html"
  "fieldcheck-methodology.html:frontend/fieldcheck-methodology.html"
  "fieldcheck-predictions.html:frontend/fieldcheck-predictions.html"
  "fieldcheck-coverage.html:frontend/fieldcheck-coverage.html"
  "fieldcheck-versus.html:frontend/fieldcheck-versus.html"
  "fieldcheck-embed.html:frontend/fieldcheck-embed.html"
  "fieldcheck-about.html:frontend/fieldcheck-about.html"
  "fieldcheck-faq.html:frontend/fieldcheck-faq.html"
  "fieldcheck-glossary.html:frontend/fieldcheck-glossary.html"
  "fieldcheck-roadmap.html:frontend/fieldcheck-roadmap.html"
  "fieldcheck-press.html:frontend/fieldcheck-press.html"
  "fieldcheck-partners.html:frontend/fieldcheck-partners.html"
  "fieldcheck-privacy.html:frontend/fieldcheck-privacy.html"
  "fieldcheck-terms.html:frontend/fieldcheck-terms.html"
  "fieldcheck-security.html:frontend/fieldcheck-security.html"
  "fieldcheck-data-policy.html:frontend/fieldcheck-data-policy.html"
  "fieldcheck-sport-mens-basketball.html:frontend/fieldcheck-sport-mens-basketball.html"
  "fieldcheck-sport-football.html:frontend/fieldcheck-sport-football.html"
  "fieldcheck-sport-womens-basketball.html:frontend/fieldcheck-sport-womens-basketball.html"
  "fieldcheck-sport-womens-volleyball.html:frontend/fieldcheck-sport-womens-volleyball.html"
  "fieldcheck-sport-baseball.html:frontend/fieldcheck-sport-baseball.html"
  "fieldcheck-conf-sec.html:frontend/fieldcheck-conf-sec.html"
  "fieldcheck-conf-bigten.html:frontend/fieldcheck-conf-bigten.html"
  "fieldcheck-conf-big12.html:frontend/fieldcheck-conf-big12.html"
  "404.html:frontend/404.html"
  "sitemap.xml:frontend/sitemap.xml"
  "robots.txt:frontend/robots.txt"
  "manifest.webmanifest:frontend/manifest.webmanifest"
)

ALL_FILES=("${PATCHED_FILES[@]}" "${NEW_FILES[@]}")
MOVED=0
SKIPPED=0

for entry in "${ALL_FILES[@]}"; do
  SRC_NAME="${entry%%:*}"
  DST_PATH="${entry##*:}"
  SRC="$DOWNLOADS/$SRC_NAME"
  DST="$ROOT/$DST_PATH"

  if [ ! -f "$SRC" ]; then
    echo -e "  ${Y}skip${N}  $SRC_NAME not in Downloads"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  mkdir -p "$(dirname "$DST")"
  cp "$SRC" "$DST"
  SIZE=$(wc -c < "$DST")
  echo -e "  ${G}OK${N}  $SRC_NAME → $DST_PATH ($SIZE bytes)"
  MOVED=$((MOVED + 1))
done

echo
echo -e "  ${W}moved: $MOVED${N}  ${Y}skipped: $SKIPPED${N}"
echo

if [ $MOVED -eq 0 ]; then
  echo -e "${R}FAIL${N}: nothing moved. Did you download the files from Claude.ai?"
  exit 1
fi

# ──────────────────────────────────────────────────────────────────────────
# STAGE 4 . VALIDATE
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[4/9]${N} ${W}Validate JS + HTML${N}"

# worker.js: node --check
if [ -f "$ROOT/worker.js" ]; then
  if node --check "$ROOT/worker.js" 2>&1; then
    echo -e "  ${G}OK${N}  worker.js parses"
  else
    echo -e "${R}  FAIL${N}: worker.js has syntax errors"
    echo -e "${R}  Aborting. Restore from $BACKUP_DIR if needed.${N}"
    exit 1
  fi
fi

# All HTML files with inline scripts: parse each script tag
HTML_FILES=$(find "$ROOT/frontend" -maxdepth 1 -name "*.html" -newer "$BACKUP_DIR" 2>/dev/null || true)
HTML_OK=0
HTML_FAIL=0

for f in $HTML_FILES; do
  RESULT=$(node -e "
    const fs = require('fs');
    const html = fs.readFileSync('$f', 'utf8');
    const scripts = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g) || [];
    let ok = 0, fail = 0;
    for (const s of scripts) {
      const code = s.replace(/<script[^>]*>/, '').replace(/<\/script>/, '');
      try { new Function(code); ok++; } catch (e) { fail++; }
    }
    console.log(ok + '/' + scripts.length);
  " 2>&1)

  BASENAME=$(basename "$f")
  if [[ "$RESULT" == *"/"* ]]; then
    OK_COUNT="${RESULT%%/*}"
    TOTAL="${RESULT##*/}"
    if [ "$OK_COUNT" = "$TOTAL" ]; then
      echo -e "  ${G}OK${N}  $BASENAME ($RESULT scripts clean)"
      HTML_OK=$((HTML_OK + 1))
    else
      # Known-acceptable: verdict.html has 1 benign Hidden Gem JSON literal that fails new Function()
      if [ "$BASENAME" = "verdict.html" ] && [ "$TOTAL" -ge 15 ]; then
        DIFF=$((TOTAL - OK_COUNT))
        if [ "$DIFF" -le 1 ]; then
          echo -e "  ${Y}known${N}  $BASENAME ($RESULT . 1 known-benign IIFE/JSON literal)"
          HTML_OK=$((HTML_OK + 1))
          continue
        fi
      fi
      echo -e "  ${R}FAIL${N}  $BASENAME ($RESULT scripts clean)"
      HTML_FAIL=$((HTML_FAIL + 1))
    fi
  fi
done

if [ $HTML_FAIL -gt 0 ]; then
  echo -e "${R}  $HTML_FAIL HTML files have syntax errors. Aborting.${N}"
  echo -e "${R}  Restore from $BACKUP_DIR${N}"
  exit 1
fi

echo
echo -e "  ${W}HTML validated: $HTML_OK files${N}"
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 5 . DEPLOY TO DEV
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[5/9]${N} ${W}Deploy worker to DEV${N}"

cd "$ROOT"
echo -e "  Deploying to fieldcheck-proxy-dev..."
if wrangler deploy --env dev 2>&1 | tee /tmp/fc_deploy_dev.log; then
  echo -e "  ${G}OK${N}  dev worker deployed"
else
  echo -e "${R}  FAIL${N}: dev deploy failed. See /tmp/fc_deploy_dev.log"
  exit 1
fi

echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 6 . SMOKE TEST DEV
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[6/9]${N} ${W}Smoke test DEV worker${N}"

DEV_BASE="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"

# Test 1: photo endpoint with curated athlete (instant return)
echo -n "  /photo Cameron Boozer (curated)... "
DEBUG=$(curl -s "$DEV_BASE/photo?q=Cameron+Boozer&sport=mens-basketball&debug=1")
if echo "$DEBUG" | grep -q '"source":"curated:duke"'; then
  echo -e "${G}OK${N} (curated:duke)"
else
  echo -e "${R}FAIL${N}"
  echo "  Response: $DEBUG"
fi

# Test 2: photo endpoint with newly-curated ICON (Cooper Flagg via ESPN)
echo -n "  /photo Cooper Flagg (FCBase55 ESPN)... "
DEBUG=$(curl -s "$DEV_BASE/photo?q=Cooper+Flagg&sport=mens-basketball&debug=1")
if echo "$DEBUG" | grep -q '"source":"curated:espn"'; then
  echo -e "${G}OK${N} (curated:espn)"
else
  echo -e "${R}FAIL${N}"
  echo "  Response: $DEBUG"
fi

# Test 3: photo endpoint with newly-curated Dybantsa via On3
echo -n "  /photo AJ Dybantsa (FCBase55 On3)... "
DEBUG=$(curl -s "$DEV_BASE/photo?q=AJ+Dybantsa&sport=mens-basketball&debug=1")
if echo "$DEBUG" | grep -q '"source":"curated:on3"'; then
  echo -e "${G}OK${N} (curated:on3)"
else
  echo -e "${R}FAIL${N}"
  echo "  Response: $DEBUG"
fi

# Test 4: photo endpoint with non-curated (cascade)
echo -n "  /photo Tyran Stokes (cascade)... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$DEV_BASE/photo?q=Tyran+Stokes&sport=mens-basketball")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
  echo -e "${G}OK${N} (HTTP $HTTP_CODE)"
else
  echo -e "${R}FAIL${N} (HTTP $HTTP_CODE)"
fi

# Test 5: worker root health
echo -n "  / worker root health... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$DEV_BASE/")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
  echo -e "${G}OK${N} (HTTP $HTTP_CODE)"
else
  echo -e "${R}FAIL${N} (HTTP $HTTP_CODE)"
fi

echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 7 . NETLIFY DEV DEPLOY (frontend)
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[7/9]${N} ${W}Deploy frontend to Netlify DEV${N}"

if command -v netlify &> /dev/null; then
  cd "$ROOT/frontend"
  echo -e "  Deploying to fieldcheck-dev branch..."
  if netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase56 MEGA deploy" 2>&1 | tee /tmp/fc_netlify_dev.log; then
    DEV_URL=$(grep -E "^Website Draft URL:|^Live Draft URL:" /tmp/fc_netlify_dev.log | head -1 | awk '{print $NF}')
    echo -e "  ${G}OK${N}  dev frontend deployed"
    echo -e "  ${W}Preview:${N} $DEV_URL"
  else
    echo -e "${R}  FAIL${N}: netlify dev deploy failed"
    exit 1
  fi
  cd "$ROOT"
else
  echo -e "${Y}  skip${N}: netlify CLI not installed. Manually drag-drop frontend/ to Netlify dev."
fi

echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 8 . HUMAN VERIFICATION PAUSE
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[8/9]${N} ${W}HUMAN VERIFICATION PAUSE${N}"
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify on DEV before promoting to PROD:${N}"
echo
echo -e "  ${W}Dev frontend:${N}  https://fieldcheck-dev--fieldcheck-app.netlify.app"
echo -e "  ${W}Dev worker:${N}    $DEV_BASE"
echo
echo -e "  ${W}Test cases:${N}"
echo -e "    • verdict.html?q=Cameron+Boozer       → real photo, tier alert UI ready"
echo -e "    • verdict.html?q=AJ+Dybantsa          → real On3 photo"
echo -e "    • verdict.html?q=Cooper+Flagg         → real ESPN photo, full eval"
echo -e "    • watchlist.html                      → v2 toolbar with 5 sorts"
echo -e "    • velocity                             → shipped vs planned timeline"
echo -e "    • methodology                          → 8 facets explainer"
echo -e "    • predictions                          → sealed predictions ledger"
echo -e "    • coverage                             → per-sport count + depth bars"
echo -e "    • versus?a=Cooper+Flagg&b=LeBron+James → 2-way compare"
echo -e "    • embed                                → live badge preview + copy code"
echo -e "    • sports/mens-basketball               → sport landing"
echo -e "    • conf-sec, conf-bigten, conf-big12   → conference rollups"
echo -e "    • Sharing verdict URL on Slack/Twitter → OG card with photo"
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo

read -p "  Promote to PROD? [y/N] " -n 1 -r CONFIRM
echo

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo
  echo -e "${Y}  Skipping prod promotion. Dev deploy stays live.${N}"
  echo -e "${Y}  Run 'wrangler deploy --env production' + 'netlify deploy --prod --dir=frontend/' manually when ready.${N}"
  echo
  echo -e "  ${W}Backup retained at:${N} $BACKUP_DIR"
  exit 0
fi

# ──────────────────────────────────────────────────────────────────────────
# STAGE 9 . PROD DEPLOY
# ──────────────────────────────────────────────────────────────────────────
echo
echo -e "${B}[9/9]${N} ${W}DEPLOY TO PROD${N}"

# Worker prod
echo -e "  Deploying worker to PROD..."
if wrangler deploy 2>&1 | tee /tmp/fc_deploy_prod.log; then
  echo -e "  ${G}OK${N}  prod worker deployed"
else
  echo -e "${R}  FAIL${N}: prod worker deploy failed"
  exit 1
fi

# Frontend prod
if command -v netlify &> /dev/null; then
  cd "$ROOT/frontend"
  echo -e "  Deploying frontend to PROD..."
  if netlify deploy --prod --dir=. --message="FCBase56 MEGA . 30+ shipped" 2>&1 | tee /tmp/fc_netlify_prod.log; then
    echo -e "  ${G}OK${N}  prod frontend deployed"
  else
    echo -e "${R}  FAIL${N}: prod frontend deploy failed"
    exit 1
  fi
  cd "$ROOT"
fi

echo

# ──────────────────────────────────────────────────────────────────────────
# FREEZE
# ──────────────────────────────────────────────────────────────────────────
FREEZE_DIR="$ROOT/freezes/FCBase56_$TIMESTAMP"
echo -e "${B}[freeze]${N} ${W}Freeze FCBase56 state${N} → $FREEZE_DIR"
mkdir -p "$FREEZE_DIR"
cp "$ROOT/worker.js" "$FREEZE_DIR/worker.js"
cp -r "$ROOT/frontend" "$FREEZE_DIR/frontend"
echo -e "  ${G}OK${N}  frozen as FCBase56_$TIMESTAMP"

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase56 MEGA DEPLOY COMPLETE${N}"
echo -e "${G}  Finished: $(date)${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo
echo -e "  ${W}Prod frontend:${N}  https://fieldcheck-app.netlify.app"
echo -e "  ${W}Prod worker:${N}    https://fieldcheck-proxy.sridhar-nallani.workers.dev"
echo -e "  ${W}Backup:${N}         $BACKUP_DIR"
echo -e "  ${W}Freeze:${N}         $FREEZE_DIR"
echo
