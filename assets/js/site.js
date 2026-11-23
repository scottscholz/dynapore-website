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

  /* forms: sent straight to HubSpot (portal 148400725, EU data centre) */
  var HS_PORTAL = '148400725';
  var HS_FORMS = {
    trial: 'e475f4ae-1c12-41ab-b0c8-3f39c85b61b8',   /* Website: Trial sample request */
    contact: '2ef76fdf-b2ef-4745-afe6-9fef89781d79', /* Website: Contact */
    notify: 'eef0d7f1-1594-471b-b390-1f3604897573'   /* Website: Notify me at launch */
  };
  var DONE = {
    trial: 'Thank you. We have your request and will be in touch within a few working days.',
    contact: 'Thank you. We will get back to you soon.',
    notify: 'Thanks, we will let you know when MemChip launches.'
  };
  function val(f, n){ var e = f.elements[n]; return e ? String(e.value || '').trim() : ''; }
  document.querySelectorAll('form[data-hs-form]').forEach(function(f){
    var kind = f.getAttribute('data-hs-form');
    var msg = f.querySelector('.form-msg') || (f.nextElementSibling && f.nextElementSibling.classList.contains('form-msg') ? f.nextElementSibling : null);
    function show(t, ok){ if (!msg) return; msg.textContent = t; msg.style.display = 'block'; msg.style.background = ok ? '' : '#fbebeb'; }
    f.addEventListener('submit', function(e){
      e.preventDefault();
      var btn = f.querySelector('button[type=submit]'); if (btn) btn.disabled = true;
      var fields = [{name: 'email', value: val(f, 'email')}];
      if (val(f, 'firstname')) fields.push({name: 'firstname', value: val(f, 'firstname')});
      if (val(f, 'lastname')) fields.push({name: 'lastname', value: val(f, 'lastname')});
      var lines = [];
      if (kind === 'trial') {
        lines.push('TRIAL SAMPLE REQUEST', 'Institution: ' + val(f, 'institution'), 'Application: ' + val(f, 'application'), 'Potentiostat: ' + (val(f, 'potentiostat') || 'not given'));
      } else if (kind === 'contact') {
        lines.push('WEBSITE CONTACT', 'Topic: ' + val(f, 'topic'));
      }
      if (val(f, 'details')) lines.push('', val(f, 'details'));
      if (lines.length) fields.push({name: 'message', value: lines.join('\n')});
      var body = JSON.stringify({fields: fields, context: {pageUri: location.href, pageName: document.title}});
      var url = 'https://api-eu1.hsforms.com/submissions/v3/integration/submit/' + HS_PORTAL + '/' + HS_FORMS[kind];
      fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: body})
        .then(function(r){ if (!r.ok) throw new Error(r.status); f.reset(); show(DONE[kind], true); })
        .catch(function(){ show('Sorry, that did not go through. Please email info@dynaporetech.com instead.', false); })
        .then(function(){ if (btn) btn.disabled = false; });
    });
  });
})();
