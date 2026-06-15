#!/usr/bin/env bash
# fc-stage.sh · auto-stage newest worker + canonical from ~/Downloads
#
# USAGE:
#   ./fc-stage.sh           # stage only (no deploy)
#   ./fc-stage.sh deploy    # stage + ship to dev in one shot
#   ./fc-stage.sh status    # show what's currently staged + what's newest in Downloads
#
# WHY THIS EXISTS:
# Chrome saves repeated downloads with "(N)" suffixes. Manually finding the
# newest "(N)" + escaping the parens + cp'ing → friction every ship. This
# script auto-detects newest by mtime, copies with correct names, verifies
# Tenet 39 alignment, and optionally chains to fc-deploy-dev.sh.
#
# After every successful stage+deploy, run with --clean to delete the
# (N)-suffix copies from Downloads (keeps tarballs).

set -e
PROJECT_DIR="$HOME/Desktop/fieldcheck-proxy"
DOWNLOADS="$HOME/Downloads"

cd "$PROJECT_DIR"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  FC-STAGE · auto-detect newest files from ~/Downloads        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# ──────────────────────────────────────────────────────────────────────
# Status mode: just show what's where
# ──────────────────────────────────────────────────────────────────────
if [ "$1" = "status" ]; then
    echo "── Currently staged in $PROJECT_DIR ──"
    if [ -f "$PROJECT_DIR/worker.js" ]; then
        W_VER=$(head -1 "$PROJECT_DIR/worker.js" | grep -oE 'V022\.[0-9.]+' | head -1 || echo "unknown")
        W_SIZE=$(stat -f%z "$PROJECT_DIR/worker.js" 2>/dev/null || stat -c%s "$PROJECT_DIR/worker.js")
        echo "  worker.js                       $W_VER  ($W_SIZE B)"
    fi
    if [ -f "$PROJECT_DIR/FC_CANONICAL_STATE_V1.html" ]; then
        C_VER=$(grep "Canonical State · V" "$PROJECT_DIR/FC_CANONICAL_STATE_V1.html" | head -1 | sed 's/.*Canonical State · //;s/<.*//')
        C_SIZE=$(stat -f%z "$PROJECT_DIR/FC_CANONICAL_STATE_V1.html" 2>/dev/null || stat -c%s "$PROJECT_DIR/FC_CANONICAL_STATE_V1.html")
        echo "  FC_CANONICAL_STATE_V1.html      $C_VER  ($C_SIZE B)"
    fi
    echo ""
    echo "── Newest in $DOWNLOADS ──"
    W_NEW=$(ls -t "$DOWNLOADS"/worker-v*.js 2>/dev/null | head -1 || true)
    C_NEW=$(ls -t "$DOWNLOADS"/FC_CANONICAL_STATE_V1*.html 2>/dev/null | head -1 || true)
    [ -n "$W_NEW" ] && echo "  $(basename "$W_NEW")        $(stat -f%z "$W_NEW" 2>/dev/null || stat -c%s "$W_NEW") B"
    [ -n "$C_NEW" ] && echo "  $(basename "$C_NEW")  $(stat -f%z "$C_NEW" 2>/dev/null || stat -c%s "$C_NEW") B"
    echo ""
    exit 0
fi

# ──────────────────────────────────────────────────────────────────────
# Stage mode
# ──────────────────────────────────────────────────────────────────────

# Find newest canonical (always present in any stage)
CANONICAL_SRC=$(ls -t "$DOWNLOADS"/FC_CANONICAL_STATE_V1*.html 2>/dev/null | head -1 || true)
if [ -z "$CANONICAL_SRC" ]; then
    echo "✗ ABORT · no FC_CANONICAL_STATE_V1*.html in $DOWNLOADS"
    exit 1
fi

# Find newest worker (optional — sometimes only canonical changes)
WORKER_SRC=$(ls -t "$DOWNLOADS"/worker-v*.js 2>/dev/null | head -1 || true)

# Stage canonical
C_NAME=$(basename "$CANONICAL_SRC")
C_SIZE=$(stat -f%z "$CANONICAL_SRC" 2>/dev/null || stat -c%s "$CANONICAL_SRC")
echo "→ CANONICAL"
echo "  source: $C_NAME"
echo "  size:   $C_SIZE B"
cp "$CANONICAL_SRC" "$PROJECT_DIR/FC_CANONICAL_STATE_V1.html"
C_VER=$(grep "Canonical State · V" "$PROJECT_DIR/FC_CANONICAL_STATE_V1.html" | head -1 | sed 's/.*Canonical State · //;s/<.*//')
echo "  staged: FC_CANONICAL_STATE_V1.html  ✓  $C_VER"
echo ""

# Stage worker if newer than what's already staged (or no current worker)
if [ -n "$WORKER_SRC" ]; then
    W_NAME=$(basename "$WORKER_SRC")
    W_SIZE=$(stat -f%z "$WORKER_SRC" 2>/dev/null || stat -c%s "$WORKER_SRC")
    NEW_W_VER=$(head -1 "$WORKER_SRC" | grep -oE 'V022\.[0-9.]+' | head -1 || echo "unknown")
    CUR_W_VER=""
    [ -f "$PROJECT_DIR/worker.js" ] && CUR_W_VER=$(head -1 "$PROJECT_DIR/worker.js" | grep -oE 'V022\.[0-9.]+' | head -1 || echo "")

    echo "→ WORKER"
    echo "  source: $W_NAME"
    echo "  size:   $W_SIZE B"
    if [ "$NEW_W_VER" = "$CUR_W_VER" ]; then
        echo "  staged worker is already $CUR_W_VER — skipping (canonical-only stage)"
    else
        cp "$WORKER_SRC" "$PROJECT_DIR/worker.js"
        echo "  staged: worker.js  ✓  $NEW_W_VER (was $CUR_W_VER)"
    fi
    echo ""
fi

# ──────────────────────────────────────────────────────────────────────
# Tenet 39 alignment check
# ──────────────────────────────────────────────────────────────────────
STAGED_W_VER=$(head -1 "$PROJECT_DIR/worker.js" | grep -oE 'V022\.[0-9.]+' | head -1 || echo "")
if [ -n "$STAGED_W_VER" ]; then
    if grep -q "$STAGED_W_VER" "$PROJECT_DIR/FC_CANONICAL_STATE_V1.html"; then
        echo "✓ TENET 39: worker $STAGED_W_VER referenced in canonical $C_VER"
    else
        echo "⚠ TENET 39 WARN: worker $STAGED_W_VER NOT mentioned in canonical $C_VER"
        echo "  fc-deploy-dev.sh guard may reject — check before deploying"
    fi
fi
echo ""

# ──────────────────────────────────────────────────────────────────────
# Optional deploy chain
# ──────────────────────────────────────────────────────────────────────
if [ "$1" = "deploy" ]; then
    echo "→ chaining to ./fc-deploy-dev.sh"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    ./fc-deploy-dev.sh
else
    echo "════════════════════════════════════════════════════════════════"
    echo "Staged. Next step:"
    echo "  ./fc-deploy-dev.sh         # ship to dev"
    echo "  ./fc-stage.sh deploy       # next time: one command stage+ship"
    echo "  ./fc-stage.sh status       # see current staged + newest available"
    echo "════════════════════════════════════════════════════════════════"
fi
