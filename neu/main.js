/* SHK-Seite v3 — „Aufgedreht": Regler, Rohr, Leiter, Kinetik, Bühne */
(function(){
  window.__lebt = true;
  const rm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => [...r.querySelectorAll(s)];
  const clamp = (v,a,b) => Math.max(a, Math.min(b, v));

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
  $$('.rv').forEach(el => io.observe(el));

  /* Bühne (Hero): Clip-Expand + Regler */
  const buehne = $('.buehne');
  const regler = $('.regler');
  let reglerP = 0.5, reglerHand = false, reglerIdle = 0, reglerZiel = 0.5;
  const bahn = regler && $('.bahn', regler);
  if (bahn) { const l = bahn.getTotalLength(); regler.style.setProperty('--bahn-l', l.toFixed(1)); }
  const wertText = regler && $('.wert', regler);
  const wertLabel = regler && $('.wert-label', regler);
  const setRegler = (p) => {
    reglerP = clamp(p, 0, 1);
    if (!regler) return;
    regler.style.setProperty('--p', reglerP.toFixed(3));
    const grad = Math.round(reglerP * 100);
    if (wertText) wertText.textContent = grad + '%';
    if (wertLabel) wertLabel.textContent = reglerP < .34 ? 'kommt nach Zufall' : reglerP < .67 ? 'wird planbar' : 'läuft planbar';
    if (buehne) { buehne.classList.toggle('reg-links', reglerP < .38); buehne.classList.toggle('reg-rechts', reglerP > .62); buehne.classList.toggle('reg-mitte', reglerP >= .38 && reglerP <= .62); }
  };
  if (regler) {
    setRegler(0.12);
    // Ziehen: Winkel um die Nabe
    const winkel = (ev) => {
      const r = regler.getBoundingClientRect();
      const x = ev.clientX - (r.left + r.width/2), y = ev.clientY - (r.top + r.height/2);
      let a = Math.atan2(y, x) * 180 / Math.PI; // -180..180, 0 = rechts
      a = (a + 90 + 360) % 360; // 0 = oben
      if (a > 180) a -= 360; // -180..180, 0 oben
      return clamp((a + 135) / 270, 0, 1);
    };
    regler.addEventListener('pointerdown', ev => { reglerHand = true; regler.setPointerCapture(ev.pointerId); setRegler(winkel(ev)); reglerIdle = performance.now(); });
    regler.addEventListener('pointermove', ev => { if (reglerHand) setRegler(winkel(ev)); });
    const los = () => { reglerHand = false; };
    regler.addEventListener('pointerup', los); regler.addEventListener('pointercancel', los);
    regler.addEventListener('keydown', ev => {
      if (ev.key === 'ArrowRight' || ev.key === 'ArrowUp') { setRegler(reglerP + .05); reglerIdle = performance.now(); ev.preventDefault(); }
      if (ev.key === 'ArrowLeft' || ev.key === 'ArrowDown') { setRegler(reglerP - .05); reglerIdle = performance.now(); ev.preventDefault(); }
    });
    // Von selbst aufdrehen, sobald die Bühne im Bild ist — danach ruht er, bis man ihn anfasst
    let gestartet = false;
    const ioR = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting && !gestartet) {
        gestartet = true;
        const t0 = performance.now(), dauer = rm ? 1 : 2600, von = reglerP, bis = .84;
        const tick = (t) => { if (reglerHand) return; const k = clamp((t - t0) / dauer, 0, 1); const e2 = 1 - Math.pow(1 - k, 3); setRegler(von + (bis - von) * e2); if (k < 1) requestAnimationFrame(tick); };
        requestAnimationFrame(tick);
      }
    }), { threshold: .4 });
    ioR.observe(regler);
  }

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
      const rad = (32 - 14 * k).toFixed(1);
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
      const r = statement.getBoundingClientRect();
      let p;
      if (r.bottom <= h * .92) p = 1; else p = clamp((h * .72 - r.top) / (r.height), 0, 1);
      const n = Math.round(p * worte.length);
      worte.forEach((w, i) => { if (i < n) w.classList.add('an'); });
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

  /* Phones auf Bühne/Unterseiten: Scrollhöhe je Bild */
  $$('.phone .scroller img, .mini-phone img').forEach(img => {
    const set = () => { const box = img.parentElement.getBoundingClientRect(); if (img.naturalHeight) img.style.setProperty('--sk', (box.height / 1038).toFixed(3)); };
    img.complete ? set() : img.addEventListener('load', set); addEventListener('resize', set);
  });

  /* Stimmen: ziehen mit der Maus */
  const bahnS = $('.stimmen-bahn');
  if (bahnS) {
    let down = false, sx = 0, sl = 0, bewegt = 0;
    bahnS.addEventListener('pointerdown', e => { down = true; sx = e.clientX; sl = bahnS.scrollLeft; bewegt = 0; bahnS.classList.add('zieht'); });
    bahnS.addEventListener('pointermove', e => { if (!down) return; const dx = e.clientX - sx; bewegt += Math.abs(dx); bahnS.scrollLeft = sl - dx; });
    const up = () => { down = false; bahnS.classList.remove('zieht'); };
    bahnS.addEventListener('pointerup', up); bahnS.addEventListener('pointerleave', up);
  }

  /* Aktiver Menüpunkt */
  const pfad = location.pathname.replace(/index\.html$/, '');
  $$('.nav-links a').forEach(a => { const h = a.getAttribute('href'); if (h && h !== '/' && pfad.startsWith(h.replace(/index\.html$/, '')) && !a.classList.contains('nav-cta')) a.classList.add('aktiv'); });
})();
