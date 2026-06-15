#!/usr/bin/env python3
"""FCBase61 inline patcher . agent on 5 sport landings"""
import gzip, base64, os, subprocess, sys, tempfile

WORKER_B64 = """
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
"""

PAGES_B64 = """
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
"""

def check_files():
    home = os.path.expanduser('~/Downloads')
    files = ['worker.js',
             'fieldcheck-sport-mens-basketball.html',
             'fieldcheck-sport-football.html',
             'fieldcheck-sport-womens-basketball.html',
             'fieldcheck-sport-womens-volleyball.html',
             'fieldcheck-sport-baseball.html']
    missing = [f for f in files if not os.path.exists(os.path.join(home, f))]
    if missing:
        print('FAIL: missing files in ~/Downloads/: ' + ', '.join(missing))
        print('  Copy from project:')
        for f in missing:
            if f == 'worker.js':
                print(f'    cp ~/Desktop/fieldcheck-proxy/{f} ~/Downloads/')
            else:
                print(f'    cp ~/Desktop/fieldcheck-proxy/frontend/{f} ~/Downloads/')
        sys.exit(1)
    print('  Files present:')
    for f in files:
        print(f'    {f}: {os.path.getsize(os.path.join(home, f))} bytes')

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
    w = open(os.path.join(home, 'worker.js')).read()
    checks = [
        ('worker buildSportSystemPrompt', 'function buildSportSystemPrompt' in w),
        ('worker sport mode dispatch', "mode === 'sport'" in w),
        ('worker FCBase61 marker', 'FCBase61' in w),
    ]
    for sport in ['mens-basketball', 'football', 'womens-basketball', 'womens-volleyball', 'baseball']:
        page = open(os.path.join(home, f'fieldcheck-sport-{sport}.html')).read()
        checks.append((f'{sport} pill', page.count('fc-agent-pill') >= 5))
        checks.append((f'{sport} mode=sport', "mode:'sport'" in page))
    print()
    for name, ok in checks:
        print(f'  {("OK" if ok else "FAIL"):<6} {name}')
    if not all(ok for _, ok in checks):
        sys.exit(1)

print('=== FCBase61 inline patcher ===')
check_files()
apply('Worker patch', WORKER_B64)
apply('Pages patch (5 sport landings)', PAGES_B64)
verify()
print('\n=== Done. Now run: cd ~/Desktop/fieldcheck-proxy && ./fc-ship-FCBase61.sh ===')
