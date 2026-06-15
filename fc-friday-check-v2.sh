PASS=0; FAIL=0
ok(){ PASS=$((PASS+1)); echo "  PASS  $1"; }
bad(){ FAIL=$((FAIL+1)); echo "  FAIL  $1"; }
B="https://fieldcheck-app.netlify.app"
W="https://fieldcheck-proxy.sridhar-nallani.workers.dev"
CB="cb=$(date +%s)"
echo "===== FIELDCHECK CHECK v2 . $(date) ====="
echo "--- routes ---"
for U in / /deck /gap /path /dream /receipts /draft-board /methodology /predictions /coverage /versus /watchlist /whats-new /outcomes /agent-transparency /coaches /gems /movement; do
  S=$(curl -s -o /dev/null -w "%{http_code}" "$B$U?$CB")
  [ "$S" = "200" ] && ok "$U" || bad "$U ($S)"
done
echo "--- features ---"
curl -s "$B/deck?$CB" | grep -q "ACCOUNTABILITY CLOCK" && ok "deck clock" || bad "deck clock"
curl -s "$B/thesis?$CB" | grep -q "JUNE 2026 REFRESH" && ok "thesis refresh" || bad "thesis refresh"
curl -s "$B/gap?$CB" | grep -q "Live demo: THE PATH" && ok "gap buttons" || bad "gap buttons"
curl -s "$B/draft-board?$CB" | grep -q "efb0edd7" && ok "draft board SHA" || bad "draft board SHA"
curl -s "$B/draft-board?$CB" | grep -q 'class="cur"' && ok "draft board current wiring" || bad "draft board current wiring"
curl -s "$B/predictions?$CB" | grep -q "HORIZON LADDER" && ok "predictions horizons" || bad "predictions horizons"
curl -s "$B/outcomes?$CB" | grep -q "LIVE SCOREBOARD" && ok "outcomes scoreboard" || bad "outcomes scoreboard"
curl -s "$B/movement?$CB" | grep -q "Movement Wire" && ok "movement wire page" || bad "movement wire page"
V=$(curl -s "$B/fieldcheck-verdict.html?$CB")
echo "$V" | grep -q "fc-path-mount" && ok "verdict PATH" || bad "verdict PATH"
echo "$V" | grep -q "fcp-share" && ok "share card" || bad "share card"
echo "$V" | grep -q "FCBase83" && ok "marquee fallback" || bad "marquee fallback"
echo "$V" | grep -q "FCBase85" && ok "movement banner" || bad "movement banner"
curl -s "$B/verdict?$CB" | grep -q "fc-path-mount" && ok "clean-name sync" || bad "clean-name STALE"
for P in methodology predictions coverage; do
  N=$(curl -s "$B/$P?$CB" | grep -o agent | wc -l | tr -d ' ')
  [ "$N" -ge 50 ] && ok "/$P agent ($N)" || bad "/$P agent ($N)"
done
echo "--- worker ---"
curl -s -o /dev/null -w "%{http_code}" "$W/agent/stats" | grep -q 200 && ok "agent stats" || bad "agent stats"
curl -s "$W/movement/feed" | grep -q '"count":6' && ok "movement feed (6 events)" || bad "movement feed"
S=$(curl -s -o /dev/null -w "%{http_code}" "$W/photo?q=Carlos+Medlock+Jr&sport=mens-basketball&cb=$(date +%s)")
[ "$S" = "404" ] && ok "Medlock photo blocked" || bad "Medlock photo NOT blocked ($S)"
for P in "Cooper+Flagg mens-basketball" "Caitlin+Clark womens-basketball" "Avery+Skinner womens-volleyball"; do
  Q=$(echo $P | cut -d' ' -f1); SP=$(echo $P | cut -d' ' -f2)
  S=$(curl -s -o /dev/null -w "%{http_code}" "$W/photo?q=$Q&sport=$SP")
  [ "$S" = "200" ] && ok "photo $Q" || bad "photo $Q ($S)"
done
echo ""
echo "===== RESULT: $PASS pass / $FAIL fail ====="
