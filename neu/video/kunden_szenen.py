#!/usr/bin/env python3
"""Hero-Zusammenschnitt der SHK-Seite (assets/reels/kunden-szenen.mp4) neu anordnen.

Noah, 29.09.2026: „keine Firma kommt sozusagen zweimal hintereinander … nach Senftleben kommt nicht nochmal Senftleben …
alles bleibt drin … vielleicht können wir die Clips noch so anpassen, dass wir noch mehr Match Cuts haben."

Quelle: der bisherige Zusammenschnitt (18 Clips à 21 Bilder, 30 fps, 540×960, aus den 4K-Originalen im Drive, 27.09.2026).
Seine Clips werden hier nur umgeordnet — keine neue Skalierung, kein Clip fällt weg. Die Zuordnung Clip → Betrieb steht in CLIPS
(per Bildvergleich mit den Porträtfotos der Betriebe bestimmt). Die Reihenfolge sucht eine Optimierung:
Pflicht = kein Betrieb zweimal hintereinander, auch nicht über die Schleife (letzter → erster Clip);
Punkte für Match Cuts = gleiche Haltung (stehend/sitzend), gleiche Umgebung (Lager, Tisch …), Geste auf Geste.

Aufruf:  python3 neu/video/kunden_szenen.py            → baut assets/reels/kunden-szenen.mp4 + Poster, prüft das Ergebnis
         python3 neu/video/kunden_szenen.py --pruefen  → nur Prüfung der fertigen Datei (Betrieb je Clip, Nachbarn inkl. Schleife)
"""
import itertools, json, random, subprocess, sys, shutil
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parents[1]
ZIEL = REPO / 'assets/reels/kunden-szenen.mp4'
QUELLE = HIER / 'kunden-szenen-quelle-2026-09-27.mp4'   # unveränderte Sicherung des alten Zusammenschnitts = Clip-Quelle
GRENZEN = [0, 21, 42, 63, 84, 104, 125, 146, 167, 188, 209, 230, 251, 272, 293, 314, 335, 355, 376]  # gemessene Schnitte

# Clip-Nr (1-basiert, Reihenfolge im alten Video) → (Betrieb, Haltung, Umgebung, Geste am Anfang, Geste am Ende)
CLIPS = {
    1: ('Sussmann', 'steht', 'lager', 0, 0),    2: ('Irlbacher', 'steht', 'wagen', 1, 1),
    3: ('Sussmann', 'steht', 'logo', 0, 0),     4: ('Senftleben', 'sitzt', 'tisch', 0, 0),
    5: ('Senftleben', 'sitzt', 'tisch', 1, 1),  6: ('Senftleben', 'sitzt', 'tisch', 0, 0),
    7: ('Irlbacher', 'steht', 'wagen', 0, 0),   8: ('Erwin Schmidt', 'steht', 'lager', 0, 0),
    9: ('Sussmann', 'steht', 'wand', 0, 0),     10: ('Erwin Schmidt', 'sitzt', 'tisch', 0, 0),
    11: ('Sussmann', 'steht', 'lager', 0, 0),   12: ('Erwin Schmidt', 'steht', 'lager', 0, 0),
    13: ('Senftleben', 'sitzt', 'tisch', 0, 0), 14: ('Irlbacher', 'steht', 'wagen', 0, 1),
    15: ('Erwin Schmidt', 'sitzt', 'tisch', 0, 0), 16: ('Sussmann', 'steht', 'logo', 1, 1),
    17: ('Senftleben', 'sitzt', 'tisch', 1, 1), 18: ('Sussmann', 'steht', 'lager', 0, 0),
}
START = 1   # Patrick im Lager eröffnet, wie bisher (Poster bleibt gleich)


def uebergang(a, b):
    A, B = CLIPS[a], CLIPS[b]
    if A[0] == B[0]:
        return -1000                      # Pflicht: nie derselbe Betrieb nebeneinander
    p = 0
    p += 3 if A[1] == B[1] else 0         # Haltung bleibt → ruhiger Schnitt
    p += 2 if A[2] == B[2] else 0         # gleiche Umgebung, anderer Betrieb → Match Cut
    p += 2 if A[4] and B[3] else 0        # Geste läuft über den Schnitt
    return p


def wertung(folge):
    return sum(uebergang(folge[i], folge[(i + 1) % len(folge)]) for i in range(len(folge)))


def suchen(runden=400000, saat=7):
    rnd = random.Random(saat)
    rest = [c for c in CLIPS if c != START]
    best, bw = None, -10**9
    for neustart in range(40):
        f = [START] + rnd.sample(rest, len(rest)); w = wertung(f)
        for _ in range(runden // 40):
            i, j = rnd.randrange(1, 18), rnd.randrange(1, 18)
            if i == j: continue
            g = f[:]; g[i], g[j] = g[j], g[i]; wg = wertung(g)
            if wg >= w: f, w = g, wg
        if w > bw: best, bw = f, w
    return best, bw


def pruefen(folge):
    fehler = []
    for i in range(len(folge)):
        a, b = folge[i], folge[(i + 1) % len(folge)]
        if CLIPS[a][0] == CLIPS[b][0]:
            fehler.append(f'Clip {a} → {b}: zweimal {CLIPS[a][0]}' + (' (über die Schleife)' if i == len(folge) - 1 else ''))
    if sorted(folge) != sorted(CLIPS):
        fehler.append('nicht alle Clips genau einmal drin')
    return fehler


def bauen(folge):
    if not QUELLE.exists():
        shutil.copy2(ZIEL, QUELLE)
    teile = ''.join(f'[0:v]trim=start_frame={GRENZEN[c-1]}:end_frame={GRENZEN[c]},setpts=PTS-STARTPTS[v{k}];' for k, c in enumerate(folge))
    kette = ''.join(f'[v{k}]' for k in range(len(folge))) + f'concat=n={len(folge)}:v=1:a=0[out]'
    tmp = ZIEL.with_suffix('.neu.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(QUELLE), '-filter_complex', teile + kette, '-map', '[out]',
                    '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', '-an', str(tmp)], check=True)
    tmp.replace(ZIEL)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(ZIEL), '-frames:v', '1', '-q:v', '3', str(ZIEL.with_name('kunden-szenen-poster.jpg'))], check=True)
    (HIER / 'kunden-szenen-folge.json').write_text(json.dumps({'folge': folge, 'betriebe': [CLIPS[c][0] for c in folge]}, ensure_ascii=False, indent=1), encoding='utf-8')


def messen():
    """Prüft die FERTIGE Datei: jedes Bild-Segment wird gegen die Quell-Clips verglichen → Clip-Nr → Betrieb → Nachbarn."""
    from PIL import Image, ImageChops, ImageStat
    import tempfile
    def bilder(datei, d):
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(datei), '-vf', 'scale=90:160', f'{d}/f_%03d.png'], check=True)
        return sorted(Path(d).glob('f_*.png'))
    with tempfile.TemporaryDirectory() as dq, tempfile.TemporaryDirectory() as dz:
        q, z = bilder(QUELLE, dq), bilder(ZIEL, dz)
        mitte_q = {c: Image.open(q[(GRENZEN[c-1] + GRENZEN[c]) // 2]).convert('L') for c in CLIPS}
        if len(z) != len(q):
            return None, [f'Bildzahl {len(z)} statt {len(q)}']
        folge, pos = [], 0
        for c_alt in range(18):
            n = GRENZEN[c_alt + 1] - GRENZEN[c_alt]
            # Segmentlänge ist nicht fest (20/21 Bilder) → Mitte des k-ten Segments über laufende Position
            folge.append(None); pos += n
        # Segmente der fertigen Datei über Schnitterkennung
        grenzen, prev = [0], None
        for i, f in enumerate(z):
            im = Image.open(f).convert('L')
            if prev is not None and ImageStat.Stat(ImageChops.difference(im, prev)).mean[0] > 18:
                grenzen.append(i)
            prev = im
        grenzen.append(len(z))
        folge = []
        for k in range(len(grenzen) - 1):
            m = Image.open(z[(grenzen[k] + grenzen[k+1]) // 2]).convert('L')
            folge.append(min(CLIPS, key=lambda c: ImageStat.Stat(ImageChops.difference(m, mitte_q[c])).mean[0]))
    return folge, pruefen(folge)


if __name__ == '__main__':
    if '--pruefen' not in sys.argv:
        folge, w = suchen()
        print('Folge:', folge, 'Wertung', w)
        f = pruefen(folge)
        if f: sys.exit('Suche fand keine gültige Folge: ' + '; '.join(f))
        bauen(folge)
    folge, fehler = messen()
    print('Gemessen:', folge)
    print('Betriebe:', ' → '.join(CLIPS[c][0] for c in folge) if folge else '-')
    if fehler:
        print('❌', *fehler, sep='\n  '); sys.exit(1)
    print('✅ 18 Clips, jeder genau einmal, nie derselbe Betrieb nebeneinander (inkl. Schleife)')
