#!/usr/bin/env bash
# fc-enrich-stubs-deploy.sh
#
# Wraps the FC22.S1A stub-enrichment sprint:
#   1. Run apply_amateur_stub_enrichment_v1.py (patches worker.js + validates)
#   2. Deploy to DEV
#   3. Pause for Sridhar to verify all 4 verdict pages render full content
#   4. After confirmation, promote to PROD
#   5. Freeze as FCBase23_STUB_ENRICHMENT
#
# Tenet 50 compliant (no inline bash with # ambiguity in interactive paste).
# Tenet 51 compliant (regression doctrine: dev verify before prod promote).
# Tenet 21 compliant (one-shot deploy script, no wall of pipes).

set -u

PROXY_DIR="$HOME/Desktop/fieldcheck-proxy"
SCRIPT="apply_amateur_stub_enrichment_v1.py"
DEV_SCRIPT="./fc-deploy-dev.sh"
PROD_SCRIPT="./fc-promote-prod.sh"
FREEZE_SCRIPT="./fc-freeze.sh"
FREEZE_LABEL="FCBase23_STUB_ENRICHMENT"

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

banner "FC22.S1A  STUB ENRICHMENT DEPLOY"
echo "Target: 4 amateur stubs -> full profiles"
echo "  - Jordan Smith Jr.  (composite 5.3 SCOUT)"
echo "  - Tyran Stokes      (composite 5.4 SCOUT)"
echo "  - Cameron Williams  (composite 5.2 SCOUT)"
echo "  - Faizon Brandon    (composite 5.3 SCOUT)"
echo "All per V5.35 doctrine (HS evidence-rigor naturally lands ~5)."

[ -f "worker.js" ]    || err "worker.js not found in $PROXY_DIR"
[ -f "$SCRIPT" ]      || err "$SCRIPT not found (copy it into $PROXY_DIR first)"
[ -x "$DEV_SCRIPT" ]  || err "$DEV_SCRIPT not executable"
[ -x "$PROD_SCRIPT" ] || err "$PROD_SCRIPT not executable"
[ -x "$FREEZE_SCRIPT" ] || err "$FREEZE_SCRIPT not executable"

banner "STEP 1 / 5  Patch worker.js"
python3 "$SCRIPT"
PATCH_STATUS=$?
if [ $PATCH_STATUS -ne 0 ]; then
  err "Patch failed (exit $PATCH_STATUS). worker.js restored from backup. Aborting."
fi

banner "STEP 2 / 5  Sanity grep"
STUB_COUNT=$(grep -c "is_amateur_stub" worker.js || true)
JSJ_COMPOSITE=$(grep -A 22 "jordan-smith-jr-paul-vi-mens-basketball" worker.js | grep "composite:" | head -1 | tr -d ' ,')
echo "  is_amateur_stub remaining:  $STUB_COUNT  (expected: 0)"
echo "  JSJ composite line:         $JSJ_COMPOSITE  (expected: composite:5.3)"
if [ "$STUB_COUNT" != "0" ]; then
  err "Stubs still present after patch. Investigate before deploy."
fi

banner "STEP 3 / 5  Deploy to DEV"
"$DEV_SCRIPT"
DEV_STATUS=$?
if [ $DEV_STATUS -ne 0 ]; then
  err "Dev deploy failed. worker.js still patched. Investigate."
fi

banner "STEP 4 / 5  VERIFY ON DEV (manual)"
echo
echo "Open these 4 URLs on dev. Each should show:"
echo "  - Full composite number (5.2-5.4, NOT '--')"
echo "  - SCOUT tier badge"
echo "  - Awards list (Naismith POY, McDonald's AA, etc.)"
echo "  - At-a-glance scores"
echo
echo "  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball"
echo "  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Tyran+Stokes&sport=mens-basketball"
echo "  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Williams&sport=mens-basketball"
echo "  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Faizon+Brandon&sport=football"
echo
read -r -p "All 4 dev pages render full content? Type 'yes' to PROMOTE TO PROD, anything else aborts: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborting before prod promote. Dev is patched; prod is untouched."
  echo "To roll back dev to pre-enrichment, restore worker.js from worker.js.pre-enrichment.bak and redeploy dev."
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
echo "Verify on PROD (same 4 URLs as dev, just remove the '-dev'):"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Tyran+Stokes&sport=mens-basketball"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Williams&sport=mens-basketball"
echo "  https://fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Faizon+Brandon&sport=football"
echo
echo "If anything looks off, the backup is at worker.js.pre-enrichment.bak."
