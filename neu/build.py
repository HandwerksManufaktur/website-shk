#!/usr/bin/env python3
"""Generator der SHK-Seite v3 „Aufgedreht" — erzeugt alle Seiten aus einer Quelle.

Aufruf:  python3 neu/build.py            → schreibt nach neu/ (Vorschau unter /neu/, noindex)
         python3 neu/build.py --live     → schreibt in die Wurzel (Livegang, index)
Alle Texte und Zahlen stammen von der abgenommenen Seite (systeme/website-shk.md) — nichts erfunden.
"""
import sys, os, json, html, re, math
from pathlib import Path
from PIL import Image
from icons import IK, ic  # Icons statt Emojis (Drive-Designregel)

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
LIVE = '--live' in sys.argv
B = '' if LIVE else '/neu'            # Basis-Pfad der Seiten
AUS = REPO if LIVE else HIER          # Ausgabeordner
DOMAIN = 'https://shk.handwerksmanufaktur.digital'
NOINDEX = not LIVE

TEL = '+49 8194 7174990'; TEL_HREF = 'tel:+4981947174990'
MAIL = 'info@handwerksmanufaktur.digital'
INSTA = 'https://www.instagram.com/handwerks.manufaktur/'   # neues Konto seit 27.09.2026 (marketing/instagram/README.md)
CAL_REC = 'https://calendly.com/noahseelau/recruiting-potenzial'
CAL_LEAD = 'https://calendly.com/noahseelau/leadgen-potenzial'

def u(p):  # Seiten-Link
    return f'{B}{p}'

# ── Assets ────────────────────────────────────────────────────────────────
def css_js_version():
    import hashlib
    h = hashlib.md5((HIER/'styles.css').read_bytes() + (HIER/'main.js').read_bytes() + (REPO/'messung.js').read_bytes() + (HIER/'optimierung.py').read_bytes() + Path(__file__).read_bytes()).hexdigest()[:8]
    return h
V = css_js_version()

LOGOS = []
for f in sorted((REPO/'Logos SHK').glob('Logo *.png')):
    if 'Handwerksmanufaktur' in f.name: continue
    im = Image.open(f); r = im.width / im.height
    LOGOS.append((f'/Logos%20SHK/{f.name.replace(" ", "%20")}', f.name[5:-4].replace(' weiss','').replace(' Weiss',''), r))

LOGOBOX = {'erwin-schmidt': 'Logo Erwin Schmidt weiss.png', 'senftleben': 'Logo Senftleben Haustechnik weiss.png', 'sussmann': 'Logo Sussmann weiss.png',
           'gallenberger': 'Logo Franz Gallenberger weiss.png', 'hannes-schmidt': 'Logo Hannes Schmidt GmbH Weiss.png', 'kirchner': 'Logo Kirchner weiss.png',
           'lanzinger': 'Logo Lanzinger GmbH weiss.png', 'suessmeier': 'Logo Suessmeier Heizungstechnik weiss.png', 'ressle': 'Logo Autohaus Ressle weiss.png'}
def logos_box():
    """Jede Referenz-Kachel 336 × 120, Logo weiß, zentriert, Füllmaß 86 % × 72 % — dieselbe Regel für alle (Noah, 3× „exakt gleich groß")."""
    ziel = REPO / 'assets' / 'logos-box'; ziel.mkdir(exist_ok=True)
    W, H = 336, 120; mw, mh = int(W * .86), int(H * .72)
    for slug, quelle in LOGOBOX.items():
        im = Image.open(REPO / 'Logos SHK' / quelle).convert('RGBA'); im = im.crop(im.getbbox())
        k = min(mw / im.width, mh / im.height)
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        a = im.getchannel('A'); werte = sorted(v for v in a.getdata() if v > 40)
        ref = werte[int(len(werte) * .75)] if werte else 255  # 90. Perzentil → volle Deckkraft; dünne, weich gezeichnete Logos (Erwin Schmidt, Sussmann) standen sonst halb durchsichtig auf Nacht
        a = a.point(lambda v: min(255, round(v * 255 / ref)))
        weiss = Image.merge('RGBA', [Image.new('L', im.size, 255)] * 3 + [a])
        box = Image.new('RGBA', (W, H), (0, 0, 0, 0)); box.alpha_composite(weiss, dest=((W - im.width) // 2, (H - im.height) // 2))
        box.save(ziel / f'{slug}.png')
logos_box()


# ── Ladezeit + Messung: eine Quelle für Redesign und Live-Startseite (optimierung.py) ──
from optimierung import css_klein, fonts_css, messung_kopf, optimieren
CSS_INLINE = fonts_css() + css_klein((HIER/'styles.css').read_text(encoding='utf-8'))
MESSUNG_KOPF = messung_kopf('shk-v3')

# ── Bausteine ─────────────────────────────────────────────────────────────
NAV = [('/monteure/', IK['users'], 'Monteure'), ('/auftraege/', IK['bath'], 'Aufträge'), ('/ueber-uns/', IK['handshake'], 'Über uns')]

# Logo-Intro nur auf der Startseite: auf Unterseiten verdeckte es beim Erstbesuch den Inhalt ~2,2 s (LCP mobil 2,8–3,0 s, 27.09.2026)
INTRO = '<div id="intro" aria-hidden="true"><img src="/assets/logo-hm-quer-weiss.svg" alt="" width="340" height="91"><span class="strich"><i></i></span></div>'

def kopf(titel, beschreibung, pfad, dunkel=False, schema_extra=None, og=None):
    canon = f'{DOMAIN}{pfad}'
    robots = 'noindex, nofollow' if NOINDEX else 'index, follow, max-image-preview:large, max-snippet:-1'
    org = {
        "@type": "ProfessionalService", "@id": "https://handwerksmanufaktur.digital/#organization",
        "name": "HandwerksManufaktur", "legalName": "HANDWERKSMANUFAKTUR LTD", "url": "https://handwerksmanufaktur.digital/",
        "description": "Marketing-Agentur ausschließlich für Handwerksbetriebe im DACH-Raum. Für SHK-Betriebe: Recruiting-Kampagnen für Monteure und Anlagenmechaniker sowie Auftrags-Kampagnen für Badsanierung und Wärmepumpe.",
        "image": f"{DOMAIN}/og-image.jpg", "logo": {"@type": "ImageObject", "url": f"{DOMAIN}/assets/logo-hm-quer-schwarz-1024.png", "width": 1024, "height": 360},
        "telephone": "+4981947174990", "email": MAIL,
        "address": {"@type": "PostalAddress", "streetAddress": "Georgiou Griva Digeni 51, Athineon Building, 1st floor", "postalCode": "8047", "addressLocality": "Paphos", "addressCountry": "CY"},
        "founder": {"@type": "Person", "name": "Noah Seelau"},
        "areaServed": [{"@type": "Country", "name": "Deutschland"}, {"@type": "Country", "name": "Österreich"}, {"@type": "Country", "name": "Schweiz"}],
        "knowsAbout": ["Mitarbeitergewinnung im SHK-Handwerk", "Social Recruiting für Anlagenmechaniker SHK", "Leadgenerierung Badsanierung", "Leadgenerierung Wärmepumpe", "Marketing für Handwerksbetriebe"],
        "sameAs": ["https://handwerksmanufaktur.digital/", "https://www.instagram.com/handwerks.manufaktur/"],
    }
    graph = [org, {"@type": "WebPage", "url": canon, "name": titel, "description": beschreibung, "inLanguage": "de-DE", "isPartOf": {"@type": "WebSite", "url": f"{DOMAIN}/", "name": "HandwerksManufaktur SHK"}}]
    if schema_extra: graph += schema_extra
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    links = ''.join(f'<li><a href="{u(p)}">{ic}{n}</a></li>' for p, ic, n in NAV)
    mlinks = ''.join(f'<a href="{u(p)}">{ic}{n}</a>' for p, ic, n in NAV)
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<script>document.documentElement.classList.add('js');setTimeout(function(){{if(!window.__lebt)document.documentElement.classList.remove('js')}},3000)</script>
<meta charset="UTF-8">
<meta name="version" content="{V}">
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
<script>addEventListener('load',function(){{try{{var v='{V}';fetch('{u("/version.json")}?t='+Date.now(),{{cache:'no-store'}}).then(function(r){{return r.json()}}).then(function(j){{if(j&&j.v&&j.v!==v&&sessionStorage.getItem('shk-reload')!==j.v){{sessionStorage.setItem('shk-reload',j.v);location.replace(location.pathname+'?v='+j.v+location.hash)}}}}).catch(function(){{}})}}catch(e){{}}}})</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(titel)}</title>
<meta name="description" content="{html.escape(beschreibung)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">
<meta property="og:type" content="website"><meta property="og:locale" content="de_DE"><meta property="og:site_name" content="HandwerksManufaktur SHK">
<meta property="og:url" content="{canon}"><meta property="og:title" content="{html.escape(titel)}"><meta property="og:description" content="{html.escape(beschreibung)}">
<meta property="og:image" content="{DOMAIN}{og or '/og-image-hm.jpg'}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{'#0B1424' if dunkel else '#F3F6FA'}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<!-- Vorab nur die drei Schriften des ersten Bildschirms (Überschrift, Text, Kursiv) — acht Preloads teilten sich die Leitung, LCP wartete auf den Schrifttausch (27.09.2026) -->
<link rel="preload" href="/fonts/sub/archivo-latin-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/inter-v20-latin_latin-ext-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/instrument-serif-v5-latin_latin-ext-italic.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS_INLINE}</style>
{MESSUNG_KOPF}
<script type="application/ld+json">{ld}</script>
</head>
<body>
{INTRO if pfad == '/' else ''}
<div class="regler-leiste" aria-hidden="true"></div>
<header class="nav{' dunkel' if dunkel else ''}">
  <div class="wrap">
    <a class="nav-logo" href="{u('/')}" aria-label="HandwerksManufaktur — Startseite">
      <img class="dunkelv" src="/assets/logo-hm-quer-schwarz.svg" alt="HandwerksManufaktur" width="340" height="91">
      <img class="hell" src="/assets/logo-hm-quer-weiss.svg" alt="" width="340" height="91">
    </a>
    <nav aria-label="Hauptnavigation"><ul class="nav-links">{links}<li><a class="nav-cta" href="{u('/potenzialanalyse/')}">{ic('target')}Potenzialanalyse</a></li></ul></nav>
    <button class="burger" aria-label="Menü" aria-expanded="false" aria-controls="mobilmenu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="mobilmenu" id="mobilmenu">{mlinks}<a class="nav-cta" href="{u('/potenzialanalyse/')}">{ic('target')}Potenzialanalyse</a></div>
<main>
'''

def fuss():
    return f'''</main>
<footer class="fuss">
  <div class="wrap">
    <div class="oben">
      <div class="marke">
        <img src="/assets/logo-hm-quer-schwarz.svg" alt="HandwerksManufaktur" width="340" height="91">
        <p>Marketing für SHK-Betriebe: Monteure und Aufträge, planbar statt nach Zufall. Ein Team, ein Ansprechpartner, seit über sechs Jahren nur Handwerk.</p>
      </div>
      <div><h4>Leistungen</h4><ul>
        <li><a href="{u('/monteure/')}">{ic('users')}Monteure gewinnen</a></li>
        <li><a href="{u('/auftraege/')}">{ic('bath')}Aufträge gewinnen</a></li>
        <li><a href="{u('/potenzialanalyse/')}">{ic('target')}Potenzialanalyse</a></li>
      </ul></div>
      <div><h4>HandwerksManufaktur</h4><ul>
        <li><a href="{u('/ueber-uns/')}">{ic('handshake')}Über uns</a></li>
        <li><a href="https://handwerksmanufaktur.digital/">{ic('globe')}Webdesign für Handwerk</a></li>
      </ul></div>
      <div><h4>Kontakt</h4><ul>
        <li><a href="{TEL_HREF}">{ic('phone')}{TEL}</a></li>
        <li><a href="mailto:{MAIL}">{ic('mail')}{MAIL}</a></li>
        <li><a href="{INSTA}" target="_blank" rel="noopener">{ic('instagram')}Instagram</a></li>
      </ul></div>
    </div>
    <div class="unten"><span><i class="kante" aria-hidden="true"></i>© 2026 HandwerksManufaktur<span class="punkt"> · </span><span class="gebiet">Einsatzgebiet: Deutschland, Österreich, Schweiz</span></span><nav class="recht" aria-label="Rechtliches"><a href="{u('/impressum/')}">Impressum</a><a href="{u('/datenschutz/')}">Datenschutz</a><a href="{u('/agb/')}">AGB</a></nav></div>
  </div>
</footer>
{rechner_dialog()}
<script src="/neu/main.js?v={V}" defer></script>
<script src="/messung.js?v={V}" defer></script>
</body>
</html>
'''

GOOGLE_G = '<svg class="g" viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.6l6.7-6.7C35.6 2.6 30.2 0 24 0 14.6 0 6.5 5.4 2.6 13.3l7.8 6.1C12.3 13.5 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.6h12.7c-.6 3-2.2 5.5-4.7 7.2l7.5 5.8c4.4-4.1 7-10.1 7-17.1z"/><path fill="#FBBC05" d="M10.4 28.6A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.1.8-4.6l-7.8-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.7l7.8-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.5-5.8c-2.1 1.4-4.9 2.3-8.4 2.3-6.3 0-11.7-4-13.6-9.9l-7.8 6.1C6.5 42.6 14.6 48 24 48z"/></svg>'

def trust(hell=True):
    return f'<p class="trust"><span><span class="stern" aria-hidden="true">{ic("star","voll")*5}</span> <b>5,0</b> auf Google</span><span>·</span><span><b>130+</b> Betriebe</span><span>·</span><span><b>Spezialisiert</b> auf SHK</span></p>'

def phone(img, etikett, farbe, klasse='', delay='0s'):
    return f'''<div class="phone {klasse}" aria-hidden="true"><div class="scroller"><img src="{img}" alt="" loading="lazy" style="--d:{delay}"></div><span class="etikett"><i style="background:{farbe}"></i>{etikett}</span></div>'''

def reel_phone(f, etikett, klasse, poster=''):
    p = f' poster="/assets/reels/{poster}"' if poster else ''
    return f'''<div class="phone reel {klasse}" aria-hidden="true"><video muted loop playsinline preload="none"{p} data-quelle="/assets/reels/{f}.mp4"></video><span class="etikett"><i style="background:#3DDC84"></i>{etikett}</span></div>'''

def hero_zettel():
    z = [(IK['inbox'], 'Neue Bewerbung', 'Anlagenmechaniker SHK · 8 Jahre · 12 km', 'qualifiziert'+IK['checkmark']), (IK['bath'], 'Neue Anfrage', 'Komplettbad · EFH Bj. 1994 · Eigentümer', 'vorqualifiziert'+IK['checkmark']), (IK['inbox'], 'Neue Bewerbung', 'Kundendiensttechniker · ab sofort · 7 km', 'qualifiziert'+IK['checkmark']), (IK['flame'], 'Neue Anfrage', 'Wärmepumpe · Ölheizung Bj. 2001 · 160 m²', 'vorqualifiziert'+IK['checkmark']), (IK['inbox'], 'Neue Bewerbung', 'Bäderbauer · Führerschein BE · 15 km', 'qualifiziert'+IK['checkmark']), (IK['bath'], 'Neue Anfrage', 'Bad barrierefrei · Eigentumswohnung · zeitnah', 'vorqualifiziert'+IK['checkmark'])]
    return ''.join(f'<div class="ticket"><span class="tic">{ic}</span><span><b>{t}</b><small>{sub}</small></span><span class="ok">{ok}</span></div>' for ic, t, sub, ok in z)

def logo_band():
    """Kundenlogos laufen durch (Noah, 27.09.2026: „die Kundenlogos sollen schon trotzdem weiter durchlaufen")."""
    wand = [l for l in LOGOS if 'Ressle' not in l[1] and 'Kirchner' not in l[1]]   # beide kein SHK (Noah, 27.09.2026: „lass auch kirchner … oben bei den logos raus")
    k = next(i for i, l in enumerate(wand) if 'Kramer' in l[1]); s = next(i for i, l in enumerate(wand) if 'Suessmeier' in l[1])
    wand.append(wand.pop(k))   # Kramer ganz ans Ende der zweiten Reihe und kleiner (Noah, 27.09.2026: „noch weiter eher rechts … dass es eher direkt verschwindet und bisschen kleiner")
    def reihe(liste, rueck=''):
        kl = lambda name, r: ' class="klein"' if 'Kramer' in name else (' class=wide' if r >= 3.6 else '')
        imgs = ''.join(f'<img src="{src}" alt="{html.escape(name)}"{kl(name, r)}>' for src, name, r in liste)
        leer = ''.join(f'<img src="{src}" alt=""{kl(name, r)} aria-hidden="true">' for src, name, r in liste)
        return f'<div class="marq{rueck}">{imgs}{leer}</div>'
    halb = (len(wand) + 1) // 2
    return f'''<section class="band hell" aria-label="Betriebe, mit denen wir arbeiten">
  <div class="wrap"><div class="band-innen rv">
    <p class="band-t">Über <b>130 Betriebe</b> setzen auf uns.</p>
    {reihe(wand[:halb])}{reihe(wand[halb:], ' rueck')}
  </div></div>
</section>'''

WEGE_ALLE = [
    (IK['monitor'], 'Stellenportal', 'Sehen nur die, die gerade aktiv suchen. Wer in Arbeit ist, öffnet keins.'),
    (IK['van'], 'Aufkleber mit QR-Code', 'Auf dem Firmenwagen. Wer ihn liest, steht gerade im Stau.'),
    (IK['globe'], 'Die eigene Webseite', '„Wir suchen dich" steht bei allen. Wer es liest, sucht schon.'),
    (IK['speech'], 'Mundpropaganda', 'Kommt, wann sie will. Planen kannst du damit nichts.'),
    (IK['cards'], 'Lead-Portale', 'Dieselbe Anfrage geht an vier Betriebe gleichzeitig.'),
]
def leiter(wege=WEGE_ALLE, kick='Was du wahrscheinlich schon probiert hast', h2='Funktionieren die alten Wege <span class="em k">2026 noch?</span>', lead='Stellenportal, Aufkleber, eigene Seite: Das erreicht nur, wer gerade aktiv sucht. Das sind die wenigsten, und oft die, die alle paar Monate wechseln. Wer bleiben soll, ist in Arbeit und sucht nicht.', ende='„Hat aber nicht so wirklich was gebracht.“', von='Florian Schmidt, Erwin&nbsp;Schmidt&nbsp;&amp;&nbsp;Sohn'):
    # Bauform nach dem Hista-Vorbild (firma/referenzen/hista-digital): Kopf-Pille, eine Reihe Wege, Schiene mit ✕-Marken, Ergebnis-Pille
    knoten = ''.join(f'''<li class="weg rv" data-d="{i+1}"><div class="ic" aria-hidden="true">{ic}</div><h3><span class="strich">{t}</span></h3><p>{p}</p><span class="x" aria-hidden="true">{IK["x"]}</span></li>''' for i, (ic, t, p) in enumerate(wege))
    return f'''<section class="probiert" id="probiert">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick k rv">{kick}</p><h2 class="d rv">{h2}</h2></div><p class="lead rv">{lead}</p></div>
    <div class="leiter wege-plan n{len(wege)} rv"><div class="wp-kopf"><span>So wird bisher gesucht</span></div><ol class="wp-reihe">{knoten}</ol><div class="wp-schiene" aria-hidden="true"></div><div class="ende schlicht" data-d="{len(wege)+1}"><img class="gesicht" src="/assets/fotos/florian-neutral.jpg" alt="Florian Schmidt, Geschäftsführer Erwin Schmidt &amp; Sohn" width="400" height="400" loading="lazy"><span><b>{ende}</b><small>{von}</small></span></div></div>
  </div>
</section>'''

VERGLEICH = [
    ('team', IK['users'], 'Aufträge ablehnen', 'Bad abgesagt, weil der Monteur fehlt.', 'Bewerbungen kommen, bevor die Stelle frei wird.'),
    ('zeit', IK['clock'], 'Zu spät gesucht', 'Gesucht wird erst, wenn einer kündigt.', 'Die Anzeigen laufen durch. Der Nachfolger ist schon da.'),
    ('portal', IK['cards'], 'Portal-Leads', 'Dieselbe Anfrage ging an vier Betriebe.', 'Jede Anfrage gehört dir allein.'),
    ('last', IK['calendar'], 'Auslastung schwankt', 'Drei Wochen voll, danach Zufall.', 'Aufträge im Tempo, das dein Team stemmt.'),
    ('umkreis', IK['eye'], 'Übersehen im Umkreis', 'Guter Betrieb, nur kennt ihn keiner.', 'Dein Team auf jedem Handy im Umkreis.'),
]

def vgl_bild(art, kanal):
    """Ein Bild je Lage, links heute, rechts mit Anzeigen (Noah, 27.09.2026: „die sektion etwas optimierter bzw. auch veranschaulichter")."""
    if art == 'team':
        m = '<i class="kopf"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8.5" r="4.2"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0z"/></svg></i>'
        koepfe = m * 4 if kanal else m * 2 + '<i class="kopf leer"></i>' * 2
        chips = ('<span class="chip gut" style="--i:1">Bewerbung · Anlagenmechaniker</span><span class="chip gut" style="--i:2">Bewerbung · Kundendienst</span>' if kanal
                 else '<span class="chip schlecht" style="--i:1">Komplettbad · abgesagt</span><span class="chip schlecht" style="--i:2">Wärmepumpe · verschoben</span>')
        return f'<div class="vb vb-team"><div class="slots">{koepfe}</div><div class="chips">{chips}</div></div>'
    if art == 'zeit':
        if kanal:
            dots = ''.join(f'<circle class="pkt" style="--i:{i}" cx="{x}" cy="46" r="6"/>' for i, x in enumerate((40, 90, 140, 195, 250)))
            return ('<svg class="vb" viewBox="0 0 300 120" aria-hidden="true"><line class="achse gut" x1="10" y1="70" x2="290" y2="70"/>' + dots
                    + '<line class="mark" x1="165" y1="58" x2="165" y2="82"/><text x="165" y="106" text-anchor="middle">Kündigung</text>'
                    + '<text class="gut" x="150" y="22" text-anchor="middle">Bewerbungen laufen weiter</text></svg>')
        return ('<svg class="vb" viewBox="0 0 300 120" aria-hidden="true"><line class="achse" x1="10" y1="70" x2="110" y2="70"/>'
                '<line class="luecke" x1="110" y1="70" x2="230" y2="70"/><line class="achse" x1="230" y1="70" x2="290" y2="70"/>'
                '<circle class="rot" cx="110" cy="70" r="7"/><circle class="grau" cx="230" cy="70" r="7"/>'
                '<text x="110" y="46" text-anchor="middle">Kündigung</text><text x="230" y="46" text-anchor="middle">Suche startet</text>'
                '<text class="schlecht" x="170" y="104" text-anchor="middle">Monate ohne Monteur</text></svg>')
    if art == 'portal':
        kopf = '<svg class="vb" viewBox="0 0 300 120" aria-hidden="true"><rect class="knoten" x="8" y="46" width="92" height="28" rx="14"/><text x="54" y="65" text-anchor="middle">Anfrage</text>'
        if kanal:
            return kopf + '<line class="strahl gut" x1="100" y1="60" x2="220" y2="60"/><circle class="du" cx="248" cy="60" r="27"/><text class="du-t" x="248" y="66" text-anchor="middle">Du</text></svg>'
        ys = (16, 45, 75, 104)
        linien = ''.join(f'<line class="strahl" style="--i:{i}" x1="100" y1="60" x2="226" y2="{y}"/>' for i, y in enumerate(ys))
        betriebe = ''.join(f'<circle class="grau" cx="238" cy="{y}" r="11"/>' for y in ys)
        return kopf + linien + betriebe + '<text class="schlecht gross" x="276" y="67" text-anchor="middle">×4</text></svg>'
    if art == 'last':
        h = (68, 70, 66, 71, 69, 67, 70, 68, 71, 69) if kanal else (96, 100, 92, 34, 18, 62, 100, 28, 12, 88)
        bars = ''.join(f'<i style="--h:{v}%;--i:{i}"></i>' for i, v in enumerate(h))
        return f'<div class="vb vb-last"><div class="saeulen">{bars}<span class="soll"><em>dein Team schafft</em></span></div></div>'
    if art == 'umkreis':
        pins = ((80, 40), (220, 34), (250, 84), (70, 92), (190, 104), (120, 20), (40, 62), (262, 48), (110, 104), (205, 62))
        p = ''.join(f'<circle class="{"pin an" if (kanal or i == 0) else "pin"}" style="--i:{i}" cx="{x}" cy="{y}" r="6"/>' for i, (x, y) in enumerate(pins))
        ring = '<circle class="ring" cx="150" cy="62" r="118"/><circle class="ring" cx="150" cy="62" r="66"/>' if kanal else ''
        return f'<svg class="vb" viewBox="0 0 300 124" aria-hidden="true">{ring}{p}<circle class="haus{" an" if kanal else ""}" cx="150" cy="62" r="11"/></svg>'
    return ''

W3F_KEY = '9a4e6ba4-58e9-4782-8953-e53eed867640'   # derselbe Web3Forms-Zugang wie auf handwerksmanufaktur.digital, geht an info@

def rechner_dialog():
    """Potenzial-Rechner als Pop-up (Noah, 27.09.2026: „der rechner kommt dann, wenn sie auf potenzial durchrechnen gehen …
    die tragen immer nur dann eine sache ein, müssen dann noch plz eingeben und dann name … abschicken … wie so nen cta")."""
    def wahl(schritt, werte):
        return '<div class="rd-wahl">' + ''.join(f'<button type="button" data-feld="{schritt}" data-wert="{w}">{l}</button>' for w, l in werte) + '</div>'
    return f'''<dialog class="rd" id="rechner-dialog" aria-labelledby="rd-titel">
  <form class="rd-form" novalidate>
    <input type="hidden" name="access_key" value="{W3F_KEY}"><input type="hidden" name="subject" value="Neue Potenzial-Anfrage über shk.handwerksmanufaktur.digital"><input type="hidden" name="from_name" value="SHK-Seite · Potenzial-Rechner"><input type="checkbox" name="botcheck" class="sr" tabindex="-1" autocomplete="off">
    <div class="rd-kopf"><p class="rd-kick" id="rd-titel">{ic('target','ic')}Potenzial durchrechnen</p><button type="button" class="rd-zu" aria-label="Schließen">{IK['x']}</button></div>
    <div class="rd-balken" aria-hidden="true"><i></i></div>
    <section class="rd-schritt an" data-schritt="1"><h3>Was fehlt dir gerade?</h3>{wahl('ziel', [('Monteure', ic('users','ic')+'Monteure'), ('Aufträge', ic('bath','ic')+'Aufträge')])}</section>
    <section class="rd-schritt" data-schritt="2" hidden><h3 data-text-monteure="Welche Stelle ist offen?" data-text-auftraege="Welche Aufträge willst du mehr?">Welche Stelle ist offen?</h3>
      <div data-fuer="Monteure">{wahl('stelle', [('Anlagenmechaniker SHK', 'Anlagenmechaniker SHK'), ('Kundendiensttechniker', 'Kundendiensttechniker'), ('Bäderbauer', 'Bäderbauer'), ('Andere Stelle', 'Andere Stelle')])}</div>
      <div data-fuer="Aufträge" hidden>{wahl('stelle', [('Badsanierung', 'Badsanierung'), ('Wärmepumpe', 'Wärmepumpe'), ('Heizung', 'Heizung'), ('Mehreres', 'Mehreres')])}</div></section>
    <section class="rd-schritt" data-schritt="3" hidden><h3 data-text-monteure="Wie viele Aufträge lehnst du im Monat ab, weil ein Monteur fehlt?" data-text-auftraege="Wie viele Aufträge mehr im Monat könnte dein Team bauen?">Wie viele Aufträge lehnst du im Monat ab?</h3>{wahl('anzahl', [('1', '1'), ('2', '2–3'), ('4', '4–5'), ('6', '6 oder mehr')])}</section>
    <section class="rd-schritt" data-schritt="4" hidden><h3>Was ist ein Auftrag bei dir im Schnitt wert?</h3>{wahl('wert', [('5000', '5.000 €'), ('10000', '10.000 €'), ('20000', '20.000 €'), ('35000', '35.000 € +')])}</section>
    <section class="rd-schritt" data-schritt="5" hidden><div class="rd-ergebnis"><small data-text-monteure="Liegen bei dir jeden Monat" data-text-auftraege="Wären jeden Monat zusätzlich drin">Liegen bei dir jeden Monat</small><b data-summe>0 €</b><p data-beleg-monteure="Bei Erwin Schmidt &amp; Sohn kamen 25 Bewerbungen in 4 Wochen, bei Senftleben Haustechnik 21 in 18 Tagen." data-beleg-auftraege="Bei Senftleben Haustechnik kamen 21 Bad-Anfragen in 2 Monaten, bei Sussmann der erste Auftrag nach 2 Wochen."></p><span class="rd-fuss">Rechenbeispiel mit deinen Angaben, keine Zusage.</span></div>
      <button type="button" class="btn btn-ink rd-weiter" data-weiter>Für meinen Umkreis prüfen lassen <span aria-hidden="true">→</span></button></section>
    <section class="rd-schritt" data-schritt="6" hidden><h3>Wo sitzt dein Betrieb?</h3><label class="rd-feld"><span>PLZ oder Ort</span><input name="plz" autocomplete="postal-code" inputmode="text" placeholder="z. B. 89584 Ehingen" required></label><button type="button" class="btn btn-ink rd-weiter" data-weiter>Weiter <span aria-hidden="true">→</span></button></section>
    <section class="rd-schritt" data-schritt="7" hidden><h3>Wie erreichen wir dich?</h3>
      <label class="rd-feld"><span>Name</span><input name="name" autocomplete="name" required></label>
      <label class="rd-feld"><span>Betrieb</span><input name="betrieb" autocomplete="organization"></label>
      <label class="rd-feld"><span>Telefon</span><input name="telefon" type="tel" autocomplete="tel" required></label>
      <label class="rd-feld"><span>E-Mail <em>(optional)</em></span><input name="email" type="email" autocomplete="email"></label>
      <p class="rd-hinweis">Mit dem Absenden meldet sich Noah bei dir wegen deines Umkreises. Deine Angaben nutzen wir nur dafür, mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p>
      <p class="rd-fehler" hidden>Bitte Name und Telefon ausfüllen.</p>
      <button type="submit" class="btn btn-ink rd-weiter">{ic('target','ic')}Abschicken</button></section>
    <section class="rd-schritt" data-schritt="8" hidden><div class="rd-danke"><span class="rd-ok">{IK['checkmark']}</span><h3>Danke, ist angekommen.</h3><p>Noah meldet sich in der Regel am selben oder nächsten Werktag bei dir. Lieber gleich einen Termin wählen?</p><a class="btn btn-ink" data-cal href="{CAL_REC}" target="_blank" rel="noopener">Termin wählen <span aria-hidden="true">→</span></a></div></section>
    <button type="button" class="rd-zurueck" hidden>← Zurück</button>
  </form>
</dialog>'''

def vergleich():
    tabs = ''.join(f'<button type="button" class="vgl-tab{" an" if i == 0 else ""}" role="tab" id="vgl-t{i}" aria-controls="vgl-p{i}" aria-selected="{"true" if i == 0 else "false"}"><span class="ic" aria-hidden="true">{icn}</span><b>{t}</b><i class="lauf" aria-hidden="true"></i></button>' for i, (a, icn, t, h, k) in enumerate(VERGLEICH))
    panels = ''.join(f'''<div class="vgl-panel{" an" if i == 0 else ""}" role="tabpanel" id="vgl-p{i}" aria-labelledby="vgl-t{i}"{"" if i == 0 else " hidden"}>
      <div class="vgl-seite heute"><span class="vgl-etikett">{IK["x"]}Heute</span>{vgl_bild(a, False)}<p>{h}</p></div>
      <div class="vgl-seite kanal"><span class="vgl-etikett">{IK["checkmark"]}Mit eigenen Anzeigen</span>{vgl_bild(a, True)}<p>{k}</p></div>
    </div>''' for i, (a, icn, t, h, k) in enumerate(VERGLEICH))
    return f'''<section class="vergleich" id="vergleich">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick k rv">Erkennst du dich wieder?</p><h2 class="d rv">Heute Zufall. <span class="em w">Morgen</span> planbar.</h2></div><p class="lead rv">Fünf Lagen aus Gesprächen mit SHK-Inhabern. Tipp auf deine.</p></div>
    <div class="vgl-buehne rv"><div class="vgl-tabs" role="tablist" aria-label="Lagen">{tabs}</div><div class="vgl-panels">{panels}</div></div>
    <p class="rv" style="margin-top:28px"><button type="button" class="btn btn-ink" data-rechner>{ic('target','ic')}Potenzial durchrechnen</button></p>
  </div>
</section>'''

TICKETS_REC = [(IK['users'], 'Anlagenmechaniker SHK', '8 Jahre Erfahrung · Führerschein B · 12 km entfernt', 'qualifiziert'+IK['checkmark']), (IK['wrench'], 'Kundendiensttechniker', 'Heizung &amp; Sanitär · ab sofort · 7 km entfernt', 'qualifiziert'+IK['checkmark']), (IK['users'], 'Geselle SHK', '3 Jahre Erfahrung · wechselwillig · 20 km entfernt', 'qualifiziert'+IK['checkmark']), (IK['bath'], 'Bäderbauer', 'Komplettbäder · Führerschein BE · 15 km entfernt', 'qualifiziert'+IK['checkmark'])]
TICKETS_LEAD = [(IK['bath'], 'Komplettbad', 'EFH · Baujahr 1994 · Eigentümer · Start im Frühjahr', 'vorqualifiziert'+IK['checkmark']), (IK['flame'], 'Wärmepumpe', 'Ölheizung Bj. 2001 · 160 m² · Eigentümer', 'vorqualifiziert'+IK['checkmark']), (IK['bath'], 'Bad barrierefrei', 'Bodengleiche Dusche · Eigentumswohnung · zeitnah', 'vorqualifiziert'+IK['checkmark']), (IK['flame'], 'Heizungstausch', 'Gas raus, Wärmepumpe rein · EFH · Förderung geklärt', 'vorqualifiziert'+IK['checkmark'])]
def tickets(liste):
    return '<div class="tickets" aria-hidden="true">' + ''.join(f'<div class="ticket" style="--d:{i*.12:.2f}s"><span class="tic">{ic}</span><span><b>{t}</b><small>{s}</small></span><span class="ok">{ok}</span></div>' for i, (ic, t, s, ok) in enumerate(liste)) + '</div>'

UMKREIS = '''<svg class="umkreis" viewBox="0 0 320 320" aria-hidden="true">
  <circle class="r" cx="160" cy="160" r="60"/><circle class="r" cx="160" cy="160" r="100"/><circle class="r aktiv" cx="160" cy="160" r="140"/>
  <circle class="puls" cx="160" cy="160" r="140"/>
  <circle class="pin" cx="110" cy="120" r="5"/><circle class="pin" cx="205" cy="95" r="5"/><circle class="pin" cx="240" cy="180" r="5"/><circle class="pin" cx="120" cy="230" r="5"/><circle class="pin" cx="190" cy="250" r="5"/><circle class="pin" cx="70" cy="170" r="5"/>
  <circle class="haus" cx="160" cy="160" r="9"/>
</svg>'''

def system(mixed=True):
    tk = TICKETS_REC[:2] + TICKETS_LEAD[:2] if mixed else TICKETS_REC
    return f'''<section class="system" id="system">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick w rv">So wird es warm</p><h2 class="d rv">Ein eigener Kanal. <span class="em w">Deine</span> Anfragen, <span class="em w">deine</span> Bewerber.</h2></div><p class="lead rv">Reichweite hat jedes Portal. Was fehlt, ist Relevanz: Anzeigen, die im Umkreis erkannt werden, weil deine Leute drauf sind. Für Monteure und Aufträge derselbe Ablauf, in unter zwei Wochen live.</p></div>
    <div class="bento">
      <article class="zelle z-a hoch rv"><div class="bild"><img src="/assets/fotos/klass-team-van.jpg" alt="Team eines SHK-Betriebs vor dem Firmenwagen — Shooting für die Kampagne" loading="lazy" width="1100" height="732" style="object-position:50% 30%"></div><span class="nr">01</span><h3>Anzeigen mit Fotos aus deinem Betrieb</h3><p>„Wir suchen dich" mit Stockfoto wird gesehen und ignoriert. Deine Leute, dein Lager, dein Firmenwagen erkennt man im Umkreis. Für das Shooting kommen wir zu dir.</p></article>
      <article class="zelle z-b hoch mit-panels rv" data-d="1"><div class="mini-phones" aria-hidden="true"><div class="mini-phone" style="--off:0%"><img src="/assets/funnels/erwin-schmidt-jobs-full.jpg" alt="" loading="lazy"></div><div class="mini-phone" style="--off:31%"><img src="/assets/funnels/senftleben-jobs-full.jpg" alt="" loading="lazy"></div><div class="mini-phone" style="--off:62%"><img src="/assets/funnels/senftleben-leadgen-full.jpg" alt="" loading="lazy"></div></div><span class="nr">02</span><h3>Filterfragen vor der Bewerbung</h3><p>Bewerbung in 60 Sekunden, ohne Lebenslauf: Gewerk, Erfahrung, Führerschein. Bei Aufträgen Objekt, Baujahr, Eigentum, Zeitrahmen. Wer nicht passt, hört vorher auf.</p></article>
      <article class="zelle z-c rv" data-d="2">{UMKREIS}<span class="nr">03</span><h3>Nur dein Einzugsgebiet</h3><p>Läuft auf deinen Namen, bespielt nur deinen Umkreis. Jede Anfrage gehört dir allein, nicht vier Wettbewerbern gleichzeitig.</p></article>
      <article class="zelle z-d mit-tickets rv" data-d="3">{tickets(tk)}<span class="nr">04</span><h3>So kommt es bei dir an</h3><p>Mit Kontaktdaten und vorgeprüft, im Postfach. Die ersten oft schon 24 Stunden nach dem Start. Du rufst zurück, wen du sehen willst.</p></article>
      <article class="zelle z-e rv" data-d="4"><div class="bild"><img src="/assets/fotos/shk-02.jpg" alt="Inhaber und Mitarbeiter am Laptop" loading="lazy" width="1100" height="732" style="object-position:50% 30%"></div><span class="nr">05</span><h3>Wir sehen, was jede Anfrage kostet</h3><p>Was funktioniert, bekommt mehr Budget. Auf Wunsch gedrosselt auf ein, zwei Aufträge im Monat.</p></article>
    </div>
  </div>
</section>'''

def hebel():
    return f'''<section class="hebel" id="hebel">
  <div class="wrap">
    <div class="sec-kopf mitte"><p class="kick rv">Zwei Hebel, ein System</p><h2 class="d rv">Was fehlt dir gerade: <span class="em k">Leute</span> oder <span class="em w">Aufträge</span>?</h2></div>
    <div class="hebel-grid">
      <a class="hebel-karte rv" href="{u('/monteure/')}"><div class="txt"><span class="chip">{ic('users')}Hebel 1 · Recruiting</span><h3>Mitarbeitergewinnung für SHK-Monteure.</h3><ul><li>{ic("checkmark")}Bewerbung in 60 Sekunden, ohne Lebenslauf</li><li>{ic("checkmark")}Vorqualifiziert: Gewerk, Erfahrung, Führerschein</li><li>{ic("checkmark")}Dein Betrieb als Marke, mit Fotos aus deinem Betrieb</li></ul><span class="btn btn-white">Recruiting ansehen <span aria-hidden="true">→</span></span></div><div class="bild"><img src="/assets/fotos/klass-hebel-monteure.jpg" alt="Monteur von Heizung Sanitär Klaß am Firmenwagen" loading="lazy" width="1920" height="1277" style="object-position:62% 40%"></div></a>
      <a class="hebel-karte w rv" data-d="1" href="{u('/auftraege/')}"><div class="txt"><span class="chip">{ic('bath')}Hebel 2 · Aufträge</span><h3>Auftrags-Funnel für Bad &amp; Wärmepumpe.</h3><ul><li>{ic("checkmark")}Exklusiv für deinen Betrieb</li><li>{ic("checkmark")}Vorqualifiziert: Objekt, Baujahr, Eigentum, Zeitrahmen</li><li>{ic("checkmark")}Regelbar, auf Wunsch nur 1–2 Aufträge im Monat</li></ul><span class="btn btn-white">Aufträge ansehen <span aria-hidden="true">→</span></span></div><div class="bild"><img src="/assets/fotos/klass-hebel-auftraege.jpg" alt="Planung vor Ort mit dem Team von Heizung Sanitär Klaß" loading="lazy" width="1920" height="1280" style="object-position:45% 35%"></div></a>
    </div>
  </div>
</section>'''

ESS_LOGO = '/assets/logos-box/erwin-schmidt.png'
SEN_LOGO = '/assets/logos-box/senftleben.png'
SUS_LOGO = '/assets/logos-box/sussmann.png'

ICON = {'Bewerbungen': IK['inbox'], 'Stelle besetzt': IK['check'], 'Wochen Laufzeit': IK['clock'], 'Aufrufe im Umkreis': IK['eye'], 'Bad-Anfragen': IK['bath'], 'Vor-Ort-Termine': IK['pin'], 'Erster Auftrag': IK['euro'], 'Tage Kampagne': IK['clock'], 'Stelle: Lohn &amp; Buchhaltung': IK['check'], 'Aufrufe im 25-km-Umkreis': IK['eye'], 'Bad-Anfragen über den Funnel': IK['bath'], 'Vor-Ort-Termine in 2 Monaten': IK['pin'], 'Wochen Kampagnen-Laufzeit': IK['clock'], 'Stelle besetzt: Anlagenmechaniker SHK': IK['check'], 'Auftrag: Teilsanierung Bad': IK['euro']}
def zahl_html(b, s, k):
    ic = ICON.get(s, '')
    zi = f'<span class="zi" aria-hidden="true">{ic}</span>' if ic else ''
    return f'<div class="zahl {k}">{zi}<b>{b}</b><small>{s}</small></div>'

def fall_karte(logo, name, ort, chip, chipk, poster, video, dauer, zitat, zahlen, zeit, d=0, alt=''):
    pos = '8%' if 'senftleben' in poster else '50%'
    z = ''.join(zahl_html(b, s, chipk) for b, s in zahlen)
    return f'''<article class="fall-karte rv" data-d="{d}">
  <div class="vid"><video preload="none" poster="{poster}" playsinline style="object-position:50% {pos}"><source src="{video}" type="video/mp4">Dein Browser kann dieses Video nicht abspielen.</video><button class="play" type="button" aria-label="Video ansehen"><span>{ic("play","voll")} Video ansehen · {dauer}</span></button></div>
  <div class="txt">
    <span class="chip {chipk}"><i aria-hidden="true"></i>{chip}</span>
    <p class="erg">{zitat}</p>
    <div class="betrieb"><span class="lg"><img src="{logo}" alt="{html.escape(name)}"></span><span><b>{name}</b></span></div>
    <div class="zahlen">{z}</div>
  </div>
</article>'''


KAL_SEN = [1,3,4,7,9,12,13,16,18,19,22,24,25,28,30,31,34,36,37,40,41]  # 21 von 42 Werktagen (Juli + August)
def kaskade(variante='senftleben'):
    if variante == 'senftleben':
        kick, h2, lead, k = 'Ein Betrieb, 42 Werktage', 'Jeder zweite Werktag <span class="em w">brachte eine Bad-Anfrage.</span>', 'Senftleben Haustechnik in Ehingen, Juli und August. Anzeigen im 25-Kilometer-Umkreis, Anfragen aus dem Werbekonto, Termine aus dem CRM.', 'w'
        stufen = [(100, '125000', '', '125.000', 'Mal im Umkreis ausgespielt', 'Anzeigen auf Instagram und Facebook, 25 Kilometer um den Betrieb.', '2 Monate'),
                  (46, '21', '', '21', 'Bad-Anfragen kamen an', 'Nach vier Filterfragen: Projektart, Zeitrahmen, Größe, Kontakt. Wer nicht passt, hört vorher auf.', '2 Monate'),
                  (24, '10', '+', '10+', 'Vor-Ort-Termine daraus', 'Benjamin Senftleben stand bei mehr als zehn dieser Anfragen im Bad.', '2 Monate')]
        tage, an, marke, kal_text, vorher = 42, KAL_SEN, 'Juli &amp; August', 'von 42 Werktagen brachten eine Anfrage, jeder zweite', 'Empfehlung, Stammkunden, Zufall'
        fuss = 'Eine Anfrage wurde abgesagt, weil sie über eine halbe Stunde entfernt lag.'
    else:
        kick, h2, lead, k = 'Ein Betrieb, 20 Werktage', 'An jedem Werktag <span class="em k">mindestens eine Bewerbung.</span>', 'Erwin Schmidt &amp; Sohn in Sindelfingen, vier Wochen Kampagne für einen Anlagenmechaniker im Kundendienst. Bewerbungen aus dem Funnel, Einstellung vom Betrieb bestätigt.', 'k'
        stufen = [(100, '25', '', '25', 'Bewerbungen kamen an', 'Über den Funnel, ohne Lebenslauf, mit Kontaktdaten und Antworten auf die Filterfragen.', '4 Wochen'),
                  (8, '1', '', '1', 'Stelle besetzt', 'Ein Anlagenmechaniker SHK, eingestellt aus diesen Bewerbungen.', '4 Wochen')]
        tage, an, marke, kal_text, vorher = 20, list(range(20)), '4 Wochen', 'Werktage, an jedem kam mindestens eine Bewerbung', 'Aufkleber am Firmenwagen, Stelle auf der eigenen Seite'
        fuss = 'Eine zweite Einstellung kam über einen anderen Weg und zählt hier nicht.'
    st = ''.join(f'<li class="k-stufe rv" data-d="{i}" style="--b:{b}"><span class="k-zahl nr" data-zahl="{z}" data-nach="{n}">{t}</span><span class="k-text"><b>{tt}</b><small>{sm}</small></span><span class="k-zeit">{zt}</span><i class="k-balken"></i></li>' for i, (b, z, n, t, tt, sm, zt) in enumerate(stufen))
    raster = ''.join(f'<i class="an" data-rang="{an.index(i)}"></i>' if i in an else '<i></i>' for i in range(tage))
    return f'''<section class="sec kaskade-sek" id="kaskade"><div class="wrap">
    <div class="sec-kopf"><div><p class="kick {k} rv">{kick}</p><h2 class="d rv">{h2}</h2></div><p class="lead rv">{lead}</p></div>
    <div class="kal-tafel {k} rv" data-kalender data-treffer="{len(an)}"><div class="kal-kopf"><div><span class="kal-nr">0</span><small>{kal_text}</small></div><span class="kal-marke">{marke}</span></div><div class="kal-raster n{tage}" aria-hidden="true">{raster}</div><div class="kal-fuss"><span><b>Vorher</b> {vorher}</span><span class="kal-stand">Scroll weiter, dann füllen sich die Tage</span></div></div>
    <p class="fussnote rv">{fuss}</p>
  </div></section>'''

def fallstudien_teaser():
    return f'''<section class="fall" id="fallstudien">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick rv">Fallstudien</p><h2 class="d rv">Wir lassen unsere <span class="em w">Kunden sprechen.</span></h2></div><p class="lead rv">Ein Anlagenmechaniker in 4&nbsp;Wochen, 21&nbsp;Bad-Anfragen in 2&nbsp;Monaten, ein Auftrag über 10.000&nbsp;€ nach 14&nbsp;Tagen. Die Zahlen stammen aus den laufenden Kampagnen.</p></div>
    <div class="fall-grid drei">
      {fall_karte(ESS_LOGO, 'Erwin Schmidt &amp; Sohn', 'Sindelfingen · SHK-Familienbetrieb in 3. Generation', 'Recruiting · läuft', '', '/assets/testimonial/ess-testimonial-poster.jpg', '/assets/testimonial/ess-testimonial.mp4', '2:48', '25 Bewerbungen, 1 Anlagenmechaniker eingestellt, in 4 Wochen.', [('25', 'Bewerbungen'), ('1', 'Stelle besetzt'), ('4', 'Wochen Laufzeit')], 'Florian Schmidt, Geschäftsführer · Zahlen aus den ersten 4 Wochen')}
      {fall_karte(SEN_LOGO, 'Senftleben Haustechnik', 'Ehingen (Donau) · Badsanierung in 3. Generation', 'Badsanierung · läuft', 'w', '/assets/testimonial/senftleben-testimonial-poster.jpg', '/assets/testimonial/senftleben-testimonial.mp4', '2:22', '21 Bad-Anfragen und 10+ Vor-Ort-Termine in 2 Monaten.', [('125.000', 'Aufrufe im Umkreis'), ('21', 'Bad-Anfragen'), ('10<span class="plus">+</span>', 'Vor-Ort-Termine')], 'Benjamin Senftleben, Inhaber · Zahlen aus den ersten 2 Monaten', 1)}
      {sussmann_karte(2)}
    </div>
  </div>
</section>'''

def fall_gross(logo, name, rolle, betrieb, poster, video, dauer, zitat, absatz, zahlen, chipk, aria, pos='50% 40%'):
    z = ''.join(zahl_html(b, s, chipk) for b, s in zahlen)
    if not video:   # Fallstudie ohne Inhaber-Video: scharfes Foto aus dem Shooting (Noah, 27.09.2026)
        return f'''<article class="fall-gross rv">
  <div class="vid bild-nur"><img src="{poster}" alt="{aria}" loading="lazy" width="1600" height="1067" style="object-position:{pos}"></div>
  <div class="txt">
    <div><blockquote>{zitat}</blockquote><p style="margin-top:18px">{absatz}</p></div>
    <div class="zahlen">{z}</div>
    <div class="person"><img src="{logo}" alt="{html.escape(betrieb)}"><span><b>{name}</b>{rolle}</span></div>
  </div>
</article>'''
    return f'''<article class="fall-gross rv">
  <div class="vid"><video preload="none" poster="{poster}" playsinline aria-label="{aria}" style="object-position:{'50% 8%' if 'senftleben' in poster else ('96% 50%' if 'ess-' in poster else '50% 50%')}"><source src="{video}" type="video/mp4">Dein Browser kann dieses Video nicht abspielen.</video><button class="play" type="button" aria-label="Video ansehen"><span>{ic("play","voll")} Video ansehen · {dauer}</span></button></div>
  <div class="txt">
    <div><blockquote>{zitat}</blockquote><p style="margin-top:18px">{absatz}</p></div>
    <div class="zahlen">{z}</div>
    <div class="person"><img src="{logo}" alt="{html.escape(betrieb)}"><span><b>{name}</b>{rolle}</span></div>
  </div>
</article>'''

FALL_ESS = lambda: fall_gross(ESS_LOGO, 'Florian Schmidt', 'Geschäftsführer, Erwin Schmidt &amp; Sohn GmbH, Sindelfingen', 'Erwin Schmidt & Sohn', '/assets/testimonial/ess-testimonial-poster.jpg', '/assets/testimonial/ess-testimonial.mp4', '2:48', '„Ich kann es jedem nur empfehlen: Wenn wirklich Personalmangel da ist, dass man den Schritt geht.“', 'Erwin Schmidt &amp; Sohn in Sindelfingen, SHK-Familienbetrieb in dritter Generation, suchte einen Anlagenmechaniker für den Kundendienst. Probiert war schon einiges: Aufkleber mit QR-Code auf den Firmenwagen, die Stelle auf der eigenen Webseite. Gebracht hat das wenig. Dann liefen 4 Wochen lang Anzeigen im Umkreis, mit Fotos aus dem Betrieb und Filterfragen vor der Bewerbung.', [('25', 'Bewerbungen'), ('4', 'Wochen Kampagnen-Laufzeit'), ('1', 'Stelle besetzt: Anlagenmechaniker SHK')], '', 'Fallstudie Erwin Schmidt & Sohn: 25 Bewerbungen in 4 Wochen')
FALL_SEN = lambda: fall_gross(SEN_LOGO, 'Benjamin Senftleben', 'Inhaber, Senftleben Haustechnik, Ehingen', 'Senftleben Haustechnik', '/assets/testimonial/senftleben-testimonial-poster.jpg', '/assets/testimonial/senftleben-testimonial.mp4', '2:22', '„Also die Zusammenarbeit würde ich auf jeden Fall jedem empfehlen, weil das auch immer unkompliziert ist.“', '„Aufträge haben wir jetzt aktuell genügend“, sagt Benjamin Senftleben. Sein Meisterbetrieb in Ehingen, dritte Generation, ist ausgelastet. Trotzdem laufen seit Juli Anzeigen für Badsanierung im Umkreis von 25 km, mit ihm selbst vor der Kamera und Filterfragen vor der Anfrage. Nach dem Startpaket hat er verlängert, damit der Name im Kopf bleibt, wenn das nächste Bad ansteht. Werbung macht man nicht nur, wenn es gut läuft. Das hat er schon in der Meisterschule gelernt.', [('125.000', 'Aufrufe im 25-km-Umkreis'), ('21', 'Bad-Anfragen über den Funnel'), ('10<span class="plus">+</span>', 'Vor-Ort-Termine in 2 Monaten')], 'w', 'Fallstudie Senftleben Haustechnik: 21 Bad-Anfragen in 2 Monaten')

FALL_SUS = lambda: fall_gross(SUS_LOGO, 'Patrick Wähnl', 'Geschäftsführer, Erich Sussmann GmbH, Kirchheim bei München', 'Erich Sussmann GmbH', '/assets/fotos/sussmann-empfang-nah.jpg', '', '', '„So sind wir super zufrieden.“', 'Erich Sussmann ist Meisterbetrieb für Heizung, Sanitär und Klima in Kirchheim bei München. Seit Anfang September laufen Anzeigen für Badsanierung im Umkreis von 30 km, mit Patrick und Mirjana vor der Kamera und Filterfragen vor jeder Anfrage. „Am Anfang war es extrem“, sagt Patrick über die ersten Tage. Nach zwei Wochen kam der erste Auftrag. Als Nächstes folgen Wärmepumpe und Klima, vor der Heizperiode.', [('14', 'Bad-Anfragen'), ('7<span class="plus">+</span>', 'Vor-Ort-Termine'), ('10.000&nbsp;€', 'Erster Auftrag nach 2 Wochen')], 'w', 'Patrick und Mirjana Wähnl am Empfang der Erich Sussmann GmbH', '40% 35%')
FALL_SEN_REC = lambda: fall_gross(SEN_LOGO, 'Benjamin Senftleben', 'Inhaber, Senftleben Haustechnik, Ehingen', 'Senftleben Haustechnik', '/assets/fotos/senftleben-team-2026.jpg', '', '', '„21 Bewerbungen in 18 Tagen, diesmal fürs Büro.“', 'Nach dem Auftrags-Funnel ging Senftleben Haustechnik denselben Weg für eine Stelle in Lohn- und Buchhaltung: Anzeigen im Umkreis, mit dem eigenen Team im Bild, Bewerbung in 60 Sekunden ohne Lebenslauf. Nach 18 Tagen lagen 21 Bewerbungen vor, die Stelle ist besetzt.', [('21', 'Bewerbungen'), ('18', 'Tage Kampagne'), ('1', 'Stelle: Lohn &amp; Buchhaltung')], 'k', 'Das Team von Senftleben Haustechnik im Lager', '50% 40%')

def senftleben_recruiting_karte():
    return f'''<a class="fall-karte klickbar rv" data-d="1" href="{u('/fallstudien/')}#senftleben-recruiting">
  <div class="vid"><img src="/assets/fotos/senftleben-team-2026.jpg" alt="Das Team von Senftleben Haustechnik" loading="lazy" width="1600" height="1060" style="object-position:50% 40%"></div>
  <div class="txt"><span class="chip"><i aria-hidden="true"></i>Recruiting · läuft</span><p class="erg">21 Bewerbungen in 18 Tagen, diesmal fürs Büro.</p><p style="color:var(--sub);font-size:14px;margin-top:-6px">Nach dem Auftrags-Funnel sucht Senftleben Haustechnik über denselben Weg eine Stelle in Lohn- und Buchhaltung.</p>
  <div class="betrieb"><span class="lg"><img src="{SEN_LOGO}" alt="Senftleben Haustechnik"></span><span><b>Senftleben Haustechnik</b><small>Ehingen (Donau) · Recruiting</small></span></div>
  <div class="zahlen"><div class="zahl"><b>21</b><small>Bewerbungen</small></div><div class="zahl"><b>18</b><small>Tage Kampagne</small></div><div class="zahl"><b>1</b><small>Stelle: Lohn &amp; Buchhaltung</small></div></div><p class="zeit">Stand 22.09.2026</p></div>
<span class="mehr">Zur Fallstudie <span aria-hidden="true">→</span></span></a>'''

def sussmann_karte(d=1):
    return f'''<article class="fall-karte rv" data-d="{d}">
  <div class="vid"><img src="/assets/fotos/sussmann-empfang-quer.jpg" alt="Patrick und Mirjana Wähnl am Empfang der Erich Sussmann GmbH" loading="lazy" width="1600" height="900" style="object-position:40% 30%"></div>
  <div class="txt">
    <span class="chip w"><i aria-hidden="true"></i>Badsanierung · läuft</span>
    <p class="erg">14 Bad-Anfragen, 7+ Termine, erster Auftrag 10.000 € nach 2 Wochen.</p>
    <div class="betrieb"><span class="lg"><img src="{SUS_LOGO}" alt="Sussmann GmbH"></span><span><b>Sussmann GmbH</b></span></div>
    <div class="zahlen">{zahl_html('14', 'Bad-Anfragen', 'w')}{zahl_html('7<span class="plus">+</span>', 'Vor-Ort-Termine', 'w')}{zahl_html('10.000&nbsp;€', 'Erster Auftrag', 'w')}</div>
  </div>
</article>'''

REELS = [('patrick-reel', 'Patrick'), ('josef', 'Josef'), ('mirjana-hook', 'Mirjana'), ('meike-solo', 'Meike'), ('benjamin-schirm', 'Benjamin')]
def reels():
    r = ''.join(f'<figure class="reel rv" data-d="{i+1}"><video muted loop playsinline preload="none" data-quelle="/assets/reels/{f}.mp4" aria-label="Ausschnitt aus einer laufenden Kampagne"></video><figcaption>{n}</figcaption></figure>' for i, (f, n) in enumerate(REELS))
    return f'''<section class="reels" id="reels">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick rv">Aus der Praxis</p><h2 class="d rv">Direkt im Betrieb <span class="em w">gedreht.</span></h2></div><p class="lead rv">Inhaber und Monteure unserer Kunden vor der Kamera. Genau so laufen die Anzeigen im Feed.</p></div>
    <div class="reel-reihe">{r}</div>
  </div>
</section>'''

STIMMEN = [
    ('Franz Gallenberger', 'Sanitär · Heizung · Klimatechnik', '„(…) Vom ersten Kontakt bis zur Umsetzung hat wirklich alles wunderbar funktioniert. Die Beratung war kompetent, verständlich und stets auf unsere individuellen Wünsche abgestimmt. (…) Das Ergebnis hat unsere Erwartungen nicht nur erfüllt, sondern sogar übertroffen. (…)“'),
    ('Benjamin Senftleben', 'Senftleben Haustechnik, Ehingen', '„(…) Wir sind sehr zufrieden! Auch der Kontakt mit Noah ist immer freundlich. Grüße Fa. Senftleben Sanitär Heizung aus Ehingen (Donau).“'),
    ('Lanzinger GmbH', 'Sanitär · Heizung · Klimatechnik', '„(…) Alle gewünschten Details wurden super umgesetzt. Vielen Dank für die einwandfreie Zusammenarbeit, gerne wieder.“'),
    ('Andrea Süßmeier', 'Süßmeier Heizungstechnik · SHK', '„Zusammenarbeit mit Hr. Seelau der HandwerksManufaktur ist nur zu empfehlen! Immer angenehm mit ihm zu schreiben oder zu telefonieren. (…)“'),
    ('Hannes Schmidt GmbH', 'Sanitär-Heizung-Klima', '„(…) Nach einem kurzen Telefonat und Kennenlernen verlief die Umsetzung reibungslos und zu unserer vollen Zufriedenheit. (…) Wir können die Zusammenarbeit definitiv weiterempfehlen.“'),
    ('Alisa Kirchner', 'Kirchner GmbH', '„(…) Zusätzlich haben wir sein Recruiting Angebot in Anspruch genommen, auch hier hat er beste Arbeit geleistet und tolle Anzeigen erstellt und sehr professionell umgesetzt! (…)“'),
    ('Isabella Rauch', 'Autohaus Ressle · Recruiting', '„(…) wir haben eine überraschend hohe Anzahl an BewerberInnen und InteressentInnen über die kreative Stellenanzeige auf Facebook etc. erhalten. Für uns ist dieser Weg der Personalsuche in jedem Fall zukunftsweisend und zeigt sicheren Erfolg. (…)“'),
]
STIMMEN_LOGO = {'Franz Gallenberger': 'gallenberger', 'Benjamin Senftleben': 'senftleben', 'Lanzinger GmbH': 'lanzinger', 'Andrea Süßmeier': 'suessmeier', 'Hannes Schmidt GmbH': 'hannes-schmidt', 'Alisa Kirchner': 'kirchner', 'Isabella Rauch': 'ressle'}
def stimmen():
    def karte(n, b, z):
        return f'<figure class="stimme"><div class="kopf"><span class="stern" aria-hidden="true">{ic("star","voll")*5}</span><span class="google-mini" aria-hidden="true">{GOOGLE_G}</span></div><blockquote>{z}</blockquote><figcaption class="wer"><span class="lg"><img src="/assets/logos-box/{STIMMEN_LOGO[n]}.png" alt="" width="336" height="120"></span><span><b>{n}</b><small>{b}</small></span></figcaption></figure>'
    reihe1 = ''.join(karte(n, b, z) for n, b, z in STIMMEN)
    still = lambda k: k.replace('<figure class="stimme">', '<figure class="stimme" aria-hidden="true">')
    return f'''<section class="stimmen" id="stimmen">
  <div class="wrap">
    <div class="sec-kopf mitte"><p class="kick rv">Stimmen aus der Branche</p><h2 class="d rv">Wir könnten viel erzählen. <span class="em k">Betriebe erzählen es besser.</span></h2><p class="rv"><span class="google">{GOOGLE_G}<span>5,0 <span class="stern" aria-hidden="true">{ic("star","voll")*5}</span></span><span style="font-weight:500;color:var(--sub)">57 Google-Bewertungen</span></span></p></div>
  </div>
  <div class="stimmen-marq rv"><div class="spur">{reihe1}{still(reihe1)}</div></div>
</section>'''

def ueber_offen(kurz=True):
    return f'''<section class="ueber offen" id="ueber-uns">
  <div class="wrap"><div class="ueber-grid rv">
    <div class="bilder nur-noah">
      <figure class="gross"><img src="/assets/fotos/noah-ueber-studio.jpg" alt="Noah Seelau, Gründer der HandwerksManufaktur" loading="lazy" width="900" height="1100" style="object-position:50% 30%"></figure>
    </div>
    <div class="txt">
      <p class="kick">Wer dahinter steht</p>
      <h2 class="d">Du beherrschst dein Handwerk. <span class="em w">Wir unseres.</span></h2>
      <p>Ich bin Noah. Seit über sechs Jahren nur Handwerk, über 130 Betriebe, die meisten davon SHK. Wir wissen, was einen Monteur zum Wechseln bringt und wann ein Eigentümer sein neues Bad plant, und bauen deine Kampagne genau darauf. Und wenn dein Umkreis dafür zu klein ist, sagen wir es dir im ersten Gespräch.</p>
      <div class="gruender"><img src="/assets/fotos/noah-koller-werkstatt.jpg" alt="Noah Seelau vor dem Firmenwagen eines Kundenbetriebs" width="400" height="320" loading="lazy"><span><b>Noah Seelau</b><small>Gründer · dein direkter Draht</small></span></div>
      <div class="stats hell"><div class="stat"><b>5,0<span class="stern">{ic("star","voll")}</span></b><small>Google-Bewertung aus 57 Bewertungen</small></div><div class="stat"><b>24<span>h</span></b><small>oft bis zur ersten Bewerbung oder Anfrage</small></div><div class="stat"><b>25<span>km</span></b><small>Umkreis, in dem die Anzeigen laufen</small></div></div>
      {'' if not kurz else f'<p style="margin-top:10px"><a class="btn btn-ink" href="{u("/ueber-uns/")}">Mehr über uns <span aria-hidden="true">→</span></a></p>'}
    </div>
  </div></div>
</section>'''

TEAM = [('noah', 'Noah', 'Gründer · Strategie&nbsp;&amp;&nbsp;Vertrieb', '50% 50%'),   # rundes Lächel-Porträt 03/2026 als Kreis — ganzer Kopf, und kein zweites Mal das Laptop-Foto aus „Wer dahinter steht" (Noah, 27.09.2026)
        ('robert-rund', 'Robert', 'Videoschnitt&nbsp;&amp;&nbsp;Creative', '50% 50%'),   # Kopf mit Luft nach oben — im Original berührt das Haar den Rand (Noah, 27.09.2026)
        (None, 'Rudolf', 'Websites&nbsp;&amp;&nbsp;Anzeigen', '')]   # Noah, 27.09.2026: „mach gesicht von rudolf raus!!! und einfach n R rein … füll die kreise aus"

def team():
    """Wer wir sind — auf jeder Seite (Noah, 27.09.2026: „bau überall noch ne team sektion … nicht so detailreich")."""
    def bild(d, n, r, pos):
        if d is None:   # kein Foto: ausgefüllter Kreis mit Initiale
            return f'<figure class="initiale" aria-hidden="true"><span>{n[0]}</span></figure>'
        return f'''<figure><img src="/assets/team/{d}.jpg" alt="{n}, {r.replace('&nbsp;', ' ').replace('&amp;', '&')}" loading="lazy" width="{ {'noah': 480, 'robert-rund': 600}.get(d, 800) }" height="{ {'noah': 480, 'robert-rund': 600}.get(d, 1000) }" style="object-position:{pos}"></figure>'''
    k = ''.join(f'''<article class="person rv" data-d="{i+1}">{bild(d, n, r, pos)}<div class="txt"><h3>{n}</h3><p>{r}</p></div></article>''' for i, (d, n, r, pos) in enumerate(TEAM))
    return f'''<section class="sec team" id="team"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick rv">Das Team</p><h2 class="d rv">Drei Leute. <span class="em k">Ein Team.</span></h2></div><p class="lead rv">Wer mit dir spricht, sitzt mit denen am Tisch, die deine Kampagne bauen.</p></div>
  <div class="team-grid">{k}</div>
</div></section>'''

def statement(text_html, mitte=False, von='', cta=''):
    # Wörter einzeln, damit sich der Satz beim Scrollen füllt; <em> bleibt als Akzent
    teile = re.split(r'(<em>.*?</em>)', text_html)
    out = []
    for t in teile:
        if t.startswith('<em>'):
            for w in t[4:-5].split(): out.append(f'<span class="w em">{w}</span>')
        else:
            for w in t.split(): out.append(f'<span class="w">{w}</span>')
    cite = f'<cite class="rv">{von}</cite>' if von else ''
    knopf = f'<div class="statement-cta rv">{cta}</div>' if cta else ''
    return f'<section class="statement{" mitte" if mitte else ""}" aria-label="Leitsatz"><div class="wrap"><p>{" ".join(out)}</p>{cite}{knopf}</div></section>'

FAQ_ALLE = [
    ('Ich habe schon eine Agentur bezahlt, und es kam nichts.', 'Social-Media-Werbung ist nicht gleich Social-Media-Werbung. Stockfoto und „Wir suchen dich" laufen bei allen, und niemand erkennt darin einen Betrieb aus seinem Ort. Wir drehen bei dir, filtern vor der Bewerbung und spielen nur deinen Umkreis aus.'),
    ('Wie schnell kommen die ersten Bewerbungen und Anfragen?', 'Bewerbungen oft in den ersten 24 Stunden nach dem Start. Bäder brauchen länger, ein Bad wird geplant: Sussmann hatte den ersten Auftrag über 10.000 € nach 2 Wochen, Senftleben 21 Anfragen in 2 Monaten.'),
    ('Ich habe keine Zeit für Social Media.', 'Dein Aufwand: ein Gespräch von 30 Minuten zum Start, ein Fototermin bei dir im Betrieb, danach die Bewerbungsgespräche. Kampagne, Anzeigen und Nachregeln machen wir.'),
    ('Wir haben keine 4-Tage-Woche und keinen Firmenwagen.', 'Brauchst du auch nicht. Pünktliches Geld, ein fester Umkreis, ein Chef, der mit anpackt: Das ist für viele Monteure schon der Grund. Das zeigen wir mit deinen Leuten vor der Kamera.'),
    ('Wir sitzen auf dem Land. Lohnt sich das da?', 'Gerade dort. Die Anzeigen laufen nur in deinem Einzugsgebiet, und auf dem Land wirbt dort kaum jemand. Ob dein Umkreis groß genug ist, rechnen wir in der Potenzialanalyse durch.'),
    ('Was, wenn wir die Anfragen nicht abarbeiten können?', 'Dann drosseln wir, auf Wunsch auf ein, zwei Aufträge im Monat. Du bekommst Anfragen in dem Tempo, das dein Team stemmt.'),
    ('Wie lange bin ich gebunden?', '3 Monate Anlaufzeit, damit die Kampagne eingespielt ist, danach monatlich kündbar.'),
    ('Woher wisst ihr, welcher Monteur zu mir passt?', 'Vor der Bewerbung stehen Filterfragen: Gewerk, Erfahrung, Führerschein, Entfernung. Wer nicht passt, hört vorher auf. Du entscheidest, wen du zurückrufst.'),
]
FAQ_START = [FAQ_ALLE[i] for i in (0, 1, 2, 3, 4, 6)]
def faq(fragen=FAQ_START, h2='Bevor du <span class="em k">fragst.</span>'):
    items = ''.join(f'<details class="faq-item"{" open" if i == 0 else ""}><summary>{q}<i aria-hidden="true">+</i></summary><div class="a"><p>{a}</p></div></details>' for i, (q, a) in enumerate(fragen))
    return f'''<section class="faq" id="faq">
  <div class="wrap"><div class="faq-grid">
    <div class="links rv"><p class="kick">Häufige Fragen</p><h2 class="d">{h2}</h2><p>Die Einwände aus fast jedem Erstgespräch, kurz beantwortet. Alles andere klären wir in der Potenzialanalyse.</p>
      <div class="faq-anker"><div class="wer"><img src="/assets/fotos/noah-kopf-nah.jpg" alt="Noah Seelau" width="400" height="400"><span><b>Deine Frage steht nicht dabei?</b><small>Am Telefon bist du direkt bei mir.</small></span></div><a class="btn btn-ink" href="{TEL_HREF}">{ic('phone','ic')}{TEL}</a></div>
    </div>
    <div class="faq-liste rv" data-d="1">{items}</div>
  </div></div>
</section>'''

def faq_schema(fragen):
    return [{"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": html.unescape(q), "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub('<[^>]+>', '', a))}} for q, a in fragen]}]

# Nur SHK-Betriebe plus wenige passende Nachbarn (Noah, 27.09.2026: „tendenziell eher die SHK-Firmen … Alpplast, Küchenhaus
# Hirschvogel … Industrie-Montage … aber so Metallbau-Bilder, von einer Zimmerei oder von Pröbstl … draußen lassen“).
# SHK: Klaß k07 k15 k17 k18 k40 · Erwin Schmidt k34–k36 k41–k46 · Senftleben k37 k38 k47 k48 · Ott Sanitär k49
# Nachbarn: Allplast k24 k26 k29 k30 k32 · Hirschvogel k19 k20 k23 · Hawe k08
# Raus: Pröbstl k01 k03 k05 k14 · Zimmerei Schneider k02 k04 k06 k09 k10 k12 k13 k16 · Metallbau k33 k39
COLLAGE = [7, 34, 37, 24, 15, 42, 19, 47, 17, 35, 29, 43, 18, 48, 20, 36,
           40, 41, 30, 38, 44, 26, 45, 23, 46, 49, 32, 8]

def kontakt(h2='Was ist in deinem Umkreis <span class="em w">drin?</span>'):
    """Potenzialanalyse — neu angesetzt (Noah, 27.09.2026, vierte Ansage: „immer noch gleich … pass es endlich an"):
    zwei gleich breite Hälften, links ein echtes Foto aus einem Kundenbetrieb, rechts drei Zeilen und die zwei Wege. Kein Avatar-Band, keine Häkchen-Liste."""
    return f'''<section class="kontakt" id="kontakt">
  <div class="wrap"><div class="kontakt-karte kontakt-neu rv">
    <figure class="kontakt-bild collage-feld"><div class="collage" data-pool='{json.dumps([f"/assets/collage/k{i:02d}.webp" for i in COLLAGE])}'>{"".join(f'<img src="/assets/collage/k{i:02d}.webp" alt="" width="320" height="320" loading="lazy" decoding="async">' for i in COLLAGE[:16])}</div><figcaption>Aus unseren Shootings in den Betrieben</figcaption></figure>
    <div class="kontakt-text">
      <p class="kick">Potenzialanalyse · 30 Min. · kostenlos</p>
      <h2 class="d">{h2}</h2>
      <p class="kontakt-satz">Am Ende steht eine Zahl für deinen Umkreis. Reicht sie nicht, sagen wir es dir.</p>
      <div class="wahl">
        <a href="{CAL_REC}" target="_blank" rel="noopener">{ic('users','ic')}<span><h3>Monteure finden</h3><small>Recruiting-Potenzial deiner Region</small></span><span class="pfeil" aria-hidden="true">→</span></a>
        <a class="w" href="{CAL_LEAD}" target="_blank" rel="noopener">{ic('bath','ic')}<span><h3>Aufträge gewinnen</h3><small>Bad- und Wärmepumpen-Potenzial</small></span><span class="pfeil" aria-hidden="true">→</span></a>
      </div>
      <p class="kontakt-zeile"><a href="{TEL_HREF}">{ic('phone')}{TEL}</a><a href="mailto:{MAIL}">{ic('mail')}{MAIL}</a></p>
    </div>
  </div></div>
</section>'''

def vorteile_bild(liste):
    """Drei Vorteile mit je einem Bild statt eines Icons (Noah, 27.09.2026: „mehr veranschaulichen als diese drei simplen Icons")."""
    return '<div class="vorteile bilder-v">' + ''.join(f'<article class="vorteil mit-bild {k} rv" data-d="{i+1}"><div class="v-bild" aria-hidden="true">{b}</div><h3>{tt}</h3><p>{pp}</p></article>' for i, (k, b, tt, pp) in enumerate(liste)) + '</div>'

def v_phone(src):
    return f'<div class="mini-phone v-phone"><img src="{src}" alt="" loading="lazy"></div>'

def szene(*icons):
    """Kleine Bildfolge statt eines Einzel-Icons (Noah, 27.09.2026: „dass die Icons so ein bisschen mehr erzählen“).
    Drei Stationen, verbunden durch eine Linie, die letzte hervorgehoben."""
    return '<div class="szene" aria-hidden="true">' + '<i class="sz-linie"></i>'.join(f'<span class="sz{" ziel" if i == len(icons)-1 else ""}">{IK[k]}</span>' for i, k in enumerate(icons)) + '</div>'

def vorteile_szene(liste):
    return '<div class="vorteile">' + ''.join(f'<article class="vorteil mit-szene {k} rv" data-d="{i+1}">{sz}<h3>{t}</h3><p>{p}</p></article>' for i, (k, sz, t, p) in enumerate(liste)) + '</div>'

def vorteile(liste):
    return '<div class="vorteile">' + ''.join(f'<article class="vorteil {k} rv" data-d="{i+1}"><div class="ic" aria-hidden="true">{ic}</div><h3>{t}</h3><p>{p}</p></article>' for i, (k, ic, t, p) in enumerate(liste)) + '</div>'

def praxis_streifen():
    fotos = [('shk-01.jpg', 'Auf der Baustelle'), ('klass-werkbank.jpg', 'An der Werkbank'), ('erwin-schmidt-van.jpg', 'Zwei Monteure am Firmenwagen'), ('shk-04.jpg', 'Im Rohbau'), ('senftleben-team.jpg', 'Das Team im Lager'), ('shk-06.jpg', 'Bohrarbeiten'), ('klass-beratung.jpg', 'Beratung im Betrieb'), ('shk-08.jpg', 'Im Lager')]
    f = ''.join(f'<figure><img src="/assets/fotos/{d}" alt="{c} — Shooting bei einem SHK-Betrieb" loading="lazy"><figcaption>{c}</figcaption></figure>' for d, c in fotos)
    return f'''<section class="praxis" id="praxis">
  <div class="wrap"><div class="sec-kopf"><div><p class="kick rv">Aus der Praxis</p><h2 class="d rv">Wir kennen deine <span class="em k">Baustellen.</span></h2></div><p class="lead rv">Heizungskeller, Lager, Baustelle: Hier entstehen die Fotos für die Kampagnen. Wir kommen dafür zu dir in den Betrieb.</p></div></div>
  <div class="streifen">{f}</div>
</section>'''

def galerie():
    fotos = [('bad-wanne.jpg', 'Waschtisch mit Lichtspiegeln', False), ('bad-dusche.jpg', 'Bodengleiche Dusche', False), ('wp-haus.jpg', 'Wärmepumpe am Einfamilienhaus', False), ('bad-marmor.jpg', 'Eckwanne in Marmoroptik', False), ('wp-garten.jpg', 'Wärmepumpe im Garten', False), ('wp-herbst.jpg', 'Wärmepumpe am Altbau', False)]
    f = ''.join(f'<figure class="rv{" quer" if q else ""}" data-d="{i+1}"><img src="/assets/projekte/{d}" alt="{c} — Projekt eines Kunden" loading="lazy"><figcaption>{c}</figcaption></figure>' for i, (d, c, q) in enumerate(fotos))
    return f'''<section class="sec" id="projekte" style="padding-top:0">
  <div class="wrap"><div class="sec-kopf"><div><p class="kick w rv">Wofür das alles läuft</p><h2 class="d rv">Bäder und Wärmepumpen, <span class="em w">fertig gebaut.</span></h2></div><p class="lead rv">Bäder und Wärmepumpen aus Projekten unserer Kunden. Genau solche Aufträge holen die Kampagnen rein.</p></div>
  <div class="galerie">{f}</div></div>
</section>'''

# ── Seiten ────────────────────────────────────────────────────────────────
def seite_start():
    h = kopf('Monteure und Aufträge für SHK-Betriebe aus deinem Umkreis', 'Monteure und Bad-Anfragen, die nur du bekommst: Anzeigen mit deinen Leuten im eigenen Umkreis, Filterfragen vor jeder Bewerbung. 130+ Betriebe, 5,0 auf Google.', '/', schema_extra=faq_schema(FAQ_START))
    hero = f'''<section class="hero" id="start">
  <div class="wrap">
    <p class="kick rv">Spezialisiert auf SHK-Betriebe</p>
    <h1 class="h-xl hero-h1 zwei"><span class="zl" aria-hidden="true"><span>Mehr <span class="wechsel"><span class="an">Monteure</span><span>Bad-Aufträge</span><span>Heizungs-Aufträge</span><i class="wechsel-lauf"></i></span></span></span><span class="zl" aria-hidden="true"><span>aus deinem Umkreis.</span></span><span class="zl" aria-hidden="true"><span class="em w glut">Live in unter 2 Wochen.</span></span><span class="sr">Mehr Monteure und Aufträge aus deinem Umkreis. Live in unter 2 Wochen.</span></h1>
    <p class="lead rv" data-d="2">Anzeigen mit deinen Leuten, nur in deinem Einzugsgebiet, Filterfragen vor jeder Bewerbung und Anfrage. Du führst nur noch die Gespräche, den Rest machen wir.</p>
    <div class="hero-cta rv" data-d="3"><a class="btn btn-ink btn-lg" href="{u('/potenzialanalyse/')}">{ic('target','ic')}Potenzialanalyse für meinen Umkreis</a><a class="btn btn-white btn-lg" href="#fallstudien">{ic('play','ic')}Fallstudien ansehen</a></div>
    <div class="rv" data-d="4">{trust()}</div>
  </div>
  <div class="wrap weit buehne-wrap"><div class="buehne feed still"><div class="raster" aria-hidden="true"></div>
    <div class="feed-innen still">
      {phone('/assets/funnels/erwin-schmidt-jobs-full.jpg', 'Recruiting · Erwin Schmidt &amp; Sohn', '#1E90E8', 'p2')}
      {reel_phone('kunden-szenen', 'Gedreht bei unseren Kunden', 'p3', 'kunden-szenen-poster.jpg')}   
      {phone('/assets/funnels/sussmann-leadgen-hero.jpg', 'Badsanierung · Sussmann GmbH', '#F5762B', 'p4')}
    </div>
  </div></div>
</section>'''
    body = hero + logo_band() + leiter() + vergleich() + system() + hebel() + fallstudien_teaser() + kaskade('senftleben') + stimmen() + ueber_offen() + team() + statement('„Werbung macht man nicht nur, <em>wenn es gut läuft.“</em>', mitte=True, von='Benjamin Senftleben · Inhaber, Senftleben Haustechnik, Ehingen') + faq() + kontakt()
    return h + body + fuss()

def uhero(kick, h1, lead, cta_text, cta_href, cta_klasse, phones, warm=False):
    return f'''<section class="uhero{' w' if warm else ''}"><div class="raster" aria-hidden="true"></div>
  <div class="wrap">
    <div class="txt"><p class="kick rv">{kick}</p><h1 class="h-xl rv" data-d="1">{h1}</h1><p class="lead rv" data-d="2">{lead}</p>
      <div class="hero-cta rv" data-d="3"><a class="btn {cta_klasse} btn-lg" href="{cta_href}" target="_blank" rel="noopener">{ic('target','ic')}{cta_text}</a><a class="btn btn-glass btn-lg" href="#fallstudie">Fallstudie ansehen</a></div>
      <div class="rv" data-d="4">{trust()}</div></div>
    <div class="buehne-phones rv" data-d="2">{phones}</div>
  </div>
</section>'''

def seite_monteure():
    fr = [FAQ_ALLE[0], FAQ_ALLE[7], FAQ_ALLE[3], FAQ_ALLE[2], FAQ_ALLE[1]]
    h = kopf('Monteure finden für SHK-Betriebe: Social Recruiting im Umkreis', 'Anlagenmechaniker und Kundendiensttechniker über Anzeigen im Umkreis: Bewerbung in 60 Sekunden, vorqualifiziert. Fallstudie: 25 Bewerbungen in 4 Wochen.', '/monteure/', dunkel=True, schema_extra='')
    body = uhero('Für SHK-Betriebe, die einen Monteur suchen', 'Monteure, die anfangen wollen. <span class="em k">Aus deinem Umkreis.</span>', 'Die guten Monteure suchen nicht, sie sind in Arbeit. Sie wechseln, wenn das richtige Angebot vor ihnen liegt. Wir bringen deins dorthin, wo sie jeden Abend sind: in ihren Feed. Du führst nur noch die Gespräche.', 'Recruiting besprechen', CAL_REC, 'btn-kalt',
        phone('/assets/funnels/senftleben-jobs-full.jpg', 'Recruiting · Senftleben Haustechnik', '#1E90E8', 'links', '2s') + phone('/assets/funnels/erwin-schmidt-jobs-full.jpg', 'Recruiting · Erwin Schmidt &amp; Sohn', '#1E90E8', 'rechts', '0s'))
    body += f'''<section class="sec" id="vorteile"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick k rv">Was anders läuft</p><h2 class="d rv">Bewerbungen von Leuten, die <span class="em k">gerade nicht suchen.</span></h2></div><p class="lead rv">Social Recruiting erreicht Anlagenmechaniker SHK und Kundendiensttechniker dort, wo sie ohnehin sind: auf Instagram und Facebook, nicht auf Stellenportalen, die nur aktiv Suchende sehen.</p></div>
  {vorteile_bild([('', v_phone('/assets/funnels/erwin-schmidt-jobs-full.jpg'), 'Bewerbung in 60 Sekunden, ohne Lebenslauf', 'Ein paar Fragen im Handy, fertig. Wer sich abends auf der Couch bewirbt, lädt keinen Lebenslauf hoch.'), ('', tickets(TICKETS_REC[:2]), 'Vorqualifiziert: Gewerk, Erfahrung, Führerschein', 'Filterfragen vor der Bewerbung. Bei dir kommt an, wer zur Stelle passt, mit Kontaktdaten.'), ('', '<img src="/assets/fotos/klass-team-van-scharf.jpg" alt="" loading="lazy" width="1600" height="1067" style="object-position:50% 40%">', 'Dein Betrieb als Marke', 'Mit Fotos aus deinem Betrieb: dein Team, dein Lager, deine Baustellen. Kein Stockbild, das jeder hat.')])}
</div></section>'''
    body += leiter(WEGE_ALLE[:4], 'Was du wahrscheinlich schon probiert hast', 'Vier Wege, die <span class="em k">kalt</span> bleiben.', 'Aufkleber, Portal, eigene Seite, Mundpropaganda: Alles erreicht nur die, die schon suchen. Und wer sich über ein Portal bewirbt, ist oft nach ein paar Monaten wieder weg.')
    body += f'''<section class="sec" id="fallstudie"><div class="wrap"><div class="sec-kopf"><div><p class="kick rv">Fallstudie · Recruiting</p><h2 class="d rv">„Wir haben nur nicht gedacht, dass es <span class="em k">so viele</span> sind.“</h2></div><p class="lead rv">Erwin Schmidt &amp; Sohn, Sindelfingen. Ein Anlagenmechaniker gesucht, 25 Bewerbungen bekommen, Stelle besetzt.</p></div>{FALL_ESS()}
  <div class="fall-abstand">{FALL_SEN_REC()}</div></div></section>'''
    body += kaskade('ess') + reels() + statement('„… der war schon eine Woche bei uns, der ist <em>echt gut.“</em>', mitte=True, von='Florian Schmidt · Geschäftsführer, Erwin Schmidt &amp; Sohn, über den Monteur aus der Kampagne') + kontakt('Such dir den Termin aus, <span class="em k">der passt.</span>')
    return h + body + fuss()

def seite_auftraege():
    fr = [FAQ_ALLE[0], FAQ_ALLE[5], FAQ_ALLE[1], FAQ_ALLE[4], FAQ_ALLE[2]]
    h = kopf('Bad- und Wärmepumpen-Aufträge für SHK-Betriebe', 'Bad- und Wärmepumpen-Anfragen aus deinem Umkreis, nur für deinen Betrieb, vorqualifiziert nach Objekt und Eigentum. Fallstudie: 21 Anfragen in 2 Monaten.', '/auftraege/', dunkel=True, schema_extra='')
    body = uhero('Für SHK-Betriebe, die Bäder und Wärmepumpen bauen', 'Bad-Aufträge, die nur du bekommst. <span class="em w">Aus deinem Umkreis.</span>', 'Anzeigen auf deinen Namen, nur in deinem Einzugsgebiet, Filterfragen vor jeder Anfrage. Jede Anfrage gehört dir allein, nicht vier Wettbewerbern gleichzeitig. Du fährst nur noch zum Termin.', 'Potenzial durchrechnen', '#rechner-auf', 'btn-warm',
        phone('/assets/funnels/sussmann-leadgen-hero.jpg', 'Aufträge · Sussmann GmbH', '#F5762B', 'links', '1s') + phone('/assets/funnels/senftleben-leadgen-full.jpg', 'Aufträge · Senftleben Haustechnik', '#F5762B', 'rechts', '0s'), warm=True)
    body += f'''<section class="sec" id="vorteile"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick w rv">Was anders läuft</p><h2 class="d rv">Bäder und Wärmepumpen, <span class="em w">wenn du sie brauchst.</span></h2></div><p class="lead rv">Ein Komplettbad oder eine Wärmepumpe bringt 20.000 bis 50.000 €. Über Mundpropaganda kommen die Projekte, wann sie wollen. Über deinen eigenen Kanal kommen sie, wenn du Kapazität hast.</p></div>
  {vorteile_bild([('w', vgl_bild('portal', True), 'Exklusiv für deinen Betrieb', 'Keine Portal-Leads, die parallel an vier Betriebe gehen. Deine Fotos, dein Gebiet, deine Anfragen.'), ('w', tickets(TICKETS_LEAD[:2]), 'Vorqualifiziert: Objekt, Baujahr, Eigentum, Zeitrahmen', 'Filterfragen vor der Anfrage. Eine Anfrage ohne Adresse und Rückrufnummer zählt bei uns nicht als Anfrage.'), ('w', vgl_bild('last', True), 'Regelbar', 'Auf Wunsch auch nur ein, zwei Aufträge im Monat. Du bekommst Anfragen in dem Tempo, das dein Team stemmen kann.')])}
</div></section>'''
    body += galerie()
    body += f'''<section class="sec" id="fallstudie"><div class="wrap"><div class="sec-kopf"><div><p class="kick w rv">Fallstudie · Auftrags-Funnel Badsanierung</p><h2 class="d rv">„Dass so schnell so viele Anfragen kommen, <span class="em w">hätte ich nicht gedacht.</span>“</h2></div><p class="lead rv">Senftleben Haustechnik, Ehingen. Ausgelastet, und trotzdem laufen die Anzeigen weiter, damit der Name im Kopf bleibt.</p></div>{FALL_SEN()}
  <div class="fall-abstand">{FALL_SUS()}</div>
</div></section>'''
    body += kaskade('senftleben') + reels() + statement('„Wieso macht Coca‑Cola Werbung? … Weil der Name sich in die Köpfe <em>einbrennen soll.“</em>', mitte=True, von='Benjamin Senftleben · Inhaber, Senftleben Haustechnik, Ehingen') + kontakt('Such dir den Termin aus, <span class="em w">der passt.</span>')
    return h + body + fuss()

def seite_fallstudien():
    h = kopf('Fallstudien: Recruiting und Auftrags-Funnel für SHK-Betriebe', 'Erwin Schmidt & Sohn: 25 Bewerbungen in 4 Wochen. Senftleben Haustechnik: 21 Bad-Anfragen in 2 Monaten. Beide Inhaber im Video, mit den Zahlen aus den ersten Wochen.', '/fallstudien/')
    body = f'''<section class="hero" id="start" style="padding-bottom:0"><div class="wrap"><p class="kick rv">Fallstudien</p><h1 class="h-xl rv" data-d="1">Vier Kampagnen, <span class="em w">die gerade laufen.</span></h1><p class="lead rv" data-d="2">Mit den Zahlen aus den ersten Wochen und den Inhabern vor der Kamera. Keine Hochrechnung, kein „bis zu".</p></div></section>
<section class="sec" id="fallstudie"><div class="wrap"><div class="sec-kopf"><div><p class="kick k rv">Recruiting · Erwin Schmidt &amp; Sohn, Sindelfingen</p><h2 class="d rv">Ein Anlagenmechaniker gesucht. <span class="em k">25 Bewerbungen.</span></h2></div></div>{FALL_ESS()}</div></section>
<section class="sec" id="senftleben" style="padding-top:0"><div class="wrap"><div class="sec-kopf"><div><p class="kick w rv">Auftrags-Funnel · Senftleben Haustechnik, Ehingen</p><h2 class="d rv">Ausgelastet, und trotzdem <span class="em w">21 Bad-Anfragen.</span></h2></div></div>{FALL_SEN()}</div></section>
<section class="sec" id="sussmann" style="padding-top:0"><div class="wrap"><div class="sec-kopf"><div><p class="kick w rv">Auftrags-Funnel · Erich Sussmann GmbH, Kirchheim bei München</p><h2 class="d rv">Erster Auftrag <span class="em w">nach zwei Wochen.</span></h2></div></div>{FALL_SUS()}</div></section>
<section class="sec" id="senftleben-recruiting" style="padding-top:0"><div class="wrap"><div class="sec-kopf"><div><p class="kick k rv">Recruiting · Senftleben Haustechnik, Ehingen</p><h2 class="d rv">Eine Bürostelle, <span class="em k">21 Bewerbungen.</span></h2></div></div>{FALL_SEN_REC()}</div></section>'''
    body += reels() + stimmen()
    return h + body + fuss()

def seite_ueber():
    h = kopf('Über uns: HandwerksManufaktur, Marketing nur fürs Handwerk', 'Seit über sechs Jahren nur Handwerk, über 130 Betriebe betreut, 5,0 auf Google. Wer hinter den Kampagnen für SHK-Betriebe steht und wie wir arbeiten.', '/ueber-uns/')
    body = f'''<section class="hero" id="start" style="padding-bottom:0"><div class="wrap"><p class="kick rv">Über uns</p><h1 class="h-xl rv" data-d="1">Eine Branche. <span class="em w">Seit über sechs Jahren.</span></h1><p class="lead rv" data-d="2">Kein Account-Manager dazwischen, keine Ticketnummer. Du weißt immer, wer an deiner Kampagne sitzt.</p></div></section>
<div style="height:64px"></div>'''
    body += ueber_offen(kurz=False) + team()
    body += f'''<section class="sec" id="wie" style="padding-top:0"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick k rv">Wie wir arbeiten</p><h2 class="d rv">Kleines Team. <span class="em k">Kurze Wege.</span></h2></div><p class="lead rv">Erstgespräch, Strategie und Kampagnenaufbau laufen über einen Tisch.</p></div>
  {vorteile_szene([('', szene('wrench', 'flame', 'bath'), 'Eine Branche, seit über sechs Jahren', 'Nur Handwerk. Wir kennen dein Gewerk, bevor du es erklären musst, und wissen, was einen Monteur zum Wechseln bringt.'), ('', szene('van', 'camera', 'phone'), 'Shooting bei dir im Betrieb', 'Heizungskeller, Lager, Baustelle: Wir kommen zu dir und fotografieren dein Team. Das ist das Material der Kampagne.'), ('', szene('euro', 'bars', 'checkmark'), 'Zahlen statt Bauchgefühl', 'Wir sehen, was jede Anfrage und jede Bewerbung kostet, und regeln nach, wenn etwas nicht läuft.')])}
</div></section>'''
    body += stimmen()
    return h + body + fuss()

def seite_potenzial():
    h = kopf('Potenzialanalyse für SHK-Betriebe: in 30 Minuten durchgerechnet', 'Kostenlos: Wir rechnen in 30 Minuten durch, was in deiner Region an Bewerbungen oder Bad- und Wärmepumpen-Anfragen drin ist. Termin online aussuchen.', '/potenzialanalyse/')
    body = f'''<section class="hero" id="start" style="padding-bottom:0"><div class="wrap"><p class="kick rv">Potenzialanalyse · 30 Minuten · kostenlos</p><h1 class="h-xl rv" data-d="1">Was ist in deiner Region <span class="em w">drin?</span></h1><p class="lead rv" data-d="2">30 Minuten, kostenlos: Wir rechnen durch, was in deinem Umkreis an Bewerbungen oder Bad-Anfragen drin ist.</p></div></section>
<div style="height:56px"></div>
{kontakt('Such dir den Termin aus, <span class="em w">der passt.</span>')}
'''
    body += faq([FAQ_ALLE[2], FAQ_ALLE[0], FAQ_ALLE[4]], 'Vor dem <span class="em k">Termin.</span>')
    return h + body + fuss()

RECHT = {'/impressum/': ('Impressum', 'Impressum der HandwerksManufaktur LTD: Anschrift, Registernummer, Umsatzsteuer-ID und Kontakt.'),
         '/datenschutz/': ('Datenschutzerklärung', 'Datenschutzerklärung der HandwerksManufaktur: welche Daten wir erheben, wofür und welche Rechte du hast.'),
         '/agb/': ('Allgemeine Geschäftsbedingungen', 'Allgemeine Geschäftsbedingungen der HandwerksManufaktur LTD für Kampagnen, Recruiting und Webdesign.')}
def seite_recht(pfad):
    """Impressum, Datenschutz, AGB im Design der Seite (28.09.2026 — vorher alte dunkle Einzeldateien mit Google Fonts und
    „USt-ID wird nachgetragen"). Text = Stand der Hauptseite, abgelegt in neu/recht/."""
    titel, beschr = RECHT[pfad]
    text = (HIER / 'recht' / (pfad.strip('/') + '.html')).read_text(encoding='utf-8')
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    return kopf(f'{titel} · HandwerksManufaktur SHK', beschr, pfad) + f'<section class="recht-seite"><div class="wrap"><article class="recht-text">{text}</article></div></section>' + fuss()

# ── Schreiben ─────────────────────────────────────────────────────────────
# /fallstudien/ ist ausgeblendet (Noah, 27.09.2026: „die Seite Fallstudien können wir aktuell noch rausnehmen“) — die alte Adresse leitet auf die Fallstudien der Startseite
SEITEN = {'/': seite_start, '/monteure/': seite_monteure, '/auftraege/': seite_auftraege, '/ueber-uns/': seite_ueber, '/potenzialanalyse/': seite_potenzial}
for _p in RECHT: SEITEN[_p] = (lambda p: lambda: seite_recht(p))(_p)
(AUS/'version.json').write_text('{"v":"%s"}\n' % V, encoding='utf-8')
for pfad, fn in SEITEN.items():
    ziel = AUS / pfad.strip('/') / 'index.html' if pfad != '/' else AUS / 'index.html'
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(optimieren(fn(), pfad=u(pfad)), encoding='utf-8')
    print('✓', ziel.relative_to(REPO))
_weg = AUS / 'fallstudien' / 'index.html'
_weg.parent.mkdir(parents=True, exist_ok=True)
_weg.write_text(f'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={u("/")}#fallstudien"><link rel="canonical" href="{u("/")}"><title>Fallstudien</title></head><body><a href="{u("/")}#fallstudien">Zu den Fallstudien</a></body></html>\n', encoding='utf-8')
if LIVE:
    sm = ''.join(f'<url><loc>{DOMAIN}{p}</loc><changefreq>monthly</changefreq><priority>{"1.0" if p == "/" else "0.8"}</priority></url>' for p in SEITEN if p not in RECHT)
    (REPO/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding='utf-8')
    print('✓ sitemap.xml')
