/* SHK-Seite v3 — „Aufgedreht": Regler, Rohr, Leiter, Kinetik, Bühne */
(function(){
  window.__lebt = true;
  const rm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => [...r.querySelectorAll(s)];
  const clamp = (v,a,b) => Math.max(a, Math.min(b, v));

  /* Intro: Logo + Regler-Strich, einmal je Sitzung (Bauform aus dem HWM-Konzept) */
  const intro = $('#intro');
  if (intro) {
    let gesehen = false; try { gesehen = sessionStorage.getItem('shk-intro') === '1'; } catch (e) {}
    if (gesehen || rm) intro.remove();
    else { requestAnimationFrame(() => intro.classList.add('los')); setTimeout(() => { intro.classList.add('aus'); try { sessionStorage.setItem('shk-intro', '1'); } catch (e) {} }, 1450); setTimeout(() => intro.remove(), 2100); }
  }

  /* Nav */
  const nav = $('.nav');
  const burger = $('.burger');
  const menu = $('.mobilmenu');
  const setNav = () => nav && nav.classList.toggle('fest', scrollY > 24 || (menu && menu.classList.contains('offen')));
  setNav();
  if (burger && menu) {
    const zu = () => { menu.classList.remove('offen'); burger.setAttribute('aria-expanded','false'); document.body.style.overflow=''; setNav(); };
    burger.addEventListener('click', () => {
      const offen = !menu.classList.contains('offen');
      menu.classList.toggle('offen', offen);
      burger.setAttribute('aria-expanded', String(offen));
      document.body.style.overflow = offen ? 'hidden' : '';
      setNav();
    });
    $$('a', menu).forEach(a => a.addEventListener('click', zu));
    addEventListener('keydown', e => { if (e.key === 'Escape') zu(); });
    addEventListener('resize', () => { if (innerWidth > 900) zu(); });
  }

  /* Reveal */
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('an'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -10% 0px', threshold: .12 });
  $$('.rv').forEach(el => { if (el.getBoundingClientRect().top < innerHeight * 1.1) el.classList.add('an'); else io.observe(el); });
  addEventListener('pageshow', () => $$('.rv').forEach(el => { if (el.getBoundingClientRect().top < innerHeight) el.classList.add('an'); }));

  /* Bühne (Hero): Clip-Expand + Regler */
  const buehne = $('.buehne');
  /* Scroll-getriebenes */
  const leiste = $('.regler-leiste');
  const kin = $$('.kinetik .zeile');
  const rohr = $('.rohr');
  const rohrPunkte = rohr ? $$('b', rohr) : [];
  const schritte = $$('.schritt');
  const streifen = $('.streifen');
  const statement = $('.statement p');
  const worte = statement ? $$('.w', statement) : [];
  let ticking = false;
  const scrollWork = () => {
    ticking = false;
    const y = scrollY, h = innerHeight, doc = document.documentElement.scrollHeight - h;
    setNav();
    if (leiste) document.documentElement.style.setProperty('--scroll', (doc > 0 ? y / doc : 0).toFixed(4));
    if (buehne && !rm) {
      const r = buehne.getBoundingClientRect();
      // 0 = Oberkante bei 90 % der Höhe, 1 = Oberkante bei 25 %
      const k = clamp((h * .9 - r.top) / (h * .65), 0, 1);
      const inset = (6 * (1 - k)).toFixed(2);
      const rad = (28 - 10 * k).toFixed(1);
      buehne.style.clipPath = `inset(0 ${inset}% round ${rad}px)`;
    }
    if (kin.length && !rm) {
      kin.forEach((z, i) => { const r = z.parentElement.getBoundingClientRect(); const k = (r.top + r.height/2 - h/2) / h; z.style.transform = `translateX(${(i % 2 ? 1 : -1) * k * 360 - (i % 2 ? 120 : 220)}px)`; });
    }
    if (rohr) {
      const r = rohr.parentElement.getBoundingClientRect();
      const p = clamp((h * .78 - r.top) / (r.height * .9), 0, 1);
      rohr.style.setProperty('--p', p.toFixed(3));
      rohrPunkte.forEach((b, i) => { const an = p >= (i + .5) / rohrPunkte.length - .02; b.classList.toggle('an', an); if (schritte[i]) schritte[i].classList.toggle('heiss', an); });
    }
    if (streifen && !rm) {
      const r = streifen.getBoundingClientRect();
      const k = clamp((h - r.top) / (h + r.height), 0, 1);
      streifen.style.transform = `translateX(${(-k * (streifen.scrollWidth - innerWidth + 56)).toFixed(0)}px)`;
    }
    if (worte.length) {
      // Fülltext: gemessen am Textelement, durch die Bildmitte, nur vorwärts, fertig sobald der Block ganz im Bild steht
      // Skill scroll-text: das TEXTELEMENT messen, Start bei 78 % der Fensterhöhe, voll bei 32 %, beide Richtungen
      const r = statement.getBoundingClientRect();
      const p = rm ? 1 : clamp((h * .78 - r.top) / (h * .46), 0, 1);
      worte.forEach((w, i) => w.classList.toggle('an', (i + 1) / worte.length <= p + .02));
    }
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(scrollWork); } }, { passive: true });
  addEventListener('resize', scrollWork);
  scrollWork();

  /* Die kalte Leiter: Stempel nacheinander */
  const leiter = $('.leiter');
  if (leiter) {
    const wege = $$('.weg', leiter);
    const ioL = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return; ioL.disconnect();
      wege.forEach((w, i) => setTimeout(() => w.classList.add('gestempelt'), rm ? 0 : 300 + i * 420));
      setTimeout(() => leiter.classList.add('fertig'), rm ? 0 : 300 + wege.length * 420 + 150);
    }), { threshold: .35 });
    ioL.observe(leiter);
  }

  /* Kaskade: Balken fahren aus, Zahlen zählen hoch */
  const zaehlen = (el) => {
    if (el.dataset.fertig) return; el.dataset.fertig = '1';
    const ziel = parseFloat(el.dataset.zahl), nach = el.dataset.nach || '';
    const fmt = n => Math.round(n).toLocaleString('de-DE') + nach;
    if (rm) { el.textContent = fmt(ziel); return; }
    const t0 = performance.now(), dauer = 1300;
    const tick = t => { const k = Math.min(1, (t - t0) / dauer), e = 1 - Math.pow(1 - k, 3); el.textContent = fmt(ziel * e); if (k < 1) requestAnimationFrame(tick); else el.textContent = fmt(ziel); };
    requestAnimationFrame(tick);
  };
  $$('.k-stufe').forEach(st => { const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { $$('.nr[data-zahl]', st).forEach(zaehlen); o.disconnect(); } }), { threshold: .4 }); o.observe(st); });

  /* Kalenderraster: Tage füllen sich beim Scrollen, Zähler läuft mit (beide Richtungen) */
  $$('[data-kalender]').forEach(tafel => {
    const treffer = $$('.kal-raster i.an', tafel), zahl = $('.kal-nr', tafel); if (!treffer.length || !zahl) return;
    let letzte = -1;
    const mal = () => { const r = tafel.getBoundingClientRect(), h = innerHeight; const p = rm ? 1 : clamp((h * .92 - r.top) / (h * .52 + r.height * .5), 0, 1); const k = Math.round(p * treffer.length); if (k === letzte) return; letzte = k; treffer.forEach((el, n) => el.classList.toggle('voll', n < k)); zahl.textContent = k; };
    addEventListener('scroll', mal, { passive: true }); addEventListener('resize', mal); mal();
  });

  /* Bauplan: Balken füllen sich, während die Tafel durchs Bild läuft */
  const bauplan = $('.ablauf'), tafel = $('.plan-tafel');
  if (bauplan && tafel) { const bp = () => { const r = tafel.getBoundingClientRect(), h = innerHeight; bauplan.style.setProperty('--p', (rm ? 1 : clamp((h * .9 - r.top) / (h * .75), 0, 1)).toFixed(3)); }; addEventListener('scroll', bp, { passive: true }); addEventListener('resize', bp); bp(); }

  /* Bewegung nur im Bild (Apple: keine Dauer-Loops außerhalb des Blickfelds): Phones scrollen zwei Durchgänge, sobald sie erscheinen; Laufbänder laufen nur sichtbar */
  $$('.phone, .mini-phone').forEach(ph => { const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { ph.classList.add('laeuft'); o.disconnect(); } }), { threshold: .3 }); o.observe(ph); });
  $$('.band-innen, .stimmen-marq').forEach(m => new IntersectionObserver(es => es.forEach(e => m.classList.toggle('laeuft', e.isIntersecting)), { threshold: 0 }).observe(m));

  /* Umkreis: dreimal pulsen, wenn er ins Bild kommt — danach nur beim Hover */
  $$('.umkreis').forEach(u => { const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { u.classList.add('an'); o.disconnect(); } }), { threshold: .4 }); o.observe(u); });

  /* Bento-Tickets erscheinen */
  $$('.zelle.mit-tickets').forEach(z => { const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { z.classList.add('sichtbar'); o.disconnect(); } }), { threshold: .3 }); o.observe(z); });

  /* Videos: Poster → Abspielen mit Ton */
  $$('.vid').forEach(v => {
    const btn = $('.play', v), vid = $('video', v);
    if (!btn || !vid) return;
    btn.addEventListener('click', () => { v.classList.add('laeuft'); vid.controls = true; vid.muted = false; vid.play(); });
  });

  /* Reels: laufen stumm, sobald im Bild; Ton-Knopf (SVG, kein Emoji) */
  const MUTE = '<svg class="ik" viewBox="0 0 24 24" aria-hidden="true"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="m22 9-6 6"/><path d="m16 9 6 6"/></svg>', VOL = '<svg class="ik" viewBox="0 0 24 24" aria-hidden="true"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5.5a9 9 0 0 1 0 13"/></svg>';
  $$('.reel .ton').forEach(t => { t.innerHTML = MUTE; });
  $$('.reel').forEach(f => {
    const vid = $('video', f); if (!vid) return;
    const q = vid.dataset.quelle;
    const o = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { if (q && !vid.src) { vid.src = q; vid.load(); } vid.play().catch(()=>{}); } else { vid.pause(); }
    }), { threshold: .3 });
    o.observe(f);
    const ton = $('.ton', f);
    if (ton) ton.addEventListener('click', () => { const an = vid.muted; $$('.reel video').forEach(x => x.muted = true); $$('.reel .ton').forEach(x => x.innerHTML = MUTE); vid.muted = !an; ton.innerHTML = an ? VOL : MUTE; ton.setAttribute('aria-label', an ? 'Ton aus' : 'Ton an'); if (an) vid.play().catch(()=>{}); });
  });

  /* Feed-Bühne: Phones parallaxen */
  const feedPhones = $$('.feed-innen .phone');
  if (feedPhones.length && !rm && !$(".feed-innen.still")) {
    const fak = [.10, .05, 0, .05, .10];
    addEventListener('scroll', () => { const y = scrollY; feedPhones.forEach((p, k) => p.style.setProperty('--ty', (-y * fak[k]).toFixed(1) + 'px')); }, { passive: true });
  }

  /* Phones auf Bühne/Unterseiten: Scrollhöhe je Bild */
  $$('.phone .scroller img, .zelle .mini-phone:not(.mini-phones .mini-phone) img').forEach(img => {
    const set = () => { const box = img.parentElement.getBoundingClientRect(); if (img.naturalHeight) img.style.setProperty('--sk', (box.height / 1038).toFixed(3)); };
    img.complete ? set() : img.addEventListener('load', set); addEventListener('resize', set);
  });

  /* Stimmen: eine Bühne, Logo-Leiste als Wähler, wechselt alle 6 s */
  const slides = $$('.stimme-buehne'), logos = $$('.stimme-logo');
  if (slides.length) {
    let i = 0, timer;
    const zeig = (k) => { i = (k + slides.length) % slides.length; slides.forEach((s, n) => s.classList.toggle('an', n === i)); logos.forEach((l, n) => l.classList.toggle('an', n === i)); };
    const takt = () => { clearInterval(timer); if (!rm) timer = setInterval(() => zeig(i + 1), 6000); };
    logos.forEach((l, n) => l.addEventListener('click', () => { zeig(n); takt(); }));
    takt();
  }

  /* Vergleich: fünf Lagen, wechseln alle 6 s, solange die Bühne im Bild ist; Klick hält an */
  const vb = $('.vgl-buehne');
  if (vb) {
    const tabs = $$('.vgl-tab', vb), pan = $$('.vgl-panel', vb), TAKT = 6000;
    let i = 0, timer = null, steht = rm;
    vb.style.setProperty('--takt', TAKT / 1000 + 's');
    const zeig = (k, fokus) => {
      i = (k + tabs.length) % tabs.length;
      tabs.forEach((t, n) => { const an = n === i; t.classList.toggle('an', an); t.setAttribute('aria-selected', an ? 'true' : 'false'); t.tabIndex = an ? 0 : -1; const l = $('.lauf', t); if (l && an) { l.style.animation = 'none'; void l.offsetWidth; l.style.animation = ''; } });
      pan.forEach((p, n) => { const an = n === i; p.hidden = !an; p.classList.remove('an'); if (an) { void p.offsetWidth; p.classList.add('an'); } });
      if (fokus) tabs[i].focus();
    };
    const lauf = () => { clearInterval(timer); if (!steht) timer = setInterval(() => zeig(i + 1), TAKT); };
    tabs.forEach((t, n) => t.addEventListener('click', () => { steht = true; vb.classList.add('steht'); clearInterval(timer); zeig(n); }));
    vb.addEventListener('keydown', e => { if (!e.target.classList.contains('vgl-tab')) return; if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); steht = true; vb.classList.add('steht'); clearInterval(timer); zeig(i + 1, true); } if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); steht = true; vb.classList.add('steht'); clearInterval(timer); zeig(i - 1, true); } });
    if (rm) vb.classList.add('steht');
    new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { zeig(i); lauf(); } else clearInterval(timer); }), { threshold: .35 }).observe(vb);
  }

  /* Hero: „Mehr [Wort]" — Breite folgt dem Wort, Regler-Strich zeigt den Takt. Alle Wörter liegen im selben Rasterfeld,
     gemessen wird die Breite des Worts (offsetWidth, unberührt vom Transform) — nichts wechselt zwischen absolut/relativ. */
  const we = $('.wechsel');
  if (we) {
    const w = $$(':scope > span', we), T = 2600; let k = 0;
    we.style.setProperty('--wtakt', T / 1000 + 's');
    const breite = () => { we.style.width = w[k].offsetWidth + 'px'; };
    const takt = () => { we.classList.remove('laeuft'); void we.offsetWidth; we.classList.add('laeuft'); };
    we.style.transition = 'none'; breite(); void we.offsetWidth; we.style.transition = '';
    addEventListener('resize', breite);
    if (document.fonts) document.fonts.ready.then(breite);
    if (!rm) {
      takt();
      setInterval(() => {
        const alt = w[k]; k = (k + 1) % w.length; const neu = w[k];
        alt.classList.remove('an'); alt.classList.add('raus'); neu.classList.remove('raus'); neu.classList.add('an');
        breite(); takt();
        setTimeout(() => alt.classList.remove('raus'), 650);
      }, T);
    }
  }

  /* Potenzial-Rechner als Pop-up: eine Frage je Schritt, dann PLZ, dann Kontakt, abschicken (Web3Forms → info@) */
  const dlg = $('#rechner-dialog');
  if (dlg) {
    const form = $('.rd-form', dlg), schritte = $$('.rd-schritt', dlg), balken = $('.rd-balken i', dlg), zurueck = $('.rd-zurueck', dlg);
    const d = {}; let akt = 1; const MAX = 7;
    const eur = n => Math.round(n).toLocaleString('de-DE') + ' €';
    const spur = (name, extra) => { try { (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: name }, extra || {})); } catch (e) {} };
    const zeig = n => {
      akt = n; schritte.forEach(s => { const an = +s.dataset.schritt === n; s.hidden = !an; s.classList.toggle('an', an); });
      balken.style.transform = `scaleX(${Math.min(n, MAX) / MAX})`;
      zurueck.hidden = n === 1 || n === 8;
      const auf = d.ziel === 'Aufträge';
      $$('[data-text-monteure]', dlg).forEach(el => el.textContent = auf ? el.dataset.textAuftraege : el.dataset.textMonteure);
      $$('[data-fuer]', dlg).forEach(el => el.hidden = el.dataset.fuer !== (d.ziel || 'Monteure'));
      if (n === 5) { $('[data-summe]', dlg).textContent = eur((+d.anzahl || 1) * (+d.wert || 5000)); const b = $('[data-beleg-monteure]', dlg); b.textContent = auf ? b.dataset.belegAuftraege : b.dataset.belegMonteure; }
      const f = $('.rd-schritt.an input', dlg); if (f) setTimeout(() => f.focus(), 60);
      spur('rechner_schritt', { schritt: n });
    };
    const oeffne = () => { if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', ''); document.documentElement.classList.add('rd-offen'); zeig(1); spur('rechner_offen'); };
    const zu = () => { if (dlg.close) dlg.close(); else dlg.removeAttribute('open'); document.documentElement.classList.remove('rd-offen'); };
    $$('[data-rechner], a[href="#rechner-auf"]').forEach(b => b.addEventListener('click', e => { e.preventDefault(); oeffne(); }));
    $('.rd-zu', dlg).addEventListener('click', zu);
    dlg.addEventListener('click', e => { if (e.target === dlg) zu(); });
    dlg.addEventListener('close', () => document.documentElement.classList.remove('rd-offen'));
    zurueck.addEventListener('click', () => zeig(Math.max(1, akt - 1)));
    $$('.rd-wahl button', dlg).forEach(b => b.addEventListener('click', () => {
      d[b.dataset.feld] = b.dataset.wert;
      $$(`.rd-wahl button[data-feld="${b.dataset.feld}"]`, dlg).forEach(x => x.classList.toggle('an', x === b));
      setTimeout(() => zeig(akt + 1), 180);
    }));
    $$('[data-weiter]', dlg).forEach(b => b.addEventListener('click', () => {
      const f = $('.rd-schritt.an input[required]', dlg);
      if (f && !f.value.trim()) { f.focus(); f.classList.add('fehlt'); return; }
      zeig(akt + 1);
    }));
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const name = form.elements.name.value.trim(), tel = form.elements.telefon.value.trim(), fehler = $('.rd-fehler', dlg);
      if (!name || !tel) { fehler.hidden = false; return; } fehler.hidden = true;
      const fd = new FormData(form);
      fd.append('Ziel', d.ziel || ''); fd.append('Stelle / Leistung', d.stelle || ''); fd.append('Anzahl je Monat', d.anzahl || ''); fd.append('Wert je Auftrag', d.wert ? eur(+d.wert) : ''); fd.append('Seite', location.pathname);
      const knopf = $('button[type=submit]', form); knopf.disabled = true;
      try { const r = await fetch('https://api.web3forms.com/submit', { method: 'POST', body: fd }); if (!r.ok) throw 0; } catch (x) { knopf.disabled = false; fehler.textContent = 'Das hat nicht geklappt. Ruf gern direkt an: +49 8194 7174990'; fehler.hidden = false; return; }
      const cal = $('[data-cal]', dlg); if (d.ziel === 'Aufträge') cal.href = 'https://calendly.com/noahseelau/leadgen-potenzial';
      spur('rechner_abgeschickt', { ziel: d.ziel }); zeig(8);
    });
  }

  /* Kontakt: Collage aus Shooting-Fotos, alle 1,4 s wechselt ein Feld */
  const col = $('.collage');
  if (col && !rm) {
    let pool = []; try { pool = JSON.parse(col.dataset.pool); } catch (e) {}
    const felder = $$('img', col); let naechstes = felder.length, timer = null;
    const tausch = () => {
      if (!pool.length) return; const f = felder[Math.floor(Math.random() * felder.length)];
      const bild = new Image(); bild.src = pool[naechstes % pool.length]; naechstes++;
      bild.onload = () => { f.classList.add('raus'); setTimeout(() => { f.src = bild.src; f.removeAttribute('srcset'); f.classList.remove('raus'); }, 350); };
    };
    new IntersectionObserver(es => es.forEach(e => { clearInterval(timer); if (e.isIntersecting) timer = setInterval(tausch, 1400); }), { threshold: .2 }).observe(col);
  }

  /* Aktiver Menüpunkt */
  const pfad = location.pathname.replace(/index\.html$/, '');
  $$('.nav-links a').forEach(a => { const h = a.getAttribute('href'); if (h && h !== '/' && pfad.startsWith(h.replace(/index\.html$/, '')) && !a.classList.contains('nav-cta')) a.classList.add('aktiv'); });
})();
