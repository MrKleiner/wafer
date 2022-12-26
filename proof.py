from pathlib import Path

thisdir = Path(__file__).parent

counter = [a for a in (thisdir / 'htbin').rglob('*.py')] + [b for b in (thisdir / 'mods').rglob('*.js')] + [c for c in (thisdir / 'mods').rglob('*.css')] + [e for e in (thisdir / 'mods').rglob('*.json')] + [n for n in (thisdir / 'panels').rglob('*.html')]


total = 0
for ln in counter:
    total += len(ln.read_text().split('\n'))

print(total)