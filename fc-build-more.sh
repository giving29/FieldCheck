#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
REDIR="${1:-_redirects}"
MODE="${2:-all}"
OUT="fieldcheck-more.html"
TMP="$(mktemp -d)"

bucket() {
  case "$1" in
    *lovb*) echo "LOVB";;
    *deck*|*pitch*) echo "Decks and Pitch";;
    *draft*|*nba*|*pro-probability*) echo "Draft and Pro";;
    *coach*|*franchise*|*program*|*fit*|*conference*|*recruiting*|*portal*|*class*) echo "Coaches and Programs";;
    *methodolog*|*calibration*|*accuracy*|*accountab*|*prediction*|*v5-algorithm*|*benchmark*|*canonical*|*trust*|*moat*|*security*|*tier*|*thesis*|*framework*|*edge*|*source*) echo "Methodology and Trust";;
    *leaderboard*|*top100*|*gems*|*drop*|*diverge*|*watchlist*|*compare*|*versus*) echo "Discovery";;
    *player*|*path*|*trajectory*|*voice*|*shape*|*clip*|*profile*|*scout*|*field-report*|*add-me*|*mypath*|*wire*|*news*|*position*) echo "Players and Verdicts";;
    *basketball*|*football*|*soccer*|*international*|*sports*) echo "Sports";;
    *) echo "Company and More";;
  esac
}

ORDER="Players and Verdicts|Discovery|Coaches and Programs|Draft and Pro|Methodology and Trust|Decks and Pitch|Sports|LOVB|Company and More"

while IFS= read -r line; do
  case "$line" in
    \#*) continue;;
    /\**) continue;;
    /*)
      route=$(echo "$line" | awk '{print $1}')
      target=$(echo "$line" | awk '{print $2}')
      if [ "$route" = "/more" ]; then continue; fi
      b=$(bucket "$route$target")
      echo "      <a class=\"mlink\" href=\"$route\">$route<span>$target</span></a>" >> "$TMP/$b.html"
    ;;
  esac
done < "$REDIR"

ROUTES_HTML=""
IFS='|'
for b in $ORDER; do
  if [ -f "$TMP/$b.html" ]; then
    ROUTES_HTML="$ROUTES_HTML
    <div class=\"grp\"><h3>$b</h3><div class=\"links\">
$(cat "$TMP/$b.html")
    </div></div>"
  fi
done
unset IFS

PUB=""
ARC=""
for f in $(ls -1 *.html 2>/dev/null | sort); do
  if [ "$f" = "$OUT" ]; then continue; fi
  case "$f" in
    *.bak.html|*.pre-*|*report*|*audit*|*HANDOFF*|*BRIEF*|*_LOCK*|*battery*|*test*|*snapshot*|*FINEPASS*|*amazed*|*sprint*|*HORIZONS*|*ARCHITECTURE*|*DESIGN_V*|katlyn*)
      ARC="$ARC<a class=\"alink\" href=\"/$f\">$f</a>" ;;
    *)
      PUB="$PUB<a class=\"alink\" href=\"/$f\">$f</a>" ;;
  esac
done

cat > "$OUT" <<HTMLHEAD
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>More · Everything we've built · FieldCheck IQ</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;1,500&family=Cormorant+Garamond:ital,wght@1,500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{--bg:#080706;--gold:#D4A24C;--gold-b:#E4B86A;--cream:#F5F1E8;--muted:rgba(245,241,232,.5);--faint:rgba(245,241,232,.28);--hair:rgba(245,241,232,.07);--line:rgba(212,162,76,.18)}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:radial-gradient(900px 500px at 50% -10%,rgba(212,162,76,.05),transparent 60%),var(--bg);color:var(--cream);font-family:'Playfair Display',Georgia,serif;-webkit-font-smoothing:antialiased}
  nav{display:flex;justify-content:space-between;align-items:center;padding:18px 30px;border-bottom:1px solid var(--hair)}
  nav a.brand{text-decoration:none;color:var(--cream);font-size:18px;font-weight:600}
  nav a.brand .iq{color:var(--gold);font-style:italic;font-size:.55em;vertical-align:.3em;margin-left:.1em}
  nav a.home{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1.6px;text-transform:uppercase;color:var(--muted);text-decoration:none}
  .wrap{max-width:1080px;margin:0 auto;padding:48px 30px 90px}
  .eyebrow{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2.6px;color:var(--gold);text-transform:uppercase}
  h1{font-size:clamp(30px,5vw,46px);font-weight:600;letter-spacing:-.5px;margin-top:12px}
  .lede{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:20px;color:rgba(245,241,232,.78);margin-top:14px;max-width:680px;line-height:1.5}
  .grp{margin-top:42px}
  .grp h3{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2px;color:var(--gold-b);text-transform:uppercase;padding-bottom:12px;border-bottom:1px solid var(--line)}
  .links{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:2px;margin-top:10px}
  .mlink{display:flex;flex-direction:column;text-decoration:none;color:var(--cream);padding:12px 14px;border-radius:9px;transition:background .14s}
  .mlink:hover{background:rgba(212,162,76,.08)}
  .mlink{font-size:16px}
  .mlink span{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.3px;color:var(--faint);margin-top:4px}
  .archive{margin-top:64px;border-top:1px solid var(--hair);padding-top:32px}
  .archive h2{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:24px;font-weight:500}
  .archive p{color:var(--muted);font-size:14px;margin-top:8px;max-width:640px;line-height:1.5}
  .arcgrid{display:flex;flex-wrap:wrap;gap:6px;margin-top:18px}
  .alink{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.3px;color:var(--muted);text-decoration:none;border:1px solid var(--hair);border-radius:7px;padding:7px 10px;transition:.14s}
  .alink:hover{border-color:var(--line);color:var(--gold)}
  .sub{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1.6px;color:var(--faint);text-transform:uppercase;margin:26px 0 10px}
  .foot{padding:30px;text-align:center;color:var(--faint);font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1.4px;text-transform:uppercase;border-top:1px solid var(--hair)}
</style>
</head>
<body>
  <nav><a class="brand" href="/">FieldCheck<span class="iq">IQ</span></a><a class="home" href="/">← Home</a></nav>
  <div class="wrap">
    <div class="eyebrow">The full index</div>
    <h1>Everything we've built</h1>
    <div class="lede">Every page, every feature, every experiment — kept here so nothing is ever lost. Some live on the main path today; the rest wait here until they earn their way back.</div>
$ROUTES_HTML
    <div class="archive">
      <h2>The complete archive</h2>
      <p>A direct link to every page in the system — including the public pages above, plus works-in-progress, prototypes, and internal references. This is the memory: nothing gets deleted, only re-homed when the time is right.</p>
      <div class="sub">Public pages</div>
      <div class="arcgrid">$PUB</div>
      <div class="sub">Internal · WIP · backups</div>
      <div class="arcgrid">$ARC</div>
    </div>
  </div>
  <div class="foot">FieldCheck IQ · ThinkDifferent Holdings · the index of everything</div>
</body>
</html>
HTMLHEAD

echo "built $OUT ($(wc -c < "$OUT") bytes)"
rm -rf "$TMP"

if [ "$MODE" != "all" ]; then
  echo "preview mode -- did not touch _redirects or index.html"
  exit 0
fi

echo "wiring /more route into _redirects"
grep -v '^/more ' _redirects > _redirects.tmp || true
awk 'BEGIN{d=0} /^\/\*/ && d==0 {print "/more                             /fieldcheck-more.html               200"; d=1} {print}' _redirects.tmp > _redirects
rm -f _redirects.tmp
echo "  done"

echo "injecting More link into index.html nav + footer"
python3 - <<'PY'
p="index.html"
s=open(p).read()
if "/more" not in s:
    s=s.replace('<a href="#">Register / Log in</a>',
                '<a href="/more">More</a>\n      <a href="#">Register / Log in</a>',1)
    s=s.replace('<a href="/nba-draft" class="colophon-col-link">NBA Draft call</a>',
                '<a href="/nba-draft" class="colophon-col-link">NBA Draft call</a>\n      <a href="/more" class="colophon-col-link">Explore everything</a>',1)
    open(p,"w").write(s)
    print("  injected")
else:
    print("  already present -- skipped")
PY

echo ""
echo "DONE. Preview locally:  open fieldcheck-more.html"
echo "Then promote with:      bash fc-promote-home.sh"
