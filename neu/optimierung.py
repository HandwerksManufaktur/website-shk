#!/usr/bin/env python3
"""Ladezeit + Messung für die SHK-Seiten — EINE Quelle für das Redesign (build.py) und die Live-Startseite.

Noah, 27.09.2026: „mobile speed, pagespeed, muss alles optimiert sein … hotjar … analytics" und danach
„bau analytics und hotjar auch auf die live startseite — und alles was wir da oben gemacht haben".

Aufruf für eine fertige, handgeschriebene Seite (z. B. die Live-Startseite):
    python3 neu/optimierung.py index.html
Wirkt idempotent: ein zweiter Lauf ändert nichts mehr.
"""
import hashlib, re, sys
from pathlib import Path
from urllib.parse import unquote
from PIL import Image, ImageOps

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
OPT = REPO / 'assets' / 'opt'

GA4 = 'G-STBDT88H69'          # dieselbe Property wie die bisherige SHK-Seite
CS_TAG = '99d8993a2bc41'      # Contentsquare (ehemals Hotjar): Heatmaps, Klick-Karten, Aufzeichnungen


def css_klein(t):
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    t = re.sub(r'\s*\n\s*', ' ', t)          # Zeilen zusammen, nie zwei Wörter verkleben (calc, grid-areas)
    return t.strip()


def fonts_css():
    """Lokale Schriften, auf Latein-Zeichen zugeschnitten (fonts/sub, pyftsubset): 418 → 149 KB, keine Verbindung zu Google."""
    return css_klein((REPO / 'fonts' / 'fonts.css').read_text(encoding='utf-8').replace("url('", "url('/fonts/sub/")) + FALLBACK


# Ersatzschriften mit angeglichenen Maßen: bis die echte Schrift da ist, nimmt der Text schon denselben Platz ein —
# sonst springen Zeilen und Knöpfe beim Tausch (PageSpeed „Layout Shift"). Werte mit fontTools aus den Dateien
# gemessen (Breite eines deutschen Satzes, hhea-Maße), 27.09.2026.
FALLBACK = ("@font-face{font-family:'Inter Fallback';src:local('Arial');size-adjust:107.09%;ascent-override:90.46%;descent-override:22.52%;line-gap-override:0%}"
            "@font-face{font-family:'Archivo Fallback';src:local('Arial');size-adjust:111.04%;ascent-override:79.07%;descent-override:18.91%;line-gap-override:0%}"
            "@font-face{font-family:'Instrument Serif Fallback';src:local('Times New Roman');size-adjust:87.40%;ascent-override:113.28%;descent-override:35.47%;line-gap-override:0%}")


def messung_kopf(gruppe):
    """GA4 + Contentsquare laden erst bei der ersten Berührung (Scroll, Tipp, Maus, Taste) oder 3,5 s nach dem Laden.
    Bis dahin sammelt dataLayer jedes Ereignis — es geht nichts verloren, aber die Seite ist zuerst da."""
    return ("<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());"
            f"gtag('config','{GA4}',{{content_group:'{gruppe}'}});window._uxa=window._uxa||[];"
            "(function(){var da=0;function los(){if(da)return;da=1;"
            f"['https://www.googletagmanager.com/gtag/js?id={GA4}','https://t.contentsquare.net/uxa/{CS_TAG}.js']"
            ".forEach(function(q){var e=document.createElement('script');e.async=true;e.src=q;document.head.appendChild(e)})}"
            "['pointerdown','keydown','scroll','touchstart','mousemove'].forEach(function(t){addEventListener(t,los,{once:true,passive:true})});"
            "addEventListener('load',function(){setTimeout(los,3500)})})()</script>")


def messung_js_version():
    return hashlib.md5((REPO / 'messung.js').read_bytes()).hexdigest()[:8]


GROESSEN = HIER / 'bildgroessen.json'   # gemessene Anzeigebreiten je Bild (bildgroessen_messen.py) → passende sizes


def stamm(pfad):
    return re.sub(r'[^a-z0-9]+', '-', unquote(pfad).lower().strip('/').rsplit('.', 1)[0])


def groessen():
    import json
    try:
        return json.loads(GROESSEN.read_text(encoding='utf-8'))
    except Exception:
        return {}


QUELLEN = OPT / '_quellen.json'           # opt-Stamm → Originalpfad; damit lässt sich eine schon umgestellte Seite neu rechnen


def _quellen():
    import json
    try:
        return json.loads(QUELLEN.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _quelle_merken(pfad):
    import json
    q = _quellen()
    if q.get(stamm(pfad)) != pfad:
        q[stamm(pfad)] = pfad
        QUELLEN.write_text(json.dumps(dict(sorted(q.items())), indent=1), encoding='utf-8')


def webp(pfad, breite):
    """Bild → WebP in assets/opt/, höchstens `breite` px breit. Gibt (url, w, h) zurück; baut nur neu, wenn die Quelle neuer ist."""
    quelle = REPO / unquote(pfad.lstrip('/'))
    if not quelle.exists():
        return None
    OPT.mkdir(exist_ok=True)
    _quelle_merken(pfad)
    im = ImageOps.exif_transpose(Image.open(quelle)); w0, h0 = im.size   # Handyfotos tragen die Drehung nur im EXIF — WebP verliert sie (bad-wanne stand quer, 27.09.2026)
    w = min(breite, w0); h = round(h0 * w / w0)
    ziel = OPT / f'{stamm(pfad)}-{w}.webp'
    if not ziel.exists() or ziel.stat().st_mtime < quelle.stat().st_mtime:
        im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') else im.convert('RGB')
        q = 56 if '/funnels/' in pfad else 78        # Funnel-Screenshots im Handy-Rahmen (lang, klein angezeigt): 56 hält sie lesbar, spart ~40 % (27.09.2026: 447 KB bremsten den LCP)
        im.resize((w, h), Image.LANCZOS).save(ziel, 'WEBP', quality=q, method=6)
    return f'/assets/opt/{ziel.name}', w, h


def breiten(pfad):
    p = pfad.lower()
    if 'logos' in p or '/logo' in p: return [180, 360]            # Logo-Kacheln ≤ 336 px
    if '/funnels/' in p: return [200, 320, 480]                  # Funnel-Screenshots: Mini-Handy 96–150 px, großes Handy 280 px
    if 'rund' in p or 'poster' in p: return [320, 640]
    return [320, 480, 640, 960, 1100]                             # Fotos: der Browser nimmt die kleinste, die reicht


def optimieren(seite, ohne_srcset=(), pfad='/'):
    """Jedes JPG/PNG-Bild als passend großes WebP (+ srcset), alles unterhalb der ersten Sektion lazy.
    `ohne_srcset`: Pfad-Teile, deren Bilder per Skript ausgetauscht werden — srcset würde den Tausch überstimmen."""
    seite = re.sub(r'(/assets/[^"\'\s,)?]+)\?v=[0-9a-f]{6,12}', r'\1', seite)   # alte Fingerabdrücke weg, am Ende neu rechnen
    teile = seite.split('</section>', 1)                          # bis zum Ende der ersten Sektion = Hero, bleibt eager
    gemessen = groessen()

    quellen = _quellen()

    def img(m, lazy):
        tag = m.group(0)
        # schon umgestellt? Original zurückholen, eigene srcset/sizes weg — dann wie neu rechnen (idempotent, auch nach Layout-Änderungen)
        alt = re.search(r'src="/assets/opt/(.+?)-\d+\.webp"', tag)
        if alt and alt.group(1) in quellen:
            tag = tag.replace(alt.group(0), f'src="{quellen[alt.group(1)]}"')
            tag = re.sub(r' srcset="/assets/opt/[^"]*"', '', tag)
            tag = re.sub(r' sizes="[^"]*"', '', tag)
        src = re.search(r'src="(/[^"]+\.(?:jpe?g|png))"', tag, re.I)
        if src:
            pfad = src.group(1)
            varianten = [v for v in (webp(pfad, b) for b in breiten(pfad)) if v]
            varianten = list({v[0]: v for v in varianten}.values())
            if varianten:
                tag = tag.replace(src.group(0), f'src="{varianten[-1][0]}"')
                if len(varianten) > 1 and 'srcset=' not in tag and not any(t in pfad for t in ohne_srcset):
                    # feste sizes-Angabe; „auto" nicht, weil Bilder mit Breite aus dem Seitenverhältnis sonst auf 300 px fallen
                    g = gemessen.get(stamm(pfad))
                    if g:   # gemessene Anzeigebreite (Handy 390 px / Desktop 1440 px), aufgerundet auf 10 px
                        groesse = f'(max-width: 700px) {g[0]}px, {g[1]}px'
                    else:
                        groesse = '(max-width: 700px) 150px, 280px' if '/funnels/' in pfad else '(max-width: 700px) 100vw, 50vw'
                    tag = tag.replace('<img ', f'<img srcset="{", ".join(f"{v[0]} {v[1]}w" for v in varianten)}" sizes="{groesse}" ', 1)
        # Feste Maße an jedes Bild (PageSpeed „Image elements do not have explicit width and height“, 27.09.2026):
        # das Grund-CSS img{max-width:100%} + img[width][height]{height:auto} hält das Layout dabei unverändert
        if src and not (re.search(r'\swidth=', tag) and re.search(r'\sheight=', tag)):
            try:
                q = REPO / unquote(src.group(1).lstrip('/'))
                w0, h0 = ImageOps.exif_transpose(Image.open(q)).size
                tag = re.sub(r'\s(?:width|height)="[^"]*"', '', tag)
                tag = tag.replace('<img ', f'<img width="{w0}" height="{h0}" ', 1)
            except Exception:
                pass
        # Funnel-Screenshots in den Handy-Rahmen sind nie das Wichtigste im Bild: immer lazy, niedrige Priorität
        funnel = src is not None and '/funnels/' in src.group(1)
        if (lazy or funnel) and 'loading=' not in tag: tag = tag.replace('<img ', '<img loading="lazy" ', 1)
        if funnel and 'fetchpriority=' not in tag: tag = tag.replace('<img ', '<img fetchpriority="low" ', 1)
        if 'decoding=' not in tag: tag = tag.replace('<img ', '<img decoding="async" ', 1)
        return tag

    vorn = re.sub(r'<img [^>]+>', lambda m: img(m, False), teile[0])
    rest = re.sub(r'<img [^>]+>', lambda m: img(m, True), teile[1]) if len(teile) > 1 else ''
    # Im Hero nie „später laden" (außer Funnel-Screenshots); das erste Foto ist meist das LCP-Element → hohe Priorität
    def hero_img(m):
        tag = m.group(0)
        if '/funnels/' in tag or 'logo' in tag: return tag
        return tag.replace(' loading="lazy"', '')
    vorn = re.sub(r'<img [^>]+>', hero_img, vorn)
    ganz_ = vorn + ('</section>' + rest if len(teile) > 1 else '')
    # Gemessen (bildgroessen_messen.py): Fotos, die auf DIESER Seite im ersten Bildschirm stehen, laden sofort,
    # das erste davon mit hoher Priorität — es ist meist das LCP-Element (Über uns: Noahs Porträt, 27.09.2026)
    oben = set(gemessen.get('_oben', {}).get(pfad, []))
    erstes = [True]
    def oben_img(m):
        tag = m.group(0); k = re.search(r'src="/assets/opt/(.+?)-\d+\.webp"', tag)
        if not k or k.group(1) not in oben or 'funnels' in k.group(1) or 'logo' in k.group(1): return tag
        tag = tag.replace(' loading="lazy"', '')
        if erstes[0] and 'fetchpriority=' not in tag:
            tag = tag.replace('<img ', '<img fetchpriority="high" ', 1); erstes[0] = False
        return tag
    ganz_ = re.sub(r'<img [^>]+>', oben_img, ganz_)
    vorn, _, rest = ganz_.partition('</section>')
    ganz = vorn + ('</section>' + rest if len(teile) > 1 else '')

    def ersetze(m, breite):
        v = webp(m.group(2), breite)
        return f'{m.group(1)}{v[0]}{m.group(3)}' if v else m.group(0)
    def zurueck(m):
        return f'{m.group(1)}{quellen.get(m.group(2), m.group(0))}{m.group(3)}' if m.group(2) in quellen else m.group(0)
    ganz = re.sub(r'(poster="|<link rel="preload" as="image" href="|src:\')/assets/opt/(.+?)-\d+\.webp("|\')', zurueck, ganz)
    ganz = re.sub(r'(poster=")(/[^"]+\.(?:jpe?g|png))(")', lambda m: ersetze(m, 960), ganz)
    ganz = re.sub(r'(<link rel="preload" as="image" href=")(/[^"]+\.(?:jpe?g|png))(")', lambda m: ersetze(m, max(breiten(m.group(2)))), ganz)
    # Bildlisten in Skripten (z. B. die rotierende Projekt-Galerie): dieselbe große Fassung wie im <img>
    ganz = re.sub(r"(src:')(/assets/[^']+\.(?:jpe?g|png))(')", lambda m: ersetze(m, max(breiten(m.group(2)))), ganz)
    return versionieren(ganz)


_FP = {}
def fingerabdruck(url):
    """8 Zeichen aus dem Dateiinhalt. Der Worker lässt Bilder/Videos 30 Tage im Browser liegen — ohne neuen
    Adressteil sah Noah nach einer Änderung weiter die alte Datei (27.09.2026: Irlbacher fehlte im Hero-Video)."""
    if url not in _FP:
        f = REPO / unquote(url.lstrip('/'))
        _FP[url] = hashlib.md5(f.read_bytes()).hexdigest()[:8] if f.is_file() else ''
    return _FP[url]

def versionieren(html):
    def fp(m):
        v = fingerabdruck(m.group(1))
        return f'{m.group(1)}?v={v}' if v else m.group(1)
    return re.sub(r'(/assets/[^"\'\s,)?]+\.(?:webp|jpe?g|png|mp4|svg|gif))(?!\?)', fp, html)


# ── Handgeschriebene Seite (Live-Startseite) ──────────────────────────────
GOOGLE_FONTS = re.compile(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
                          r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*'
                          r'<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">')
ALT_MESSUNG = re.compile(r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-STBDT88H69"></script>\s*'
                         r"<script>window\.dataLayer=window\.dataLayer\|\|\[\];function gtag\(\)\{dataLayer\.push\(arguments\);\}gtag\('js',new Date\(\)\);gtag\('config','G-STBDT88H69'\);\s*"
                         r"window\.__lebt = true;\s*</script>\s*"
                         r'<script src="https://t\.contentsquare\.net/uxa/99d8993a2bc41\.js"></script>')


def statische_seite(datei, gruppe='shk-live'):
    p = Path(datei); s = p.read_text(encoding='utf-8'); vorher = s
    schrift = ('<link rel="preload" href="/fonts/sub/inter-v20-latin_latin-ext-800.woff2" as="font" type="font/woff2" crossorigin>\n'
               '<link rel="preload" href="/fonts/sub/inter-v20-latin_latin-ext-regular.woff2" as="font" type="font/woff2" crossorigin>\n'
               f'<style>{fonts_css()}</style>')
    s, n1 = GOOGLE_FONTS.subn(schrift, s)
    s, n2 = ALT_MESSUNG.subn(messung_kopf(gruppe) + '\n<script>window.__lebt = true;</script>', s)
    if 'src="/messung.js' not in s:
        s = s.replace('</body>', f'<script src="/messung.js?v={messung_js_version()}" defer></script>\n</body>', 1)
    else:
        s = re.sub(r'src="/messung\.js\?v=[0-9a-f]+"', f'src="/messung.js?v={messung_js_version()}"', s)
    s = optimieren(s, ohne_srcset=('/assets/projekte/',), pfad='/')
    p.write_text(s, encoding='utf-8')
    print(f'✓ {p.name}: Google-Schriften {"ersetzt" if n1 else "schon lokal"} · Messung {"verzögert" if n2 else "schon umgestellt"} · '
          f'{"geändert" if s != vorher else "unverändert"}')


if __name__ == '__main__':
    for d in sys.argv[1:]:
        statische_seite(d)
