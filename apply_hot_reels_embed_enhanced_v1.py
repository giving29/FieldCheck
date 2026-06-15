#!/usr/bin/env python3
"""
apply_hot_reels_embed_enhanced_v1.py

FCBase28-fix · Replaces the FCBase28 modal script with an enhanced version:

  1. YT THUMBNAILS on static cards (via MutationObserver) — pulls from
     i.ytimg.com/vi/{ID}/hqdefault.jpg so users see real video previews
     instead of opaque gradient boxes. Gradient overlay stays at the bottom
     for the platform tag + title readability.

  2. YOUTUBE-NOCOOKIE embed domain instead of youtube.com — fewer embed
     restrictions, more videos play inline.

  3. NO AUTOPLAY (browsers block autoplay without user gesture, which
     produces a blank iframe). User taps play inside the modal.

  4. STANDARD INSTAGRAM EMBED URL (drops the /captioned/?cr=1&v=14 suffix
     that fails for some posts; standard /embed works on all public posts).

  5. PROPER PLAYER PARAMS: rel=0, modestbranding=1, playsinline=1, controls=1.

Single str_replace: replaces the entire FCBase28 modal <script> block.

Run from fieldcheck-proxy directory:
  python3 apply_hot_reels_embed_enhanced_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-embed-enh.bak')

# ─── Anchor: the entire previous FCBase28 modal block ────────────────────────
OLD_START = "<!-- FCBase28 · Hot Reels modal player (added 2026-06-07) -->"
OLD_END = "</script>\n</body>"


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    start_idx = content.find(OLD_START)
    if start_idx == -1:
        print("ERROR: Previous FCBase28 modal block anchor not found.")
        return 1
    if content.count(OLD_START) > 1:
        print(f"ERROR: Start anchor appears {content.count(OLD_START)} times. Ambiguous.")
        return 1

    end_idx = content.find(OLD_END, start_idx)
    if end_idx == -1:
        print("ERROR: End anchor (</script>\\n</body>) not found after start.")
        return 1
    end_idx += len(OLD_END)

    # Build the replacement block
    new_block = """<!-- FCBase28-fix · Enhanced Hot Reels modal + YT thumbnails (2026-06-07) -->
<script>
(function(){
  if (window._fcHrModalInit) return;
  window._fcHrModalInit = true;

  /* ─── Modal CSS ─── */
  var css = [
    '.fc-hr-mod-overlay{position:fixed;inset:0;background:rgba(8,8,12,.92);z-index:99999;display:flex;align-items:center;justify-content:center;padding:24px;animation:fcHrModFade .25s ease}',
    '@keyframes fcHrModFade{from{opacity:0}to{opacity:1}}',
    '.fc-hr-mod-content{position:relative;max-width:min(440px,95vw);max-height:90vh;display:flex;flex-direction:column;gap:12px}',
    '.fc-hr-mod-frame{aspect-ratio:9/16;width:100%;background:#0a0a0e;border-radius:18px;overflow:hidden;border:1px solid #2a2a32;box-shadow:0 30px 80px -20px rgba(0,0,0,.8)}',
    '.fc-hr-mod-frame.fc-hr-wide{aspect-ratio:16/9}',
    '.fc-hr-mod-frame iframe{width:100%;height:100%;border:0;display:block;background:#0a0a0e}',
    '.fc-hr-mod-title{color:#eee;font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;line-height:1.4;text-align:center;opacity:.85}',
    '.fc-hr-mod-close{position:absolute;top:-44px;right:0;background:rgba(255,255,255,.95);color:#111;border:0;width:36px;height:36px;border-radius:50%;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-weight:700;font-family:system-ui;transition:transform .2s ease}',
    '.fc-hr-mod-close:hover{transform:scale(1.08);background:#f0c66e}',
    '.fc-hr-mod-open{position:absolute;bottom:-44px;left:0;right:0;text-align:center;color:rgba(255,255,255,.7);font-size:11px;font-family:ui-monospace,Menlo,monospace;text-decoration:none;letter-spacing:.05em;text-transform:uppercase}',
    '.fc-hr-mod-open:hover{color:#f0c66e}',
    /* Static-card YT thumbnail enhancement */
    '.fc-hr-card.fc-hr-yt[data-thumb]{background-image:linear-gradient(180deg,transparent 35%,rgba(0,0,0,.85) 100%),var(--fc-hr-thumb)!important;background-size:cover,cover!important;background-position:center,center!important}',
    '.fc-hr-card.fc-hr-ig[data-thumb]{background-image:linear-gradient(180deg,transparent 35%,rgba(0,0,0,.85) 100%),var(--fc-hr-thumb)!important;background-size:cover,cover!important;background-position:center,center!important}'
  ].join('');
  var sEl = document.createElement('style');
  sEl.id = 'fc-hr-mod-styles';
  sEl.appendChild(document.createTextNode(css));
  document.head.appendChild(sEl);

  /* ─── URL → embed src translator ─── */
  function _ytId(url){
    var m = url.match(/(?:youtube\\.com\\/shorts\\/|youtube\\.com\\/watch\\?v=|youtu\\.be\\/)([A-Za-z0-9_-]{11})/);
    return m ? m[1] : null;
  }
  function _igId(url){
    var m = url.match(/instagram\\.com\\/(?:p|reel)\\/([A-Za-z0-9_-]+)/);
    return m ? m[1] : null;
  }
  function _ttId(url){
    var m = url.match(/tiktok\\.com\\/@[^/]+\\/video\\/(\\d+)/);
    return m ? m[1] : null;
  }
  function _embedSrc(url, platform){
    try {
      if (platform === 'youtube_shorts' || platform === 'youtube') {
        var id = _ytId(url);
        if (id) return { src: 'https://www.youtube-nocookie.com/embed/' + id + '?rel=0&modestbranding=1&playsinline=1&controls=1', wide: platform === 'youtube' };
      } else if (platform === 'instagram_reel' || platform === 'instagram') {
        var id2 = _igId(url);
        if (id2) return { src: 'https://www.instagram.com/p/' + id2 + '/embed', wide: false };
      } else if (platform === 'tiktok') {
        var id3 = _ttId(url);
        if (id3) return { src: 'https://www.tiktok.com/embed/v2/' + id3, wide: false };
      }
    } catch(e) {}
    return null;
  }

  /* ─── Modal opener ─── */
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
      ifr.setAttribute('allow','autoplay; encrypted-media; picture-in-picture; fullscreen; clipboard-write');
      ifr.setAttribute('allowfullscreen','');
      ifr.setAttribute('loading','eager');
      ifr.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
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
    openLink.textContent = 'Open on ' + (platform === 'tiktok' ? 'TikTok' : (platform && platform.indexOf('instagram') === 0) ? 'Instagram' : 'YouTube') + ' \\u2197';
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

  /* ─── Click interceptor on Hot Reel cards ─── */
  document.addEventListener('click', function(e){
    var card = e.target.closest && e.target.closest('.fc-hr-card');
    if (!card) return;
    e.preventDefault();
    e.stopPropagation();
    var url = card.getAttribute('href') || card.dataset.url;
    var platform = card.dataset.platform || (url && url.indexOf('youtube') !== -1 ? (url.indexOf('shorts') !== -1 ? 'youtube_shorts' : 'youtube') : url && url.indexOf('instagram') !== -1 ? 'instagram_reel' : url && url.indexOf('tiktok') !== -1 ? 'tiktok' : '');
    var title = card.dataset.title || card.getAttribute('aria-label') || (card.querySelector('.fc-hr-card-title') || {}).textContent || '';
    if (url) window.fcOpenHotReelModal(url, platform, title);
  }, true);

  /* ─── Static-card thumbnail decoration ─── */
  function decorateCards(){
    document.querySelectorAll('.fc-hr-card').forEach(function(card){
      if (card.dataset.thumb) return;
      var href = card.getAttribute('href') || '';
      var id = _ytId(href);
      if (id) {
        card.style.setProperty('--fc-hr-thumb', 'url(https://i.ytimg.com/vi/' + id + '/hqdefault.jpg)');
        card.setAttribute('data-thumb', '1');
        return;
      }
      /* Instagram thumbnails come through their embed, not a public CDN.
         Leave the gradient for IG/TT cards as-is. */
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', decorateCards);
  } else {
    decorateCards();
  }
  /* Also re-decorate on DOM mutations (renderVerdict may render after load) */
  var mo = new MutationObserver(function(){ decorateCards(); });
  mo.observe(document.body, { childList: true, subtree: true });
})();
</script>
</body>"""

    new_content = content[:start_idx] + new_block + content[end_idx:]
    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Enhanced embed block applied  ({delta:+d} bytes)")
    print()
    print("Deploy:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Then hard refresh:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Expected:")
    print("  - YT Shorts cards now show real YouTube thumbnails (not opaque gradient)")
    print("  - IG Reel cards keep the purple/sunset gradient (no public IG thumbnail API)")
    print("  - Tap YT card → modal with YouTube player visible (controls + click to play)")
    print("  - Tap IG card → IG embed loads inline (already worked)")
    print()
    print("If all 6 cards look right + 4-6 of them embed in modal:")
    print("  ./fc-promote-prod.sh")
    print("  ./fc-freeze.sh FCBase28_HOTREELS_EMBED")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
