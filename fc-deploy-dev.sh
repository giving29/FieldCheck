#!/usr/bin/env bash
# fc-deploy-dev.sh · ships to DEV only · per Tenet 2 · NEVER to prod
# After this passes + Sridhar verifies on dev URL, run fc-promote-prod.sh to ship to prod
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
R='\033[0;31m'; G='\033[0;32m'; Y='\033[0;33m'; B='\033[1m'; N='\033[0m'

echo ""
echo -e "${B}╔═══════════════════════════════════════════════════════════════╗${N}"
echo -e "${B}║  FC-DEPLOY-DEV · ships to DEV only (Tenet 2 ritual)           ║${N}"
echo -e "${B}╚═══════════════════════════════════════════════════════════════╝${N}"
echo ""

# Guard runs FIRST. Aborts deploy on Tenet 39 violation.
WS="$WS" bash "$WS/fc-canonical-guard.sh" "$@" || {
  echo -e "${R}✗ DEV DEPLOY BLOCKED · canonical guard failed${N}"
  exit 1
}

echo ""
echo -e "${B}▸ Deploying to DEV (worker + frontend)${N}"

# Worker to dev environment
if [ -f wrangler.toml ]; then
  if grep -q "\[env.dev\]" wrangler.toml; then
    wrangler deploy --env dev
  else
    wrangler deploy
  fi
fi

# Frontend to dev (no --prod flag)
netlify deploy --alias=fieldcheck-dev

echo ""
echo -e "${G}✓ DEV DEPLOY COMPLETE${N}"
echo ""
echo -e "${B}▸ NEXT STEPS (Tenet 2: verify on dev before prod)${N}"
echo "  1. Visit dev URLs and verify the change works"
echo "     Worker: https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
echo "     Frontend: https://fieldcheck-dev--fieldcheck-app.netlify.app"
echo "     Canonical: https://fieldcheck-dev--fieldcheck-app.netlify.app/fc_canonical_state_v1"
echo "  2. If verified ok, promote to prod with: ./fc-promote-prod.sh"
echo "  3. If broken on dev, fix + re-run this script — DO NOT promote broken"
echo ""
