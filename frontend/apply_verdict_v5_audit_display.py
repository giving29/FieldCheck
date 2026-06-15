#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
VERDICT PAGE · V5 AUDIT TRAIL UI INTEGRATION
═══════════════════════════════════════════════════════════════════════════
Sprint B1 · V022.36-V5.2 · the moat-revealing transparency feature.

Adds three things to fieldcheck-verdict.html:
  1. <script src="/fc17-v5-audit-panel.js"></script>  in <head>
  2. <div id="fc-v5-audit-mount"></div>  in verdict body (after polygon)
  3. Integration hook that calls FCv5Audit.render(response) after verdict fetch

Per Canonical Doctrine: surgical str_replace anchored on actual file content.
If verdict file structure has changed, patch will report which anchor missed
and exit cleanly. Idempotent — skips if already applied.

REQUIREMENTS:
  - fieldcheck-verdict.html in current directory (~/Desktop/fieldcheck-proxy/)
  - fc17-v5-audit-panel.js in current directory (will be copied to deploy)
  - Run AFTER V022.36-V5.2 worker is deployed to dev

═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, re
from pathlib import Path

print("═══ VERDICT PAGE · V5 AUDIT TRAIL INTEGRATION ═══\n")

VERDICT = Path('fieldcheck-verdict.html')
JS_MODULE = Path('fc17-v5-audit-panel.js')

if not VERDICT.exists():
    print(f"✗ FAIL: {VERDICT} not found in cwd")
    print("  Expected to run from ~/Desktop/fieldcheck-proxy/")
    sys.exit(1)

if not JS_MODULE.exists():
    print(f"✗ FAIL: {JS_MODULE} not found in cwd")
    print(f"  Upload fc17-v5-audit-panel.js to ~/Desktop/fieldcheck-proxy/ first")
    sys.exit(1)

c = VERDICT.read_text()
orig_bytes = VERDICT.stat().st_size
print(f"▸ {VERDICT} · {orig_bytes:,} bytes")
print(f"▸ {JS_MODULE} · {JS_MODULE.stat().st_size:,} bytes\n")


# ══════════════════════════════════════════════════════════════════════════
# Idempotency check
# ══════════════════════════════════════════════════════════════════════════
if 'fc17-v5-audit-panel.js' in c or 'fc-v5-audit-mount' in c or 'FCv5Audit' in c:
    print("✓ V5 audit panel integration already present (idempotent)")
    sys.exit(0)


# ══════════════════════════════════════════════════════════════════════════
# Backup
# ══════════════════════════════════════════════════════════════════════════
backup = VERDICT.with_suffix('.html.pre-v5-audit-panel.bak')
shutil.copy(VERDICT, backup)
print(f"▸ Backup: {backup}\n")


# ══════════════════════════════════════════════════════════════════════════
# PATCH 1 · Insert script tag in <head>
# ══════════════════════════════════════════════════════════════════════════
print("▸ PATCH 1 · script tag in <head>")

script_tag = '<script src="/fc17-v5-audit-panel.js" defer></script>'

# Try multiple anchor strategies
head_anchors = [
    ('</head>', '  ' + script_tag + '\n</head>'),
]

p1_applied = False
for old_pat, new_pat in head_anchors:
    if old_pat in c:
        c = c.replace(old_pat, new_pat, 1)
        p1_applied = True
        print(f"  ✓ inserted before </head>")
        break

if not p1_applied:
    print("  ✗ FAIL: no </head> anchor found in verdict page")
    print(f"  Restore: cp {backup} {VERDICT}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# PATCH 2 · Insert mount div + integration script
# ══════════════════════════════════════════════════════════════════════════
print("\n▸ PATCH 2 · mount div + integration hook")

mount_block = '''
  <!-- V5 Audit Trail Panel · Sprint B1 · V022.36-V5.2 -->
  <div id="fc-v5-audit-mount" style="max-width: 880px; margin: 24px auto; padding: 0 16px;"></div>
  <script>
    // V5 Audit · render after verdict response arrives
    // This hook tries multiple known integration points:
    //   1. Listens for fc-verdict-rendered custom event
    //   2. Polls window.lastVerdictResponse / window.verdictResponse / window.lastVerdict
    //   3. Hooks fetch() to intercept /verdict/player responses
    (function() {
      const target = document.getElementById('fc-v5-audit-mount');
      if (!target) return;

      function tryRender(response) {
        if (window.FCv5Audit && response) {
          window.FCv5Audit.render(response, target);
        }
      }

      // Strategy 1: listen for explicit event
      document.addEventListener('fc-verdict-rendered', function(ev) {
        if (ev.detail && ev.detail.response) tryRender(ev.detail.response);
      });

      // Strategy 2: poll for global state (with timeout)
      let attempts = 0;
      const pollInterval = setInterval(function() {
        attempts++;
        const candidates = [
          window.lastVerdictResponse,
          window.verdictResponse,
          window.lastVerdict,
          window.__fcVerdict,
          window.fcVerdictData
        ];
        for (let i = 0; i < candidates.length; i++) {
          if (candidates[i] && candidates[i].composite_v022_31) {
            tryRender(candidates[i]);
            clearInterval(pollInterval);
            return;
          }
        }
        if (attempts > 60) clearInterval(pollInterval); // give up after 30s
      }, 500);

      // Strategy 3: monkey-patch fetch to intercept /verdict/player
      const origFetch = window.fetch;
      window.fetch = function() {
        const result = origFetch.apply(this, arguments);
        const url = (arguments[0] && (arguments[0].url || arguments[0])) || '';
        if (typeof url === 'string' && url.indexOf('/verdict/player') !== -1) {
          result.then(function(r) {
            return r.clone().json().then(function(data) {
              if (data && data.composite_v022_31) {
                tryRender(data);
              }
            }).catch(function() {});
          }).catch(function() {});
        }
        return result;
      };
    })();
  </script>
'''

# Insert before </body>
if '</body>' in c:
    c = c.replace('</body>', mount_block + '\n</body>', 1)
    print(f"  ✓ inserted mount div + integration hook before </body>")
else:
    print("  ✗ FAIL: no </body> anchor found")
    print(f"  Restore: cp {backup} {VERDICT}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════════
VERDICT.write_text(c)
new_bytes = VERDICT.stat().st_size
delta = new_bytes - orig_bytes
print(f"\n▸ {VERDICT} · {new_bytes:,} bytes (delta +{delta:,})\n")


# ══════════════════════════════════════════════════════════════════════════
# VERIFY
# ══════════════════════════════════════════════════════════════════════════
print("▸ Post-patch verification\n")
checks = [
    ('script tag fc17-v5-audit-panel.js', 'fc17-v5-audit-panel.js' in c),
    ('mount div id', 'id="fc-v5-audit-mount"' in c),
    ('FCv5Audit reference', 'FCv5Audit' in c),
    ('integration hook present', 'tryRender(response)' in c or 'tryRender(' in c),
    ('fetch monkey-patch', 'origFetch.apply' in c),
]
ok = True
for label, found in checks:
    print(f"  {'✓' if found else '✗'} {label}")
    if not found:
        ok = False

if not ok:
    print(f"\n✗ POST-PATCH VERIFICATION FAILED")
    print(f"  Restore: cp {backup} {VERDICT}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════
print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" VERDICT PAGE V5 AUDIT INTEGRATION APPLIED")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" {VERDICT} · {orig_bytes:,} → {new_bytes:,} bytes (+{delta:,})")
print(f" backup: {backup}")
print(f"")
print(f" Inserted:")
print(f"   ✓ <script src='/fc17-v5-audit-panel.js' defer> in <head>")
print(f"   ✓ <div id='fc-v5-audit-mount'> before </body>")
print(f"   ✓ Multi-strategy integration hook (event/poll/fetch-intercept)")
print(f"")
print(f" The integration is defensive — uses 3 strategies to find the verdict response:")
print(f"   1. Listens for 'fc-verdict-rendered' custom event")
print(f"   2. Polls window.lastVerdictResponse and 4 other common globals")
print(f"   3. Monkey-patches fetch() to intercept /verdict/player responses")
print(f"")
print(f" NEXT:")
print(f"   1. ./fc-deploy-dev.sh")
print(f"   2. Visit a verdict page on DEV, e.g.:")
print(f"      https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens_basketball")
print(f"   3. Verify audit panel appears with raw → corrections → final flow")
print(f"   4. Test on: Tim Duncan (no corrections), Cooper Flagg (R4), Jordan Smith Jr (R1+R2), Tate Ivanyo (R4+R6 flag)")
print(f"   5. If clean: ./fc-promote-prod.sh")
print(f"")
print(f" KNOWN LIMITS:")
print(f"   • fetch interception may double-fire on retries — render is idempotent so safe")
print(f"   • If verdict page uses XHR instead of fetch, hook may miss. Use Strategy 1 (event) instead.")
print(f"   • Audit panel positioning is below the polygon by default. Adjust margin if needed.")
