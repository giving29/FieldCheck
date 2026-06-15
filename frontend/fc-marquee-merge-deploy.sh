#!/usr/bin/env bash
# fc-marquee-merge-deploy.sh
#
# Wraps FC22.S1C: adds CURATED_MEDIA merge to the /api/marquee/verdict-instant
# endpoint in worker.js. Fixes the V038 architectural gap where the fast-path
# marquee endpoint never picked up curated videos + news.
#
# After this lands, the 6 amateur verdict pages (and Cooper Flagg, Mikel Brown,
# Boozer, AJ Dybantsa, Caitlin Clark, etc.) will all render their curated
# YouTube videos + news instead of the search-links fallback template.
#
# Process: patch worker.js -> validate -> dev -> verify (manual) -> prod -> freeze.

set -u

PROXY_DIR="$HOME/Desktop/fieldcheck-proxy"
SCRIPT="apply_marquee_media_merge_v1.py"
DEV_SCRIPT="./fc-deploy-dev.sh"
PROD_SCRIPT="./fc-promote-prod.sh"
FREEZE_SCRIPT="./fc-freeze.sh"
FREEZE_LABEL="FCBase25_MARQUEE_MEDIA_MERGE"

banner() {
  echo
  echo "============================================================"
  echo "  $1"
  echo "============================================================"
}

err() {
  echo "ERROR: $1" >&2
  exit 1
}

cd "$PROXY_DIR" || err "Cannot cd to $PROXY_DIR"

banner "FC22.S1C  MARQUEE MEDIA MERGE"
echo "Target: insert CURATED_MEDIA merge logic into the marquee endpoint"
echo "        (the 'EDGE-SERVED' fast-path) so videos + news ship in its"
echo "        response. Pure addition: ~30 lines added, nothing removed."
echo
echo "Will fix all 6 amateurs + Cooper Flagg + Boozer + AJ + Mikel Brown +"
echo "every other marquee profile that has CURATED_MEDIA entries."

[ -f "worker.js" ]       || err "worker.js not found in $PROXY_DIR"
[ -f "$SCRIPT" ]         || err "$SCRIPT not found (copy it into $PROXY_DIR first)"
[ -x "$DEV_SCRIPT" ]     || err "$DEV_SCRIPT not executable"
[ -x "$PROD_SCRIPT" ]    || err "$PROD_SCRIPT not executable"
[ -x "$FREEZE_SCRIPT" ]  || err "$FREEZE_SCRIPT not executable"

banner "STEP 1 / 5  Patch worker.js"
python3 "$SCRIPT"
PATCH_STATUS=$?
if [ $PATCH_STATUS -ne 0 ]; then
  err "Patch failed (exit $PATCH_STATUS). worker.js restored from backup. Aborting."
fi

banner "STEP 2 / 5  Sanity grep"
NEW_BLOCK=$(grep -c "FCBase25.*MEDIA MERGE FIX" worker.js || true)
echo "  'FCBase25 . MEDIA MERGE FIX' anchor: $NEW_BLOCK  (expected: 1)"
if [ "$NEW_BLOCK" != "1" ]; then
  err "Anchor count off. Restore from worker.js.pre-marquee-merge.bak and investigate."
fi

banner "STEP 3 / 5  Deploy to DEV"
"$DEV_SCRIPT"
DEV_STATUS=$?
if [ $DEV_STATUS -ne 0 ]; then
  err "Dev deploy failed. worker.js still patched. Investigate."
fi

banner "STEP 4 / 5  VERIFY ON DEV (manual)"
echo
echo "1. Open each URL on dev"
echo "2. Hard refresh (Cmd+Shift+R) — IMPORTANT: bypass CDN cache"
echo "3. Click 'News & Video' tab"
echo "4. Confirm REAL curated YouTube videos render (not 'Search the public record')"
echo
echo "  JSJ      https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball"
echo "  Tyran    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Tyran+Stokes&sport=mens-basketball"
echo "  Cam W    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Williams&sport=mens-basketball"
echo "  Faizon   https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Faizon+Brandon&sport=football"
echo "  AJ       https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=AJ+Dybantsa&sport=mens-basketball"
echo "  Boozer   https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Boozer&sport=mens-basketball"
echo
echo "Quick curl test (also verifies the endpoint directly):"
echo "  curl -s 'https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev/api/marquee/verdict-instant?slug=jordan-smith-jr-paul-vi-mens-basketball&sport=mens-basketball' | python3 -c \"import json,sys; d=json.load(sys.stdin); print('videos:', len((d.get('encyclopedia') or {}).get('videos') or [])); print('news:', len(d.get('recent_news_mentions') or []))\""
echo
read -r -p "All 6 dev pages now render curated videos? Type 'yes' to PROMOTE TO PROD: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborting before prod promote. Dev is patched; prod untouched."
  echo "Rollback dev: cp worker.js.pre-marquee-merge.bak worker.js && $DEV_SCRIPT"
  exit 0
fi

banner "STEP 5 / 5  Promote to PROD and freeze"
"$PROD_SCRIPT"
PROD_STATUS=$?
if [ $PROD_STATUS -ne 0 ]; then
  err "Prod promote failed. Investigate immediately."
fi

"$FREEZE_SCRIPT" "$FREEZE_LABEL"
FREEZE_STATUS=$?
if [ $FREEZE_STATUS -ne 0 ]; then
  echo "WARNING: freeze failed but prod deploy succeeded. Manually:"
  echo "  $FREEZE_SCRIPT $FREEZE_LABEL"
fi

banner "DONE"
echo "Baseline: $FREEZE_LABEL"
echo
echo "All 6 amateur verdict pages now ship videos + news from CURATED_MEDIA."
echo "Backup at: worker.js.pre-marquee-merge.bak"
