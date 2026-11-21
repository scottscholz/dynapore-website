/* DynaPore site script: menus, floating CTA, videos, reveal, forms. No tracking, no cookies. */
(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* mobile nav */
  var burger = document.querySelector('.burger'), nav = document.querySelector('.nav');
  if (burger && nav) burger.addEventListener('click', function(){
    var open = nav.classList.toggle('open'); burger.setAttribute('aria-expanded', open);
  });
  document.querySelectorAll('.has-menu > button').forEach(function(b){
    b.addEventListener('click', function(e){
      var li = b.parentNode, open = !li.classList.contains('open');
      document.querySelectorAll('.has-menu.open').forEach(function(x){ x.classList.remove('open'); });
      if (open) li.classList.add('open');
      b.setAttribute('aria-expanded', open); e.stopPropagation();
    });
  });
  document.addEventListener('click', function(){ document.querySelectorAll('.has-menu.open').forEach(function(x){ x.classList.remove('open'); }); });

  /* floating CTA: appears once the visitor scrolls past the hero (adapted from the Wix button) */
  var cta = document.querySelector('.dpb'), trigger = document.querySelector('[data-cta-after]');
  if (cta && trigger && 'IntersectionObserver' in window) {
    new IntersectionObserver(function(en){ en.forEach(function(x){
      var past = !x.isIntersecting && x.boundingClientRect.top < 0;
      cta.classList.toggle('show', past);
    }); }, {threshold: 0}).observe(trigger);
  }

  /* videos: muted loops play only while visible; swap to mobile source on small screens */
  var small = window.matchMedia && window.matchMedia('(max-width:620px)').matches;
  document.querySelectorAll('video[data-src]').forEach(function(v){
    var src = (small && v.dataset.srcMobile) ? v.dataset.srcMobile : v.dataset.src;
    var loaded = false, held = reduce;
    function load(){ if (!loaded) { v.src = src; loaded = true; } }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function(en){ en.forEach(function(x){
        if (x.isIntersecting) { load(); if (!held) { var p = v.play(); if (p && p.catch) p.catch(function(){}); } }
        else if (!v.paused) v.pause();
      }); }, {rootMargin: '200px 0px', threshold: 0.25}).observe(v);
    } else { load(); }
    var btn = v.parentNode.querySelector('.vctl');
    if (btn) {
      var icon = function(){ btn.innerHTML = v.paused
        ? '<svg viewBox="0 0 16 16"><path fill="currentColor" d="M5 3.2v9.6L12.6 8z"/></svg>'
        : '<svg viewBox="0 0 16 16"><path d="M5.5 3.5v9M10.5 3.5v9" stroke="currentColor" stroke-width="2"/></svg>';
        btn.setAttribute('aria-label', v.paused ? 'Play video' : 'Pause video'); };
      v.addEventListener('play', icon); v.addEventListener('pause', icon); icon();
      btn.addEventListener('click', function(){ load(); if (v.paused) { held = false; v.play(); } else { held = true; v.pause(); } });
    }
  });

  /* reveal on scroll */
  var rs = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var ro = new IntersectionObserver(function(en){ en.forEach(function(x){ if (x.isIntersecting) { x.target.classList.add('in'); ro.unobserve(x.target); } }); }, {threshold: .08});
    rs.forEach(function(r){ ro.observe(r); });
  } else rs.forEach(function(r){ r.classList.add('in'); });

  /* forms: until the HubSpot embed is connected, show a note instead of sending */
  document.querySelectorAll('form[data-placeholder-form]').forEach(function(f){
    f.addEventListener('submit', function(e){
      e.preventDefault();
      var m = f.querySelector('.form-msg') || f.parentNode.querySelector('.form-msg');
      if (m) { m.style.display = 'block'; }
    });
  });
})();
