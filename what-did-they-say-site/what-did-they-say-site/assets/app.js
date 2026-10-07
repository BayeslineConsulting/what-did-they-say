/* What Did They Say? shared script. Page data arrives in window.SITE (always) and
   window.PAGE (page-specific). Everything is guarded so each page runs only its parts. */
(function () {
  'use strict';
  var S = window.SITE || {}, P = window.PAGE || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  /* ---------- storage (plan) ---------- */
  var KEY = 'wdts-plan-' + (S.conf || '');
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '') || { items: {}, notes: {} }; } catch (e) { return { items: {}, notes: {} }; } }
  function save(st) { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
  var state = load();

  /* ---------- toast ---------- */
  var toastEl;
  function toast(html) {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'toast'; toastEl.setAttribute('role', 'status'); document.body.appendChild(toastEl); }
    toastEl.innerHTML = html; toastEl.classList.add('on');
    clearTimeout(toastEl._t); toastEl._t = setTimeout(function () { toastEl.classList.remove('on'); }, 3200);
  }

  /* ---------- "Add to my plan" buttons anywhere ---------- */
  function syncAddButtons() {
    $$('[data-add]').forEach(function (b) {
      var on = !!state.items[b.getAttribute('data-add')];
      if (b.classList.contains('xbtn')) return;
      b.classList.toggle('added', on); b.setAttribute('aria-pressed', on);
      b.textContent = on ? 'In my plan \u2713' : 'Add to my plan';
    });
    var n = Object.keys(state.items).length;
    $$('[data-plancount]').forEach(function (el) { el.textContent = n ? n + ' in your plan' : 'Your plan'; });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-add]');
    if (!b) return;
    var id = b.getAttribute('data-add');
    if (state.items[id]) { delete state.items[id]; toast('Removed from your plan.'); }
    else { state.items[id] = { when: '', will: '', freq: 'Weekly', start: 0, checks: {} }; toast('Added to your plan. <a href="' + S.base + 'plan/">Open my plan</a>'); }
    save(state); syncAddButtons(); if (window.__renderPlan) window.__renderPlan();
  });
  syncAddButtons();

  /* ---------- video facades ---------- */
  $$('[data-yt]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-yt');
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0';
      f.title = btn.getAttribute('aria-label') || 'Talk video';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      f.allowFullscreen = true; f.loading = 'lazy';
      btn.parentNode.replaceChild(f, btn);
    });
  });

  /* ---------- sign-up ---------- */
  var form = $('#sform');
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault();
    var em = $('#email').value.trim(), fn = $('#fname').value.trim(), msg = $('#smsg');
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) { msg.textContent = 'Please enter a valid email address.'; $('#email').focus(); return; }
    if (!S.signup_endpoint) { msg.textContent = 'Preview: sign-ups are not connected here. Your email was not sent anywhere.'; return; }
    msg.textContent = 'Signing you up\u2026';
    var h = { 'Content-Type': 'application/json', 'Prefer': 'return=minimal' }; for (var k in (S.signup_headers || {})) h[k] = S.signup_headers[k];
    fetch(S.signup_endpoint, { method: 'POST', headers: h, body: JSON.stringify({ email: em.toLowerCase(), first_name: fn || null, source: S.conf }) })
      .then(function (r) { var ok = r.ok || r.status === 409; msg.textContent = ok ? 'You\u2019re on the list. See you after the next conference.' : 'That didn\u2019t go through. Please try again in a moment.'; if (ok) form.reset(); })
      .catch(function () { msg.textContent = 'That didn\u2019t go through. Please check your connection and try again.'; });
  });

  /* ---------- guess-the-number cards ---------- */
  $$('.gcard').forEach(function (c) {
    c.addEventListener('click', function () {
      var on = c.getAttribute('aria-pressed') !== 'true'; c.setAttribute('aria-pressed', on);
      var n = $('.num', c); n.textContent = on ? c.getAttribute('data-ans') : '? ? ?'; n.classList.toggle('hid', !on);
      $('.tap', c).textContent = on ? 'Tap to hide' : 'Tap to reveal'; var d = $('.det', c); if (d) d.hidden = !on;
    });
  });

  /* ---------- quiz ---------- */
  var qz = $('#quiz');
  if (qz && P.quiz && P.quiz.length) {
    var Q = P.quiz, qi = 0, score = 0, answered = false, art = qz.getAttribute('data-art') ? $(qz.getAttribute('data-art')).innerHTML : '';
    var render = function () {
      if (qi >= Q.length) {
        qz.innerHTML = '<div><h3>How well do you remember?</h3><p class="qq" style="margin-top:14px">You got ' + score + ' of ' + Q.length + '.</p><p class="qwhy">' + (score === Q.length ? 'Perfect. The neighbor would be impressed.' : 'Every answer is on this site. Try again any time.') + '</p><button class="btn qnext" id="qagain">Take it again</button></div>' + art;
        $('#qagain').onclick = function () { qi = 0; score = 0; render(); }; return;
      }
      var q = Q[qi]; answered = false;
      qz.innerHTML = '<div><h3>How well do you remember?</h3><div class="qmeta">Question ' + (qi + 1) + ' of ' + Q.length + '</div><p class="qq">' + esc(q.q) + '</p><div class="qopts">' +
        q.options.map(function (o, j) { return '<button class="qopt" data-j="' + j + '">' + esc(o) + '</button>'; }).join('') +
        '</div><p class="qwhy" id="qwhy"></p><button class="btn qnext" id="qnext" hidden>' + (qi + 1 < Q.length ? 'Next question' : 'See my score') + '</button></div>' + art;
      $$('.qopt', qz).forEach(function (b) {
        b.onclick = function () {
          if (answered) return; answered = true; var j = +b.getAttribute('data-j'); if (j === q.a) score++;
          $$('.qopt', qz).forEach(function (x) { var k = +x.getAttribute('data-j'); if (k === q.a) x.classList.add('right'); else if (k === j) x.classList.add('wrong'); });
          $('#qwhy').textContent = (j === q.a ? 'Right. ' : 'Not quite. ') + q.why; $('#qnext').hidden = false; $('#qnext').focus();
        };
      });
      $('#qnext').onclick = function () { qi++; render(); };
    };
    render();
  }

  /* ---------- word cloud ---------- */
  var cl = $('#cloud');
  if (cl && P.words) {
    var W = 900, H = 470, cx = W / 2, cy = H / 2, rows = P.words, placed = [];
    var mx = Math.max.apply(null, rows.map(function (r) { return r[1]; })), mn = Math.min.apply(null, rows.map(function (r) { return r[1]; }));
    var size = function (n) { return 13 + 52 * Math.sqrt((n - mn) / (mx - mn)); };
    var hit = function (b) { return placed.some(function (p) { return b.x < p.x + p.w && b.x + b.w > p.x && b.y < p.y + p.h && b.y + b.h > p.y; }); };
    rows.forEach(function (r, i) {
      var fs = size(r[1]), bw = r[0].length * fs * .62 + fs * .5, bh = fs * 1.04;
      for (var t = 0; t < 1400; t += .1) { var rr = 2.8 * t, x = cx + rr * Math.cos(t) * 1.75 - bw / 2, y = cy + rr * Math.sin(t) - bh / 2; if (x < 4 || x + bw > W - 4 || y < 4 || y + bh > H - 4) continue; var b = { x: x, y: y, w: bw, h: bh }; if (!hit(b)) { b.word = r[0]; b.n = r[1]; b.fs = fs; b.i = i; placed.push(b); break; } }
    });
    var col = function (i) { return i < 5 ? 'var(--gold)' : i < 18 ? 'var(--head)' : 'var(--muted)'; };
    cl.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Word cloud of the 60 most-used content words">' + placed.map(function (p) {
      return '<text x="' + (p.x + p.w / 2) + '" y="' + (p.y + p.h * .8) + '" text-anchor="middle" font-family="Literata, Georgia, serif" font-size="' + p.fs + '" font-weight="' + (p.i < 5 ? 700 : 500) + '" fill="' + col(p.i) + '"><title>' + esc(p.word) + ': ' + p.n + ' uses</title>' + esc(p.word) + '</text>';
    }).join('') + '</svg>';
  }

  /* ---------- six-month plan ---------- */
  var app = $('#planapp');
  if (app && P.bundles) {
    var B = P.bundles, MONTHS = P.months, WEEKS = P.weeks, FREQ = ['Daily', 'A few times a week', 'Weekly', 'Sundays', 'Monthly'];
    var mine = $('#mine'), pick = $('#pick'), sum = $('#plansum');
    var weeksFor = function (it) { return WEEKS.filter(function (w) { return w.m >= (+it.start || 0); }); };
    var pct = function (it) { var ws = weeksFor(it), d = ws.filter(function (w) { return it.checks[w.i]; }).length; return ws.length ? Math.round(100 * d / ws.length) : 0; };
    function renderPlan() {
      var ids = Object.keys(state.items).filter(function (id) { return B[id]; });
      var total = 0, done = 0;
      ids.forEach(function (id) { var it = state.items[id]; var ws = weeksFor(it); total += ws.length; done += ws.filter(function (w) { return it.checks[w.i]; }).length; });
      sum.innerHTML = ids.length
        ? '<b>' + ids.length + '</b> invitation' + (ids.length > 1 ? 's' : '') + ' in your plan &middot; <b>' + (total ? Math.round(100 * done / total) : 0) + '%</b> of weekly check-ins done' + (ids.length > 3 ? '<span class="hint">Tip: most people do best focusing on one to three at a time. Stagger the rest with \u201CStarts in.\u201D</span>' : '')
        : 'Your plan is empty. Choose one to three invitations below to begin.';
      $('#planacts').hidden = !ids.length;
      mine.innerHTML = ids.map(function (id) {
        var b = B[id], it = state.items[id];
        return '<article class="pitem" data-id="' + id + '"><div class="ph2"><div><span class="ptag">' + esc(b.group_label) + '</span><h3>' + esc(b.title) + '</h3><div class="by">Asked by ' + esc(b.speakers.join(', ')) + '</div></div><button class="xbtn" data-add="' + id + '" aria-label="Remove from plan">Remove</button></div>' +
          (b.ideas && b.ideas.length ? '<div class="ideas"><span>Ideas to make it specific:</span>' + b.ideas.map(function (x) { return '<button class="idea" type="button">' + esc(x) + '</button>'; }).join('') + '</div>' : '') +
          '<div class="pform"><label>When<input data-f="when" value="' + esc(it.when) + '" placeholder="e.g. after breakfast, on Sunday evening"></label><label>I will<input data-f="will" value="' + esc(it.will) + '" placeholder="e.g. read one chapter, pray for one person by name"></label>' +
          '<label>How often<select data-f="freq">' + FREQ.map(function (f) { return '<option' + (f === it.freq ? ' selected' : '') + '>' + f + '</option>'; }).join('') + '</select></label>' +
          '<label>Starts in<select data-f="start">' + MONTHS.map(function (m, i) { return '<option value="' + i + '"' + (+it.start === i ? ' selected' : '') + '>' + m + '</option>'; }).join('') + '</select></label></div>' +
          '<div class="wk"><div class="wkh"><span>Weekly check-in</span><span class="pc">' + pct(it) + '%</span></div><div class="weeks">' + WEEKS.map(function (w) {
            var off = w.m < (+it.start || 0);
            return '<button type="button" class="wbox' + (it.checks[w.i] ? ' on' : '') + '" data-w="' + w.i + '"' + (off ? ' disabled' : '') + ' title="Week of ' + w.label + '" aria-label="Week of ' + w.label + (it.checks[w.i] ? ', done' : '') + '"></button>';
          }).join('') + '</div><div class="wkl">' + MONTHS.map(function (m, mi) { var n = WEEKS.filter(function (w) { return w.m === mi; }).length; return n ? '<span style="grid-column:span ' + n + '">' + m.slice(0, 3) + '</span>' : ''; }).join('') + '</div></div></article>';
      }).join('');
      $('#notes').innerHTML = ids.length ? '<h2>Monthly reflection</h2><p class="note">At the end of each month, write what went well and what you\u2019ll adjust. It stays on this device.</p><div class="ngrid">' + MONTHS.map(function (m, i) { return '<label>' + m + '<textarea data-n="' + i + '" rows="3" placeholder="What went well? What will I adjust?">' + esc(state.notes[i] || '') + '</textarea></label>'; }).join('') + '</div>' : '';
      syncAddButtons();
    }
    window.__renderPlan = renderPlan;
    mine.addEventListener('input', function (e) {
      var card = e.target.closest('.pitem'), f = e.target.getAttribute('data-f'); if (!card || !f) return;
      state.items[card.getAttribute('data-id')][f] = e.target.value; save(state);
    });
    mine.addEventListener('change', function (e) { if (e.target.getAttribute('data-f') === 'start') renderPlan(); });
    mine.addEventListener('click', function (e) {
      var card = e.target.closest('.pitem'); if (!card) return; var it = state.items[card.getAttribute('data-id')];
      if (e.target.classList.contains('idea')) { var inp = $('[data-f="will"]', card); inp.value = e.target.textContent; it.will = inp.value; save(state); inp.focus(); return; }
      var w = e.target.closest('.wbox'); if (w && !w.disabled) { var i = w.getAttribute('data-w'); it.checks[i] = !it.checks[i]; save(state); w.classList.toggle('on', !!it.checks[i]); $('.pc', card).textContent = pct(it) + '%'; renderSummaryOnly(); }
    });
    function renderSummaryOnly() { var keep = document.activeElement; renderPlan(); if (keep && keep.getAttribute && keep.getAttribute('data-w')) { var again = $('.pitem [data-w="' + keep.getAttribute('data-w') + '"]'); if (again) again.focus(); } }
    $('#notes').addEventListener('input', function (e) { var n = e.target.getAttribute('data-n'); if (n === null) return; state.notes[n] = e.target.value; save(state); });
    $('#printplan').addEventListener('click', function () { window.print(); });
    $('#resetplan').addEventListener('click', function () { if (confirm('Clear your whole plan on this device?')) { state = { items: {}, notes: {} }; save(state); renderPlan(); } });
    $('#icsplan').addEventListener('click', function () {
      var ids = Object.keys(state.items).filter(function (id) { return B[id]; });
      var lines = ids.map(function (id) { var it = state.items[id]; return '- ' + B[id].title + (it.will ? ' (I will ' + it.will + (it.when ? ', ' + it.when : '') + ')' : ''); });
      var desc = ('My six-month plan from ' + S.label + ':\\n' + lines.join('\\n') + '\\n\\nCheck in: ' + location.origin + S.base + 'plan/').replace(/[,;]/g, function (c) { return '\\' + c; });
      var ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//What Did They Say//Plan//EN', 'BEGIN:VEVENT', 'UID:' + Date.now() + '@whatdidtheysay', 'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z',
        'DTSTART:' + P.ics_start + 'T190000', 'DURATION:PT15M', 'RRULE:FREQ=WEEKLY;COUNT=' + WEEKS.length, 'SUMMARY:Six-month plan check-in', 'DESCRIPTION:' + desc, 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
      var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' })); a.download = 'six-month-plan-check-in.ics'; document.body.appendChild(a); a.click(); a.remove();
      toast('Calendar reminder downloaded. Open it to add a weekly Sunday check-in.');
    });
    renderPlan();
    if (pick) pick.addEventListener('toggle', function () {}, true);
  }
})();
