#!/usr/bin/env python3
"""Hero-Zusammenschnitt der SHK-Seite (assets/reels/kunden-szenen.mp4) — reihum, jeder Betrieb gleich oft.

Noah, 18.10.2026: „es sollten doch bei dem Handyvideo alle einmal durchlaufen, möglichst immer hintereinander gewechselt …
kein Kunde soll 2x kommen, bevor die nicht alle Kunden 1x gekommen sind."
Davor, 29.09.2026: „keine Firma kommt zweimal hintereinander … noch mehr Match Cuts."

Regel (Pflicht, gemessen): Die Betriebe laufen in einer FESTEN Reihenfolge reihum. Jedes Fenster aus so vielen Szenen,
wie es Betriebe gibt, enthält jeden Betrieb genau einmal — von jeder Stelle aus und auch über die Schleife (Ende → Anfang).
Dafür hat jeder Betrieb gleich viele Szenen (SZENEN_JE_BETRIEB). Kommt ein Betrieb dazu, braucht er so viele Szenen
wie die anderen; fehlen ihm welche, wird nicht hinten angehängt, sondern geschnitten oder bei den anderen gekürzt.

Quellen:
- QUELLE: der alte Zusammenschnitt vom 27.09.2026 (18 Clips à 20/21 Bilder, 540×960, aus den 4K-Originalen im Drive).
- zusatz/*.mp4: je 21 Bilder 540×960, geschnitten aus den Kunden-Rohclips (Herkunft in ZUSATZ).

Aufruf:  python3 neu/video/kunden_szenen.py            → baut assets/reels/kunden-szenen.mp4 + Poster, prüft das Ergebnis
         python3 neu/video/kunden_szenen.py --pruefen  → misst nur die fertige Datei (Betrieb je Szene, Reihum-Regel)
"""
import itertools, json, random, subprocess, sys, shutil
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parents[1]
ZIEL = REPO / 'assets/reels/kunden-szenen.mp4'
QUELLE = HIER / 'kunden-szenen-quelle-2026-09-27.mp4'
ZUSATZ_ORDNER = HIER / 'zusatz'
GRENZEN = [0, 21, 42, 63, 84, 104, 125, 146, 167, 188, 209, 230, 251, 272, 293, 314, 335, 355, 376]  # Schnitte in QUELLE
SZENEN_JE_BETRIEB = 4

# Szene → (Betrieb, Haltung, Umgebung, Geste am Anfang, Geste am Ende). Zahlen = Clip im alten Video, Text = zusatz/<name>.mp4
SZENEN = {
    1: ('Sussmann', 'steht', 'lager', 0, 0),        3: ('Sussmann', 'steht', 'logo', 0, 0),
    9: ('Sussmann', 'steht', 'wand', 0, 0),         18: ('Sussmann', 'steht', 'lager', 0, 0),
    2: ('Irlbacher', 'steht', 'wagen', 1, 1),       7: ('Irlbacher', 'steht', 'wagen', 0, 0),
    14: ('Irlbacher', 'steht', 'wagen', 0, 1),      'irlbacher-buero': ('Irlbacher', 'steht', 'buero', 0, 0),
    4: ('Senftleben', 'sitzt', 'tisch', 0, 0),      6: ('Senftleben', 'sitzt', 'tisch', 0, 0),
    13: ('Senftleben', 'sitzt', 'tisch', 0, 0),     17: ('Senftleben', 'sitzt', 'tisch', 1, 1),
    8: ('Erwin Schmidt', 'steht', 'lager', 0, 0),   10: ('Erwin Schmidt', 'sitzt', 'tisch', 0, 0),
    12: ('Erwin Schmidt', 'steht', 'lager', 0, 0),  15: ('Erwin Schmidt', 'sitzt', 'tisch', 0, 0),
    'fischer-lager': ('Fischer', 'steht', 'lager', 0, 0),   'fischer-werkbank': ('Fischer', 'sitzt', 'tisch', 0, 0),
    'fischer-gelb': ('Fischer', 'sitzt', 'raum', 0, 0),     'fischer-buero': ('Fischer', 'steht', 'buero', 0, 0),
    'stimpfle-regal': ('Stimpfle', 'steht', 'lager', 0, 1), 'stimpfle-werkstatt': ('Stimpfle', 'sitzt', 'werkstatt', 0, 0),
    'stimpfle-monteur': ('Stimpfle', 'sitzt', 'werkstatt', 0, 0), 'stimpfle-halle': ('Stimpfle', 'steht', 'halle', 0, 0),
}
# Bewusst raus (18.10.2026, damit jeder Betrieb 4 hat): 11 Patrick im Lager (wie 1), 16 Mirjana am Logo (wie 3), 5 Benjamin (kommt in 17).
ZUSATZ = {   # Herkunft der neuen Szenen: Rohclip, Startsekunde (je 21 Bilder, 30 fps)
    'fischer-lager': 'kunden/fischer-chemnitz/videos/rohmaterial/c1.mp4 @30,0',
    'fischer-werkbank': 'kunden/fischer-chemnitz/videos/rohmaterial/h9.mp4 @9,0',
    'fischer-gelb': 'kunden/fischer-chemnitz/videos/rohmaterial/h11.mp4 @12,0',
    'fischer-buero': 'kunden/fischer-chemnitz/videos/rohmaterial/b1.mp4 @200,0',
    'stimpfle-regal': 'kunden/stimpfle/videos/rohmaterial/c1.mp4 @30,0',
    'stimpfle-werkstatt': 'kunden/stimpfle/videos/rohmaterial/br2.mp4 @30,0',
    'stimpfle-monteur': 'kunden/stimpfle/videos/rohmaterial/br3.mp4 @80,0',
    'stimpfle-halle': 'kunden/stimpfle/videos/rohmaterial/g1.mp4 @130,0 (4096×2304, Mitte 1296×2304 ausgeschnitten)',
    'irlbacher-buero': 'Drive Irlbacher/Videos/Rohmaterial/Arbeitsclips/h4.mp4 @10,0',
}
START = 1   # Patrick im Lager eröffnet (Poster bleibt gleich)


def betrieb(s): return SZENEN[s][0]
BETRIEBE = sorted({betrieb(s) for s in SZENEN})


def uebergang(a, b):
    A, B = SZENEN[a], SZENEN[b]
    p = 0
    p += 3 if A[1] == B[1] else 0         # Haltung bleibt → ruhiger Schnitt
    p += 2 if A[2] == B[2] else 0         # gleiche Umgebung, anderer Betrieb → Match Cut
    p += 2 if A[4] and B[3] else 0        # Geste läuft über den Schnitt
    return p


def wertung(folge):
    return sum(uebergang(folge[i], folge[(i + 1) % len(folge)]) for i in range(len(folge)))


def suchen(saat=7):
    """Feste Betriebsreihenfolge (alle Umläufe gleich) × Szenenwahl je Umlauf; beste Match-Cut-Wertung gewinnt."""
    rnd = random.Random(saat)
    je = {b: [s for s in SZENEN if betrieb(s) == b] for b in BETRIEBE}
    for b, l in je.items():
        if len(l) != SZENEN_JE_BETRIEB:
            sys.exit(f'{b} hat {len(l)} Szenen statt {SZENEN_JE_BETRIEB} — erst angleichen, nie hinten anhängen')
    erster = betrieb(START)
    best, bw = None, -1
    for rest in itertools.permutations([b for b in BETRIEBE if b != erster]):
        kreis = (erster,) + rest
        ordnung = {b: l[:] for b, l in je.items()}
        ordnung[erster].remove(START); ordnung[erster].insert(0, START)
        def folge_aus(o): return [o[kreis[i % len(kreis)]][i // len(kreis)] for i in range(len(kreis) * SZENEN_JE_BETRIEB)]
        f = folge_aus(ordnung); w = wertung(f)
        for _ in range(3000):
            b = rnd.choice(kreis); l = ordnung[b]
            i, j = rnd.randrange(len(l)), rnd.randrange(len(l))
            if i == j or (b == erster and 0 in (i, j)): continue
            l[i], l[j] = l[j], l[i]
            w2 = wertung(folge_aus(ordnung))
            if w2 >= w: w = w2
            else: l[i], l[j] = l[j], l[i]
        if w > bw: best, bw = folge_aus(ordnung), w
    return best, bw


def pruefen(folge):
    """Reihum-Regel: jedes Fenster aus len(BETRIEBE) Szenen (auch über die Schleife) enthält jeden Betrieb genau einmal."""
    fehler, n, k = [], len(folge), len(BETRIEBE)
    if n % k:
        fehler.append(f'{n} Szenen gehen nicht in Umläufe à {k} auf')
    for i in range(n):
        fenster = [betrieb(folge[(i + j) % n]) for j in range(k)]
        doppelt = sorted({b for b in fenster if fenster.count(b) > 1})
        if doppelt:
            fehler.append(f'ab Szene {i + 1}: {", ".join(doppelt)} zweimal, bevor alle einmal kamen' + (' (über die Schleife)' if i + k > n else ''))
    if sorted(map(str, folge)) != sorted(map(str, SZENEN)):
        fehler.append('nicht alle Szenen genau einmal drin')
    return fehler


def bauen(folge):
    eingaben, teile = ['-i', str(QUELLE)], []
    zusatz_idx = {}
    for s in folge:
        if isinstance(s, str) and s not in zusatz_idx:
            zusatz_idx[s] = len(zusatz_idx) + 1
            eingaben += ['-i', str(ZUSATZ_ORDNER / f'{s}.mp4')]
    for k, s in enumerate(folge):
        if isinstance(s, int):
            teile.append(f'[0:v]trim=start_frame={GRENZEN[s-1]}:end_frame={GRENZEN[s]},setpts=PTS-STARTPTS,setsar=1[v{k}];')
        else:
            teile.append(f'[{zusatz_idx[s]}:v]trim=end_frame=21,setpts=PTS-STARTPTS,setsar=1[v{k}];')
    kette = ''.join(teile) + ''.join(f'[v{k}]' for k in range(len(folge))) + f'concat=n={len(folge)}:v=1:a=0[out]'
    tmp = ZIEL.with_suffix('.neu.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *eingaben, '-filter_complex', kette, '-map', '[out]',
                    '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', '-an', str(tmp)], check=True)
    tmp.replace(ZIEL)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(ZIEL), '-frames:v', '1', '-q:v', '3', str(ZIEL.with_name('kunden-szenen-poster.jpg'))], check=True)
    (HIER / 'kunden-szenen-folge.json').write_text(json.dumps({'folge': folge, 'betriebe': [betrieb(s) for s in folge]}, ensure_ascii=False, indent=1), encoding='utf-8')


def messen():
    """Misst die FERTIGE Datei: Schnitte per Bildwechsel, jede Szene per Bildvergleich gegen alle Quellszenen → Betrieb."""
    from PIL import Image, ImageChops, ImageStat
    import tempfile
    def bilder(datei, d, pre):
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(datei), '-vf', 'scale=90:160', f'{d}/{pre}_%03d.png'], check=True)
        return sorted(Path(d).glob(f'{pre}_*.png'))
    diff = lambda a, b: ImageStat.Stat(ImageChops.difference(a, b)).mean[0]
    with tempfile.TemporaryDirectory() as d:
        q = bilder(QUELLE, d, 'q')
        ref = {s: Image.open(q[(GRENZEN[s-1] + GRENZEN[s]) // 2]).convert('L') for s in SZENEN if isinstance(s, int)}
        for s in SZENEN:
            if isinstance(s, str):
                ref[s] = Image.open(bilder(ZUSATZ_ORDNER / f'{s}.mp4', d, s.replace('-', '_'))[10]).convert('L')
        z = [Image.open(f).convert('L') for f in bilder(ZIEL, d, 'z')]
        grenzen = [0] + [i for i in range(1, len(z)) if diff(z[i], z[i-1]) > 18] + [len(z)]
        folge = [min(ref, key=lambda s: diff(z[(grenzen[k] + grenzen[k+1]) // 2], ref[s])) for k in range(len(grenzen) - 1)]
    fehler = pruefen(folge)
    if len(folge) != len(SZENEN):
        fehler.insert(0, f'{len(folge)} Szenen gemessen statt {len(SZENEN)}')
    return folge, fehler


if __name__ == '__main__':
    if '--pruefen' not in sys.argv:
        folge, w = suchen()
        print('Folge:', folge, 'Match-Cut-Wertung', w)
        f = pruefen(folge)
        if f: sys.exit('Suche fand keine gültige Folge: ' + '; '.join(f))
        bauen(folge)
    folge, fehler = messen()
    print('Gemessen:', folge)
    k = len(BETRIEBE)
    for u in range(0, len(folge), k):
        print(f'  Umlauf {u // k + 1}:', ' → '.join(betrieb(s) for s in folge[u:u + k]))
    if fehler:
        print('❌', *fehler, sep='\n  '); sys.exit(1)
    print(f'✅ {len(folge)} Szenen, {k} Betriebe à {SZENEN_JE_BETRIEB}, reihum: jedes Fenster aus {k} Szenen hat jeden Betrieb genau einmal (inkl. Schleife)')
