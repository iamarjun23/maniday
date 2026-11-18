const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Mobile menu
const toggle = document.querySelector('.nav-toggle');
const menu = document.getElementById('nav-menu');
toggle.addEventListener('click', () => {
  const open = menu.classList.toggle('open');
  toggle.setAttribute('aria-expanded', open);
});
menu.addEventListener('click', e => {
  if (e.target.closest('a')) { menu.classList.remove('open'); toggle.setAttribute('aria-expanded', false); }
});

// Header shrinks once the page scrolls
const header = document.querySelector('.site-header');
const onScroll = () => header.classList.toggle('scrolled', scrollY > 40);
addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Project filter
const chips = document.querySelectorAll('.chip');
chips.forEach(chip => chip.addEventListener('click', () => {
  const cat = chip.dataset.filter;
  chips.forEach(c => c.setAttribute('aria-pressed', c === chip));
  document.querySelectorAll('.project').forEach(p => {
    p.hidden = cat !== 'all' && p.dataset.category !== cat && !p.classList.contains('project-more');
  });
}));

// Count-up numbers
const countUp = el => {
  const end = +el.dataset.count;
  if (reduceMotion || end < 2) return;
  const start = performance.now(), dur = 1600;
  const step = now => {
    const t = Math.min(1, (now - start) / dur);
    el.textContent = Math.round(end * (1 - Math.pow(1 - t, 3)));
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
};

// Reveal on scroll (also starts counters inside the revealed element)
const revealer = new IntersectionObserver(entries => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    const el = e.target;
    el.classList.add('in');
    el.querySelectorAll('[data-count]').forEach(countUp);
    // after the entrance, drop the stagger delay so hover effects respond instantly
    setTimeout(() => { el.style.transitionDelay = '0s'; }, 1400);
    revealer.unobserve(el);
  }
}, { rootMargin: '0px 0px -10% 0px' });
document.querySelectorAll('[data-reveal]').forEach(el => revealer.observe(el));

// Process stages: tabs, arrow-key navigation, and autoplay while on screen
// (the selected tab's progress bar is a CSS animation; when it ends we advance)
const stages = document.querySelector('[data-stages]');
if (stages) {
  const tabs = [...stages.querySelectorAll('[role="tab"]')];
  const select = (tab, focus) => {
    for (const t of tabs) {
      const on = t === tab;
      t.setAttribute('aria-selected', on);
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    }
    if (focus) tab.focus();
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', e => {
      const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (d) select(tabs[(i + d + tabs.length) % tabs.length], true);
    });
    tab.querySelector('.stage-bar i').addEventListener('animationend', () => select(tabs[(i + 1) % tabs.length]));
  });
  new IntersectionObserver(([e]) => stages.classList.toggle('playing', e.isIntersecting), { threshold: .4 }).observe(stages);
}

// 3D tilt on cards, following the mouse (skipped for touch and reduced motion)
if (matchMedia('(hover: hover) and (prefers-reduced-motion: no-preference)').matches) {
  document.querySelectorAll('.tilt').forEach(el => {
    el.addEventListener('pointermove', e => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5;
      const y = (e.clientY - r.top) / r.height - .5;
      el.style.transform = `perspective(900px) rotateX(${-y * 6}deg) rotateY(${x * 6}deg) translateY(-4px)`;
    });
    el.addEventListener('pointerleave', () => { el.style.transform = ''; });
  });
}

document.getElementById('year').textContent = new Date().getFullYear();
