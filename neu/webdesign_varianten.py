"""Kleine Varianten der Webdesign-Screenshots (assets/webdesign/*-start-desk.jpg → -600.jpg, *-start-mobil.jpg → -240.jpg).
Nach jedem neuen Screenshot laufen lassen: python3 neu/webdesign_varianten.py  (PageSpeed: „Properly size images“, 02.11.2026)."""
from pathlib import Path
from PIL import Image
D = Path(__file__).resolve().parent.parent / 'assets' / 'webdesign'
for p in sorted(D.glob('*-start-*.jpg')):
    if p.stem.endswith(('-600', '-240')): continue
    w = 600 if p.stem.endswith('desk') else 240
    ziel = p.with_name(f'{p.stem}-{w}.jpg')
    im = Image.open(p); im = im.convert('RGB').resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(ziel, 'JPEG', quality=78, optimize=True, progressive=True)
    print(ziel.name, ziel.stat().st_size // 1024, 'KB')
