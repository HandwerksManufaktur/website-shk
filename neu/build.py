#!/usr/bin/env python3
"""Generator der SHK-Seite v3 „Aufgedreht" — erzeugt alle Seiten aus einer Quelle.

Aufruf:  python3 neu/build.py            → schreibt nach neu/ (Vorschau unter /neu/, noindex)
         python3 neu/build.py --live     → schreibt in die Wurzel (Livegang, index)
Alle Texte und Zahlen stammen von der abgenommenen Seite (systeme/website-shk.md) — nichts erfunden.
"""
import sys, os, json, html, re, math
from pathlib import Path
from PIL import Image

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
    h = hashlib.md5((HIER/'styles.css').read_bytes() + (HIER/'main.js').read_bytes()).hexdigest()[:8]
    return h
V = css_js_version()

LOGOS = []
for f in sorted((REPO/'Logos SHK').glob('Logo *.png')):
    if 'Handwerksmanufaktur' in f.name: continue
    im = Image.open(f); r = im.width / im.height
    LOGOS.append((f'/Logos%20SHK/{f.name.replace(" ", "%20")}', f.name[5:-4].replace(' weiss','').replace(' Weiss',''), r))

# ── Bausteine ─────────────────────────────────────────────────────────────
NAV = [('/monteure/', '👷', 'Monteure'), ('/auftraege/', '🛁', 'Aufträge'), ('/fallstudien/', '🎬', 'Fallstudien'), ('/ueber-uns/', '🤝', 'Über uns')]

def kopf(titel, beschreibung, pfad, dunkel=False, schema_extra=None, og=None):
    canon = f'{DOMAIN}{pfad}'
    robots = 'noindex, nofollow' if NOINDEX else 'index, follow, max-image-preview:large, max-snippet:-1'
    org = {
        "@type": "ProfessionalService", "@id": "https://handwerksmanufaktur.digital/#organization",
        "name": "HandwerksManufaktur", "legalName": "HANDWERKSMANUFAKTUR LTD", "url": "https://handwerksmanufaktur.digital/",
        "description": "Marketing-Agentur ausschließlich für Handwerksbetriebe im DACH-Raum. Für SHK-Betriebe: Recruiting-Kampagnen für Monteure und Anlagenmechaniker sowie Auftrags-Kampagnen für Badsanierung und Wärmepumpe.",
        "image": f"{DOMAIN}/og-image.jpg", "logo": {"@type": "ImageObject", "url": f"{DOMAIN}/favicon.png"},
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
    links = ''.join(f'<li><a href="{u(p)}"><span aria-hidden="true">{ic}</span>{n}</a></li>' for p, ic, n in NAV)
    mlinks = ''.join(f'<a href="{u(p)}"><span aria-hidden="true">{ic}</span>{n}</a>' for p, ic, n in NAV)
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<script>document.documentElement.classList.add('js');setTimeout(function(){{if(!window.__lebt)document.documentElement.classList.remove('js')}},3000)</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(titel)}</title>
<meta name="description" content="{html.escape(beschreibung)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">
<meta property="og:type" content="website"><meta property="og:locale" content="de_DE"><meta property="og:site_name" content="HandwerksManufaktur SHK">
<meta property="og:url" content="{canon}"><meta property="og:title" content="{html.escape(titel)}"><meta property="og:description" content="{html.escape(beschreibung)}">
<meta property="og:image" content="{DOMAIN}{og or '/og-image.jpg'}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{'#0B1424' if dunkel else '#F3F6FA'}">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/inter-v20-latin_latin-ext-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/instrument-serif-v5-latin_latin-ext-italic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts/fonts.css">
<link rel="stylesheet" href="{u('/styles.css')}?v={V}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<div class="regler-leiste" aria-hidden="true"></div>
<header class="nav{' dunkel' if dunkel else ''}">
  <div class="wrap">
    <a class="nav-logo" href="{u('/')}" aria-label="HandwerksManufaktur — Startseite">
      <img class="dunkelv" src="/assets/logo-hwm-schwarz.png" alt="HandwerksManufaktur" width="849" height="247">
      <img class="hell" src="/assets/logo-hwm-weiss.png" alt="" width="884" height="282">
    </a>
    <nav aria-label="Hauptnavigation"><ul class="nav-links">{links}<li><a class="nav-cta" href="{u('/potenzialanalyse/')}"><span aria-hidden="true">🎯</span>Potenzialanalyse</a></li></ul></nav>
    <button class="burger" aria-label="Menü" aria-expanded="false" aria-controls="mobilmenu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="mobilmenu" id="mobilmenu">{mlinks}<a class="nav-cta" href="{u('/potenzialanalyse/')}"><span aria-hidden="true">🎯</span>Potenzialanalyse</a></div>
<main>
'''

def fuss():
    return f'''</main>
<footer class="fuss">
  <div class="wrap">
    <div class="oben">
      <div class="marke">
        <img src="/assets/logo-hwm-schwarz.png" alt="HandwerksManufaktur" width="849" height="247">
        <p>Marketing für SHK-Betriebe: Monteure und Aufträge, planbar statt nach Zufall. Ein Team, ein Ansprechpartner, seit über sechs Jahren nur Handwerk.</p>
      </div>
      <div><h4>Leistungen</h4><ul>
        <li><a href="{u('/monteure/')}"><span aria-hidden="true">👷</span>Monteure gewinnen</a></li>
        <li><a href="{u('/auftraege/')}"><span aria-hidden="true">🛁</span>Aufträge gewinnen</a></li>
        <li><a href="{u('/potenzialanalyse/')}"><span aria-hidden="true">🎯</span>Potenzialanalyse</a></li>
      </ul></div>
      <div><h4>HandwerksManufaktur</h4><ul>
        <li><a href="{u('/fallstudien/')}"><span aria-hidden="true">🎬</span>Fallstudien</a></li>
        <li><a href="{u('/ueber-uns/')}"><span aria-hidden="true">🤝</span>Über uns</a></li>
        <li><a href="https://handwerksmanufaktur.digital/"><span aria-hidden="true">🌐</span>Webdesign für Handwerk</a></li>
      </ul></div>
      <div><h4>Kontakt</h4><ul>
        <li><a href="{TEL_HREF}"><span aria-hidden="true">📞</span>{TEL}</a></li>
        <li><a href="mailto:{MAIL}"><span aria-hidden="true">✉️</span>{MAIL}</a></li>
        <li><a href="/impressum/"><span aria-hidden="true">📄</span>Impressum</a></li>
        <li><a href="/datenschutz/"><span aria-hidden="true">🔒</span>Datenschutz</a></li>
        <li><a href="/agb/"><span aria-hidden="true">📑</span>AGB</a></li>
      </ul></div>
    </div>
    <div class="unten"><span><i class="kante" aria-hidden="true"></i>© 2026 HandwerksManufaktur LTD · Alle Rechte vorbehalten.</span><span>Einsatzgebiet: Deutschland · Österreich · Schweiz</span></div>
  </div>
</footer>
<script src="{u('/main.js')}?v={V}" defer></script>
</body>
</html>
'''

GOOGLE_G = '<svg class="g" viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.6l6.7-6.7C35.6 2.6 30.2 0 24 0 14.6 0 6.5 5.4 2.6 13.3l7.8 6.1C12.3 13.5 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.6h12.7c-.6 3-2.2 5.5-4.7 7.2l7.5 5.8c4.4-4.1 7-10.1 7-17.1z"/><path fill="#FBBC05" d="M10.4 28.6A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.1.8-4.6l-7.8-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.7l7.8-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.5-5.8c-2.1 1.4-4.9 2.3-8.4 2.3-6.3 0-11.7-4-13.6-9.9l-7.8 6.1C6.5 42.6 14.6 48 24 48z"/></svg>'

def trust(hell=True):
    return '<p class="trust"><span><span class="stern" aria-hidden="true">★★★★★</span> <b>5,0</b> auf Google</span><span>·</span><span><b>120+</b> Betriebe</span><span>·</span><span><b>Spezialisiert</b> auf SHK</span></p>'

def phone(img, etikett, farbe, klasse='', delay='0s'):
    return f'''<div class="phone {klasse}" aria-hidden="true"><div class="scroller"><img src="{img}" alt="" loading="lazy" style="--d:{delay}"></div><span class="etikett"><i style="background:{farbe}"></i>{etikett}</span></div>'''

def reel_phone(f, etikett, klasse):
    return f'''<div class="phone reel {klasse}" aria-hidden="true"><video muted loop playsinline preload="none" data-quelle="/assets/reels/{f}.mp4"></video><span class="etikett"><i style="background:#3DDC84"></i>{etikett}</span></div>'''

def hero_zettel():
    z = [('📩', 'Neue Bewerbung', 'Anlagenmechaniker SHK · 8 Jahre · 12 km', 'qualifiziert ✓'), ('🛁', 'Neue Anfrage', 'Komplettbad · EFH Bj. 1994 · Eigentümer', 'vorqualifiziert ✓'), ('📩', 'Neue Bewerbung', 'Kundendiensttechniker · ab sofort · 7 km', 'qualifiziert ✓'), ('🔥', 'Neue Anfrage', 'Wärmepumpe · Ölheizung Bj. 2001 · 160 m²', 'vorqualifiziert ✓'), ('📩', 'Neue Bewerbung', 'Bäderbauer · Führerschein BE · 15 km', 'qualifiziert ✓'), ('🛁', 'Neue Anfrage', 'Bad barrierefrei · Eigentumswohnung · zeitnah', 'vorqualifiziert ✓')]
    return ''.join(f'<div class="ticket"><span class="tic">{ic}</span><span><b>{t}</b><small>{sub}</small></span><span class="ok">{ok}</span></div>' for ic, t, sub, ok in z)

def logo_band():
    imgs = ''.join(f'<img src="{src}" alt="{html.escape(name)}" loading="lazy"{" class=wide" if r >= 3.6 else ""}>' for src, name, r in LOGOS)
    imgs2 = ''.join(f'<img src="{src}" alt="" loading="lazy"{" class=wide" if r >= 3.6 else ""}>' for src, name, r in LOGOS[::-1])
    return f'''<section class="band" aria-label="Betriebe, mit denen wir arbeiten">
  <div class="wrap"><div class="band-innen rv">
    <p class="band-t">Über <b>130 Betriebe</b> setzen auf uns. Hier ein Ausschnitt</p>
    <div class="marq">{imgs}{imgs}</div>
    <div class="marq rueck">{imgs2}{imgs2}</div>
  </div></div>
</section>'''

def kinetik():
    return '''<section class="kinetik" aria-hidden="true">
  <div><span class="zeile">Badsanierungen<span class="sep">·</span>Wärmepumpen<span class="sep">·</span>Neue Monteure<span class="sep">·</span>Badsanierungen<span class="sep">·</span>Wärmepumpen</span></div>
  <div><span class="zeile serif">Planbar statt Zufall · <b>Messbar statt Bauchgefühl</b> · Planbar statt Zufall · <b>Messbar statt Bauchgefühl</b></span></div>
</section>'''

WEGE_ALLE = [
    ('🖥️', 'Stellenportal', 'Sehen nur die, die aktiv suchen. Wer in Arbeit ist, öffnet kein Portal.'),
    ('🚐', 'Aufkleber mit QR-Code', 'Auf dem Firmenwagen. Wer ihn liest, steht gerade im Stau.'),
    ('🌐', 'Die Stelle auf der eigenen Webseite', 'Wer sie findet, sucht schon. Alle anderen kommen nie vorbei.'),
    ('🗣️', 'Mundpropaganda', 'Bringt Großprojekte, wann sie wollen: monatelang nichts, dann drei gleichzeitig.'),
    ('📇', 'Lead-Portale', 'Dieselbe Anfrage geht an vier Betriebe. Du telefonierst um die Wette mit Preisvergleichern.'),
]
def leiter(wege=WEGE_ALLE, kick='Was du wahrscheinlich schon probiert hast', h2='Fünf Wege, die <span class="em k">kalt</span> bleiben.', lead='Aus hunderten Gesprächen mit SHK-Inhabern: So wird bisher gesucht. Und so wenig kommt zurück.'):
    karten = ''.join(f'''<article class="weg rv" data-d="{i+1}"><span class="x" aria-hidden="true">✕</span><div class="ic" aria-hidden="true">{ic}</div><h3>{t}</h3><p>{p}</p></article>''' for i, (ic, t, p) in enumerate(wege))
    return f'''<section class="probiert" id="probiert">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick k rv">{kick}</p><h2 class="d rv">{h2}</h2></div><p class="lead rv">{lead}</p></div>
    <div class="leiter n{len(wege)}">{karten}<div class="ende rv" data-d="{len(wege)+1}"><span>„Kam kaum was zurück."<small>Florian Schmidt, Erwin Schmidt &amp; Sohn, über die Suche vor der Kampagne</small></span></div></div>
  </div>
</section>'''

def problem():
    karten = [
        ('🔧', 12, 'Der Kleinkram frisst den Tag', 'Notdienst, tropfende Ventile, Wartungen, der Kalender ist voll. Ein Inhaber hat es so gesagt: fünfmal vor Ort, sechsmal Kuchen bei der Oma, und am Ende bleibt nichts hängen.'),
        ('🎲', 20, 'Großprojekte kommen nach Zufall', 'Ein Komplettbad oder eine Wärmepumpe bringt 20.000 bis 50.000 €. Nur kommen die Projekte, wann sie wollen: monatelang nichts, und dann drei gleichzeitig, wenn ohnehin keine Kapazität da ist. Über Mundpropaganda lässt sich das nicht steuern.'),
        ('👷', 8, 'Der Auftrag ist da, der Monteur nicht', 'Kommt das große Projekt dann doch, fehlt der Mann dafür. Ein Inhaber hat es so gesagt: er schiebt Aufträge vom letzten Jahr vor sich her, weil das Personal fehlt. Und wer schon in Arbeit ist, schaut nicht auf Stellenportalen nach.'),
    ]
    k = ''.join(f'''<article class="kalt-karte rv" data-d="{i+1}"><div class="mini" style="--grad:{g}%" aria-hidden="true"><span>{ic}</span></div><div><h3>{t}</h3><p>{p}</p></div></article>''' for i, (ic, g, t, p) in enumerate(karten))
    return f'''<section class="problem" id="problem">
  <div class="wrap"><div class="problem-grid">
    <div class="links"><p class="kick k rv">Das eigentliche Problem</p><h2 class="d rv">Entweder fehlen die Aufträge. <span class="em k">Oder die Leute dafür.</span></h2><p class="lead rv" style="margin-top:18px">In hunderten Gesprächen mit SHK-Inhabern hören wir fast immer dasselbe: Es hakt an einem von beiden, und meistens hängt das eine am anderen.</p><p class="rv" style="margin-top:26px"><a class="btn btn-ink" href="{u('/potenzialanalyse/')}"><span class="ic" aria-hidden="true">🎯</span>Potenzial durchrechnen</a></p></div>
    <div class="kalt-liste">{k}</div>
  </div></div>
</section>'''

TICKETS_REC = [('👷', 'Anlagenmechaniker SHK', '8 Jahre Erfahrung · Führerschein B · 12 km entfernt', 'qualifiziert ✓'), ('🔧', 'Kundendiensttechniker', 'Heizung &amp; Sanitär · ab sofort · 7 km entfernt', 'qualifiziert ✓'), ('👷', 'Geselle SHK', '3 Jahre Erfahrung · wechselwillig · 20 km entfernt', 'qualifiziert ✓'), ('🛁', 'Bäderbauer', 'Komplettbäder · Führerschein BE · 15 km entfernt', 'qualifiziert ✓')]
TICKETS_LEAD = [('🛁', 'Komplettbad', 'EFH · Baujahr 1994 · Eigentümer · Start im Frühjahr', 'vorqualifiziert ✓'), ('🔥', 'Wärmepumpe', 'Ölheizung Bj. 2001 · 160 m² · Eigentümer', 'vorqualifiziert ✓'), ('🛁', 'Bad barrierefrei', 'Bodengleiche Dusche · Eigentumswohnung · zeitnah', 'vorqualifiziert ✓'), ('🔥', 'Heizungstausch', 'Gas raus, Wärmepumpe rein · EFH · Förderung geklärt', 'vorqualifiziert ✓')]
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
    <div class="sec-kopf"><div><p class="kick w rv">So wird es warm</p><h2 class="d rv">Ein eigener Kanal. <span class="em w">Deine</span> Anfragen, <span class="em w">deine</span> Bewerber.</h2></div><p class="lead rv">Der Ablauf ist für Recruiting und Auftragsgewinnung derselbe. In unter zwei Wochen läuft die erste Kampagne.</p></div>
    <div class="bento">
      <article class="zelle z-a hoch rv"><div class="bild"><img src="/assets/fotos/klass-team-van.jpg" alt="Team eines SHK-Betriebs vor dem Firmenwagen — Shooting für die Kampagne" loading="lazy" width="1100" height="732" style="object-position:50% 30%"></div><span class="nr">01</span><h3>Anzeigen mit Fotos aus deinem Betrieb</h3><p>Dein Betrieb als Marke, mit deinen Leuten vor der Kamera. Wir kommen für das Shooting zu dir: Heizungskeller, Lager, Baustelle.</p></article>
      <article class="zelle z-b hoch mit-panels rv" data-d="1"><div class="mini-phones" aria-hidden="true"><div class="mini-phone" style="--off:0%"><img src="/assets/funnels/erwin-schmidt-jobs-full.jpg" alt="" loading="lazy"></div><div class="mini-phone" style="--off:31%"><img src="/assets/funnels/erwin-schmidt-jobs-full.jpg" alt="" loading="lazy"></div><div class="mini-phone" style="--off:62%"><img src="/assets/funnels/senftleben-leadgen-full.jpg" alt="" loading="lazy"></div></div><span class="nr">02</span><h3>Filterfragen vor der Bewerbung</h3><p>Bewerbung in 60 Sekunden, ohne Lebenslauf. Vorqualifiziert nach Gewerk, Erfahrung und Führerschein. Bei Aufträgen: Objekt, Baujahr, Eigentum, Zeitrahmen.</p></article>
      <article class="zelle z-c rv" data-d="2">{UMKREIS}<span class="nr">03</span><h3>Nur dein Einzugsgebiet</h3><p>Läuft auf deinen Namen, bespielt nur deinen Umkreis. Jede Anfrage gehört dir allein, nicht vier Wettbewerbern gleichzeitig.</p></article>
      <article class="zelle z-d mit-tickets rv" data-d="3">{tickets(tk)}<span class="nr">04</span><h3>So kommt es bei dir an</h3><p>Mit Kontaktdaten und vorgeprüft. Meist nach sieben Tagen die ersten.</p></article>
      <article class="zelle z-e rv" data-d="4"><div class="bild"><img src="/assets/fotos/shk-02.jpg" alt="Inhaber und Mitarbeiter am Laptop" loading="lazy" width="1100" height="732" style="object-position:50% 30%"></div><span class="nr">05</span><h3>Wir sehen, was jede Anfrage kostet</h3><p>Was funktioniert, bekommt mehr Budget. Auf Wunsch gedrosselt auf ein, zwei Aufträge im Monat.</p></article>
    </div>
  </div>
</section>'''

def hebel():
    return f'''<section class="hebel" id="hebel">
  <div class="wrap">
    <div class="sec-kopf mitte"><p class="kick rv">Zwei Hebel, ein System</p><h2 class="d rv">Was fehlt dir gerade: <span class="em k">Leute</span> oder <span class="em w">Aufträge</span>?</h2></div>
    <div class="hebel-grid">
      <a class="hebel-karte rv" href="{u('/monteure/')}"><div class="txt"><span class="chip"><span aria-hidden="true">👷</span>Hebel 1 · Recruiting</span><h3>Mitarbeitergewinnung für SHK-Monteure.</h3><ul><li>Bewerbung in 60 Sekunden, ohne Lebenslauf</li><li>Vorqualifiziert: Gewerk, Erfahrung, Führerschein</li><li>Dein Betrieb als Marke, mit Fotos aus deinem Betrieb</li></ul><span class="btn btn-white">Recruiting ansehen <span aria-hidden="true">→</span></span></div><div class="bild"><img src="/assets/fotos/erwin-schmidt-monteur.jpg" alt="Monteur eines SHK-Betriebs mit Werkzeug" loading="lazy" width="1100" height="733" style="object-position:55% 25%"></div></a>
      <a class="hebel-karte w rv" data-d="1" href="{u('/auftraege/')}"><div class="txt"><span class="chip"><span aria-hidden="true">🛁</span>Hebel 2 · Aufträge</span><h3>Auftrags-Funnel für Bad &amp; Wärmepumpe.</h3><ul><li>Exklusiv für deinen Betrieb</li><li>Vorqualifiziert: Objekt, Baujahr, Eigentum, Zeitrahmen</li><li>Regelbar, auf Wunsch nur 1–2 Aufträge im Monat</li></ul><span class="btn btn-white">Aufträge ansehen <span aria-hidden="true">→</span></span></div><div class="bild"><img src="/assets/fotos/senftleben-team.jpg" alt="Das Team von Senftleben Haustechnik" loading="lazy" width="1100" height="725" style="object-position:50% 30%"></div></a>
    </div>
  </div>
</section>'''

ESS_LOGO = '/Logos%20SHK/Logo%20Erwin%20Schmidt%20weiss.png'
SEN_LOGO = '/Logos%20SHK/Logo%20Senftleben%20Haustechnik%20weiss.png'
SUS_LOGO = '/Logos%20SHK/Logo%20Sussmann%20weiss.png'

def fall_karte(logo, name, ort, chip, chipk, poster, video, dauer, zitat, zahlen, zeit, d=0, alt=''):
    pos = '8%' if 'senftleben' in poster else '50%'
    z = ''.join(f'<div class="zahl {chipk}"><b>{b}</b><small>{s}</small></div>' for b, s in zahlen)
    return f'''<article class="fall-karte rv" data-d="{d}">
  <div class="vid"><video preload="none" poster="{poster}" playsinline style="object-position:50% {pos}"><source src="{video}" type="video/mp4">Dein Browser kann dieses Video nicht abspielen.</video><button class="play" type="button" aria-label="Video ansehen"><span><span aria-hidden="true">▶</span> Video ansehen · {dauer}</span></button></div>
  <div class="txt">
    <span class="chip {chipk}"><i aria-hidden="true"></i>{chip}</span>
    <blockquote>{zitat}</blockquote>
    <div class="betrieb"><img src="{logo}" alt="{html.escape(name)}" loading="lazy"><span><b>{name}</b><small>{ort}</small></span></div>
    <div class="zahlen">{z}</div>
    <p class="zeit">{zeit}</p>
  </div>
</article>'''

def fallstudien_teaser():
    return f'''<section class="fall" id="fallstudien">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick rv">Ausgewählte Kampagnen</p><h2 class="d rv">Funnels, die <span class="em w">liefern.</span></h2></div><p class="lead rv">Drei Kampagnen, die gerade laufen, mit den Zahlen aus den ersten Wochen. Die Inhaber vor der Kamera.</p></div>
    <div class="fall-grid drei">
      {fall_karte(ESS_LOGO, 'Erwin Schmidt &amp; Sohn', 'Sindelfingen · SHK-Familienbetrieb in 3. Generation', 'Recruiting-Funnel · läuft', '', '/assets/testimonial/ess-testimonial-poster.jpg', '/assets/testimonial/ess-testimonial.mp4', '2:48', '„Wir haben nur nicht gedacht, dass es so viele sind."', [('25', 'Bewerbungen'), ('1', 'Stelle besetzt'), ('4', 'Wochen Laufzeit')], 'Florian Schmidt, Geschäftsführer · Anlagenmechaniker SHK, erste 4 Wochen')}
      {fall_karte(SEN_LOGO, 'Senftleben Haustechnik', 'Ehingen (Donau) · Badsanierung in 3. Generation', 'Auftrags-Funnel · läuft', 'w', '/assets/testimonial/senftleben-testimonial-poster.jpg', '/assets/testimonial/senftleben-testimonial.mp4', '2:22', '„Dass so schnell so viele Anfragen kommen, hätte ich nicht gedacht."', [('125.000', 'Aufrufe im Umkreis'), ('21', 'Bad-Anfragen'), ('10<span class="plus">+</span>', 'Vor-Ort-Termine')], 'Benjamin Senftleben, Inhaber · 25-km-Umkreis, erste 2 Monate', 1)}
      {sussmann_karte(2)}
    </div>
    <p class="rv" style="text-align:center;margin-top:32px"><a class="btn btn-white" href="{u('/fallstudien/')}">Alle Fallstudien in voller Länge <span aria-hidden="true">→</span></a></p>
  </div>
</section>'''

def fall_gross(logo, name, rolle, betrieb, poster, video, dauer, zitat, absatz, zahlen, chipk, aria):
    z = ''.join(f'<div class="zahl {chipk}"><b>{b}</b><small>{s}</small></div>' for b, s in zahlen)
    return f'''<article class="fall-gross rv">
  <div class="vid"><video preload="none" poster="{poster}" playsinline aria-label="{aria}" style="object-position:50% {'8%' if 'senftleben' in poster else '50%'}"><source src="{video}" type="video/mp4">Dein Browser kann dieses Video nicht abspielen.</video><button class="play" type="button" aria-label="Video ansehen"><span><span aria-hidden="true">▶</span> Video ansehen · {dauer}</span></button></div>
  <div class="txt">
    <div><blockquote>{zitat}</blockquote><p style="margin-top:18px">{absatz}</p></div>
    <div class="zahlen">{z}</div>
    <div class="person"><img src="{logo}" alt="{html.escape(betrieb)}" loading="lazy"><span><b>{name}</b>{rolle}</span></div>
  </div>
</article>'''

FALL_ESS = lambda: fall_gross(ESS_LOGO, 'Florian Schmidt', 'Geschäftsführer, Erwin Schmidt &amp; Sohn GmbH, Sindelfingen', 'Erwin Schmidt & Sohn', '/assets/testimonial/ess-testimonial-poster.jpg', '/assets/testimonial/ess-testimonial.mp4', '2:48', '„Ich kann es jedem nur empfehlen: Wenn wirklich Personalmangel da ist, dass man den Schritt geht."', 'Erwin Schmidt &amp; Sohn in Sindelfingen, SHK-Familienbetrieb in dritter Generation, suchte einen Anlagenmechaniker für den Kundendienst. Probiert war schon einiges: Aufkleber mit QR-Code auf den Firmenwagen, die Stelle auf der eigenen Webseite. Kam kaum was zurück. Dann liefen 4 Wochen lang Anzeigen im Umkreis, mit Fotos aus dem Betrieb und Filterfragen vor der Bewerbung.', [('25', 'Bewerbungen'), ('4', 'Wochen Kampagnen-Laufzeit'), ('1', 'Stelle besetzt: Anlagenmechaniker SHK')], '', 'Fallstudie Erwin Schmidt & Sohn: 25 Bewerbungen in 4 Wochen')
FALL_SEN = lambda: fall_gross(SEN_LOGO, 'Benjamin Senftleben', 'Inhaber, Senftleben Haustechnik, Ehingen', 'Senftleben Haustechnik', '/assets/testimonial/senftleben-testimonial-poster.jpg', '/assets/testimonial/senftleben-testimonial.mp4', '2:22', '„Also die Zusammenarbeit würde ich auf jeden Fall jedem empfehlen, weil das auch immer unkompliziert ist."', '„Aufträge haben wir jetzt aktuell genügend", sagt Benjamin Senftleben. Sein Meisterbetrieb in Ehingen, dritte Generation, ist ausgelastet. Trotzdem laufen seit Juli Anzeigen für Badsanierung im Umkreis von 25 km, mit ihm selbst vor der Kamera und Filterfragen vor der Anfrage. Nach dem Startpaket hat er verlängert, damit der Name im Kopf bleibt, wenn das nächste Bad ansteht. Werbung macht man nicht nur, wenn es gut läuft. Das hat er schon in der Meisterschule gelernt.', [('125.000', 'Aufrufe im 25-km-Umkreis'), ('21', 'Bad-Anfragen über den Funnel'), ('10<span class="plus">+</span>', 'Vor-Ort-Termine in 2 Monaten')], 'w', 'Fallstudie Senftleben Haustechnik: 21 Bad-Anfragen in 2 Monaten')

def senftleben_recruiting_karte():
    return f'''<article class="fall-karte rv" data-d="1">
  <div class="vid"><img src="/assets/fotos/senftleben-team.jpg" alt="Das Team von Senftleben Haustechnik" loading="lazy" width="1100" height="725" style="object-position:50% 30%"></div>
  <div class="txt"><span class="chip"><i aria-hidden="true"></i>Recruiting-Funnel · läuft</span><blockquote>Zweite Kampagne beim selben Betrieb, diesmal fürs Büro.</blockquote><p style="color:var(--sub);font-size:14px;margin-top:-6px">Nach dem Auftrags-Funnel sucht Senftleben Haustechnik über denselben Weg eine Stelle in Lohn- und Buchhaltung.</p>
  <div class="betrieb"><img src="{SEN_LOGO}" alt="Senftleben Haustechnik" loading="lazy"><span><b>Senftleben Haustechnik</b><small>Ehingen (Donau) · Recruiting</small></span></div>
  <div class="zahlen"><div class="zahl"><b>21</b><small>Bewerbungen</small></div><div class="zahl"><b>18</b><small>Tage Kampagne</small></div><div class="zahl"><b>1</b><small>Stelle: Lohn &amp; Buchhaltung</small></div></div><p class="zeit">Stand 22.09.2026</p></div>
</article>'''

def sussmann_karte(d=1):
    return f'''<article class="fall-karte rv" data-d="{d}">
  <div class="vid"><img src="/assets/fotos/shk-02.jpg" alt="Patrick und Mirjana Sussmann in ihrem Betrieb" loading="lazy" width="1100" height="732" style="object-position:50% 30%"></div>
  <div class="txt"><span class="chip w"><i aria-hidden="true"></i>Auftrags-Funnel · läuft</span><blockquote>„Wir kriegen auch immer wieder E-Mails: Sie hat unsere Werbung bei Instagram gesehen und voll sympathisch (…)"</blockquote><p style="color:var(--sub);font-size:14px;margin-top:-6px">Benjamin Senftleben über das, was neben den Anfragen noch ankommt.</p>
  <div class="betrieb"><img src="{SUS_LOGO}" alt="Sussmann GmbH" loading="lazy"><span><b>Sussmann GmbH</b><small>Kirchheim · Badsanierung</small></span></div>
  <div class="zahlen"><div class="zahl w"><b>14</b><small>Bad-Anfragen</small></div><div class="zahl w"><b>7<span class="plus">+</span></b><small>Vor-Ort-Termine</small></div><div class="zahl w"><b>10.000 €</b><small>Erster Auftrag</small></div></div><p class="zeit">Patrick Wähnl, Sussmann GmbH · erster Auftrag nach 2 Wochen Kampagne · Stand 22.09.2026</p></div>
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
STIMMEN_LOGO = {'Franz Gallenberger': 'Logo Franz Gallenberger weiss.png', 'Benjamin Senftleben': 'Logo Senftleben Haustechnik weiss.png', 'Lanzinger GmbH': 'Logo Lanzinger GmbH weiss.png', 'Andrea Süßmeier': 'Logo Suessmeier Heizungstechnik weiss.png', 'Hannes Schmidt GmbH': 'Logo Hannes Schmidt GmbH Weiss.png', 'Alisa Kirchner': 'Logo Kirchner weiss.png', 'Isabella Rauch': 'Logo Autohaus Ressle weiss.png'}
def stimmen():
    k = ''.join(f'<article class="stimme"><div class="kopf"><span class="lg"><img src="/Logos%20SHK/{STIMMEN_LOGO[n].replace(" ", "%20")}" alt="{html.escape(b)}" loading="lazy"></span><span class="stern" aria-label="5 von 5 Sternen">★★★★★</span></div><blockquote>{z}</blockquote><div class="wer"><span><b>{n}</b><small>{b}</small></span></div></article>' for n, b, z in STIMMEN)
    return f'''<section class="stimmen" id="stimmen">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick rv">Stimmen aus der Branche</p><h2 class="d rv">Wir könnten viel erzählen. <span class="em k">Betriebe erzählen es besser.</span></h2></div><p class="rv"><span class="google">{GOOGLE_G}<span>5,0 <span class="stern" aria-hidden="true">★★★★★</span></span><span style="font-weight:500;color:var(--sub)">Google Bewertungen</span></span></p></div>
    <div class="stimmen-marq"><div class="spur">{k}{k}</div></div>
  </div>
</section>'''

SCHRITTE = [('🔍', 'Potenzialanalyse', 'Wir schauen uns dein Einzugsgebiet an: Wie viele Leute erreichen wir, wer wirbt dort schon, was ist realistisch drin.', 'kostet nichts'), ('🎯', 'Strategie &amp; Setup', 'Zielgruppe, Botschaft und Funnel bauen wir auf dein Ziel zu: Monteure, Aufträge oder beides.', 'unter 2 Wochen'), ('🚀', 'Kampagne live', 'Meist nach sieben Tagen kommen die ersten Anfragen oder Bewerbungen rein, mit Kontaktdaten und vorgeprüft.', 'ab Tag 7'), ('📈', 'Optimieren &amp; Skalieren', 'Wir sehen, was jede Anfrage und jede Bewerbung kostet. Was funktioniert, bekommt mehr Budget.', 'laufend')]
def ablauf():
    s = ''.join(f'<article class="schritt rv" data-d="{i+1}"><span class="nr" aria-hidden="true">0{i+1}</span><div class="ic" aria-hidden="true">{ic}</div><h3>{t}</h3><p>{p}</p><span class="dauer">{d}</span></article>' for i, (ic, t, p, d) in enumerate(SCHRITTE))
    punkte = ''.join(f'<b style="left:{(i+.5)/4*100:.1f}%"></b>' for i in range(4))
    return f'''<section class="ablauf" id="ablauf">
  <div class="wrap">
    <div class="sec-kopf"><div><p class="kick w rv">Unser Vorgehen</p><h2 class="d rv">Vier Schritte, bis es <span class="em w">läuft.</span></h2></div><p class="lead rv">Der Ablauf ist für Recruiting und Auftragsgewinnung derselbe. In unter zwei Wochen läuft die erste Kampagne.</p></div>
    <div class="rohr-wrap"><div class="rohr" aria-hidden="true"><i></i>{punkte}</div><div class="schritte">{s}</div></div>
  </div>
</section>'''

def ueber_insel(kurz=True):
    return f'''<section class="ueber" id="ueber-uns">
  <div class="wrap"><div class="insel rv">
    <div class="txt">
      <p class="kick">Wer dahinter steht</p>
      <h2 class="d">Du beherrschst dein Handwerk. <span class="em w">Wir unseres.</span></h2>
      <p>Ich bin Noah. Seit über sechs Jahren dreht sich bei uns alles um eine Branche: das Handwerk. Über 120 Betriebe später wissen wir ziemlich genau, was funktioniert und was du dir sparen kannst.</p>
      <p><b>Wir kennen dein Gewerk, bevor du es erklären musst.</b> Wir wissen, was einen Monteur zum Wechseln bringt und wann ein Eigentümer bereit für sein neues Bad ist, und bauen deine Kampagne genau darauf.</p>
      <div class="gruender"><img src="/assets/fotos/noah-rund.png" alt="Noah Seelau" width="500" height="500"><span><b>Noah Seelau</b><small>Gründer · dein direkter Draht vom ersten Call bis zum Reporting</small></span></div>
      <div class="stats"><div class="stat"><b>120<span>+</span></b><small>Handwerksbetriebe betreut</small></div><div class="stat"><b>5,0<span>★</span></b><small>Google-Bewertung aus 57 Bewertungen</small></div><div class="stat"><b>Ø 7</b><small>Tage bis zur ersten Anfrage oder Bewerbung</small></div></div>
      {'' if not kurz else f'<p style="margin-top:10px"><a class="btn btn-glass" href="{u("/ueber-uns/")}">Mehr über uns <span aria-hidden="true">→</span></a></p>'}
    </div>
    <div class="foto"><img src="/assets/fotos/noah-portrait.jpg" alt="Noah Seelau, Gründer der HandwerksManufaktur" loading="lazy" width="2000" height="1333" style="object-position:68% 30%"></div>
  </div></div>
</section>'''

def statement(text_html, mitte=False):
    # Wörter einzeln, damit sich der Satz beim Scrollen füllt; <em> bleibt als Akzent
    teile = re.split(r'(<em>.*?</em>)', text_html)
    out = []
    for t in teile:
        if t.startswith('<em>'):
            for w in t[4:-5].split(): out.append(f'<span class="w em">{w}</span>')
        else:
            for w in t.split(): out.append(f'<span class="w">{w}</span>')
    return f'<section class="statement{" mitte" if mitte else ""}" aria-label="Leitsatz"><div class="wrap"><p>{" ".join(out)}</p></div></section>'

FAQ_ALLE = [
    ('Wir haben schon genug zu tun, warum dann ihr?', 'Voll ist der Kalender bei fast jedem Betrieb. Die Frage ist, womit. Wenn du mehr margenstarke Badsanierungen und Wärmepumpen statt Kleinreparaturen willst, bringen wir genau diese Anfragen planbar rein.'),
    ('Wie schnell kommen die ersten Anfragen?', 'In den meisten Fällen gehen erste qualifizierte Anfragen innerhalb von 7 Tagen nach Kampagnenstart ein. Das Setup davor dauert unter 2 Wochen.'),
    ('Wie funktioniert Mitarbeitergewinnung über Social Media?', 'Social Recruiting erreicht Anlagenmechaniker SHK und Kundendiensttechniker dort, wo sie ohnehin sind: auf Instagram und Facebook, nicht auf Stellenportalen, die nur aktiv Suchende sehen. Die meisten Fachkräfte im Handwerk sind in Arbeit und wechseln nur, wenn ein Angebot vor ihnen landet. Wir spielen deine Stellen als Anzeige in deinem Einzugsgebiet aus, die Bewerbung dauert 60 Sekunden ohne Lebenslauf, und du bekommst nur vorqualifizierte Kandidaten mit Gewerk, Erfahrung und Führerschein.'),
    ('Was, wenn wir die Anfragen nicht abarbeiten können?', 'Die Kampagne lässt sich über die Qualifizierung drosseln, auf Wunsch auf ein, zwei Aufträge im Monat. Du bekommst Anfragen in dem Tempo, das dein Team stemmen kann. Es geht um planbare Auslastung, nicht um Masse.'),
    ('Was unterscheidet euch von Lead-Portalen?', 'Portal-Leads werden parallel an mehrere Betriebe verkauft, du telefonierst um die Wette mit Preisvergleichern. Wir bauen stattdessen einen eigenen Kanal in deinem Namen: deine Fotos, dein Gebiet, deine Anfragen. Und eine Anfrage ohne Adresse und Rückrufnummer zählt bei uns nicht als Anfrage.'),
    ('Muss ich mich lange binden?', 'Nein. Eine Anlaufzeit von 3 Monaten gilt, damit das System seine volle Wirkung entfalten kann. Danach monatlich kündbar. Kein Knebelvertrag.'),
    ('Was, wenn Personal unser Engpass ist?', 'Dann starten wir mit Recruiting statt Auftragsgewinnung: gezielte Kampagnen für Monteure in deiner Region, dieselbe Methodik mit anderem Ziel. Siehst du oben live bei Senftleben und Erwin Schmidt &amp; Sohn.'),
]
def faq(fragen=FAQ_ALLE, h2='Bevor du <span class="em k">fragst.</span>'):
    items = ''.join(f'<details class="faq-item"{" open" if i == 0 else ""}><summary>{q}<i aria-hidden="true">+</i></summary><div class="a"><p>{a}</p></div></details>' for i, (q, a) in enumerate(fragen))
    return f'''<section class="faq" id="faq">
  <div class="wrap"><div class="faq-grid">
    <div class="links rv"><p class="kick">Häufige Fragen</p><h2 class="d">{h2}</h2><p>Die Fragen, die in fast jedem Erstgespräch mit SHK-Inhabern kommen. Alles andere klären wir in der Potenzialanalyse, ohne Fachchinesisch.</p>
      <div class="faq-anker"><div class="wer"><img src="/assets/fotos/noah-rund.png" alt="Noah Seelau" width="500" height="500"><span><b>Deine Frage steht nicht dabei?</b><small>Am Telefon bist du direkt bei mir.</small></span></div><a class="btn btn-ink" href="{TEL_HREF}"><span class="ic" aria-hidden="true">📞</span>{TEL}</a></div>
    </div>
    <div class="faq-liste rv" data-d="1">{items}</div>
  </div></div>
</section>'''

def faq_schema(fragen):
    return [{"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": html.unescape(q), "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub('<[^>]+>', '', a))}} for q, a in fragen]}]

def kontakt(h2='Bereit für <span class="em w">planbare</span> Aufträge und Bewerbungen?'):
    return f'''<section class="kontakt" id="kontakt">
  <div class="wrap"><div class="kontakt-karte rv">
    <div>
      <p class="kick">Potenzialanalyse</p>
      <h2 class="d">{h2}</h2>
      <p style="margin-top:18px">In 30 Minuten rechnen wir durch, was in deiner Region drin ist: Bewerbungen von Monteuren oder Anfragen für Bäder und Wärmepumpen. Kostenlos und unverbindlich.</p>
      <div class="kontakt-wege"><a href="{TEL_HREF}"><span aria-hidden="true">📞</span>{TEL}</a><a href="mailto:{MAIL}"><span aria-hidden="true">✉️</span>{MAIL}</a><span><span aria-hidden="true">📍</span>DACH-weit</span></div>
      <p class="zusagen"><span>Kostenlos &amp; unverbindlich</span><span>Rückmeldung in 24h</span><span>Nur SHK &amp; Handwerk</span></p>
    </div>
    <div class="wahl">
      <a href="{CAL_REC}" target="_blank" rel="noopener"><span class="ic" aria-hidden="true">👷</span><span><b>Monteure finden</b><small>30 Minuten · Recruiting-Potenzial deiner Region</small></span><span class="pfeil" aria-hidden="true">→</span></a>
      <a class="w" href="{CAL_LEAD}" target="_blank" rel="noopener"><span class="ic" aria-hidden="true">🛁</span><span><b>Aufträge gewinnen</b><small>30 Minuten · Bad- und Wärmepumpen-Potenzial</small></span><span class="pfeil" aria-hidden="true">→</span></a>
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
    h = kopf('Marketing für SHK-Betriebe: Monteure & Aufträge gewinnen', 'Kampagnen für SHK-Betriebe: Bewerbungen von Monteuren und Bad- & Wärmepumpen-Anfragen. 120+ Betriebe betreut, erste Ergebnisse in 7 Tagen. Kostenlose Analyse.', '/', schema_extra=faq_schema(FAQ_ALLE))
    hero = f'''<section class="hero" id="start">
  <div class="wrap">
    <p class="kick rv">Recruiting &amp; Aufträge für SHK-Betriebe</p>
    <h1 class="h-xl hero-h1"><span class="zl"><span>Monteure &amp; Aufträge</span></span><span class="zl"><span>für SHK-Betriebe.</span></span><span class="zl"><span class="em w glut">Aufgedreht.</span></span></h1>
    <p class="lead rv" data-d="2">Zu wenig Leute oder zu wenig Großprojekte? Wir bauen dir für beides einen eigenen Kampagnen-Kanal: Monteure, die kein Stellenportal öffnen. Bäder und Wärmepumpen mit 20.000 bis 50.000 € Projektwert.</p>
    <div class="hero-cta rv" data-d="3"><a class="btn btn-ink btn-lg" href="{u('/monteure/')}"><span class="ic" aria-hidden="true">👷</span>Mehr Monteure</a><a class="btn btn-white btn-lg" href="{u('/auftraege/')}"><span class="ic" aria-hidden="true">🛁</span>Mehr Aufträge</a></div>
    <div class="rv" data-d="4">{trust()}</div>
  </div>
  <div class="wrap weit buehne-wrap"><div class="buehne feed"><div class="raster" aria-hidden="true"></div><span class="live"><i aria-hidden="true"></i>Läuft gerade für unsere Kunden</span>
    <div class="feed-innen">
      {phone('/assets/funnels/erwin-schmidt-jobs-full.jpg', 'Recruiting · Erwin Schmidt &amp; Sohn', '#1E90E8', 'p1', '0s')}
      {reel_phone('patrick-reel', 'Patrick · Sussmann', 'p2')}
      {reel_phone('mirjana-hook', 'Mirjana · Sussmann', 'p3')}
      {reel_phone('benjamin-schirm', 'Benjamin · Senftleben', 'p4')}
      {phone('/assets/funnels/senftleben-leadgen-full.jpg', 'Aufträge · Senftleben Haustechnik', '#F5762B', 'p5', '3s')}
    </div>
    <div class="zettel" aria-hidden="true">{hero_zettel()}</div>
  </div></div>
</section>'''
    body = hero + logo_band() + kinetik() + leiter() + problem() + system() + hebel() + fallstudien_teaser() + stimmen() + ablauf() + ueber_insel() + statement('Der Auftrag ist da, der Monteur nicht. <em>Oder umgekehrt.</em>', mitte=True) + faq() + kontakt()
    return h + body + fuss()

def uhero(kick, h1, lead, cta_text, cta_href, cta_klasse, phones, warm=False):
    return f'''<section class="uhero{' w' if warm else ''}"><div class="raster" aria-hidden="true"></div>
  <div class="wrap">
    <div class="txt"><p class="kick rv">{kick}</p><h1 class="h-xl rv" data-d="1">{h1}</h1><p class="lead rv" data-d="2">{lead}</p>
      <div class="hero-cta rv" data-d="3"><a class="btn {cta_klasse} btn-lg" href="{cta_href}" target="_blank" rel="noopener"><span class="ic" aria-hidden="true">🎯</span>{cta_text}</a><a class="btn btn-glass btn-lg" href="#fallstudie">Fallstudie ansehen</a></div>
      <div class="rv" data-d="4">{trust()}</div></div>
    <div class="buehne-phones rv" data-d="2">{phones}</div>
  </div>
</section>'''

def seite_monteure():
    fr = [FAQ_ALLE[2], FAQ_ALLE[1], FAQ_ALLE[5], FAQ_ALLE[6]]
    h = kopf('Mitarbeitergewinnung für SHK-Betriebe: Monteure über Social Recruiting', 'Anlagenmechaniker SHK und Kundendiensttechniker über Anzeigen im Umkreis: Bewerbung in 60 Sekunden, vorqualifiziert, mit Fotos aus deinem Betrieb. Fallstudie: 25 Bewerbungen in 4 Wochen.', '/monteure/', dunkel=True, schema_extra=faq_schema(fr))
    body = uhero('Hebel 1 · Recruiting', 'Mitarbeitergewinnung für <span class="em k">SHK-Monteure.</span>', 'Die guten Monteure suchen nicht. Sie sind in Arbeit. Aber sie wechseln, wenn das richtige Angebot vor ihnen liegt. Wir bringen deins dorthin, wo sie jeden Abend sind: in ihren Feed.', 'Recruiting besprechen', CAL_REC, 'btn-kalt',
        phone('/assets/funnels/senftleben-jobs-full.jpg', 'Recruiting · Senftleben Haustechnik', '#1E90E8', 'links', '2s') + phone('/assets/funnels/erwin-schmidt-jobs-full.jpg', 'Recruiting · Erwin Schmidt &amp; Sohn', '#1E90E8', 'rechts', '0s'))
    body += f'''<section class="sec" id="vorteile"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick k rv">Was anders läuft</p><h2 class="d rv">Bewerbungen von Leuten, die <span class="em k">gerade nicht suchen.</span></h2></div><p class="lead rv">Social Recruiting erreicht Anlagenmechaniker SHK und Kundendiensttechniker dort, wo sie ohnehin sind: auf Instagram und Facebook, nicht auf Stellenportalen, die nur aktiv Suchende sehen.</p></div>
  {vorteile([('', '⏱️', 'Bewerbung in 60 Sekunden, ohne Lebenslauf', 'Ein paar Fragen im Handy, fertig. Wer sich abends auf der Couch bewirbt, lädt keinen Lebenslauf hoch.'), ('', '✅', 'Vorqualifiziert: Gewerk, Erfahrung, Führerschein', 'Filterfragen vor der Bewerbung. Bei dir kommt an, wer zur Stelle passt, mit Kontaktdaten.'), ('', '📸', 'Dein Betrieb als Marke', 'Mit Fotos aus deinem Betrieb: dein Team, dein Lager, deine Baustellen. Kein Stockbild, das jeder hat.')])}
</div></section>'''
    body += leiter(WEGE_ALLE[:4], 'Was du wahrscheinlich schon probiert hast', 'Vier Wege, die <span class="em k">kalt</span> bleiben.', 'Aufkleber, Portal, eigene Seite, Mundpropaganda: Alles erreicht nur die, die schon suchen. Und das sind die wenigsten.')
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
  <div class="fall-grid" style="margin-top:20px">{senftleben_recruiting_karte()}<article class="fall-karte rv" data-d="2" style="background:var(--night);color:#fff;border-color:var(--night)"><div class="txt" style="justify-content:center"><p class="kick" style="color:var(--night-sub)">Was die Zahlen bedeuten</p><blockquote>„In den ersten X Wochen" heißt: die Kampagnen laufen weiter.</blockquote><p style="color:var(--night-sub)">Alle Zahlen stammen aus dem Funnel und dem CRM des jeweiligen Betriebs und beziehen sich auf den genannten Zeitraum nach Kampagnenstart.</p><p><a class="btn btn-kalt" href="{CAL_REC}" target="_blank" rel="noopener"><span class="ic" aria-hidden="true">🎯</span>Recruiting besprechen</a></p></div></article></div></div></section>'''
    body += reels() + statement('Die guten Monteure suchen nicht. Sie sind in Arbeit. Aber sie wechseln, wenn das <em>richtige Angebot</em> vor ihnen liegt.') + ablauf() + faq(fr, 'Fragen zum <span class="em k">Recruiting.</span>') + kontakt('Reden wir über <span class="em k">die Stelle.</span>')
    return h + body + fuss()

def seite_auftraege():
    fr = [FAQ_ALLE[0], FAQ_ALLE[4], FAQ_ALLE[3], FAQ_ALLE[1], FAQ_ALLE[5]]
    h = kopf('Auftrags-Funnel für Badsanierung & Wärmepumpe: Anfragen für SHK-Betriebe', 'Bad- und Wärmepumpen-Anfragen aus deinem Einzugsgebiet, exklusiv für deinen Betrieb, vorqualifiziert nach Objekt, Baujahr und Eigentum. Fallstudie: 21 Bad-Anfragen in 2 Monaten.', '/auftraege/', dunkel=True, schema_extra=faq_schema(fr))
    body = uhero('Hebel 2 · Aufträge', 'Auftrags-Funnel für <span class="em w">Bad &amp; Wärmepumpe.</span>', 'Dein eigener Kanal statt gekaufter Portal-Leads: läuft auf deinen Namen, bespielt nur dein Einzugsgebiet, und jede Anfrage gehört dir allein, nicht vier Wettbewerbern gleichzeitig.', 'Potenzial durchrechnen', CAL_LEAD, 'btn-warm',
        phone('/assets/funnels/sussmann-leadgen-hero.jpg', 'Aufträge · Sussmann GmbH', '#F5762B', 'links', '1s') + phone('/assets/funnels/senftleben-leadgen-full.jpg', 'Aufträge · Senftleben Haustechnik', '#F5762B', 'rechts', '0s'), warm=True)
    body += f'''<section class="sec" id="vorteile"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick w rv">Was anders läuft</p><h2 class="d rv">Bäder und Wärmepumpen, <span class="em w">wenn du sie brauchst.</span></h2></div><p class="lead rv">Ein Komplettbad oder eine Wärmepumpe bringt 20.000 bis 50.000 €. Über Mundpropaganda kommen die Projekte, wann sie wollen. Über deinen eigenen Kanal kommen sie, wenn du Kapazität hast.</p></div>
  {vorteile([('w', '🔒', 'Exklusiv für deinen Betrieb', 'Keine Portal-Leads, die parallel an vier Betriebe gehen. Deine Fotos, dein Gebiet, deine Anfragen.'), ('w', '✅', 'Vorqualifiziert: Objekt, Baujahr, Eigentum, Zeitrahmen', 'Filterfragen vor der Anfrage. Eine Anfrage ohne Adresse und Rückrufnummer zählt bei uns nicht als Anfrage.'), ('w', '🎚️', 'Regelbar', 'Auf Wunsch auch nur ein, zwei Aufträge im Monat. Du bekommst Anfragen in dem Tempo, das dein Team stemmen kann.')])}
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
  <div class="fall-grid" style="margin-top:20px;grid-template-columns:1fr 1fr">{sussmann_karte()}<article class="fall-karte rv" data-d="2" style="justify-content:center;background:var(--night);color:#fff;border-color:var(--night)"><div class="txt" style="justify-content:center"><p class="kick" style="color:var(--night-sub)">Nach dem Startpaket</p><blockquote>Werbung macht man nicht nur, wenn es gut läuft.</blockquote><p style="color:var(--night-sub)">Benjamin Senftleben hat nach dem Startpaket verlängert, damit der Name im Kopf bleibt, wenn das nächste Bad ansteht. Das hat er schon in der Meisterschule gelernt.</p><p><a class="btn btn-warm" href="{CAL_LEAD}" target="_blank" rel="noopener"><span class="ic" aria-hidden="true">🎯</span>Potenzial durchrechnen</a></p></div></article></div>
</div></section>'''
    body += statement('Ein Komplettbad oder eine Wärmepumpe bringt 20.000 bis 50.000 €. Nur kommen die Projekte, <em>wann sie wollen.</em>') + ablauf() + faq(fr, 'Fragen zum <span class="em w">Auftrags-Funnel.</span>') + kontakt('Sehen wir uns <span class="em w">deinen Umkreis</span> an.')
    return h + body + fuss()

def seite_fallstudien():
    h = kopf('Fallstudien: Recruiting und Auftrags-Funnel für SHK-Betriebe', 'Erwin Schmidt & Sohn: 25 Bewerbungen in 4 Wochen. Senftleben Haustechnik: 21 Bad-Anfragen in 2 Monaten. Beide Inhaber im Video, mit den Zahlen aus den ersten Wochen.', '/fallstudien/')
    body = f'''<section class="hero" id="start" style="padding-bottom:0"><div class="wrap"><p class="kick rv">Fallstudien</p><h1 class="h-xl rv" data-d="1">Zwei Kampagnen, <span class="em w">die gerade laufen.</span></h1><p class="lead rv" data-d="2">Mit den Zahlen aus den ersten Wochen und den Inhabern vor der Kamera. Keine Hochrechnung, kein „bis zu".</p></div></section>
<section class="sec" id="fallstudie"><div class="wrap"><div class="sec-kopf"><div><p class="kick k rv">Recruiting · Erwin Schmidt &amp; Sohn, Sindelfingen</p><h2 class="d rv">Ein Anlagenmechaniker gesucht. <span class="em k">25 Bewerbungen.</span></h2></div></div>{FALL_ESS()}</div></section>
<section class="sec" id="senftleben" style="padding-top:0"><div class="wrap"><div class="sec-kopf"><div><p class="kick w rv">Auftrags-Funnel · Senftleben Haustechnik, Ehingen</p><h2 class="d rv">Ausgelastet, und trotzdem <span class="em w">21 Bad-Anfragen.</span></h2></div></div>{FALL_SEN()}
<div class="fall-grid" style="margin-top:20px">{sussmann_karte()}<article class="fall-karte rv" data-d="2" style="background:var(--night);color:#fff;border-color:var(--night)"><div class="txt" style="justify-content:center"><p class="kick" style="color:var(--night-sub)">Was die Zahlen bedeuten</p><blockquote>„In den ersten X Wochen" heißt: die Kampagnen laufen weiter.</blockquote><p style="color:var(--night-sub)">Alle Zahlen stammen aus dem Funnel und dem CRM des jeweiligen Betriebs und beziehen sich auf den genannten Zeitraum nach Kampagnenstart. Was danach dazukam, steht hier nicht.</p></div></article></div></div></section>'''
    body += reels() + stimmen() + kontakt()
    return h + body + fuss()

def seite_ueber():
    h = kopf('Über uns: HandwerksManufaktur, Marketing nur für Handwerksbetriebe', 'Seit über sechs Jahren nur Handwerk, über 120 Betriebe betreut, 5,0 auf Google. Wer hinter den Kampagnen für SHK-Betriebe steht und wie wir arbeiten.', '/ueber-uns/')
    body = f'''<section class="hero" id="start" style="padding-bottom:0"><div class="wrap"><p class="kick rv">Über uns</p><h1 class="h-xl rv" data-d="1">Eine Branche. <span class="em w">Seit über sechs Jahren.</span></h1><p class="lead rv" data-d="2">Kein Account-Manager dazwischen, keine Ticketnummer. Du weißt immer, wer an deiner Kampagne sitzt.</p></div></section>
<div style="height:64px"></div>'''
    body += ueber_insel(kurz=False) + praxis_streifen()
    body += f'''<section class="sec" id="wie" style="padding-top:0"><div class="wrap">
  <div class="sec-kopf"><div><p class="kick k rv">Wie wir arbeiten</p><h2 class="d rv">Kleines Team. <span class="em k">Kurze Wege.</span></h2></div><p class="lead rv">Erstgespräch, Strategie und Kampagnenaufbau laufen über einen Tisch. Vom ersten Call bis zum Reporting.</p></div>
  {vorteile([('', '🧭', 'Eine Branche, seit über sechs Jahren', 'Nur Handwerk. Wir kennen dein Gewerk, bevor du es erklären musst, und wissen, was einen Monteur zum Wechseln bringt.'), ('', '📸', 'Shooting bei dir im Betrieb', 'Heizungskeller, Lager, Baustelle: Wir kommen zu dir und fotografieren dein Team. Das ist das Material der Kampagne.'), ('', '📊', 'Zahlen statt Bauchgefühl', 'Wir sehen, was jede Anfrage und jede Bewerbung kostet, und regeln nach, wenn etwas nicht läuft.')])}
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
  {vorteile([('', '🗺️', 'Dein Einzugsgebiet', 'Wie viele Leute erreichen wir im Umkreis deines Betriebs, und wie viele davon passen zur Stelle oder zum Projekt.'), ('', '🔎', 'Wer dort schon wirbt', 'Welche Betriebe in deiner Region bereits Anzeigen schalten, und was das für deine Kampagne bedeutet.'), ('w', '🧮', 'Was realistisch drin ist', 'Was eine Bewerbung oder eine Anfrage in deiner Region kostet, und was Setup und Betreuung für dich bedeuten.')])}
</div></section>'''
    body += statement('Kein Verkaufsgespräch. Eine Rechnung für <em>deine Region.</em>') + faq([FAQ_ALLE[1], FAQ_ALLE[5], FAQ_ALLE[6], FAQ_ALLE[0]], 'Vor dem <span class="em k">Termin.</span>')
    return h + body + fuss()

# ── Schreiben ─────────────────────────────────────────────────────────────
SEITEN = {'/': seite_start, '/monteure/': seite_monteure, '/auftraege/': seite_auftraege, '/fallstudien/': seite_fallstudien, '/ueber-uns/': seite_ueber, '/potenzialanalyse/': seite_potenzial}
for pfad, fn in SEITEN.items():
    ziel = AUS / pfad.strip('/') / 'index.html' if pfad != '/' else AUS / 'index.html'
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(fn(), encoding='utf-8')
    print('✓', ziel.relative_to(REPO))
if LIVE:
    sm = ''.join(f'<url><loc>{DOMAIN}{p}</loc><changefreq>monthly</changefreq><priority>{"1.0" if p == "/" else "0.8"}</priority></url>' for p in SEITEN)
    (REPO/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding='utf-8')
    print('✓ sitemap.xml')
