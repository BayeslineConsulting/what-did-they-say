/* What Did They Say? shared script. Page data arrives in window.SITE (always) and
   window.PAGE (page-specific). Everything is guarded so each page runs only its parts. */
(function () {
  'use strict';
  var S = window.SITE || {}, P = window.PAGE || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  /* ---------- storage (plan): saved on this device; optionally synced through a private link ---------- */
  var KEY = 'wdts-plan-' + (S.conf || '') + '-v3', PKEY = KEY + '-pid';
  var EMPTY = function () { return { items: {}, notes: {}, t: 0 }; };
  function load() { try { var o = JSON.parse(localStorage.getItem(KEY) || ''); if (o && o.items) { o.notes = o.notes || {}; o.t = o.t || 0; return o; } } catch (e) {} return EMPTY(); }
  function getPid() { try { return localStorage.getItem(PKEY) || ''; } catch (e) { return ''; } }
  function setPid(v) { try { if (v) localStorage.setItem(PKEY, v); else localStorage.removeItem(PKEY); } catch (e) {} }
  var state = load(), pid = getPid(), syncState = pid ? 'checking' : 'off', pushTimer = null, ready = Promise.resolve();
  var SUPA = (S.signup_endpoint || '').replace(/\/rest\/v1\/.*$/, '');
  var UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  function rpc(name, body) {
    if (!SUPA) return Promise.reject(new Error('offline'));
    var h = { 'Content-Type': 'application/json' }; for (var k in (S.signup_headers || {})) h[k] = S.signup_headers[k];
    return fetch(SUPA + '/rest/v1/rpc/' + name, { method: 'POST', headers: h, body: JSON.stringify(body) }).then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); });
  }
  function setSync(st) { syncState = st; if (window.__renderSync) window.__renderSync(); }
  function push() {
    if (!pid) return;
    setSync('saving');
    ready.then(function () { return rpc('plan_save', { p_id: pid, p_data: state }); })
      .then(function (ok) { setSync(ok ? 'saved' : 'missing'); }).catch(function () { setSync('error'); });
  }
  function save(st) {
    st.t = Date.now();
    try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
    if (pid) { clearTimeout(pushTimer); pushTimer = setTimeout(push, 1200); }
  }
  function adopt(data) { state = { items: data.items || {}, notes: data.notes || {}, t: data.t || 0 }; try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function refresh() { syncAddButtons(); if (window.__renderPlan) window.__renderPlan(); }
  /* a private link looks like /plan/#p=<code>; the code never leaves the browser except to fetch the plan */
  var hm = /[#&]p=([0-9a-f-]{36})/i.exec(location.hash || '');
  if (hm && UUID.test(hm[1])) {
    var incoming = hm[1];
    try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
    setSync('checking');
    ready = rpc('plan_get', { p_id: incoming }).then(function (res) {
      if (!res || !res.data) { setSync(pid ? 'saved' : 'off'); toast('That link did not open a plan. Check that you copied all of it.'); return; }
      var mineCount = Object.keys(state.items).length;
      if (incoming !== pid && mineCount && !confirm('Open the plan from this link? It will replace the plan saved on this device.')) { setSync(pid ? 'saved' : 'off'); return; }
      pid = incoming; setPid(pid); adopt(res.data); setSync('saved'); refresh(); toast('Your plan is open on this device.');
    }).catch(function () { setSync('error'); });
  } else if (pid) {
    ready = rpc('plan_get', { p_id: pid }).then(function (res) {
      if (!res || !res.data) { setSync('missing'); return; }
      if ((res.data.t || 0) > (state.t || 0)) { adopt(res.data); setSync('saved'); refresh(); }
      else if ((state.t || 0) > (res.data.t || 0)) { setSync('saved'); push(); }
      else setSync('saved');
    }).catch(function () { setSync('error'); });
  }

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
    else { state.items[id] = { will: '', when: '', obs: '', backup: '', tell: '', why: '', freq: 'Weekly', start: 0, checks: {} }; toast('Added. <a href="' + S.base + 'plan/">Make it specific in my plan</a>'); }
    save(state); syncAddButtons(); if (window.__renderPlan) window.__renderPlan();
  });
  syncAddButtons();
  document.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('[data-print]')) window.print(); });

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

  /* ---------- quizzes: three levels, shuffled options, best score kept on this device ---------- */
  var qz = $('#qz');
  if (qz && P.quiz && P.quiz.levels) {
    var QZ = P.quiz, LV = ['easy', 'medium', 'hard'].filter(function (l) { return QZ.levels[l] && QZ.levels[l].length; });
    var LN = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
    var LD = { easy: 'For families and first-time listeners', medium: 'For those who want to understand it', hard: 'For those who have studied it' };
    var BK = 'wdts-quiz-' + (S.conf || '') + '-' + QZ.id, best = {};
    try { best = JSON.parse(localStorage.getItem(BK) || '{}') || {}; } catch (e) { best = {}; }
    var lv, qs, qi, score, answered;
    var shuf = function (a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; };
    var top = function () { var r = qz.getBoundingClientRect(); if (r.top < 0 || r.top > window.innerHeight * .6) qz.scrollIntoView({ block: 'start', behavior: 'smooth' }); };
    var home = function () {
      qz.innerHTML = '<div><h3>Choose a level</h3><div class="qlv">' + LV.map(function (l) {
        var b = best[l]; return '<button class="qlvb" data-l="' + l + '"><b>' + LN[l] + '</b><span>' + LD[l] + '</span><i>' + QZ.levels[l].length + ' questions' + (b != null ? ' · your best: ' + b + ' of ' + QZ.levels[l].length : '') + '</i></button>';
      }).join('') + '</div></div>';
      $$('.qlvb', qz).forEach(function (b) { b.onclick = function () { start(b.getAttribute('data-l')); top(); }; });
    };
    var start = function (l) {
      lv = l; qi = 0; score = 0;
      qs = QZ.levels[l].map(function (q) { var idx = shuf(q.o.map(function (_, i) { return i; })); return { q: q.q, o: idx.map(function (i) { return q.o[i]; }), a: idx.indexOf(q.a), w: q.w, r: q.r, h: q.h }; });
      ask();
    };
    var ask = function () {
      var q = qs[qi], n = qs.length; answered = false;
      qz.innerHTML = '<div><div class="qtop"><span class="qtag">' + LN[lv] + '</span><span class="qmeta">Question ' + (qi + 1) + ' of ' + n + '</span><button class="qquit" id="qquit">Change level</button></div>' +
        '<div class="qbar"><i style="width:' + Math.round(100 * qi / n) + '%"></i></div><p class="qq" id="qq" tabindex="-1">' + esc(q.q) + '</p><div class="qopts">' +
        q.o.map(function (o, j) { return '<button class="qopt" data-j="' + j + '">' + esc(o) + '</button>'; }).join('') +
        '</div><div class="qwhy" id="qwhy" role="status"></div><button class="btn qnext" id="qnext" hidden>' + (qi + 1 < n ? 'Next question' : 'See my score') + '</button></div>';
      $('#qquit').onclick = home;
      $$('.qopt', qz).forEach(function (b) {
        b.onclick = function () {
          if (answered) return; answered = true; var j = +b.getAttribute('data-j'), ok = j === q.a; if (ok) score++;
          $$('.qopt', qz).forEach(function (x) { var k = +x.getAttribute('data-j'); x.disabled = true; if (k === q.a) x.classList.add('right'); else if (k === j) x.classList.add('wrong'); });
          $('#qwhy').innerHTML = '<b>' + (ok ? 'Right.' : 'Not quite.') + '</b> ' + esc(q.w) + (q.r ? ' <span class="qref">' + (q.h ? '<a href="' + esc(q.h) + '">' + esc(q.r) + '</a>' : esc(q.r)) + '</span>' : '');
          $('#qnext').hidden = false; $('#qnext').focus();
        };
      });
      $('#qnext').onclick = function () { qi++; if (qi < qs.length) ask(); else done(); top(); };
      if (qi > 0) { try { $('#qq').focus({ preventScroll: true }); } catch (e) {} }
    };
    var done = function () {
      var n = qs.length, pct = score / n, nxt = LV[LV.indexOf(lv) + 1];
      if (best[lv] == null || score > best[lv]) { best[lv] = score; try { localStorage.setItem(BK, JSON.stringify(best)); } catch (e) {} }
      var msg = pct === 1 ? 'A perfect score.' : pct >= .8 ? 'Well done. You were listening.' : pct >= .5 ? 'A good start. The explanations show where to look again.' : 'Worth another listen. Every answer is in the talks.';
      qz.innerHTML = '<div><div class="qtop"><span class="qtag">' + LN[lv] + '</span></div><p class="qscore" id="qscore" tabindex="-1">' + score + ' of ' + n + '</p><p class="qq">' + msg + '</p><div class="qacts">' +
        (nxt ? '<button class="btn" id="qup">Try the ' + LN[nxt].toLowerCase() + ' quiz</button>' : '') + '<button class="btn ghost" id="qagain">Take it again</button><button class="btn ghost" id="qshare">Share my score</button><button class="btn ghost" id="qhome">All levels</button></div><p class="qwhy" id="qsmsg" role="status"></p></div>';
      if (nxt) $('#qup').onclick = function () { start(nxt); top(); };
      $('#qagain').onclick = function () { start(lv); top(); };
      $('#qhome').onclick = home;
      $('#qshare').onclick = function () {
        var url = location.origin + QZ.path, text = 'I got ' + score + ' of ' + n + ' on the ' + LN[lv].toLowerCase() + ' quiz for ' + QZ.name + '. Can you beat it?';
        var copied = function () { $('#qsmsg').textContent = 'Copied. Paste it anywhere to share.'; };
        if (navigator.share) { navigator.share({ text: text, url: url }).catch(function () {}); }
        else if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text + ' ' + url).then(copied, function () { $('#qsmsg').textContent = text + ' ' + url; }); }
        else { $('#qsmsg').textContent = text + ' ' + url; }
      };
      try { $('#qscore').focus({ preventScroll: true }); } catch (e) {}
    };
    var hm = /^#quiz-(easy|medium|hard)$/.exec(location.hash || '');
    if (hm && LV.indexOf(hm[1]) >= 0) { start(hm[1]); setTimeout(function () { qz.scrollIntoView({ block: 'center' }); }, 60); } else home();
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
    var CUES = ['after my morning prayer', 'at breakfast', 'on my way to work or school', 'at lunch', 'after dinner', 'before bed', 'on Sunday after church', 'on Monday evening'];
    var mine = $('#mine'), pick = $('#pick'), sum = $('#plansum'), tw = $('#thisweek'), sbox = $('#syncbox');
    var today = new Date(), iso = today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
    var NOW = 0; WEEKS.forEach(function (w) { if (w.d && w.d <= iso) NOW = w.i; });
    var weeksFor = function (it) { return WEEKS.filter(function (w) { return w.m >= (+it.start || 0); }); };
    var pct = function (it) { var ws = weeksFor(it), d = ws.filter(function (w) { return it.checks[w.i]; }).length; return ws.length ? Math.round(100 * d / ws.length) : 0; };
    var ids = function () { return Object.keys(state.items).filter(function (id) { return B[id]; }); };
    var lower = function (x) { x = String(x || '').trim().replace(/[.!]+$/, ''); return x && !/^I\b/.test(x) && /^[A-Z][a-z]/.test(x) ? x.charAt(0).toLowerCase() + x.slice(1) : x; };
    function commitHTML(it) {
      var will = lower(it.will).replace(/^i will\s+/i, ''), when = lower(it.when), obs = lower(it.obs).replace(/^if\s+/i, ''), bk = lower(it.backup).replace(/^(then\s+)?i will\s+/i, '');
      if (!will) return '<small>My commitment</small><span class="todo">Answer the first question below and your commitment will appear here.</span>';
      var s1 = (when ? when.charAt(0).toUpperCase() + when.slice(1) + ', I will ' : 'I will ') + esc(will) + '.';
      if (when) s1 = esc(when.charAt(0).toUpperCase() + when.slice(1)) + ', I will ' + esc(will) + '.';
      var s2 = obs && bk ? ' If ' + esc(obs) + ', then I will ' + esc(bk) + '.' : '';
      var s3 = it.tell && it.tell.trim() ? ' I will tell ' + esc(it.tell.trim().replace(/[.!]+$/, '')) + '.' : '';
      return '<small>My commitment &middot; ' + esc(String(it.freq || '').toLowerCase()) + '</small>' + s1 + s2 + s3;
    }
    function short(id) { var it = state.items[id]; return it.will && it.will.trim() ? it.will.trim() : (B[id].label || B[id].title); }
    function renderWeek() {
      var list = ids().filter(function (id) { var it = state.items[id]; return WEEKS[NOW].m >= (+it.start || 0); });
      if (!list.length) { tw.innerHTML = ''; return; }
      tw.innerHTML = '<div class="tw"><h2>This week</h2><p>Week of ' + esc(WEEKS[NOW].label) + '. One tap when you have followed through.</p>' + list.map(function (id) {
        var on = !!state.items[id].checks[NOW];
        return '<div class="twrow"><span>' + esc(short(id)) + '</span><button type="button" class="twbtn' + (on ? ' on' : '') + '" data-tw="' + id + '" aria-pressed="' + on + '">' + (on ? 'Done this week ✓' : 'I did this') + '</button></div>';
      }).join('') + '</div>';
    }
    function renderSummary() {
      var list = ids(), total = 0, done = 0;
      list.forEach(function (id) { var it = state.items[id]; var ws = weeksFor(it); total += ws.length; done += ws.filter(function (w) { return it.checks[w.i]; }).length; });
      sum.innerHTML = list.length
        ? '<b>' + list.length + '</b> invitation' + (list.length > 1 ? 's' : '') + ' in your plan &middot; <b>' + (total ? Math.round(100 * done / total) : 0) + '%</b> of weekly check-ins done' + (list.length > 3 ? '<span class="hint">Tip: most people do best with one to three at a time. Stagger the rest with “Starts in.”</span>' : '')
        : 'Your plan is empty. Choose one to three invitations below to begin.';
      $('#planacts').hidden = !list.length;
    }
    function renderPlan() {
      var list = ids();
      renderSummary(); renderWeek(); renderSync();
      mine.innerHTML = list.map(function (id) {
        var b = B[id], it = state.items[id];
        var val = function (f) { return esc(it[f] || ''); };
        return '<article class="pitem" data-id="' + id + '"><div class="ph2"><div><span class="ptag">' + esc(b.group_label) + (b.label ? ' &middot; ' + esc(b.label) : '') + '</span><h3>“' + esc(b.title) + '”</h3><div class="by">' + esc(b.speakers.join(', ')) + '</div></div><button class="xbtn" data-add="' + id + '" aria-label="Remove from plan">Remove</button></div>' +
          '<div class="commit" data-commit>' + commitHTML(it) + '</div>' +
          '<div class="qa">' +
          '<label><span class="qh"><span class="stepno">1</span>What exactly will I do?</span><small>Small and specific beats big and vague. Start with something you could do even on a hard day.</small><input data-f="will" value="' + val('will') + '" placeholder="e.g. read one chapter of the Book of Mormon" autocomplete="off"></label>' +
          (b.ideas && b.ideas.length ? '<div class="ideas"><span>Ideas:</span>' + b.ideas.map(function (x) { return '<button class="idea" type="button">' + esc(x) + '</button>'; }).join('') + '</div>' : '') +
          '<label><span class="qh"><span class="stepno">2</span>When and where?</span><small>Tie it to something you already do.</small><input data-f="when" value="' + val('when') + '" placeholder="e.g. after dinner, at the kitchen table" autocomplete="off"></label>' +
          '<div class="cues">' + CUES.map(function (c) { return '<button class="cue" type="button">' + esc(c) + '</button>'; }).join('') + '</div>' +
          '<div class="pair"><label>How often<select data-f="freq">' + FREQ.map(function (f) { return '<option' + (f === it.freq ? ' selected' : '') + '>' + f + '</option>'; }).join('') + '</select></label>' +
          '<label>Starts in<select data-f="start">' + MONTHS.map(function (m, i) { return '<option value="' + i + '"' + (+it.start === i ? ' selected' : '') + '>' + m + '</option>'; }).join('') + '</select></label></div>' +
          '<div><label><span class="qh"><span class="stepno">3</span>What might get in the way, and what will I do then?</span><small>Naming the obstacle ahead of time makes it far easier to get past.</small></label><div class="pair" style="margin-top:6px"><input data-f="obs" aria-label="If this gets in the way" value="' + val('obs') + '" placeholder="If… e.g. I get home late" autocomplete="off"><input data-f="backup" aria-label="Then I will" value="' + val('backup') + '" placeholder="then I will… e.g. read one verse before bed" autocomplete="off"></div></div>' +
          '<label><span class="qh"><span class="stepno">4</span>Who will I tell?</span><small>Optional. Telling one person makes a commitment real.</small><input data-f="tell" value="' + val('tell') + '" placeholder="e.g. my wife, my ministering brother" autocomplete="off"></label>' +
          '</div>' +
          '<details class="more"' + (it.why ? ' open' : '') + '><summary>Why this one? (optional)</summary><div class="qa"><label><small>What do I hope will be different by the next conference?</small><input data-f="why" value="' + val('why') + '" autocomplete="off"></label></div></details>' +
          '<div class="wk"><div class="wkh"><span>Weekly check-ins</span><span class="pc">' + pct(it) + '%</span></div><div class="weeks">' + WEEKS.map(function (w) {
            var off = w.m < (+it.start || 0);
            return '<button type="button" class="wbox' + (it.checks[w.i] ? ' on' : '') + '" data-w="' + w.i + '"' + (off ? ' disabled' : '') + ' title="Week of ' + w.label + '" aria-label="Week of ' + w.label + (it.checks[w.i] ? ', done' : '') + '"></button>';
          }).join('') + '</div><div class="wkl">' + MONTHS.map(function (m, mi) { var n = WEEKS.filter(function (w) { return w.m === mi; }).length; return n ? '<span style="grid-column:span ' + n + '">' + m.slice(0, 3) + '</span>' : ''; }).join('') + '</div></div></article>';
      }).join('');
      $('#notes').innerHTML = list.length ? '<h2>Monthly reflection</h2><p class="note">At the end of each month, write what went well and what you’ll adjust.</p><div class="ngrid">' + MONTHS.map(function (m, i) { return '<label>' + m + '<textarea data-n="' + i + '" rows="3" placeholder="What went well? What will I adjust?">' + esc(state.notes[i] || '') + '</textarea></label>'; }).join('') + '</div>' : '';
      syncAddButtons();
    }
    window.__renderPlan = renderPlan;
    /* ----- private link ----- */
    function linkURL() { return location.origin + S.base + 'plan/#p=' + pid; }
    function renderSync() {
      if (!sbox) return;
      if (!SUPA) { sbox.hidden = true; return; }
      var has = ids().length > 0;
      sbox.hidden = !has && !pid;
      if (!pid) { sbox.innerHTML = '<b>Keep this plan on every device.</b> Create a private link and open it on your phone, tablet or computer. No account, no email.<div class="row"><button class="tbtn" id="mklink" type="button">Create my private link</button><span class="st">Anyone who has the link can open and change this plan, so keep it to yourself.</span></div>'; return; }
      var msg = { checking: 'Checking for your latest plan…', saving: 'Saving…', saved: 'Saved online', error: 'Could not reach the server. Your plan is still saved on this device and will sync when you are back online.', missing: 'The online copy was not found. Your plan is still saved on this device.' }[syncState] || '';
      sbox.innerHTML = '<b>Your private link</b> &middot; <span class="st" id="syncst">' + esc(msg) + '</span><div class="row"><input id="plink" readonly aria-label="Your private plan link" value="' + esc(linkURL()) + '"><button class="tbtn" id="cplink" type="button">Copy link</button><a class="tbtn" style="text-decoration:none;display:inline-flex;align-items:center" href="mailto:?subject=' + encodeURIComponent('My six-month plan') + '&body=' + encodeURIComponent('My private plan link (keep this to yourself):\n' + linkURL()) + '">Email it to myself</a></div><span class="st">Open this link on any device to pick up your plan. Keep it private: anyone who has it can open and change the plan.</span> <button class="linkbtn" id="unlink" type="button">Stop syncing and delete the online copy</button>';
    }
    window.__renderSync = function () { var st = $('#syncst'); if (pid && st && sbox.querySelector('#plink')) { var m = { checking: 'Checking for your latest plan…', saving: 'Saving…', saved: 'Saved online', error: 'Could not reach the server. Your plan is still saved on this device and will sync when you are back online.', missing: 'The online copy was not found. Your plan is still saved on this device.' }[syncState] || ''; st.textContent = m; } else renderSync(); };
    if (sbox) sbox.addEventListener('click', function (e) {
      var t = e.target;
      if (t.id === 'mklink') {
        t.disabled = true; t.textContent = 'Creating…'; state.t = Date.now();
        rpc('plan_create', { p_conf: S.conf, p_data: state }).then(function (id) { if (!UUID.test(String(id))) throw new Error('bad id'); pid = String(id); setPid(pid); syncState = 'saved'; renderSync(); toast('Your private link is ready. Copy it or email it to yourself.'); })
          .catch(function () { t.disabled = false; t.textContent = 'Create my private link'; toast('That didn’t go through. Please check your connection and try again.'); });
      } else if (t.id === 'cplink') {
        var inp = $('#plink'); inp.select();
        (navigator.clipboard && navigator.clipboard.writeText ? navigator.clipboard.writeText(inp.value) : Promise.reject()).then(function () { toast('Link copied.'); }, function () { try { document.execCommand('copy'); toast('Link copied.'); } catch (x) { toast('Press and hold the link to copy it.'); } });
      } else if (t.id === 'unlink') {
        if (!confirm('Stop syncing and delete the online copy? Your plan stays on this device.')) return;
        var old = pid; pid = ''; setPid(''); syncState = 'off'; renderSync();
        rpc('plan_delete', { p_id: old }).then(function () { toast('Online copy deleted. Your plan is still on this device.'); }, function () { toast('Syncing stopped on this device.'); });
      }
    });
    /* ----- editing ----- */
    mine.addEventListener('input', function (e) {
      var card = e.target.closest('.pitem'), f = e.target.getAttribute('data-f'); if (!card || !f) return;
      var it = state.items[card.getAttribute('data-id')]; it[f] = e.target.value; save(state);
      $('[data-commit]', card).innerHTML = commitHTML(it); if (f === 'will') renderWeek();
    });
    mine.addEventListener('change', function (e) { if (e.target.getAttribute('data-f') === 'start') renderPlan(); });
    mine.addEventListener('click', function (e) {
      var card = e.target.closest('.pitem'); if (!card) return; var it = state.items[card.getAttribute('data-id')];
      var fill = function (f, v) { var inp = $('[data-f="' + f + '"]', card); inp.value = v; it[f] = v; save(state); $('[data-commit]', card).innerHTML = commitHTML(it); renderWeek(); inp.focus(); };
      if (e.target.classList.contains('idea')) { fill('will', e.target.textContent); return; }
      if (e.target.classList.contains('cue')) { fill('when', e.target.textContent); return; }
      var w = e.target.closest('.wbox'); if (w && !w.disabled) { var i = w.getAttribute('data-w'); it.checks[i] = !it.checks[i]; save(state); w.classList.toggle('on', !!it.checks[i]); $('.pc', card).textContent = pct(it) + '%'; renderSummary(); renderWeek(); }
    });
    tw.addEventListener('click', function (e) {
      var b = e.target.closest('[data-tw]'); if (!b) return; var it = state.items[b.getAttribute('data-tw')]; if (!it) return;
      it.checks[NOW] = !it.checks[NOW]; save(state); renderPlan(); var again = $('[data-tw="' + b.getAttribute('data-tw') + '"]'); if (again) again.focus();
    });
    $('#notes').addEventListener('input', function (e) { var n = e.target.getAttribute('data-n'); if (n === null) return; state.notes[n] = e.target.value; save(state); });
    $('#printplan').addEventListener('click', function () { window.print(); });
    $('#resetplan').addEventListener('click', function () { if (confirm('Clear your whole plan?' + (pid ? ' This also clears it on your other devices.' : ''))) { state = EMPTY(); save(state); renderPlan(); } });
    $('#icsplan').addEventListener('click', function () {
      var lines = ids().map(function (id) { var d = document.createElement('div'); d.innerHTML = commitHTML(state.items[id]).replace(/<small>.*?<\/small>/, ''); var c = state.items[id].will ? d.textContent : (B[id].label || B[id].title); return '- ' + c; });
      var desc = ('My six-month plan from ' + S.label + ':\\n' + lines.join('\\n') + '\\n\\nCheck in: ' + location.origin + S.base + 'plan/').replace(/[,;]/g, function (c) { return '\\' + c; });
      var ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//What Did They Say//Plan//EN', 'BEGIN:VEVENT', 'UID:' + Date.now() + '@whatdidtheysay', 'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z',
        'DTSTART:' + P.ics_start + 'T190000', 'DURATION:PT15M', 'RRULE:FREQ=WEEKLY;COUNT=' + WEEKS.length, 'SUMMARY:Six-month plan check-in', 'DESCRIPTION:' + desc, 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
      var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' })); a.download = 'six-month-plan-check-in.ics'; document.body.appendChild(a); a.click(); a.remove();
      toast('Calendar reminder downloaded. Open it to add a weekly Sunday check-in.');
    });
    renderPlan();
  }
})();
