#!/usr/bin/env bash
# fc-media-realign-deploy.sh
#
# Wraps FC22.S1B: realigns 6 CURATED_MEDIA dict keys to match the long-form
# PLAYER_PROFILES slugs, fixing the V038 slug-mismatch that left the 6 amateur
# verdict pages showing the "Search the public record" fallback instead of
# their curated videos + news.
#
# Mapping:
#   aj-dybantsa-mens-basketball       -> aj-dybantsa-byu-mens-basketball
#   cameron-boozer-mens-basketball    -> cameron-boozer-duke-mens-basketball
#   tyran-stokes-mens-basketball      -> tyran-stokes-notre-dame-mens-basketball
#   faizon-brandon-football           -> faizon-brandon-grimsley-football
#   cameron-williams-mens-basketball  -> cameron-williams-st-marys-mens-basketball
#   jordan-smith-jr-mens-basketball   -> jordan-smith-jr-paul-vi-mens-basketball
#
# Process: patch -> validate -> dev -> verify (manual) -> prod -> freeze.

set -u

PROXY_DIR="$HOME/Desktop/fieldcheck-proxy"
SCRIPT="apply_curated_media_slug_realignment_v1.py"
DEV_SCRIPT="./fc-deploy-dev.sh"
PROD_SCRIPT="./fc-promote-prod.sh"
FREEZE_SCRIPT="./fc-freeze.sh"
FREEZE_LABEL="FCBase24_MEDIA_REALIGN"

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

banner "FC22.S1B  CURATED_MEDIA SLUG REALIGN"
echo "Target: 6 CURATED_MEDIA keys renamed to long-form (school-included) slugs"
echo "Result: AJ Dybantsa, Cameron Boozer, Tyran, Faizon, Cam Williams, JSJ"
echo "        all start rendering their curated videos + news on verdict pages."

[ -f "worker.js" ]       || err "worker.js not found in $PROXY_DIR"
[ -f "$SCRIPT" ]         || err "$SCRIPT not found (copy it into $PROXY_DIR first)"
[ -x "$DEV_SCRIPT" ]     || err "$DEV_SCRIPT not executable"
[ -x "$PROD_SCRIPT" ]    || err "$PROD_SCRIPT not executable"
[ -x "$FREEZE_SCRIPT" ]  || err "$FREEZE_SCRIPT not executable"

banner "STEP 1 / 5  Realign CURATED_MEDIA keys"
python3 "$SCRIPT"
PATCH_STATUS=$?
if [ $PATCH_STATUS -ne 0 ]; then
  err "Patch failed (exit $PATCH_STATUS). worker.js restored from backup. Aborting."
fi

banner "STEP 2 / 5  Sanity grep"
echo "Confirming all 6 long-form keys now exist in CURATED_MEDIA region..."
LONG_KEYS=$(grep -cE "'(aj-dybantsa-byu|cameron-boozer-duke|tyran-stokes-notre-dame|faizon-brandon-grimsley|cameron-williams-st-marys|jordan-smith-jr-paul-vi)[a-z-]*':" worker.js || true)
echo "  Long-form key occurrences: $LONG_KEYS  (expected: >= 12 = 6 in CURATED_MEDIA + 6 in PLAYER_PROFILES)"
if [ "$LONG_KEYS" -lt 12 ]; then
  err "Sanity check failed (got $LONG_KEYS, expected >= 12). Investigate."
fi

SHORT_KEYS=$(grep -cE "'(aj-dybantsa-mens-basketball|cameron-boozer-mens-basketball|tyran-stokes-mens-basketball|faizon-brandon-football|cameron-williams-mens-basketball|jordan-smith-jr-mens-basketball)':" worker.js || true)
echo "  Old short-form key occurrences: $SHORT_KEYS  (expected: 0)"
if [ "$SHORT_KEYS" != "0" ]; then
  err "Old short-form keys still present ($SHORT_KEYS). Investigate before deploy."
fi

banner "STEP 3 / 5  Deploy to DEV"
"$DEV_SCRIPT"
DEV_STATUS=$?
if [ $DEV_STATUS -ne 0 ]; then
  err "Dev deploy failed. worker.js still patched. Investigate."
fi

banner "STEP 4 / 5  VERIFY ON DEV (manual)"
echo
echo "Open each URL on dev. The News & Video tab should show curated"
echo "videos + news, NOT the 'Search the public record' fallback template."
echo
echo "  1. JSJ      https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball"
echo "  2. Tyran    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Tyran+Stokes&sport=mens-basketball"
echo "  3. Cam W    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Williams&sport=mens-basketball"
echo "  4. Faizon   https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Faizon+Brandon&sport=football"
echo "  5. AJ       https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=AJ+Dybantsa&sport=mens-basketball"
echo "  6. Boozer   https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Boozer&sport=mens-basketball"
echo
read -r -p "All 6 dev pages show real videos + news (no fallback template)? Type 'yes' to PROMOTE TO PROD: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborting before prod. Dev is patched; prod untouched."
  echo "To roll back dev: restore worker.js from worker.js.pre-media-realign.bak and redeploy."
  exit 0
fi

banner "STEP 5 / 5  Promote to PROD and freeze"
"$PROD_SCRIPT"
PROD_STATUS=$?
if [ $PROD_STATUS -ne 0 ]; then
  err "Prod promote failed. Dev is patched; prod is in mixed state. Investigate immediately."
fi

"$FREEZE_SCRIPT" "$FREEZE_LABEL"
FREEZE_STATUS=$?
if [ $FREEZE_STATUS -ne 0 ]; then
  echo "WARNING: freeze failed but prod deploy succeeded. Manually freeze with:"
  echo "  $FREEZE_SCRIPT $FREEZE_LABEL"
fi

banner "DONE"
echo "Baseline: $FREEZE_LABEL"
echo
echo "Verify on PROD (same 6 URLs, remove '-dev'):"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Tyran+Stokes&sport=mens-basketball"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Williams&sport=mens-basketball"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Faizon+Brandon&sport=football"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=AJ+Dybantsa&sport=mens-basketball"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Boozer&sport=mens-basketball"
echo
echo "Backup at worker.js.pre-media-realign.bak if rollback needed."
