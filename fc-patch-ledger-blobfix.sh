#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"; F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if grep -q "fc-ledger-blobfix" "$F"; then echo "Already blob-fixed. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.blobfix.$(date +%Y%m%d_%H%M)"; echo "backed up $F"
python3 - <<'PYEOF'
f="fieldcheck-verdict.html"; s=open(f).read()
block='''<style id="fc-ledger-blobfix">
/* kill over-greedy .verified/.pending pill rules that blob out section/row containers */
[data-vtab="evalgrid"] .verified,[data-vtab="evalgrid"] .pending,
.eg-subpanel .verified,.eg-subpanel .pending,
.ledger-section.verified,.ledger-section.pending,
.ledger-row.verified,.ledger-row.pending{
  background:transparent !important;border:0 !important;border-radius:0 !important;
  box-shadow:none !important;display:block !important;padding:0 !important;
  font:inherit !important;color:inherit !important
}
.ledger-section.verified,.ledger-section.pending{padding-left:40px !important}
</style>
</head>'''
assert s.count("</head>")>=1
s=s.replace("</head>",block,1)
open(f,"w").write(s); print("blob fix applied: .verified/.pending pill styling stripped from ledger containers")
PYEOF
echo ""; echo "Ship to DEV:  bash fc-dev.sh"
