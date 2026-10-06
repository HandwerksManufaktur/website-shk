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
    if (gesehen || rm || matchMedia('(max-width:760px)').matches) intro.remove();
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
  const HANDY = matchMedia('(max-width:760px)').matches && !rm;   // am Handy übernimmt die Handy-Fassung unten (Scroll statt Takt)
  if (leiter && !(HANDY && leiter.classList.contains('wege-plan'))) {
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
    const tabs = $$('.vgl-tab', vb), pan = $$('.vgl-panel', vb), TAKT = matchMedia('(max-width: 760px)').matches ? 10000 : 6000;  // Handy: 10 s je Lage (Noah, 05.10.2026: „die animation geht etwas zu schnell beim handy“)
    let i = 0, timer = null, steht = rm;
    // Reiterleiste scrollt unter 1000 px waagerecht: Kante blendet aus, solange dahinter noch Reiter liegen, und der aktive Reiter rückt ins Bild (Sichtprüfung 29.09.2026)
    const leiste = $('.vgl-tabs', vb);
    const rand = () => { if (!leiste) return; const m = leiste.scrollWidth - leiste.clientWidth; leiste.classList.toggle('rand-r', m > 4 && leiste.scrollLeft < m - 4); leiste.classList.toggle('rand-l', m > 4 && leiste.scrollLeft > 4); };
    if (leiste) { leiste.addEventListener('scroll', rand, { passive: true }); addEventListener('resize', rand, { passive: true }); rand(); }
    vb.style.setProperty('--takt', TAKT / 1000 + 's');
    /* Handy (≤760 px), 05.10.2026: kompakte, interaktive Fassung. Noah zur klebenden Scroll-Bühne: „richtig langsam … langer Abstand … nicht interaktiv“
       → NIE WIEDER Pinnen/Sticky für diese Bühne. Fünf Icons als Raster, kleiner Titel „Lage k von 5“, Wischen über die Karten wechselt die Lage,
       der Takt läuft weiter, ein Tipp/Wisch hält ihn an. Klassen mit Präfix vglm- (keine generischen Namen wie weg/an/aus). */
    const mq = matchMedia('(max-width:760px)');
    let vglmTitel = null;
    {
      const kopf = document.createElement('div');
      kopf.className = 'vglm-titel'; kopf.setAttribute('aria-live', 'polite');
      kopf.innerHTML = '<small></small><b></b>';
      if (leiste) leiste.after(kopf);
      vglmTitel = () => {
        $('small', kopf).textContent = 'Lage ' + (i + 1) + ' von ' + tabs.length;
        $('b', kopf).textContent = $('b', tabs[i]).textContent;
        if (!rm) { kopf.classList.remove('vglm-neu'); void kopf.offsetWidth; kopf.classList.add('vglm-neu'); }
      };
    }
    /* Ein Rahmen, zwei Seiten übereinander (05.10.2026, Noah: „ja genau, mach es bei SHK genauso“ — wie „Gute Arbeit reicht nicht mehr“ auf handwerksmanufaktur.digital):
       erst Heute, nach 3,5 s wischt „Mit eigenen Anzeigen“ von rechts darüber. Kleiner Schalter oben im Rahmen (Ohne uns / Mit uns) springt mit und ist antippbar,
       Tipp auf den Rahmen schaltet um, Wischen links = erst Mit uns, dann nächste Lage. Alles nur ≤ 760 px; am Desktop bleibt es bei den zwei Karten nebeneinander.
       Klassen mit Präfix vglm- (die Karten-Regel .weg hat auf der Schwesterseite einmal den Rahmen überdeckt). */
    const vp = $('.vgl-panels', vb), FLIP = 3500;
    let flip = null, aktivP = null;
    const sch = document.createElement('div'); sch.className = 'vglm-schalter'; sch.dataset.mit = '0';
    sch.setAttribute('role', 'group'); sch.setAttribute('aria-label', 'Vergleich umschalten');
    sch.innerHTML = '<i class="vglm-daumen" aria-hidden="true"></i><button type="button" aria-pressed="true"><i aria-hidden="true">✕</i>Ohne uns</button><button type="button" aria-pressed="false"><i aria-hidden="true">✓</i>Mit uns</button>';
    const [bH, bM] = $$('button', sch);
    if (vp) vp.append(sch);
    const neuStarten = el => { el.style.display = 'none'; void el.offsetWidth; el.style.display = ''; };   // Szenen-Animationen der sichtbaren Seite von vorn
    const ist = () => !!(aktivP && aktivP.classList.contains('vglm-mit'));
    const setMit = mit => {
      clearTimeout(flip);
      const p = aktivP || pan[i]; if (!p) return;
      p.classList.toggle('vglm-mit', mit);
      sch.dataset.mit = mit ? '1' : '0'; bH.setAttribute('aria-pressed', mit ? 'false' : 'true'); bM.setAttribute('aria-pressed', mit ? 'true' : 'false');
      const se = $(mit ? '.vgl-seite.kanal' : '.vgl-seite.heute', p); if (se && mq.matches) neuStarten(se);
    };
    const stopp = () => { steht = true; vb.classList.add('steht'); clearInterval(timer); };
    // Schalter: hält den Takt an und zeigt die gewählte Seite der aktuellen Lage
    bH.addEventListener('click', e => { e.stopPropagation(); stopp(); setMit(false); });
    bM.addEventListener('click', e => { e.stopPropagation(); stopp(); setMit(true); });
    let gewischt = false;
    if (vp) {
      vp.addEventListener('click', () => { if (!mq.matches) return; if (gewischt) { gewischt = false; return; } stopp(); setMit(!ist()); });
      let x0 = 0, y0 = 0, aktiv = false;
      vp.addEventListener('touchstart', e => { if (!mq.matches || e.touches.length !== 1) return; aktiv = true; x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
      vp.addEventListener('touchend', e => {
        if (!aktiv) return; aktiv = false;
        const t = e.changedTouches[0], dx = t.clientX - x0, dy = t.clientY - y0;
        if (Math.abs(dx) < 44 || Math.abs(dx) < Math.abs(dy) * 1.5) return;
        gewischt = true; setTimeout(() => { gewischt = false; }, 400);
        stopp();
        if (dx < 0) { if (!ist()) setMit(true); else zeig(i + 1, false, false); }
        else { if (ist()) setMit(false); else zeig(i - 1, false, true); }
      }, { passive: true });
    }
    const zeig = (k, fokus, mitStart) => {
      i = (k + tabs.length) % tabs.length;
      tabs.forEach((t, n) => { const an = n === i; t.classList.toggle('an', an); t.setAttribute('aria-selected', an ? 'true' : 'false'); t.tabIndex = an ? 0 : -1; const l = $('.lauf', t); if (l && an) { l.style.animation = 'none'; void l.offsetWidth; l.style.animation = ''; } });
      pan.forEach((p, n) => { const an = n === i; p.hidden = !an; p.classList.remove('an', 'vglm-mit'); if (an) { void p.offsetWidth; p.classList.add('an'); aktivP = p; } });
      clearTimeout(flip);
      sch.dataset.mit = '0'; bH.setAttribute('aria-pressed', 'true'); bM.setAttribute('aria-pressed', 'false');
      if (mq.matches) {
        if (mitStart !== undefined) { if (mitStart) setMit(true); }                  // Wisch nach rechts auf die vorige Lage: gleich „Mit uns“
        else if (!rm) flip = setTimeout(() => setMit(true), FLIP);                    // reduzierte Bewegung: Umschalten nur per Tipp
      }
      if (vglmTitel) vglmTitel();
      if (fokus) tabs[i].focus({ preventScroll: true });
      if (leiste && leiste.scrollWidth > leiste.clientWidth + 4) { const x = tabs[i].getBoundingClientRect().left - leiste.getBoundingClientRect().left + leiste.scrollLeft - 16; leiste.scrollTo({ left: Math.max(0, x), behavior: rm ? 'auto' : 'smooth' }); }
    };
    // alle Rahmen gleich hoch: die größte der fünf Lagen (beide Seiten liegen übereinander) bestimmt die Höhe
    const messen = () => {
      vb.style.removeProperty('--vglm-h'); if (!mq.matches) return; let h = 0;
      // je Lage EINZELN messen (die anderen kurz verstecken) — sonst stapeln sich zwei sichtbare Lagen und der Rahmen wird doppelt so hoch (05.10.2026)
      const war = pan.map(p => p.hidden);
      pan.forEach(p => { pan.forEach(x => { x.hidden = x !== p; }); h = Math.max(h, p.offsetHeight); });
      pan.forEach((p, n) => { p.hidden = war[n]; });
      if (h) vb.style.setProperty('--vglm-h', Math.ceil(h) + 'px');
    };
    messen(); addEventListener('load', messen); if (document.fonts) document.fonts.ready.then(messen);
    let bx = innerWidth; addEventListener('resize', () => { if (innerWidth !== bx) { bx = innerWidth; messen(); } });
    const lauf = () => { clearInterval(timer); if (!steht) timer = setInterval(() => zeig(i + 1), TAKT); };
    tabs.forEach((t, n) => t.addEventListener('click', () => { steht = true; vb.classList.add('steht'); clearInterval(timer); zeig(n); }));
    vb.addEventListener('keydown', e => { if (!e.target.classList.contains('vgl-tab')) return; if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); steht = true; vb.classList.add('steht'); clearInterval(timer); zeig(i + 1, true); } if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); steht = true; vb.classList.add('steht'); clearInterval(timer); zeig(i - 1, true); } });
    if (rm) vb.classList.add('steht');
    new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { if (!steht || !aktivP) zeig(i); lauf(); } else clearInterval(timer); }), { threshold: .35 }).observe(vb);
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
    const d = {}; let akt = 1; const MAX = 9; let radarUhr = 0;
    const eur = n => Math.round(n).toLocaleString('de-DE') + ' €';
    const spur = (name, extra) => { try { (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: name }, extra || {})); } catch (e) {} };
    const zeig = n => {
      akt = n; schritte.forEach(s => { const an = +s.dataset.schritt === n; s.hidden = !an; s.classList.toggle('an', an); });
      balken.style.transform = `scaleX(${Math.min(n, MAX) / MAX})`;
      zurueck.hidden = n === 1 || n === 7 || n === 10;
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
    // Enter in einem Feld geht einen Schritt weiter statt das ganze Formular abzuschicken
    form.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.tagName === 'INPUT' && akt < 9) { e.preventDefault(); const w = $('.rd-schritt.an [data-weiter]', dlg); if (w) w.click(); } });
    zurueck.addEventListener('click', () => zeig(akt === 8 ? 6 : Math.max(1, akt - 1)));   // zurück über den Radar hinweg
    $$('.rd-wahl button', dlg).forEach(b => b.addEventListener('click', () => {
      d[b.dataset.feld] = b.dataset.wert;
      $$(`.rd-wahl button[data-feld="${b.dataset.feld}"]`, dlg).forEach(x => x.classList.toggle('an', x === b));
      setTimeout(() => zeig(akt + 1), 180);
    }));
    // Radar nach PLZ + Ort (Noah, 28.09.2026: „nachdem der seine Postleitzahl eingibt, kommt so ein kurzer Radar … in deinem Umfeld ist es möglich“)
    const radar = () => {
      const r = $('[data-radar]', dlg), ok = $('.rd-radar-ok', r), t = $('[data-radar-text]', r);
      const ort = form.elements.ort.value.trim(), plz = form.elements.plz.value.trim();
      clearTimeout(radarUhr); r.classList.remove('fertig'); ok.hidden = true; t.hidden = false;
      t.textContent = `Umkreis ${plz} ${ort} wird vorgemerkt …`;
      const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
      radarUhr = setTimeout(() => {
        r.classList.add('fertig'); t.hidden = true; ok.hidden = false;
        $('[data-radar-titel]', r).textContent = `${ort} ist vorgemerkt.`;
        const k = $('button', ok); if (k) k.focus();
        spur('rechner_radar', { plz });
      }, ruhig ? 300 : 1400);
    };
    $$('[data-weiter]', dlg).forEach(b => b.addEventListener('click', () => {
      const felder = $$('.rd-schritt.an input[required]', dlg);
      let leer = null;
      felder.forEach(f => { const falsch = !f.value.trim() || (f.name === 'plz' && !/^[0-9]{4,5}$/.test(f.value.trim())); f.classList.toggle('fehlt', falsch); if (falsch && !leer) leer = f; });
      const hinweis = $('.rd-schritt.an [data-fehler-ort]', dlg); if (hinweis) hinweis.hidden = !leer;
      if (leer) { leer.focus(); return; }
      zeig(akt + 1);
      if (akt === 7) radar();
    }));
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const name = form.elements.name.value.trim(), tel = form.elements.telefon.value.trim(), fehler = $('[data-fehler-kontakt]', dlg);
      if (!name || !tel) { fehler.hidden = false; return; } fehler.hidden = true;
      const fd = new FormData(form);
      fd.append('Ziel', d.ziel || ''); fd.append('Stelle / Leistung', d.stelle || ''); fd.append('Anzahl je Monat', d.anzahl || ''); fd.append('Wert je Auftrag', d.wert ? eur(+d.wert) : ''); fd.append('Seite', location.pathname);
      const knopf = $('button[type=submit]', form); knopf.disabled = true;
      try { const r = await fetch('https://api.web3forms.com/submit', { method: 'POST', body: fd }); if (!r.ok) throw 0; } catch (x) { knopf.disabled = false; fehler.textContent = 'Das hat nicht geklappt. Ruf gern direkt an: +49 8194 7174990'; fehler.hidden = false; return; }
      const cal = $('[data-cal]', dlg); if (d.ziel === 'Aufträge') cal.href = 'https://calendly.com/noahseelau/leadgen-potenzial';
      spur('rechner_abgeschickt', { ziel: d.ziel }); try { document.dispatchEvent(new CustomEvent('hwm:lead', { detail: { formular: 'rechner-' + (d.ziel || '').toLowerCase() } })); } catch (x) {} zeig(10);
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

  /* Reels-Bahn: unter 900 px (Handy UND Tablet) liegen Reels seitlich in einer Wischbahn — die erreicht der Reveal-Beobachter nie.
     Aufdecken, sobald die Bahn im Bild ist (Prüfung 04.10.2026: zwischen 761 und 900 px blieben Reel 3–5 unsichtbar) */
  /* Reels haben kein Poster und laden erst im Bild — am Handy/Tablet (langsames Netz) standen sie sekundenlang schwarz da.
     Ein Standbild (10–16 KB je Reel) kommt, sobald die Bahn auf 800 px herankommt (Prüfung 04.10.2026). */
  if (matchMedia('(max-width:1180px)').matches) $$('.reel-reihe').forEach(r => { const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { o.disconnect(); $$('video[data-standbild]', r).forEach(v => { if (!v.poster) v.poster = v.dataset.standbild; }); } }), { rootMargin: '800px 0px' }); o.observe(r); });
  if (matchMedia('(max-width:900px)').matches) $$('.reel-reihe').forEach(r => { const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { o.disconnect(); $$('.rv', r).forEach(k => k.classList.add('an')); } }), { threshold: .1 }); o.observe(r); });

  /* Aktiver Menüpunkt */
  const pfad = location.pathname.replace(/index\.html$/, '');
  $$('.nav-links a').forEach(a => { const h = a.getAttribute('href'); if (h && h !== '/' && pfad.startsWith(h.replace(/index\.html$/, '')) && !a.classList.contains('nav-cta')) a.classList.add('aktiv'); });
})();

/* ── Handy-Fassung (03.10.2026): eigene Scroll-Animationen am Telefon ─────────────────────────────────────────────
   EINE Schleife, geglättet (die Szene folgt dem Daumen weich nach), gemessen wird nur beim Laden/Größenwechsel —
   im Takt selbst nur scrollY + gespeicherte Lagen, geschrieben nur transform/opacity bzw. Variablen darauf.
   Desktop läuft hier nie hinein (matchMedia), reduzierte Bewegung bekommt die Endlage aus dem CSS. */
(function () {
  const handy = matchMedia('(max-width:760px)');
  if (!handy.matches) return;
  const rm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const oben = el => el.getBoundingClientRect().top + scrollY;   // nur in messen()
  const spuren = [];
  let h = innerHeight, sy = scrollY, laeuft = false;
  const setze = (el, k, v) => { const alt = el['_' + k]; if (alt !== undefined && Math.abs(alt - v) < .0015) return; el['_' + k] = v; el.style.setProperty(k, v.toFixed(4)); };

  /* Zahlen zählen hoch (Fallstudien, Kennzahlen), sobald sie zur Hälfte im Bild sind */
  const zaehlbar = el => {
    const t = [...el.childNodes].find(n => n.nodeType === 3 && /\d/.test(n.textContent)); if (!t) return;
    const m = t.textContent.match(/^(\s*)([\d.]+)(,\d+)?(.*)$/s); if (!m || m[3]) return;
    const ziel = parseInt(m[2].replace(/\./g, ''), 10); if (!(ziel > 1)) return;
    const fmt = n => m[1] + Math.round(n).toLocaleString('de-DE') + m[4];
    if (rm) return;
    const breite = el.getBoundingClientRect().width; el.style.minWidth = breite ? breite + 'px' : '';   // nichts springt beim Zählen
    // 06.10.2026: gemessen wurde vor der Webschrift — mit Archivo ist die Endzahl breiter, der Text daneben brach beim Zählen um
    // (Safari 360 px, /auftraege/: +18 px). Nach dem Laden der Schrift die Endbreite noch einmal messen.
    if (document.fonts && document.fonts.status !== 'loaded') document.fonts.ready.then(() => {
      const jetzt = t.textContent; t.textContent = fmt(ziel); el.style.minWidth = ''; const w = el.getBoundingClientRect().width; t.textContent = jetzt; if (w) el.style.minWidth = w + 'px';
    });
    t.textContent = fmt(0);
    const o = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return; o.disconnect();
      const t0 = performance.now(), d = 1100 + Math.min(700, String(ziel).length * 90);
      const tick = n => { const k = Math.min(1, (n - t0) / d), e2 = 1 - Math.pow(1 - k, 3); t.textContent = fmt(ziel * e2); if (k < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    }), { threshold: .6 });
    o.observe(el);
  };

  /* Bilder in Wischbahnen: seitlich liegende lädt „lazy" nie (die Bahn schneidet sie ab) — darum „eager", aber erst wenn die Bahn
     auf 900 px herankommt. Vorher geschah das beim Laden und zog 200 KB+ Bilder vor das LCP (PageSpeed mobil /monteure/ 84–88, 04.10.2026). */
  const vorladen = bahn => { const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { o.disconnect(); $$('img[loading="lazy"]', bahn).forEach(i => { i.loading = 'eager'; }); } }), { rootMargin: '900px 0px' }); o.observe(bahn); };

  /* 1 · Hero: Handys fächern auf */
  const feed = $('.hero .feed-innen'), buehne = feed && feed.closest('.buehne');
  if (feed && !rm) { let top = 0; spuren.push({ messen() { top = oben(buehne); }, an(y) { setze(feed, '--fan', clamp((y + h * .86 - top) / (h * .5))); } }); }

  /* 2 · Wege-Plan: Linie läuft, Stempel folgen ihr (beide Richtungen) */
  $$('.leiter.wege-plan').forEach(l => {
    if (rm) return;
    const reihe = $('.wp-reihe', l), wege = $$('.weg', l); if (!reihe || !wege.length) return;
    let rt = 0, rh = 1, mitten = [];
    spuren.push({
      messen() { rt = oben(reihe); rh = reihe.offsetHeight || 1; mitten = wege.map(w => oben(w) + 28 - rt); },
      an(y) {
        const lauf = clamp((y + h * .62 - rt) / rh); setze(reihe, '--lp', lauf);
        let alle = true; wege.forEach((w, i) => { const an = lauf * rh >= mitten[i]; if (w.classList.contains('gestempelt') !== an) w.classList.toggle('gestempelt', an); if (!an) alle = false; });
        if (l.classList.contains('fertig') !== (alle && lauf > .97)) l.classList.toggle('fertig', alle && lauf > .97);
      }
    });
  });

  /* 3 · Karten-Stapel „So wird es warm": stehen bleiben, nächste schiebt sich darüber, die untere tritt zurück */
  const bento = $('.system .bento');
  if (bento && !rm) {
    const karten = $$('.zelle', bento); let halt = [];
    spuren.push({
      messen() {
        let y0 = oben(bento); halt = [];
        karten.forEach((k, i) => { const kh = k.offsetHeight, st = Math.min(72 + i * 12, h - kh - 14); k.style.setProperty('--st', st + 'px'); halt.push(y0 - st); y0 += kh + 14; });
      },
      an(y) { karten.forEach((k, i) => { if (i === karten.length - 1) return; const p = clamp((y - halt[i]) / Math.max(1, halt[i + 1] - halt[i])); setze(k, '--sk', 1 - .07 * p); setze(k, '--dk', .62 * p); }); }
    });
  }

  /* 4 · Hebel: Foto zoomt auf, Haken laufen ein */
  $$('.hebel-karte').forEach(k => {
    const img = $('.bild img', k); if (rm) { k.classList.add('offen'); return; }
    let top = 0;
    spuren.push({ messen() { top = oben(k); }, an(y) { const p = clamp((y + h - top) / (h * .8)); if (img) setze(img, '--zm', 1.22 - .22 * p); const of = y + h * .86 > top + 200; if (k.classList.contains('offen') !== of) k.classList.toggle('offen', of); } });
  });

  /* 5 · Fallstudien als Wischbahn: Punkte zeigen die Lage, einmal antippen genügt; Bilder laden sofort (Bahn rechnet lazy falsch) */
  $$('.fall-grid.drei').forEach(bahn => {
    const karten = $$('.fall-karte', bahn); if (karten.length < 2) return;
    vorladen(bahn);
    const zeigen = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { zeigen.disconnect(); karten.forEach(k => k.classList.add('an')); } }), { threshold: .1 }); zeigen.observe(bahn);
    const punkte = document.createElement('div'); punkte.className = 'fall-punkte'; punkte.setAttribute('role', 'group'); punkte.setAttribute('aria-label', 'Fallstudie wählen');
    karten.forEach((k, n) => { const b = document.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', 'Fallstudie ' + (n + 1) + ' von ' + karten.length); b.innerHTML = '<i></i>'; b.addEventListener('click', () => bahn.scrollTo({ left: k.offsetLeft - (bahn.clientWidth - k.offsetWidth) / 2, behavior: rm ? 'auto' : 'smooth' })); punkte.appendChild(b); });
    bahn.after(punkte);
    const knoepfe = $$('button', punkte); knoepfe[0].classList.add('an');
    const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { const n = karten.indexOf(e.target); knoepfe.forEach((b, m) => { b.classList.toggle('an', m === n); b.setAttribute('aria-current', m === n ? 'true' : 'false'); }); } }), { root: bahn, threshold: .6 });
    karten.forEach(k => o.observe(k));
    if (!rm) { const s = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { s.disconnect(); bahn.classList.add('stups'); setTimeout(() => bahn.classList.remove('stups'), 1500); } }), { threshold: .5 }); s.observe(bahn); }
  });
  $$('.fall-karte .zahl b, .fall-gross .zahl b').forEach(zaehlbar);

  /* 6 · Vergleich: Kanal-Karte steigt über die Heute-Karte */
  const vpan = $('.vgl-panels');
  if (vpan && !rm) { let top = 0; spuren.push({ messen() { top = oben(vpan); }, an(y) { setze(vpan, '--vr', clamp((y + h * .95 - top - 330) / (h * .4))); } }); }

  /* 7 · Über: Porträt mit Tiefe */
  const pz = $('.ueber.offen .bilder.nur-noah .gross');
  if (pz && !rm) { const img = $('img', pz); let top = 0, hh = 1; spuren.push({ messen() { top = oben(pz); hh = pz.offsetHeight; }, an(y) { const p = clamp((y + h - top) / (h + hh)); setze(img, '--pz', 1.18 - .1 * p); img.style.setProperty('--py', ((p - .5) * -28).toFixed(1) + 'px'); } }); }
  $$('.stats .stat b').forEach(zaehlbar);

  /* 8 · Team: Rollen dürfen am Handy umbrechen (feste Leerzeichen nur für den Desktop gedacht) */
  $$('.team .person p').forEach(p => { p.textContent = p.textContent.replace(/\u00a0/g, ' '); });

  /* 10 · Unterseiten-Hero: zwei Handys fächern auf */
  const uph = $('.uhero .buehne-phones');
  if (uph && !rm) { let top = 0; spuren.push({ messen() { top = oben(uph); }, an(y) { setze(uph, '--fan', clamp((y + h * .92 - top) / (h * .45))); } }); }

  /* 11 · Wischbahnen: Zähler „2 / 6“ + Laufbalken, ein Stups beim ersten Erscheinen, Bilder sofort laden */
  $$('.vorteile, .galerie, .wx-uebersicht .wx-raster, .wx-weiter .wx-raster').forEach(bahn => {
    const karten = [...bahn.children]; if (karten.length < 2) return;
    vorladen(bahn);
    const zeigen = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { zeigen.disconnect(); karten.forEach(k => k.classList.add('an')); } }), { threshold: .1 }); zeigen.observe(bahn);   // seitlich liegende Karten erreicht der Reveal-Beobachter nie
    const z = document.createElement('div'); z.setAttribute('aria-hidden', 'true');
    z.innerHTML = `<span class="bahn-zaehler"><b>1</b> / ${karten.length} · wischen</span><span class="bahn-lauf"><i></i></span>`;
    bahn.after(z);
    const nr = $('b', z), lauf = $('.bahn-lauf', z);
    lauf.style.setProperty('--bp', (1 / karten.length).toFixed(3));
    const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { const n = karten.indexOf(e.target) + 1; nr.textContent = n; lauf.style.setProperty('--bp', (n / karten.length).toFixed(3)); } }), { root: bahn, threshold: .6 });
    karten.forEach(k => o.observe(k));
    if (!rm) { const s = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { s.disconnect(); bahn.classList.add('bahn-stups'); setTimeout(() => bahn.classList.remove('bahn-stups'), 1500); } }), { threshold: .5 }); s.observe(bahn); }
  });

  /* 12 · Große Fallstudien: Bild mit Tiefe */
  $$('.fall-gross .vid').forEach(v => {
    if (rm) return; const m = $('img, video', v); if (!m) return; let top = 0, hh = 1;
    spuren.push({ messen() { top = oben(v); hh = v.offsetHeight; }, an(y) { if (y + h < top - 200 || y > top + hh + 200) return; setze(m, '--pz', 1.16 - .16 * clamp((y + h - top) / (h * .9))); } });
  });
  $$('.wx-zahl b').forEach(zaehlbar);

  /* 13 · Ratgeber (06.10.2026): Inhaltsverzeichnis steht am Handy oben und ist zugeklappt — ein Tipp auf „Inhalt" klappt es auf, ein Sprung klappt es wieder zu */
  $$('.wx-toc').forEach(t => {
    const kopf = $('p', t); if (!kopf || !$('ol', t)) return;
    t.classList.add('mo-klapp'); kopf.setAttribute('role', 'button'); kopf.tabIndex = 0; kopf.setAttribute('aria-expanded', 'false');
    const setz = auf => { t.classList.toggle('mo-offen', auf); kopf.setAttribute('aria-expanded', auf ? 'true' : 'false'); };
    kopf.addEventListener('click', () => setz(!t.classList.contains('mo-offen')));
    kopf.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setz(!t.classList.contains('mo-offen')); } });
    $$('a', t).forEach(a => a.addEventListener('click', () => setz(false)));
  });

  /* Schleife */
  const messen = () => { h = innerHeight; spuren.forEach(s => s.messen && s.messen()); los(); };
  const takt = () => {
    const ziel = scrollY; sy += (ziel - sy) * .24; if (Math.abs(ziel - sy) < .5) sy = ziel;
    spuren.forEach(s => s.an(sy));
    if (sy !== ziel) requestAnimationFrame(takt); else laeuft = false;
  };
  function los() { if (!laeuft) { laeuft = true; requestAnimationFrame(takt); } }
  addEventListener('scroll', los, { passive: true });
  addEventListener('resize', messen);
  addEventListener('load', messen);
  if (document.fonts) document.fonts.ready.then(messen);
  let ro = 0; new ResizeObserver(() => { cancelAnimationFrame(ro); ro = requestAnimationFrame(messen); }).observe(document.body);
  messen(); sy = scrollY; spuren.forEach(s => s.an(sy));
  window.__handy = { spuren: spuren.length };
})();

/* ---- Hintergrund-Videos am Handy etwas schneller (05.10.2026, Noah: „lass die videos bisschen schneller durchlaufen da mobil").
        Nur stumme Schleifen-Videos (nicht die Kundenstimmen mit Ton), nur bis 760 px; bei play/loadeddata nachziehen, weil neues Laden das Tempo zurücksetzt. ---- */
(() => {
  if (!matchMedia('(max-width: 760px)').matches) return;
  const TEMPO = 1.3;
  const setze = v => { v.defaultPlaybackRate = TEMPO; if (v.playbackRate !== TEMPO) v.playbackRate = TEMPO; };
  document.querySelectorAll('video[muted][loop]').forEach(v => { setze(v); ['loadeddata', 'play'].forEach(e => v.addEventListener(e, () => setze(v))); });
})();
