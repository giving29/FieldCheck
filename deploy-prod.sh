#!/bin/bash
set -e
[ "$(git branch --show-current)" != "main" ] && { echo "BLOCKED: not on main. Prod ships only from main."; exit 1; }
[ -n "$(git status --porcelain)" ] && { echo "BLOCKED: uncommitted changes."; exit 1; }
read -p "Deploy clean main to PROD worker? (yes/no) " ok; [ "$ok" != "yes" ] && exit 1
wrangler deploy
git tag "prod-live-$(date +%Y%m%d-%H%M)"
echo "Deployed + tagged. Undo with: wrangler rollback"
