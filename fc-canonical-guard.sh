#!/usr/bin/env bash
# fc-canonical-guard.sh · v4 · Tenet 39 enforcement · TESTED in container before ship
# Parameters:
#   WS env var (default $HOME/Desktop/fieldcheck-proxy) — workspace path
#   First arg --skip-tenet-39 — emergency bypass
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
CANONICAL="$WS/FC_CANONICAL_STATE_V1.html"
WORKER="$WS/worker.js"

R='\033[0;31m'; G='\033[0;32m'; Y='\033[0;33m'; B='\033[1m'; N='\033[0m'

echo ""
echo -e "${B}╔═══════════════════════════════════════════════════════════════╗${N}"
echo -e "${B}║  TENET 39 · ATOMIC CANONICAL-DEPLOY GUARD · v4                ║${N}"
echo -e "${B}╚═══════════════════════════════════════════════════════════════╝${N}"
echo ""

[ ! -f "$CANONICAL" ] && { echo -e "${R}✗ ABORT${N} · canonical not found at $CANONICAL"; exit 1; }
[ ! -f "$WORKER" ] && { echo -e "${R}✗ ABORT${N} · worker.js not found at $WORKER"; exit 1; }

# Read V-stamp from FOOTER only (precise anchor)
FOOTER_MATCH=$(grep -oE 'class="ftr-l">FC_CANONICAL_STATE_V1\.html · V[0-9]+\.[0-9]+ · May [0-9]+, 2026' "$CANONICAL" | head -1)
[ -z "$FOOTER_MATCH" ] && { echo -e "${R}✗ ABORT${N} · footer V-stamp not found"; exit 1; }
CANON_V=$(echo "$FOOTER_MATCH" | grep -oE 'V[0-9]+\.[0-9]+' | head -1)
CANON_DATE=$(echo "$FOOTER_MATCH" | grep -oE 'May [0-9]+, 2026')
CANON_DAY=$(echo "$CANON_DATE" | grep -oE 'May ([0-9]+)' | grep -oE '[0-9]+$')
WORKER_V=$(head -1 "$WORKER" | grep -oE 'V[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1)
TODAY_DAY=$(date +%-d)
THRESHOLD=$((TODAY_DAY - 1))

echo "  Canonical V-stamp:  $CANON_V · $CANON_DATE"
echo "  Worker version:     $WORKER_V"
echo "  Canonical size:     $(wc -c < "$CANONICAL") B"
echo "  Local date:         $(date +'%B %-d, %Y')"

# Today, yesterday, OR future = OK. Only OLDER than yesterday = abort.
if [ "$CANON_DAY" -ge "$THRESHOLD" ]; then
  if [ "$CANON_DAY" -gt "$TODAY_DAY" ]; then
    echo -e "  ${G}✓${N} canonical is current (V-stamp ahead of local — Claude clock skew · fine)"
  else
    echo -e "  ${G}✓${N} canonical is current (within 1 day)"
  fi
else
  echo ""
  echo -e "${R}✗ ABORT · TENET 39 VIOLATION${N}"
  echo -e "${R}  Canonical V-stamp ($CANON_DATE, day $CANON_DAY) is older than yesterday (day $THRESHOLD).${N}"
  echo -e "${R}  Patch the canonical with whatever changed before deploying.${N}"
  if [ "$1" != "--skip-tenet-39" ]; then exit 1; fi
  echo -e "${Y}  ⚠ SKIPPING (emergency bypass)${N}"
fi

# Check worker version is referenced in canonical
if grep -q "$WORKER_V" "$CANONICAL"; then
  echo -e "  ${G}✓${N} worker $WORKER_V referenced in canonical"
else
  echo ""
  echo -e "${R}✗ ABORT · TENET 39 VIOLATION${N}"
  echo -e "${R}  Worker is at $WORKER_V but canonical doesn't reference this version.${N}"
  if [ "$1" != "--skip-tenet-39" ]; then exit 1; fi
fi

echo ""
echo -e "${G}✓ TENET 39 GUARD PASSED · canonical + worker are atomic${N}"
echo ""
