// Tiny slider for Elementor carousel-like markup, no dependencies.
(function () {
  // Mobile nav toggle for custom header
  function mountNavToggle() {
    const header = document.querySelector('.site-header');
    const btn = header && header.querySelector('.nav-toggle');
    if (!header || !btn) return;
    btn.addEventListener('click', () => {
      const expanded = header.getAttribute('aria-expanded') === 'true';
      header.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
    });
  }

  function mountCarousel(root) {
    const wrapper = root.querySelector('.swiper-wrapper');
    if (!wrapper) return;
    const slides = Array.from(wrapper.querySelectorAll('.swiper-slide'));
    if (!slides.length) return;

    let idx = 0;
    function show(i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach((el, k) => el.classList.toggle('is-active', k === idx));
    }
    show(0);

    const prev = root.querySelector('.elementor-swiper-button-prev');
    const next = root.querySelector('.elementor-swiper-button-next');
    if (prev) prev.addEventListener('click', () => show(idx - 1));
    if (next) next.addEventListener('click', () => show(idx + 1));

    // autoplay
    let timer = setInterval(() => show(idx + 1), 5000);
    root.addEventListener('mouseenter', () => clearInterval(timer));
    root.addEventListener('mouseleave', () => (timer = setInterval(() => show(idx + 1), 5000)));
  }

  function init() {
    mountNavToggle();
    document.querySelectorAll('.elementor-widget-media-carousel').forEach(mountCarousel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
