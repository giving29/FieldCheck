#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  FieldCheck — STEP 2: Deploy to PROD
#  Only run AFTER dev is verified.
# ═══════════════════════════════════════════════════════════════
set -e
P=~/Desktop/fieldcheck-proxy
PROD=https://fieldcheck-app.netlify.app

G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; N='\033[0m'
ok()   { echo -e "${G}  ✓ $1${N}"; }
hdr()  { echo ""; echo -e "${Y}── $1 ──────────────${N}"; }
fail() { echo -e "${R}  ✗ $1${N}"; exit 1; }

echo ""
echo -e "${Y}╔══════════════════════════════════════╗${N}"
echo -e "${Y}║  FieldCheck — PROD DEPLOY            ║${N}"
echo -e "${Y}║  Step 2 of 2.                        ║${N}"
echo -e "${Y}╚══════════════════════════════════════╝${N}"
echo ""
echo -e "${R}  DEV verified?${N} https://fieldcheck-dev--fieldcheck-app.netlify.app"
echo ""
read -p "  Type YES to promote to prod: " CONFIRM
[ "$CONFIRM" = "YES" ] || { echo -e "${R}  Aborted.${N}"; exit 1; }

hdr "SYNTAX CHECK"
command -v node &>/dev/null && {
  node --check $P/worker.js && ok "worker.js clean" || fail "SYNTAX ERROR"
}

hdr "WORKER → PROD"
cd $P && wrangler deploy --env="" || fail "Worker failed"
ok "Worker live on PROD"

hdr "FRONTEND → PROD"
netlify deploy --dir=. --prod || fail "Frontend failed"
ok "Frontend live on PROD"

hdr "POST-DEPLOY QA"
sleep 20
[ -f "$P/fc-jobs-qa.sh" ]    && bash "$P/fc-jobs-qa.sh"    "$PROD" || true
[ -f "$P/fc-site-audit.sh" ] && bash "$P/fc-site-audit.sh" "$PROD" || true

echo ""
echo -e "${G}╔══════════════════════════════════════════════╗${N}"
echo -e "${G}║  PROD LIVE: $PROD${N}"
echo -e "${G}╚══════════════════════════════════════════════╝${N}"
echo ""
