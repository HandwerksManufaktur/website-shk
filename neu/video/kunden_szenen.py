#!/usr/bin/env python3
"""Hero-Zusammenschnitt der SHK-Seite (assets/reels/kunden-szenen.mp4): jeder Betrieb EINMAL, Köpfe als Match Cut.

Noah, 18.10.2026 (1): „es sollten doch bei dem Handyvideo alle einmal durchlaufen … kein Kunde soll 2x kommen,
bevor die nicht alle Kunden 1x gekommen sind."
Noah, 18.10.2026 (2): „im Clip von Irlbacher schaut er auf einmal so komisch zur Seite. Bettina kannst du vielleicht
auch einfach nur einmal nehmen. Bei Senftleben nimmst du einfach das Video von ihm, wo er steht. Schau auch überall,
dass die Köpfe zentriert sind, sodass es aussieht wie ein Match Cut."

Noah, 19.10.2026: „immernoch nur 6 ausschnitte oder so drin? und patrick ist nicht zentriert und von patrick hätte ich gerne
den ausschnitt im lager drin und die match-cuts gescheit.“

Aufbau (Stand 19.10.2026):
- 12 Szenen à 1,0 s (30 Bilder): Umlauf 1 jeder Betrieb einmal, Umlauf 2 weitere Personen/Orte derselben Betriebe;
  nie derselbe Betrieb direkt hintereinander, auch nicht über die Schleife.
- Stehend oder sitzend, Blick in die Kamera, aus dem Original (keine eingebrannten Untertitel); Augen, Hände, Logos von Hand
  im Kontaktbogen geprüft, Startbild dann fest im Feld `bild`.
- Match Cut: Kopfmitte bei x 50 %, y 21,5 %, Kopfhöhe 17 % (KOPF_*). Zoom je Szene nur so weit wie Größe oder Lage es
  verlangen, höchstens ZOOM_MAX = 1,5 — kein Porträt (Noah 18.10.). Kopf ganz oben/unten im Original → anderen Take nehmen.

Aufruf:  python3 neu/video/kunden_szenen.py              → setzt szenen/*.mp4 zusammen, schreibt Video + Poster, prüft
         python3 neu/video/kunden_szenen.py --schneiden  → holt die Fenster neu (lokal / Drive), richtet aus, dann wie oben
         python3 neu/video/kunden_szenen.py --pruefen    → misst nur die fertige Datei
Braucht OpenCV mit CascadeClassifier (System-python3; das .venv-cv2 hat ihn nicht).
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parents[1]
WS = REPO.parents[1]                                   # CEO-GPT
ZIEL = REPO / 'assets/reels/kunden-szenen.mp4'
SZENEN_ORDNER = HIER / 'szenen'
BILDER = 30                                            # 1,0 s je Szene
VOLLBILD = False                                       # 18.10. nachts: volles Kamerabild ohne Zoom → 19.10.: Köpfe lagen dann zwischen x 0,43–0,58 und y 0,17–0,34, kein Match Cut
# Noah, 19.10.2026: „patrick ist nicht zentriert … und die match-cuts gescheit“ → Match-Cut-Modus mit HÖCHSTENS leichtem Zoom:
# Kopf in jeder Szene an derselben Stelle (50 %/21,5 %) und gleich groß (17 % Bildhöhe). Werte per Rechnung über alle zwölf Szenen gewählt:
# kleinster Zoom (max 1,5 bei Benjamin), bei dem jeder Kopf innerhalb ±15 % gleich groß ist; Grenze setzt der sitzende Senftleben-Mitarbeiter.
# Je Szene nur so viel Zoom, wie Größe ODER Lage verlangen, nie mehr als ZOOM_MAX (sonst wirkt es wie ein Porträt, Noah 18.10.).
KOPF_X, KOPF_Y, KOPF_H = 0.50, 0.215, 0.17
ZOOM_MAX = 1.5
TOL_LAGE, TOL_GROESSE = 0.03, 0.15

# Reihenfolge = Reihenfolge im Video (Frau/Mann wechseln, Hintergründe wechseln). 18.10. abends: weiter weg, wo möglich lächelnd (Noah).
# quelle: lokaler Pfad (relativ zu CEO-GPT) oder drive:<Datei-ID>; ab: Sekunde im Original, ab der das 6–40-s-Fenster läuft.
SZENEN = [
    # ── Umlauf 1: jeder Betrieb einmal ──
    dict(betrieb='Sussmann', wer='Patrick Wähnl im Lager', quelle='drive:18ng_habZYeS93k-Kslk3rCGAJaXpqY3e', datei='Sussmann Hooks (32).MP4', ab=2.5, dauer=6),   # Noah 19.10.: „von patrick hätte ich gerne den ausschnitt im lager drin“
    dict(betrieb='Fischer', wer='Bettina Tittmann im Lager an der Kiste', quelle='kunden/fischer-chemnitz/videos/rohmaterial/b2.mp4', datei='Bodys - Fischer (2).MP4 (Proxy)', ab=58, dauer=2.5, bild=15),   # Logo 1:1 geprüft: alle drei Symbole + FISCHER frei
    dict(betrieb='Erwin Schmidt', wer='Florian Schmidt lächelt in der Badausstellung', quelle='drive:1cTO1f2TFeT2tXk70QJN3_4QLYDUU6fJH', datei='Erwin Schmidt Videos (1) - Skript 1.MP4', ab=27.5, dauer=4, bild=39),
    dict(betrieb='Senftleben', wer='Benjamin Senftleben steht vor dem Firmenwagen und lacht', quelle='drive:1rSxSZJGqGEnIZ4qJeNti8Rq-ygGvPd16', datei='LeadGen/Skript 1 - 1.MP4', ab=77, dauer=7, bild=174),   # bei Bild 24–29 Zunge raus
    dict(betrieb='Stimpfle', wer='Yannick Stimpfle lächelt, Werkstatt', quelle='kunden/stimpfle/videos/rohmaterial/c1.mp4', datei='CTA (Proxy)', ab=21.5, dauer=2, bild=9),
    dict(betrieb='Irlbacher', wer='Josef Irlbacher vor dem Firmenwagen', quelle='drive:1m-aq3JRkKiYh-hzbfRZR2R5DoBgA61ji', datei='Arbeitsclips/b2.mp4 (Proxy)', ab=20, dauer=9.5),   # ab 30 s Handgesten; 19.10.: h6 (lacht) hatte den Kopf bei 15 % ganz oben → Match Cut nur mit 1,6-fachem Zoom; b2 derselbe Wagen, Kopf bei 23 %
    # ── Umlauf 2: weitere Personen und Orte derselben Betriebe (Noah 19.10.: „immernoch nur 6 ausschnitte oder so“) ──
    dict(betrieb='Sussmann', id='sussmann-mirjana', wer='Mirjana Wähnl vor der Sussmann-Logowand', quelle='drive:1halUBA2cGwhBz5GF4YmQWQfMjl_eRJEk', datei='Sussmann Hooks (7).MP4', ab=3.5, dauer=3),
    dict(betrieb='Senftleben', id='senftleben-mitarbeiter', wer='Mitarbeiter von Senftleben lächelt im Interview', quelle='drive:1UoQmbmYsOkSTgdlFyMja62lpe5nr5TpV', datei='Recruiting/MA-Interviews/Senftleben Mitarbeiter (1).MP4', ab=33.5, dauer=5),   # 19.10.: Mitarbeiter (4) kneift fast durchgehend die Augen zu
    dict(betrieb='Erwin Schmidt', id='erwin-schmidt-meike', wer='Meike im Lager vor den Regalkästen', quelle='drive:1234ziq-iZdt-irLxt0nd7-Hsj5HkDwHk', datei='Erwin Schmidt Videos (8) - Skript 5 Meike.MP4', ab=46, dauer=5, bild=60),   # ab 48 s lächelt sie, bei 49,5 s lacht sie
    dict(betrieb='Irlbacher', id='irlbacher-lager', wer='Josef Irlbacher im Regallager', quelle='drive:1sweKzYxD0t7cJ83e6iHeclf0c3mb9J0M', datei='Arbeitsclips/h8.mp4 (Proxy)', ab=42.5, dauer=5),
    dict(betrieb='Fischer', id='fischer-buero', wer='Bettina Tittmann im hellen Raum mit Pflanzen', quelle='kunden/fischer-chemnitz/videos/rohmaterial/b1.mp4', datei='Bodys - Fischer (1).MP4 (Proxy)', ab=55, dauer=4),   # bei 53–55 s Blick nach oben
    dict(betrieb='Stimpfle', id='stimpfle-regal', wer='Yannick Stimpfle vor dem Regal', quelle='kunden/stimpfle/videos/rohmaterial/h9.mp4', datei='Hooks (9).MP4 (Proxy)', ab=49, dauer=3),
]
# Raus (18.10.2026): Josef im Büro (dreht den Kopf weg), Josef in der Sonne (kneift die Augen), alle Clips mit eingebrannten
# Untertiteln aus dem Zusammenschnitt vom 27.09., drei weitere Bettina-Szenen, Senftleben-Szenen im Sitzen.


def slug(b): return b.lower().replace(' ', '-')
def sid(sz): return sz.get('id', slug(sz['betrieb']))      # Szenen-Name (Datei); Zusatzpersonen tragen eine eigene id


# ── Gesicht ──────────────────────────────────────────────────────────────
def _cv():
    import cv2
    if not hasattr(cv2, 'CascadeClassifier'):
        # Das .venv-OpenCV (5.x) hat den CascadeClassifier nicht: einmal selbst mit dem System-python3 neu starten
        # (Sammel-Testläufer und Regel-Prüfer rufen mit dem venv-Python auf).
        if not os.environ.get('KUNDEN_SZENEN_NEUSTART') and os.path.exists('/usr/bin/python3'):
            os.environ['KUNDEN_SZENEN_NEUSTART'] = '1'
            os.execv('/usr/bin/python3', ['/usr/bin/python3'] + sys.argv)
        sys.exit('OpenCV ohne CascadeClassifier — mit System-python3 aufrufen')
    # Zwei frontale Modelle: das zweite (alt2) fängt Brillenträger im Gegenlicht (Josef Irlbacher, 19.10.2026), die das erste
    # zwischendurch verliert. Ein weggedrehter Kopf fällt in beiden durch — der Wegschau-Test bleibt scharf.
    return cv2, [cv2.CascadeClassifier(cv2.data.haarcascades + n) for n in ('haarcascade_frontalface_default.xml', 'haarcascade_frontalface_alt2.xml')]


def gesichter(pfad, verkl=0.5):
    """Je Bild: Kopfmitte (cx, cy) und Kopfhöhe h als Anteil des Bildes, oder None (kein frontales Gesicht)."""
    cv2, ges = _cv()
    cap, out = cv2.VideoCapture(str(pfad)), []
    while True:
        ok, f = cap.read()
        if not ok: break
        H, W = f.shape[:2]
        g = cv2.cvtColor(cv2.resize(f, None, fx=verkl, fy=verkl), cv2.COLOR_BGR2GRAY)
        fs = ()
        for modell in ges:
            fs = modell.detectMultiScale(g, 1.1, 6, minSize=(30, 30))
            if len(fs): break
        if len(fs) == 0: out.append(None); continue
        x, y, w, h = max(fs, key=lambda r: r[2] * r[3]); k = 1 / verkl
        out.append(dict(cx=(x + w / 2) * k / W, cy=(y + h / 2) * k / H, h=h * k / H, W=W, H=H))
    return out


def ruhigste_sekunde(d, fest=None):
    """Start der 30 Bilder mit stabilstem Kopf (Lage + Größe); Kopfdrehung lässt die frontale Erkennung ausfallen.
    fest = Startbild, das per Sichtprüfung gewählt wurde (Augen offen, keine Geste) — Messung läuft trotzdem darüber."""
    import statistics as st
    best = None
    for s in ([fest] if fest is not None else range(len(d) - BILDER + 1)):
        f = d[s:s + BILDER]
        if any(x is None for x in f): continue
        u = st.pstdev([x['cx'] for x in f]) * 10 + st.pstdev([x['cy'] for x in f]) * 10 + (max(x['h'] for x in f) / min(x['h'] for x in f) - 1) * 3
        if best is None or u < best[0]: best = (u, s)
    if best is None: sys.exit('keine Sekunde mit durchgehend frontalem Gesicht')
    f = d[best[1]:best[1] + BILDER]
    mitte = lambda k: sorted(x[k] for x in f)[BILDER // 2]
    return best[1], dict(cx=mitte('cx'), cy=mitte('cy'), h=mitte('h'), W=f[0]['W'], H=f[0]['H'])


# ── Schneiden ────────────────────────────────────────────────────────────
def drive_token():
    py = WS / '.venv/bin/python'
    code = ("from google.oauth2.credentials import Credentials; from google.auth.transport.requests import Request\n"
            f"c=Credentials.from_authorized_user_file('{WS}/system/credentials/google-oauth-token.json')\n"
            "c.valid or c.refresh(Request()); print(c.token)")
    return subprocess.run([str(py), '-c', code], capture_output=True, text=True, check=True).stdout.strip()


def fenster_holen(sz, ziel, token):
    ein = ['-ss', str(sz['ab'])]
    if sz['quelle'].startswith('drive:'):
        fid = sz['quelle'][6:]
        ein += ['-headers', f'Authorization: Bearer {token}\r\n', '-i', f'https://www.googleapis.com/drive/v3/files/{fid}?alt=media&supportsAllDrives=true']
    else:
        ein += ['-i', str(WS / sz['quelle'])]
    # Volle Auflösung behalten (Hoch- und Querformat); die Fenster sind kurz, weil die Leitung schmal sein kann
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ein, '-t', str(sz['dauer']), '-an', '-vf', 'fps=30',
                    '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', str(ziel)], check=True, timeout=900)


def ausrichten(fenster, start, kopf, ziel):
    W, H = kopf['W'], kopf['H']
    fx, fy = kopf['cx'] * W, kopf['cy'] * H
    if VOLLBILD:                                        # volles Kamerabild, kein Zoom; Querformat → 9:16 in voller Höhe um den Kopf
        ch, cw = H, H * 9 / 16
        if cw > W: cw, ch = W, W * 16 / 9
        x0, y0 = min(max(0, fx - cw / 2), W - cw), (H - ch) / 2
    else:
        # Zoom nur so weit wie nötig: Kopfgröße auf KOPF_H bringen und Platz schaffen, damit der Kopf auf KOPF_X/KOPF_Y rücken kann
        z_groesse = KOPF_H / kopf['h']
        cw1, ch1 = (W, W * 16 / 9) if W * 16 / 9 <= H else (H * 9 / 16, H)      # größtes 9:16-Fenster im Bild
        z_x = max(KOPF_X * cw1 / fx if fx < KOPF_X * cw1 else 1, (1 - KOPF_X) * cw1 / (W - fx) if (W - fx) < (1 - KOPF_X) * cw1 else 1)
        z_y = max(KOPF_Y * ch1 / fy if fy < KOPF_Y * ch1 else 1, (1 - KOPF_Y) * ch1 / (H - fy) if (H - fy) < (1 - KOPF_Y) * ch1 else 1)
        z = min(ZOOM_MAX, max(1.0, z_groesse, z_x, z_y))
        cw, ch = cw1 / z, ch1 / z
        x0, y0 = min(max(0, fx - KOPF_X * cw), W - cw), min(max(0, fy - KOPF_Y * ch), H - ch)
    lage = ((fx - x0) / cw, (fy - y0) / ch)
    vf = (f"select='between(n\\,{start}\\,{start + BILDER - 1})',setpts=N/30/TB,"
          f"crop={cw:.0f}:{ch:.0f}:{x0:.0f}:{y0:.0f},scale=540:960:flags=lanczos,setsar=1,format=yuv420p")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(fenster), '-vf', vf, '-frames:v', str(BILDER), '-r', '30', '-an',
                    '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', str(ziel)], check=True)
    return lage, cw / 540


def schneiden():
    SZENEN_ORDNER.mkdir(exist_ok=True)
    token = drive_token() if any(s['quelle'].startswith('drive:') for s in SZENEN) else ''
    protokoll = {}
    with tempfile.TemporaryDirectory() as tmp:
        for sz in SZENEN:
            # Zwischenspeicher (SZENEN_CACHE=<Ordner>): gleiche Quelle + Startsekunde + Länge wird nicht neu geladen
            cache = os.environ.get('SZENEN_CACHE')
            schluessel = f"{sid(sz)}-{sz['quelle'].split(':')[-1].replace('/', '_')[-24:]}-{sz['ab']}-{sz['dauer']}.mp4"
            fen = (Path(cache) if cache else Path(tmp)) / schluessel
            if not fen.exists() or fen.stat().st_size < 10000:
                fenster_holen(sz, fen, token)
            breite = int(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width', '-of', 'csv=p=0', str(fen)], capture_output=True, text=True).stdout.strip() or 0)
            start, kopf = ruhigste_sekunde(gesichter(fen, verkl=1.0 if breite < 2000 else 0.5), sz.get('bild'))   # Proxys (1296 px) in voller Größe, sonst verliert die Erkennung Brillenträger
            lage, quellpx = ausrichten(fen, start, kopf, SZENEN_ORDNER / f"{sid(sz)}.mp4")
            protokoll[sid(sz)] = dict(sekunde=round(sz['ab'] + start / 30, 2), kopf_x=round(lage[0], 3), kopf_y=round(lage[1], 3), quellpixel_je_zielpixel=round(quellpx, 2))
            print(f"{sz['betrieb']:14s} ab {sz['ab'] + start / 30:7.2f} s  Kopf x={lage[0]:.2f} y={lage[1]:.2f}  Quellpixel/Zielpixel {quellpx:.2f}")
    (HIER / 'kunden-szenen-schnitt.json').write_text(json.dumps(protokoll, ensure_ascii=False, indent=1), encoding='utf-8')


# ── Zusammensetzen ───────────────────────────────────────────────────────
def bauen():
    ein, teile = [], []
    for i, sz in enumerate(SZENEN):
        ein += ['-i', str(SZENEN_ORDNER / f"{sid(sz)}.mp4")]
        teile.append(f'[{i}:v]trim=end_frame={BILDER},setpts=PTS-STARTPTS,setsar=1[v{i}];')
    kette = ''.join(teile) + ''.join(f'[v{i}]' for i in range(len(SZENEN))) + f'concat=n={len(SZENEN)}:v=1:a=0[out]'
    tmp = ZIEL.with_suffix('.neu.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ein, '-filter_complex', kette, '-map', '[out]', '-c:v', 'libx264', '-crf', '20',
                    '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', '-an', str(tmp)], check=True)
    tmp.replace(ZIEL)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(ZIEL), '-frames:v', '1', '-q:v', '3', str(ZIEL.with_name('kunden-szenen-poster.jpg'))], check=True)
    (HIER / 'kunden-szenen-folge.json').write_text(json.dumps({'szenen': [sid(s) for s in SZENEN], 'betriebe': [s['betrieb'] for s in SZENEN], 'wer': [s['wer'] for s in SZENEN]}, ensure_ascii=False, indent=1), encoding='utf-8')


# ── Prüfen (am fertigen Video) ───────────────────────────────────────────
def pruefen():
    from PIL import Image, ImageChops, ImageStat
    diff = lambda a, b: ImageStat.Stat(ImageChops.difference(a, b)).mean[0]
    fehler = []
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(ZIEL), '-vf', 'scale=90:160', f'{d}/z_%03d.png'], check=True)
        z = [Image.open(p).convert('L') for p in sorted(Path(d).glob('z_*.png'))]
        ref = {}
        for sz in SZENEN:
            p = f"{d}/r_{sid(sz)}.png"
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(SZENEN_ORDNER / f"{sid(sz)}.mp4"), '-vf', f'select=eq(n\\,{BILDER // 2}),scale=90:160', '-frames:v', '1', p], check=True)
            ref[sid(sz)] = Image.open(p).convert('L')
    grenzen = [0] + [i for i in range(1, len(z)) if diff(z[i], z[i - 1]) > 18] + [len(z)]
    folge = [min(ref, key=lambda b: diff(z[(grenzen[k] + grenzen[k + 1]) // 2], ref[b])) for k in range(len(grenzen) - 1)]
    # Regeln (Noah, 18.10.2026): jede Szene genau einmal · die ersten Szenen zeigen jeden Betrieb genau einmal, bevor eine
    # Zusatzperson kommt · nie derselbe Betrieb direkt hintereinander, auch nicht über die Schleife
    b_von = {sid(s): s['betrieb'] for s in SZENEN}
    if sorted(folge) != sorted(sid(s) for s in SZENEN):
        fehler.append(f'Szenen im Video: {folge} — erwartet jede genau einmal: {[sid(s) for s in SZENEN]}')
    betriebe = sorted({s['betrieb'] for s in SZENEN})
    erste = [b_von.get(x, '?') for x in folge[:len(betriebe)]]
    if sorted(erste) != betriebe:
        fehler.append(f'die ersten {len(betriebe)} Szenen zeigen nicht jeden Betrieb genau einmal: {erste}')
    for i in range(len(folge)):
        a, b2 = b_von.get(folge[i]), b_von.get(folge[(i + 1) % len(folge)])
        if a == b2:
            fehler.append(f'{a} zweimal hintereinander (Szene {i + 1} → {(i + 1) % len(folge) + 1})' + (' über die Schleife' if i == len(folge) - 1 else ''))
    # Kopf je Szene: Lage + Größe gleich, Kopf durchgehend frontal (dreht er weg, fällt die Erkennung aus)
    kd = gesichter(ZIEL, verkl=1.0)
    werte = []
    for k in range(len(grenzen) - 1):
        f = kd[grenzen[k]:grenzen[k + 1]]; b = folge[k] if k < len(folge) else '?'
        erkannt = [x for x in f if x]
        quote = len(erkannt) / max(1, len(f))
        if quote < 0.9:
            fehler.append(f'{b}: Kopf nur in {quote:.0%} der Bilder frontal (wegdrehen?)'); continue
        m = lambda key: sorted(x[key] for x in erkannt)[len(erkannt) // 2]
        cx, cy, h = m('cx'), m('cy'), m('h'); werte.append((b, cx, cy, h))
        if not VOLLBILD and (abs(cx - KOPF_X) > TOL_LAGE or abs(cy - KOPF_Y) > TOL_LAGE):
            fehler.append(f'{b}: Kopf bei x={cx:.2f} y={cy:.2f} statt {KOPF_X:.2f}/{KOPF_Y:.2f}')
        if not VOLLBILD and abs(h / KOPF_H - 1) > TOL_GROESSE:
            fehler.append(f'{b}: Kopfhöhe {h:.2f} statt {KOPF_H:.2f}')
    return folge, werte, fehler


if __name__ == '__main__':
    if '--schneiden' in sys.argv:
        schneiden()
    if '--pruefen' not in sys.argv:
        bauen()
    folge, werte, fehler = pruefen()
    print('Folge:', ' → '.join(folge))
    for b, cx, cy, h in werte:
        print(f'  {b:14s} Kopf x={cx:.3f} y={cy:.3f} Höhe={h:.3f}')
    if fehler:
        print('❌', *fehler, sep='\n  '); sys.exit(1)
    ausschnitt = 'volles Kamerabild (kein Zoom)' if VOLLBILD else f'Kopf in jeder Szene bei {KOPF_X:.0%}/{KOPF_Y:.0%} mit {KOPF_H:.0%} Höhe (±{TOL_LAGE:.0%} / ±{TOL_GROESSE:.0%})'
    print(f'✅ {len(folge)} Szenen, jeder Betrieb zuerst einmal, nie zweimal hintereinander (inkl. Schleife), {ausschnitt}, Kopf durchgehend frontal')
