#!/usr/bin/env python3
"""FCBase58 inline patcher . worker observability + methodology agent UI"""
import gzip, base64, os, subprocess, sys, tempfile

WORKER_B64 = """
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
"""

METHODOLOGY_B64 = """
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
WOf/AHzpzVrVNwAA
"""

def check_files():
    home = os.path.expanduser('~/Downloads')
    w = os.path.join(home, 'worker.js')
    m = os.path.join(home, 'fieldcheck-methodology.html')
    if not os.path.exists(w):
        print(f'FAIL: {w} not found'); sys.exit(1)
    if not os.path.exists(m):
        print(f'FAIL: {m} not found in ~/Downloads/')
        print(f'Note: copy from project if not in Downloads:')
        print(f'  cp ~/Desktop/fieldcheck-proxy/frontend/fieldcheck-methodology.html ~/Downloads/')
        sys.exit(1)
    print(f'  Before: worker.js {os.path.getsize(w)} bytes, methodology.html {os.path.getsize(m)} bytes')

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
            print(f'FAIL: {label} returned {result.returncode}'); sys.exit(1)
    finally:
        os.unlink(tmp)

def verify():
    home = os.path.expanduser('~/Downloads')
    w = open(os.path.join(home, 'worker.js')).read()
    m = open(os.path.join(home, 'fieldcheck-methodology.html')).read()
    checks = [
        ('worker /agent/stats route', "path === '/agent/stats'" in w),
        ('worker buildMethodologySystemPrompt', 'buildMethodologySystemPrompt' in w),
        ('worker handleAgentStats', 'async function handleAgentStats' in w),
        ('worker FCBase58 marker', 'FCBase58' in w),
        ('methodology fc-agent-pill', m.count('fc-agent-pill') >= 5),
        ('methodology mode=methodology', "mode: 'methodology'" in m),
    ]
    print()
    for name, ok in checks:
        print(f'  {("OK" if ok else "FAIL"):<6} {name}')
    if not all(ok for _, ok in checks):
        sys.exit(1)

print('=== FCBase58 inline patcher ===')
check_files()
apply('Worker patch', WORKER_B64)
apply('Methodology patch', METHODOLOGY_B64)
verify()
print('\n=== Done. Now run: cd ~/Desktop/fieldcheck-proxy && ./fc-ship-FCBase58.sh ===')
