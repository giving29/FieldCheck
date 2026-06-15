#!/bin/bash
# FieldCheck Snapshot Tool
# Usage:
#   ./snapshot.sh save v0.26-clean-base "Production-ready baseline with NIL, multi-sport, claim flow"
#   ./snapshot.sh list
#   ./snapshot.sh restore v0.26-clean-base
#   ./snapshot.sh diff v0.26-clean-base

set -e
SNAP_DIR="$HOME/Desktop/fieldcheck-snapshots"
PROJ_DIR="$HOME/Desktop/fieldcheck-proxy"

mkdir -p "$SNAP_DIR"

cmd="${1:-help}"
name="$2"
desc="$3"

case "$cmd" in
  save)
    if [ -z "$name" ]; then echo "Usage: snapshot.sh save <name> [description]"; exit 1; fi
    target="$SNAP_DIR/$name"
    if [ -d "$target" ]; then
      echo "⚠ Snapshot '$name' already exists. Overwrite? (y/N)"
      read -r ans
      [ "$ans" != "y" ] && { echo "Cancelled"; exit 0; }
      rm -rf "$target"
    fi
    mkdir -p "$target"
    cd "$PROJ_DIR"
    # Copy all production files
    for f in worker.js index.html mypath.html trust.html news.html pricing.html wire.html qa.sh; do
      [ -f "$f" ] && cp "$f" "$target/"
    done
    # Save meta + description
    cat > "$target/SNAPSHOT.md" <<EOF
# Snapshot: $name

**Saved:** $(date '+%Y-%m-%d %H:%M:%S')
**Description:** ${desc:-No description}

## Files included
$(ls -la "$target" | grep -v "^total" | grep -v "SNAPSHOT.md" | awk '{print "- " $NF " (" $5 " bytes)"}')

## Worker version (from health endpoint)
$(curl -s "https://fieldcheck-proxy.sridhar-nallani.workers.dev/health" 2>/dev/null | head -c 300 || echo "Worker not reachable at snapshot time")

## How to restore
\`\`\`
./snapshot.sh restore $name
\`\`\`

This copies all files from this snapshot back to ~/Desktop/fieldcheck-proxy/
overwriting current files. Then deploy with: fcworker && fcdeploy
EOF
    echo "✓ Snapshot saved: $target"
    echo "✓ Files captured: $(ls "$target" | wc -l | tr -d ' ')"
    echo ""
    echo "Restore anytime with: ./snapshot.sh restore $name"
    ;;

  list)
    echo "── FieldCheck Snapshots ──"
    if [ -z "$(ls -A "$SNAP_DIR" 2>/dev/null)" ]; then
      echo "(no snapshots yet — run: ./snapshot.sh save <name>)"
      exit 0
    fi
    for d in "$SNAP_DIR"/*/; do
      [ -d "$d" ] || continue
      n=$(basename "$d")
      saved=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$d" 2>/dev/null || echo "?")
      desc=$(grep -m 1 "^\*\*Description:\*\*" "$d/SNAPSHOT.md" 2>/dev/null | sed 's/\*\*Description:\*\* //' || echo "")
      size=$(du -sh "$d" 2>/dev/null | awk '{print $1}')
      echo ""
      echo "  📸 $n"
      echo "     Saved: $saved  ·  Size: $size"
      [ -n "$desc" ] && echo "     $desc"
    done
    ;;

  restore)
    if [ -z "$name" ]; then echo "Usage: snapshot.sh restore <name>"; exit 1; fi
    src="$SNAP_DIR/$name"
    if [ ! -d "$src" ]; then echo "✗ Snapshot '$name' not found"; ./snapshot.sh list; exit 1; fi
    echo "About to restore snapshot: $name"
    echo "This will OVERWRITE files in $PROJ_DIR with snapshot versions."
    echo "Continue? (y/N)"
    read -r ans
    [ "$ans" != "y" ] && { echo "Cancelled"; exit 0; }
    cd "$PROJ_DIR"
    for f in worker.js index.html mypath.html trust.html news.html pricing.html wire.html qa.sh; do
      [ -f "$src/$f" ] && cp "$src/$f" "./" && echo "✓ Restored $f"
    done
    echo ""
    echo "✓ Snapshot '$name' restored to $PROJ_DIR"
    echo "Deploy with: fcworker && fcdeploy"
    ;;

  diff)
    if [ -z "$name" ]; then echo "Usage: snapshot.sh diff <name>"; exit 1; fi
    src="$SNAP_DIR/$name"
    if [ ! -d "$src" ]; then echo "✗ Snapshot '$name' not found"; exit 1; fi
    cd "$PROJ_DIR"
    echo "── Diff vs snapshot: $name ──"
    for f in worker.js index.html mypath.html trust.html news.html pricing.html wire.html; do
      [ ! -f "$f" ] && continue
      [ ! -f "$src/$f" ] && { echo "✗ $f exists locally but not in snapshot"; continue; }
      cur_size=$(wc -c < "$f" | tr -d ' ')
      snap_size=$(wc -c < "$src/$f" | tr -d ' ')
      diff_lines=$(diff "$src/$f" "$f" 2>/dev/null | wc -l | tr -d ' ')
      if [ "$diff_lines" = "0" ]; then
        echo "  $f: identical ($cur_size bytes)"
      else
        echo "  $f: CHANGED ($snap_size → $cur_size bytes, $diff_lines diff lines)"
      fi
    done
    ;;

  help|*)
    cat <<EOF
FieldCheck Snapshot Tool

Commands:
  ./snapshot.sh save <name> [description]   Save current files as a snapshot
  ./snapshot.sh list                         List all saved snapshots
  ./snapshot.sh restore <name>              Restore snapshot (overwrites current files)
  ./snapshot.sh diff <name>                 Show what changed since snapshot

Snapshots stored in: $SNAP_DIR

Common workflow:
  Before risky changes:  ./snapshot.sh save before-experiment "trying new pathway algo"
  After successful work: ./snapshot.sh save v0.27-stable "Conference pages live"
  Roll back if needed:   ./snapshot.sh restore v0.27-stable

Recommended snapshots to keep:
  - v0.26-clean-base    (the baseline you're locking in now)
  - latest-stable        (whatever is currently deployed and working)
  - before-<experiment>  (just before any risky change)
EOF
    ;;
esac
