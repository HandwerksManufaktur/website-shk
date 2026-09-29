/* SHK-Seite v3 — Messung: was geklickt wird, wie weit gelesen wird, welcher Knopf den Termin bringt.
   GA4 (G-STBDT88H69) + Contentsquare/Hotjar (Heatmaps, Klick-Karten, Sitzungsaufzeichnung) lädt der Kopf
   verzögert (erste Berührung oder 3,5 s nach dem Laden), damit PageSpeed nicht leidet. Hier hängen nur die
   Ereignisse dran; bis die Skripte da sind, sammelt dataLayer alles. Eingebaut 27.09.2026 (Noah). */
(function () {
  // Ratgeber: jedes Ereignis trägt den Artikel mit, damit sich Wissensseiten einzeln auswerten lassen (29.09.2026)
  const artikel = (location.pathname.match(/\/wissen\/([^/]+)\//) || [])[1] || (/\/wissen\/$/.test(location.pathname) ? 'uebersicht' : '');
  const g = (name, p) => { try { window.gtag && gtag('event', name, Object.assign({ seite: location.pathname }, artikel ? { artikel } : {}, p || {})); } catch (e) {} };
  const kurz = s => (s || '').replace(/\s+/g, ' ').trim().slice(0, 90);

  // Wo auf der Seite: Navigation, Fuß, Menü oder die Sektion (id, sonst erste Überschrift)
  const bereich = el => {
    if (el.closest('.nav')) return 'navigation';
    if (el.closest('.mobilmenu')) return 'menue-mobil';
    if (el.closest('.fuss')) return 'fusszeile';
    const s = el.closest('main > section, main > div > section, section');
    if (!s) return 'sonstiges';
    if (s.matches('.hero, .uhero')) return 'hero';
    if (s.id) return s.id;
    const h = s.querySelector('h1, h2, .kick');
    return kurz(h && h.textContent).slice(0, 50) || (s.className.split(' ')[0] || 'sektion');
  };

  // Calendly bekommt die Herkunft mit — steht dann im Termin (Calendly + Close): welche Seite, welcher Knopf
  const mitHerkunft = (a, wo) => {
    try {
      const url = new URL(a.href);
      url.searchParams.set('utm_source', 'shk-website');
      url.searchParams.set('utm_medium', 'website');
      url.searchParams.set('utm_campaign', (location.pathname.replace(/^\/neu/, '').replace(/\//g, '') || 'start'));
      url.searchParams.set('utm_content', wo);
      a.href = url.toString();
    } catch (e) {}
  };

  // Ratgeber: welche Handlungsaufforderung zieht (Mitte/Ende/Seitenleiste) und welcher Querlink zur Hauptseite
  document.addEventListener('click', e => {
    const c = e.target.closest('[data-cta]');
    if (c) g('wissen_cta', { position: c.dataset.cta, link_text: kurz(c.textContent) });
    const q = e.target.closest('.wx-quer a, .wx-karte');
    if (q) g(q.matches('.wx-karte') ? 'wissen_weiter' : 'wissen_quer', { ziel: q.getAttribute('href') });
  }, { capture: true, passive: true });

  // Ratgeber: „gelesen" = 75 % des Artikeltexts im Bild und mindestens 30 Sekunden auf der Seite
  const text = document.querySelector('.wx-text');
  if (text) {
    const start = Date.now(); let gemeldet = false;
    const pruef = () => {
      if (gemeldet) return;
      const r = text.getBoundingClientRect();
      const gelesen = (innerHeight - r.top) / r.height;
      if (gelesen >= 0.75 && Date.now() - start >= 30000) { gemeldet = true; g('wissen_gelesen', { sekunden: Math.round((Date.now() - start) / 1000) }); }
    };
    addEventListener('scroll', pruef, { passive: true }); setInterval(pruef, 5000);
  }

  document.addEventListener('click', e => {
    const a = e.target.closest('a[href]');
    const b = e.target.closest('button');
    if (a) {
      const href = a.getAttribute('href') || '';
      const wo = bereich(a);
      const p = { link_text: kurz(a.textContent), link_url: a.href, bereich: wo, knopf: a.matches('.btn, .nav-cta') ? 'ja' : 'nein' };
      if (/calendly\.com/.test(href)) { mitHerkunft(a, wo); g('termin_klick', p); }
      else if (href.startsWith('tel:')) g('telefon_klick', p);
      else if (href.startsWith('mailto:')) g('mail_klick', p);
      else if (/potenzialanalyse/.test(href)) g('cta_klick', p);
      else if (href.startsWith('#')) g('sprung_klick', p);
      else if (a.host && a.host !== location.host) g('extern_klick', p);
      else g(a.matches('.btn, .nav-cta') ? 'cta_klick' : 'navigation_klick', p);
      return;
    }
    if (b) {
      if (b.matches('.play')) { const k = b.closest('.fall-karte, article, section'); g('video_start', { video: kurz(k && (k.querySelector('h2, h3, .erg') || {}).textContent), bereich: bereich(b) }); }
      else if (b.matches('.burger')) g('menue_klick', { offen: b.getAttribute('aria-expanded') !== 'true' ? 'ja' : 'nein' });
      else if (b.matches('.ton')) g('reel_ton', { bereich: bereich(b) });
      else g('knopf_klick', { link_text: kurz(b.getAttribute('aria-label') || b.textContent), bereich: bereich(b) });
    }
  }, { capture: true, passive: true });

  // FAQ: welche Frage wird aufgeklappt
  document.querySelectorAll('details.faq-item').forEach(d => d.addEventListener('toggle', () => { if (d.open) g('faq_offen', { frage: kurz(d.querySelector('summary') && d.querySelector('summary').textContent) }); }));

  // Lesetiefe 25/50/75/100 % (GA4 misst von sich aus nur 90 %)
  const marken = [25, 50, 75, 100]; const erreicht = new Set();
  const tiefe = () => {
    const h = document.documentElement.scrollHeight - innerHeight;
    const pz = h > 0 ? (scrollY / h) * 100 : 100;
    marken.forEach(m => { if (pz >= m - 1 && !erreicht.has(m)) { erreicht.add(m); g('scroll_tiefe', { prozent: m }); } });
  };
  let t; addEventListener('scroll', () => { clearTimeout(t); t = setTimeout(tiefe, 200); }, { passive: true });

  // Welche Sektion wirklich gesehen wurde (erreicht die Bildmitte, gilt auch für Sektionen höher als der Bildschirm) — zeigt, wo die Leute aussteigen
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { g('sektion_gesehen', { bereich: bereich(e.target), nr: String(e.target.dataset.nr) }); io.unobserve(e.target); } }), { rootMargin: '-45% 0px -45% 0px', threshold: 0 });
  document.querySelectorAll('main > section, main > div > section').forEach((s, i) => { s.dataset.nr = i + 1; io.observe(s); });
})();

/* Cookieloser Seitenzähler (Worker seiten-zaehler, D1 zaehler-db — gebaut im Chat „HWM Website Überarbeitung", 29.09.2026).
   Nichts im Browser gespeichert, keine IP, keine Nutzer-Kennung → keine Einwilligung nötig. Zählt Aufrufe, Klicks (Knopftext),
   Formulare (Ereignis 'hwm:lead') und Lesetiefe für die Montags-Mail (web_wochenbericht.py, Block „Seitenzähler"). */
(() => { if (!/(^|\.)handwerksmanufaktur\.digital$/.test(location.hostname)) return;
const Z='https://seiten-zaehler.handwerksmanufaktur.workers.dev/z', id=Math.random().toString(36).slice(2,12), g=innerWidth<768?'m':'d';
const s=(t,x)=>{const d=JSON.stringify(Object.assign({t,s:location.hostname,p:location.pathname,g,id},x||{}));try{if(!(navigator.sendBeacon&&navigator.sendBeacon(Z,new Blob([d],{type:'text/plain'}))))fetch(Z,{method:'POST',body:d,keepalive:true,mode:'no-cors'})}catch(e){}};
let r='direkt';try{const q=new URLSearchParams(location.search);if(q.get('utm_source'))r='utm:'+q.get('utm_source');else if(document.referrer){const h=new URL(document.referrer).hostname.replace(/^www\./,'');if(h&&h!==location.hostname)r=h}}catch(e){}
s('v',{r});
document.addEventListener('click',e=>{const a=e.target.closest('a,button,summary');if(!a)return;const t=(a.getAttribute('aria-label')||a.textContent||'').trim().replace(/\s+/g,' ').slice(0,70);const h=a.getAttribute('href')||'';s('k',{z:t+(h.startsWith('tel:')?' → Anruf':h.startsWith('mailto:')?' → Mail':/calendly/.test(h)?' → Termin':'')})},{capture:true});
document.addEventListener('hwm:lead',e=>s('f',{z:(e.detail&&e.detail.formular)||'formular'}));
const m=[25,50,75,100],done=new Set();let l=false;addEventListener('scroll',()=>{if(l)return;l=true;requestAnimationFrame(()=>{l=false;const h=document.documentElement.scrollHeight-innerHeight;if(h<=0)return;const p=Math.round(scrollY/h*100);m.forEach(x=>{if(p>=x-2&&!done.has(x)){done.add(x);s('l',{z:String(x)})}})})},{passive:true});
})();
