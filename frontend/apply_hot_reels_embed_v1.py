#!/usr/bin/env python3
"""
apply_hot_reels_embed_v1.py

FCBase28 · Replaces JSJ's prototype short_form data with REAL direct URLs
(YouTube Shorts video IDs, Instagram Reel post IDs) AND adds an in-page modal
player that opens when a Hot Reel card is tapped. Iframe embeds keep the user
on FieldCheck.

What changes:
  PATCH A — FE_CURATED_GENZ.jordansmithjr.short_form replaced with 6 real entries
            (3 YouTube Shorts + 2 IG Reels + 1 long-form YouTube video).
            Socials updated to verified handles: @lilsmitty_23 (IG), @sm23itty (X).
  PATCH B — Inject inline <script> block (right before </body>) that:
            - Defines fcOpenHotReelModal(url, platform, title)
            - Adds modal CSS (overlay, content, close, iframe)
            - Adds document-level delegated click listener on .fc-hr-card
              that prevents external nav and opens the modal instead.
            - Maps YT URLs → /embed/{ID}, IG URLs → /embed, TikTok → search fallback.

Run from fieldcheck-proxy directory:
  python3 apply_hot_reels_embed_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-embed.bak')

# ─── PATCH A: Replace FE_CURATED_GENZ with REAL URLs + verified handles ───────
DATA_OLD = """    'jordansmithjr': {
      short_form: [
        { url: 'https://www.youtube.com/results?search_query=Jordan+Smith+Jr+Arkansas+commit&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Arkansas commit reaction \\u00b7 Coach Cal handshake',
          duration_seconds: 42, creator: '@PaulVIHoops' },
        { url: 'https://www.youtube.com/results?search_query=Jordan+Smith+Jr+39+points+WCAC&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: '39 PTS double-OT vs St. John\\u2019s \\u2014 title shot',
          duration_seconds: 55, creator: '@OvertimeBBall' },
        { url: 'https://www.instagram.com/explore/tags/jordansmithjr/',
          platform: 'instagram_reel', title: '5AM gym session before Naismith ceremony',
          duration_seconds: 28, creator: '@jordansmithjr' },
        { url: 'https://www.instagram.com/explore/tags/paulviHoops/',
          platform: 'instagram_reel', title: 'Family signing day \\u00b7 Arkansas red',
          duration_seconds: 19, creator: '@jordansmithjr' },
        { url: 'https://www.tiktok.com/search?q=Jordan%20Smith%20Jr%20basketball',
          platform: 'tiktok', title: 'Mock draft talk \\u00b7 "lottery pick by 2027"',
          duration_seconds: 46, creator: '@hooper.io' },
        { url: 'https://www.tiktok.com/search?q=Jordan%20Smith%20Jr%20Paul%20VI',
          platform: 'tiktok', title: 'Coach Cal call \\u00b7 live reaction',
          duration_seconds: 34, creator: '@jsj_hoops' }
      ],
      socials: { instagram: '@jordansmithjr', tiktok: '@jsj_hoops', x: '@JordanSmithJr' }
    }"""

DATA_NEW = """    'jordansmithjr': {
      /* FCBase28 · VERIFIED direct URLs (embed-ready) */
      short_form: [
        { url: 'https://www.youtube.com/shorts/SXsTZFfvD-Y',
          platform: 'youtube_shorts', title: 'JSJ has BEEN HIM \\u00b7 EYBL fyp moments',
          duration_seconds: 38, creator: '@MADEHoops' },
        { url: 'https://www.youtube.com/shorts/On_WJNufn_o',
          platform: 'youtube_shorts', title: 'Two-Way SUPERSTAR \\u00b7 senior season',
          duration_seconds: 52, creator: '@OvertimeHoops' },
        { url: 'https://www.youtube.com/shorts/V5nUc-cIVJM',
          platform: 'youtube_shorts', title: 'Over or Under? Future top-5 NBA pick',
          duration_seconds: 45, creator: '@HoopsAnalysis' },
        { url: 'https://www.youtube.com/watch?v=vuVl4Kz9SzM',
          platform: 'youtube', title: 'CBS Sports HQ \\u00b7 Arkansas commit reaction',
          duration_seconds: 178, creator: '@CBSSportsHQ' },
        { url: 'https://www.instagram.com/p/DWXMRl4Ce6h/',
          platform: 'instagram_reel', title: 'King of the court \\u00b7 Gatorade NPOY announcement',
          duration_seconds: 30, creator: '@Gatorade' },
        { url: 'https://www.instagram.com/p/DGe1hEysPQ1/',
          platform: 'instagram_reel', title: 'Scored HALF of Paul VI\\u2019s points \\u00b7 ESPN 60 #5',
          duration_seconds: 24, creator: '@lilsmitty_23' }
      ],
      socials: { instagram: '@lilsmitty_23', x: '@sm23itty' }
    }"""

# ─── PATCH B: Inject modal player + click interceptor before </body> ──────────
EMBED_BLOCK = """<!-- FCBase28 · Hot Reels modal player (added 2026-06-07) -->
<script>
(function(){
  if (window._fcHrModalInit) return;
  window._fcHrModalInit = true;

  /* Modal CSS — injected once */
  var css = '\\
.fc-hr-mod-overlay{position:fixed;inset:0;background:rgba(8,8,12,.92);z-index:99999;display:flex;align-items:center;justify-content:center;padding:24px;animation:fcHrModFade .25s ease}\\
@keyframes fcHrModFade{from{opacity:0}to{opacity:1}}\\
.fc-hr-mod-content{position:relative;max-width:min(440px,95vw);max-height:90vh;display:flex;flex-direction:column;gap:12px}\\
.fc-hr-mod-frame{aspect-ratio:9/16;width:100%;background:#0a0a0e;border-radius:18px;overflow:hidden;border:1px solid #2a2a32;box-shadow:0 30px 80px -20px rgba(0,0,0,.8)}\\
.fc-hr-mod-frame.fc-hr-wide{aspect-ratio:16/9}\\
.fc-hr-mod-frame iframe{width:100%;height:100%;border:0;display:block}\\
.fc-hr-mod-title{color:#eee;font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;line-height:1.4;text-align:center;opacity:.85}\\
.fc-hr-mod-close{position:absolute;top:-44px;right:0;background:rgba(255,255,255,.95);color:#111;border:0;width:36px;height:36px;border-radius:50%;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-weight:700;font-family:system-ui;transition:transform .2s ease}\\
.fc-hr-mod-close:hover{transform:scale(1.08);background:#f0c66e}\\
.fc-hr-mod-open{position:absolute;bottom:-44px;left:0;right:0;text-align:center;color:rgba(255,255,255,.7);font-size:11px;font-family:ui-monospace,Menlo,monospace;text-decoration:none;letter-spacing:.05em;text-transform:uppercase}\\
.fc-hr-mod-open:hover{color:#f0c66e}\\
';
  var s = document.createElement('style');
  s.id = 'fc-hr-mod-styles';
  s.appendChild(document.createTextNode(css));
  document.head.appendChild(s);

  /* URL → embed-src translator */
  function _embedSrc(url, platform){
    try {
      if (platform === 'youtube_shorts' || platform === 'youtube') {
        var m = url.match(/(?:youtube\\.com\\/shorts\\/|youtube\\.com\\/watch\\?v=|youtu\\.be\\/)([A-Za-z0-9_-]{11})/);
        if (m) return { src: 'https://www.youtube.com/embed/' + m[1] + '?autoplay=1&rel=0', wide: platform === 'youtube' };
      } else if (platform === 'instagram_reel' || platform === 'instagram') {
        var m2 = url.match(/instagram\\.com\\/(?:p|reel)\\/([A-Za-z0-9_-]+)/);
        if (m2) return { src: 'https://www.instagram.com/p/' + m2[1] + '/embed/captioned/?cr=1&v=14', wide: false };
      } else if (platform === 'tiktok') {
        var m3 = url.match(/tiktok\\.com\\/@[^/]+\\/video\\/(\\d+)/);
        if (m3) return { src: 'https://www.tiktok.com/embed/v2/' + m3[1], wide: false };
      }
    } catch(e) {}
    return null;
  }

  window.fcOpenHotReelModal = function(url, platform, title){
    var emb = _embedSrc(url, platform);
    var overlay = document.createElement('div');
    overlay.className = 'fc-hr-mod-overlay';
    var content = document.createElement('div');
    content.className = 'fc-hr-mod-content';
    var closeBtn = document.createElement('button');
    closeBtn.className = 'fc-hr-mod-close';
    closeBtn.innerHTML = '\\u2715';
    closeBtn.setAttribute('aria-label','Close');
    var frame = document.createElement('div');
    frame.className = 'fc-hr-mod-frame' + (emb && emb.wide ? ' fc-hr-wide' : '');
    if (emb) {
      var ifr = document.createElement('iframe');
      ifr.src = emb.src;
      ifr.setAttribute('allow','autoplay; encrypted-media; picture-in-picture; fullscreen');
      ifr.setAttribute('allowfullscreen','');
      ifr.setAttribute('loading','eager');
      frame.appendChild(ifr);
    } else {
      frame.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#888;font-family:ui-sans-serif,system-ui;font-size:13px;padding:20px;text-align:center">Embed unavailable.<br>Use the open link below.</div>';
    }
    var titleEl = document.createElement('div');
    titleEl.className = 'fc-hr-mod-title';
    titleEl.textContent = title || '';
    var openLink = document.createElement('a');
    openLink.className = 'fc-hr-mod-open';
    openLink.href = url;
    openLink.target = '_blank';
    openLink.rel = 'noopener';
    openLink.textContent = 'Open on ' + (platform === 'tiktok' ? 'TikTok' : platform.indexOf('instagram') === 0 ? 'Instagram' : 'YouTube') + ' \\u2197';
    content.appendChild(closeBtn);
    content.appendChild(frame);
    content.appendChild(titleEl);
    content.appendChild(openLink);
    overlay.appendChild(content);
    function close(){ if (overlay.parentNode) overlay.parentNode.removeChild(overlay); document.removeEventListener('keydown', escClose); }
    function escClose(e){ if (e.key === 'Escape') close(); }
    closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', function(e){ if (e.target === overlay) close(); });
    document.addEventListener('keydown', escClose);
    document.body.appendChild(overlay);
  };

  /* Delegated click listener — intercept Hot Reel card clicks. */
  document.addEventListener('click', function(e){
    var card = e.target.closest && e.target.closest('.fc-hr-card');
    if (!card) return;
    e.preventDefault();
    e.stopPropagation();
    var url = card.getAttribute('href') || card.dataset.url;
    var platform = card.dataset.platform || (url && url.indexOf('youtube') !== -1 ? (url.indexOf('shorts') !== -1 ? 'youtube_shorts' : 'youtube') : url && url.indexOf('instagram') !== -1 ? 'instagram_reel' : url && url.indexOf('tiktok') !== -1 ? 'tiktok' : '');
    var title = card.dataset.title || card.getAttribute('aria-label') || '';
    if (url) window.fcOpenHotReelModal(url, platform, title);
  }, true);
})();
</script>
</body>"""


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    # Validate anchors
    if DATA_OLD not in content:
        print("ERROR: Patch A data anchor not found. FE_CURATED_GENZ may have already been modified.")
        return 1
    if content.count(DATA_OLD) > 1:
        print(f"ERROR: Patch A anchor appears {content.count(DATA_OLD)} times. Ambiguous.")
        return 1
    if '</body>' not in content:
        print("ERROR: </body> not found in HTML — cannot inject embed block.")
        return 1
    if content.count('</body>') > 1:
        print(f"ERROR: </body> appears {content.count('</body>')} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(DATA_OLD, DATA_NEW, 1)
    new_content = new_content.replace('</body>', EMBED_BLOCK, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patches A+B applied  ({delta:+d} bytes)")
    print()
    print("Next:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Hard refresh:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Tap any Hot Reel card — should open a fullscreen modal player on FieldCheck")
    print("with the YouTube Short / IG Reel embedded. Click outside or press Esc to close.")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
