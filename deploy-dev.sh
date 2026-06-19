#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  FieldCheck — STEP 1: Deploy to DEV
#  Deploys whatever is currently in the project directory.
#  No patches needed. Patches are applied separately before this.
# ═══════════════════════════════════════════════════════════════
set -e
DL=~/Downloads
P=~/Desktop/fieldcheck-proxy
DEV=https://fieldcheck-dev--fieldcheck-app.netlify.app

G='\033[0;32m'; Y='\033[0;33m'; R='\033[0;31m'; D='\033[0;90m'; N='\033[0m'
ok()   { echo -e "${G}  ✓ $1${N}"; }
hdr()  { echo ""; echo -e "${Y}── $1 ──────────────${N}"; }
fail() { echo -e "${R}  ✗ $1${N}"; exit 1; }
skip() { echo -e "${D}  ○ $1${N}"; }

echo ""
echo -e "${Y}╔══════════════════════════════════════╗${N}"
echo -e "${Y}║  FieldCheck — DEV DEPLOY             ║${N}"
echo -e "${Y}║  Step 1 of 2. Verify before prod.    ║${N}"
echo -e "${Y}╚══════════════════════════════════════╝${N}"

[ -d "$P" ] || fail "Project not found: $P"

# ── COPY ANY NEW HTML PAGES FROM DOWNLOADS (if present) ─────
hdr "NEW PAGES FROM DOWNLOADS (optional)"
NEW_PAGES=0
for pg in fc-draft-intelligence fc-calibration \
          fieldcheck-trajectory fieldcheck-athlete-voice fieldcheck-accountability \
          fieldcheck-nba-draft fieldcheck-benchmarks fieldcheck-coaches \
          fieldcheck-portal fieldcheck-compare fieldcheck-recruiting-class \
          fieldcheck-path fieldcheck-about fieldcheck-pro-probability \
          fieldcheck-conference fieldcheck-roadmap \
          for-players for-coaches for-franchises \
          fieldcheck-gems fieldcheck-video-iq fieldcheck-fit \
          fieldcheck-class fieldcheck-features fieldcheck-field-report; do
  if [ -f "$DL/$pg.html" ]; then
    cp "$DL/$pg.html" "$P/$pg.html"
    ok "$pg.html (from Downloads)"
    NEW_PAGES=$((NEW_PAGES+1))
  fi
done
[ $NEW_PAGES -eq 0 ] && skip "No new HTML pages in Downloads — using project copies"

# ── APPLY ANY PATCHES FROM DOWNLOADS (if present) ───────────
hdr "NEW PATCHES FROM DOWNLOADS (optional)"
NEW_PATCHES=0
for p in $(ls $DL/fc-patch-*.py 2>/dev/null); do
  python3 "$p" && ok "$(basename $p)" && NEW_PATCHES=$((NEW_PATCHES+1))
done
[ $NEW_PATCHES -eq 0 ] && skip "No patch files in Downloads — using current project state"

# ── COPY QA AGENTS (if present) ─────────────────────────────
for qa in fc-qa-agent fc-jobs-qa fc-site-audit; do
  [ -f "$DL/$qa.sh" ] && { cp "$DL/$qa.sh" "$P/$qa.sh" && chmod +x "$P/$qa.sh" && ok "$qa.sh"; }
done

# ── _REDIRECTS · preserve live routes, add dev-only /roadmap ──
hdr "_REDIRECTS"
[ -f "$P/_redirects" ] || fail "_redirects missing — refusing to deploy without routing"
if ! grep -q '^/roadmap ' "$P/_redirects"; then
  awk 'BEGIN{d=0} /^\/\*/ && d==0 {print "/roadmap                  /fieldcheck-roadmap.html          200"; d=1} {print}' "$P/_redirects" > "$P/_redirects.tmp"
  mv "$P/_redirects.tmp" "$P/_redirects"
fi
ok "_redirects preserved (full live routes + dev-only /roadmap)"

# ── SYNTAX CHECK ─────────────────────────────────────────────
hdr "SYNTAX CHECK"
command -v node &>/dev/null && {
  node --check $P/worker.js && ok "worker.js clean" || fail "SYNTAX ERROR — fix before deploying"
} || skip "node not in PATH"

# ── DEPLOY WORKER → DEV ──────────────────────────────────────
hdr "WORKER → DEV"
cd $P && wrangler deploy --env=dev || fail "Worker deploy failed"
ok "Worker live on DEV"

# ── DEPLOY FRONTEND → DEV ────────────────────────────────────
hdr "FRONTEND → DEV"
netlify deploy --dir=. --alias fieldcheck-dev || fail "Frontend deploy failed"
ok "Frontend live on DEV"
# Remove roadmap from file AFTER deploy (keeps dev live, never reaches prod file)
sed -i '' '/\/roadmap/d' "$P/_redirects" 2>/dev/null || true

echo ""
echo -e "${Y}╔══════════════════════════════════════════════╗${N}"
echo -e "${Y}║  DEV DEPLOY COMPLETE                         ║${N}"
echo -e "${Y}╚══════════════════════════════════════════════╝${N}"
echo ""
echo "  Verify on DEV:"
echo "  $DEV"
echo "  $DEV/accountability  ← Nebraska, LSU, Stanford"
echo "  $DEV/trajectory"
echo "  $DEV/coaches"
echo "  $DEV/voice"
echo "  $DEV/nba-draft"
echo ""
echo -e "  ${R}Only promote to prod when dev looks good.${N}"
echo -e "  ${Y}When ready:${N} bash ~/Desktop/fieldcheck-proxy/deploy-prod.sh"
echo ""
