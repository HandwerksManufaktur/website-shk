// ─── BOILERPLATE ─────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', function () {
  document.getElementById('aboutPortrait').src = IMG_NOAH_FULL;
  document.getElementById('aboutAvatar').src   = IMG_NOAH_ROUND;
  var sData=[{n:'100+',l:'Betreute Betriebe'},{n:'14 Tage',l:'Bis 1. Anfrage'},{n:'\u20AC40.000',l:'\u00D8 Auftragswert'},{n:'5+ Jahre',l:'Erfahrung'},{n:'DACH',l:'Marktabdeckung'}];
  var st=document.getElementById('statsTrack');
  sData.concat(sData).concat(sData).forEach(function(s,i,a){var d=document.createElement('div');d.className='stat-item';d.innerHTML='<span class="stat-item-num">'+s.n+'</span><span class="stat-item-label">'+s.l+'</span>'+(i<a.length-1?'<span class="stat-sep"></span>':'');st.appendChild(d);});
  var logos=[{img:IMG_SENFTLEBEN,n:'Senftleben'},{img:IMG_GALLEN,n:'Gallenberger'},{img:IMG_GOLDACKER,n:'Goldacker'},{img:IMG_HANNES,n:'Hannes Schmidt'},{img:IMG_BUCHSCHMID,n:'Buchschmid'},{img:IMG_KLASS,n:'Klaß'},{img:IMG_KRAMER,n:'Kramer'},{img:IMG_LANZINGER,n:'Lanzinger'},{img:IMG_LUEDERS,n:'Lüders'},{img:IMG_DITSCH,n:'Ditsch'},{img:IMG_AZEMI,n:'Azemi'},{img:IMG_FRANTI,n:'Franti Construct'},{img:IMG_SUESSMEIER,n:'Süssmeier'},{img:IMG_STIMPFLE,n:'Stimpfle'}];
  var tt=document.getElementById('tickerTrack');
  logos.forEach(function(l){var d=document.createElement('div');d.className='ticker-item';d.innerHTML='<div class="ticker-logo-wrap"><img src="'+l.img+'" alt="'+l.n+'" class="ticker-logo"></div>';tt.appendChild(d);});
  startAnim();
});
document.addEventListener('mousemove',function(e){var g=document.getElementById('cursorGlow');if(g){g.style.left=e.clientX+'px';g.style.top=e.clientY+'px';}});
window.addEventListener('scroll',function(){document.getElementById('navbar').classList.toggle('scrolled',window.scrollY>50);var pc=document.getElementById('processConnector');if(pc){var r=pc.getBoundingClientRect();if(r.top<window.innerHeight*.8)pc.classList.add('active');}});
function toggleMenu(){document.getElementById('mobileMenu').classList.toggle('open');}
var ro=new IntersectionObserver(function(ent){ent.forEach(function(e,i){if(e.isIntersecting){setTimeout(function(){e.target.classList.add('visible');},i*60);ro.unobserve(e.target);}});},{threshold:.08});
document.querySelectorAll('.reveal,.reveal-left,.reveal-right,.reveal-scale').forEach(function(el){ro.observe(el);});
function toggleFaq(el){var it=el.parentElement,op=it.classList.contains('open');document.querySelectorAll('.faq-item.open').forEach(function(i){i.classList.remove('open');});if(!op)it.classList.add('open');}
var so=new IntersectionObserver(function(ent){ent.forEach(function(e){if(!e.isIntersecting)return;e.target.querySelectorAll('.stat-val[data-target]').forEach(function(el){var tg=+el.dataset.target,sf=el.dataset.suffix||'',pf=el.dataset.prefix||'';var dur=1800,t0=performance.now();(function step(ts){var p=Math.min((ts-t0)/dur,1),eq=1-Math.pow(1-p,3);el.textContent=pf+Math.floor(eq*tg).toLocaleString('de')+sf;if(p<1)requestAnimationFrame(step);})(t0);});so.unobserve(e.target);});},{threshold:.3});
var sg=document.querySelector('.results-stats');if(sg)so.observe(sg);
document.querySelectorAll('a[href^="#"]').forEach(function(a){a.addEventListener('click',function(e){var t=document.querySelector(a.getAttribute('href'));if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth',block:'start'});}});});
function openLegal(p){document.getElementById(p+'-page').classList.add('active');document.body.style.overflow='hidden';}
function closeLegal(){document.querySelectorAll('.legal-page').forEach(function(p){p.classList.remove('active');});document.body.style.overflow='';}

// ─── ANIMATION ───────────────────────────────────────────────────────────────
function startAnim(){
  var cv=document.getElementById('bathCanvas');
  if(!cv)return;
  var c=cv.getContext('2d');
  var dpr=Math.min(window.devicePixelRatio||1,2);
  function rsz(){cv.width=cv.offsetWidth*dpr;cv.height=cv.offsetHeight*dpr;c.setTransform(dpr,0,0,dpr,0,0);}
  window.addEventListener('resize',rsz); rsz();
  var W=function(){return cv.offsetWidth;};
  var H=function(){return cv.offsetHeight;};
  var T0=null;

  // shared particles
  var drops=[], ripples=[], lastDrop=0;

  // ── helpers ──────────────────────────────────────────────────────────────
  function eo(t){return 1-Math.pow(1-t,3);}
  function cl(v,a,b){return Math.min(b,Math.max(a,v));}
  function fb(sz){return '700 '+Math.round(sz)+'px "DM Sans",system-ui,sans-serif';}
  function fm(sz){return '500 '+Math.round(sz)+'px "DM Sans",system-ui,sans-serif';}
  function rr(x,y,w,h,r){
    r=Math.min(r,w/2,h/2);
    c.beginPath();c.moveTo(x+r,y);c.arcTo(x+w,y,x+w,y+h,r);c.arcTo(x+w,y+h,x,y+h,r);c.arcTo(x,y+h,x,y,r);c.arcTo(x,y,x+w,y,r);c.closePath();
  }

  // 4 scenes × 6s, 0.7s crossfade
  var SDUR=6, NS=4, FADE=0.7;

  var SCENES=[
    {
      label:'Badsanierung', col:'#22a8d4', shk:'Sanit\u00e4r',
      cards:[
        {icon:'\uD83D\uDEC1',title:'Komplettsanierung',sub:'Thomas W. \u00B7 M\u00FCnchen',  price:'\u20AC 42.000',col:'#22a8d4',delay:0.4},
        {icon:'\uD83D\uDEBF',title:'Teilsanierung',    sub:'Klaus M. \u00B7 Stuttgart',       price:'\u20AC 20.000',col:'#22a8d4',delay:1.0},
        {icon:'\uD83D\uDEC1',title:'Komplettsanierung',sub:'Maria L. \u00B7 Augsburg',        price:'\u20AC 38.000',col:'#22a8d4',delay:1.6},
        {icon:'\uD83D\uDEBF',title:'Teilsanierung',    sub:'Andreas B. \u00B7 Ulm',           price:'\u20AC 15.000',col:'#22a8d4',delay:2.2},
      ]
    },
    {
      label:'W\u00e4rmepumpe', col:'#d4a853', shk:'Heizung',
      cards:[
        {icon:'\uD83D\uDD25',title:'W\u00e4rmepumpe',    sub:'Sabine K. \u00B7 Augsburg',    price:'\u20AC 25.000',col:'#d4a853',delay:0.4},
        {icon:'\uD83C\uDF21\uFE0F',title:'Heizungstausch',sub:'Peter H. \u00B7 N\u00FCrnberg',price:'\u20AC 35.000',col:'#d4a853',delay:1.0},
        {icon:'\uD83D\uDD25',title:'W\u00e4rmepumpe',    sub:'Familie M. \u00B7 Ingolstadt', price:'\u20AC 28.000',col:'#d4a853',delay:1.6},
        {icon:'\uD83C\uDF21\uFE0F',title:'Heizungstausch',sub:'Franz G. \u00B7 Regensburg',  price:'\u20AC 32.000',col:'#d4a853',delay:2.2},
      ]
    },
    {
      label:'Mitarbeiter', col:'#22c55e', shk:'SHK-Team',
      cards:[
        {icon:'\uD83D\uDC64',title:'Heizungsbauer',     sub:'Markus H. \u00B7 M\u00FCnchen',  price:'3 J. Erfahrung',col:'#22c55e',delay:0.4},
        {icon:'\uD83D\uDC64',title:'Anlagenmechaniker', sub:'Stefan K. \u00B7 Augsburg',       price:'5 J. Erfahrung',col:'#22c55e',delay:1.0},
        {icon:'\uD83D\uDC64',title:'Kundendienst.',     sub:'Jonas F. \u00B7 Stuttgart',       price:'2 J. Erfahrung',col:'#22c55e',delay:1.6},
        {icon:'\uD83D\uDC64',title:'Anlagenmechaniker', sub:'Tim R. \u00B7 N\u00FCrnberg',     price:'4 J. Erfahrung',col:'#22c55e',delay:2.2},
      ]
    },
    {
      label:'Klimatisierung', col:'#4285f4', shk:'Klima',
      cards:[
        {icon:'\u2744\uFE0F',title:'Klimatisierung',       sub:'Michael W. \u00B7 M\u00FCnchen', price:'\u20AC 45.000',col:'#4285f4',delay:0.4},
        {icon:'\uD83C\uDF00',title:'L\u00FCftungsanlage',  sub:'Sandra K. \u00B7 Stuttgart',         price:'\u20AC 62.000',col:'#4285f4',delay:1.0},
        {icon:'\u2744\uFE0F',title:'Klimatisierung',       sub:'Thomas H. \u00B7 Augsburg',      price:'\u20AC 38.000',col:'#4285f4',delay:1.6},
        {icon:'\uD83C\uDF00',title:'L\u00FCftungsanlage',  sub:'Familie R. \u00B7 Regensburg',  price:'\u20AC 55.000',col:'#4285f4',delay:2.2},
      ]
    },
  ];

  function getScene(el){
    var tot=SDUR*NS, pos=el%tot, s=Math.floor(pos/SDUR), p=(pos%SDUR)/SDUR;
    var a=p<FADE/SDUR?eo(p*SDUR/FADE):p>1-FADE/SDUR?eo((1-p)*SDUR/FADE):1;
    return{s:s,p:p,a:a,st:pos%SDUR};
  }

  // ── drawCard ─────────────────────────────────────────────────────────────
  function drawCard(x,y,w,h,item,sceneT,delay,alpha){
    var a=cl((sceneT-delay)/.5,0,1)*alpha;
    if(a<=0)return;
    c.save(); c.globalAlpha=a;
    c.translate((1-eo(cl((sceneT-delay)/.5,0,1)))*18,0);
    c.fillStyle='rgba(8,18,32,.82)'; rr(x,y,w,h,8); c.fill();
    c.strokeStyle=item.col+'55'; c.lineWidth=1; rr(x,y,w,h,8); c.stroke();
    c.fillStyle=item.col+'20'; c.fillRect(x+8,y,w-16,3);
    var pulse=.55+Math.sin(sceneT*3+delay)*.4;
    c.fillStyle=item.col; c.globalAlpha=a*pulse;
    c.beginPath(); c.arc(x+14,y+h*.25,3.5,0,6.28); c.fill();
    c.globalAlpha=a;
    c.font='500 '+Math.round(h*.36)+'px serif'; c.textAlign='left';
    c.fillText(item.icon,x+w-h*.48,y+h*.54);
    c.fillStyle='rgba(244,241,235,.92)';
    var fs=h*.28; c.font=fb(fs);
    while(c.measureText(item.title).width>w*.68&&fs>8){fs-=.5;c.font=fb(fs);}
    c.fillText(item.title,x+26,y+h*.4);
    c.fillStyle='rgba(143,168,192,.7)';
    var fs2=h*.22; c.font=fm(fs2);
    while(c.measureText(item.sub).width>w*.72&&fs2>7){fs2-=.5;c.font=fm(fs2);}
    c.fillText(item.sub,x+26,y+h*.63);
    c.fillStyle=item.col;
    var fs3=h*.22; c.font=fb(fs3);
    while(c.measureText(item.price).width>w*.72&&fs3>7){fs3-=.5;c.font=fb(fs3);}
    c.fillText(item.price,x+26,y+h*.84);
    c.textAlign='left'; c.restore();
  }

  // ── SCENE A: Badsanierung ─────────────────────────────────────────────────
  function drawBad(lx,lw,t,a){
    c.save(); c.globalAlpha=a;
    var h=H();
    // warm tile wall
    var ts=Math.round(lw/5);
    c.strokeStyle='rgba(180,155,110,.07)'; c.lineWidth=.8;
    for(var tx=lx;tx<lx+lw;tx+=ts){c.beginPath();c.moveTo(tx,0);c.lineTo(tx,h*.68);c.stroke();}
    for(var ty=0;ty<h*.68;ty+=ts){c.beginPath();c.moveTo(lx,ty);c.lineTo(lx+lw,ty);c.stroke();}
    // ambient
    var ag=c.createRadialGradient(lx+lw*.5,h*.2,0,lx+lw*.5,h*.2,lw*.6);
    ag.addColorStop(0,'rgba(34,168,212,.08)'); ag.addColorStop(1,'rgba(0,0,0,0)');
    c.fillStyle=ag; c.fillRect(lx,0,lw,h*.5);
    var cg=c.createRadialGradient(lx+lw*.2,h*.85,0,lx+lw*.2,h*.85,lw*.4);
    cg.addColorStop(0,'rgba(212,150,40,.1)'); cg.addColorStop(1,'rgba(0,0,0,0)');
    c.fillStyle=cg; c.fillRect(lx,h*.5,lw,h*.5);
    // ceiling rain shower
    var shCx=lx+lw*.45, shW=lw*.32, shY=h*.05, rhH=h*.02;
    c.strokeStyle='rgba(190,175,140,.35)'; c.lineWidth=2.5; c.lineCap='round';
    c.beginPath(); c.moveTo(shCx,0); c.lineTo(shCx,shY); c.stroke(); c.lineCap='butt';
    var rhG=c.createLinearGradient(shCx-shW/2,shY,shCx-shW/2,shY+rhH);
    rhG.addColorStop(0,'rgba(200,185,150,.5)'); rhG.addColorStop(1,'rgba(160,145,110,.35)');
    c.fillStyle=rhG; rr(shCx-shW/2,shY,shW,rhH,4); c.fill();
    c.strokeStyle='rgba(190,175,140,.45)'; c.lineWidth=1; c.stroke();
    c.fillStyle='rgba(34,168,212,.55)';
    var nC=9,nR=2,nsx=shW/(nC+1),nsy=rhH/(nR+1);
    for(var nr=0;nr<nR;nr++) for(var nc=0;nc<nC;nc++){c.beginPath();c.arc(shCx-shW/2+nsx*(nc+1),shY+nsy*(nr+1),.9,0,6.28);c.fill();}
    // rain drops
    for(var rd=0;rd<16;rd++){
      var rdx=shCx-shW/2+8+(rd/15)*(shW-16);
      var rdt=((t*.7+rd*.063)%1);
      var rdy=shY+rhH+rdt*(h*.48);
      var rda=(rdt<.08?rdt/.08:rdt>.85?(1-rdt)/.15:1)*.4;
      c.save(); c.globalAlpha=rda; c.strokeStyle='rgba(34,168,212,.6)'; c.lineWidth=1;
      c.beginPath(); c.moveTo(rdx,rdy); c.lineTo(rdx,rdy+h*.038); c.stroke(); c.restore();
    }


    // ── Shower floor (no box, transparent) ──────────────────────────────
    var tbx=lx, tby=h*.76, tbw=lw, tbh=h*.16;
    // tile grid
    var tW=tbw/7, tH=tbh/3;
    c.strokeStyle='rgba(34,168,212,.1)'; c.lineWidth=1;
    for(var ftx=0;ftx<=7;ftx++){c.beginPath();c.moveTo(tbx+ftx*tW,tby);c.lineTo(tbx+ftx*tW,tby+tbh);c.stroke();}
    for(var fty=0;fty<=3;fty++){c.beginPath();c.moveTo(tbx,tby+fty*tH);c.lineTo(tbx+tbw,tby+fty*tH);c.stroke();}
    // wall–floor edge
    c.strokeStyle='rgba(34,168,212,.2)'; c.lineWidth=1.5;
    c.beginPath(); c.moveTo(tbx,tby); c.lineTo(tbx+tbw,tby); c.stroke();
    // linear drain near bottom
    var drY=tby+tbh*.78;
    c.fillStyle='rgba(6,14,24,.95)'; c.fillRect(tbx+tbw*.08,drY,tbw*.84,5);
    c.strokeStyle='rgba(34,168,212,.28)'; c.lineWidth=1;
    c.beginPath(); c.moveTo(tbx+tbw*.08,drY); c.lineTo(tbx+tbw*.92,drY); c.stroke();
    c.beginPath(); c.moveTo(tbx+tbw*.08,drY+5); c.lineTo(tbx+tbw*.92,drY+5); c.stroke();
    c.strokeStyle='rgba(34,168,212,.2)'; c.lineWidth=1; c.lineCap='round';
    for(var ds=0;ds<14;ds++){var dsx=tbx+tbw*.1+ds*(tbw*.8/13);c.beginPath();c.moveTo(dsx,drY+1);c.lineTo(dsx,drY+4);c.stroke();}
    c.lineCap='butt';

    // ── Armatur ──────────────────────────────────────────────────────────
    var ax=lx+lw*.7, mY=h*.44, pR=Math.min(lw*.07,h*.052);
    // round plate
    c.fillStyle='rgba(22,40,62,.88)';
    c.beginPath(); c.arc(ax,mY,pR,0,6.28); c.fill();
    c.strokeStyle='rgba(150,165,180,.3)'; c.lineWidth=1; c.stroke();
    // lever straight down
    c.fillStyle='rgba(130,148,168,.5)';
    c.beginPath(); c.moveTo(ax-pR*.22,mY+pR*.4); c.lineTo(ax-pR*.22,mY+pR*2.1);
    c.quadraticCurveTo(ax-pR*.22,mY+pR*2.4,ax,mY+pR*2.4);
    c.quadraticCurveTo(ax+pR*.22,mY+pR*2.4,ax+pR*.22,mY+pR*2.1);
    c.lineTo(ax+pR*.22,mY+pR*.4); c.closePath(); c.fill();
    c.strokeStyle='rgba(150,165,180,.28)'; c.lineWidth=1; c.stroke();

    // ── Shower drops (from ceiling head, simple) ─────────────────────────
    if(ts2-lastDrop>100+Math.random()*90){
      var fromRain=Math.random()<.8;
      drops.push({
        x:fromRain?shCx-shW/2+8+Math.random()*(shW-16):ax+(Math.random()-.5)*20,
        y:fromRain?shY+rhH:mY-pR,
        vy:3.5+Math.random()*2.5, vx:(Math.random()-.5)*.1,
        r:1+Math.random()*1.2, alpha:.5+Math.random()*.4, trail:[]
      });
      lastDrop=ts2;
    }
    drops=drops.filter(function(d){return d.y<tby+tbh&&d.alpha>.02;});
    drops.forEach(function(d){
      d.trail.push({x:d.x,y:d.y}); if(d.trail.length>7) d.trail.shift();
      d.trail.forEach(function(tr,ti){
        c.save();c.globalAlpha=d.alpha*(ti/d.trail.length)*.22;
        c.strokeStyle='rgba(34,168,212,.8)'; c.lineWidth=d.r*.8;
        if(ti>0){var prev=d.trail[ti-1];c.beginPath();c.moveTo(prev.x,prev.y);c.lineTo(tr.x,tr.y);c.stroke();}
        c.restore();
      });
      c.save(); c.globalAlpha=d.alpha*.85;
      c.fillStyle='rgba(180,235,255,.9)';
      c.save(); c.translate(d.x,d.y); c.scale(.6,1.2);
      c.beginPath(); c.arc(0,0,d.r,0,6.28); c.fill();
      c.restore(); c.restore();
      d.vy*=1.038; d.x+=d.vx; d.y+=d.vy;
    });
    c.restore();
  }

  // ── SCENE B: Wärmepumpe ───────────────────────────────────────────────────
  function drawWaerme(lx,lw,t,a){
    c.save(); c.globalAlpha=a;
    var h=H();
    var ag=c.createRadialGradient(lx+lw*.5,h*.55,0,lx+lw*.5,h*.55,lw*.6);
    ag.addColorStop(0,'rgba(212,100,20,.08)'); ag.addColorStop(1,'rgba(0,0,0,0)');
    c.fillStyle=ag; c.fillRect(lx,0,lw,h);
    c.strokeStyle='rgba(34,168,212,.07)'; c.lineWidth=1;
    c.beginPath(); c.moveTo(lx,h*.88); c.lineTo(lx+lw,h*.88); c.stroke();
    // unit housing
    var ux=lx+lw*.15, uy=h*.18, uw=lw*.7, uh=h*.6;
    var ug=c.createLinearGradient(ux,uy,ux+uw*.4,uy+uh);
    ug.addColorStop(0,'#1c2e42'); ug.addColorStop(.5,'#152438'); ug.addColorStop(1,'#0f1c2e');
    c.fillStyle=ug;
    c.beginPath(); c.moveTo(ux+10,uy); c.lineTo(ux+uw-10,uy);
    c.quadraticCurveTo(ux+uw,uy,ux+uw,uy+10); c.lineTo(ux+uw,uy+uh-10);
    c.quadraticCurveTo(ux+uw,uy+uh,ux+uw-10,uy+uh); c.lineTo(ux+10,uy+uh);
    c.quadraticCurveTo(ux,uy+uh,ux,uy+uh-10); c.lineTo(ux,uy+10);
    c.quadraticCurveTo(ux,uy,ux+10,uy); c.closePath(); c.fill();
    var bs=c.createLinearGradient(ux,uy,ux+uw,uy);
    bs.addColorStop(0,'rgba(212,100,20,.55)'); bs.addColorStop(1,'rgba(212,150,30,.55)');
    c.fillStyle=bs; c.fillRect(ux+10,uy,uw-20,5);
    c.strokeStyle='rgba(212,100,20,.25)'; c.lineWidth=1.5;
    c.beginPath(); c.moveTo(ux+10,uy); c.lineTo(ux+uw-10,uy);
    c.quadraticCurveTo(ux+uw,uy,ux+uw,uy+10); c.lineTo(ux+uw,uy+uh-10);
    c.quadraticCurveTo(ux+uw,uy+uh,ux+uw-10,uy+uh); c.lineTo(ux+10,uy+uh);
    c.quadraticCurveTo(ux,uy+uh,ux,uy+uh-10); c.lineTo(ux,uy+10);
    c.quadraticCurveTo(ux,uy,ux+10,uy); c.stroke();
    c.strokeStyle='rgba(34,168,212,.07)'; c.lineWidth=1;
    [.3,.54,.76].forEach(function(f){c.beginPath();c.moveTo(ux+4,uy+uh*f);c.lineTo(ux+uw-4,uy+uh*f);c.stroke();});
    // fan
    var fcx=lx+lw*.5, fcy=uy+uh*.44, fR=uw*.28;
    c.strokeStyle='rgba(34,168,212,.14)'; c.lineWidth=1.5; c.beginPath(); c.arc(fcx,fcy,fR,0,6.28); c.stroke();
    c.strokeStyle='rgba(34,168,212,.08)'; c.lineWidth=1;
    [.7,.4].forEach(function(f){c.beginPath();c.arc(fcx,fcy,fR*f,0,6.28);c.stroke();});
    c.strokeStyle='rgba(190,170,130,.28)'; c.lineWidth=2.5; c.lineCap='round';
    for(var b=0;b<5;b++){
      var ang=t*.9+b*Math.PI*.4;
      c.beginPath(); c.moveTo(fcx+Math.cos(ang)*fR*.25,fcy+Math.sin(ang)*fR*.25);
      c.lineTo(fcx+Math.cos(ang+.65)*fR*.85,fcy+Math.sin(ang+.65)*fR*.85); c.stroke();
    }
    c.lineCap='butt';
    c.fillStyle='rgba(212,100,20,.38)'; c.beginPath(); c.arc(fcx,fcy,fR*.08,0,6.28); c.fill();
    // status panel
    var px=ux+uw*.86, py=uy+uh*.03, pw=uw*.09, ph=uh*.09;
    c.fillStyle='rgba(8,18,32,.72)'; rr(px,py,pw,ph,5); c.fill();
    c.strokeStyle='rgba(212,100,20,.22)'; c.lineWidth=1; c.stroke();
    var led=.5+Math.sin(t*3)*.45;
    var onMidY=py+ph*.5;
    var onFs=Math.round(pw*.26); c.font=fm(onFs);
    var onTw=c.measureText('ON').width;
    var onTotalW=4.4+pw*.08+onTw;
    var onStartX=px+(pw-onTotalW)/2;
    c.fillStyle='rgba(34,197,94,'+led+')'; c.beginPath(); c.arc(onStartX+2.2,onMidY,2.2,0,6.28); c.fill();
    c.fillStyle='rgba(34,197,94,.55)'; c.textAlign='left';
    c.fillText('ON',onStartX+4.4+pw*.08,onMidY+onFs*.36);
    c.textAlign='left';
    // pipes
    c.strokeStyle='rgba(130,158,180,.2)'; c.lineWidth=4.5; c.lineCap='round';
    c.beginPath(); c.moveTo(ux+uw*.3,uy+uh); c.lineTo(ux+uw*.3,h*.88); c.stroke();
    c.beginPath(); c.moveTo(ux+uw*.7,uy+uh); c.lineTo(ux+uw*.7,h*.88); c.stroke();
    c.lineCap='butt';
    c.fillStyle='rgba(100,135,165,.28)'; c.font=fm(Math.round(h*.016)); c.textAlign='center';
    c.fillText('VL',ux+uw*.3,h*.87+h*.022); c.fillText('RL',ux+uw*.7,h*.87+h*.022);
    // heat waves
    for(var wave=0;wave<5;wave++){
      var wx3=ux+uw*.12+wave*(uw*.76/4);
      c.strokeStyle='rgba(212,100,20,'+(0.07+wave*.012)+')'; c.lineWidth=1.5;
      c.beginPath();
      for(var pt=0;pt<=8;pt++){
        var py2=uy-pt*(h*.065);
        var px2=wx3+Math.sin(t*1.3+wave*.7+pt*.6)*8*(1-pt/8);
        pt===0?c.moveTo(px2,py2):c.lineTo(px2,py2);
      }
      c.stroke();
    }
    c.textAlign='left'; c.restore();
  }

  // ── SCENE C: Mitarbeiter ──────────────────────────────────────────────────
  function drawMitarbeiter(lx,lw,t,a){
    c.save(); c.globalAlpha=a;
    var h=H();
    var ag=c.createRadialGradient(lx+lw*.5,h*.4,0,lx+lw*.5,h*.4,lw*.6);
    ag.addColorStop(0,'rgba(34,197,94,.07)'); ag.addColorStop(1,'rgba(0,0,0,0)');
    c.fillStyle=ag; c.fillRect(lx,0,lw,h);
    var people=[
      {x:lx+lw*.2,y:h*.3,col:'#22a8d4',label:'Heizungsmonteur',delay:0},
      {x:lx+lw*.5,y:h*.2,col:'#22c55e',label:'Heizungsbauer',delay:.3},
      {x:lx+lw*.8,y:h*.3,col:'#d4a853',label:'Anlagenmech.',delay:.6},
    ];
    people.forEach(function(p,i){
      var bob=Math.sin(t*.85+i*2)*4, pa=cl((t-p.delay)/.5,0,1);
      var r=Math.min(h*.048,34);
      c.save(); c.globalAlpha=pa;
      var pg=c.createRadialGradient(p.x,p.y+bob,0,p.x,p.y+bob,r*1.8);
      pg.addColorStop(0,p.col+'15'); pg.addColorStop(1,'rgba(0,0,0,0)');
      c.fillStyle=pg; c.fillRect(p.x-r*2,p.y+bob-r*2,r*4,r*4);
      c.fillStyle=p.col+'20'; c.beginPath(); c.arc(p.x,p.y+bob,r,0,6.28); c.fill();
      c.strokeStyle=p.col; c.lineWidth=1.5; c.beginPath(); c.arc(p.x,p.y+bob,r,0,6.28); c.stroke();
      c.fillStyle=p.col+'88'; c.beginPath(); c.arc(p.x,p.y+bob-r*.32,r*.28,0,6.28); c.fill();
      c.strokeStyle=p.col+'77'; c.lineWidth=2; c.lineCap='round';
      c.beginPath(); c.arc(p.x,p.y+bob+r*.1,r*.42,Math.PI*.18,Math.PI*.82); c.stroke();
      c.lineCap='butt';
      if(pa>.8){
        c.fillStyle='#22c55e'; c.beginPath(); c.arc(p.x+r*.65,p.y+bob-r*.65,r*.26,0,6.28); c.fill();
        c.fillStyle='#fff'; c.font=fb(Math.round(r*.3)); c.textAlign='center';
        c.fillText('\u2713',p.x+r*.65,p.y+bob-r*.58);
      }
      c.fillStyle='rgba(244,241,235,.58)'; c.font=fm(Math.round(h*.019)); c.textAlign='center';
      c.fillText(p.label,p.x,p.y+bob+r+h*.038);
      c.restore();
    });
    c.strokeStyle='rgba(34,197,94,.1)'; c.lineWidth=1; c.setLineDash([3,5]);
    people.forEach(function(p,i){if(i<2){c.beginPath();c.moveTo(p.x,p.y);c.lineTo(people[i+1].x,people[i+1].y);c.stroke();}});
    c.setLineDash([]);
    var na=cl((t-2)/.6,0,1);
    if(na>0){
      var nw=Math.min(lw*.82,280), nh=h*.14, nx=lx+lw*.5-nw/2, ny=h*.62;
      c.save(); c.globalAlpha=na; c.translate(0,(1-eo(na))*20);
      c.fillStyle='rgba(4,16,6,.95)'; rr(nx,ny,nw,nh,9); c.fill();
      c.strokeStyle='rgba(34,197,94,.5)'; c.lineWidth=1.2; c.stroke();
      c.fillStyle='rgba(34,197,94,.2)'; c.fillRect(nx+9,ny,nw-18,3);
      var pulse2=.55+Math.sin(t*4)*.4;
      c.fillStyle='rgba(34,197,94,'+pulse2+')'; c.beginPath(); c.arc(nx+16,ny+nh*.3,4,0,6.28); c.fill();
      c.fillStyle='rgba(34,197,94,.9)'; c.font=fb(Math.round(nw*.068)); c.textAlign='left';
      c.fillText('Neue Bewerbung!',nx+28,ny+nh*.35);
      c.fillStyle='rgba(244,241,235,.88)'; c.font=fb(Math.round(nw*.072));
      c.fillText('Markus H. \u00B7 Heizungsbauer',nx+14,ny+nh*.62);
      c.fillStyle='rgba(34,197,94,.65)'; c.font=fm(Math.round(nw*.064));
      c.fillText('3 Jahre Erfahrung \u00B7 M\u00FCnchen',nx+14,ny+nh*.84);
      c.restore(); c.textAlign='left';
    }
    c.textAlign='left'; c.restore();
  }

  // ── SCENE D: Klimatisierung ───────────────────────────────────────────────
  function drawKlima(lx,lw,t,a){
    c.save(); c.globalAlpha=a;
    var h=H();
    var ag=c.createRadialGradient(lx+lw*.5,h*.45,0,lx+lw*.5,h*.45,lw*.65);
    ag.addColorStop(0,'rgba(66,133,244,.09)'); ag.addColorStop(1,'rgba(0,0,0,0)');
    c.fillStyle=ag; c.fillRect(lx,0,lw,h);
    var gs2=Math.round(lw/6);
    c.strokeStyle='rgba(66,133,244,.06)'; c.lineWidth=.8;
    for(var gx2=lx;gx2<lx+lw;gx2+=gs2){c.beginPath();c.moveTo(gx2,0);c.lineTo(gx2,h);c.stroke();}
    for(var gy2=0;gy2<h;gy2+=gs2){c.beginPath();c.moveTo(lx,gy2);c.lineTo(lx+lw,gy2);c.stroke();}
    // indoor split unit
    var ux=lx+lw*.08, uy=h*.14, uw=lw*.78, uh=h*.15;
    var ug=c.createLinearGradient(ux,uy,ux,uy+uh);
    ug.addColorStop(0,'#1c2e48'); ug.addColorStop(1,'#121e30');
    c.fillStyle=ug;
    c.beginPath(); c.moveTo(ux+8,uy); c.lineTo(ux+uw-8,uy);
    c.quadraticCurveTo(ux+uw,uy,ux+uw,uy+8); c.lineTo(ux+uw,uy+uh-6);
    c.quadraticCurveTo(ux+uw,uy+uh,ux+uw-8,uy+uh); c.lineTo(ux+8,uy+uh);
    c.quadraticCurveTo(ux,uy+uh,ux,uy+uh-6); c.lineTo(ux,uy+8);
    c.quadraticCurveTo(ux,uy,ux+8,uy); c.closePath(); c.fill();
    c.strokeStyle='rgba(66,133,244,.35)'; c.lineWidth=1.5; c.stroke();
    var tb2=c.createLinearGradient(ux,uy,ux+uw,uy);
    tb2.addColorStop(0,'rgba(66,133,244,.5)'); tb2.addColorStop(1,'rgba(100,180,255,.5)');
    c.fillStyle=tb2; c.fillRect(ux+8,uy,uw-16,4);
    c.strokeStyle='rgba(66,133,244,.18)'; c.lineWidth=1;
    for(var sl=0;sl<7;sl++){var sly=uy+uh*.55+sl*(uh*.06);c.beginPath();c.moveTo(ux+uw*.08,sly);c.lineTo(ux+uw*.92,sly);c.stroke();}
    var led3=.5+Math.sin(t*2.8)*.45;
    c.fillStyle='rgba(66,133,244,'+led3+')'; c.beginPath(); c.arc(ux+uw*.92,uy+uh*.3,3,0,6.28); c.fill();
    c.fillStyle='rgba(180,210,255,.8)'; c.font='700 '+Math.round(uh*.38)+'px DM Sans,system-ui,sans-serif'; c.textAlign='center';
    c.fillText('22\u00B0C',lx+lw*.5,uy+uh*.65); c.textAlign='left';
    // ductwork
    c.strokeStyle='rgba(66,133,244,.12)'; c.lineWidth=12; c.lineCap='square';
    c.beginPath(); c.moveTo(ux,h*.38); c.lineTo(lx+lw*.95,h*.38); c.stroke();
    [lx+lw*.22,lx+lw*.45,lx+lw*.68,lx+lw*.88].forEach(function(dx){
      c.strokeStyle='rgba(66,133,244,.1)'; c.lineWidth=9;
      c.beginPath(); c.moveTo(dx,h*.38); c.lineTo(dx,h*.82); c.stroke();
      c.strokeStyle='rgba(66,133,244,.22)'; c.lineWidth=1;
      for(var vl=0;vl<5;vl++){c.beginPath();c.moveTo(dx-7,h*.82+vl*4.5);c.lineTo(dx+7,h*.82+vl*4.5);c.stroke();}
    });
    c.lineCap='butt';
    // cold air particles
    for(var fp=0;fp<12;fp++){
      var fpt=((t*.55+fp*.083)%1);
      var fpx=ux+uw*.08+(fp%4)*(uw*.28);
      var fpy=uy+uh+fpt*h*.55;
      var fpa=(fpt<.1?fpt/.1:fpt>.8?(1-fpt)/.2:1)*.18;
      c.save(); c.globalAlpha=fpa;
      var fpg=c.createRadialGradient(fpx,fpy,0,fpx,fpy,8);
      fpg.addColorStop(0,'rgba(150,210,255,.8)'); fpg.addColorStop(1,'rgba(66,133,244,0)');
      c.fillStyle=fpg; c.beginPath(); c.arc(fpx,fpy,8,0,6.28); c.fill(); c.restore();
    }
    // snowflakes
    for(var sf=0;sf<8;sf++){
      var sft=((t*.35+sf*.125)%1);
      var sfx=lx+lw*.08+sf*(lw*.12)+Math.sin(t*.6+sf)*lw*.04;
      var sfy=uy+uh+h*.05+sft*(h*.65);
      var sfa=(sft<.08?sft/.08:sft>.85?(1-sft)/.15:1)*.35;
      var sfr=4+sf%3;
      c.save(); c.globalAlpha=sfa; c.strokeStyle='rgba(150,210,255,.8)'; c.lineWidth=1; c.lineCap='round';
      for(var sa=0;sa<6;sa++){
        var sang=sa*Math.PI/3+t*.2;
        c.beginPath(); c.moveTo(sfx,sfy); c.lineTo(sfx+Math.cos(sang)*sfr,sfy+Math.sin(sang)*sfr); c.stroke();
        var mx=sfx+Math.cos(sang)*sfr*.55, my=sfy+Math.sin(sang)*sfr*.55, sp3=sang+Math.PI/2;
        c.beginPath(); c.moveTo(mx+Math.cos(sp3)*sfr*.22,my+Math.sin(sp3)*sfr*.22);
        c.lineTo(mx-Math.cos(sp3)*sfr*.22,my-Math.sin(sp3)*sfr*.22); c.stroke();
      }
      c.lineCap='butt'; c.restore();
    }
    // small outdoor unit
    var ox=lx+lw*.62, oy=h*.72, ow=lw*.3, oh=h*.18;
    var og=c.createLinearGradient(ox,oy,ox,oy+oh);
    og.addColorStop(0,'#1a2838'); og.addColorStop(1,'#0e1820');
    c.fillStyle=og;
    c.beginPath(); c.moveTo(ox+6,oy); c.lineTo(ox+ow-6,oy);
    c.quadraticCurveTo(ox+ow,oy,ox+ow,oy+6); c.lineTo(ox+ow,oy+oh-6);
    c.quadraticCurveTo(ox+ow,oy+oh,ox+ow-6,oy+oh); c.lineTo(ox+6,oy+oh);
    c.quadraticCurveTo(ox,oy+oh,ox,oy+oh-6); c.lineTo(ox,oy+6);
    c.quadraticCurveTo(ox,oy,ox+6,oy); c.closePath(); c.fill();
    c.strokeStyle='rgba(66,133,244,.25)'; c.lineWidth=1; c.stroke();
    var ofcx=ox+ow*.5, ofcy=oy+oh*.5, ofr=Math.min(ow,oh)*.35;
    c.strokeStyle='rgba(66,133,244,.15)'; c.lineWidth=1; c.beginPath(); c.arc(ofcx,ofcy,ofr,0,6.28); c.stroke();
    c.strokeStyle='rgba(150,180,220,.25)'; c.lineWidth=1.5; c.lineCap='round';
    for(var ob=0;ob<4;ob++){
      var oang=t*1.1+ob*Math.PI*.5;
      c.beginPath(); c.moveTo(ofcx+Math.cos(oang)*ofr*.2,ofcy+Math.sin(oang)*ofr*.2);
      c.lineTo(ofcx+Math.cos(oang+.5)*ofr*.88,ofcy+Math.sin(oang+.5)*ofr*.88); c.stroke();
    }
    c.lineCap='butt';
    c.strokeStyle='rgba(66,133,244,.15)'; c.lineWidth=4;
    c.beginPath(); c.moveTo(ox,oy+oh*.5); c.lineTo(ux+uw,uy+uh*.5); c.stroke();
    c.textAlign='left'; c.restore();
  }

  // ── RENDER ───────────────────────────────────────────────────────────────
  var ts2=0;
  function render(ts){
    ts2=ts;
    if(!T0)T0=ts;
    var t=(ts-T0)/1000;
    var w=W(), h=H();
    c.clearRect(0,0,w,h);

    // subtle bg grid
    c.strokeStyle='rgba(34,168,212,.038)'; c.lineWidth=1;
    var gs=Math.round(w/13);
    for(var gx=0;gx<w;gx+=gs){c.beginPath();c.moveTo(gx,0);c.lineTo(gx,h);c.stroke();}
    for(var gy=0;gy<h;gy+=gs){c.beginPath();c.moveTo(0,gy);c.lineTo(w,gy);c.stroke();}

    var sc=getScene(t), s=sc.s, a=sc.a, st=sc.st;
    var lx=w*.01, lw=w*.62;
    var rx=w*.68, maxCw=w-rx-w*.006;

    // when not in Bad scene, fade drops
    if(s!==0){drops.forEach(function(d){d.alpha*=.94;}); drops=drops.filter(function(d){return d.alpha>.02;});}

    // LEFT animation
    if(s===0)      drawBad(lx,lw,t,a);
    else if(s===1) drawWaerme(lx,lw,t,a);
    else if(s===2) drawMitarbeiter(lx,lw,t,a);
    else           drawKlima(lx,lw,t,a);

    // TOP: SHK icons horizontal
    var shkY=h*.05;
    var shkItems=[
      {label:'Sanit\u00e4r', col:'#22a8d4', active:s===0, draw:'S'},
      {label:'Heizung',       col:'#d4a853', active:s===1, draw:'H'},
      {label:'Klima',         col:'#4285f4', active:s===3, draw:'K'},
      {label:'Team',          col:'#22c55e', active:s===2, draw:'T'},
    ];
    var shkSpacing=maxCw/shkItems.length;
    shkItems.forEach(function(item,i){
      var icx=rx+i*shkSpacing+shkSpacing*.5;
      c.save(); c.globalAlpha=item.active?1:.35;
      var ir=Math.min(h*.026,17);
      c.fillStyle='rgba(8,18,32,.75)'; c.beginPath(); c.arc(icx,shkY,ir,0,6.28); c.fill();
      c.strokeStyle=item.col; c.lineWidth=item.active?1.8:1; c.beginPath(); c.arc(icx,shkY,ir,0,6.28); c.stroke();
      var sr=ir*.52;
      c.strokeStyle=item.col; c.lineWidth=1.8; c.lineCap='round'; c.lineJoin='round';
      if(item.draw==='S'){
        c.beginPath(); c.moveTo(icx,shkY-sr*.9); c.quadraticCurveTo(icx+sr*.78,shkY,icx,shkY+sr*.85); c.quadraticCurveTo(icx-sr*.78,shkY,icx,shkY-sr*.9); c.stroke();
      } else if(item.draw==='H'){
        c.beginPath(); c.moveTo(icx,shkY+sr*.9); c.bezierCurveTo(icx-sr*.7,shkY+sr*.3,icx-sr*.5,shkY-sr*.2,icx,shkY-sr*.5); c.bezierCurveTo(icx+sr*.1,shkY,icx+sr*.05,shkY+sr*.2,icx+sr*.2,shkY+sr*.15); c.bezierCurveTo(icx+sr*.7,shkY-sr*.1,icx+sr*.55,shkY-sr*.55,icx+sr*.25,shkY-sr*.75); c.bezierCurveTo(icx+sr*.8,shkY-sr*.35,icx+sr*.85,shkY+sr*.15,icx,shkY+sr*.9); c.stroke();
      } else if(item.draw==='K'){
        for(var sp2=0;sp2<6;sp2++){var ang=sp2*Math.PI/3;c.beginPath();c.moveTo(icx,shkY);c.lineTo(icx+Math.cos(ang)*sr*.88,shkY+Math.sin(ang)*sr*.88);c.stroke();var mx=icx+Math.cos(ang)*sr*.5,my=shkY+Math.sin(ang)*sr*.5,pa3=ang+Math.PI/2;c.beginPath();c.moveTo(mx+Math.cos(pa3)*sr*.18,my+Math.sin(pa3)*sr*.18);c.lineTo(mx-Math.cos(pa3)*sr*.18,my-Math.sin(pa3)*sr*.18);c.stroke();}
      } else {
        c.beginPath(); c.arc(icx,shkY-sr*.28,sr*.28,0,6.28); c.stroke();
        c.beginPath(); c.arc(icx,shkY+sr*.35,sr*.45,Math.PI*.15,Math.PI*.85); c.stroke();
      }
      c.lineCap='butt'; c.lineJoin='miter';
      c.fillStyle=item.col; c.font=fb(Math.round(h*.015)); c.textAlign='center';
      c.fillText(item.label,icx,shkY+ir+h*.022);
      c.restore();
    });
    c.textAlign='left';

    // scene label
    var scene=SCENES[s];
    c.fillStyle=scene.col; c.font=fb(Math.round(h*.016)); c.textAlign='right'; c.globalAlpha=.55;
    c.fillText(scene.label,rx+maxCw,shkY+Math.min(h*.038,24)+h*.052);
    c.globalAlpha=1; c.textAlign='left';

    // RIGHT: cards
    var cardH=h*.075, cardGap=h*.01;
    var cardsTop=shkY+Math.min(h*.030,19)+h*.055;
    c.fillStyle='rgba(244,241,235,.45)'; c.font=fb(Math.round(h*.016));
    c.fillText(s<2?'Neue Auftr\u00e4ge':'Bewerbungen',rx,cardsTop);
    c.strokeStyle=scene.col+'30'; c.lineWidth=1;
    c.beginPath(); c.moveTo(rx,cardsTop+h*.016); c.lineTo(rx+maxCw,cardsTop+h*.016); c.stroke();
    cardsTop+=h*.038;
    scene.cards.forEach(function(card,i){
      drawCard(rx,cardsTop+i*(cardH+cardGap),maxCw,cardH,card,st,card.delay,a);
    });

    // dots
    var dotY=h*.96, dotGap=14;
    for(var di=0;di<NS;di++){
      c.fillStyle=di===s?scene.col:'rgba(34,168,212,.18)';
      c.beginPath(); c.arc(lx+lw*.5+(di-1.5)*dotGap,dotY,di===s?4:2.8,0,6.28); c.fill();
    }

    // 100+ badge
    // 100+ badge – centered under animation area
    var bH=h*.048, bW=Math.min(lw*.7,260), bX=lx+lw*.5-bW/2, bY=h*.92;