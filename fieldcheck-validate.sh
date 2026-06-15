#!/usr/bin/env bash
# v0.30.5.30: FieldCheck pre-deploy validation
# Run this BEFORE every deploy. If it fails, do not deploy.
#
# Adaptive: works whether your files are named:
#   - fieldcheck.html + fieldcheck-worker.js (pre-rename, Downloads-style)
#   - index.html + worker.js (post-rename, in deploy directory)
#
# Usage: bash fieldcheck-validate.sh

set -e

echo "═══════════════════════════════════════════════════"
echo "  FieldCheck pre-deploy validation"
echo "═══════════════════════════════════════════════════"
echo ""

# 1. Detect which naming convention we have
HTML_FILE=""
WORKER_FILE=""
if [ -f "fieldcheck.html" ]; then HTML_FILE="fieldcheck.html"
elif [ -f "index.html" ]; then HTML_FILE="index.html"
fi
if [ -f "fieldcheck-worker.js" ]; then WORKER_FILE="fieldcheck-worker.js"
elif [ -f "worker.js" ]; then WORKER_FILE="worker.js"
fi

if [ -z "$HTML_FILE" ]; then
  echo "✗ Neither fieldcheck.html nor index.html found in current directory"
  echo "  cd to the directory containing your build files first"
  exit 1
fi
if [ -z "$WORKER_FILE" ]; then
  echo "✗ Neither fieldcheck-worker.js nor worker.js found in current directory"
  exit 1
fi
echo "✓ Files found: $HTML_FILE + $WORKER_FILE"

# 2. Worker syntax
node --check "$WORKER_FILE"
echo "✓ Worker syntax clean"

# 3. Inline HTML JS syntax — extracts every <script> block and node-checks it
python3 - "$HTML_FILE" << 'PYEOF'
import re, sys
html_file = sys.argv[1]
with open(html_file, 'r') as f:
    html = f.read()
blocks = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
combined = '\n// === BOUNDARY ===\n'.join(blocks)
with open('/tmp/fieldcheck-inline-validate.js', 'w') as f:
    f.write(combined)
PYEOF
node --check /tmp/fieldcheck-inline-validate.js
echo "✓ Inline HTML JS syntax clean"

# 4. Critical click-handler smoke check
python3 - "$HTML_FILE" << 'PYEOF'
import re, sys
html_file = sys.argv[1]
with open(html_file, 'r') as f:
    html = f.read()

onclick_funcs = set(re.findall(r'onclick="([a-zA-Z_$][a-zA-Z0-9_$]*)\(', html))
defined_funcs = set()
defined_funcs.update(re.findall(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', html))
defined_funcs.update(re.findall(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:function|\([^)]*\)\s*=>|[^=])', html))
defined_funcs.update(re.findall(r'window\.([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=', html))

builtins = {'alert', 'confirm', 'prompt', 'console', 'window', 'document', 'event', 'parseInt', 'parseFloat',
            'this', 'setTimeout', 'setInterval', 'fetch', 'JSON', 'Array', 'Object', 'String', 'Number',
            'if', 'else', 'return', 'true', 'false', 'null', 'undefined', 'void', 'typeof', 'new', 'await'}

undefined = onclick_funcs - defined_funcs - builtins
if undefined:
    print(f"✗ {len(undefined)} click handler(s) reference undefined functions: {undefined}")
    sys.exit(1)
else:
    print(f"✓ All {len(onclick_funcs)} onclick handlers reference defined functions")
PYEOF

# 5. Critical handler presence
for fn in selectTrack goHome runPlayerVerdict runProgramVerdict; do
    if ! grep -q "function $fn" "$HTML_FILE"; then
        echo "✗ critical function $fn() is missing from $HTML_FILE"
        exit 1
    fi
done
echo "✓ Critical click handlers (selectTrack, goHome, runPlayerVerdict, runProgramVerdict) all present"

# 6. Build version string match
HTML_VER=$(grep -oE "v[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+_[A-Z_]+" "$HTML_FILE" | head -1)
WORKER_VER=$(grep -oE "v[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+_[A-Z_]+" "$WORKER_FILE" | head -1)
if [ "$HTML_VER" != "$WORKER_VER" ]; then
    echo "✗ Version mismatch:"
    echo "  HTML:   $HTML_VER"
    echo "  Worker: $WORKER_VER"
    exit 1
fi
echo "✓ HTML and worker version match: $HTML_VER"

# 7. v0.30.5.60: Dead-element selector check. Catches the bug class where JS
# calls .style/.classList/.value on a querySelector or getElementById that
# returns null because the element was removed from HTML. This is what broke
# v58: selectTrack() called document.querySelector('.tracks').style.display
# but the Tracks section had been deleted. Every click threw TypeError.
python3 - "$HTML_FILE" << 'PYEOF'
import re, sys
with open(sys.argv[1]) as f:
    html = f.read()

# Find chained calls on querySelector/getElementById results — these are the
# dangerous ones. .style.x, .classList.x, .value, .innerHTML, .textContent,
# .checked, .disabled all throw if the lookup returned null.
DANGEROUS = re.compile(
    r"""document\.(querySelector|getElementById)\(\s*['"]([^'"]+)['"]\s*\)\.(style|classList|value|innerHTML|textContent|checked|disabled|focus|click|src|href|appendChild|remove)""",
    re.MULTILINE
)

issues = []
for m in DANGEROUS.finditer(html):
    method = m.group(1)
    selector = m.group(2)
    line_no = html[:m.start()].count('\n') + 1
    # Check if the element exists in HTML
    if method == 'getElementById':
        # id="foo" or id='foo'
        if not re.search(r'''id=['"]''' + re.escape(selector) + r'''['"]''', html):
            issues.append((line_no, method, selector))
    else:  # querySelector
        # Handle class .foo or id #foo or tag foo
        if selector.startswith('.'):
            cls = selector[1:].split()[0]  # first class in compound selector
            if not re.search(r'''class=['"][^'"]*\b''' + re.escape(cls) + r'''\b''', html):
                issues.append((line_no, method, selector))
        elif selector.startswith('#'):
            sid = selector[1:].split()[0]
            if not re.search(r'''id=['"]''' + re.escape(sid) + r'''['"]''', html):
                issues.append((line_no, method, selector))
        # tag-based selectors we skip — too noisy

if issues:
    print(f"✗ {len(issues)} unguarded DOM reference(s) to missing elements:")
    for ln, method, sel in issues:
        print(f"    line {ln}: document.{method}('{sel}').<...> — element not found in HTML")
    print()
    print("  Add a null guard: const el = document.{method}('{sel}'); if (el) el.style/...")
    sys.exit(1)
else:
    print(f"✓ DOM selector audit: every chained query lookup resolves to a real element")
PYEOF

echo ""
echo "═══════════════════════════════════════════════════"
echo "  ALL CHECKS PASSED — safe to deploy"
echo "═══════════════════════════════════════════════════"
