#!/usr/bin/env python3
"""FCBase59 PAGES-ONLY recovery patcher (worker patch already succeeded)"""
import gzip, base64, os, subprocess, sys, tempfile

PAGES_B64 = """
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
"""

def check_files():
    home = os.path.expanduser('~/Downloads')
    files = ['fieldcheck-predictions.html', 'fieldcheck-coverage.html', 'fieldcheck-versus.html']
    missing = [f for f in files if not os.path.exists(os.path.join(home, f))]
    if missing:
        print('FAIL: missing files in ~/Downloads/: ' + ', '.join(missing))
        sys.exit(1)
    print('  Page files in ~/Downloads/:')
    for f in files:
        sz = os.path.getsize(os.path.join(home, f))
        already = sz > 20000  # patched is >25k, original is <19k
        print(f'    {f}: {sz} bytes' + (' (already patched, will skip)' if already else ''))

def apply(label, b64):
    print(f'\n>>> {label}')
    code = gzip.decompress(base64.b64decode(b64.strip())).decode()
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
        f.write(code); tmp = f.name
    try:
        result = subprocess.run([sys.executable, tmp], capture_output=True, text=True)
        if result.stdout: print(result.stdout, end='')
        if result.stderr: print(result.stderr, end='', file=sys.stderr)
        if result.returncode != 0:
            print(f'FAIL: {label} returned {result.returncode}')
            sys.exit(1)
    finally:
        os.unlink(tmp)

def verify():
    home = os.path.expanduser('~/Downloads')
    p = open(os.path.join(home, 'fieldcheck-predictions.html')).read()
    c = open(os.path.join(home, 'fieldcheck-coverage.html')).read()
    v = open(os.path.join(home, 'fieldcheck-versus.html')).read()
    checks = [
        ('predictions agent pill', p.count('fc-agent-pill') >= 5),
        ("predictions mode='predictions'", "'predictions'" in p),
        ('coverage agent pill', c.count('fc-agent-pill') >= 5),
        ("coverage mode='coverage'", "'coverage'" in c),
        ('versus agent pill', v.count('fc-agent-pill') >= 5),
        ("versus mode='comparison'", "'comparison'" in v),
    ]
    print()
    for name, ok in checks:
        print(f'  {("OK" if ok else "FAIL"):<6} {name}')
    if not all(ok for _, ok in checks):
        sys.exit(1)

print('=== FCBase59 PAGES-ONLY recovery patcher ===')
print('(Worker patch already succeeded earlier - skipping)')
check_files()
apply('Pages patch (predictions + coverage + versus)', PAGES_B64)
verify()
print('\n=== Done. Now run: cd ~/Desktop/fieldcheck-proxy && ./fc-ship-FCBase59.sh ===')
