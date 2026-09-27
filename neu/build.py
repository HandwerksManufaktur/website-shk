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
NAV = [('/monteure/', IK['users'], 'Monteure'), ('/auftraege/', IK['bath'], 'Aufträge'), ('/fallstudien/', IK['film'], 'Fallstudien'), ('/ueber-uns/', IK['handshake'], 'Über uns')]

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
        "sameAs": ["https://handwerksmanufaktur.digital/"],
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
<link rel="preload" href="/fonts/sub/archivo-latin-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/archivo-latin-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/inter-v20-latin_latin-ext-500.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/inter-v20-latin_latin-ext-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/inter-v20-latin_latin-ext-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/inter-v20-latin_latin-ext-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/inter-v20-latin_latin-ext-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/sub/instrument-serif-v5-latin_latin-ext-italic.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS_INLINE}</style>
{MESSUNG_KOPF}
<script type="application/ld+json">{ld}</script>
</head>
<body>
<div id="intro" aria-hidden="true"><img src="/assets/logo-hm-quer-weiss.svg" alt="" width="340" height="91"><span class="strich"><i></i></span></div>
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
        <li><a href="{u('/fallstudien/')}">{ic('film')}Fallstudien</a></li>
        <li><a href="{u('/ueber-uns/')}">{ic('handshake')}Über uns</a></li>
        <li><a href="https://handwerksmanufaktur.digital/">{ic('globe')}Webdesign für Handwerk</a></li>
      </ul></div>
      <div><h4>Kontakt</h4><ul>
        <li><a href="{TEL_HREF}">{ic('phone')}{TEL}</a></li>
        <li><a href="mailto:{MAIL}">{ic('mail')}{MAIL}</a></li>
        <li><a href="/impressum/">{ic('doc')}Impressum</a></li>
        <li><a href="/datenschutz/">{ic('lock')}Datenschutz</a></li>
        <li><a href="/agb/">{ic('docs')}AGB</a></li>
      </ul></div>
    </div>
    <div class="unten"><span><i class="kante" aria-hidden="true"></i>© 2026 HandwerksManufaktur LTD · Alle Rechte vorbehalten.</span><span>Einsatzgebiet: Deutschland · Österreich · Schweiz</span></div>
  </div>
</footer>
<script src="/neu/main.js?v={V}" defer></script>
<script src="/messung.js?v={V}" defer></script>
</body>
</html>
'''

GOOGLE_G = '<svg class="g" viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.6l6.7-6.7C35.6 2.6 30.2 0 24 0 14.6 0 6.5 5.4 2.6 13.3l7.8 6.1C12.3 13.5 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.6h12.7c-.6 3-2.2 5.5-4.7 7.2l7.5 5.8c4.4-4.1 7-10.1 7-17.1z"/><path fill="#FBBC05" d="M10.4 28.6A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.1.8-4.6l-7.8-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.7l7.8-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.5-5.8c-2.1 1.4-4.9 2.3-8.4 2.3-6.3 0-11.7-4-13.6-9.9l-7.8 6.1C6.5 42.6 14.6 48 24 48z"/></svg>'

def trust(hell=True):
    return f'<p class="trust"><span><span class="stern" aria-hidden="true">{ic("star","voll")*5}</span> <b>5,0</b> auf Google</span><span>·</span><span><b>130+</b> Betriebe</span><span>·</span><span><b>Nur</b> SHK-Betriebe</span></p>'

def phone(img, etikett, farbe, klasse='', delay='0s'):
    return f'''<div class="phone {klasse}" aria-hidden="true"><div class="scroller"><img src="{img}" alt="" loading="lazy" style="--d:{delay}"></div><span class="etikett"><i style="background:{farbe}"></i>{etikett}</span></div>'''

def reel_phone(f, etikett, klasse):
    return f'''<div class="phone reel {klasse}" aria-hidden="true"><video muted loop playsinline preload="none" data-quelle="/assets/reels/{f}.mp4"></video><span class="etikett"><i style="background:#3DDC84"></i>{etikett}</span></div>'''

def hero_zettel():
    z = [(IK['inbox'], 'Neue Bewerbung', 'Anlagenmechaniker SHK · 8 Jahre · 12 km', 'qualifiziert'+IK['checkmark']), (IK['bath'], 'Neue Anfrage', 'Komplettbad · EFH Bj. 1994 · Eigentümer', 'vorqualifiziert'+IK['checkmark']), (IK['inbox'], 'Neue Bewerbung', 'Kundendiensttechniker · ab sofort · 7 km', 'qualifiziert'+IK['checkmark']), (IK['flame'], 'Neue Anfrage', 'Wärmepumpe · Ölheizung Bj. 2001 · 160 m²', 'vorqualifiziert'+IK['checkmark']), (IK['inbox'], 'Neue Bewerbung', 'Bäderbauer · Führerschein BE · 15 km', 'qualifiziert'+IK['checkmark']), (IK['bath'], 'Neue Anfrage', 'Bad barrierefrei · Eigentumswohnung · zeitnah', 'vorqualifiziert'+IK['checkmark'])]
    return ''.join(f'<div class="ticket"><span class="tic">{ic}</span><span><b>{t}</b><small>{sub}</small></span><span class="ok">{ok}</span></div>' for ic, t, sub, ok in z)

def logo_band():
    wand = [l for l in LOGOS if 'Ressle' not in l[1]][:20]
    imgs = ''.join(f'<span><img src="{src}" alt="{html.escape(name)}"{" class=wide" if r >= 3.6 else ""}></span>' for src, name, r in wand)
    return f'''<section class="band hell" aria-label="Betriebe, mit denen wir arbeiten">
  <div class="wrap"><div class="band-innen rv">
    <p class="band-t">Über <b>130 Betriebe</b> setzen auf uns. Ein Ausschnitt, fast alle SHK</p>
    <div class="logo-wand">{imgs}</div>
  </div></div>
</section>'''

WEGE_ALLE = [
    (IK['monitor'], 'Stellenportal', 'Sehen nur die, die gerade aktiv suchen. Wer in Arbeit ist, öffnet keins.'),
    (IK['van'], 'Aufkleber mit QR-Code', 'Auf dem Firmenwagen. Wer ihn liest, steht gerade im Stau.'),
    (IK['globe'], 'Die eigene Webseite', '„Wir suchen dich" steht bei allen. Wer es liest, sucht schon.'),
    (IK['speech'], 'Mundpropaganda', 'Kommt, wann sie will. Planen kannst du damit nichts.'),
    (IK['cards'], 'Lead-Portale', 'Dieselbe Anfrage geht an vier Betriebe gleichzeitig.'),
]
def leiter(wege=WEGE_ALLE, kick='Was du wahrscheinlich schon probiert hast', h2='Funktionieren die alten Wege <span class="em k">2026 noch?</span>', lead='Stellenportal, Aufkleber, eigene Seite: Das erreicht nur, wer gerade aktiv sucht. Das sind die wenigsten, und oft die, die alle paar Monate wechseln. Wer bleiben soll, ist in Arbeit und sucht nicht.', ende='„Kam kaum was zurück."', von='Florian Schmidt, Erwin Schmidt &amp; Sohn, über die Suche vor der Kampagne'):
    # Bauform nach dem Hista-Vorbild (firma/referenzen/hista-digital): Kopf-Pille, eine Reihe Wege, Schiene mit ✕-Marken, Ergebnis-Pille
    knoten = ''.join(f'''<li class="weg rv" data-d="{i+1}"><div class="ic" aria-hidden="true">{ic}</div><h3>{t}</h3><p>{p}</p><span class="x" aria-hidden="true">{IK["x"]}</span></li>''' for i, (ic, t, p) in enumerate(wege))
    return f'''<section class="probiert" id="probiert">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick k rv">{kick}</p><h2 class="d rv">{h2}</h2></div><p class="lead rv">{lead}</p></div>
    <div class="leiter wege-plan n{len(wege)} rv"><div class="wp-kopf"><span>So wird bisher gesucht</span></div><ol class="wp-reihe">{knoten}</ol><div class="wp-schiene" aria-hidden="true"></div><div class="ende" data-d="{len(wege)+1}"><span>{ende}<small>{von}</small></span></div></div>
  </div>
</section>'''

VERGLEICH = [
    (IK['users'], 'Aufträge ablehnen', 'Du sagst ein Bad ab, weil der Monteur dafür fehlt, und der Kunde bucht beim Betrieb zwei Orte weiter?', 'Bewerbungen kommen, bevor die Stelle frei wird. Du stellst ein, wenn es passt, nicht wenn es brennt.'),
    (IK['clock'], 'Zu spät gesucht', 'Die Suche beginnt erst, wenn einer kündigt, und das Team fährt wochenlang auf Reserve?', 'Die Anzeigen laufen durch. Wer im Umkreis wechseln will, sieht zuerst deinen Betrieb, nicht ein Portal.'),
    (IK['cards'], 'Portal-Leads', 'Die Bad-Anfrage aus dem Portal ging an vier Betriebe, und du fährst zu einem Termin, den drei andere auch haben?', 'Jede Anfrage gehört dir allein: mit Adresse, Baujahr, Eigentum und Zeitrahmen. Du rufst an, die anderen nicht.'),
    (IK['calendar'], 'Auslastung schwankt', 'Drei Wochen voll, und was nach der nächsten Baustelle kommt, entscheidet der Zufall?', 'Bäder und Wärmepumpen in dem Tempo, das dein Team stemmt. Auf Wunsch gedrosselt auf ein, zwei im Monat.'),
    (IK['eye'], 'Übersehen im Umkreis', 'Dein Betrieb ist gut, nur weiß es im Umkreis keiner, weil „Wir suchen dich" bei allen steht?', 'Deine Leute, deine Fotos, dein Name, auf jedem Handy in deinem Einzugsgebiet. Das schreibt sich kein Wettbewerber ab.'),
]
def vergleich():
    zellen = ''.join(f'<div class="vgl-t rv" data-d="{i%3+1}"><span class="ic" aria-hidden="true">{ic}</span><b>{t}</b></div><div class="vgl-c heute rv" data-d="{i%3+1}">{IK["x"]}<p>{h}</p></div><div class="vgl-c kanal rv" data-d="{i%3+2}">{IK["checkmark"]}<p>{k}</p></div>' for i, (ic, t, h, k) in enumerate(VERGLEICH))
    return f'''<section class="vergleich" id="vergleich">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick k rv">Erkennst du dich wieder?</p><h2 class="d rv">Heute Zufall. <span class="em w">Morgen</span> planbar.</h2></div><p class="lead rv">Fünf Lagen aus hunderten Gesprächen mit SHK-Inhabern. Links, wie es heute läuft. Rechts, was sich mit eigenen Anzeigen im Umkreis an jeder davon ändert.</p></div>
    <div class="vgl-tafel drei rv"><div class="vgl-h leer" aria-hidden="true"></div><div class="vgl-h heute">Heute</div><div class="vgl-h kanal">Mit eigenen Anzeigen</div>{zellen}</div>
    <p class="rv" style="margin-top:28px"><a class="btn btn-ink" href="{u('/potenzialanalyse/')}">{ic('target','ic')}Potenzial durchrechnen</a></p>
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
      <a class="hebel-karte rv" href="{u('/monteure/')}"><div class="txt"><span class="chip">{ic('users')}Hebel 1 · Recruiting</span><h3>Mitarbeitergewinnung für SHK-Monteure.</h3><ul><li>{ic("checkmark")}Bewerbung in 60 Sekunden, ohne Lebenslauf</li><li>{ic("checkmark")}Vorqualifiziert: Gewerk, Erfahrung, Führerschein</li><li>{ic("checkmark")}Dein Betrieb als Marke, mit Fotos aus deinem Betrieb</li></ul><span class="btn btn-white">Recruiting ansehen <span aria-hidden="true">→</span></span></div><div class="bild"><img src="/assets/fotos/erwin-schmidt-monteur.jpg" alt="Monteur eines SHK-Betriebs mit Werkzeug" loading="lazy" width="1100" height="733" style="object-position:55% 25%"></div></a>
      <a class="hebel-karte w rv" data-d="1" href="{u('/auftraege/')}"><div class="txt"><span class="chip">{ic('bath')}Hebel 2 · Aufträge</span><h3>Auftrags-Funnel für Bad &amp; Wärmepumpe.</h3><ul><li>{ic("checkmark")}Exklusiv für deinen Betrieb</li><li>{ic("checkmark")}Vorqualifiziert: Objekt, Baujahr, Eigentum, Zeitrahmen</li><li>{ic("checkmark")}Regelbar, auf Wunsch nur 1–2 Aufträge im Monat</li></ul><span class="btn btn-white">Aufträge ansehen <span aria-hidden="true">→</span></span></div><div class="bild"><img src="/assets/fotos/senftleben-benjamin-fenster.jpg" alt="Benjamin Senftleben im Firmenwagen von Senftleben Haustechnik" loading="lazy" width="1100" height="733" style="object-position:78% 30%"></div></a>
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
    <div class="betrieb"><span class="lg"><img src="{logo}" alt="{html.escape(name)}"></span><span><b>{name}</b><small>{ort}</small></span></div>
    <div class="zahlen">{z}</div>
    <p class="zeit">{zeit}</p>
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
    <div class="sec-kopf"><div><p class="kick rv">Drei Betriebe, drei Ergebnisse</p><h2 class="d rv">Was bei drei SHK-Betrieben <span class="em w">rauskam.</span></h2></div><p class="lead rv">Ein Anlagenmechaniker in 4 Wochen, 21 Bad-Anfragen in 2 Monaten, ein Auftrag über 10.000 € nach 14 Tagen. Die Inhaber erzählen es selbst im Video.</p></div>
    <div class="fall-grid drei">
      {fall_karte(ESS_LOGO, 'Erwin Schmidt &amp; Sohn', 'Sindelfingen · SHK-Familienbetrieb in 3. Generation', 'Recruiting · läuft', '', '/assets/testimonial/ess-testimonial-poster.jpg', '/assets/testimonial/ess-testimonial.mp4', '2:48', '25 Bewerbungen, 1 Anlagenmechaniker eingestellt, in 4 Wochen.', [('25', 'Bewerbungen'), ('1', 'Stelle besetzt'), ('4', 'Wochen Laufzeit')], 'Florian Schmidt, Geschäftsführer · Zahlen aus den ersten 4 Wochen')}
      {fall_karte(SEN_LOGO, 'Senftleben Haustechnik', 'Ehingen (Donau) · Badsanierung in 3. Generation', 'Badsanierung · läuft', 'w', '/assets/testimonial/senftleben-testimonial-poster.jpg', '/assets/testimonial/senftleben-testimonial.mp4', '2:22', '21 Bad-Anfragen und 10+ Vor-Ort-Termine in 2 Monaten.', [('125.000', 'Aufrufe im Umkreis'), ('21', 'Bad-Anfragen'), ('10<span class="plus">+</span>', 'Vor-Ort-Termine')], 'Benjamin Senftleben, Inhaber · Zahlen aus den ersten 2 Monaten', 1)}
      {sussmann_karte(2)}
    </div>
    <p class="rv" style="text-align:center;margin-top:32px"><a class="btn btn-white" href="{u('/fallstudien/')}">Alle Fallstudien in voller Länge <span aria-hidden="true">→</span></a></p>
  </div>
</section>'''

def fall_gross(logo, name, rolle, betrieb, poster, video, dauer, zitat, absatz, zahlen, chipk, aria):
    z = ''.join(zahl_html(b, s, chipk) for b, s in zahlen)
    return f'''<article class="fall-gross rv">
  <div class="vid"><video preload="none" poster="{poster}" playsinline aria-label="{aria}" style="object-position:50% {'8%' if 'senftleben' in poster else '50%'}"><source src="{video}" type="video/mp4">Dein Browser kann dieses Video nicht abspielen.</video><button class="play" type="button" aria-label="Video ansehen"><span>{ic("play","voll")} Video ansehen · {dauer}</span></button></div>
  <div class="txt">
    <div><blockquote>{zitat}</blockquote><p style="margin-top:18px">{absatz}</p></div>
    <div class="zahlen">{z}</div>
    <div class="person"><img src="{logo}" alt="{html.escape(betrieb)}"><span><b>{name}</b>{rolle}</span></div>
  </div>
</article>'''

FALL_ESS = lambda: fall_gross(ESS_LOGO, 'Florian Schmidt', 'Geschäftsführer, Erwin Schmidt &amp; Sohn GmbH, Sindelfingen', 'Erwin Schmidt & Sohn', '/assets/testimonial/ess-testimonial-poster.jpg', '/assets/testimonial/ess-testimonial.mp4', '2:48', '„Ich kann es jedem nur empfehlen: Wenn wirklich Personalmangel da ist, dass man den Schritt geht."', 'Erwin Schmidt &amp; Sohn in Sindelfingen, SHK-Familienbetrieb in dritter Generation, suchte einen Anlagenmechaniker für den Kundendienst. Probiert war schon einiges: Aufkleber mit QR-Code auf den Firmenwagen, die Stelle auf der eigenen Webseite. Kam kaum was zurück. Dann liefen 4 Wochen lang Anzeigen im Umkreis, mit Fotos aus dem Betrieb und Filterfragen vor der Bewerbung.', [('25', 'Bewerbungen'), ('4', 'Wochen Kampagnen-Laufzeit'), ('1', 'Stelle besetzt: Anlagenmechaniker SHK')], '', 'Fallstudie Erwin Schmidt & Sohn: 25 Bewerbungen in 4 Wochen')
FALL_SEN = lambda: fall_gross(SEN_LOGO, 'Benjamin Senftleben', 'Inhaber, Senftleben Haustechnik, Ehingen', 'Senftleben Haustechnik', '/assets/testimonial/senftleben-testimonial-poster.jpg', '/assets/testimonial/senftleben-testimonial.mp4', '2:22', '„Also die Zusammenarbeit würde ich auf jeden Fall jedem empfehlen, weil das auch immer unkompliziert ist."', '„Aufträge haben wir jetzt aktuell genügend", sagt Benjamin Senftleben. Sein Meisterbetrieb in Ehingen, dritte Generation, ist ausgelastet. Trotzdem laufen seit Juli Anzeigen für Badsanierung im Umkreis von 25 km, mit ihm selbst vor der Kamera und Filterfragen vor der Anfrage. Nach dem Startpaket hat er verlängert, damit der Name im Kopf bleibt, wenn das nächste Bad ansteht. Werbung macht man nicht nur, wenn es gut läuft. Das hat er schon in der Meisterschule gelernt.', [('125.000', 'Aufrufe im 25-km-Umkreis'), ('21', 'Bad-Anfragen über den Funnel'), ('10<span class="plus">+</span>', 'Vor-Ort-Termine in 2 Monaten')], 'w', 'Fallstudie Senftleben Haustechnik: 21 Bad-Anfragen in 2 Monaten')

def senftleben_recruiting_karte():
    return f'''<article class="fall-karte rv" data-d="1">
  <div class="vid"><img src="/assets/fotos/senftleben-team.jpg" alt="Das Team von Senftleben Haustechnik" loading="lazy" width="1100" height="725" style="object-position:50% 30%"></div>
  <div class="txt"><span class="chip"><i aria-hidden="true"></i>Recruiting · läuft</span><p class="erg">21 Bewerbungen in 18 Tagen, diesmal fürs Büro.</p><p style="color:var(--sub);font-size:14px;margin-top:-6px">Nach dem Auftrags-Funnel sucht Senftleben Haustechnik über denselben Weg eine Stelle in Lohn- und Buchhaltung.</p>
  <div class="betrieb"><span class="lg"><img src="{SEN_LOGO}" alt="Senftleben Haustechnik"></span><span><b>Senftleben Haustechnik</b><small>Ehingen (Donau) · Recruiting</small></span></div>
  <div class="zahlen"><div class="zahl"><b>21</b><small>Bewerbungen</small></div><div class="zahl"><b>18</b><small>Tage Kampagne</small></div><div class="zahl"><b>1</b><small>Stelle: Lohn &amp; Buchhaltung</small></div></div><p class="zeit">Stand 22.09.2026</p></div>
</article>'''

def sussmann_karte(d=1):
    return f'''<article class="fall-karte rv" data-d="{d}">
  <div class="vid"><img src="/assets/fotos/sussmann-patrick-mirjana.jpg" alt="Patrick Wähnl und Mirjana Sussmann vor dem Firmenwagen der Erich Sussmann GmbH" loading="lazy" width="1100" height="733" style="object-position:50% 25%"></div>
  <div class="txt">
    <span class="chip w"><i aria-hidden="true"></i>Badsanierung · läuft</span>
    <p class="erg">14 Bad-Anfragen, 7+ Termine, erster Auftrag 10.000 € nach 2 Wochen.</p>
    <div class="betrieb"><span class="lg"><img src="{SUS_LOGO}" alt="Sussmann GmbH"></span><span><b>Sussmann GmbH</b><small>Kirchheim · Badsanierung</small></span></div>
    <div class="zahlen">{zahl_html('14', 'Bad-Anfragen', 'w')}{zahl_html('7<span class="plus">+</span>', 'Vor-Ort-Termine', 'w')}{zahl_html('10.000 €', 'Erster Auftrag', 'w')}</div>
    <p class="zeit">Patrick Wähnl, Inhaber · Zahlen aus den ersten 2 Wochen</p>
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
    <div class="bilder">
      <figure class="gross"><img src="/assets/fotos/noah-portrait.jpg" alt="Noah Seelau, Gründer der HandwerksManufaktur" loading="lazy" width="2000" height="1333" style="object-position:68% 30%"></figure>
      <figure class="klein"><img src="/assets/fotos/erwin-schmidt-team.jpg" alt="Das Team von Erwin Schmidt &amp; Sohn beim Shooting" loading="lazy" width="1100" height="733" style="object-position:50% 35%"></figure>
      <div class="kachel"><b>130<span>+</span></b><small>Betriebe seit 2019</small></div>
    </div>
    <div class="txt">
      <p class="kick">Wer dahinter steht</p>
      <h2 class="d">Du beherrschst dein Handwerk. <span class="em w">Wir unseres.</span></h2>
      <p>Ich bin Noah. Seit über sechs Jahren nur Handwerk, über 130 Betriebe, die meisten davon SHK. Wir wissen, was einen Monteur zum Wechseln bringt und wann ein Eigentümer sein neues Bad plant, und bauen deine Kampagne genau darauf. Und wenn dein Umkreis dafür zu klein ist, sagen wir es dir im ersten Gespräch.</p>
      <div class="gruender"><img src="/assets/fotos/noah-kopf.jpg" alt="Noah Seelau" width="500" height="500"><span><b>Noah Seelau</b><small>Gründer · dein direkter Draht vom ersten Call bis zum Reporting</small></span></div>
      <div class="stats hell"><div class="stat"><b>5,0<span class="stern">{ic("star","voll")}</span></b><small>Google-Bewertung aus 57 Bewertungen</small></div><div class="stat"><b>24<span>h</span></b><small>oft bis zur ersten Bewerbung oder Anfrage</small></div><div class="stat"><b>25<span>km</span></b><small>Umkreis, in dem die Anzeigen laufen</small></div></div>
      {'' if not kurz else f'<p style="margin-top:10px"><a class="btn btn-ink" href="{u("/ueber-uns/")}">Mehr über uns <span aria-hidden="true">→</span></a></p>'}
    </div>
  </div></div>
</section>'''

TEAM = [('noah', 'Noah', 'Gründer · Strategie&nbsp;&amp;&nbsp;Vertrieb', '50% 40%'),   # Lächel-Porträt wie auf der HWM-Seite (Noah, 27.09.2026)
        ('robert', 'Robert', 'Videoschnitt&nbsp;&amp;&nbsp;Creative', '50% 18%'),
        (None, 'Rudolf', 'Websites&nbsp;&amp;&nbsp;Anzeigen', '')]   # Noah, 27.09.2026: „mach gesicht von rudolf raus!!! und einfach n R rein … füll die kreise aus"

def team():
    """Wer wir sind — auf jeder Seite (Noah, 27.09.2026: „bau überall noch ne team sektion … nicht so detailreich")."""
    def bild(d, n, r, pos):
        if d is None:   # kein Foto: ausgefüllter Kreis mit Initiale
            return f'<figure class="initiale" aria-hidden="true"><span>{n[0]}</span></figure>'
        return f'''<figure><img src="/assets/team/{d}.jpg" alt="{n}, {r.replace('&nbsp;', ' ').replace('&amp;', '&')}" loading="lazy" width="{800 if d != 'noah' else 312}" height="{1000 if d != 'noah' else 390}" style="object-position:{pos}"></figure>'''
    k = ''.join(f'''<article class="person rv" data-d="{i+1}">{bild(d, n, r, pos)}<div class="txt"><h3>{n}</h3><p>{r}</p></div></article>''' for i, (d, n, r, pos) in enumerate(TEAM))
    return f'''<section class="sec team" id="team"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick rv">Das Team</p><h2 class="d rv">Drei Leute. <span class="em k">Ein Team.</span></h2></div><p class="lead rv">Wer mit dir spricht, sitzt mit denen am Tisch, die deine Kampagne bauen.</p></div>
  <div class="team-grid">{k}</div>
</div></section>'''

def statement(text_html, mitte=False, von=''):
    # Wörter einzeln, damit sich der Satz beim Scrollen füllt; <em> bleibt als Akzent
    teile = re.split(r'(<em>.*?</em>)', text_html)
    out = []
    for t in teile:
        if t.startswith('<em>'):
            for w in t[4:-5].split(): out.append(f'<span class="w em">{w}</span>')
        else:
            for w in t.split(): out.append(f'<span class="w">{w}</span>')
    cite = f'<cite class="rv">{von}</cite>' if von else ''
    return f'<section class="statement{" mitte" if mitte else ""}" aria-label="Leitsatz"><div class="wrap"><p>{" ".join(out)}</p>{cite}</div></section>'

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
      <div class="faq-anker"><div class="wer"><img src="/assets/fotos/noah-kopf.jpg" alt="Noah Seelau" width="500" height="500"><span><b>Deine Frage steht nicht dabei?</b><small>Am Telefon bist du direkt bei mir.</small></span></div><a class="btn btn-ink" href="{TEL_HREF}">{ic('phone','ic')}{TEL}</a></div>
    </div>
    <div class="faq-liste rv" data-d="1">{items}</div>
  </div></div>
</section>'''

def faq_schema(fragen):
    return [{"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": html.unescape(q), "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub('<[^>]+>', '', a))}} for q, a in fragen]}]

def kontakt(h2='Jede Woche ohne zweiten Monteur ist <span class="em w">ein Bad, das ein anderer baut.</span>'):
    return f'''<section class="kontakt" id="kontakt">
  <div class="wrap"><div class="kontakt-karte rv">
    <div>
      <p class="kick">Potenzialanalyse · 30 Minuten · kostenlos</p>
      <h2 class="d">{h2}</h2>
      <p style="margin-top:18px">Das Gespräch kostet nichts und endet mit einer Zahl für deinen Umkreis. Reicht er nicht für Bewerbungen oder Bad-Anfragen, sagen wir es dir. Passt es, bist du in unter 2 Wochen live.</p>
      <div class="mit-wem"><img src="/assets/fotos/noah-kopf.jpg" alt="Noah Seelau" width="500" height="500"><span><b>Noah Seelau</b><small>rechnet selbst mit dir, kein Callcenter dazwischen</small></span></div>
    </div>
    <div class="wahl-spalte">
      <div class="wahl">
        <a href="{CAL_REC}" target="_blank" rel="noopener">{ic('users','ic')}<span><h3>Monteure finden</h3><small>Recruiting-Potenzial deiner Region</small></span><span class="pfeil" aria-hidden="true">→</span></a>
        <a class="w" href="{CAL_LEAD}" target="_blank" rel="noopener">{ic('bath','ic')}<span><h3>Aufträge gewinnen</h3><small>Bad- und Wärmepumpen-Potenzial</small></span><span class="pfeil" aria-hidden="true">→</span></a>
      </div>
      <p class="kontakt-zeile"><a href="{TEL_HREF}">{ic('phone')}{TEL}</a><a href="mailto:{MAIL}">{ic('mail')}{MAIL}</a></p>
      <div class="kunden-reihe" aria-label="Betriebe, mit denen wir arbeiten"><img src="/assets/fotos/erwin-schmidt-monteur.jpg" alt="" width="1100" height="733" style="object-position:40% 20%"><img src="/assets/fotos/sussmann-patrick-mirjana.jpg" alt="" width="1100" height="734" style="object-position:35% 25%"><img src="/assets/fotos/senftleben-benjamin-van.jpg" alt="" width="1100" height="733" style="object-position:62% 22%"><img src="/assets/fotos/shk-05.jpg" alt="" width="1100" height="733" style="object-position:62% 25%"><img src="/assets/fotos/klass-monteur.jpg" alt="" width="880" height="1100" style="object-position:50% 18%"><span>130+ SHK-Betriebe · 5,0 auf Google · erste Bewerbung oft binnen 24 h</span></div>
    </div>
  </div></div>
</section>'''

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
    fotos = [('bad-wanne.jpg', 'Komplettbad mit freistehender Wanne', True), ('bad-dusche.jpg', 'Bodengleiche Dusche', False), ('wp-haus.jpg', 'Wärmepumpe am Einfamilienhaus', False), ('bad-marmor.jpg', 'Bad in Marmoroptik', False), ('wp-garten.jpg', 'Wärmepumpe im Garten', False)]
    f = ''.join(f'<figure class="rv{" quer" if q else ""}" data-d="{i+1}"><img src="/assets/projekte/{d}" alt="{c} — Projekt eines Kunden" loading="lazy"><figcaption>{c}</figcaption></figure>' for i, (d, c, q) in enumerate(fotos))
    return f'''<section class="sec" id="projekte" style="padding-top:0">
  <div class="wrap"><div class="sec-kopf"><div><p class="kick w rv">Wofür das alles läuft</p><h2 class="d rv">Bäder und Wärmepumpen, <span class="em w">fertig gebaut.</span></h2></div><p class="lead rv">Bäder und Wärmepumpen aus Projekten unserer Kunden. Genau solche Aufträge holen die Kampagnen rein.</p></div>
  <div class="galerie">{f}</div></div>
</section>'''

# ── Seiten ────────────────────────────────────────────────────────────────
def seite_start():
    h = kopf('Monteure und Aufträge für SHK-Betriebe: Anzeigen im eigenen Umkreis', 'Monteure, die anfangen wollen, und Bad-Anfragen, die nur du bekommst: Anzeigen mit deinen Leuten in deinem Einzugsgebiet, Filterfragen vor jeder Bewerbung. 130+ Betriebe, 5,0 auf Google.', '/', schema_extra=faq_schema(FAQ_START))
    hero = f'''<section class="hero" id="start">
  <div class="wrap">
    <p class="kick rv">Für inhabergeführte SHK-Betriebe</p>
    <h1 class="h-xl hero-h1 zwei"><span class="zl"><span>Monteure und Bad-Aufträge</span></span><span class="zl"><span>aus deinem Umkreis.</span></span><span class="zl"><span class="em w glut">Live in unter 2 Wochen.</span></span></h1>
    <p class="lead rv" data-d="2">Anzeigen mit deinen Leuten, nur in deinem Einzugsgebiet, Filterfragen vor jeder Bewerbung und Anfrage. Du führst nur noch die Gespräche, den Rest machen wir.</p>
    <div class="hero-cta rv" data-d="3"><a class="btn btn-ink btn-lg" href="{u('/potenzialanalyse/')}">{ic('target','ic')}Potenzialanalyse für meinen Umkreis</a><a class="btn btn-white btn-lg" href="#fallstudien">Was bei Kunden rauskam</a></div>
    <p class="micro rv" data-d="3">30 Minuten, kostenlos, kein Vertrag. Wir sagen dir vorher, ob dein Umkreis genug hergibt.</p>
    <div class="rv" data-d="4">{trust()}</div>
  </div>
  <div class="wrap weit buehne-wrap"><div class="buehne feed still"><div class="raster" aria-hidden="true"></div>
    <div class="feed-innen still">
      {phone('/assets/funnels/erwin-schmidt-jobs-full.jpg', 'Recruiting · Erwin Schmidt &amp; Sohn', '#1E90E8', 'p2')}
      {phone('/assets/funnels/senftleben-leadgen-full.jpg', 'Badsanierung · Senftleben Haustechnik', '#F5762B', 'p3')}
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
    h = kopf('Mitarbeitergewinnung für SHK-Betriebe: Monteure über Social Recruiting', 'Anlagenmechaniker SHK und Kundendiensttechniker über Anzeigen im Umkreis: Bewerbung in 60 Sekunden, vorqualifiziert, mit Fotos aus deinem Betrieb. Fallstudie: 25 Bewerbungen in 4 Wochen.', '/monteure/', dunkel=True, schema_extra=faq_schema(fr))
    body = uhero('Für SHK-Betriebe, die einen Monteur suchen', 'Monteure, die anfangen wollen. <span class="em k">Aus deinem Umkreis.</span>', 'Die guten Monteure suchen nicht, sie sind in Arbeit. Sie wechseln, wenn das richtige Angebot vor ihnen liegt. Wir bringen deins dorthin, wo sie jeden Abend sind: in ihren Feed. Du führst nur noch die Gespräche.', 'Recruiting besprechen', CAL_REC, 'btn-kalt',
        phone('/assets/funnels/senftleben-jobs-full.jpg', 'Recruiting · Senftleben Haustechnik', '#1E90E8', 'links', '2s') + phone('/assets/funnels/erwin-schmidt-jobs-full.jpg', 'Recruiting · Erwin Schmidt &amp; Sohn', '#1E90E8', 'rechts', '0s'))
    body += f'''<section class="sec" id="vorteile"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick k rv">Was anders läuft</p><h2 class="d rv">Bewerbungen von Leuten, die <span class="em k">gerade nicht suchen.</span></h2></div><p class="lead rv">Social Recruiting erreicht Anlagenmechaniker SHK und Kundendiensttechniker dort, wo sie ohnehin sind: auf Instagram und Facebook, nicht auf Stellenportalen, die nur aktiv Suchende sehen.</p></div>
  {vorteile([('', IK['clock'], 'Bewerbung in 60 Sekunden, ohne Lebenslauf', 'Ein paar Fragen im Handy, fertig. Wer sich abends auf der Couch bewirbt, lädt keinen Lebenslauf hoch.'), ('', IK['check'], 'Vorqualifiziert: Gewerk, Erfahrung, Führerschein', 'Filterfragen vor der Bewerbung. Bei dir kommt an, wer zur Stelle passt, mit Kontaktdaten.'), ('', IK['camera'], 'Dein Betrieb als Marke', 'Mit Fotos aus deinem Betrieb: dein Team, dein Lager, deine Baustellen. Kein Stockbild, das jeder hat.')])}
</div></section>'''
    body += leiter(WEGE_ALLE[:4], 'Was du wahrscheinlich schon probiert hast', 'Vier Wege, die <span class="em k">kalt</span> bleiben.', 'Aufkleber, Portal, eigene Seite, Mundpropaganda: Alles erreicht nur die, die schon suchen. Und wer sich über ein Portal bewirbt, ist oft nach ein paar Monaten wieder weg.')
    body += f'''<section class="system" id="system"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick w rv">So kommen Bewerbungen bei dir an</p><h2 class="d rv">Vorgeprüft, mit Kontaktdaten, <span class="em w">im Postfach.</span></h2></div><p class="lead rv">Jede Bewerbung durchläuft den Funnel, bevor sie bei dir landet. Was nicht passt, kommt gar nicht erst an.</p></div>
  <div class="bento">
    <article class="zelle z-a hoch mit-tickets rv">{tickets(TICKETS_REC)}<span class="nr">01</span><h3>So sieht dein Posteingang aus</h3><p>Gewerk, Erfahrung, Führerschein, Entfernung. Du rufst zurück, wen du sehen willst.</p></article>
    <article class="zelle z-b hoch mit-phone rv" data-d="1"><div class="mini-phone" aria-hidden="true"><img src="/assets/funnels/erwin-schmidt-jobs-full.jpg" alt="" loading="lazy"></div><span class="nr">02</span><h3>Der Funnel von Erwin Schmidt &amp; Sohn</h3><p>Fotos aus dem Betrieb, drei Fragen, Bewerbung abgeschickt. Genau diese Strecke brachte 25 Bewerbungen in vier Wochen.</p></article>
    <article class="zelle z-c rv" data-d="2"><div class="bild"><img src="/assets/fotos/erwin-schmidt-team.jpg" alt="Das Team von Erwin Schmidt &amp; Sohn vor dem Betrieb" loading="lazy" width="1100" height="733" style="object-position:50% 35%"></div><span class="nr">03</span><h3>Das Team vor der Kamera</h3><p>Wer bei dir arbeitet, zeigt, wie es bei dir ist. Das überzeugt mehr als jeder Text.</p></article>
    <article class="zelle z-d rv" data-d="3">{UMKREIS}<span class="nr">04</span><h3>Nur in deinem Einzugsgebiet</h3><p>Die Anzeigen laufen im Umkreis deines Betriebs. Wer sich bewirbt, wohnt in Fahrweite.</p></article>
    <article class="zelle z-e rv" data-d="4"><div class="bild"><img src="/assets/fotos/klass-monteur.jpg" alt="Monteur mit Werkzeug im Rohbau" loading="lazy" width="880" height="1100" style="object-position:50% 28%"></div><span class="nr">05</span><h3>Für jede Stelle im SHK</h3><p>Anlagenmechaniker, Kundendiensttechniker, Bäderbauer, Geselle. Eine Kampagne je Stelle, mit eigenem Funnel.</p></article>
  </div>
</div></section>'''
    body += f'''<section class="sec" id="fallstudie"><div class="wrap"><div class="sec-kopf"><div><p class="kick rv">Fallstudie · Recruiting</p><h2 class="d rv">„Wir haben nur nicht gedacht, dass es <span class="em k">so viele</span> sind."</h2></div><p class="lead rv">Erwin Schmidt &amp; Sohn, Sindelfingen. Ein Anlagenmechaniker gesucht, 25 Bewerbungen bekommen, Stelle besetzt.</p></div>{FALL_ESS()}
  <div class="fall-grid" style="margin-top:20px">{senftleben_recruiting_karte()}<article class="fall-karte rv" data-d="2"><div class="vid"><img src="/assets/fotos/klass-werkbank.jpg" alt="Monteur an der Werkbank, Shooting bei Heizung Sanitär Klaß" loading="lazy" width="1100" height="733" style="object-position:50% 40%"></div><div class="txt"><span class="chip"><i aria-hidden="true"></i>Nächster Schritt</span><p class="erg">Welche Stelle ist bei dir offen?</p><p style="color:var(--sub);font-size:15px;margin-top:-4px">In 30 Minuten rechnen wir durch, was in deinem Umkreis an Bewerbungen drin ist.</p><p style="margin-top:auto"><a class="btn btn-kalt" href="{CAL_REC}" target="_blank" rel="noopener">{ic('target','ic')}Recruiting besprechen</a></p></div></article></div></div></section>'''
    body += kaskade('ess') + reels() + statement('Die guten Monteure suchen nicht. Sie sind in Arbeit. Aber sie wechseln, wenn das <em>richtige Angebot</em> vor ihnen liegt.') + team() + faq(fr, 'Fragen zum <span class="em k">Recruiting.</span>') + kontakt('Reden wir über <span class="em k">deine Stelle.</span>')
    return h + body + fuss()

def seite_auftraege():
    fr = [FAQ_ALLE[0], FAQ_ALLE[5], FAQ_ALLE[1], FAQ_ALLE[4], FAQ_ALLE[2]]
    h = kopf('Auftrags-Funnel für Badsanierung & Wärmepumpe: Anfragen für SHK-Betriebe', 'Bad- und Wärmepumpen-Anfragen aus deinem Einzugsgebiet, exklusiv für deinen Betrieb, vorqualifiziert nach Objekt, Baujahr und Eigentum. Fallstudie: 21 Bad-Anfragen in 2 Monaten.', '/auftraege/', dunkel=True, schema_extra=faq_schema(fr))
    body = uhero('Für SHK-Betriebe, die Bäder und Wärmepumpen bauen', 'Bad-Aufträge, die nur du bekommst. <span class="em w">Aus deinem Umkreis.</span>', 'Anzeigen auf deinen Namen, nur in deinem Einzugsgebiet, Filterfragen vor jeder Anfrage. Jede Anfrage gehört dir allein, nicht vier Wettbewerbern gleichzeitig. Du fährst nur noch zum Termin.', 'Potenzial durchrechnen', CAL_LEAD, 'btn-warm',
        phone('/assets/funnels/sussmann-leadgen-hero.jpg', 'Aufträge · Sussmann GmbH', '#F5762B', 'links', '1s') + phone('/assets/funnels/senftleben-leadgen-full.jpg', 'Aufträge · Senftleben Haustechnik', '#F5762B', 'rechts', '0s'), warm=True)
    body += f'''<section class="sec" id="vorteile"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick w rv">Was anders läuft</p><h2 class="d rv">Bäder und Wärmepumpen, <span class="em w">wenn du sie brauchst.</span></h2></div><p class="lead rv">Ein Komplettbad oder eine Wärmepumpe bringt 20.000 bis 50.000 €. Über Mundpropaganda kommen die Projekte, wann sie wollen. Über deinen eigenen Kanal kommen sie, wenn du Kapazität hast.</p></div>
  {vorteile([('w', IK['lock'], 'Exklusiv für deinen Betrieb', 'Keine Portal-Leads, die parallel an vier Betriebe gehen. Deine Fotos, dein Gebiet, deine Anfragen.'), ('w', IK['check'], 'Vorqualifiziert: Objekt, Baujahr, Eigentum, Zeitrahmen', 'Filterfragen vor der Anfrage. Eine Anfrage ohne Adresse und Rückrufnummer zählt bei uns nicht als Anfrage.'), ('w', IK['slider'], 'Regelbar', 'Auf Wunsch auch nur ein, zwei Aufträge im Monat. Du bekommst Anfragen in dem Tempo, das dein Team stemmen kann.')])}
</div></section>'''
    body += galerie()
    body += f'''<section class="system" id="system"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick w rv">So kommen Anfragen bei dir an</p><h2 class="d rv">Eigentümer, Baujahr, Zeitrahmen: <span class="em w">alles dabei.</span></h2></div><p class="lead rv">Jede Anfrage durchläuft den Funnel, bevor sie bei dir landet. Du siehst vor dem ersten Anruf, worum es geht.</p></div>
  <div class="bento">
    <article class="zelle z-a hoch mit-tickets rv">{tickets(TICKETS_LEAD)}<span class="nr">01</span><h3>So sieht dein Posteingang aus</h3><p>Objekt, Baujahr, Eigentum, Zeitrahmen. Du rufst zurück, mit allem, was du für den Termin brauchst.</p></article>
    <article class="zelle z-b hoch mit-phone rv" data-d="1"><div class="mini-phone" aria-hidden="true"><img src="/assets/funnels/senftleben-leadgen-full.jpg" alt="" loading="lazy"></div><span class="nr">02</span><h3>Der Funnel von Senftleben Haustechnik</h3><p>Benjamin selbst vor der Kamera, drei Fragen, Anfrage abgeschickt. 21 Bad-Anfragen in zwei Monaten.</p></article>
    <article class="zelle z-c rv" data-d="2">{UMKREIS}<span class="nr">03</span><h3>25 km rund um deinen Betrieb</h3><p>Die Anzeigen laufen nur in deinem Einzugsgebiet. Bei Senftleben: 125.000 Aufrufe im 25-km-Umkreis.</p></article>
    <article class="zelle z-d rv" data-d="3"><div class="bild"><img src="/assets/fotos/senftleben-team.jpg" alt="Das Team von Senftleben Haustechnik im Lager" loading="lazy" width="1100" height="725" style="object-position:50% 30%"></div><span class="nr">04</span><h3>Der Inhaber vor der Kamera</h3><p>Wer das Bad später baut, zeigt sich in der Anzeige. Das schafft Vertrauen, bevor der erste Anruf kommt.</p></article>
    <article class="zelle z-e rv" data-d="4"><div class="bild"><img src="/assets/projekte/wp-herbst.jpg" alt="Wärmepumpe an einem Wohnhaus im Herbst" loading="lazy" width="825" height="1100"></div><span class="nr">05</span><h3>Bad, Wärmepumpe oder beides</h3><p>Eine Kampagne je Leistung, mit eigenem Funnel und eigenen Filterfragen.</p></article>
  </div>
</div></section>'''
    body += f'''<section class="sec" id="fallstudie"><div class="wrap"><div class="sec-kopf"><div><p class="kick w rv">Fallstudie · Auftrags-Funnel Badsanierung</p><h2 class="d rv">„Dass so schnell so viele Anfragen kommen, <span class="em w">hätte ich nicht gedacht.</span>"</h2></div><p class="lead rv">Senftleben Haustechnik, Ehingen. Ausgelastet, und trotzdem laufen die Anzeigen weiter, damit der Name im Kopf bleibt.</p></div>{FALL_SEN()}
  <div class="fall-grid" style="margin-top:20px">{sussmann_karte()}<article class="fall-karte rv" data-d="2" style="justify-content:center;background:var(--night);color:#fff;border-color:var(--night)"><div class="txt" style="justify-content:center"><p class="kick" style="color:var(--night-sub)">Nach dem Startpaket</p><p class="erg">Werbung macht man nicht nur, wenn es gut läuft.</p><p style="color:var(--night-sub)">Benjamin Senftleben hat nach dem Startpaket verlängert, damit der Name im Kopf bleibt, wenn das nächste Bad ansteht. Das hat er schon in der Meisterschule gelernt.</p><p><a class="btn btn-warm" href="{CAL_LEAD}" target="_blank" rel="noopener">{ic('target','ic')}Potenzial durchrechnen</a></p></div></article></div>
</div></section>'''
    body += kaskade('senftleben') + statement('Ein Komplettbad oder eine Wärmepumpe bringt 20.000 bis 50.000 €. Nur kommen die Projekte, <em>wann sie wollen.</em>') + team() + faq(fr, 'Fragen zur <span class="em w">Badsanierung.</span>') + kontakt('Sehen wir uns <span class="em w">deinen Umkreis</span> an.')
    return h + body + fuss()

def seite_fallstudien():
    h = kopf('Fallstudien: Recruiting und Auftrags-Funnel für SHK-Betriebe', 'Erwin Schmidt & Sohn: 25 Bewerbungen in 4 Wochen. Senftleben Haustechnik: 21 Bad-Anfragen in 2 Monaten. Beide Inhaber im Video, mit den Zahlen aus den ersten Wochen.', '/fallstudien/')
    body = f'''<section class="hero" id="start" style="padding-bottom:0"><div class="wrap"><p class="kick rv">Fallstudien</p><h1 class="h-xl rv" data-d="1">Vier Kampagnen, <span class="em w">die gerade laufen.</span></h1><p class="lead rv" data-d="2">Mit den Zahlen aus den ersten Wochen und den Inhabern vor der Kamera. Keine Hochrechnung, kein „bis zu".</p></div></section>
<section class="sec" id="fallstudie"><div class="wrap"><div class="sec-kopf"><div><p class="kick k rv">Recruiting · Erwin Schmidt &amp; Sohn, Sindelfingen</p><h2 class="d rv">Ein Anlagenmechaniker gesucht. <span class="em k">25 Bewerbungen.</span></h2></div></div>{FALL_ESS()}</div></section>
<section class="sec" id="senftleben" style="padding-top:0"><div class="wrap"><div class="sec-kopf"><div><p class="kick w rv">Auftrags-Funnel · Senftleben Haustechnik, Ehingen</p><h2 class="d rv">Ausgelastet, und trotzdem <span class="em w">21 Bad-Anfragen.</span></h2></div></div>{FALL_SEN()}
<div class="fall-grid" style="margin-top:20px">{sussmann_karte()}{senftleben_recruiting_karte()}</div></div></section>'''
    body += reels() + stimmen() + team() + kontakt()
    return h + body + fuss()

def seite_ueber():
    h = kopf('Über uns: HandwerksManufaktur, Marketing nur für Handwerksbetriebe', 'Seit über sechs Jahren nur Handwerk, über 130 Betriebe betreut, 5,0 auf Google. Wer hinter den Kampagnen für SHK-Betriebe steht und wie wir arbeiten.', '/ueber-uns/')
    body = f'''<section class="hero" id="start" style="padding-bottom:0"><div class="wrap"><p class="kick rv">Über uns</p><h1 class="h-xl rv" data-d="1">Eine Branche. <span class="em w">Seit über sechs Jahren.</span></h1><p class="lead rv" data-d="2">Kein Account-Manager dazwischen, keine Ticketnummer. Du weißt immer, wer an deiner Kampagne sitzt.</p></div></section>
<div style="height:64px"></div>'''
    body += ueber_offen(kurz=False) + team() + praxis_streifen()
    body += f'''<section class="sec" id="wie" style="padding-top:0"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick k rv">Wie wir arbeiten</p><h2 class="d rv">Kleines Team. <span class="em k">Kurze Wege.</span></h2></div><p class="lead rv">Erstgespräch, Strategie und Kampagnenaufbau laufen über einen Tisch. Vom ersten Call bis zum Reporting.</p></div>
  {vorteile([('', IK['compass'], 'Eine Branche, seit über sechs Jahren', 'Nur Handwerk. Wir kennen dein Gewerk, bevor du es erklären musst, und wissen, was einen Monteur zum Wechseln bringt.'), ('', IK['camera'], 'Shooting bei dir im Betrieb', 'Heizungskeller, Lager, Baustelle: Wir kommen zu dir und fotografieren dein Team. Das ist das Material der Kampagne.'), ('', IK['bars'], 'Zahlen statt Bauchgefühl', 'Wir sehen, was jede Anfrage und jede Bewerbung kostet, und regeln nach, wenn etwas nicht läuft.')])}
</div></section>'''
    body += galerie() + stimmen() + kontakt()
    return h + body + fuss()

def seite_potenzial():
    h = kopf('Potenzialanalyse für SHK-Betriebe: in 30 Minuten durchgerechnet', 'Kostenlos und unverbindlich: Wir rechnen durch, was in deiner Region an Bewerbungen von Monteuren oder Anfragen für Bäder und Wärmepumpen drin ist. Termin online aussuchen.', '/potenzialanalyse/')
    body = f'''<section class="hero" id="start" style="padding-bottom:0"><div class="wrap"><p class="kick rv">Potenzialanalyse · 30 Minuten · kostenlos</p><h1 class="h-xl rv" data-d="1">Was ist in deiner Region <span class="em w">drin?</span></h1><p class="lead rv" data-d="2">In 30 Minuten rechnen wir durch, was in deinem Einzugsgebiet möglich ist: Bewerbungen von Monteuren oder Anfragen für Bäder und Wärmepumpen. Kostenlos und unverbindlich.</p></div></section>
<div style="height:56px"></div>
{kontakt('Such dir den Termin aus, <span class="em w">der passt.</span>')}
<section class="sec" id="was" style="padding-top:0"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick k rv">Was in den 30 Minuten passiert</p><h2 class="d rv">Drei Dinge schauen wir uns an.</h2></div><p class="lead rv">Kein Verkaufsgespräch, sondern eine Rechnung für deine Region. Danach weißt du, ob es sich lohnt.</p></div>
  {vorteile([('', IK['map'], 'Dein Einzugsgebiet', 'Wie viele Leute erreichen wir im Umkreis deines Betriebs, und wie viele davon passen zur Stelle oder zum Projekt.'), ('', IK['search'], 'Wer dort schon wirbt', 'Welche Betriebe in deiner Region bereits Anzeigen schalten, und was das für deine Kampagne bedeutet.'), ('w', IK['calculator'], 'Was realistisch drin ist', 'Was eine Bewerbung oder eine Anfrage in deiner Region kostet, und was Setup und Betreuung für dich bedeuten.')])}
</div></section>'''
    body += team() + statement('Kein Verkaufsgespräch. Eine Rechnung für <em>deine Region.</em>') + faq([FAQ_ALLE[2], FAQ_ALLE[0], FAQ_ALLE[4], FAQ_ALLE[6]], 'Vor dem <span class="em k">Termin.</span>')
    return h + body + fuss()

# ── Schreiben ─────────────────────────────────────────────────────────────
SEITEN = {'/': seite_start, '/monteure/': seite_monteure, '/auftraege/': seite_auftraege, '/fallstudien/': seite_fallstudien, '/ueber-uns/': seite_ueber, '/potenzialanalyse/': seite_potenzial}
(AUS/'version.json').write_text('{"v":"%s"}\n' % V, encoding='utf-8')
for pfad, fn in SEITEN.items():
    ziel = AUS / pfad.strip('/') / 'index.html' if pfad != '/' else AUS / 'index.html'
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(optimieren(fn(), pfad=u(pfad)), encoding='utf-8')
    print('✓', ziel.relative_to(REPO))
if LIVE:
    sm = ''.join(f'<url><loc>{DOMAIN}{p}</loc><changefreq>monthly</changefreq><priority>{"1.0" if p == "/" else "0.8"}</priority></url>' for p in SEITEN)
    (REPO/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding='utf-8')
    print('✓ sitemap.xml')
