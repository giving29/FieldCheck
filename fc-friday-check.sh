PASS=0; FAIL=0
ok(){ PASS=$((PASS+1)); echo "  PASS  $1"; }
bad(){ FAIL=$((FAIL+1)); echo "  FAIL  $1"; }
B="https://fieldcheck-app.netlify.app"
W="https://fieldcheck-proxy.sridhar-nallani.workers.dev"
CB="cb=$(date +%s)"

echo "===== FIELDCHECK FRIDAY CHECK · $(date) ====="
echo ""
echo "--- routes alive ---"
for U in / /deck /gap /path /dream /receipts /methodology /predictions /coverage /versus /watchlist /whats-new /outcomes /agent-transparency /coaches /gems /nba-draft /sports/mens-basketball /sports/womens-volleyball /fieldcheck-roster-110; do
  S=$(curl -s -o /dev/null -w "%{http_code}" "$B$U?$CB")
  [ "$S" = "200" ] && ok "$U" || bad "$U ($S)"
done

echo ""
echo "--- feature markers ---"
curl -s "$B/deck?$CB" | grep -q "We are the verdict" && ok "deck: articulation + layer table" || bad "deck: GAP arsenal missing"
curl -s "$B/gap?$CB" | grep -q "Live demo: THE PATH" && ok "gap: demo buttons" || bad "gap: demo buttons missing"
curl -s "$B/receipts?$CB" | grep -q "THE PATH" && ok "receipts: PATH link" || bad "receipts: PATH link missing"
curl -s "$B/dream?$CB" | grep -q "GPS" && ok "dream: live" || bad "dream: missing"
V=$(curl -s "$B/fieldcheck-verdict.html?$CB")
echo "$V" | grep -q "fc-path-mount" && ok "verdict: THE PATH" || bad "verdict: PATH missing"
echo "$V" | grep -q "fcp-share" && ok "verdict: share card" || bad "verdict: share card missing"
echo "$V" | grep -q "FCBase80" && ok "verdict: FCBase80 polish" || bad "verdict: FCBase80 missing"
V2=$(curl -s "$B/verdict?$CB")
echo "$V2" | grep -q "FCBase80" && ok "verdict route (clean name): synced" || bad "verdict route: STALE duplicate"
for P in methodology predictions coverage; do
  N=$(curl -s "$B/$P?$CB" | grep -o agent | wc -l | tr -d ' ')
  [ "$N" -ge 50 ] && ok "/$P: agent present ($N)" || bad "/$P: agent weak ($N)"
done

echo ""
echo "--- worker + photos ---"
curl -s -o /dev/null -w "%{http_code}" "$W/agent/stats" | grep -q 200 && ok "agent stats" || bad "agent stats"
for P in "Cooper+Flagg|mens-basketball" "Caitlin+Clark|womens-basketball" "Avery+Skinner|womens-volleyball" "AJ+Dybantsa|mens-basketball"; do
  Q="${P%%|*}"; SP="${P##*|}"
  S=$(curl -s -o /dev/null -w "%{http_code}" "$W/photo?q=$Q&sport=$SP")
  [ "$S" = "200" ] && ok "photo $Q" || bad "photo $Q ($S)"
done

echo ""
echo "===== RESULT: $PASS pass / $FAIL fail ====="
[ "$FAIL" -eq 0 ] && echo "ALL GREEN - demo ready" || echo "FIX BEFORE FRIDAY"
