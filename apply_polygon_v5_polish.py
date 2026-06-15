#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
POLYGON POLISH · V5 · Sprint A1 v2 integration
═══════════════════════════════════════════════════════════════════════
Surgically adds consensus shadow overlay + asymmetry callout to FC17
polygon WITHOUT touching the existing renderSVG function.

Strategy: ZERO-RISK ADDITION pattern
  - New function enhanceWithConsensus(root, canonical) added to fc17-polygon-mount.js
  - Called AFTER existing render completes (mount → buildPolygonDOM → enhance)
  - Only runs if window.FC17_CONSENSUS_DATA[canonical] exists
  - DOM injection via createElementNS — existing rendering untouched
  - Idempotent: rerunning is a no-op
  - Self-rollback: any verification failure auto-restores .bak

Files modified (with .pre-polygon-polish.bak):
  - fc17-polygon-mount.js  (CSS additions + enhanceWithConsensus function + mount hook)
  - fieldcheck-verdict.html (one new script tag for fc17-consensus-data.js)

Files added:
  - fc17-consensus-data.js  (copied from ~/Downloads if not in cwd)

Run from ~/Desktop/fieldcheck-proxy/
═══════════════════════════════════════════════════════════════════════
"""
import sys, shutil
from pathlib import Path

print("═══ POLYGON POLISH V5 · APPLY ═══\n")

POLYGON_MOUNT = Path('fc17-polygon-mount.js')
VERDICT_HTML = Path('fieldcheck-verdict.html')
CONSENSUS_DATA = Path('fc17-consensus-data.js')
DOWNLOADS_CONSENSUS = Path.home() / 'Downloads' / 'fc17-consensus-data.js'

IDEMPOTENCY_MARKER = 'enhanceWithConsensus'


# ════════════════════════ STEP 1 · pre-flight ════════════════════════

if not POLYGON_MOUNT.exists():
    print(f"✗ FAIL: {POLYGON_MOUNT} not found in cwd")
    sys.exit(1)
if not VERDICT_HTML.exists():
    print(f"✗ FAIL: {VERDICT_HTML} not found in cwd")
    sys.exit(1)

poly_content = POLYGON_MOUNT.read_text()
verdict_content = VERDICT_HTML.read_text()

# Stage consensus data file
if not CONSENSUS_DATA.exists():
    if DOWNLOADS_CONSENSUS.exists():
        shutil.copy(DOWNLOADS_CONSENSUS, CONSENSUS_DATA)
        print(f"✓ Copied {CONSENSUS_DATA.name} from ~/Downloads ({CONSENSUS_DATA.stat().st_size:,} B)")
    else:
        print(f"✗ FAIL: {CONSENSUS_DATA.name} not in cwd and not in ~/Downloads")
        print(f"  Please download fc17-consensus-data.js first, then re-run.")
        sys.exit(1)
else:
    print(f"✓ {CONSENSUS_DATA.name} already in cwd ({CONSENSUS_DATA.stat().st_size:,} B)")

# Idempotency
if IDEMPOTENCY_MARKER in poly_content:
    print(f"\n✓ Already applied (idempotency marker '{IDEMPOTENCY_MARKER}' present)")
    print(f"  To re-apply: cp <file>.pre-polygon-polish.bak <file> first")
    sys.exit(0)

print(f"\n▸ {POLYGON_MOUNT}: {POLYGON_MOUNT.stat().st_size:,} bytes")
print(f"▸ {VERDICT_HTML}: {VERDICT_HTML.stat().st_size:,} bytes")


# ════════════════════════ STEP 2 · backups ════════════════════════

print(f"\n▸ Creating .pre-polygon-polish.bak backups...")

backup1 = Path(str(POLYGON_MOUNT) + '.pre-polygon-polish.bak')
backup2 = Path(str(VERDICT_HTML) + '.pre-polygon-polish.bak')
shutil.copy(POLYGON_MOUNT, backup1)
shutil.copy(VERDICT_HTML, backup2)
print(f"  ✓ {backup1.name} ({backup1.stat().st_size:,} B)")
print(f"  ✓ {backup2.name} ({backup2.stat().st_size:,} B)")


def rollback(reason):
    print(f"\n✗ ROLLING BACK · {reason}")
    shutil.copy(backup1, POLYGON_MOUNT)
    shutil.copy(backup2, VERDICT_HTML)
    print(f"  ✓ Restored {POLYGON_MOUNT.name}")
    print(f"  ✓ Restored {VERDICT_HTML.name}")
    sys.exit(1)


# ════════════════════════ STEP 3 · patches ════════════════════════

# ── PATCH 3A · CSS additions ──────────────────────────────────────
NEW_CSS = """
/* ── consensus shadow overlay · Sprint A1 v2 ────────────────── */
.fc17-consensus-polygon{fill:rgba(160,150,140,.10);stroke:rgba(160,150,140,.55);stroke-width:1.4;stroke-dasharray:3 3;stroke-linejoin:round;pointer-events:none}
.fc17-consensus-dot{fill:rgba(160,150,140,.6);stroke:#06050A;stroke-width:.8;pointer-events:none}
.fc17-asym-callout{margin-top:22px;padding:14px 18px;border-left:3px solid var(--fc17-gold);background:rgba(245,184,0,.04);border-radius:0 8px 8px 0;position:relative;animation:fc17-fadeIn .6s 1.6s both}
.fc17-asym-callout.converged{border-left-color:var(--fc17-moss);background:rgba(107,170,90,.04)}
.fc17-asym-callout.gem{border-left-color:var(--fc17-goldb);background:rgba(255,210,74,.04)}
.fc17-asym-lbl{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.6px;color:var(--fc17-gold);text-transform:uppercase;margin-bottom:6px}
.fc17-asym-callout.converged .fc17-asym-lbl{color:var(--fc17-moss)}
.fc17-asym-callout.gem .fc17-asym-lbl{color:var(--fc17-goldb)}
.fc17-asym-txt{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:16px;color:var(--fc17-t);line-height:1.55}
.fc17-asym-txt strong{font-family:'Anton',sans-serif;font-style:normal;font-weight:400;color:var(--fc17-gold);letter-spacing:.005em}
.fc17-asym-callout.converged .fc17-asym-txt strong{color:var(--fc17-moss)}
.fc17-asym-callout.gem .fc17-asym-txt strong{color:var(--fc17-goldb)}
.fc17-asym-meta{margin-top:10px;padding-top:10px;border-top:1px solid var(--fc17-ge2);font-family:'JetBrains Mono',monospace;font-size:9.5px;color:var(--fc17-t4);letter-spacing:.6px;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
.fc17-asym-legend{display:flex;gap:18px;justify-content:center;flex-wrap:wrap;margin:14px 0 4px;padding:10px 0;border-top:1px solid var(--fc17-ge2);border-bottom:1px solid var(--fc17-ge2)}
.fc17-asym-legend .leg-item{display:flex;align-items:center;gap:7px;font-family:'JetBrains Mono',monospace;font-size:9.5px;letter-spacing:.5px;color:var(--fc17-t3);text-transform:uppercase;font-weight:700}
.fc17-asym-legend .leg-sw{width:18px;height:3px;border-radius:2px}
.fc17-asym-legend .leg-sw.fc{background:var(--fc17-gold);box-shadow:0 0 6px rgba(245,184,0,.5)}
.fc17-asym-legend .leg-sw.cons{background:rgba(160,150,140,.55)}
.fc17-asym-legend .leg-sw.ci{background:linear-gradient(90deg,transparent,var(--fc17-gold),transparent);opacity:.4}
"""

css_anchor = ".fc17-drill-note b{color:var(--fc17-gold);font-style:normal;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase}\n`;"
css_replacement = ".fc17-drill-note b{color:var(--fc17-gold);font-style:normal;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase}\n" + NEW_CSS + "`;"

if poly_content.count(css_anchor) != 1:
    rollback(f"CSS anchor not unique (found {poly_content.count(css_anchor)})")
poly_content = poly_content.replace(css_anchor, css_replacement, 1)
print(f"  ✓ CSS · consensus styles + asymmetry callout + legend added")


# ── PATCH 3B · inject enhanceWithConsensus function ──────────────
ENHANCE_FN = '''
  // ════════════════════════════════════════════════════════════════
  // ENHANCE WITH CONSENSUS · Sprint A1 v2 · Polygon polish
  // ════════════════════════════════════════════════════════════════
  // ZERO-RISK ADDITION pattern: runs AFTER existing renderSVG completes.
  // Only inserts consensus polygon + asymmetry callout when consensus
  // data exists for this player. Existing rendering completely untouched.
  function enhanceWithConsensus(root, canonical) {
    if (!window.FC17_CONSENSUS_DATA) return;
    var cdata = window.FC17_CONSENSUS_DATA[canonical];
    if (!cdata || !cdata.consensus) {
      // No consensus data for this player — render NOTHING extra (graceful degradation)
      return;
    }

    var svgEl = root.querySelector('.fc17-svg');
    if (!svgEl) return;

    // Match FC17 polygon geometry exactly (CX/CY/MAX_R, pointAt, SVG_NS in scope)
    var axisDefs = [
      ['character', 0], ['mindset', 45], ['mental_strength', 90], ['talent', 135],
      ['physical', 180], ['mental_iq', 225], ['coachability', 270], ['competitive', 315]
    ];

    // Consensus polygon points
    var consensusPoints = axisDefs.map(function(def) {
      var v = Math.max(0, Math.min(10, cdata.consensus[def[0]] || 0));
      var p = pointAt(def[1], v, CX, CY, MAX_R);
      return p.x.toFixed(1) + ',' + p.y.toFixed(1);
    }).join(' ');

    // Insert consensus polygon BEFORE the FC mean polygon (renders underneath)
    var meanPoly = svgEl.querySelector('.fc17-mean-polygon');
    if (meanPoly) {
      var consPoly = document.createElementNS(SVG_NS, 'polygon');
      consPoly.setAttribute('class', 'fc17-consensus-polygon');
      consPoly.setAttribute('points', consensusPoints);
      meanPoly.parentNode.insertBefore(consPoly, meanPoly);

      // Consensus vertex dots (subtle, beneath FC dots)
      axisDefs.forEach(function(def) {
        var v = Math.max(0, Math.min(10, cdata.consensus[def[0]] || 0));
        var p = pointAt(def[1], v, CX, CY, MAX_R);
        var dot = document.createElementNS(SVG_NS, 'circle');
        dot.setAttribute('class', 'fc17-consensus-dot');
        dot.setAttribute('cx', p.x.toFixed(1));
        dot.setAttribute('cy', p.y.toFixed(1));
        dot.setAttribute('r', '2.5');
        meanPoly.parentNode.insertBefore(dot, meanPoly);
      });
    }

    // Legend below the polygon (FC · Consensus · CI band)
    var layout = root.querySelector('.fc17-layout');
    var legend = document.createElement('div');
    legend.className = 'fc17-asym-legend';
    legend.innerHTML =
      '<div class="leg-item"><span class="leg-sw fc"></span><span>FieldCheck · calculated</span></div>' +
      '<div class="leg-item"><span class="leg-sw cons"></span><span>Market consensus · shadow</span></div>' +
      '<div class="leg-item"><span class="leg-sw ci"></span><span>95% CI band</span></div>';
    if (layout && layout.parentNode) {
      layout.parentNode.insertBefore(legend, layout.nextSibling);
    }

    // Asymmetry callout (below legend, shape-based)
    var shape = cdata.shape || 'hype';
    var callout = document.createElement('div');
    callout.className = 'fc17-asym-callout ' + shape;

    var label, text;
    if (shape === 'converged') {
      label = '\u258C The convergence';
      text = 'Consensus and FieldCheck <strong>align</strong> on every axis \u2014 the asymmetry has collapsed into truth. This is what the algorithm gravitates toward over time: validated evidence eliminates the gap.';
    } else if (shape === 'gem') {
      label = '\u258C The asymmetry \u00b7 hidden gem';
      text = '<strong>The polygon stands alone</strong>. No market consensus exists \u2014 the gem is hidden because the market wasn\\'t looking.';
    } else {
      label = '\u258C The asymmetry';
      text = 'Market grades on <strong>projection</strong>. We grade on <strong>evidence-against-10</strong>. The consensus polygon overshoots the FC polygon \u2014 that gap is the bet. Every axis above shows where the market priced production, athleticism, or character the evidence hasn\\'t yet delivered.';
    }

    var metaHtml = '';
    if (cdata.sources && cdata.sources.length) {
      metaHtml = '<div class="fc17-asym-meta"><span>Consensus sources: ' + cdata.sources.join(' \u00b7 ') + '</span>';
      if (cdata.last_updated) metaHtml += '<span>Last updated: ' + cdata.last_updated + '</span>';
      metaHtml += '</div>';
    }

    callout.innerHTML = '<div class="fc17-asym-lbl">' + label + '</div><div class="fc17-asym-txt">' + text + '</div>' + metaHtml;

    if (legend && legend.parentNode) {
      legend.parentNode.insertBefore(callout, legend.nextSibling);
    } else if (layout && layout.parentNode) {
      layout.parentNode.insertBefore(callout, layout.nextSibling);
    }
  }

'''

# Insert function just before the IIFE closing })();
iife_close = '\n})();\n'
if poly_content.count('})();') != 1:
    rollback(f"IIFE close not unique (found {poly_content.count('})();')})")

# Find the last occurrence safely
idx = poly_content.rfind('})();')
if idx < 0:
    rollback("IIFE close not found")
poly_content = poly_content[:idx] + ENHANCE_FN + poly_content[idx:]
print(f"  ✓ Function · enhanceWithConsensus injected before IIFE close")


# ── PATCH 3C · hook enhanceWithConsensus into mount ──────────────
mount_anchor = "container.appendChild(root);\n      return true;"
mount_replacement = "container.appendChild(root);\n      enhanceWithConsensus(root, canonical);\n      return true;"

if poly_content.count(mount_anchor) != 1:
    rollback(f"Mount anchor not unique (found {poly_content.count(mount_anchor)})")
poly_content = poly_content.replace(mount_anchor, mount_replacement, 1)
print(f"  ✓ Hook · enhanceWithConsensus called in mount()")


# Write polygon mount
POLYGON_MOUNT.write_text(poly_content)
print(f"  ✓ Wrote {POLYGON_MOUNT.name} ({POLYGON_MOUNT.stat().st_size:,} B, was {backup1.stat().st_size:,})")


# ── PATCH 3D · add consensus-data script tag in verdict.html ─────
verdict_anchor = '<script src="/fc17-polygon-mount.js" defer></script>'
verdict_replacement = '<script src="/fc17-consensus-data.js" defer></script>\n<script src="/fc17-polygon-mount.js" defer></script>'

if verdict_anchor not in verdict_content:
    rollback("Verdict polygon script tag not found")
if verdict_content.count(verdict_anchor) != 1:
    rollback(f"Verdict anchor not unique (found {verdict_content.count(verdict_anchor)})")

verdict_content = verdict_content.replace(verdict_anchor, verdict_replacement, 1)
VERDICT_HTML.write_text(verdict_content)
print(f"  ✓ Verdict · fc17-consensus-data.js script tag added")


# ════════════════════════ STEP 4 · verification ════════════════════════

print(f"\n▸ Verification\n")

checks = [
    ('CSS · consensus polygon class',     '.fc17-consensus-polygon{', POLYGON_MOUNT),
    ('CSS · asymmetry callout class',     '.fc17-asym-callout{',      POLYGON_MOUNT),
    ('CSS · legend styles',               '.fc17-asym-legend{',       POLYGON_MOUNT),
    ('Function · enhanceWithConsensus',   'function enhanceWithConsensus(root, canonical)', POLYGON_MOUNT),
    ('Hook · call in mount()',            'enhanceWithConsensus(root, canonical)', POLYGON_MOUNT),
    ('Verdict · consensus-data script',   '<script src="/fc17-consensus-data.js" defer>', VERDICT_HTML),
    ('Verdict · polygon-mount preserved', '<script src="/fc17-polygon-mount.js" defer>',   VERDICT_HTML),
    ('Consensus data file present',       'cooper_flagg',             CONSENSUS_DATA),
]

all_pass = True
for label, marker, file in checks:
    if not file.exists():
        print(f"  ✗ {label} (file missing)")
        all_pass = False
        continue
    found = marker in file.read_text()
    print(f"  {'✓' if found else '✗'} {label}")
    if not found:
        all_pass = False

if not all_pass:
    rollback("post-patch verification failed")


# ════════════════════════ STEP 5 · summary ════════════════════════

print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" POLYGON POLISH V5 · APPLIED  ·  Sprint A1 v2 consensus overlay live")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" Modified · {POLYGON_MOUNT.name} ({POLYGON_MOUNT.stat().st_size:,} B, was {backup1.stat().st_size:,})")
print(f" Modified · {VERDICT_HTML.name} ({VERDICT_HTML.stat().st_size:,} B, was {backup2.stat().st_size:,})")
print(f" Added    · {CONSENSUS_DATA.name} ({CONSENSUS_DATA.stat().st_size:,} B)")
print(f" Backups  · {backup1.name}")
print(f"           · {backup2.name}")
print()
print(f" Coverage · {CONSENSUS_DATA.name} has consensus polygons for:")
print(f"             cooper_flagg (hype) · caleb_williams (hype)")
print(f"             caitlin_clark (converged) · avery_skinner (converged)")
print(f"             Other players → no consensus overlay rendered (graceful degradation)")
print()
print(f" ROLLBACK · single file (most surgical):")
print(f"            cp {backup1.name} {POLYGON_MOUNT.name}")
print(f"            cp {backup2.name} {VERDICT_HTML.name}")
print(f"            ./fc-deploy-dev.sh")
print()
print(f" ROLLBACK · full state (nuclear):")
print(f"            tar -xzf FCBase17_V002_pre_polygon_polish_*.tar.gz -C .")
print(f"            ./fc-deploy-dev.sh")
print()
print(f" NEXT · ./fc-deploy-dev.sh")
print(f"        Then test on DEV with Cooper Flagg + Caitlin Clark URLs")
print(f"        If good → ./fc-promote-prod.sh")
