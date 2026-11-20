// Shared behaviour for every page. Each block checks that its elements exist.
(() => {
  const $ = s => document.querySelector(s), $$ = s => document.querySelectorAll(s);

  // ---- icon sprite (one copy for all pages; works from file:// too)
  const ic = {
    arr: '<path d="M7 17 17 7M8 7h9v9"/>',
    r: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    l: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    ph: '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    pin: '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    tg: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3" fill="currentColor"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    ok: '<path d="m5 12 4.5 4.5L19 7"/>',
    wa: '<path d="M4 20l1.3-4A8 8 0 1 1 8 19z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-1.8-1.8l.8-1-1-2z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    design: '<path d="M12 3v3M6 21l6-15 6 15M8.4 15h7.2"/><circle cx="12" cy="6" r="1.6"/>',
    arch: '<path d="M3 21h18M5 21V10l7-6 7 6v11M9 21v-6h6v6"/>',
    stamp: '<path d="M9 4h6v5l-1 3h5v4H5v-4h5L9 9zM5 20h14"/>',
    rupee: '<path d="M7 4h11M7 8.5h11M7 4h3a4.5 4.5 0 0 1 0 9H7l8 7"/>',
    crane: '<path d="M5 21V4M5 4h15l-3 3M5 8h9M14 8v4M12 12h4v2h-4zM3 21h6"/>',
    wall: '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="M3 10h18M3 15h18M9 5v5M15 5v5M6 10v5M12 10v5M18 10v5M9 15v4M15 15v4"/>',
    cap: '<path d="M2 9.5 12 5l10 4.5L12 14zM6 11.5v4.5c0 1.4 2.7 3 6 3s6-1.6 6-3v-4.5"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    video: '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="m16 10 5-3v10l-5-3"/>',
    spark: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
    key: '<circle cx="8" cy="15" r="4.5"/><path d="M11.2 11.8 20 3M16 7l3 3M13.5 9.5l2.5 2.5"/>',
    seal: '<circle cx="12" cy="10" r="6"/><path d="m9.5 10 1.8 1.8L14.5 8.5M8.5 15 7 21l5-2.5 5 2.5-1.5-6"/>'
  };
  const sprite = document.createElement('div');
  sprite.innerHTML = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' +
    Object.entries(ic).map(([k, v]) => `<symbol id="i-${k}" viewBox="0 0 24 24">${v}</symbol>`).join('') +
    '<symbol id="logo" viewBox="0 0 34 34"><rect width="34" height="34" rx="10" style="fill:var(--ink)"/><path d="M8 26V15l9-7 9 7v11M12.5 26v-7.5L17 23l4.5-4.5V26" fill="none" style="stroke:var(--bg)" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/></symbol></svg>';
  document.body.prepend(sprite.firstChild);

  const yr = $('#yr'); if (yr) yr.textContent = new Date().getFullYear();

  // ---- theme: system by default, the toggle remembers a choice
  const root = document.documentElement, dark = matchMedia('(prefers-color-scheme: dark)');
  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : dark.matches;
  const announce = () => dispatchEvent(new CustomEvent('themechange', { detail: isDark() }));
  $$('.theme').forEach(b => {
    const label = () => b.setAttribute('aria-label', isDark() ? 'Switch to light theme' : 'Switch to dark theme');
    label();
    b.addEventListener('click', () => {
      const next = isDark() ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch {}
      $$('.theme').forEach(x => x.setAttribute('aria-label', next === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'));
      announce();
    });
  });
  dark.addEventListener('change', () => { if (!root.dataset.theme) announce(); });

  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- stagger: children of [data-stagger] reveal one after another
  $$('[data-stagger]').forEach(box => [...box.children].forEach((c, i) => {
    if (!c.hasAttribute('data-r')) c.setAttribute('data-r', box.dataset.stagger || '');
    c.style.setProperty('--d', (i * 0.08).toFixed(2) + 's');
  }));

  // ---- any other copy, list item, button or card drifts up as it enters; siblings follow each other.
  // Skips blocks that already animate themselves (the hero, the scroll story, scrubbed and staggered blocks).
  if (!still) $$('main p, main .eyebrow, main li, main .btn, main .link, main h3, main h4, main dl, main figure, main form, main .ctas, .ftr .fg > div').forEach(el => {
    if (el.closest('[data-r], [data-stagger], [data-scrub], .hero, .story-grid, .drawer') || el.parentElement.closest('[data-r]')) return;
    const prev = [...el.parentElement.children].slice(0, [...el.parentElement.children].indexOf(el)).filter(s => s.hasAttribute('data-r')).length;
    el.setAttribute('data-r', '');
    el.style.setProperty('--d', Math.min(prev * .08, .4).toFixed(2) + 's');
  });

  // ---- headings rise word by word
  if (!still) $$('h1, main h2').forEach(h => {
    let wi = 0;
    const wrap = node => [...node.childNodes].forEach(n => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        n.nodeValue.split(/(\s+)/).forEach(part => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.append(' '); return; }
          const w = document.createElement('span'); w.className = 'w';
          const inner = document.createElement('span'); inner.textContent = part;
          w.style.setProperty('--wi', wi++); w.append(inner); frag.append(w);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1 && n.tagName !== 'BR') wrap(n);
    });
    wrap(h);
    h.classList.add('words');
  });

  // ---- reveal on scroll (also starts word animations and fills timeline dots)
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -8% 0px' });
  $$('[data-r], .words, .timeline li').forEach(el => io.observe(el));

  // ---- home hero: copy, stat cards and service cards arrive one after another while the 3D house builds.
  // Web Animations sit on top of the CSS float / scroll-out animations and hand back to them when done.
  if (!still) $$('.hero .headline .eyebrow, .hero .intro > *, .hero .stat, .hero .trust, .hero .arrows, .hero .svc').forEach((el, i) => el.animate(
    [{ opacity: 0, translate: '0 32px', scale: .96 }, { opacity: 1, translate: '0 0', scale: 1 }],
    { duration: 1100, delay: 200 + i * 110, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' }));

  // ---- numbers count up when they come into view: data-count="30" data-pad="2"
  const counter = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    counter.unobserve(e.target);
    const el = e.target, end = +el.dataset.count, pad = +(el.dataset.pad || 0);
    const tn = [...el.childNodes].find(n => n.nodeType === 3);
    if (!tn) return;
    const suffix = tn.nodeValue.replace(/^[\d,]+/, '');
    const fmt = v => String(Math.round(v)).padStart(pad, '0') + suffix;
    if (still) { tn.nodeValue = fmt(end); return; }
    const t0 = performance.now(), dur = 1600;
    const step = now => {
      const t = Math.min(1, (now - t0) / dur);
      tn.nodeValue = fmt(end * (1 - Math.pow(1 - t, 3)));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }), { threshold: .6 });
  $$('[data-count]').forEach(el => counter.observe(el));

  // ---- bottom dock: the header scrolls away with the hero, then this dock rises from the bottom.
  // Warm light sweeps across it as you read down the page (--p); the current page's tab is highlighted.
  const navLinks = [...$$('.pill-nav a')].filter(a => a.getAttribute('href') !== 'index.html');
  const dock = document.createElement('nav');
  dock.className = 'dock'; dock.setAttribute('aria-label', 'Quick links'); dock.inert = true;
  dock.innerHTML = '<a class="dock-logo" href="index.html" aria-label="Manidhay Business Services, home"><svg aria-hidden="true"><use href="#logo"/></svg></a>' +
    navLinks.map(a => `<a class="tab" href="${a.getAttribute('href')}"${a.hasAttribute('aria-current') ? ' aria-current="page"' : ''}>${a.textContent}</a>`).join('') +
    '<button class="dmenu" type="button" aria-controls="drawer" aria-expanded="false">Menu</button>' +
    '<a class="call" href="tel:+919986470846" aria-label="Call +91 99864 70846"><svg class="i" aria-hidden="true"><use href="#i-ph"/></svg></a>' +
    '<a class="btn btn-or" href="contact.html">Quote</a>';
  document.body.append(dock);
  const heroEl = $('.hero-panel, .page-hero .panel');
  let dockOn = false;

  // ---- scroll progress engine: scrub(el, fn, 'pin'|'pass') calls fn(0..1) as el moves through the viewport
  const scrubs = [];
  let queued = false;
  function measure() {
    queued = false;
    const vh = innerHeight;
    for (const s of scrubs) {
      const r = s.el.getBoundingClientRect();
      let p = s.mode === 'pin' ? -r.top / Math.max(1, r.height - vh) : (vh * .85 - r.top) / (r.height + vh * .25);
      p = Math.min(1, Math.max(0, p));
      if (p !== s.p) { s.p = p; s.fn(p); }
    }
    const p = Math.min(1, scrollY / Math.max(1, document.documentElement.scrollHeight - vh));
    dock.style.setProperty('--p', p.toFixed(3));
    const show = heroEl ? heroEl.getBoundingClientRect().bottom < vh * .35 : scrollY > vh * .6;
    if (show !== dockOn) { dockOn = show; dock.classList.toggle('on', show); dock.inert = !show; }
  }
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(measure); } };
  window.scrub = (el, fn, mode = 'pass') => { scrubs.push({ el, fn, mode, p: -1 }); queue(); };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  queue();

  // ---- one section per screen: CSS snaps the page (styles.css §16). A wheel or trackpad gesture moves
  // exactly one section; inside a section taller than the screen it scrolls normally until that section's edge.
  const snaps = [...$$('main > section'), $('.ftr')].filter(Boolean);
  let wheelLock = 0;
  if (snaps.length > 1) addEventListener('wheel', e => {
    if (e.ctrlKey || Math.abs(e.deltaY) < 2 || Math.abs(e.deltaX) > Math.abs(e.deltaY) || document.body.style.overflow === 'hidden') return;
    const now = performance.now(), vh = innerHeight, y = scrollY, dir = Math.sign(e.deltaY);
    const max = document.documentElement.scrollHeight - vh;
    const tops = snaps.map(el => el.getBoundingClientRect().top + y);
    let i = 0;
    tops.forEach((t, k) => { if (t <= y + 2) i = k; });
    if (y >= max - 2) i = snaps.length - 1;                     // the footer snaps to the bottom, so it may start below scrollY
    const end = tops[i] + snaps[i].offsetHeight;
    if (dir > 0 ? y + vh < end - 2 : y > tops[i] + 2) return;   // still inside a tall section: native scroll
    e.preventDefault();
    if (now < wheelLock) { wheelLock = Math.max(wheelLock, now + 200); return; }   // ignore the rest of this gesture
    const j = Math.min(snaps.length - 1, Math.max(0, i + dir));
    if (j === i) return;
    const tall = snaps[j].offsetHeight > vh + 2;
    const top = dir < 0 && tall ? tops[j] + snaps[j].offsetHeight - vh : tops[j];
    wheelLock = now + 750;
    scrollTo({ top: Math.min(max, Math.max(0, top)), behavior: still ? 'auto' : 'smooth' });
  }, { passive: false });

  // ---- section gradients: the section crossing the middle of the screen sets the page tone (styles.css §17).
  // Sections take tones 1 to 5 in turn; a section can pick its own with data-tone="3".
  const toneIO = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) root.dataset.tone = e.target.dataset.tone || (snaps.indexOf(e.target) % 5) + 1;
  }), { rootMargin: '-50% 0px -50% 0px' });
  snaps.forEach(el => toneIO.observe(el));

  // ---- [data-scrub]: children with data-at="0.3" get .on past that point; the box gets .done at data-scrub
  $$('[data-scrub]').forEach(box => {
    const items = [...box.querySelectorAll('[data-at]')], doneAt = +(box.dataset.scrub || 1);
    scrub(box, p => {
      box.style.setProperty('--p', p.toFixed(3));
      items.forEach(i => i.classList.toggle('on', still || p >= +i.dataset.at));
      box.classList.toggle('done', still || p >= doneAt);
    });
  });

  // ---- mobile menu
  const drawer = $('#drawer'), btn = $('#menuBtn');
  if (drawer && btn) {
    const dmenu = dock.querySelector('.dmenu');
    let opener = btn;
    const setMenu = open => {
      drawer.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open); dmenu.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
      if (open) $('#menuClose').focus(); else opener.focus({ preventScroll: true });
    };
    btn.onclick = () => { opener = btn; setMenu(true); };
    dmenu.onclick = () => { opener = dmenu; setMenu(true); };
    $('#menuClose').onclick = () => setMenu(false);
    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
    addEventListener('keydown', e => { if (e.key === 'Escape' && drawer.classList.contains('open')) setMenu(false); });
  }

  // ---- home: service slider arrows
  const track = $('#track');
  if (track) {
    const step = () => track.firstElementChild.offsetWidth + 12;
    $('#prev').onclick = () => track.scrollBy({ left: -step(), behavior: 'smooth' });
    $('#next').onclick = () => track.scrollBy({ left: step(), behavior: 'smooth' });
  }

  // ---- services: highlight the index entry for the row in view
  const toc = $$('.toc a');
  if (toc.length) {
    const spy = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) toc.forEach(a => a.classList.toggle('on', a.hash === '#' + e.target.id));
    }), { rootMargin: '-40% 0px -55% 0px' });
    $$('.svc-row').forEach(r => spy.observe(r));
  }

  // ---- projects: filter by type
  const fbtns = $$('.filter button');
  fbtns.forEach(b => b.addEventListener('click', () => {
    fbtns.forEach(x => x.setAttribute('aria-pressed', x === b));
    const f = b.dataset.f;
    let i = 0;
    $$('.proj').forEach(p => {
      const hide = f !== 'all' && !p.dataset.type.split(' ').includes(f);
      p.classList.toggle('out', hide);
      p.classList.remove('pop');
      if (hide || still) return;
      void p.offsetWidth; // restart the animation
      p.style.setProperty('--d', (i++ * 0.06).toFixed(2) + 's');
      p.classList.add('in', 'pop');
    });
  }));
  const pre = new URLSearchParams(location.search).get('type');
  if (pre) [...fbtns].find(b => b.dataset.f === pre)?.click();

  // ---- contact: pre-select the enquiry from ?service=…, confirm on submit
  const sel = $('#f-svc');
  if (sel) {
    const want = new URLSearchParams(location.search).get('service');
    if (want) {
      const opt = [...sel.options].find(o => o.value === want);
      if (opt) sel.value = want;
    }
  }
  const form = $('#form');
  // ponytail: no backend yet; the form only confirms on screen. Wire to email/CRM/WhatsApp before launch.
  if (form) form.addEventListener('submit', e => {
    e.preventDefault();
    $('#ok').hidden = false;
    form.querySelector('button[type=submit]').disabled = true;
  });
})();
