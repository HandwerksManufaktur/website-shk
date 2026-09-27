#!/usr/bin/env python3
"""Ladezeit + Messung für die SHK-Seiten — EINE Quelle für das Redesign (build.py) und die Live-Startseite.

Noah, 27.09.2026: „mobile speed, pagespeed, muss alles optimiert sein … hotjar … analytics" und danach
„bau analytics und hotjar auch auf die live startseite — und alles was wir da oben gemacht haben".

Aufruf für eine fertige, handgeschriebene Seite (z. B. die Live-Startseite):
    python3 neu/optimierung.py index.html
Wirkt idempotent: ein zweiter Lauf ändert nichts mehr.
"""
import re, sys, hashlib
from pathlib import Path
from urllib.parse import unquote
from PIL import Image

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
    return css_klein((REPO / 'fonts' / 'fonts.css').read_text(encoding='utf-8').replace("url('", "url('/fonts/sub/"))


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


def webp(pfad, breite):
    """Bild → WebP in assets/opt/, höchstens `breite` px breit. Gibt (url, w, h) zurück; baut nur neu, wenn die Quelle neuer ist."""
    quelle = REPO / unquote(pfad.lstrip('/'))
    if not quelle.exists():
        return None
    OPT.mkdir(exist_ok=True)
    stamm = re.sub(r'[^a-z0-9]+', '-', unquote(pfad).lower().strip('/').rsplit('.', 1)[0])
    im = Image.open(quelle); w0, h0 = im.size
    w = min(breite, w0); h = round(h0 * w / w0)
    ziel = OPT / f'{stamm}-{w}.webp'
    if not ziel.exists() or ziel.stat().st_mtime < quelle.stat().st_mtime:
        im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') else im.convert('RGB')
        im.resize((w, h), Image.LANCZOS).save(ziel, 'WEBP', quality=78, method=6)
    return f'/assets/opt/{ziel.name}', w, h


def breiten(pfad):
    p = pfad.lower()
    if 'logos' in p or '/logo' in p: return [360]                 # Logo-Kacheln ≤ 336 px
    if '/funnels/' in p: return [320, 480]                       # Funnel-Screenshots: Mini-Handy 150 px, großes Handy 280 px
    if 'rund' in p or 'poster' in p: return [640]
    return [640, 1100]                                            # Fotos: Handy + groß


def optimieren(seite, ohne_srcset=()):
    """Jedes JPG/PNG-Bild als passend großes WebP (+ srcset), alles unterhalb der ersten Sektion lazy.
    `ohne_srcset`: Pfad-Teile, deren Bilder per Skript ausgetauscht werden — srcset würde den Tausch überstimmen."""
    teile = seite.split('</section>', 1)                          # bis zum Ende der ersten Sektion = Hero, bleibt eager

    def img(m, lazy):
        tag = m.group(0)
        src = re.search(r'src="(/[^"]+\.(?:jpe?g|png))"', tag, re.I)
        if src:
            pfad = src.group(1)
            varianten = [v for v in (webp(pfad, b) for b in breiten(pfad)) if v]
            varianten = list({v[0]: v for v in varianten}.values())
            if varianten:
                tag = tag.replace(src.group(0), f'src="{varianten[-1][0]}"')
                if len(varianten) > 1 and 'srcset=' not in tag and not any(t in pfad for t in ohne_srcset):
                    # feste sizes-Angabe; „auto" nicht, weil Bilder mit Breite aus dem Seitenverhältnis sonst auf 300 px fallen
                    groesse = '280px' if '/funnels/' in pfad else '(max-width: 700px) 100vw, 50vw'
                    tag = tag.replace('<img ', f'<img srcset="{", ".join(f"{v[0]} {v[1]}w" for v in varianten)}" sizes="{groesse}" ', 1)
        if lazy and 'loading=' not in tag: tag = tag.replace('<img ', '<img loading="lazy" ', 1)
        if 'decoding=' not in tag: tag = tag.replace('<img ', '<img decoding="async" ', 1)
        return tag

    vorn = re.sub(r'<img [^>]+>', lambda m: img(m, False), teile[0])
    rest = re.sub(r'<img [^>]+>', lambda m: img(m, True), teile[1]) if len(teile) > 1 else ''
    ganz = vorn + ('</section>' + rest if len(teile) > 1 else '')

    def ersetze(m, breite):
        v = webp(m.group(2), breite)
        return f'{m.group(1)}{v[0]}{m.group(3)}' if v else m.group(0)
    ganz = re.sub(r'(poster=")(/[^"]+\.(?:jpe?g|png))(")', lambda m: ersetze(m, 960), ganz)
    ganz = re.sub(r'(<link rel="preload" as="image" href=")(/[^"]+\.(?:jpe?g|png))(")', lambda m: ersetze(m, max(breiten(m.group(2)))), ganz)
    # Bildlisten in Skripten (z. B. die rotierende Projekt-Galerie): dieselbe große Fassung wie im <img>
    ganz = re.sub(r"(src:')(/assets/[^']+\.(?:jpe?g|png))(')", lambda m: ersetze(m, max(breiten(m.group(2)))), ganz)
    return ganz


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
    s = optimieren(s, ohne_srcset=('/assets/projekte/',))
    p.write_text(s, encoding='utf-8')
    print(f'✓ {p.name}: Google-Schriften {"ersetzt" if n1 else "schon lokal"} · Messung {"verzögert" if n2 else "schon umgestellt"} · '
          f'{"geändert" if s != vorher else "unverändert"}')


if __name__ == '__main__':
    for d in sys.argv[1:]:
        statische_seite(d)
