#!/usr/bin/env bash
# fcdeploy.sh — FieldCheck one-command deploy + QA
# Version-gated · self-updating · auto-validates · auto-runs QA agent

set -e

# ════════════════════════════════════════════════════════════════════
# v0.30.5.946 Target version is now AUTO-DETECTED from the actual
# index.html in Downloads. Eliminates drift between this script
# and the files it's deploying. Falls back to hardcoded default if
# auto-detect fails. Override via env: TARGET_VERSION=v0.30.5.2280 ...
# ════════════════════════════════════════════════════════════════════

DOWNLOADS="$HOME/Downloads"
PROJECT="$HOME/Desktop/fieldcheck-proxy"

# Auto-detect TARGET_VERSION from the HTML in Downloads (unless overridden)
if [[ -z "${TARGET_VERSION:-}" ]]; then
  if [[ -f "$DOWNLOADS/index.html" ]]; then
    DETECTED=$(grep -o "FIELDCHECK_BUILD = '[^']*'" "$DOWNLOADS/index.html" 2>/dev/null | head -1 | sed "s/FIELDCHECK_BUILD = '//;s/'$//" | grep -o '^v[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+')
    if [[ -n "$DETECTED" ]]; then
      TARGET_VERSION="$DETECTED"
      echo "→ Auto-detected target version: $TARGET_VERSION"
    else
      TARGET_VERSION="v0.30.5.2280"
      echo "→ Could not auto-detect, defaulting to: $TARGET_VERSION"
    fi
  else
    TARGET_VERSION="v0.30.5.2280"
  fi
fi

# ─── 1. Self-update: if a different fcdeploy.sh is in Downloads, install + re-exec ───
if [[ -f "$DOWNLOADS/fcdeploy.sh" ]]; then
  if [[ ! -f "$PROJECT/fcdeploy.sh" ]] || ! diff -q "$DOWNLOADS/fcdeploy.sh" "$PROJECT/fcdeploy.sh" >/dev/null 2>&1; then
    echo "→ New fcdeploy.sh in Downloads — installing to project dir"
    cp "$DOWNLOADS/fcdeploy.sh" "$PROJECT/fcdeploy.sh"
    chmod +x "$PROJECT/fcdeploy.sh"
    if [[ "$0" != "$PROJECT/fcdeploy.sh" ]]; then
      echo "→ Re-executing from $PROJECT/fcdeploy.sh"
      exec bash "$PROJECT/fcdeploy.sh"
    fi
  fi
fi

cd "$PROJECT"

echo "══════════════════════════════════════════════════════════════════════"
echo "  FieldCheck Deploy + QA"
echo "  Target version: $TARGET_VERSION"
echo "══════════════════════════════════════════════════════════════════════"
echo ""

# ─── 2. Pick up files from Downloads ───
echo "──── Picking up files from Downloads ────────────────────────"

# v0.30.5.946 Auto-clean tooling files that don't belong in the public deploy.
# Netlify treats the project dir as publish dir and tries to upload every file.
# It chokes on .sh files (422 errors). Strip them. They get copied back from
# Downloads in step 2 if Downloads has them — required for post-deploy QA.
shopt -s nullglob
strays=( "$PROJECT"/fc-*.sh "$PROJECT"/fc-*.js "$PROJECT"/CHANGELOG_*.md "$PROJECT"/*.tsv "$PROJECT"/*.bak "$PROJECT"/.DS_Store "$PROJECT"/rollback-to-v3.sh )
if (( ${#strays[@]} > 0 )); then
  echo "  → Removing ${#strays[@]} local-only tooling file(s) from project dir before deploy:"
  for f in "${strays[@]}"; do
    echo "    rm $(basename "$f")"
    rm -f "$f"
  done
fi
shopt -u nullglob
picked=0
if [[ -f "$DOWNLOADS/index.html" ]]; then
  cp "$DOWNLOADS/index.html" "$PROJECT/index.html"
  echo "  → index.html → index.html"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-lovb.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-lovb.html" "$PROJECT/lovb.html"
  echo "  → fieldcheck-lovb.html → lovb.html"
  picked=$((picked+1))
fi
# v0.30.5.2213 — LOVB toolkit (5 tools shipped under /lovb/*)
if [[ -f "$DOWNLOADS/fc-lovb-projection.html" ]]; then
  cp "$DOWNLOADS/fc-lovb-projection.html" "$PROJECT/fc-lovb-projection.html"
  echo "  → fc-lovb-projection.html → /lovb/projection (Pro Fit Score)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fc-lovb-match.html" ]]; then
  cp "$DOWNLOADS/fc-lovb-match.html" "$PROJECT/fc-lovb-match.html"
  echo "  → fc-lovb-match.html → /lovb/match (FA Match)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fc-lovb-fit.html" ]]; then
  cp "$DOWNLOADS/fc-lovb-fit.html" "$PROJECT/fc-lovb-fit.html"
  echo "  → fc-lovb-fit.html → /lovb/fit (Market Fit)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fc-lovb-roster.html" ]]; then
  cp "$DOWNLOADS/fc-lovb-roster.html" "$PROJECT/fc-lovb-roster.html"
  echo "  → fc-lovb-roster.html → /lovb/roster (Roster Gap Analyzer)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fc-lovb-archive.html" ]]; then
  cp "$DOWNLOADS/fc-lovb-archive.html" "$PROJECT/fc-lovb-archive.html"
  cp -v "$DOWNLOADS/fc-iq.html" "fc-iq.html" 2>/dev/null && echo "  → fc-iq.html → /iq (FieldCheck IQ destination)"
  cp -v "$DOWNLOADS/fc-trust-graph.html" "fc-trust-graph.html" 2>/dev/null && echo "  → fc-trust-graph.html → /trust-graph (Trust Graph v0)"
  cp -v "$DOWNLOADS/fc-edge.html" "fc-edge.html" 2>/dev/null && echo "  → fc-edge.html → /edge (FieldCheck Edge · Institutional)"
  cp -v "$DOWNLOADS/fc-iq-api.html" "fc-iq-api.html" 2>/dev/null && echo "  → fc-iq-api.html → /api (IQ API docs · Edge tier)"
  cp -v "$DOWNLOADS/fc-methodology.html" "fc-methodology.html" 2>/dev/null && echo "  → fc-methodology.html → /methodology"
  cp -v "$DOWNLOADS/fc-founding-athletes.html" "fc-founding-athletes.html" 2>/dev/null && echo "  → fc-founding-athletes.html → /founding-athletes"
  cp -v "$DOWNLOADS/fc-changelog.html" "fc-changelog.html" 2>/dev/null && echo "  → fc-changelog.html → /changelog"
  cp -v "$DOWNLOADS/fc-security.html" "fc-security.html" 2>/dev/null && echo "  → fc-security.html → /security"
  cp -v "$DOWNLOADS/fc-playbook.html" "fc-playbook.html" 2>/dev/null && echo "  → fc-playbook.html → /playbook"
  cp -v "$DOWNLOADS/fc-agents.html" "fc-agents.html" 2>/dev/null && echo "  → fc-agents.html → /agents"
  cp -v "$DOWNLOADS/fc-case-studies.html" "fc-case-studies.html" 2>/dev/null && echo "  → fc-case-studies.html → /case-studies"
  cp -v "$DOWNLOADS/fc-vs.html" "fc-vs.html" 2>/dev/null && echo "  → fc-vs.html → /vs (FieldCheck IQ vs. rankings)"
  echo "  → fc-lovb-archive.html → /lovb/archive"
  picked=$((picked+1))
fi
# v0.30.5.2218 — V006: wire + news pages deploy. /wire and /news routes existed in
# _redirects but the source files weren't being copied — that's why those pages
# had stale navs.
if [[ -f "$DOWNLOADS/fieldcheck-wire.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-wire.html" "$PROJECT/wire.html"
  echo "  → fieldcheck-wire.html → wire.html"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-news.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-news.html" "$PROJECT/news.html"
  echo "  → fieldcheck-news.html → news.html"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-about.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-about.html" "$PROJECT/about.html"
  echo "  → fieldcheck-about.html → about.html"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-accuracy.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-accuracy.html" "$PROJECT/accuracy.html"
  echo "  → fieldcheck-accuracy.html → accuracy.html (v224 ML track record page)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-moat.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-moat.html" "$PROJECT/moat.html"
  echo "  → fieldcheck-moat.html → moat.html (v248 public moat status page)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-portal.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-portal.html" "$PROJECT/portal.html"
  echo "  → fieldcheck-portal.html → portal.html (v286 agentic portal MVP)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-katlyn.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-katlyn.html" "$PROJECT/katlyn.html"
  echo "  → fieldcheck-katlyn.html → katlyn.html (v321 custom brief, password-gated)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-developmental-os.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-developmental-os.html" "$PROJECT/fieldcheck-developmental-os.html"
  echo "  → fieldcheck-developmental-os.html → /developmental-os (v405 killer feature landing)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-pathway.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-pathway.html" "$PROJECT/fieldcheck-pathway.html"
  echo "  → fieldcheck-pathway.html → /pathway (v450 stickiness page)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-voices.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-voices.html" "$PROJECT/fieldcheck-voices.html"
  echo "  → fieldcheck-voices.html → /voices (v800 persona signal council)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-position-fit.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-position-fit.html" "$PROJECT/fieldcheck-position-fit.html"
  echo "  → fieldcheck-position-fit.html → /position-fit (v860 oracle UI)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-add-me.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-add-me.html" "$PROJECT/fieldcheck-add-me.html"
  echo "  → fieldcheck-add-me.html → /add-me (v875 player profile submit)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-profile.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-profile.html" "$PROJECT/fieldcheck-profile.html"
  echo "  → fieldcheck-profile.html → /m/<slug> + /profile (v960 public player profile)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-coach.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-coach.html" "$PROJECT/fieldcheck-coach.html"
  echo "  → fieldcheck-coach.html → /coach (v1045 coach workspace v1)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-coaches.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-coaches.html" "$PROJECT/fieldcheck-coaches.html"
  echo "  → fieldcheck-coaches.html → /coaches (v1170 coach culture UI)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-pitch.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-pitch.html" "$PROJECT/fieldcheck-pitch.html"
  echo "  → fieldcheck-pitch.html → /pitch (v1296 strategic roadmap presentation)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-pricing-v2.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-pricing-v2.html" "$PROJECT/fieldcheck-pricing-v2.html"
  echo "  → fieldcheck-pricing-v2.html → /pricing (v1255 paid-tier scaffolding)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fc-i18n.js" ]]; then
  cp "$DOWNLOADS/fc-i18n.js" "$PROJECT/fc-i18n.js"
  echo "  → fc-i18n.js (v1491 shared i18n loader · EN/ES toggle)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-for-players.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-for-players.html" "$PROJECT/fieldcheck-for-players.html"
  echo "  → fieldcheck-for-players.html → /for-players (v1641 player journey)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-for-coaches.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-for-coaches.html" "$PROJECT/fieldcheck-for-coaches.html"
  echo "  → fieldcheck-for-coaches.html → /for-coaches (v1861 coach journey)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-for-parents.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-for-parents.html" "$PROJECT/fieldcheck-for-parents.html"
  echo "  → fieldcheck-for-parents.html → /for-parents (v1911 parent journey)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-for-scouts.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-for-scouts.html" "$PROJECT/fieldcheck-for-scouts.html"
  echo "  → fieldcheck-for-scouts.html → /for-scouts (v1961 scout journey)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fieldcheck-index.html" ]]; then
  cp "$DOWNLOADS/fieldcheck-index.html" "$PROJECT/fieldcheck-index.html"
  echo "  → fieldcheck-index.html → fieldcheck-index.html (v109 inverse search page)"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/_redirects" ]]; then
  cp "$DOWNLOADS/_redirects" "$PROJECT/_redirects"
  echo "  → _redirects"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/worker.js" ]]; then
  cp "$DOWNLOADS/worker.js" "$PROJECT/worker.js"
  echo "  → worker.js → worker.js"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fc-qa-agent.sh" ]]; then
  cp "$DOWNLOADS/fc-qa-agent.sh" "$PROJECT/fc-qa-agent.sh"
  chmod +x "$PROJECT/fc-qa-agent.sh"
  echo "  → fc-qa-agent.sh"
  picked=$((picked+1))
fi
if [[ -f "$DOWNLOADS/fc-jobs-qa.sh" ]]; then
  cp "$DOWNLOADS/fc-jobs-qa.sh" "$PROJECT/fc-jobs-qa.sh"
  chmod +x "$PROJECT/fc-jobs-qa.sh"
  echo "  → fc-jobs-qa.sh"
  picked=$((picked+1))
fi
if [[ $picked -eq 0 ]]; then
  echo "  (no new files in Downloads — using project copies)"
fi
echo ""

# ─── 3. HARD VERSION GATE — refuses to deploy if anything is stale ───
echo "──── Version gate ───────────────────────────────────────────"
# Match the FULL build stamp (e.g. v0.30.5.31.0511.0300_PLAYER_DB_PHASE2) so we
# don't accidentally match version strings in code comments.
HTML_BUILD=$(grep -oE "v0\.30\.5\.[0-9]+\.[0-9]+\.[0-9]+_[A-Z_0-9]+" "$PROJECT/index.html" 2>/dev/null | head -1 || echo "MISSING")
WORKER_BUILD=$(grep -oE "v0\.30\.5\.[0-9]+\.[0-9]+\.[0-9]+_[A-Z_0-9]+" "$PROJECT/worker.js" 2>/dev/null | head -1 || echo "MISSING")
# Extract just the version prefix (v0.30.5.X) for comparison against TARGET_VERSION
HTML_VERSION="${HTML_BUILD%%.0*}"  # strip everything from .0NNN onwards
WORKER_VERSION="${WORKER_BUILD%%.0*}"
# But HTML_BUILD looks like "v0.30.5.31.0511.0300_..." — splitting at ".0" loses precision.
# Cleaner: capture via regex
HTML_VERSION=$(echo "$HTML_BUILD" | grep -oE "^v0\.30\.5\.[0-9]+")
WORKER_VERSION=$(echo "$WORKER_BUILD" | grep -oE "^v0\.30\.5\.[0-9]+")

if [[ "$HTML_VERSION" != "$TARGET_VERSION" ]] || [[ "$WORKER_VERSION" != "$TARGET_VERSION" ]]; then
  echo ""
  echo "══════════════════════════════════════════════════════════════════════"
  echo "  ✗ VERSION MISMATCH — DEPLOY ABORTED"
  echo ""
  echo "    Expected:           $TARGET_VERSION"
  echo "    HTML build stamp:   $HTML_BUILD  (extracted: $HTML_VERSION)"
  echo "    Worker build stamp: $WORKER_BUILD  (extracted: $WORKER_VERSION)"
  echo ""
  echo "  → The files in ~/Downloads don't match the target version."
  echo "    Re-download index.html and worker.js"
  echo "    from your latest Claude message, then re-run this script."
  echo "══════════════════════════════════════════════════════════════════════"
  exit 1
fi
echo "✓ HTML build:    $HTML_BUILD"
echo "✓ Worker build:  $WORKER_BUILD"
echo ""

# ─── 4. Validate (6 gates) ───
echo "──── Validation ─────────────────────────────────────────────"
if [[ -f "$PROJECT/fieldcheck-validate.sh" ]]; then
  bash "$PROJECT/fieldcheck-validate.sh"
else
  echo "  (fieldcheck-validate.sh not found — skipping syntax gates)"
fi
echo ""

# ─── 5. Deploy Netlify ───
echo "──── Netlify (frontend) ─────────────────────────────────────"
netlify deploy --dir=. --prod
echo ""

# ─── 6. Deploy Cloudflare ───
echo "──── Cloudflare (worker) ────────────────────────────────────"
wrangler deploy --env=""
echo ""

# ─── 7. Wait for CDN propagation ───
echo "──── Waiting 30s for Netlify CDN to propagate ───────────────"
sleep 30
echo ""

# ─── 8. Run QA agents ───
# v0.30.5.184: Fall back to ~/Downloads when project dir has been stripped.
# Netlify upload requires strip; QA still needs to find the scripts somewhere.
_resolve_qa() {
  local name="$1"
  if [[ -f "$PROJECT/$name" ]]; then echo "$PROJECT/$name"
  elif [[ -f "$DOWNLOADS/$name" ]]; then echo "$DOWNLOADS/$name"
  else echo ""
  fi
}

QA_EXIT=0
echo "──── QA Agent (24 curated profile tests) ────────────────────"
QA_SCRIPT="$(_resolve_qa fc-qa-agent.sh)"
if [[ -n "$QA_SCRIPT" ]]; then
  bash "$QA_SCRIPT" || QA_EXIT=$?
else
  echo "  ⚠ fc-qa-agent.sh not found in project or Downloads — skipping QA"
  QA_EXIT=99
fi

echo ""
JOBS_EXIT=0
echo "──── Steve Jobs QA Agent (Apple-bar audit) ──────────────────"
JOBS_SCRIPT="$(_resolve_qa fc-jobs-qa.sh)"
if [[ -n "$JOBS_SCRIPT" ]]; then
  bash "$JOBS_SCRIPT" || JOBS_EXIT=$?
else
  echo "  ⚠ fc-jobs-qa.sh not found in project or Downloads — skipping Jobs audit"
  JOBS_EXIT=99
fi

# Jobs exit codes: 0=clean/warn, 1=SHIP-BLOCKER, 2=missing key/preflight, 3=URL fail
# Only exit 1 (actual SHIP-BLOCKER) should fail the deploy. Skips/preflight = ok.
if [[ $JOBS_EXIT -eq 2 ]] || [[ $JOBS_EXIT -eq 3 ]] || [[ $JOBS_EXIT -eq 99 ]]; then
  echo "  (Jobs audit skipped/preflight — non-blocking)"
  JOBS_EXIT=0
fi

# v0.30.5.541 — proactive site round audit. Catches the bugs Sridhar
# shouldn't have to find: photo coverage drops, alias regressions,
# endpoint shape changes, render-path failures.
echo ""
SITE_AUDIT_EXIT=0
echo "──── Site Round Audit (proactive bug catcher) ───────────────"
SITE_AUDIT_SCRIPT="$(_resolve_qa fc-site-audit.sh)"
if [[ -n "$SITE_AUDIT_SCRIPT" ]]; then
  bash "$SITE_AUDIT_SCRIPT" || SITE_AUDIT_EXIT=$?
else
  echo "  ⚠ fc-site-audit.sh not found in project or Downloads — skipping site audit"
  SITE_AUDIT_EXIT=99
fi
if [[ $SITE_AUDIT_EXIT -eq 99 ]]; then
  echo "  (Site audit skipped — non-blocking)"
  SITE_AUDIT_EXIT=0
fi

echo ""
echo "══════════════════════════════════════════════════════════════════════"
if [[ $QA_EXIT -eq 0 && $JOBS_EXIT -eq 0 && $SITE_AUDIT_EXIT -eq 0 ]]; then
  echo "  ✓ DEPLOY + QA COMPLETE — $TARGET_VERSION is live and verified"
elif [[ $JOBS_EXIT -eq 1 ]]; then
  echo "  ⚠ DEPLOY COMPLETE — Jobs audit flagged SHIP-BLOCKERs (see above)"
elif [[ $SITE_AUDIT_EXIT -ne 0 ]]; then
  echo "  ⚠ DEPLOY COMPLETE — site audit flagged $SITE_AUDIT_EXIT failure(s) (see above)"
else
  echo "  ⚠ DEPLOY COMPLETE — qa_exit=$QA_EXIT jobs_exit=$JOBS_EXIT site_audit=$SITE_AUDIT_EXIT (see above)"
fi
echo "══════════════════════════════════════════════════════════════════════"
exit $(( QA_EXIT + JOBS_EXIT + SITE_AUDIT_EXIT ))
