#!/usr/bin/env python3
"""
apply_class_leaderboard_v1.py

FCBase35 \\u00b7 Phase 6 Strike 1 \\u00b7 Class Leaderboard.

Adds a "// THE LEADERBOARD" section on every verdict page. Shows the
current sport's verified-athlete corpus sorted by composite, with the
current player highlighted at their rank. Every row taps through to
that athlete's verdict page \\u2014 the leaderboard becomes a discovery
surface, not just a ranking display.

Architecture:
  - Self-mounting via MutationObserver (matches FCBase31\\u201334 pattern)
  - Hardcoded sport-corpus (current Phase 5 marquees: Boozer, Dybantsa,
    Stokes, Williams, Brandon, JSJ) \\u2014 expands as Phase 6.2 wires
    backend /leaderboard endpoint
  - Current player slotted into rank by composite \\u2014 if already in
    corpus, highlighted; if not, dynamically added + sorted
  - Per-sport leaderboard (mens-basketball, football, etc.)
  - Each row is a link to /fieldcheck-verdict.html?q=...&sport=... \\u2014
    discovery + navigation in one tap

Inserts after the Trajectory section (FCBase34), before Highlights.

Single str_replace: injects the module before </body>.

Run from fieldcheck-proxy directory:
  python3 apply_class_leaderboard_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-leaderboard.bak')

LEADERBOARD_BLOCK = """<!-- FCBase35 \\u00b7 Phase 6 Strike 1 \\u00b7 Class Leaderboard (2026-06-07) -->
<script>
(function(){
  if (window._fcLeaderInit) return;
  window._fcLeaderInit = true;

  /* Per-sport verified corpus \\u2014 expands as marquees ship.
     When Phase 6.2 wires a /leaderboard endpoint on the worker,
     this hardcoded set gets replaced with a live fetch. */
  var CORPUS = {
    'mens-basketball': [
      { name: 'Cameron Boozer',    composite: 9.5, tier: 'ICON',    school: 'Duke (fr)',          sport: 'mens-basketball' },
      { name: 'AJ Dybantsa',       composite: 9.4, tier: 'ELITE+',  school: 'BYU (fr)',           sport: 'mens-basketball' },
      { name: 'Tyran Stokes',      composite: 9.0, tier: 'ELITE+',  school: 'Kansas (signee)',    sport: 'mens-basketball' },
      { name: 'Cameron Williams',  composite: 7.8, tier: 'ELITE',   school: 'Duke (signee)',      sport: 'mens-basketball' },
      { name: 'Jordan Smith Jr',   composite: 5.3, tier: 'SCOUT',   school: 'Arkansas (signee)',  sport: 'mens-basketball' }
    ],
    'football': [
      { name: 'Faizon Brandon',    composite: 8.2, tier: 'ELITE',   school: 'Tennessee (signee)', sport: 'football' }
    ]
  };

  /* CSS */
  var css = [
    '.fc-leader-section{padding:32px 24px;margin:8px 0 14px;border-radius:18px;background:linear-gradient(180deg,rgba(20,20,26,.6) 0%,rgba(10,10,14,.4) 100%);border:1px solid #2a2a32;position:relative;overflow:hidden}',
    '.fc-leader-section::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(240,198,110,.4),transparent)}',
    '.fc-leader-header{display:flex;align-items:baseline;justify-content:space-between;gap:14px;margin-bottom:22px;font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:rgba(240,198,110,.85);flex-wrap:wrap}',
    '.fc-leader-header-sub{color:rgba(255,255,255,.45);font-size:10px}',
    '.fc-leader-rows{display:flex;flex-direction:column;gap:1px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);border-radius:12px;overflow:hidden}',
    '.fc-leader-row{display:grid;grid-template-columns:42px 1fr 70px 90px;gap:14px;align-items:center;padding:14px 16px;background:rgba(10,10,14,.6);color:rgba(255,255,255,.85);font-family:ui-sans-serif,system-ui,sans-serif;font-size:14px;text-decoration:none;transition:background .2s ease,transform .15s ease;cursor:pointer}',
    '@media(max-width:520px){.fc-leader-row{grid-template-columns:34px 1fr 60px 70px;gap:10px;padding:12px 12px;font-size:13px}}',
    '.fc-leader-row:hover{background:rgba(20,20,26,.85)}',
    '.fc-leader-row.is-current{background:linear-gradient(90deg,rgba(240,198,110,.12),rgba(240,198,110,.04));border-left:3px solid #f0c66e;padding-left:13px}',
    '.fc-leader-row.is-current:hover{background:linear-gradient(90deg,rgba(240,198,110,.18),rgba(240,198,110,.06))}',
    '.fc-leader-rank{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:24px;line-height:1;font-weight:700;color:rgba(255,255,255,.45);letter-spacing:-.01em}',
    '.fc-leader-row.is-current .fc-leader-rank{color:#f0c66e}',
    '.fc-leader-row.is-icon .fc-leader-rank{color:#f0c66e}',
    '.fc-leader-name{display:flex;flex-direction:column;gap:2px;min-width:0;overflow:hidden}',
    '.fc-leader-name-title{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:18px;line-height:1;font-weight:700;color:#fff;letter-spacing:-.005em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
    '.fc-leader-name-meta{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.06em;color:rgba(255,255,255,.5);line-height:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
    '.fc-leader-composite{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:28px;line-height:1;font-weight:700;color:#f0c66e;letter-spacing:-.02em;text-align:right}',
    '@media(max-width:520px){.fc-leader-composite{font-size:22px}}',
    '.fc-leader-tier{font-family:ui-monospace,Menlo,monospace;font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:#f0c66e;background:rgba(240,198,110,.12);border:1px solid rgba(240,198,110,.3);padding:3px 6px;border-radius:5px;text-align:center;font-weight:600;line-height:1.2}',
    '@media(max-width:520px){.fc-leader-tier{font-size:8.5px;padding:2px 4px}}',
    '.fc-leader-footer{margin-top:14px;font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;line-height:1.55;color:rgba(255,255,255,.5)}',
    '.fc-leader-footer strong{color:rgba(255,255,255,.8);font-weight:500}',
    '.fc-leader-empty{padding:20px;text-align:center;font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.5)}'
  ].join('');
  var sEl = document.createElement('style');
  sEl.id = 'fc-leader-styles';
  sEl.appendChild(document.createTextNode(css));
  document.head.appendChild(sEl);

  /* Harvest current player from DOM */
  function _harvest(){
    var urlParams = new URLSearchParams(window.location.search);
    var name = urlParams.get('q') || '';
    var sport = urlParams.get('sport') || 'mens-basketball';
    var nameEl = document.querySelector('h1');
    if (nameEl && nameEl.textContent && nameEl.textContent.trim().length > 1 && nameEl.textContent.trim().length < 60) {
      name = nameEl.textContent.trim();
    }
    var score = '';
    var all = document.querySelectorAll('*');
    for (var i=0; i<all.length && i<1500; i++){
      var t = (all[i].textContent || '').trim();
      if (/^[0-9]\\.[0-9]$/.test(t) && all[i].children.length === 0) { score = t; break; }
    }
    var tier = '';
    var tierMatch = (document.body.innerText || '').match(/\\b(ICON|ELITE\\+?|STAR|PROSPECT|SCOUT)\\b/);
    if (tierMatch) tier = tierMatch[1];
    var bodyText = document.body.innerText || '';
    var schoolMatch = bodyText.match(/([A-Z][^\\n]{0,40}(?:Catholic|Prep|HS|High School|Academy|University|signee|fr))/);
    var school = schoolMatch ? schoolMatch[1] : '';
    return { name: name, composite: parseFloat(score) || 0, tier: tier, school: school, sport: sport };
  }

  /* Build leaderboard rows */
  function _buildBoard(current){
    var sport = current.sport;
    var board = (CORPUS[sport] || []).slice();
    var currentLower = (current.name || '').toLowerCase().trim();
    var inBoard = board.some(function(p){ return p.name.toLowerCase().trim() === currentLower; });
    if (!inBoard && current.name && current.composite > 0) {
      board.push({
        name: current.name,
        composite: current.composite,
        tier: current.tier || '\\u2014',
        school: current.school || '',
        sport: sport,
        injected: true
      });
    }
    board.sort(function(a, b){ return b.composite - a.composite; });
    return { board: board, sport: sport };
  }

  /* Sport label */
  function _sportLabel(sport){
    return (sport || '').replace(/-/g, ' ').replace(/\\b\\w/g, function(c){ return c.toUpperCase(); });
  }

  /* Render section */
  function _render(current){
    var built = _buildBoard(current);
    var board = built.board;
    var sport = built.sport;
    var sportLabel = _sportLabel(sport);

    var html =
      '<div class="fc-leader-header">' +
        '<span>// The Leaderboard \\u00b7 ' + sportLabel + '</span>' +
        '<span class="fc-leader-header-sub">verified corpus \\u00b7 ' + board.length + ' athletes</span>' +
      '</div>';

    if (board.length === 0) {
      html += '<div class="fc-leader-empty">Corpus expanding \\u2014 verified leaderboard coming in Phase 6.2</div>';
    } else {
      html += '<div class="fc-leader-rows">';
      board.forEach(function(p, idx){
        var rank = idx + 1;
        var isCurrent = p.name.toLowerCase().trim() === (current.name || '').toLowerCase().trim();
        var isIcon = p.tier === 'ICON' && !isCurrent;
        var cls = 'fc-leader-row' + (isCurrent ? ' is-current' : '') + (isIcon ? ' is-icon' : '');
        var href = '/fieldcheck-verdict.html?q=' + encodeURIComponent(p.name) + '&sport=' + encodeURIComponent(p.sport || sport);
        html +=
          '<a class="' + cls + '" href="' + href + '">' +
            '<div class="fc-leader-rank">#' + rank + '</div>' +
            '<div class="fc-leader-name">' +
              '<div class="fc-leader-name-title">' + p.name + (isCurrent ? ' \\u2190 you' : '') + '</div>' +
              '<div class="fc-leader-name-meta">' + (p.school || '\\u00b7') + '</div>' +
            '</div>' +
            '<div class="fc-leader-composite">' + p.composite.toFixed(1) + '</div>' +
            '<div class="fc-leader-tier">' + (p.tier || '\\u2014') + '</div>' +
          '</a>';
      });
      html += '</div>';
    }

    html += '<div class="fc-leader-footer">Corpus expanding to <strong>110+ athletes</strong> in Phase 6 \\u00b7 hidden gems, watchlist, and daily digest shipping next.</div>';

    return html;
  }

  /* Mount */
  function _mount(){
    if (document.querySelector('.fc-leader-section')) return;
    if (!/fieldcheck-verdict\\.html/.test(window.location.pathname)) return;
    var current = _harvest();
    if (!current.name || current.name.length < 2 || current.composite <= 0) return;

    /* Insertion: after Trajectory if present, else after Polygon, else after Hot Reels */
    var anchor = document.querySelector('.fc-traj-section');
    if (!anchor) anchor = document.querySelector('.fc-poly-section');
    if (!anchor) {
      var hr = document.querySelector('.fc-hr-row');
      if (hr) anchor = hr.closest('.sec');
    }
    if (!anchor) {
      var secs = document.querySelectorAll('.sec');
      if (secs.length) anchor = secs[0];
    }
    if (!anchor) return;

    var section = document.createElement('section');
    section.className = 'fc-leader-section';
    section.innerHTML = _render(current);

    anchor.insertAdjacentElement('afterend', section);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', _mount);
  else _mount();
  var mo = new MutationObserver(function(){ _mount(); });
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

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace('</body>', LEADERBOARD_BLOCK, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Class Leaderboard module injected  ({delta:+d} bytes)")
    print()
    print("Deploy:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Hard refresh and verify across the corpus:")
    print("  JSJ should show as #5 of 5 in mens-basketball:")
    print("    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print("  Boozer should show as #1 of 5 (ICON tier):")
    print("    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Boozer&sport=mens-basketball")
    print()
    print("Expected layout per verdict page:")
    print("  Hot Reels \\u2192 Polygon \\u2192 Trajectory \\u2192 LEADERBOARD \\u2192 Highlights \\u2192 News")
    print()
    print("Section shows:")
    print("  - 'The Leaderboard \\u00b7 Mens Basketball \\u00b7 verified corpus \\u00b7 N athletes'")
    print("  - Top 5 rows with rank, name, school, composite, tier")
    print("  - Current player row highlighted with gold left-border + '\\u2190 you' label")
    print("  - Each row is a link to that athlete's verdict")
    print("  - Footer: 'Corpus expanding to 110+ athletes in Phase 6'")
    print()
    print("Ship to prod:")
    print("  ./fc-promote-prod.sh")
    print("  ./fc-freeze.sh FCBase35_LEADERBOARD_LIVE")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
