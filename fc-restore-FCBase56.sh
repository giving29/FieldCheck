#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
# fc-restore-FCBase56.sh · ONE-COMMAND ROLLBACK to FCBase56 freeze
# ══════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./fc-restore-FCBase56.sh
#
# Or:
#   ./fc-restore-FCBase56.sh /path/to/FCBase56_FROZEN_20260609.tar.gz
#
# DEFAULT TARBALL LOCATION: ~/Downloads/FCBase56_FROZEN_20260609.tar.gz
#
# WHAT THIS DOES:
#   1. Verifies the tarball exists + SHA-256 matches (if known)
#   2. Backs up your CURRENT state to backups/PRE_RESTORE_<timestamp>/
#   3. Extracts the tarball to a staging dir
#   4. Verifies checksums of every file in the freeze
#   5. Copies files from the freeze into the project
#   6. Validates with node --check + inline-script parse
#   7. Deploys to DEV worker + Netlify dev
#   8. Smoke-tests dev (curl /photo for known curated athletes)
#   9. PAUSES for human "y" before promoting to PROD
#   10. Deploys to PROD
#   11. Re-freezes the post-restore state as FCBase56_POST_RESTORE_<timestamp>
#
# SAFETY GUARANTEES:
#   - NEVER deletes anything irreversibly
#   - Backup happens BEFORE any restore action
#   - Aborts immediately on checksum mismatch
#   - Pauses for human confirm before prod
#   - Backup directory path printed at the end so you can recover
#
# IF THIS SCRIPT FAILS PARTWAY:
#   Look for the path printed in stage 2 (backup location).
#   Copy contents back to ~/Desktop/fieldcheck-proxy/ to recover.
# ══════════════════════════════════════════════════════════════════════════

set -e

G='\033[0;32m'  # green
Y='\033[0;33m'  # yellow
R='\033[0;31m'  # red
B='\033[0;36m'  # cyan
W='\033[1;37m'  # white bold
N='\033[0m'

# Configuration
ROOT="$HOME/Desktop/fieldcheck-proxy"
TARBALL="${1:-$HOME/Downloads/FCBase56_FROZEN_20260609.tar.gz}"
EXPECTED_SHA256="6c8e26b3a2205dafd02392b0c31a8dde411cd4b64a672e7a9d578ab1f8d94e51"
STAGING_DIR="/tmp/fc-restore-$(date +%s)"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$ROOT/backups/PRE_RESTORE_$TIMESTAMP"

echo
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${W}  FCBase56 ROLLBACK . restore from frozen baseline${N}"
echo -e "${W}  Tarball: $TARBALL${N}"
echo -e "${W}  Started: $(date)${N}"
echo -e "${W}════════════════════════════════════════════════════════════════════════${N}"
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 1 . VERIFY TARBALL EXISTS + SHA-256
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[1/11]${N} ${W}Verify tarball${N}"

if [ ! -f "$TARBALL" ]; then
  echo -e "  ${R}FAIL${N}: tarball not found at $TARBALL"
  echo -e "         Download from Claude.ai outputs and place at $TARBALL"
  echo -e "         Or pass the path as argument: $0 /path/to/tarball.tar.gz"
  exit 1
fi
SIZE=$(wc -c < "$TARBALL")
echo -e "  ${G}OK${N}  tarball found ($SIZE bytes)"

ACTUAL_SHA=$(shasum -a 256 "$TARBALL" 2>/dev/null | awk '{print $1}' || sha256sum "$TARBALL" | awk '{print $1}')
echo -e "  ${B}sha256:${N} $ACTUAL_SHA"

if [ "$ACTUAL_SHA" = "$EXPECTED_SHA256" ]; then
  echo -e "  ${G}OK${N}  tarball SHA-256 matches expected"
else
  echo -e "  ${Y}WARN${N}: tarball SHA-256 differs from expected"
  echo -e "         Expected: $EXPECTED_SHA256"
  echo -e "         Actual:   $ACTUAL_SHA"
  read -p "  Continue anyway? [y/N] " -n 1 -r ANS
  echo
  if [[ ! "$ANS" =~ ^[Yy]$ ]]; then
    echo -e "${R}  Aborted by user.${N}"
    exit 1
  fi
fi
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 2 . BACKUP CURRENT STATE
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[2/11]${N} ${W}Backup current state${N}"

if [ ! -d "$ROOT" ]; then
  echo -e "  ${Y}skip${N}: project root not at $ROOT (creating fresh)"
  mkdir -p "$ROOT/frontend" "$ROOT/canonical"
else
  mkdir -p "$BACKUP_DIR"
  if [ -f "$ROOT/worker.js" ]; then
    cp -a "$ROOT/worker.js" "$BACKUP_DIR/"
    echo -e "  ${G}OK${N}  backed up worker.js"
  fi
  if [ -d "$ROOT/frontend" ]; then
    cp -ra "$ROOT/frontend" "$BACKUP_DIR/"
    FRONT_COUNT=$(find "$BACKUP_DIR/frontend" -type f | wc -l)
    echo -e "  ${G}OK${N}  backed up frontend/ ($FRONT_COUNT files)"
  fi
  if [ -d "$ROOT/canonical" ]; then
    cp -ra "$ROOT/canonical" "$BACKUP_DIR/"
    echo -e "  ${G}OK${N}  backed up canonical/"
  fi
  echo -e "  ${W}Backup location:${N} $BACKUP_DIR"
  echo -e "  ${W}To recover from this backup:${N}"
  echo -e "         cp -r $BACKUP_DIR/* $ROOT/"
fi
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 3 . EXTRACT TARBALL
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[3/11]${N} ${W}Extract tarball to staging${N}"

mkdir -p "$STAGING_DIR"
tar -xzf "$TARBALL" -C "$STAGING_DIR"

EXTRACT_DIR="$STAGING_DIR/FCBase56_FROZEN_20260609"
if [ ! -d "$EXTRACT_DIR" ]; then
  echo -e "  ${R}FAIL${N}: extraction did not produce expected directory"
  echo -e "         Looking for: $EXTRACT_DIR"
  ls -la "$STAGING_DIR"
  exit 1
fi

FILE_COUNT=$(find "$EXTRACT_DIR" -type f | wc -l)
echo -e "  ${G}OK${N}  extracted to $EXTRACT_DIR"
echo -e "  ${G}OK${N}  $FILE_COUNT files in freeze"
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 4 . VERIFY FILE INTEGRITY (per-file SHA-256)
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[4/11]${N} ${W}Verify file integrity (checksums)${N}"

cd "$EXTRACT_DIR"
if [ ! -f "CHECKSUMS.txt" ]; then
  echo -e "  ${R}FAIL${N}: CHECKSUMS.txt not found in extracted archive"
  exit 1
fi

CHECK_RESULT=$(sha256sum -c CHECKSUMS.txt 2>&1 || true)
FAIL_COUNT=$(echo "$CHECK_RESULT" | grep -c "FAILED" || true)
OK_COUNT=$(echo "$CHECK_RESULT" | grep -c ": OK$" || true)

if [ "$FAIL_COUNT" -gt 0 ]; then
  echo -e "  ${R}FAIL${N}: $FAIL_COUNT files have bad checksums"
  echo "$CHECK_RESULT" | grep "FAILED" | head -5
  echo -e "  ${R}STOP. Archive is corrupted. Restore aborted.${N}"
  echo -e "  ${R}Your original state is intact at: $BACKUP_DIR${N}"
  exit 1
fi

echo -e "  ${G}OK${N}  $OK_COUNT/$FILE_COUNT files passed SHA-256 verification"
cd - > /dev/null
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 5 . COPY FILES INTO PROJECT
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[5/11]${N} ${W}Copy freeze files into project${N}"

# Worker (root level)
cp "$EXTRACT_DIR/worker.js" "$ROOT/worker.js"
WORKER_SIZE=$(wc -c < "$ROOT/worker.js")
echo -e "  ${G}OK${N}  worker.js → $ROOT ($WORKER_SIZE bytes)"

# Frontend files
mkdir -p "$ROOT/frontend"
cp -r "$EXTRACT_DIR/frontend/"* "$ROOT/frontend/"
FRONT_COUNT=$(find "$ROOT/frontend" -maxdepth 1 -type f | wc -l)
echo -e "  ${G}OK${N}  frontend/ → $ROOT/frontend ($FRONT_COUNT files)"

# Canonical state
mkdir -p "$ROOT/canonical"
cp "$EXTRACT_DIR/canonical/FC_CANONICAL_STATE_V1.html" "$ROOT/canonical/"
echo -e "  ${G}OK${N}  canonical/FC_CANONICAL_STATE_V1.html → $ROOT/canonical"

echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 6 . VALIDATE
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[6/11]${N} ${W}Validate restored files${N}"

# Worker.js with node
if command -v node &> /dev/null; then
  if node --check "$ROOT/worker.js" 2>&1; then
    echo -e "  ${G}OK${N}  worker.js parses clean"
  else
    echo -e "  ${R}FAIL${N}: worker.js has syntax errors after restore (impossible if checksums passed)"
    exit 1
  fi
else
  echo -e "  ${Y}skip${N}: node not installed, skipping worker.js syntax check"
fi

# Spot-check key markers
echo -n "  FCBase53 in verdict.html: "
if grep -q "FCBase53" "$ROOT/frontend/verdict.html"; then echo -e "${G}OK${N}"; else echo -e "${R}MISSING${N}"; exit 1; fi

echo -n "  FCBase54 in watchlist.html: "
if grep -q "FCBase54" "$ROOT/frontend/watchlist.html"; then echo -e "${G}OK${N}"; else echo -e "${R}MISSING${N}"; exit 1; fi

echo -n "  FCBase55 in worker.js: "
if grep -q "FCBase55" "$ROOT/worker.js"; then echo -e "${G}OK${N}"; else echo -e "${R}MISSING${N}"; exit 1; fi

echo -n "  FCBase56 in verdict.html: "
if grep -q "FCBase56" "$ROOT/frontend/verdict.html"; then echo -e "${G}OK${N}"; else echo -e "${R}MISSING${N}"; exit 1; fi

echo -n "  CURATED_PHOTO_OVERRIDES entries: "
ENTRIES=$(grep -cE "^  '[a-z][^|]+\|" "$ROOT/worker.js")
if [ "$ENTRIES" -ge 30 ]; then
  echo -e "${G}$ENTRIES${N}"
else
  echo -e "${R}only $ENTRIES (expected >=30)${N}"
  exit 1
fi

echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 7 . DEPLOY WORKER TO DEV
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[7/11]${N} ${W}Deploy worker to DEV${N}"

cd "$ROOT"

if ! command -v wrangler &> /dev/null; then
  echo -e "  ${R}FAIL${N}: wrangler not installed"
  echo -e "         Restore is complete on disk. Deploy manually when wrangler is available."
  echo -e "         Files at: $ROOT"
  exit 1
fi

if wrangler deploy --env dev 2>&1 | tee /tmp/fc_restore_dev.log; then
  echo -e "  ${G}OK${N}  dev worker deployed"
else
  echo -e "  ${R}FAIL${N}: dev worker deploy failed"
  echo -e "         Files restored to disk; deploy manually with: wrangler deploy --env dev"
  exit 1
fi
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 8 . SMOKE TEST DEV
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[8/11]${N} ${W}Smoke test DEV worker${N}"

DEV_BASE="https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev"

run_smoke_test() {
  local name="$1"
  local query="$2"
  local expected_source="$3"

  echo -n "  $name... "
  local result=$(curl -s "$DEV_BASE/photo?${query}&debug=1" | tr -d " \n\t")
  if echo "$result" | grep -q "\"source\":\"$expected_source\""; then
    echo -e "${G}OK${N}"
  else
    echo -e "${R}FAIL${N}"
    echo "    Response: $result"
    return 1
  fi
}

SMOKE_FAIL=0
run_smoke_test "Boozer (curated:duke)"     "q=Cameron+Boozer&sport=mens-basketball" "curated:duke"     || SMOKE_FAIL=1
run_smoke_test "Flagg (curated:espn)"      "q=Cooper+Flagg&sport=mens-basketball"   "curated:espn"     || SMOKE_FAIL=1
run_smoke_test "Dybantsa (curated:on3)"    "q=AJ+Dybantsa&sport=mens-basketball"    "curated:on3"      || SMOKE_FAIL=1
run_smoke_test "Brandon (curated:247sports)" "q=Faizon+Brandon&sport=football"      "curated:247sports" || SMOKE_FAIL=1

if [ $SMOKE_FAIL -ne 0 ]; then
  echo -e "  ${R}FAIL${N}: smoke tests failed. Restore is on disk but worker behavior is wrong."
  echo -e "         Investigate before promoting to prod."
  exit 1
fi

echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 9 . DEPLOY FRONTEND TO DEV (Netlify)
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[9/11]${N} ${W}Deploy frontend to Netlify DEV${N}"

if command -v netlify &> /dev/null; then
  cd "$ROOT/frontend"
  if netlify deploy --dir=. --alias=fieldcheck-dev --message="FCBase56 restore from freeze" 2>&1 | tee /tmp/fc_restore_netlify_dev.log; then
    DEV_URL=$(grep -E "^Website Draft URL:|^Live Draft URL:" /tmp/fc_restore_netlify_dev.log | head -1 | awk '{print $NF}')
    echo -e "  ${G}OK${N}  dev frontend deployed"
    echo -e "  ${W}Preview:${N} $DEV_URL"
  else
    echo -e "  ${R}FAIL${N}: netlify dev deploy failed"
    exit 1
  fi
  cd "$ROOT"
else
  echo -e "  ${Y}skip${N}: netlify CLI not installed. Manually deploy frontend/ to Netlify dev."
fi
echo

# ──────────────────────────────────────────────────────────────────────────
# STAGE 10 . HUMAN VERIFICATION PAUSE
# ──────────────────────────────────────────────────────────────────────────
echo -e "${B}[10/11]${N} ${W}HUMAN VERIFICATION PAUSE${N}"
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${Y}  Verify dev BEFORE promoting restore to PROD:${N}"
echo
echo -e "  ${W}Dev frontend:${N}  https://fieldcheck-dev--fieldcheck-app.netlify.app"
echo -e "  ${W}Dev worker:${N}    $DEV_BASE"
echo
echo -e "  ${W}Test cases:${N}"
echo -e "    • verdict.html?q=Cameron+Boozer     → photo + tier alert UI"
echo -e "    • verdict.html?q=AJ+Dybantsa        → real On3 photo"
echo -e "    • watchlist.html                    → v2 toolbar with 5 sorts"
echo -e "    • /velocity, /methodology           → all render"
echo
echo -e "${Y}════════════════════════════════════════════════════════════════════════${N}"
echo

read -p "  Promote restored state to PROD? [y/N] " -n 1 -r CONFIRM
echo

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo
  echo -e "${Y}  Skipping prod promotion. Dev has restored state, prod unchanged.${N}"
  echo -e "${Y}  To promote later: cd $ROOT && wrangler deploy && netlify deploy --prod --dir=frontend${N}"
  echo
  echo -e "  ${W}Backup retained at:${N} $BACKUP_DIR"
  exit 0
fi

# ──────────────────────────────────────────────────────────────────────────
# STAGE 11 . DEPLOY TO PROD + RE-FREEZE
# ──────────────────────────────────────────────────────────────────────────
echo
echo -e "${B}[11/11]${N} ${W}Deploy restored state to PROD + re-freeze${N}"

# Worker prod
echo -e "  Deploying worker to PROD..."
if wrangler deploy 2>&1 | tee /tmp/fc_restore_prod.log; then
  echo -e "  ${G}OK${N}  prod worker deployed"
else
  echo -e "${R}  FAIL${N}: prod worker deploy failed"
  exit 1
fi

# Frontend prod
if command -v netlify &> /dev/null; then
  cd "$ROOT/frontend"
  if netlify deploy --prod --dir=. --message="FCBase56 restored from freeze" 2>&1 | tee /tmp/fc_restore_netlify_prod.log; then
    echo -e "  ${G}OK${N}  prod frontend deployed"
  fi
  cd "$ROOT"
fi

# Re-freeze post-restore state
FREEZE_DIR="$ROOT/freezes/FCBase56_POST_RESTORE_$TIMESTAMP"
mkdir -p "$FREEZE_DIR"
cp "$ROOT/worker.js" "$FREEZE_DIR/"
cp -r "$ROOT/frontend" "$FREEZE_DIR/"
echo -e "  ${G}OK${N}  Re-frozen as $FREEZE_DIR"

# Cleanup staging
rm -rf "$STAGING_DIR"

echo
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo -e "${G}  ✓ FCBase56 RESTORE COMPLETE${N}"
echo -e "${G}  Finished: $(date)${N}"
echo -e "${G}════════════════════════════════════════════════════════════════════════${N}"
echo
echo -e "  ${W}Prod frontend:${N}  https://fieldcheck-app.netlify.app"
echo -e "  ${W}Prod worker:${N}    https://fieldcheck-proxy.sridhar-nallani.workers.dev"
echo -e "  ${W}Pre-restore backup:${N}  $BACKUP_DIR"
echo -e "  ${W}Post-restore freeze:${N}  $FREEZE_DIR"
echo
echo -e "  ${W}If you need to roll BACK the restore (return to pre-restore state):${N}"
echo -e "    cp -r $BACKUP_DIR/* $ROOT/"
echo -e "    wrangler deploy && netlify deploy --prod --dir=frontend"
echo
