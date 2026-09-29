#!/usr/bin/env python3
"""Misst, wie breit jedes Bild auf den SHK-Seiten wirklich angezeigt wird — Handy (390 px) und Desktop (1440 px).

Daraus baut optimierung.py die sizes-Angabe je Bild, damit der Browser die kleinste passende WebP-Fassung lädt
(vorher: Pauschale „100vw / 50vw" → am Handy luden Galeriebilder in 1100 px, angezeigt wurden ~200 px).

Aufruf (lokaler Server auf 8792 muss laufen, launch.json „shk-website"):
    ../../.venv/bin/python neu/bildgroessen_messen.py && python3 neu/build.py && python3 neu/optimierung.py index.html
Nach jeder Layout-Änderung erneut laufen lassen; ohne Messung fällt optimierung.py auf die Pauschale zurück.
"""
import asyncio, json, math, re, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
BASIS = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8792'
SEITEN = ['/', '/neu/', '/neu/monteure/', '/neu/auftraege/', '/neu/fallstudien/', '/neu/ueber-uns/', '/neu/potenzialanalyse/']
# Wissen/Ratgeber (29.09.2026): Übersicht + jeder Artikel aus neu/wissen-daten — auch die zeitgesteuerten, damit ihre Fotos
# beim Veröffentlichen schon die gemessene Anzeigegröße haben (sonst lädt das Handy ein zu großes Bild).
SEITEN += ['/neu/wissen/'] + [f'/neu/wissen/{p.stem}/' for p in sorted((Path(__file__).resolve().parent / 'wissen-daten').glob('*.json')) if not p.name.startswith('_')]
MESSEN = '''async () => {
  document.querySelectorAll('img').forEach(i => i.loading = 'eager');
  await Promise.all([...document.images].map(i => i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 8000); })));
  const m = {}, oben = [];
  for (const i of document.images) {
    const src = i.currentSrc || i.src || '';
    const k = (src.match(/\\/assets\\/opt\\/(.+)-\\d+\\.webp/) || [])[1];
    const w = i.getBoundingClientRect().width;
    if (k && w > 0) m[k] = Math.max(m[k] || 0, w);
    const r = i.getBoundingClientRect();
    if (k && w > 40 && r.top < innerHeight && r.bottom > 0) oben.push(k);   // im ersten Bildschirm sichtbar
  }
  return {m, oben};
}'''


async def main():
    from playwright.async_api import async_playwright
    breite, oben = {}, {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nr, (w, h) in enumerate(((390, 844), (1440, 900))):
            ctx = await b.new_context(viewport={'width': w, 'height': h})
            for s in SEITEN:
                pg = await ctx.new_page()
                await pg.goto(BASIS + s, wait_until='networkidle')
                erg = await pg.evaluate(MESSEN)
                oben.setdefault(s, set()).update(erg['oben'])
                for k, v in erg['m'].items():
                    breite.setdefault(k, [0, 0])
                    breite[k][nr] = max(breite[k][nr], math.ceil(v / 10) * 10)
                await pg.close()
            await ctx.close()
        await b.close()
    # Nur am Handy oder nur am Desktop sichtbar: die andere Seite erbt den gemessenen Wert
    for k, (m, d) in breite.items():
        breite[k] = [m or d, d or m]
    daten = dict(sorted(breite.items()))
    daten['_oben'] = {s: sorted(v) for s, v in oben.items()}     # je Seite: Bilder im ersten Bildschirm (Handy oder Desktop)
    (HIER / 'bildgroessen.json').write_text(json.dumps(daten, indent=1), encoding='utf-8')
    print(f'✓ {len(breite)} Bilder gemessen → neu/bildgroessen.json')


if __name__ == '__main__':
    asyncio.run(main())
