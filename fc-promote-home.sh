#!/usr/bin/env bash
set -e
WS="$HOME/Desktop/fieldcheck-proxy"
PARK="/tmp/fc_park_$$"
cd "$WS"

echo "=============================================="
echo " FC PROMOTE HOME -> PROD (gem-safe)"
echo "=============================================="

echo ""
echo "STEP 0 :: freeze current state"
bash "$WS/fc-freeze.sh"

echo ""
echo "STEP 0b :: guard _redirects (every gem route must be present)"
MISSING=0
for r in /leaderboard /thesis /v5-algorithm /top100 /voices /deck /clips /add-clip /shape /drop /pitch /nba-draft /gems /deck-kevin /deck-arjun /deck-master /draft-intelligence /path /about /canonical; do
  if grep -q "^$r " "$WS/_redirects"; then
    echo "   ok  $r"
  else
    echo "   MISSING  $r"
    MISSING=1
  fi
done
if [ "$MISSING" = "1" ]; then
  echo ""
  echo "ABORT :: _redirects is missing routes above. Do NOT promote."
  echo "Likely deploy-dev.sh overwrote it with its stale block. Restore _redirects first."
  exit 1
fi
echo "   all gem routes present"

echo ""
echo "STEP 0c :: worker syntax"
node --check "$WS/worker.js"
echo "   worker.js clean"

echo ""
echo "STEP 0d :: park 13GB so netlify upload will not hang"
mkdir -p "$PARK/tarballs"
if [ -d "$WS/freezes" ]; then mv "$WS/freezes" "$PARK/"; fi
if [ -d "$WS/backups" ]; then mv "$WS/backups" "$PARK/"; fi
mv "$WS"/*.tar.gz "$PARK/tarballs/" 2>/dev/null || true
echo "   parked to $PARK"

restore() {
  echo ""
  echo "RESTORE :: moving parked files back"
  if [ -d "$PARK/freezes" ]; then mv "$PARK/freezes" "$WS/"; fi
  if [ -d "$PARK/backups" ]; then mv "$PARK/backups" "$WS/"; fi
  mv "$PARK"/tarballs/*.tar.gz "$WS/" 2>/dev/null || true
  rmdir "$PARK/tarballs" 2>/dev/null || true
  rmdir "$PARK" 2>/dev/null || true
}
trap restore EXIT

echo ""
echo "STEP 1 :: DEV deploy (safe; does not rewrite _redirects)"
bash "$WS/fc-deploy-dev.sh"

echo ""
echo "PAUSE :: verify DEV now"
echo "   https://fieldcheck-dev--fieldcheck-app.netlify.app/"
echo "   spot-check gems: /leaderboard  /thesis  /top100  /nba-draft  /voices  /deck-kevin"
read -p "Type yes when DEV looks right to promote to PROD: " OKGO
if [ "$OKGO" != "yes" ]; then
  echo "Stopped before prod. Nothing shipped to prod."
  exit 1
fi

echo ""
echo "STEP 2 :: PROD promote (safe; does not rewrite _redirects)"
bash "$WS/fc-promote-prod.sh"

echo ""
echo "STEP 3 :: re-freeze post-prod"
bash "$WS/fc-freeze.sh"

echo ""
echo "STEP 4 :: GitHub sync"
cd "$WS"
git add .
git commit -m "Promote home (index.html) to prod; gem routes preserved" || true
git push || true

echo ""
echo "=============================================="
echo " DONE. Verify on PROD:"
echo "   https://fieldcheck-app.netlify.app/"
echo "   https://fieldcheck-app.netlify.app/leaderboard"
echo "   https://fieldcheck-app.netlify.app/thesis"
echo "   https://fieldcheck-app.netlify.app/top100"
echo "   https://fieldcheck-app.netlify.app/nba-draft"
echo "   https://fieldcheck-app.netlify.app/voices"
echo "   https://fieldcheck-app.netlify.app/deck-kevin"
echo "=============================================="
