/* Emmaus Import Export PLC - site behaviour fixes
   - preloader: hide on DOMContentLoaded (don't wait for every image)
   - stats counters: count once when visible, no plugin
   - anchors: land below the fixed header, also after the preloader
   - forms: send every field through the mailto action + confirmation
*/
(function () {
  'use strict';

  /* ---------- preloader ---------- */
  function hidePreloader() {
    var wrap = document.getElementById('preloader');
    if (!wrap) return;
    var ctn = document.getElementById('ctn-preloader');
    if (ctn) ctn.classList.add('loaded');
    setTimeout(function () {
      if (wrap.parentNode) wrap.parentNode.removeChild(wrap);
      jumpToHash();
    }, 700);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', hidePreloader);
  } else {
    hidePreloader();
  }

  /* ---------- off-canvas menu: add IQ Fortune + aria state ---------- */
  var offUl = document.querySelector('.ca-offcanvas-menu-3 nav > ul');
  if (offUl && !offUl.querySelector('a[href*="iqfortune"]')) {
    var li = document.createElement('li');
    li.innerHTML = '<a href="https://iqfortune.com" target="_blank" rel="noopener">IQ Fortune</a>';
    offUl.appendChild(li);
  }
  var toggle = document.querySelector('.ca-offcanvas-toogle');
  var panel = document.querySelector('.ca-offcanvas');
  if (toggle && panel) {
    new MutationObserver(function () {
      toggle.setAttribute('aria-expanded', panel.classList.contains('ca-offcanvas-open') ? 'true' : 'false');
    }).observe(panel, { attributes: true, attributeFilter: ['class'] });
  }

  /* ---------- anchor targets ---------- */
  function jumpToHash() {
    if (!location.hash || location.hash.length < 2) return;
    var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) {
      target.scrollIntoView({ block: 'start' });
    }
  }
  window.addEventListener('hashchange', jumpToHash);

  /* ---------- stats counters ---------- */
  function animateCounter(el) {
    var target = parseInt(el.getAttribute('data-count'), 10);
    if (isNaN(target)) return;
    var start = null, duration = 1200;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }
    requestAnimationFrame(step);
  }
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!('IntersectionObserver' in window) || reduce) {
      counters.forEach(function (el) { el.textContent = el.getAttribute('data-count'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.4 });
      counters.forEach(function (el) { el.textContent = '0'; io.observe(el); });
    }
  }

  /* ---------- forms ---------- */
  var forms = document.querySelectorAll('form[data-emmaus-form]');
  forms.forEach(function (form) {
    form.setAttribute('novalidate', 'novalidate');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = form.querySelector('.form-status');
      if (!form.checkValidity()) {
        form.classList.add('was-validated');
        var first = form.querySelector(':invalid');
        if (first) first.focus();
        if (status) {
          status.textContent = 'Please fill in the highlighted fields.';
          status.className = 'form-status is-error';
        }
        return;
      }
      var mailto = form.getAttribute('action') || '';
      var lines = [];
      var fields = form.querySelectorAll('input, select, textarea');
      fields.forEach(function (f) {
        if (!f.name || f.type === 'submit') return;
        var label = form.querySelector('label[for="' + f.id + '"]');
        var name = label ? label.textContent.trim() : f.name;
        var value = f.value;
        if (f.tagName === 'SELECT') {
          var opt = f.options[f.selectedIndex];
          value = opt ? opt.textContent.trim() : '';
        }
        lines.push(name + ': ' + value);
      });
      var subject = form.getAttribute('data-subject') || 'Website enquiry';
      var href = mailto + (mailto.indexOf('?') === -1 ? '?' : '&') +
        'subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(lines.join('\n'));
      window.location.href = href;
      if (status) {
        status.textContent = 'Thanks — your email app should open with the details filled in. If it does not, write to ' + mailto.replace('mailto:', '') + '.';
        status.className = 'form-status is-success';
      }
    });
  });
})();
