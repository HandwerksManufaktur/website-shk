#!/usr/bin/env python3
"""Handy-Prüfer der SHK-Seite — misst jede Seite am Handy auf die Fehler, die Noah sieht.

Aufruf (Server im Repo: python3 -m http.server 8831 --bind 127.0.0.1):
  .venv/bin/python neu/werkzeug/mobil_pruefen.py                       → alle Seiten, 390×844 + 375×667, chromium + webkit
  … --seiten / /monteure/   --engines chromium   --groessen 390x844   → Auswahl
  … --bilder <ordner>                                                    → zusätzlich Bildschirmhöhen-Abschnitte bei 390×844 (chromium)
  … --json <datei>                                                       → alle Funde maschinenlesbar

Je Seite: laden (load + kurze Wartezeit, NICHT networkidle — die Messskripte halten das Netz offen), Cookie-Hinweis
„Nur notwendige", einmal ganz durchscrollen (Lazy-Bilder, Einblendungen), zurück nach oben, dann messen:
  1 ueberlauf   — scrollWidth > innerWidth (Seite wackelt seitlich)
  2 abgeschnitten — Text, der an einem overflow:hidden/clip-Vorfahren oder an text-overflow:ellipsis endet;
                  Eingabefelder, deren Wert oder Platzhalter breiter ist als das Feld
  3 klein       — sichtbarer Text unter 13 px (Hausregel)
  4 tippziel    — a/button kleiner als 44 px (Fließtext-Links im Satz ausgenommen)
  5 rand        — Element ragt über den Bildschirmrand, ohne von einer Bahn (overflow-x:auto) oder einem Vorfahren geschnitten zu werden
  6 ueberlappung — Text liegt auf Text
  8 bild        — Bild geladen, aber kaputt
  7 springen    — Layout-Sprünge beim Durchscrollen (layout-shift, nur chromium), scroll-snap, Sektionen, deren Höhe sich beim Scrollen ändert
Ausnahmen stehen in AUSNAHMEN unten — jede mit Grund.
"""
import argparse, json, re, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASIS = 'http://127.0.0.1:8831'
RECHT = ['/impressum/', '/datenschutz/', '/agb/']

# Bewusste Ausnahmen: (Prüfung, CSS-Selektor, der auf das Element oder einen Vorfahren passt, Grund)
AUSNAHMEN = [
    ('klein', '.sr-only, .visually-hidden', 'nur für Vorleseprogramme'),
    ('abgeschnitten', '.stimmen-marq .spur, .marq', 'Laufband: die Karten laufen durch den Rand, das ist die Bewegung'),
    ('rand', '.stimmen-marq .spur, .marq', 'Laufband: die Karten laufen durch den Rand, das ist die Bewegung'),
    ('abgeschnitten', '.wechsel', 'Wort-Wechsel im Hero: die Breite läuft mit, die Messung fängt den Zwischenstand; längstes Wort per Messung geprüft (passt bei 360 px)'),
]

def seiten_aus_sitemap():
    t = (REPO / 'sitemap.xml').read_text(encoding='utf-8')
    pfade = [re.sub(r'^https?://[^/]+', '', x) or '/' for x in re.findall(r'<loc>([^<]+)</loc>', t)]
    return pfade + [p for p in RECHT if p not in pfade]

JS_MESSEN = r"""
([ausnahmen, nurFenster]) => {
  const W = innerWidth, H = innerHeight, funde = [];
  const ausgen = (art, el) => ausnahmen.some(([a, sel]) => a === art && el.closest && el.closest(sel));
  const pfad = el => { const t = []; let e = el; for (let i = 0; e && e.nodeType === 1 && i < 4; i++, e = e.parentElement) {
      let s = e.tagName.toLowerCase(); if (e.id) { s += '#' + e.id; t.unshift(s); break; }
      const k = [...e.classList].slice(0, 2).join('.'); if (k) s += '.' + k; t.unshift(s); } return t.join(' > '); };
  const txt = el => (el.innerText || el.value || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 60);
  const sichtbar = el => { for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const c = getComputedStyle(e);
      if (c.display === 'none' || c.visibility === 'hidden' || parseFloat(c.opacity) < 0.05) return false;
      if (e.tagName === 'DIALOG' && !e.open) return false; if (e.hidden) return false;
      if (e.parentElement && e.parentElement.tagName === 'DETAILS' && !e.parentElement.open && e.tagName !== 'SUMMARY') return false;   // zugeklappte Antwort
      if (/rect\(0(px)?,? 0(px)?,? 0(px)?,? 0(px)?\)/.test(c.clip) || c.clipPath === 'inset(50%)') return false;   // nur für Vorleseprogramme
      if (c.position === 'absolute' && parseFloat(c.width) <= 1 && parseFloat(c.height) <= 1 && c.overflow === 'hidden') return false; } return true; };
  const absY = r => Math.round(r.top + scrollY);
  const add = (art, el, info) => { if (!ausgen(art, el)) funde.push({ art, wo: pfad(el), text: txt(el), y: absY(el.getBoundingClientRect()), ...info }); };

  // Textknoten einsammeln
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, { acceptNode: n => n.nodeValue.trim() ? 1 : 2 });
  const texte = []; const sichtCache = new Map();
  const istSicht = el => { if (!sichtCache.has(el)) sichtCache.set(el, sichtbar(el)); return sichtCache.get(el); };
  for (let n; (n = tw.nextNode());) {
    const el = n.parentElement; if (!el || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'OPTION'].includes(el.tagName)) continue;
    if (el.closest('svg')) continue;
    const r = document.createRange(); r.selectNodeContents(n); const rects = [...r.getClientRects()].filter(q => q.width > 0.5 && q.height > 0.5);
    if (!rects.length || !istSicht(el)) continue;
    texte.push({ n, el, rects });
  }

  if (!nurFenster) {
  // 1 Überlauf
  const sw = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
  if (sw > W + 1) funde.push({ art: 'ueberlauf', wo: 'html', text: '', y: 0, mass: `scrollWidth ${sw} > ${W}` });

  // 3 klein
  const kleinGesehen = new Set();
  for (const t of texte) { const fs = parseFloat(getComputedStyle(t.el).fontSize);
    if (fs < 12.95 && !kleinGesehen.has(t.el)) { kleinGesehen.add(t.el); add('klein', t.el, { mass: fs.toFixed(1) + 'px' }); } }

  // 2 abgeschnitten (Text an einem schneidenden Vorfahren)
  const clipVorfahr = el => { for (let e = el; e && e !== document.body; e = e.parentElement) { const c = getComputedStyle(e);
      if (['hidden', 'clip'].includes(c.overflowX) || ['hidden', 'clip'].includes(c.overflowY)) return e; } return null; };
  const schnittGesehen = new Set();
  for (const t of texte) {
    const c = getComputedStyle(t.el);
    if (c.textOverflow === 'ellipsis' && t.el.scrollWidth > t.el.clientWidth + 1 && !schnittGesehen.has(t.el)) {
      schnittGesehen.add(t.el); add('abgeschnitten', t.el, { mass: `Ellipse ${t.el.scrollWidth}>${t.el.clientWidth}` }); continue; }
    // alle schneidenden Vorfahren prüfen (nicht nur den nächsten)
    for (let e = t.el; e && e !== document.body && e !== document.documentElement; e = e.parentElement) {
      const ce = getComputedStyle(e);
      if (['auto', 'scroll'].includes(ce.overflowX) || ['auto', 'scroll'].includes(ce.overflowY)) break;   // Wischbahn/Scrollbereich: Wischen zeigt den Rest
      const cx = ['hidden', 'clip'].includes(ce.overflowX), cy = ['hidden', 'clip'].includes(ce.overflowY);
      if (!cx && !cy) continue;
      const b = e.getBoundingClientRect(); if (b.width < 2 || b.height < 2) continue;
      for (const q of t.rects) {
        const innen = q.right > b.left + 1 && q.left < b.right - 1 && q.bottom > b.top + 1 && q.top < b.bottom - 1;
        if (!innen) continue; // ganz draußen = bewusst versteckt (Bahn, Wechsel)
        const ueber = (cx && (q.left < b.left - 1.5 || q.right > b.right + 1.5)) || (cy && (q.top < b.top - 1.5 || q.bottom > b.bottom + 1.5));
        if (ueber && !schnittGesehen.has(t.el)) { schnittGesehen.add(t.el);
          add('abgeschnitten', t.el, { mass: `an ${pfad(e)} (Text ${Math.round(q.left)}–${Math.round(q.right)}×${Math.round(q.top)}–${Math.round(q.bottom)}, Rahmen ${Math.round(b.left)}–${Math.round(b.right)}×${Math.round(b.top)}–${Math.round(b.bottom)})` }); }
      }
    }
  }
  // Eingabefelder: Wert / Platzhalter breiter als das Feld
  const cv = document.createElement('canvas').getContext('2d');
  for (const f of document.querySelectorAll('input, textarea, select')) {
    if (!istSicht(f) || ['hidden', 'checkbox', 'radio', 'range', 'submit', 'button'].includes(f.type)) continue;
    const c = getComputedStyle(f); const innen = f.clientWidth - parseFloat(c.paddingLeft) - parseFloat(c.paddingRight);
    cv.font = `${c.fontWeight} ${c.fontSize} ${c.fontFamily}`;
    for (const [was, s] of [['Wert', f.value], ['Platzhalter', f.placeholder]]) {
      if (!s || f.tagName === 'TEXTAREA') continue; const b = cv.measureText(s).width;
      if (b > innen + 1) add('abgeschnitten', f, { mass: `${was} ${Math.round(b)}px > Feld ${Math.round(innen)}px: „${s.slice(0, 40)}“` }); }
    if (f.scrollWidth > f.clientWidth + 1 && f.tagName !== 'SELECT') add('abgeschnitten', f, { mass: `Feld scrollWidth ${f.scrollWidth}>${f.clientWidth}` });
  }

  // 8 kaputte Bilder (geladen, aber ohne Pixel)
  for (const im of document.querySelectorAll('img')) { if (!istSicht(im)) continue; const r = im.getBoundingClientRect();
    if (r.width > 4 && im.complete && im.naturalWidth === 0 && im.currentSrc) add('bild', im, { mass: 'lädt nicht: ' + im.currentSrc.slice(-60) }); }
  // Bild/Video ohne Fläche (z. B. WebKit: aspect-ratio im gestreckten Raster → 0 × 0), obwohl nichts es ausblendet
  for (const m of document.querySelectorAll('img, video')) { if (!istSicht(m) || m.closest('[aria-hidden=true]')) continue;
    const r = m.getBoundingClientRect(); if ((r.width < 2 || r.height < 2) && (m.getAttribute('width') || 0) > 20)
      add('bild', m, { mass: `ohne Fläche ${Math.round(r.width)}×${Math.round(r.height)}: ` + (m.currentSrc || m.src || '').slice(-50) }); }

  // 4 Tippziele
  for (const el of document.querySelectorAll('a[href], button, [role=button], summary, label[for]')) {
    if (!istSicht(el)) continue; const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1) continue;
    if (el.closest('[aria-hidden=true]') || el.tabIndex < 0 && el.tagName === 'A') continue;
    // Fließtext-Link im Satz (WCAG 2.5.8 Ausnahme „inline")
    const c = getComputedStyle(el);
    if (c.display === 'inline' && el.parentElement && /\S/.test([...el.parentElement.childNodes].filter(x => x !== el && x.nodeType === 3).map(x => x.nodeValue).join(''))) continue;
    // Tippfläche über ::before/::after (position:absolute; inset:-6px …) zählt mit
    let bw = r.width, bh = r.height;
    for (const ps of ['::before', '::after']) { const q = getComputedStyle(el, ps);
      if (q.content === 'none' || q.position !== 'absolute') continue;
      const v = k => { const x = parseFloat(q[k]); return isNaN(x) ? null : x; };
      const [t, rr, b, l] = ['top', 'right', 'bottom', 'left'].map(v);
      if (l !== null && rr !== null) bw = Math.max(bw, r.width - l - rr); else if (parseFloat(q.width)) bw = Math.max(bw, parseFloat(q.width));
      if (t !== null && b !== null) bh = Math.max(bh, r.height - t - b); else if (parseFloat(q.height)) bh = Math.max(bh, parseFloat(q.height)); }
    if (bw < 43.5 || bh < 43.5) add('tippziel', el, { mass: `${Math.round(bw)}×${Math.round(bh)}` });
  }

  // 5 über den Rand
  const schneidetX = e => { const c = getComputedStyle(e); return ['hidden', 'clip', 'auto', 'scroll'].includes(c.overflowX); };
  const randGesehen = [];
  for (const el of document.body.querySelectorAll('*')) {
    if (['SCRIPT', 'STYLE', 'BR'].includes(el.tagName)) continue;
    const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    if (r.right <= W + 1 && r.left >= -1) continue;
    if (r.left >= W || r.right <= 0) continue; // ganz außerhalb = versteckt
    let geschnitten = false;
    for (let e = el.parentElement; e && e !== document.documentElement; e = e.parentElement) {
      if (e === document.body) { break; }
      if (schneidetX(e)) { const b = e.getBoundingClientRect(); if (b.left >= -1 && b.right <= W + 1) { geschnitten = true; break; } }
    }
    if (geschnitten || !istSicht(el)) continue;
    if (randGesehen.some(p => p.contains(el))) continue; randGesehen.push(el);
    add('rand', el, { mass: `${Math.round(r.left)}…${Math.round(r.right)} bei Breite ${W}` });
  }

  }
  if (nurFenster) {
  // 6 Text über Text — nur im aktuellen Fenster (elementFromPoint braucht sichtbare Punkte)
  const boxen = []; for (const t of texte) for (const q of t.rects) if (q.bottom > 0 && q.top < H) boxen.push({ el: t.el, q });
  const ueberGesehen = new Set();
  for (let i = 0; i < boxen.length; i++) for (let j = i + 1; j < boxen.length; j++) {
    const a = boxen[i], b = boxen[j]; if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
    const x = Math.min(a.q.right, b.q.right) - Math.max(a.q.left, b.q.left), y = Math.min(a.q.bottom, b.q.bottom) - Math.max(a.q.top, b.q.top);
    if (x < 3 || y < Math.min(a.q.height, b.q.height) * 0.35) continue;
    // nur, wenn beide an der Stelle auch wirklich oben liegen könnten (nicht von einer Fläche verdeckt)
    const mx = (Math.max(a.q.left, b.q.left) + Math.min(a.q.right, b.q.right)) / 2, my = (Math.max(a.q.top, b.q.top) + Math.min(a.q.bottom, b.q.bottom)) / 2;
    if (my < 0 || my > H || mx < 0 || mx > W) continue;   // außerhalb des Fensters nicht prüfbar — ein anderer Fenster-Schritt zeigt die Stelle
    { const top = document.elementFromPoint(mx, my); if (top && !(a.el.contains(top) || top.contains(a.el) || b.el.contains(top) || top.contains(b.el))) continue;
      // liegt der obere Text auf einer eigenen deckenden Fläche (Karten-Stapel), ist der untere verdeckt — kein Fund
      const oben = top && (a.el.contains(top) || top.contains(a.el)) ? a.el : b.el, unten = oben === a.el ? b.el : a.el;
      let deckt = false; for (let e = oben; e && !e.contains(unten); e = e.parentElement) { const c = getComputedStyle(e);
        const bg = c.backgroundColor; if ((bg && bg !== 'transparent' && !/rgba\([^)]*,\s*0\)$/.test(bg) && !/,\s*0(\.0+)?\)$/.test(bg)) || c.backgroundImage !== 'none' || parseFloat(c.backdropFilter) ) {
          const fr = e.getBoundingClientRect(), uq = unten === a.el ? a.q : b.q;   // nur wenn die Fläche den unteren Text ganz zudeckt
          if (fr.left <= uq.left + 1 && fr.right >= uq.right - 1 && fr.top <= uq.top + 1 && fr.bottom >= uq.bottom - 1) { deckt = true; break; } } }
      if (deckt) continue; }
    const key = pfad(a.el) + '|' + pfad(b.el); if (ueberGesehen.has(key)) continue; ueberGesehen.add(key);
    add('ueberlappung', a.el, { mass: `mit ${pfad(b.el)} „${txt(b.el).slice(0, 30)}“` });
  }
  }
  return { funde, hoehe: document.documentElement.scrollHeight };
}
"""

def laden(page, url):
    page.goto(url, wait_until='load', timeout=60000)
    page.wait_for_timeout(2600 if re.sub(r'^https?://[^/]+', '', url) in ('', '/') else 900)  # Startseite: Logo-Intro abwarten
    try:
        b = page.locator('.hmc-n')
        if b.count() and b.first.is_visible(): b.first.click(); page.wait_for_timeout(400)
    except Exception: pass

INIT_SPRUNG = r"""
window.__spruenge = [];
try { new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput && e.value > 0.002) window.__spruenge.push({ v: e.value, t: e.startTime, y: scrollY,
  q: (e.sources || []).map(s => { const n = s.node; if (!n || n.nodeType !== 1) return '?'; let x = n.tagName.toLowerCase(); if (n.id) x += '#' + n.id; else if (n.classList.length) x += '.' + [...n.classList].slice(0, 2).join('.'); return x + ` ${Math.round(s.previousRect.top)}→${Math.round(s.currentRect.top)} h${Math.round(s.previousRect.height)}→${Math.round(s.currentRect.height)}`; }) }); })).observe({ type: 'layout-shift', buffered: true }); } catch (e) {}
"""
JS_HOEHEN = "[...document.querySelectorAll('body > *, main > *, section')].map(e => [e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.classList.length ? '.' + [...e.classList].slice(0,2).join('.') : ''), Math.round(e.getBoundingClientRect().height)])"
JS_SNAP = "[...document.querySelectorAll('*')].filter(e => { const c = getComputedStyle(e); return c.scrollSnapType && c.scrollSnapType !== 'none' && (e === document.documentElement || e === document.body || c.overflowY === 'auto' || c.overflowY === 'scroll'); }).map(e => e.tagName.toLowerCase() + '.' + [...e.classList].join('.') + ' ' + getComputedStyle(e).scrollSnapType + ' ox:' + getComputedStyle(e).overflowX)"

def durchscrollen(page):
    h = page.evaluate('document.documentElement.scrollHeight'); vh = page.evaluate('innerHeight'); y = 0
    page.evaluate('window.__spruenge = []')
    while y < h:
        y += int(vh * 0.7); page.evaluate(f'scrollTo(0,{y})'); page.wait_for_timeout(140)
        h = page.evaluate('document.documentElement.scrollHeight')
    page.wait_for_timeout(500)

def springen(page):
    """Zweiter Durchlauf (alles schon geladen/eingeblendet): misst Sprünge und Höhenänderungen, die beim echten Scrollen bleiben."""
    funde = []
    page.evaluate('scrollTo(0,0)'); page.wait_for_timeout(300)
    vorher = dict(page.evaluate(JS_HOEHEN))
    page.evaluate('window.__spruenge = []')
    h = page.evaluate('document.documentElement.scrollHeight'); vh = page.evaluate('innerHeight'); y = 0
    while y < h:
        y += int(vh * 0.25); page.evaluate(f'scrollBy(0,{int(vh * 0.25)})'); page.wait_for_timeout(90)
    page.wait_for_timeout(400)
    for s in page.evaluate('window.__spruenge || []'):
        funde.append({'art': 'springen', 'wo': '; '.join(s['q'])[:200], 'text': f"layout-shift {s['v']:.3f}", 'y': s['y'], 'mass': f"bei scrollY {s['y']}"})
    nachher = dict(page.evaluate(JS_HOEHEN))
    for k, v in vorher.items():
        if k in nachher and abs(nachher[k] - v) > 4:
            funde.append({'art': 'springen', 'wo': k, 'text': 'Höhe ändert sich beim Scrollen', 'y': 0, 'mass': f'{v}→{nachher[k]}px'})
    for x in page.evaluate(JS_SNAP):
        if 'ox:auto' in x or 'ox:scroll' in x: continue  # Wischbahn mit Einrasten ist gewollt
        funde.append({'art': 'springen', 'wo': x, 'text': 'scroll-snap auf senkrechtem Scrollen', 'y': 0})
    return funde

def messen_im_fenster(page):
    """Misst in Fenster-Schritten, damit Überlappung (elementFromPoint) und Einblendungen am Ort stimmen."""
    alle = {}; vh = page.evaluate('innerHeight'); h = page.evaluate('document.documentElement.scrollHeight'); y = 0
    while True:
        page.evaluate(f'scrollTo(0,{y})'); page.wait_for_timeout(260)
        erg = page.evaluate(JS_MESSEN, [[[a, s] for a, s, _ in AUSNAHMEN], True])
        if y == 0: erg['funde'] += page.evaluate(JS_MESSEN, [[[a, s] for a, s, _ in AUSNAHMEN], False])['funde']
        for f in erg['funde']:
            k = (f['art'], f['wo'], f.get('mass', '') if f['art'] in ('ueberlauf',) else '')
            alle.setdefault(k, f)
        if y + vh >= h: break
        y = min(y + vh, h - vh)
    return list(alle.values())

def abschnitte(page, ordner, name):
    ordner.mkdir(parents=True, exist_ok=True); vh = page.evaluate('innerHeight'); h = page.evaluate('document.documentElement.scrollHeight')
    dateien = []; y = 0; i = 0
    while True:
        page.evaluate(f'scrollTo(0,{y})'); page.wait_for_timeout(700)
        d = ordner / f'{name}_{i:02d}.png'; page.screenshot(path=str(d)); dateien.append(d); i += 1
        if y + vh >= h: break
        y = min(y + vh, h - vh)
    return dateien

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--basis', default=BASIS); ap.add_argument('--seiten', nargs='*')
    ap.add_argument('--groessen', nargs='*', default=['390x844', '375x667']); ap.add_argument('--engines', nargs='*', default=['chromium', 'webkit'])
    ap.add_argument('--bilder'); ap.add_argument('--json'); ap.add_argument('--nur', nargs='*', help='nur diese Prüfarten zeigen')
    a = ap.parse_args()
    seiten = a.seiten or seiten_aus_sitemap()
    from playwright.sync_api import sync_playwright
    ergebnis = []
    with sync_playwright() as p:
        for eng in a.engines:
            br = getattr(p, eng).launch()
            for g in a.groessen:
                w, h = map(int, g.split('x'))
                for s in seiten:
                    ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True, device_scale_factor=1,
                                         user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1')
                    ctx.add_init_script(INIT_SPRUNG)
                    pg = ctx.new_page()
                    try:
                        laden(pg, a.basis + s); durchscrollen(pg); pg.evaluate('scrollTo(0,0)'); pg.wait_for_timeout(300)
                        funde = messen_im_fenster(pg) + springen(pg)
                        if a.bilder and eng == 'chromium' and g == '390x844':
                            name = s.strip('/').replace('/', '_') or 'start'
                            abschnitte(pg, Path(a.bilder), name)
                    except Exception as e:
                        funde = [{'art': 'fehler', 'wo': '', 'text': str(e)[:200], 'y': 0}]
                    ctx.close()
                    if a.nur: funde = [f for f in funde if f['art'] in a.nur]
                    for f in funde: f.update(seite=s, engine=eng, groesse=g)
                    ergebnis += funde
                    zahl = {}
                    for f in funde: zahl[f['art']] = zahl.get(f['art'], 0) + 1
                    print(f'{eng:8} {g:8} {s:45} {len(funde):3} ' + ' '.join(f'{k}:{v}' for k, v in sorted(zahl.items())), flush=True)
            br.close()
    if a.json: Path(a.json).write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1), encoding='utf-8')
    gesamt = {}
    for f in ergebnis: gesamt[f['art']] = gesamt.get(f['art'], 0) + 1
    print('\nSUMME', len(ergebnis), gesamt)
    return 1 if ergebnis else 0

if __name__ == '__main__':
    sys.exit(main())
