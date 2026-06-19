#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }

if grep -q "function egPruneEmpty" "$F"; then
  echo "Already patched. Nothing to do."
  exit 0
fi

cp "$F" "$F.bak.$(date +%Y%m%d_%H%M)"
echo "backed up $F"

python3 - <<'PY'
f="fieldcheck-verdict.html"
s=open(f).read()
def repl(old,new,why):
    global s
    assert s.count(old)>=1, "ANCHOR MISSING: "+why
    s=s.replace(old,new,1)
    print("ok:",why)

# 1) disable trust-by-numbers strip mount
repl("if (window.FC17_TRUST) {","if (false /* trust strip removed */ && window.FC17_TRUST) {","trust strip mount off")
# 2) remove the trust strip anchor div
repl("""  h+='<div id="fc17-trust-anchor-verdict" style="margin: 40px auto 0; max-width: 1100px;"></div>';""","""  /* trust strip anchor removed */""","trust anchor div removed")
# 3) disable the V5 audit trail panel (script self-aborts when mount id is absent)
repl('<div id="fc-v5-audit-mount"','<div id="fc-v5-audit-mount-off"',"audit trail panel off")

# 4) insert egPruneEmpty before egInitSubtabs + call it first
prune = r'''function egPruneEmpty(){
  // Hide eval-grid nav tabs whose panel has no real content (data-light athletes)
  var items=document.querySelectorAll('.eg-toc-item');
  for(var i=0;i<items.length;i++){
    var it=items[i];
    var href=(it.getAttribute('href')||'').replace(/^#/,'');
    if(!href)continue;
    var panel=document.querySelector('.eg-subpanel[data-subtab="'+href+'"]');
    var empty=!panel || (panel.textContent||'').replace(/\s+/g,'').length < 24;
    if(empty){ it.style.display='none'; if(panel)panel.setAttribute('data-empty','1'); }
    else { it.style.display=''; }
  }
}
function egInitSubtabs(){
  egPruneEmpty();'''
repl("function egInitSubtabs(){",prune,"egPruneEmpty + call")

# 5) deep-link target must not be an empty panel
repl("if(match)target=hash;","if(match && match.getAttribute('data-empty')!=='1')target=hash;","deep-link skips empty")

# 6) default selection = first NON-empty panel (egInitSubtabs)
repl("""    var first=document.querySelector('.eg-subpanel');
    if(first)target=first.getAttribute('data-subtab');""",
"""    var first=document.querySelector('.eg-subpanel:not([data-empty=\"1\"])')||document.querySelector('.eg-subpanel');
    if(first)target=first.getAttribute('data-subtab');""","default to first non-empty")

# 7) activate fallback = first NON-empty (egActivateSubtab)
repl("""  if(!matched){
    var first=document.querySelector('.eg-subpanel');""",
"""  if(!matched){
    var first=document.querySelector('.eg-subpanel:not([data-empty=\"1\"])')||document.querySelector('.eg-subpanel');""","activate fallback non-empty")

open(f,"w").write(s)
print("DONE writing", f)
PY

echo ""
echo "Ship to DEV:  bash fc-dev.sh"
