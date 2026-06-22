#!/bin/bash
set -e
[ "$(git branch --show-current)" != "main" ] && { echo "BLOCKED: not on main."; exit 1; }
[ -n "$(git status --porcelain)" ] && { echo "BLOCKED: commit first so the freeze tag captures exactly what ships."; exit 1; }
read -p "Deploy SITE to prod (netlify --prod)? (yes/no) " ok; [ "$ok" != "yes" ] && exit 1
TAG="site-live-$(date +%Y%m%d-%H%M)"
git tag "$TAG"
netlify deploy --prod
echo "Site live + frozen as $TAG  ·  rollback: Netlify → Deploys → publish a previous deploy"
