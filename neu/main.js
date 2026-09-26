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
    else { requestAnimationFrame(() => intro.classList.add('los')); setTimeout(() => { intro.classList.add('weg'); try { sessionStorage.setItem('shk-intro', '1'); } catch (e) {} }, 1450); setTimeout(() => intro.remove(), 2100); }
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
      wege.forEach((w, i) => setTimeout(() => w.classList.add('gestempelt'), rm ? 0 : 380 + i * 260));
      setTimeout(() => leiter.classList.add('fertig'), rm ? 0 : 380 + wege.length * 260 + 100);
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

  /* Reels: laufen stumm, sobald im Bild; Ton-Knopf */
  $$('.reel').forEach(f => {
    const vid = $('video', f); if (!vid) return;
    const q = vid.dataset.quelle;
    const o = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { if (q && !vid.src) { vid.src = q; vid.load(); } vid.play().catch(()=>{}); } else { vid.pause(); }
    }), { threshold: .3 });
    o.observe(f);
    const ton = $('.ton', f);
    if (ton) ton.addEventListener('click', () => { const an = vid.muted; $$('.reel video').forEach(x => x.muted = true); $$('.reel .ton').forEach(x => x.textContent = '🔇'); vid.muted = !an; ton.textContent = an ? '🔊' : '🔇'; if (an) vid.play().catch(()=>{}); });
  });

  /* Feed-Bühne: Phones parallaxen */
  const feedPhones = $$('.feed-innen .phone');
  if (feedPhones.length && !rm) {
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

  /* Aktiver Menüpunkt */
  const pfad = location.pathname.replace(/index\.html$/, '');
  $$('.nav-links a').forEach(a => { const h = a.getAttribute('href'); if (h && h !== '/' && pfad.startsWith(h.replace(/index\.html$/, '')) && !a.classList.contains('nav-cta')) a.classList.add('aktiv'); });
})();
