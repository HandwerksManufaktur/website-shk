/* HandwerksManufaktur SHK — Analyse NUR mit Einwilligung · /zustimmung.js
   🔴 28.09.2026: Die SHK-Seite lud GA4 + Hotjar (Sitzungsaufzeichnung) beim ersten Scrollen OHNE Einwilligung (§ 25 TDDDG).
   Jetzt derselbe Hinweis wie auf handwerksmanufaktur.digital (firma/website/tracking.js — Zwilling, bei Änderung beide ziehen).
   • GA4 G-STBDT88H69 (content_group aus window.HM_GRUPPE) · Hotjar über Contentsquare 99d8993a2bc41
   • Die SHK-Ereignisse (termin_klick, cta_klick, Scrolltiefe, Rechner …) schickt /messung.js — gehen nur raus, wenn GA geladen ist. */
(function () {
'use strict';
var GA4 = 'G-STBDT88H69';
var HOTJAR = 'https://t.contentsquare.net/uxa/99d8993a2bc41.js';
var SCHLUESSEL = 'cookie-consent';
function lies() { try { return localStorage.getItem(SCHLUESSEL); } catch (e) { return null; } }
function schreib(w) { try { localStorage.setItem(SCHLUESSEL, w); } catch (e) {} }
var test = false;
try {
  if (new URLSearchParams(location.search).get('tracking') === 'test') sessionStorage.setItem('hm-tracking-test', '1');
  test = sessionStorage.getItem('hm-tracking-test') === '1';
} catch (e) {}
var echt = /(^|\.)handwerksmanufaktur\.digital$/.test(location.hostname) || test;

window.dataLayer = window.dataLayer || [];
function gtag() { window.dataLayer.push(arguments); }
window.gtag = window.gtag || gtag;
var geladen = false;
function laden() {
  if (geladen || !echt) return; geladen = true;
  gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
  gtag('js', new Date());
  gtag('config', GA4, { debug_mode: test, content_group: window.HM_GRUPPE || 'shk' });
  var g = document.createElement('script'); g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4; document.head.appendChild(g);
  var h = document.createElement('script'); h.async = true; h.src = HOTJAR; document.head.appendChild(h);
}
function ereignis(name, daten) {
  if (!geladen) return;
  var d = { seite: location.pathname }; for (var k in daten) d[k] = daten[k];
  gtag('event', name, d);
}

/* ---- Aussehen: Tinte/Papier wie die Seite, eigene Klassen mit Präfix ---- */
var css = '.hmc{position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:560px;margin-left:auto;background:#FAF7F1;color:#16130E;'
  + 'border-radius:22px;padding:20px 22px;font:15px/1.5 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;'
  + 'box-shadow:0 0 0 1px rgba(22,19,14,.08),0 24px 60px -18px rgba(22,19,14,.45);opacity:0;transform:translateY(16px);transition:opacity .25s,transform .25s}'
  + '.hmc.da{opacity:1;transform:none}.hmc p{margin:0;font-size:14.5px;letter-spacing:.01em}.hmc b{display:block;font-size:16px;margin-bottom:4px;letter-spacing:-.01em}'
  + '.hmc a{color:inherit;text-decoration:underline;text-underline-offset:3px}.hmc a:active{opacity:.7}.hmc-k{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}'
  + '.hmc-k button{flex:1 1 180px;min-height:48px;border-radius:999px;font-weight:600;font-size:15px;line-height:1;font-family:inherit;cursor:pointer;border:0;transition:transform .1s,background .2s,color .2s}'
  + '.hmc-k button:active{transform:scale(.97)}.hmc-n{background:transparent;color:#16130E;box-shadow:inset 0 0 0 2px #16130E}.hmc-n:hover{background:#16130E;color:#FAF7F1}'
  + '.hmc-j{background:#16130E;color:#FAF7F1}.hmc-j:hover{background:#2d2820}'
  + '.hmc-link{background:none;border:0;padding:0;margin-left:16px;min-height:44px;font:inherit;color:inherit;opacity:.85;cursor:pointer;text-decoration:none}.hmc-link:hover{opacity:1;text-decoration:underline}.hmc-link:active{opacity:.6}'
  + '@media(max-width:760px){.hmc{left:12px;right:12px;bottom:12px;padding:18px}}@media(prefers-reduced-motion:reduce){.hmc{transition:none}}';
var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

var box = null;
function hinweis() {
  if (box) { box.hidden = false; requestAnimationFrame(function () { box.classList.add('da'); }); return; }
  box = document.createElement('div');
  box.className = 'hmc'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', 'Cookie-Einstellungen');
  box.innerHTML = '<p><b>Dürfen wir mitzählen?</b> Mit deiner Erlaubnis messen wir über Google Analytics und Hotjar, welche Seiten gelesen und welche Knöpfe genutzt werden. Mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p>'
    + '<div class="hmc-k"><button type="button" class="hmc-n" data-wahl="declined">Nur notwendige</button><button type="button" class="hmc-j" data-wahl="accepted">Alle akzeptieren</button></div>';
  document.body.appendChild(box);
  box.addEventListener('click', function (e) {
    var b = e.target.closest('[data-wahl]'); if (!b) return;
    var w = b.getAttribute('data-wahl'), vorher = lies(); schreib(w);
    box.classList.remove('da'); setTimeout(function () { box.hidden = true; }, 300);
    if (w === 'accepted') laden();
    else if (vorher === 'accepted' && geladen) location.reload(); // Widerruf: geladene Dienste nur per Neuladen los
  });
  requestAnimationFrame(function () { requestAnimationFrame(function () { box.classList.add('da'); }); });
}
document.addEventListener('click', function (e) { if (e.target.closest('[data-cookie-wahl]')) hinweis(); });

/* „Cookie-Einstellungen" neben den Datenschutz-Link im Fuß — jede Seite, ohne sie einzeln anzufassen */
function fussLink() {
  if (document.querySelector('[data-cookie-wahl]')) return;
  // Fuß der Seite: <footer>, sonst der LETZTE Datenschutz-Link (Rechtsseiten haben eine Linkzeile statt <footer>)
  var fuss = document.querySelector('footer');
  var alle = document.querySelectorAll('a[href*="datenschutz"]');
  var ds = fuss ? fuss.querySelector('a[href*="datenschutz"]') : alle[alle.length - 1];
  if (!fuss && !ds) return;
  var b = document.createElement('button'); b.type = 'button'; b.className = 'hmc-link'; b.setAttribute('data-cookie-wahl', '');
  b.textContent = 'Cookie-Einstellungen';
  var zeile = document.querySelector('.fuss .recht'); if (zeile) { zeile.appendChild(b); return; }   // SHK: ans Ende der Rechtszeile
  if (ds && ds.parentNode) ds.parentNode.insertBefore(b, ds.nextSibling); else fuss.appendChild(b);
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fussLink); else fussLink();

var wahl = lies();
if (wahl === 'accepted') laden();
else if (!wahl) {
  var zeigen = function () { setTimeout(hinweis, 900); };
  if (document.readyState === 'complete') zeigen(); else addEventListener('load', zeigen, { once: true });
}

})();
