#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# fc-freeze.sh · FieldCheck baseline freeze with auto-versioning
# ──────────────────────────────────────────────────────────────────────
#   Drop-in replacement for the May 19-20 hardcoded version that
#   labeled every tarball "FCBase16_V001" and required manual rename.
#
#   Resolves the freeze label in this priority order:
#     1. First argument:    ./fc-freeze.sh FCBase17_V008_universal-search
#     2. $BASELINE_VERSION env var
#     3. Auto-detect: scan existing FCBase*.tar.gz, increment to next V###
#     4. Fallback:         FCBase17_V001  (warns)
#
#   USAGE
#     # Auto-detect next baseline (most common):
#     ./fc-freeze.sh
#
#     # Explicit label (most reliable for narrative tags):
#     ./fc-freeze.sh FCBase17_V008_universal-search
#
#     # Via env var:
#     BASELINE_VERSION=FCBase17_V008_universal-search ./fc-freeze.sh
#
#   OUTPUT
#     ~/Desktop/fieldcheck-proxy/{LABEL}_{YYYYMMDD_HHMM}.tar.gz
#     Mirrored to ~/Downloads/ for safety (Tenet 11 keeps tarballs forever)
# ──────────────────────────────────────────────────────────────────────

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/Desktop/fieldcheck-proxy}"
DOWNLOADS="${DOWNLOADS:-$HOME/Downloads}"
STAMP="$(date +%Y%m%d_%H%M)"

cd "$WORKSPACE"

# ── Resolve baseline label ────────────────────────────────────────────
LABEL=""

if [[ $# -ge 1 && -n "$1" ]]; then
  LABEL="$1"
  echo "  → Using explicit argument: $LABEL"
elif [[ -n "${BASELINE_VERSION:-}" ]]; then
  LABEL="$BASELINE_VERSION"
  echo "  → Using BASELINE_VERSION env: $LABEL"
else
  # Auto-detect: find highest FCBase*_V### in workspace
  HIGHEST="$(ls -1 FCBase*_V[0-9][0-9][0-9]*.tar.gz 2>/dev/null \
    | sed -E 's/.*FCBase([0-9]+)_V([0-9]+).*/\1 \2/' \
    | sort -k1,1n -k2,2n \
    | tail -1)"
  if [[ -n "$HIGHEST" ]]; then
    BASE_NUM=$(echo "$HIGHEST" | awk '{print $1}')
    VER_NUM=$(echo "$HIGHEST" | awk '{print $2}')
    NEXT_VER=$(printf "%03d" $((10#$VER_NUM + 1)))
    LABEL="FCBase${BASE_NUM}_V${NEXT_VER}"
    echo "  → Auto-detected next: $LABEL (highest was FCBase${BASE_NUM}_V${VER_NUM})"
  else
    LABEL="FCBase17_V001"
    echo "  ⚠ No existing tarballs found — defaulting to: $LABEL"
  fi
fi

ARCHIVE_NAME="${LABEL}_${STAMP}.tar.gz"
ARCHIVE_PATH="$WORKSPACE/$ARCHIVE_NAME"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  FieldCheck · BASELINE FREEZE                ║"
echo "║  Label: $(printf '%-37s' "$LABEL") ║"
echo "║  Stamp: $(printf '%-37s' "$STAMP") ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Confirm overwrite if archive already exists ───────────────────────
if [[ -f "$ARCHIVE_PATH" ]]; then
  echo "  ⚠ Archive already exists: $ARCHIVE_PATH"
  read -p "  Overwrite? [y/N]: " CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "  Aborted."
    exit 1
  fi
fi

# ── Build the tarball ─────────────────────────────────────────────────
echo "── BUILDING TARBALL ──────────────"

# Files to include — adjust if your workspace shape differs
INCLUDE=(
  "worker.js"
  "wrangler.toml"
  "index.html"
  "fieldcheck-verdict.html"
  "fieldcheck-roadmap.html"
  "_redirects"
  "deploy-dev.sh"
  "deploy-prod.sh"
  "fc-freeze.sh"
)

# Optional files — included if present
OPTIONAL=(
  "FC_CANONICAL_STATE_V1.html"
  "PLAYER_THESIS_V1_6_HUB.html"
  "fc17-polygon-mount.js"
  "fc17-sport-adapter.js"
  "fc17-hero-sync.js"
  "fc17-interpretation-panel.js"
  "fc17-trust-strip.js"
  "fc17-s2b-flagg-data.js"
  "fc17-s2b-caleb-data.js"
  "fc17-s2c-caitlin-data.js"
  "fc17-s2d-skinner-data.js"
)

TAR_FILES=()
for f in "${INCLUDE[@]}"; do
  if [[ -e "$f" ]]; then
    TAR_FILES+=("$f")
  else
    echo "  ⚠ Missing required file: $f"
  fi
done
for f in "${OPTIONAL[@]}"; do
  [[ -e "$f" ]] && TAR_FILES+=("$f")
done

if [[ ${#TAR_FILES[@]} -eq 0 ]]; then
  echo "  ✗ No files to archive — aborting."
  exit 1
fi

echo "  → Archiving ${#TAR_FILES[@]} files into $ARCHIVE_NAME"
tar -czf "$ARCHIVE_PATH" "${TAR_FILES[@]}"

# ── Mirror to Downloads for safety ────────────────────────────────────
if [[ -d "$DOWNLOADS" ]]; then
  cp "$ARCHIVE_PATH" "$DOWNLOADS/$ARCHIVE_NAME"
  echo "  → Mirrored to: $DOWNLOADS/$ARCHIVE_NAME"
fi

# ── Report ────────────────────────────────────────────────────────────
SIZE=$(ls -lh "$ARCHIVE_PATH" | awk '{print $5}')
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  FREEZE COMPLETE                             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "  Archive:  $ARCHIVE_PATH"
echo "  Size:     $SIZE"
echo "  Mirrored: $DOWNLOADS/$ARCHIVE_NAME"
echo ""
echo "  Restore:  tar -xzf $ARCHIVE_PATH -C $WORKSPACE"
echo ""

# ── List current baselines (auto-detect verification) ─────────────────
echo "── ALL BASELINES IN WORKSPACE ──"
ls -lht FCBase*.tar.gz 2>/dev/null | head -10 | awk '{print "  " $NF "  (" $5 ")"}'
echo ""
