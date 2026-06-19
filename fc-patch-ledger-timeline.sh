#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if grep -q "fc-evalgrid-ledger-timeline" "$F"; then echo "Already done. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.ledgertl.$(date +%Y%m%d_%H%M)"
echo "backed up $F"
python3 - <<'PY'
f="fieldcheck-verdict.html"; s=open(f).read()
# 1) hook: tag the live verified row with a .live class
old='<div class="ledger-row verified"><div class="ledger-icon">'
new='<div class="ledger-row verified\'+(v.live?\' live\':\'\')+\'"><div class="ledger-icon">'
assert s.count(old)==1, "ledger live-row anchor not unique/found"
s=s.replace(old,new,1)
# 2) timeline CSS transform
block=r"""<style id="fc-evalgrid-ledger-timeline">
/* OUTCOME LEDGER -> signed verdict timeline (scoped, additive) */
.eg-subpanel .ledgerbox{color:var(--t2)}
.eg-subpanel .ledger-stats{display:flex;gap:12px;flex-wrap:wrap;margin:6px 0 36px}
.eg-subpanel .ledger-stat{flex:1;min-width:150px;position:relative;overflow:hidden;background:linear-gradient(155deg,rgba(28,26,38,.7),rgba(15,14,19,.4));border:1px solid var(--ge2);border-radius:16px;padding:18px}
.eg-subpanel .ledger-stat::after{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--moss)}
.eg-subpanel .ledger-stat.pending::after{background:var(--t4)}
.eg-subpanel .ledger-stat:not(.verified):not(.pending)::after{background:var(--gold)}
.eg-subpanel .ledger-stat-num{font-family:"Anton",sans-serif;font-size:42px;line-height:1;color:rgba(245,241,232,.96)}
.eg-subpanel .ledger-stat.verified .ledger-stat-num{color:var(--moss)}
.eg-subpanel .ledger-stat-lbl{font-family:"JetBrains Mono",monospace;font-size:10px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--t3);margin-top:6px}
.eg-subpanel .ledger-section-h{font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--t3);margin:8px 0 22px}
.eg-subpanel .ledger-section{position:relative;padding-left:40px;margin-bottom:10px}
.eg-subpanel .ledger-section::before{content:"";position:absolute;left:13px;top:34px;bottom:18px;width:2px;background:var(--moss)}
.eg-subpanel .ledger-section.pending::before{background:var(--gold);opacity:.55}
.eg-subpanel .ledger-row{position:relative;display:block;margin-bottom:20px;padding:0}
.eg-subpanel .ledger-icon{position:absolute;left:-33px;top:2px;width:16px;height:16px;border-radius:50%;background:var(--bg1,#0F0E13);border:2px solid var(--moss);box-shadow:0 0 0 4px var(--bg,#07060A);font-size:0;z-index:2}
.eg-subpanel .ledger-section.pending .ledger-icon{border-color:var(--gold);border-style:dashed;background:transparent}
.eg-subpanel .ledger-row.live .ledger-icon{border-color:var(--gold);box-shadow:0 0 0 4px var(--bg,#07060A),0 0 16px rgba(212,162,76,.6)}
.eg-subpanel .ledger-section.pending .ledger-row:last-child .ledger-icon{width:20px;height:20px;left:-35px;border-style:solid;background:radial-gradient(circle,rgba(212,162,76,.35),transparent 70%);box-shadow:0 0 0 4px var(--bg,#07060A),0 0 22px rgba(212,162,76,.7)}
.eg-subpanel .ledger-body{background:linear-gradient(155deg,rgba(28,26,38,.55),rgba(15,14,19,.32));border:1px solid var(--ge2);border-radius:14px;padding:14px 16px}
.eg-subpanel .ledger-row.live .ledger-body{border-color:var(--goldl);background:linear-gradient(155deg,rgba(212,162,76,.10),rgba(15,14,19,.4))}
.eg-subpanel .ledger-section.pending .ledger-row:last-child .ledger-body{border-color:rgba(212,162,76,.45);background:linear-gradient(155deg,rgba(212,162,76,.14),rgba(15,14,19,.45))}
.eg-subpanel .ledger-date{font-family:"JetBrains Mono",monospace;font-size:10.5px;font-weight:700;letter-spacing:.5px;color:var(--gold);margin-bottom:5px}
.eg-subpanel .ledger-event{font-family:"Big Shoulders Display",sans-serif;font-weight:700;font-size:17px;line-height:1.2;color:rgba(245,241,232,.96);margin-bottom:9px}
.eg-subpanel .ledger-call{display:block;padding-top:9px;border-top:1px solid var(--ge2);color:var(--t2);font-size:12.5px;line-height:1.55}
.eg-subpanel .ledger-call strong{display:inline-block;font-family:"JetBrains Mono",monospace;font-size:8.5px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:var(--moss);background:rgba(107,170,90,.12);border:1px solid rgba(107,170,90,.3);border-radius:6px;padding:3px 7px;margin:0 8px 4px 0;vertical-align:middle}
.eg-subpanel .ledger-section.pending .ledger-call strong,.eg-subpanel .ledger-row.live .ledger-call strong{color:var(--gold);background:rgba(212,162,76,.10);border-color:var(--goldl)}
</style>
</head>"""
assert s.count("</head>")>=1
s=s.replace("</head>",block,1)
open(f,"w").write(s); print("ledger: live-row hook + timeline CSS installed")
PY
# validate the ledger script block parses
python3 - <<'PY'
import re
s=open('fieldcheck-verdict.html').read()
for m in re.finditer(r'<script>(.*?)</script>', s, re.S):
    if 'OUTCOME_LEDGER' in m.group(1): open('/tmp/lg.js','w').write(m.group(1)); break
PY
node --check /tmp/lg.js && echo "ledger JS OK"
echo "Ship to DEV:  bash fc-dev.sh"
