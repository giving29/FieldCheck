/* FieldCheck lightweight session (test phase) — no backend.
   Stores who's logged in via localStorage and swaps the nav Register/Log-in
   control to the user's name + a Sign-out menu. Same-origin = shared site-wide. */
(function(){
  var KEY='fc_user_v1';
  function get(){ try{ return JSON.parse(localStorage.getItem(KEY)||'null'); }catch(e){ return null; } }
  function set(u){ try{ localStorage.setItem(KEY, JSON.stringify(u)); }catch(e){} }
  function clear(){ try{ localStorage.removeItem(KEY); }catch(e){} }

  function findAuthEl(){
    var el=document.querySelector('[data-fc-auth]');
    if(el) return el;
    var as=document.querySelectorAll('nav a, header a, a');
    for(var i=0;i<as.length;i++){
      if(/register|log\s?in|sign\s?in/i.test(as[i].textContent||'')) return as[i];
    }
    return null;
  }

  function closeMenu(){ var m=document.getElementById('fc-acct-menu'); if(m) m.remove(); }

  function openMenu(anchor,u){
    closeMenu();
    var r=anchor.getBoundingClientRect();
    var m=document.createElement('div');
    m.id='fc-acct-menu';
    m.style.cssText='position:fixed;z-index:99999;min-width:208px;background:#13100b;border:1px solid rgba(184,152,90,.3);'
      +'border-radius:12px;padding:8px;box-shadow:0 18px 50px rgba(0,0,0,.5);font-family:Inter,system-ui,sans-serif;'
      +'top:'+(r.bottom+8)+'px;left:'+Math.max(12,Math.min(r.left, window.innerWidth-220))+'px';
    var first=(u.name||'Account');
    m.innerHTML=
      '<div style="padding:10px 12px 12px;border-bottom:1px solid rgba(184,152,90,.18);margin-bottom:6px">'
        +'<div style="font-family:Fraunces,Georgia,serif;font-size:16px;font-weight:600;color:#f3eee2">'+esc(first)+'</div>'
        +'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;letter-spacing:1.2px;text-transform:uppercase;color:#9a9486;margin-top:4px">'+esc(u.role||'Member')+(u.email?' \u00b7 '+esc(shortEmail(u.email)):'')+'</div>'
      +'</div>'
      +'<a href="/login" style="display:block;padding:9px 12px;border-radius:8px;color:#cfc9bb;text-decoration:none;font-size:13.5px">Account</a>'
      +'<button id="fc-signout" style="width:100%;text-align:left;background:none;border:0;cursor:pointer;padding:9px 12px;border-radius:8px;color:#e7a17e;font-size:13.5px;font-family:inherit">Sign out</button>';
    document.body.appendChild(m);
    m.querySelector('#fc-signout').onclick=function(){ clear(); closeMenu(); location.reload(); };
    setTimeout(function(){
      document.addEventListener('click',function h(ev){
        if(!m.contains(ev.target) && ev.target!==anchor){ closeMenu(); document.removeEventListener('click',h); }
      });
    },0);
  }

  function shortEmail(e){ return e.length>22 ? e.slice(0,20)+'…' : e; }
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }

  function initNav(){
    var el=findAuthEl(); if(!el) return;
    var u=get();
    if(u && u.name){
      var first=(u.name.split(' ')[0])||'Account';
      el.textContent=first+' \u25BE';
      el.setAttribute('href','#');
      el.style.color='var(--gold-hi, #e8bf70)';
      el.onclick=function(ev){ ev.preventDefault(); if(document.getElementById('fc-acct-menu')){closeMenu();return;} openMenu(el,u); };
    } else {
      el.textContent='Register / Log in';
      el.setAttribute('href','/login');
      el.onclick=null;
    }
  }

  window.FCSession={get:get,set:set,clear:clear,initNav:initNav};
  if(document.readyState!=='loading') initNav();
  else document.addEventListener('DOMContentLoaded',initNav);
})();
