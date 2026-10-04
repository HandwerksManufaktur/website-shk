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

/* ---- Aussehen: Tinte/Papier wie die Seite, eigene Klassen mit Präfix ----
   28.09.2026 (Noah): Text über Cookies statt „Dürfen wir mitzählen?“, keine Dienstnamen im Hinweis, ein Cookie daneben,
   „Akzeptieren“ groß, „Nur notwendige“ klein. */
var css = '.hmc{position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:440px;margin-left:auto;background:#FAF7F1;color:#16130E;'
  + 'border-radius:22px;padding:18px 20px;font:15px/1.5 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;'
  + 'box-shadow:0 0 0 1px rgba(22,19,14,.08),0 24px 60px -18px rgba(22,19,14,.45);opacity:0;transform:translateY(16px);transition:opacity .25s,transform .25s}'
  + '.hmc.da{opacity:1;transform:none}.hmc-oben{display:flex;gap:14px;align-items:flex-start}.hmc-keks{width:52px;height:52px;flex:none}'
  + '.hmc p{margin:0;font-size:14.5px;letter-spacing:.01em}.hmc b{display:block;font-size:16px;margin-bottom:2px;letter-spacing:-.01em}'
  + '.hmc a{color:inherit;text-decoration:underline;text-underline-offset:3px}.hmc a:active{opacity:.7}'
  + '.hmc-k{display:flex;align-items:center;gap:6px;margin-top:14px}'
  + '.hmc-j{flex:1;min-height:50px;border-radius:999px;border:0;background:#16130E;color:#FAF7F1;font-weight:600;font-size:16px;line-height:1;font-family:inherit;cursor:pointer;transition:transform .1s,background .2s}'
  + '.hmc-j:hover{background:#2d2820}.hmc-j:active{transform:scale(.97)}'
  + '.hmc-n{flex:none;min-height:44px;padding:0 12px;border:0;background:none;color:#5b5448;font-weight:500;font-size:13.5px;line-height:1;font-family:inherit;cursor:pointer;text-decoration:underline;text-underline-offset:3px;transition:color .2s}'
  + '.hmc-n:hover{color:#16130E}.hmc-n:active{opacity:.6}'
  + '.hmc-link{background:none;border:0;padding:0;margin-left:16px;min-height:44px;font:inherit;color:inherit;opacity:.85;cursor:pointer;text-decoration:none}.hmc-link:hover{opacity:1;text-decoration:underline}.hmc-link:active{opacity:.6}'
  + '@media(max-width:760px){.hmc{left:12px;right:12px;bottom:12px;padding:14px 16px}.hmc-keks{width:40px;height:40px}.hmc-oben{gap:12px}.hmc p{font-size:14px;line-height:1.45}.hmc-k{margin-top:10px}.hmc-j{min-height:48px}}@media(orientation:landscape) and (max-height:500px){.hmc{left:auto;right:12px;bottom:8px;width:min(520px,62vw);padding:10px 14px}.hmc-keks{display:none}.hmc p{font-size:13px;line-height:1.4}.hmc-k{margin-top:8px}.hmc-j{min-height:40px}}@media(prefers-reduced-motion:reduce){.hmc{transition:none}}';
var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
var KEKS = '<svg class="hmc-keks" viewBox="0 0 64 64" aria-hidden="true"><defs><mask id="hmcBiss"><rect width="64" height="64" fill="#fff"/><circle cx="56" cy="10" r="11" fill="#000"/><circle cx="60" cy="24" r="6" fill="#000"/></mask></defs>'
  + '<g mask="url(#hmcBiss)"><circle cx="32" cy="33" r="27" fill="#C98A45"/><circle cx="32" cy="33" r="23" fill="#DDA35E"/></g>'
  + '<g fill="#5A3A22"><circle cx="22" cy="24" r="3.4"/><circle cx="36" cy="38" r="3.8"/><circle cx="22" cy="44" r="3"/><circle cx="41" cy="23" r="2.6"/><circle cx="30" cy="31" r="2.2"/><circle cx="46" cy="44" r="2.6"/></g></svg>';

var box = null;
function hinweis() {
  if (box) { box.hidden = false; requestAnimationFrame(function () { box.classList.add('da'); }); return; }
  box = document.createElement('div');
  box.className = 'hmc'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', 'Cookie-Einstellungen');
  box.innerHTML = '<div class="hmc-oben">' + KEKS + '<p><b>Kurz zu Cookies</b>Wir setzen Cookies, damit wir sehen, welche Seiten gelesen und welche Knöpfe genutzt werden. Mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p></div>'
    + '<div class="hmc-k"><button type="button" class="hmc-j" data-wahl="accepted">Akzeptieren</button><button type="button" class="hmc-n" data-wahl="declined">Nur notwendige</button></div>';
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
