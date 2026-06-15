#!/usr/bin/env bash
# fc-promote-prod.sh · ONLY for promoting an already-dev-verified change to prod
# Re-runs the guard one more time as a safety net. Per Tenet 2.
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
R='\033[0;31m'; G='\033[0;32m'; Y='\033[0;33m'; B='\033[1m'; N='\033[0m'

echo ""
echo -e "${B}╔═══════════════════════════════════════════════════════════════╗${N}"
echo -e "${B}║  FC-PROMOTE-PROD · prod ship (dev must already be verified)   ║${N}"
echo -e "${B}╚═══════════════════════════════════════════════════════════════╝${N}"
echo ""
echo -e "${Y}⚠ This ships to PRODUCTION.${N}"
echo -e "${Y}  Have you already deployed to dev AND verified the change works?${N}"
read -p "  Type 'yes' to continue, anything else aborts: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo -e "${R}✗ Promotion cancelled — run ./fc-deploy-dev.sh first, verify, then return here${N}"
  exit 1
fi

# Guard re-runs as safety net
WS="$WS" bash "$WS/fc-canonical-guard.sh" "$@" || {
  echo -e "${R}✗ PROD PROMOTE BLOCKED · canonical guard failed${N}"
  exit 1
}

echo ""
echo -e "${B}▸ Promoting to PROD${N}"

if [ -f wrangler.toml ]; then
  wrangler deploy
fi
netlify deploy --prod

echo ""
echo -e "${G}✓ PROD PROMOTE COMPLETE${N}"
echo ""
echo -e "${B}▸ Verify (Tenet 21)${N}"
echo "  https://fieldcheck-app.netlify.app/fc_canonical_state_v1"
echo "  Password: thinkdifferent2026"
echo "  Footer should show the V-stamp you just shipped."
echo ""
