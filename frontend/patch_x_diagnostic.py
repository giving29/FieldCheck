#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
PATCH X DISCOVERY DIAGNOSTIC · find synthesis Haiku prompt code
═══════════════════════════════════════════════════════════════════════════
Read-only. Dumps the synthesis function + prompt construction so we can
design Patch X (within-level decimal differentiation) against actual code.

What we need to see:
  · The Claude Haiku API call (messages.create or fetch to anthropic.com)
  · The system/user prompt construction
  · Patch H V4 table embedding
  · Patch I brutal_honest V4 anchoring
  · The cacheVersion synthesis context (already know: v022.32u at line 8310)
═══════════════════════════════════════════════════════════════════════════
"""
import re, sys
from pathlib import Path

WORKER = Path('worker.js')
if not WORKER.exists():
    print("✗ worker.js not found"); sys.exit(1)

with open(WORKER) as f:
    lines = f.readlines()

print(f"▸ worker.js: {len(lines)} lines\n")


def find_all_with_context(pattern, label, ctx_before=3, ctx_after=15, max_hits=4):
    rx = re.compile(pattern, re.IGNORECASE)
    hits = [i for i, line in enumerate(lines, 1) if rx.search(line)]
    print(f"═══ {label}")
    print(f"    pattern: {pattern}")
    print(f"    hits: {len(hits)}")
    if not hits:
        print(f"    ✗ NOT FOUND\n")
        return []
    for hit_n, line_no in enumerate(hits[:max_hits]):
        start = max(0, line_no - 1 - ctx_before)
        end = min(len(lines), line_no - 1 + ctx_after + 1)
        print(f"\n    ── hit {hit_n+1} at line {line_no} ──")
        for j in range(start, end):
            marker = '  >>> ' if j + 1 == line_no else '      '
            print(f"    {j+1:>6}{marker}{lines[j].rstrip()[:150]}")
    if len(hits) > max_hits:
        print(f"\n    ... +{len(hits)-max_hits} more hits at lines: {hits[max_hits:max_hits+8]}")
    print()
    return hits


# ─── A1 · Claude Haiku API call ─────────────────────────────────────────────
find_all_with_context(
    r"claude-3-5-haiku|claude-haiku|haiku-3-5|haiku-4-5|claude-3-haiku",
    "A1 · Claude Haiku model identifier",
    ctx_before=5, ctx_after=20, max_hits=6
)

# ─── A2 · Anthropic API call construction ──────────────────────────────────
find_all_with_context(
    r"messages\.create|api\.anthropic\.com|/v1/messages|anthropic-version",
    "A2 · Anthropic API call",
    ctx_before=3, ctx_after=15, max_hits=4
)

# ─── A3 · Synthesis function definition ────────────────────────────────────
find_all_with_context(
    r"function (?:synth|synthesize|generateComposite|computeComposite|buildComposite|scoreComposite|synthesizePlayer)",
    "A3 · Synthesis function definition",
    ctx_before=2, ctx_after=10, max_hits=4
)

# ─── A4 · V4 calibration table in prompt (Patch H) ─────────────────────────
find_all_with_context(
    r"HS#1|hard cap|5\.4.*ceiling|V4 (?:cap|calibration)|prep_amateur.*5\.4|amateur.*ceiling",
    "A4 · V4 calibration text in prompts (Patch H)",
    ctx_before=3, ctx_after=20, max_hits=5
)

# ─── A5 · brutal_honest prompt (Patch I) ────────────────────────────────────
find_all_with_context(
    r"brutal[_ ]?honest|brutally honest|brutal verdict",
    "A5 · brutal_honest prompt (Patch I)",
    ctx_before=3, ctx_after=25, max_hits=4
)

# ─── A6 · cacheVersion area (line 8310) ─────────────────────────────────────
find_all_with_context(
    r"cacheVersion\s*=\s*'v022",
    "A6 · cacheVersion (Patch H/I area)",
    ctx_before=20, ctx_after=30, max_hits=2
)

# ─── A7 · The actual prompt strings · find where score/composite is asked ──
find_all_with_context(
    r"composite.*0[\.-]10|score.*0[\.-]10|rate.*0[\.-]10|rating.*scale|raw_composite",
    "A7 · Composite scoring instruction text in prompts",
    ctx_before=3, ctx_after=20, max_hits=5
)

# ─── A8 · Position pool benchmark (where tier is resolved upstream) ─────────
find_all_with_context(
    r"position_pool_benchmark|position_pool_refs|positionPool",
    "A8 · Position pool benchmark (Patch G area)",
    ctx_before=2, ctx_after=15, max_hits=4
)

print("═══════════════════════════════════════════════════════════════════════")
print(" SUMMARY · paste this whole output back · Patch X design will follow")
print("═══════════════════════════════════════════════════════════════════════")
print(f" worker.js: {len(lines)} lines")
print(f" Key finds needed: A1 (Haiku call) + A2 (API construction) + A6 (cache+synthesis area)")
print(f" Optional but useful: A4 (V4 calibration text), A5 (brutal_honest), A7 (composite instruction)")
