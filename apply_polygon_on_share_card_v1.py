#!/usr/bin/env python3
"""
apply_polygon_on_share_card_v1.py

FCBase32 · Phase 5 Strike 3 · Polygon on Share Card.

Enhances the shareable verdict card (FCBase30) by injecting the 8-facet
polygon (FCBase31) directly into the card DOM. Result: every downloaded /
shared verdict card now carries the athlete's unique polygon fingerprint
baked into the PNG.

Architecture:
  - Pure additive patch. Does NOT modify FCBase30 or FCBase31 code.
  - MutationObserver watches for .fc-share-card mounting and injects polygon
    SVG between school-meta and score-wrap.
  - Polygon scores use IDENTICAL hashing + facet logic as FCBase31, so the
    card polygon and verdict-page polygon are the same fingerprint per player.
  - html2canvas captures the inline SVG cleanly (no external resources).

Visual: 170px polygon centered above the composite score in the card. Compact
4-letter facet labels (CHAR, MIND, STR, TLT, PHY, IQ, COA, COMP) around the
perimeter. Same gold + dark aesthetic as the rest of the card.

Single str_replace: injects the module before </body>.

Run from fieldcheck-proxy directory:
  python3 apply_polygon_on_share_card_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-polygon-on-card.bak')

POLY_ON_CARD_BLOCK = """<!-- FCBase32 · Phase 5 Strike 3 · Polygon on Share Card (2026-06-07) -->
<script>
(function(){
  if (window._fcPolyOnCardInit) return;
  window._fcPolyOnCardInit = true;

  var SHORT_LABELS = ['CHAR','MIND','STR','TLT','PHY','IQ','COA','COMP'];

  /* ─── CSS for polygon-in-card (additive only, doesn't override FCBase30) ─── */
  var css = [
    '.fc-share-polygon{position:relative;z-index:2;display:flex;justify-content:center;align-items:center;margin:14px 0 0;pointer-events:none}',
    '.fc-share-polygon svg{width:200px;height:200px;display:block;overflow:visible}',
    '.fc-share-polygon .pgrid{fill:none;stroke:rgba(255,255,255,.07);stroke-width:1}',
    '.fc-share-polygon .paxis{stroke:rgba(255,255,255,.05);stroke-width:1}',
    '.fc-share-polygon .pshape-fill{fill:rgba(240,198,110,.22)}',
    '.fc-share-polygon .pshape-stroke{fill:none;stroke:#f0c66e;stroke-width:1.8;stroke-linejoin:round;stroke-linecap:round}',
    '.fc-share-polygon .pvertex{fill:#f0c66e}',
    '.fc-share-polygon .plabel{font-family:ui-monospace,Menlo,monospace;font-size:7.5px;fill:rgba(255,255,255,.72);letter-spacing:.06em;font-weight:600}',
    '.fc-share-polygon .plabel-active{fill:rgba(240,198,110,.95)}',
    /* Tighten score area below polygon so card stays balanced */
    '.fc-share-card .fc-share-score-wrap{margin-bottom:14px}',
    '.fc-share-card .fc-share-score{font-size:78px}',
    '.fc-share-card .fc-share-awards{padding-top:10px;margin-bottom:12px;gap:4px}',
    '.fc-share-card .fc-share-award{font-size:9px}'
  ].join('');
  var sEl = document.createElement('style');
  sEl.id = 'fc-poly-on-card-styles';
  sEl.appendChild(document.createTextNode(css));
  document.head.appendChild(sEl);

  /* ─── IDENTICAL hashing logic to FCBase31 so shapes match ─── */
  function _seed(name){
    var s = 0;
    name = String(name || 'athlete').toLowerCase();
    for (var i=0; i<name.length; i++) s = ((s << 5) - s + name.charCodeAt(i)) | 0;
    return Math.abs(s);
  }
  function _facetScores(name, composite){
    var c = parseFloat(composite);
    if (!isFinite(c) || c <= 0) c = 5.0;
    var seed = _seed(name);
    var scores = [];
    for (var i=0; i<8; i++){
      var hash = ((seed * 1103515245) + 12345 + i * 2654435761) & 0x7fffffff;
      var noise = ((hash % 2000) / 1000) - 1.0;
      var sc = c + noise * 1.6;
      scores.push(Math.max(1.5, Math.min(9.8, sc)));
      seed = hash;
    }
    return scores;
  }

  /* ─── Build compact polygon SVG ─── */
  function _buildMiniPolygon(name, composite){
    var scores = _facetScores(name, composite);
    var W = 200, H = 200, cx = W/2, cy = H/2, R = 68;

    var pts = [];
    for (var i=0; i<8; i++){
      var ang = -Math.PI/2 + (i * 2 * Math.PI / 8);
      var r = (scores[i] / 10) * R;
      pts.push([cx + Math.cos(ang) * r, cy + Math.sin(ang) * r]);
    }
    var polyD = 'M ' + pts.map(function(p){ return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' L ') + ' Z';

    var grid = '';
    [0.33, 0.66, 1.0].forEach(function(p){
      var gpts = [];
      for (var i=0; i<8; i++){
        var ang = -Math.PI/2 + (i * 2 * Math.PI / 8);
        gpts.push([cx + Math.cos(ang) * p * R, cy + Math.sin(ang) * p * R]);
      }
      grid += '<path class="pgrid" d="M ' + gpts.map(function(p){ return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' L ') + ' Z"/>';
    });

    var axes = '';
    for (var i=0; i<8; i++){
      var ang = -Math.PI/2 + (i * 2 * Math.PI / 8);
      var ex = cx + Math.cos(ang) * R;
      var ey = cy + Math.sin(ang) * R;
      axes += '<line class="paxis" x1="' + cx + '" y1="' + cy + '" x2="' + ex.toFixed(1) + '" y2="' + ey.toFixed(1) + '"/>';
    }

    var verts = '';
    pts.forEach(function(p){
      verts += '<circle class="pvertex" cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="2.5"/>';
    });

    var labels = '';
    for (var i=0; i<8; i++){
      var ang = -Math.PI/2 + (i * 2 * Math.PI / 8);
      var lx = cx + Math.cos(ang) * (R + 16);
      var ly = cy + Math.sin(ang) * (R + 16);
      var anchor = 'middle';
      if (Math.cos(ang) > 0.4) anchor = 'start';
      else if (Math.cos(ang) < -0.4) anchor = 'end';
      var dy = Math.sin(ang) > 0.4 ? '0.7em' : Math.sin(ang) < -0.4 ? '0em' : '0.32em';
      var activeCls = scores[i] >= 7 ? ' plabel-active' : '';
      labels += '<text class="plabel' + activeCls + '" x="' + lx.toFixed(1) + '" y="' + ly.toFixed(1) + '" text-anchor="' + anchor + '" dy="' + dy + '">' + SHORT_LABELS[i] + '</text>';
    }

    return '<svg viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
      grid + axes +
      '<path class="pshape-fill" d="' + polyD + '"/>' +
      '<path class="pshape-stroke" d="' + polyD + '"/>' +
      verts + labels +
    '</svg>';
  }

  /* ─── Enhance the share card DOM when it appears ─── */
  function _enhance(card){
    if (!card || card.querySelector('.fc-share-polygon')) return;
    var nameEl = card.querySelector('.fc-share-name');
    var scoreEl = card.querySelector('.fc-share-score');
    if (!nameEl || !scoreEl) return;
    var name = nameEl.textContent.trim();
    var composite = scoreEl.textContent.trim();
    if (!name || !composite || composite === '\\u2014') return;

    var polyDiv = document.createElement('div');
    polyDiv.className = 'fc-share-polygon';
    polyDiv.innerHTML = _buildMiniPolygon(name, composite);

    /* Insert above the score-wrap, below the school meta */
    var scoreWrap = card.querySelector('.fc-share-score-wrap');
    if (scoreWrap) {
      scoreWrap.insertAdjacentElement('beforebegin', polyDiv);
    }
  }

  /* MutationObserver: watch for share card modal */
  var mo = new MutationObserver(function(mutations){
    mutations.forEach(function(m){
      m.addedNodes.forEach(function(n){
        if (n.nodeType !== 1) return;
        if (n.classList && n.classList.contains('fc-share-card')) {
          _enhance(n);
        } else if (n.querySelector) {
          var card = n.querySelector('.fc-share-card');
          if (card) _enhance(card);
        }
      });
    });
  });
  mo.observe(document.body, { childList: true, subtree: true });
})();
</script>
</body>"""


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    if '</body>' not in content:
        print("ERROR: </body> not found.")
        return 1
    if content.count('</body>') > 1:
        print(f"ERROR: </body> appears {content.count('</body>')} times. Ambiguous.")
        return 1

    # Verify FCBase30 share card and FCBase31 polygon are present (pre-flight)
    if '_fcShareCardInit' not in content:
        print("WARN: FCBase30 share card module not detected. Polygon will inject if card appears anyway.")
    if '_fcPolyInit' not in content:
        print("WARN: FCBase31 polygon module not detected. Hash logic is self-contained, OK.")

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace('</body>', POLY_ON_CARD_BLOCK, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Polygon-on-Share-Card module injected  ({delta:+d} bytes)")
    print()
    print("Deploy:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Hard refresh any verdict page, tap the floating 'Share Card' button:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Expected in modal:")
    print("  - Card now has polygon centered between school line and score")
    print("  - Polygon shape MATCHES the one on the verdict page (same hash)")
    print("  - Download button captures polygon in the PNG (html2canvas handles inline SVG)")
    print("  - Each player has a distinct fingerprint (compare JSJ vs Boozer vs Stokes)")
    print()
    print("Ship to prod:")
    print("  ./fc-promote-prod.sh")
    print("  ./fc-freeze.sh FCBase32_POLYGON_ON_CARD_LIVE")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
