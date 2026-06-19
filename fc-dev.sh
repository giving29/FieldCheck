#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
PARK="/tmp/fc_park_dev_$$"
mkdir -p "$PARK/tarballs"

echo "parking heavy dirs so netlify will not upload 13GB"
if [ -d freezes ]; then mv freezes "$PARK/"; fi
if [ -d backups ]; then mv backups "$PARK/"; fi
mv ./*.tar.gz "$PARK/tarballs/" 2>/dev/null || true
echo "  parked to $PARK"

restore() {
  echo "restoring parked files"
  if [ -d "$PARK/freezes" ]; then mv "$PARK/freezes" "$WS/"; fi
  if [ -d "$PARK/backups" ]; then mv "$PARK/backups" "$WS/"; fi
  mv "$PARK"/tarballs/*.tar.gz "$WS/" 2>/dev/null || true
  rmdir "$PARK/tarballs" 2>/dev/null || true
  rmdir "$PARK" 2>/dev/null || true
}
trap restore EXIT

echo "deploying to DEV (lean publish root)"
bash "$WS/fc-deploy-dev.sh"
