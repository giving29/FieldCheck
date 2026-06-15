#!/usr/bin/env bash
# fcdeploy-dev.sh — FieldCheck DEV deploy
# Frontend : https://fieldcheck-dev--fieldcheck-app.netlify.app
# Worker   : https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev
# No version gate, no QA. Dev is for iteration — build fast, test here, promote to prod.

set -e

DOWNLOADS="$HOME/Downloads"
PROJECT="$HOME/Desktop/fieldcheck-proxy"

echo "══════════════════════════════════════════════════════════════════════"
echo "  FieldCheck DEV Deploy"
echo "  → fieldcheck-dev--fieldcheck-app.netlify.app"
echo "  → fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
echo "══════════════════════════════════════════════════════════════════════"
echo ""

cd "$PROJECT"

# ─── Restore prod URLs on exit (runs even if deploy fails) ───────────────────
_restore_prod_url() {
  find "$PROJECT" -type f ! -name "*.sh" -exec sed -i '' \
    's|fieldcheck-proxy-dev\.sridhar-nallani\.workers\.dev|fieldcheck-proxy.sridhar-nallani.workers.dev|g' \
    {} + 2>/dev/null || true
  echo "  → prod URL restored in all project files"
}
trap _restore_prod_url EXIT

# ─── 1. Strip tooling files Netlify can't upload ─────────────────────────────
echo "──── Cleaning tooling files from project dir ────────────────────────"
shopt -s nullglob
strays=( "$PROJECT"/fc-*.sh "$PROJECT"/fc-*.js "$PROJECT"/CHANGELOG_*.md \
         "$PROJECT"/*.tsv "$PROJECT"/*.bak "$PROJECT"/.DS_Store \
         "$PROJECT"/rollback-to-v3.sh "$PROJECT"/fc-qa-agent.sh \
         "$PROJECT"/fc-jobs-qa.sh "$PROJECT"/fc-site-audit.sh )
if (( ${#strays[@]} > 0 )); then
  for f in "${strays[@]}"; do rm -f "$f"; done
  echo "  → tooling files stripped"
fi
shopt -u nullglob

# ─── 2. Pick up files from Downloads ─────────────────────────────────────────
echo ""
echo "──── Picking up files from Downloads ────────────────────────────────"
picked=0
if [[ -f "$DOWNLOADS/fieldcheck.html" ]];              then cp "$DOWNLOADS/fieldcheck.html"              "$PROJECT/index.html";                    echo "  → fieldcheck.html → index.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-lovb.html" ]];         then cp "$DOWNLOADS/fieldcheck-lovb.html"         "$PROJECT/lovb.html";                     echo "  → fieldcheck-lovb.html → lovb.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fc-lovb-projection.html" ]];      then cp "$DOWNLOADS/fc-lovb-projection.html"      "$PROJECT/fc-lovb-projection.html";       echo "  → fc-lovb-projection.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fc-lovb-match.html" ]];           then cp "$DOWNLOADS/fc-lovb-match.html"           "$PROJECT/fc-lovb-match.html";            echo "  → fc-lovb-match.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fc-lovb-fit.html" ]];             then cp "$DOWNLOADS/fc-lovb-fit.html"             "$PROJECT/fc-lovb-fit.html";              echo "  → fc-lovb-fit.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fc-lovb-roster.html" ]];          then cp "$DOWNLOADS/fc-lovb-roster.html"          "$PROJECT/fc-lovb-roster.html";           echo "  → fc-lovb-roster.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fc-lovb-archive.html" ]]; then
  cp "$DOWNLOADS/fc-lovb-archive.html" "$PROJECT/fc-lovb-archive.html"
  [[ -f "$DOWNLOADS/fc-iq.html" ]]              && cp "$DOWNLOADS/fc-iq.html"              "$PROJECT/fc-iq.html"
  [[ -f "$DOWNLOADS/fc-trust-graph.html" ]]     && cp "$DOWNLOADS/fc-trust-graph.html"     "$PROJECT/fc-trust-graph.html"
  [[ -f "$DOWNLOADS/fc-edge.html" ]]            && cp "$DOWNLOADS/fc-edge.html"            "$PROJECT/fc-edge.html"
  [[ -f "$DOWNLOADS/fc-iq-api.html" ]]          && cp "$DOWNLOADS/fc-iq-api.html"          "$PROJECT/fc-iq-api.html"
  [[ -f "$DOWNLOADS/fc-methodology.html" ]]     && cp "$DOWNLOADS/fc-methodology.html"     "$PROJECT/fc-methodology.html"
  [[ -f "$DOWNLOADS/fc-founding-athletes.html" ]] && cp "$DOWNLOADS/fc-founding-athletes.html" "$PROJECT/fc-founding-athletes.html"
  [[ -f "$DOWNLOADS/fc-changelog.html" ]]       && cp "$DOWNLOADS/fc-changelog.html"       "$PROJECT/fc-changelog.html"
  [[ -f "$DOWNLOADS/fc-security.html" ]]        && cp "$DOWNLOADS/fc-security.html"        "$PROJECT/fc-security.html"
  [[ -f "$DOWNLOADS/fc-playbook.html" ]]        && cp "$DOWNLOADS/fc-playbook.html"        "$PROJECT/fc-playbook.html"
  [[ -f "$DOWNLOADS/fc-agents.html" ]]          && cp "$DOWNLOADS/fc-agents.html"          "$PROJECT/fc-agents.html"
  [[ -f "$DOWNLOADS/fc-case-studies.html" ]]    && cp "$DOWNLOADS/fc-case-studies.html"    "$PROJECT/fc-case-studies.html"
  [[ -f "$DOWNLOADS/fc-vs.html" ]]              && cp "$DOWNLOADS/fc-vs.html"              "$PROJECT/fc-vs.html"
  echo "  → fc-lovb-archive.html + companion pages"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-wire.html" ]];         then cp "$DOWNLOADS/fieldcheck-wire.html"         "$PROJECT/wire.html";                     echo "  → fieldcheck-wire.html → wire.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-news.html" ]];         then cp "$DOWNLOADS/fieldcheck-news.html"         "$PROJECT/news.html";                     echo "  → fieldcheck-news.html → news.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-about.html" ]];        then cp "$DOWNLOADS/fieldcheck-about.html"        "$PROJECT/about.html";                    echo "  → fieldcheck-about.html → about.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-accuracy.html" ]];     then cp "$DOWNLOADS/fieldcheck-accuracy.html"     "$PROJECT/accuracy.html";                 echo "  → fieldcheck-accuracy.html → accuracy.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-moat.html" ]];         then cp "$DOWNLOADS/fieldcheck-moat.html"         "$PROJECT/moat.html";                     echo "  → fieldcheck-moat.html → moat.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-portal.html" ]];       then cp "$DOWNLOADS/fieldcheck-portal.html"       "$PROJECT/portal.html";                   echo "  → fieldcheck-portal.html → portal.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-katlyn.html" ]];       then cp "$DOWNLOADS/fieldcheck-katlyn.html"       "$PROJECT/katlyn.html";                   echo "  → fieldcheck-katlyn.html → katlyn.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-developmental-os.html" ]]; then cp "$DOWNLOADS/fieldcheck-developmental-os.html" "$PROJECT/fieldcheck-developmental-os.html"; echo "  → fieldcheck-developmental-os.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-pathway.html" ]];      then cp "$DOWNLOADS/fieldcheck-pathway.html"      "$PROJECT/fieldcheck-pathway.html";       echo "  → fieldcheck-pathway.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-voices.html" ]];       then cp "$DOWNLOADS/fieldcheck-voices.html"       "$PROJECT/fieldcheck-voices.html";        echo "  → fieldcheck-voices.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-position-fit.html" ]]; then cp "$DOWNLOADS/fieldcheck-position-fit.html" "$PROJECT/fieldcheck-position-fit.html";  echo "  → fieldcheck-position-fit.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-add-me.html" ]];       then cp "$DOWNLOADS/fieldcheck-add-me.html"       "$PROJECT/fieldcheck-add-me.html";        echo "  → fieldcheck-add-me.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-profile.html" ]];      then cp "$DOWNLOADS/fieldcheck-profile.html"      "$PROJECT/fieldcheck-profile.html";       echo "  → fieldcheck-profile.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-coach.html" ]];        then cp "$DOWNLOADS/fieldcheck-coach.html"        "$PROJECT/fieldcheck-coach.html";         echo "  → fieldcheck-coach.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-coaches.html" ]];      then cp "$DOWNLOADS/fieldcheck-coaches.html"      "$PROJECT/fieldcheck-coaches.html";       echo "  → fieldcheck-coaches.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-pitch.html" ]];        then cp "$DOWNLOADS/fieldcheck-pitch.html"        "$PROJECT/fieldcheck-pitch.html";         echo "  → fieldcheck-pitch.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-pricing-v2.html" ]];   then cp "$DOWNLOADS/fieldcheck-pricing-v2.html"   "$PROJECT/fieldcheck-pricing-v2.html";    echo "  → fieldcheck-pricing-v2.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fc-i18n.js" ]];                   then cp "$DOWNLOADS/fc-i18n.js"                   "$PROJECT/fc-i18n.js";                    echo "  → fc-i18n.js"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-for-players.html" ]];  then cp "$DOWNLOADS/fieldcheck-for-players.html"  "$PROJECT/fieldcheck-for-players.html";   echo "  → fieldcheck-for-players.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-for-coaches.html" ]];  then cp "$DOWNLOADS/fieldcheck-for-coaches.html"  "$PROJECT/fieldcheck-for-coaches.html";   echo "  → fieldcheck-for-coaches.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-for-parents.html" ]];  then cp "$DOWNLOADS/fieldcheck-for-parents.html"  "$PROJECT/fieldcheck-for-parents.html";   echo "  → fieldcheck-for-parents.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-for-scouts.html" ]];   then cp "$DOWNLOADS/fieldcheck-for-scouts.html"   "$PROJECT/fieldcheck-for-scouts.html";    echo "  → fieldcheck-for-scouts.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-index.html" ]];        then cp "$DOWNLOADS/fieldcheck-index.html"        "$PROJECT/fieldcheck-index.html";         echo "  → fieldcheck-index.html"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/_redirects" ]];                   then cp "$DOWNLOADS/_redirects"                   "$PROJECT/_redirects";                    echo "  → _redirects"; picked=$((picked+1)); fi
if [[ -f "$DOWNLOADS/fieldcheck-worker.js" ]];         then cp "$DOWNLOADS/fieldcheck-worker.js"         "$PROJECT/worker.js";                     echo "  → fieldcheck-worker.js → worker.js"; picked=$((picked+1)); fi
if [[ $picked -eq 0 ]]; then
  echo "  (no new files in Downloads — using project copies)"
fi
echo ""

# ─── 3. Swap all worker URLs to dev ──────────────────────────────────────────
echo "──── Swapping worker URL → dev ──────────────────────────────────────"
find "$PROJECT" -type f ! -name "*.sh" -exec sed -i '' \
  's|fieldcheck-proxy\.sridhar-nallani\.workers\.dev|fieldcheck-proxy-dev.sridhar-nallani.workers.dev|g' \
  {} +
echo "  → all references → fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
echo "  → prod URL will be restored automatically on script exit"
echo ""

# ─── 4. Deploy Netlify dev (branch alias — does NOT touch prod) ───────────────
echo "──── Netlify DEV frontend ───────────────────────────────────────────"
netlify deploy --dir=. --alias fieldcheck-dev
echo ""

# ─── 5. Deploy Cloudflare dev worker ─────────────────────────────────────────
echo "──── Cloudflare DEV worker ──────────────────────────────────────────"
wrangler deploy --env dev
echo ""

echo "══════════════════════════════════════════════════════════════════════"
echo "  DEV deploy complete"
echo ""
echo "  Frontend : https://fieldcheck-dev--fieldcheck-app.netlify.app"
echo "  Worker   : https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"
echo ""
echo "  Prod is untouched. Run fcdeploy.sh when you're ready to promote."
echo "══════════════════════════════════════════════════════════════════════"
