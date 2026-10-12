#!/usr/bin/env python3
"""Build the What Did They Say? website (static, multi-page) for one conference.
Usage: python build_site.py DATA.json OUT_DIR [SITE_URL]
DATA.json is the data object written by build_report_page.py (OUT.html -> OUT.json).
Earlier conference folders already in OUT_DIR are kept, so the archive grows each run.
Pages per conference (/CONF/...): overview, talks/, talks/SLUG/, themes/, themes/SLUG/, plan/,
numbers/, methodology/. Site pages: /about/, /conferences/, 404.html. Plus /assets/site.css,
/assets/app.js, og.png, robots.txt, sitemap.xml, vercel.json.
Talk videos: put {"T01": {"youtube": "VIDEO_ID", "church": "https://..."}} in RUN/links.json and
rebuild; talk pages then show a click-to-play video and a link to the Church's talk page."""
import os, re, sys, json, html as H, datetime as dt
DATA, out = sys.argv[1:3]; URL = (sys.argv[3] if len(sys.argv) > 3 else '').rstrip('/')
here = os.path.dirname(os.path.abspath(__file__)); A = lambda f: os.path.join(here, '..', 'assets', f)
D = json.load(open(DATA)); S = D['site']; CONF = D['conf']; LABEL = D['label']; NAME = S.get('name', 'What Did They Say?'); B = f'/{CONF}/'
TPL = open(A('report_template.html')).read()
e = lambda x: H.escape(str(x), quote=True)
qe = lambda x: e(str(x).replace('“', '‘').replace('”', '’'))
brand = e(NAME).replace('?', '<span>?</span>')
CSS = re.search(r'<style>(.*?)</style>', TPL, re.S).group(1)
FONTS = re.search(r'<link rel="preconnect".*?rel="stylesheet">', TPL, re.S).group(0)
FAV = re.search(r'<link rel="icon"[^>]*>', TPL).group(0)
ICONS = dict(re.findall(r"(\w+):'(<[^']+)'", re.search(r'const ICON=\{(.*?)\};', TPL, re.S).group(1)))
ART = re.search(r'<svg class="art".*?</svg>', TPL, re.S).group(0)
BOOK = re.search(r'<svg class="book".*?</svg>', TPL, re.S).group(0)
COMPASS = re.search(r"const QART='(.*?)';", TPL, re.S).group(1).replace('\\"', '"')
ic = lambda tid: f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS.get(D["icons"].get(tid, "dot"), ICONS.get("dot", ""))}</svg>'
T = {t['id']: t for t in D['talks']}; ORD = [t['id'] for t in D['talks']]
TH = {t['id']: t for t in D['themes']}; THS = sorted(D['themes'], key=lambda t: t['n'])
BYNAME = {}
for t in D['talks']: BYNAME.setdefault(t['short'], t)
nlink = lambda n: f'<a href="{B}talks/{BYNAME[n]["slug"]}/">{e(n)}</a>' if n in BYNAME else e(n)
SESS = D['sessnames']; OFFICIAL = 'https://www.churchofjesuschrist.org/study/general-conference?lang=eng'
PAGES = []
SITEJS = json.dumps({'conf': CONF, 'base': B, 'label': LABEL, 'signup_endpoint': S.get('signup_endpoint', ''), 'signup_headers': S.get('signup_headers', {})})
TABS = [('overview', 'Overview', '', '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>'),
        ('talks', 'Talks', 'talks/', '<rect x="3" y="5" width="18" height="13" rx="2"/><path d="M10 9l5 2.5-5 2.5z"/>'),
        ('themes', 'Themes', 'themes/', '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>'),
        ('plan', 'Your Plan', 'plan/', '<path d="M9 11l2 2 4-4"/><rect x="4" y="4" width="16" height="16" rx="3"/>'),
        ('lessons', 'Lessons', 'lessons/', '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/><path d="M9 8h7M9 12h5"/>'),
        ('numbers', 'By the Numbers', 'numbers/', '<path d="M5 20V10M12 20V4M19 20v-7"/>'),
        ('how', 'How It Works', 'how-it-works/', '')]
def jsdump(o): return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
def layout(title, desc, body, path, tab='', page_js=None, kind='article'):
    url = (URL + path) if URL else path
    on = lambda k: ' class="on" aria-current="page"' if k == tab else ''
    links = ''.join(f'<a href="{B}{u}"{on(k)}>{lab}</a>' for k, lab, u, _ in TABS)
    short = {'By the Numbers': 'Numbers', 'Your Plan': 'Plan', 'How It Works': 'How', 'Overview': 'Home'}
    bar = ''.join(f'<a href="{B}{u}"{on(k)}><svg viewBox="0 0 24 24" aria-hidden="true">{svg}</svg>{short.get(lab, lab)}</a>' for k, lab, u, svg in TABS if svg)
    pj = f'<script>window.PAGE={jsdump(page_js)}</script>' if page_js else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="{kind}"><meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e((URL or '') + '/og.png')}"><meta name="twitter:card" content="summary_large_image">
{FAV}
{FONTS}<link rel="stylesheet" href="/assets/site.css">
<script defer src="/_vercel/insights/script.js"></script></head><body>
<a href="#main" class="skip">Skip to content</a>
<nav class="top" aria-label="Main"><div class="wrap"><a class="brand" href="/">{brand}</a><div class="links">{links}</div><a class="cta" href="#signup">Get updates</a></div></nav>
<main id="main">{body}</main>
<section class="band tint" id="signup"><div class="wrap"><div class="signup">{BOOK}<div><h2>Never miss a conference.</h2><p>One email after each general conference: what was said, the numbers, and a fresh six-month list.</p></div>
<form id="sform" novalidate><label for="fname">First name (optional)</label><input id="fname" type="text" autocomplete="given-name"><label for="email">Email</label><input id="email" type="email" autocomplete="email" inputmode="email" required><button class="btn" type="submit">Sign me up</button><div class="msg" id="smsg" role="status"></div><div class="fine">Your email is used only for conference updates, never shared.</div></form></div></div></section>
<footer><div class="wrap"><div class="brand">{brand}</div><p style="max-width:76ch">{e(S.get('disclaimer', ''))}</p><p style="font-size:14px">Quotations are taken word for word from the official talk texts and checked by script. Labels such as T05.12 mean talk 5, paragraph 12. Talk summaries and plan ideas are written for this site; read and watch the official talks at churchofjesuschrist.org. Illustrations are original artwork made for this site.</p><p><a href="/about/">About</a> · <a href="/privacy/">Privacy</a> · <a href="/conferences/">All conferences</a> · <a href="{B}how-it-works/">How it works</a> · <a href="{B}methodology/">Full methodology</a></p></div></footer>
<nav class="tabbar" aria-label="Sections">{bar}</nav>
<script>window.SITE={SITEJS}</script>{pj}<script src="/assets/app.js" defer></script></body></html>'''
def write(path, htm):
    f = os.path.join(out, path.strip('/'), 'index.html') if path.endswith('/') else os.path.join(out, path.strip('/'))
    os.makedirs(os.path.dirname(f), exist_ok=True); open(f, 'w').write(htm); PAGES.append(path)
crumb = lambda *xs: '<div class="wrap"><p class="crumbs">' + ' › '.join(xs) + '</p></div>'
conf_c = f'<a href="{B}">{e(LABEL)}</a>'
def head(kick, h1, sub='', extra=''):
    return f'<div class="wrap"><header class="ph"><div class="kick">{kick}</div><h1>{h1}</h1>' + (f'<p class="sub2">{sub}</p>' if sub else '') + f'{extra}</header></div>'
def initials(n):
    w = [x for x in re.sub(r'^(Elder|Sister|President|Bishop|Brother)\s+', '', n.replace('*', '')).split() if x[0].isalpha() and not re.fullmatch(r'[A-Z]\.', x)]
    return (w[0][0] + w[-1][0]) if len(w) > 1 else (w[0][0] if w else '')
def first_sentence(s):
    m = re.match(r'(.+?[.!?])(\s|$)', s or ''); return m.group(1) if m else (s or '')
def thumb(t):
    v = t.get('video') or {}
    if v.get('youtube'): return f'<div class="thumb"><img src="https://i.ytimg.com/vi/{e(v["youtube"])}/mqdefault.jpg" alt="" loading="lazy" width="320" height="180"><span class="play"></span></div>'
    return f'<div class="thumb"><span class="ini">{e(initials(t["speaker"]))}</span><span class="st">Video coming soon</span></div>'
def talkcard(t, summary=True):
    tags = ''.join(f'<span>{e(TH[k]["short"])}</span>' for k, v in t['themes'][:2])
    sm = f'<p>{e(first_sentence(t.get("summary")))}</p>' if summary and t.get('summary') else ''
    tt = f'<i class="tt">{e(t["title"])}</i>' if t.get('title') else ''
    return f'<a class="tc" href="{B}talks/{t["slug"]}/">{thumb(t)}<div class="bd"><b>{e(t["speaker"])}</b>{tt}<small>{e(t["role"])}</small>{sm}<div class="tags">{tags}</div></div></a>'
def via(it): return f' <span class="via">{e(it["via"])}</span>' if it.get('via') else ''
def asked(b): return ('Repeated by ' if b['group'] == 'repeated' else 'Asked by ') + ', '.join(nlink(n) for n in b['speakers'])
GROUPLAB = {'own': "The prophet's invitation", 'repeated': "The prophet's earlier invitation, repeated", 'multi': 'Invitation from several speakers', 'audience': 'For a specific group', 'single': 'Invitation'}
BID = {i: b for i, b in enumerate(D['bundles'])}
addbtn = lambda i: f'<button class="addbtn" type="button" data-add="{BID[i]["key"]}">Add to my plan</button>'
def stat(b, s): return f'<div class="stat"><b>{b}</b><span>{s}</span></div>'
STATS = [(D["stats"]["talks"], "talks"), (D["stats"]["speakers"], "speakers"), (f'{D["stats"]["words"]:,}', "words"), (f'{D["stats"]["units"]:,}', "passages coded"), (D["stats"]["scripture"], "scripture references"), (len(D["bundles"]), "invitations")]
# ================= OVERVIEW =================
WHY = ('<aside class="whyname" aria-label="Why this site has its name"><b>Why the name?</b> President Dieter F. Uchtdorf once told of a Church member whose neighbor, on hearing that prophets and apostles speak to the world twice a year, asked exactly that. The member could not recall the details of a single talk, and resolved to remember better. This site is here to help all of us have an answer. '
       '<a href="https://www.churchofjesuschrist.org/study/liahona/2011/09/general-conference-no-ordinary-blessing?lang=eng" target="_blank" rel="noopener">Read the story in &ldquo;General Conference&mdash;No Ordinary Blessing&rdquo;</a> <span class="src">(Liahona, Sept. 2011)</span></aside>')
five = ''.join(f'<div><b>{e(t)}</b><p>{e(p)}</p></div>' for t, p in D['five'])
own = [(i, b) for i, b in BID.items() if b['group'] == 'own']
oaks_html = ''.join(f'<div class="oask"><b>“{qe(b["title"])}”</b>{addbtn(i)}</div>' for i, b in own)
tg = ''.join(f'<a href="{B}themes/{t["slug"]}/"><span class="ic">{ic(t["id"])}</span><b>{e(t["name"])}</b><small>{t["talks"]} of {len(ORD)} talks</small></a>' for t in THS)
rails = ''.join(f'<div class="sec" style="margin-top:26px"><h3 style="font-size:20px;margin:0 0 10px">{e(SESS.get(s, s))}</h3><div class="rail">' + ''.join(talkcard(T[tid], False) for tid in ORD if T[tid]['session'] == s) + '</div></div>' for s in D['sessions'])
ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": f"What did they say at the {LABEL}?", "about": LABEL, "publisher": {"@type": "Organization", "name": NAME}, "image": (URL or '') + '/og.png', "inLanguage": "en"})
ov = f'''<script type="application/ld+json">{ld}</script><header class="hero"><div class="wrap hero-grid"><div><span class="kick">{e(LABEL)}</span><h1>{e(S.get("hero", "What did they say in the last general conference?"))}</h1>{WHY}<p class="lead">{e(D["lead"])}</p>
<div class="btns"><a class="btn primary" href="{B}plan/">Build my six-month plan</a><a class="btn" href="#five">Read the 5-minute version</a></div></div>{ART}</div></header>
<div class="wrap"><section class="five" id="five" aria-labelledby="fiveh"><div class="five-head"><h2 id="fiveh">The 5-minute version</h2><span>{len(ORD)} talks · {len(THS)} themes · {len(D["bundles"])} invitations</span></div><div class="five-grid">{five}</div>
<nav class="jump" aria-label="Explore"><a href="{B}talks/">Read &amp; watch the talks</a><a href="{B}themes/">Themes we noticed</a><a href="{B}plan/">Build your plan</a><a href="{B}lessons/">Lessons to teach</a><a href="{B}numbers/">Fun with numbers</a><a href="{B}how-it-works/">How it works</a></nav></section></div>
<section class="band"><div class="wrap"><div class="prophet" style="margin:0 0 6px"><div class="pk">Start here</div><h3>{e(D["president"])}'s invitations</h3><p class="pd">The President of the Church extended these {len(own)} direct invitations, in his own words. Add any of them to your plan.</p><div class="oasks">{oaks_html}</div><p style="margin:20px 0 10px"><a href="{B}plan/" style="color:var(--gold-l);font-weight:600">See all {len(D["bundles"])} invitations and build your plan →</a></p></div></div></section>
<section class="band tint"><div class="wrap"><div class="sechead"><div><div class="part-no">Your six-month plan</div><h2>Turn what you heard into what you do</h2></div><a href="{B}plan/">Start my plan →</a></div>
<div class="how"><div><b>Choose one to three</b><span>Pick the invitations that speak to you. A few done well beats many done halfway.</span></div><div><b>Make it yours</b><span>Four short questions turn an invitation into a commitment: what, when, what might get in the way, and who you will tell.</span></div><div><b>Check in weekly</b><span>One tap a week. Save a private link, with no account, to keep your plan on every device.</span></div></div></div></section>
<section class="band"><div class="wrap"><div class="sechead"><div><div class="part-no">What was said</div><h2>Ten themes we noticed</h2></div><a href="{B}how-it-works/">How we found them →</a></div><div class="tg">{tg}</div></div></section>
<section class="band tint"><div class="wrap"><div class="sechead"><div><div class="part-no">The talks</div><h2>Every talk, summarized</h2></div><a href="{B}talks/">All {len(ORD)} talks →</a></div>{rails}</div></section>
<section class="band"><div class="wrap"><div class="sechead"><div><div class="part-no">By the numbers</div><h2>How well do you remember?</h2></div><a href="{B}numbers/">Take the quiz →</a></div><div class="stats">{"".join(stat(b, s) for b, s in STATS)}</div></div></section>'''
write(B, layout(f'{LABEL}: what was said · {NAME}', f'What did they say at the {LABEL}? Every talk summarized, the themes we noticed, every direct invitation in the speakers\' own words, a six-month plan, and lessons to teach.', ov, B, 'overview', kind='website'))
# ================= TALKS INDEX =================
rows = ''.join(f'<section class="sec" style="margin-top:{14 if i == 0 else 46}px"><h2>{e(SESS.get(s, s))}</h2><div class="tcards">' + ''.join(talkcard(T[tid]) for tid in ORD if T[tid]['session'] == s) + '</div></section>' for i, s in enumerate(D['sessions']))
nv = sum(1 for t in D['talks'] if (t.get('video') or {}).get('youtube'))
vnote = f'<p class="flag" style="margin-top:14px">All {len(ORD)} videos play from the Church’s official General Conference YouTube channel.</p>' if nv == len(ORD) else f'<p class="flag" style="margin-top:14px">Videos are added as the Church publishes each talk: {nv} of {len(ORD)} so far.</p>'
write(f'{B}talks/', layout(f'All talks · {LABEL} · {NAME}', f'Every talk from the {LABEL} by session: a short summary, themes, invitations, key passages, scripture, and video.', crumb(conf_c, 'Talks') + head(e(LABEL), f'All {len(ORD)} talks', 'Choose a talk for its summary, video, themes, invitations, and key passages.', vnote) + f'<div class="wrap" style="padding-bottom:70px">{rows}</div>', f'{B}talks/', 'talks'))
# ================= LESSONS =================
LESS = D.get('lessons', {}); AUD = [('adults', 'Adults', 'Relief Society, elders quorum, Sunday School, or home'), ('youth', 'Youth', 'Ages 11–18: classes, quorums, or home'), ('children', 'Children', 'Ages 3–11: Primary or home')]
def LES(t):
    if t['id'] not in LESS: return ''
    L = LESS[t['id']]
    cards = ''.join(f'<a class="lcard" href="{B}talks/{t["slug"]}/lessons/{a}/"><small>{lab} · 30 minutes</small><b>{e(L[a]["title"])}</b><span>{e(L[a]["big_idea"])}</span></a>' for a, lab, _ in AUD if a in L)
    return f'<div class="sec"><h2>Teach this talk</h2><p class="note">Three ready-to-teach 30-minute lessons built on this talk.</p><div class="lcards">{cards}</div></div>'
def para(u): return f'paragraph {int(u[4:])}'
LNOTE = ('This lesson is an independent study aid written for this site. It is not an official lesson of The Church of Jesus Christ of Latter-day Saints. Quotations are word for word from the official talk; paragraph numbers count the paragraphs of the talk as published at churchofjesuschrist.org, not counting headings or picture captions. '
         'The activities, questions and ideas for acting are suggestions; follow the Spirit and adapt them to those you teach.')
def aq_who(q):
    if q['source'] == 'this conference':
        ot = T[q['unit'][:3]]; return f'{e(q["speaker"])} · <a href="{B}talks/{ot["slug"]}/">{e(ot["title"])}</a>, {para(q["unit"])}'
    return f'{e(q["speaker"])}, quoted in this talk ({para(q["unit"])})'
li = lambda xs: ''.join(f'<li>{e(x)}</li>' for x in xs)
for tid in ORD:
    if tid not in LESS: continue
    t = T[tid]; v = t.get('video') or {}
    for a, lab, who in AUD:
        l = LESS[tid].get(a)
        if not l: continue
        segs_h = ''; clock = 0
        for sg in l['segments']:
            steps = ''.join(f'<li>{e(x)}</li>' for x in sg['steps'])
            qs = ('<div class="lq"><span>Ask</span><ul>' + ''.join(f'<li>{e(x)}</li>' for x in sg.get('questions', [])) + '</ul></div>') if sg.get('questions') else ''
            segs_h += f'<section class="lseg"><div class="lt"><b>{sg["minutes"]} min</b><span>{clock}–{clock + sg["minutes"]}</span></div><div><h3>{e(sg["name"])}</h3><ol>{steps}</ol>{qs}</div></section>'
            clock += sg['minutes']
        kq = ''.join(f'<div class="qcard"><p>“{qe(q["text"])}”</p><div class="who">{e(t["short"])}’s talk, {para(q["unit"])}</div></div>' for q in l['key_quotes'])
        inv = ''.join(f'<div class="qcard inv"><p>“{qe(q["text"])}”</p><div class="who">{e(t["short"])}’s talk, {para(q["unit"])}{via({"via": D.get("quoting", {}).get(q["unit"])})}</div></div>' for q in l.get('invitations', []))
        aq = ''.join(f'<div class="qcard"><p>“{qe(q["text"])}”</p><div class="who">{aq_who(q)}</div></div>' for q in l['aligned_quotes'])
        sc = ''.join(f'<li><b>{e(x["ref"])}</b> {e(x["use"])}</li>' for x in l['scriptures'])
        ad = l['adapt']
        if isinstance(ad, dict):
            y = re.sub(r"^(For )?[Aa]ges 3[–-]7[:.,]\s*", "", ad["younger"]); o = re.sub(r"^(For )?[Aa]ges 8[–-]11[:.,]\s*", "", ad["older"])
            adh = f'<li><b>Ages 3–7.</b> {e(y[:1].upper() + y[1:])}</li><li><b>Ages 8–11.</b> {e(o[:1].upper() + o[1:])}</li>'
        else: adh = li(ad)
        mus = f'<div class="lbox"><h3>Music</h3><ul class="plain">{li(l["music"])}</ul></div>' if l.get('music') else ''
        others = ''.join(f'<a class="{"on" if x == a else ""}" href="{B}talks/{t["slug"]}/lessons/{x}/">{xl}</a>' for x, xl, _ in AUD if x in LESS[tid])
        invh = f'<div class="sec"><h2>The speaker’s direct invitation{"s" if len(l.get("invitations", [])) != 1 else ""}</h2>{inv}</div>' if inv else ''
        path = f'{B}talks/{t["slug"]}/lessons/{a}/'
        body = (crumb(conf_c, f'<a href="{B}lessons/">Lessons</a>', f'<a href="{B}talks/{t["slug"]}/">{e(t["speaker"])}</a>', lab)
            + f'<div class="wrap lesson" style="max-width:900px;padding-bottom:70px"><header class="ph"><div class="kick">30-minute lesson · {lab} · {e(who)}</div><h1>{e(l["title"])}</h1>'
            + f'<p class="sub2">From “{e(t["title"].strip("“”"))},” by {e(t["speaker"])} · {e(t["session_name"])}, {e(LABEL)}</p>'
            + f'<div class="laud" role="navigation" aria-label="Choose an audience">{others}</div>'
            + f'<div class="vlinks no-print"><a class="btn" href="{B}talks/{t["slug"]}/">Watch the talk</a><a class="btn" href="{e(v.get("church") or OFFICIAL)}" rel="noopener">Read the full talk</a><button class="btn" type="button" data-print>Print this lesson</button></div></header>'
            + f'<div class="lgrid"><div class="lbox big"><h3>The big idea</h3><p>{e(l["big_idea"])}</p></div><div class="lbox"><h3>Objective</h3><p>{e(l["objective"])}</p></div></div>'
            + f'<div class="lbox"><h3>Before you teach</h3><ul class="plain">{li(l["prepare"])}</ul></div>'
            + f'<div class="sec"><h2>Lesson plan</h2><p class="note">Thirty minutes in {len(l["segments"])} parts. Times are a guide; let the Spirit and the learners set the pace.</p>{segs_h}</div>'
            + f'<div class="sec"><h2>Key passages from the talk</h2>{kq}</div>{invh}'
            + f'<div class="sec"><h2>Scriptures</h2><ul class="plain lsc">{sc}</ul></div>'
            + f'<div class="sec"><h2>Other voices that agree</h2>{aq}</div>'
            + f'<div class="lgrid" style="margin-top:46px"><div class="lbox"><h3>Three things to remember</h3><ul class="plain">{li(l["takeaways"])}</ul></div><div class="lbox gold"><h3>Ways to act this week</h3><ul class="plain">{li(l["act"])}</ul><p class="note" style="font-size:14px;margin:10px 0 0">Suggestions written for this lesson, not the speaker’s words.</p></div></div>'
            + f'<div class="lgrid">{mus}<div class="lbox"><h3>Adapting the lesson</h3><ul class="plain">{adh}</ul></div></div>'
            + f'<p class="note lnote">{e(LNOTE)}</p></div>')
        write(path, layout(f'{l["title"]} · {lab} lesson · {t["speaker"]} · {NAME}', f'A 30-minute lesson for {lab.lower()} on “{t["title"].strip("“”")}” by {t["speaker"]}: {l["big_idea"]}'[:300], body, path, 'lessons'))
if LESS:
    rows_l = ''
    for i, sx in enumerate(D['sessions']):
        rws = ''
        for tid in ORD:
            t = T[tid]
            if t['session'] != sx or tid not in LESS: continue
            links = ''.join(f'<a href="{B}talks/{t["slug"]}/lessons/{a}/"><small>{lab}</small>{e(LESS[tid][a]["title"])}</a>' for a, lab, _ in AUD if a in LESS[tid])
            rws += f'<div class="lrow"><div class="lwho"><b>{e(t["speaker"])}</b><i>{e(t["title"])}</i></div><div class="llinks">{links}</div></div>'
        rows_l += f'<section class="sec" style="margin-top:{14 if i == 0 else 46}px"><h2>{e(SESS.get(sx, sx))}</h2>{rws}</section>'
    nl = sum(len([a for a, _, _ in AUD if a in LESS[x]]) for x in LESS)
    write(f'{B}lessons/', layout(f'Lessons for every talk · {LABEL} · {NAME}', f'{nl} ready-to-teach 30-minute lessons from the {LABEL}: one for adults, one for youth and one for children for every talk.',
        crumb(conf_c, 'Lessons') + head(e(LABEL), 'Lessons for every talk', f'{nl} ready-to-teach 30-minute lessons: one for adults, one for youth, and one for children ages 3–11 for each of the {len(ORD)} talks. Each is built on the speaker’s own words, the scriptures the talk cites, and any direct invitation the speaker gave.',
        '<p class="flag" style="margin-top:14px">Independent study aids, not official Church lessons. Every quotation is word for word from the official talks.</p>') + f'<div class="wrap" style="padding-bottom:70px">{rows_l}</div>', f'{B}lessons/', 'lessons'))
PRIV = (f'<p><b>{e(NAME)}</b> is an independent project and collects as little as it can.</p>'
    '<h2>Your six-month plan</h2><p>Your plan is saved in your own browser on your own device. It is not sent anywhere unless you choose <b>Create my private link</b>. If you do, the text of your plan (the invitations you chose, what you wrote, and your check-ins) is stored in this site’s database under a long random code, with no name, email address or account attached. Anyone who has your link can see and change that plan, so keep the link to yourself. To remove it, choose <b>Stop syncing and delete the online copy</b> on the plan page.</p>'
    '<h2>Email updates</h2><p>If you sign up for updates, your email address and optional first name are stored so that one email can be sent after each general conference. They are used for nothing else and are never sold or shared.</p>'
    '<h2>Visits and video</h2><p>The site counts page visits with a tool that uses no cookies and does not identify you. Talk videos load from YouTube only when you press play; YouTube’s own privacy terms then apply.</p>'
    '<h2>Children</h2><p>The site does not ask for or knowingly collect information from children. Lessons for children are written for the adults who teach them.</p>'
    '<h2>Independence</h2><p>This site is not affiliated with or endorsed by The Church of Jesus Christ of Latter-day Saints.</p>')
write('/privacy/', layout(f'Privacy · {NAME}', 'What this site stores and what it does not.', f'<div class="wrap" style="max-width:760px;padding-bottom:60px"><header class="ph"><div class="kick">Privacy</div><h1 style="max-width:18ch">What this site keeps, and what it doesn’t.</h1></header><div class="prose">{PRIV}</div></div>', '/privacy/'))
# ================= TALK PAGES =================
acts = {}
for a in D['actions']: acts.setdefault(a['unit'][:3], []).append(a)
bund_of_unit = {}
for i, b in BID.items():
    for it in b['items']: bund_of_unit[(it['unit'], it['q'])] = i
exs = {}
for t in THS:
    for x in t['examples']: exs.setdefault(x['unit'][:3], []).append((t, x))
for k, tid in enumerate(ORD):
    t = T[tid]; v = t.get('video') or {}; ta = acts.get(tid, [])
    if v.get('youtube'):
        video = f'<div class="video"><button class="vbtn" type="button" data-yt="{e(v["youtube"])}" aria-label="Play video: {e(t.get("title") or "talk")}, {e(t["speaker"])}"><img src="https://i.ytimg.com/vi/{e(v["youtube"])}/maxresdefault.jpg" alt="" loading="lazy" width="1280" height="720"><span class="play"></span></button></div>'
    else:
        video = '<div class="video soon"><span class="pi"></span><div><b>Video coming soon</b><span>The Church publishes each talk\'s video and text after conference. We\'ll add this talk\'s video here as soon as it\'s posted. Until then, find it on the Church\'s general conference page.</span></div></div>'
    vl = f'<div class="vlinks"><a class="btn" href="{e(v.get("church") or OFFICIAL)}" rel="noopener">' + ('Read the full talk on churchofjesuschrist.org' if v.get('church') else 'General conference on churchofjesuschrist.org') + '</a>' + (f'<a class="btn" href="https://www.youtube.com/watch?v={e(v["youtube"])}" rel="noopener">Watch on YouTube</a>' if v.get('youtube') else '') + '</div>'
    seen = set(); quotes = []
    for th, x in exs.get(tid, []):
        if x['unit'] not in seen: seen.add(x['unit']); quotes.append((th, x))
    inv = ''; done_b = set()
    for a in ta:
        bi = bund_of_unit.get((a['unit'], a['q'])); btn = addbtn(bi) if bi is not None and bi not in done_b else ''
        if bi is not None: done_b.add(bi)
        inv += f'<div class="qcard inv"><span class="tag">{e((BID[bi].get("label") or BID[bi]["title"]) if bi is not None else a["act"])}{via(a)}</span><p>“{qe(a["q"])}”</p><div class="who" style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap"><span>{a["unit"]}</span>{btn}</div></div>'
    pv, nx = (T[ORD[k - 1]] if k else None), (T[ORD[k + 1]] if k + 1 < len(ORD) else None)
    flag = '<span class="flag">Name as transcribed from the broadcast; spelling may differ.</span>' if t['uncertain'] else ''
    chips = ''.join(f'<a href="{B}themes/{TH[x]["slug"]}/">{e(TH[x]["short"])} <span>{n}</span></a>' for x, n in t['themes'])
    qhtml = ''.join(f'<div class="qcard"><span class="tag"><a href="{B}themes/{th["slug"]}/" style="color:inherit;text-decoration:none">{e(th["short"])}</a> · {e(x["code"])}</span><p>“{qe(x["q"])}”</p><div class="who">{x["unit"]}{via(x)}</div></div>' for th, x in quotes)
    scr = ''.join(f'<li>{e(r)}</li>' for r in t['scripture'])
    pn = (f'<a href="{B}talks/{pv["slug"]}/"><small>Previous talk</small>{e(pv["speaker"])}</a>' if pv else '<span></span>') + (f'<a href="{B}talks/{nx["slug"]}/" style="text-align:right"><small>Next talk</small>{e(nx["speaker"])}</a>' if nx else '')
    body = crumb(conf_c, f'<a href="{B}talks/">Talks</a>', e(t['speaker'])) + f'''<div class="wrap" style="max-width:900px;padding-bottom:70px"><header class="ph"><div class="kick">{e(t["session_name"])} · {e(LABEL)}</div><h1>{e(t["speaker"])}</h1>{f'<p class="ttl">{e(t["title"])}</p>' if t.get("title") else ''}<p class="sub2">{e(t["role"])}</p>{flag}</header>
{video}{vl}
<div class="sec" style="margin-top:30px"><h2>In brief</h2><p class="brief">{e(t.get("summary", ""))}</p></div>
<div class="pstats" style="margin-top:28px">{stat(f"{t['words']:,}", "words")}{stat(f"~{round(t['minutes'])}", "minutes")}{stat(t["christ"], "references to Christ per 1,000 words")}{stat(t["questions"], "questions asked")}{stat(len(ta), "direct invitation" + ("s" if len(ta) != 1 else ""))}</div>
<div class="sec"><h2>Themes in this talk</h2><div class="chips">{chips}</div><p class="note" style="margin-top:10px;font-size:14px">Number of coded passages from this talk in each theme.</p></div>
{f'<div class="sec"><h2>Direct invitations</h2><p class="note">Sentences where the speaker directly invited, urged, asked or pleaded with us to act, in the exact words.</p>{inv}</div>' if inv else ''}
{LES(t)}
{f'<div class="sec"><h2>Key passages</h2>{qhtml}</div>' if qhtml else ''}
{f'<div class="sec"><h2>Scripture referenced</h2><ul class="refs2">{scr}</ul><p class="note" style="font-size:14px">From the talk&#39;s official footnotes and in-text citations.</p></div>' if scr else ''}
<nav class="pn">{pn}</nav></div>'''
    write(f'{B}talks/{t["slug"]}/', layout((f'{t["title"]} · ' if t.get("title") else '') + f'{t["speaker"]} · {LABEL} · {NAME}', (first_sentence(t.get('summary')) or f'{t["speaker"]} at the {LABEL}.')[:300], body, f'{B}talks/{t["slug"]}/', 'talks'))
# ================= THEMES INDEX =================
sat = [s.startswith('Sat') for s in D['sessions']]; ns = sum(sat)
hm = f'<tr><th></th><th class="day" colspan="{ns}">Saturday</th><th class="day" colspan="{len(sat) - ns}">Sunday</th><th></th></tr><tr><th>Theme</th>' + ''.join(f'<th style="text-align:center">{e(s)}</th>' for s in D['sessions']) + '<th style="text-align:right">Larger day</th></tr>'
for t in THS:
    tot = sum(t['sessions']) or 1; sp = sum(v for v, f in zip(t['sessions'], sat) if f) / tot; f = max(sp, 1 - sp) >= .75
    cells = ''.join(f'<td class="c" style="background:color-mix(in srgb, var(--navy2) {round(4 + 56 * v / tot)}%, transparent);color:{"#fff" if v / tot > .45 else "var(--ink)"}">{v}</td>' for v in t['sessions'])
    hm += f'<tr class="{"f" if f else ""}"><td class="nm"><a href="{B}themes/{t["slug"]}/" style="color:inherit">{t["n"]}. {e(t["short"])}</a></td>{cells}<td style="text-align:right;{"font-weight:700" if f else "color:var(--muted)"}">{round(100 * max(sp, 1 - sp))}% {"Sat" if sp >= .5 else "Sun"}</td></tr>'
cards = ''.join(f'<a class="tc" href="{B}themes/{t["slug"]}/" style="padding:22px;gap:10px"><div style="display:flex;gap:14px;align-items:center"><span class="ic" style="grid-row:auto;flex:none">{ic(t["id"])}</span><span class="tname"><small>Theme {t["n"]}</small>{e(t["name"])}</span></div><p style="color:var(--muted);margin:0">{e(t["claim"])}</p><div class="trow" style="margin-top:auto"><i><b style="width:{100 * t["talks"] / len(ORD):.0f}%"></b></i>{t["talks"]} of {len(ORD)} talks · {(lambda n: f"{n} invitation" + ("" if n == 1 else "s"))(sum(1 for b in D["bundles"] if b.get("area") == t["id"]))}</div></a>' for t in THS)
write(f'{B}themes/', layout(f'Themes we noticed · {LABEL} · {NAME}', f'Ten themes we noticed across the {LABEL}, each backed by the speakers\' own words and linked to what we were asked to do.', crumb(conf_c, 'Themes') + head(e(LABEL), 'Ten themes we noticed', f'One careful way of organizing what was said, found by coding all {D["stats"]["units"]:,} passages and grouping the codes. They are lenses for pondering, not an official or final summary; the talks themselves are always the source.', f'<p style="margin-top:14px"><a class="more" href="{B}how-it-works/">How these themes were found →</a></p>') + f'<div class="wrap" style="padding-bottom:70px"><div class="tcards" style="grid-template-columns:repeat(auto-fill,minmax(320px,1fr))">{cards}</div><div class="sec"><h2>How the weekend unfolded</h2><p class="note">{e(D["arc"])} Each cell counts coded passages; darker means more of that theme fell in the session.</p><div class="heatwrap scroll"><table class="heat">{hm}</table></div></div></div>', f'{B}themes/', 'themes'))
# ================= THEME PAGES =================
for i, t in enumerate(THS):
    m = re.match(r"^(.*?):\s*'(.*)'\s*\((.*)\)$", t.get('anchor', ''))
    tal = sorted([(tid, dict(T[tid]['themes']).get(t['id'], 0)) for tid in ORD if dict(T[tid]['themes']).get(t['id'])], key=lambda x: -x[1])
    asks = [(j, b) for j, b in BID.items() if b.get('area') == t['id']]
    anchor = f'<div class="qcard"><p>“{qe(m.group(2))}”</p><div class="who"><a href="{B}talks/{T[m.group(3)[:3]]["slug"]}/">{e(T[m.group(3)[:3]]["short"])}</a> · {e(m.group(3))}</div></div>' if m else ''
    askh = ''.join(f'<div class="pickrow"><span class="t"><small class="lab">{e(b.get("label", ""))}</small>“{qe(b["title"])}”</span><span class="by">{asked(b)}</span>{addbtn(j)}</div>' for j, b in asks)
    talh = ''.join(f'<a href="{B}talks/{T[tid]["slug"]}/"><b>{e(T[tid]["speaker"])}</b><small>{e(T[tid]["role"])} · {e(T[tid]["session_name"])}</small><em>{n} passage{"s" if n > 1 else ""}</em></a>' for tid, n in tal)
    evid = ''.join(f'<div class="qcard"><span class="tag">{e(x["cat"])} · {e(x["code"])}</span><p>“{qe(x["q"])}”</p><div class="who"><a href="{B}talks/{T[x["unit"][:3]]["slug"]}/">{e(x["who"])}</a> · {x["unit"]}{via(x)}</div></div>' for x in t['examples'])
    sstats = ''.join(stat(v, e(SESS.get(s, s).replace(' session', ''))) for s, v in zip(D['sessions'], t['sessions']))
    pn = (f'<a href="{B}themes/{THS[i - 1]["slug"]}/"><small>Previous theme</small>{e(THS[i - 1]["name"])}</a>' if i else '<span></span>') + (f'<a href="{B}themes/{THS[i + 1]["slug"]}/" style="text-align:right"><small>Next theme</small>{e(THS[i + 1]["name"])}</a>' if i + 1 < len(THS) else '')
    body = crumb(conf_c, f'<a href="{B}themes/">Themes</a>', e(t['short'])) + f'''<div class="wrap" style="padding-bottom:70px"><header class="ph"><div class="kick">One of ten themes we noticed</div><div class="ph-row"><span class="ic">{ic(t["id"])}</span><h1>{e(t["name"])}</h1></div><p class="sub2">{e(t["claim"])}</p><span class="flag">A lens for pondering what was said, found through careful coding. Not an official summary; read the talks themselves for the full message. <a href="{B}how-it-works/">How it works</a></span></header>
<div class="pstats p6">{stat(t["talks"], f"of {len(ORD)} talks")}{stat(t["units"], "coded passages")}{sstats}</div>{anchor}
<div class="sec prose"><h2>What this theme is about</h2><p>{e(t["note"])}</p></div>
{f'<div class="sec"><h2>Direct invitations in this theme</h2>{askh}</div>' if askh else ''}
<div class="sec"><h2>Talks that carried this theme</h2><p class="note">Ordered by how many passages in each talk were coded to this theme.</p><div class="tl">{talh}</div></div>
<div class="sec"><h2>The evidence</h2><p class="note">Coded passages from the talks, quoted word for word from the official texts.</p>{evid}</div><nav class="pn">{pn}</nav></div>'''
    write(f'{B}themes/{t["slug"]}/', layout(f'{t["name"]} · {LABEL} · {NAME}', f'A theme we noticed in {t["talks"]} of {len(ORD)} talks at the {LABEL}: {t["claim"]}', body, f'{B}themes/{t["slug"]}/', 'themes'))
# ================= PLAN =================
y, mo = int(CONF[:4]), int(CONF[5:])
start = dt.date(y, mo, 1)
while start.weekday() != 6: start += dt.timedelta(days=1)          # conference Sunday (first Sunday of the month)
start += dt.timedelta(days=1)                                      # plan weeks begin the Monday after
mnames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MONTHS = [mnames[(mo - 1 + i) % 12] for i in range(6)]
WEEKS = []
for w in range(26):
    d = start + dt.timedelta(days=7 * w); mi = (d.year - y) * 12 + d.month - mo
    WEEKS.append({'i': w, 'm': max(0, min(5, mi)), 'label': f'{mnames[d.month - 1][:3]} {d.day}', 'd': d.isoformat()})
first_sun = start + dt.timedelta(days=6)
def pickrows(rows_):
    return ''.join(f'<div class="pickrow"><span class="t"><small class="lab">{e(b.get("label", ""))}' + (f' <span class="aud">{e(b["audience"].replace("for ", "For ").replace("repeated to", "Repeated to"))}</span>' if b.get('audience') else '') + f'</small>“{qe(b["title"])}”</span><span class="by">{asked(b)}</span>{addbtn(j)}' + (f'<details><summary>All {len(b["items"])} invitations like this</summary>' + ''.join(f'<p class="q">“{qe(it["q"])}”<cite>{e(it["who"])} · {it["unit"]}{via(it)}</cite></p>' for it in b['items']) + '</details>' if len(b['items']) > 1 else '') + '</div>' for j, b in rows_)
pick = ''
for g, lab in [('own', f"{D['president']}'s invitations"), ('repeated', 'His earlier invitations, repeated by other speakers')]:
    rows_ = [(j, b) for j, b in BID.items() if b['group'] == g]
    if rows_: pick += f'<div class="pickgrp"><h3>{e(lab)}</h3>{pickrows(rows_)}</div>'
for t in THS:
    rows_ = [(j, b) for j, b in BID.items() if b['group'] not in ('own', 'repeated') and b.get('area') == t['id']]
    if rows_: pick += f'<div class="pickgrp"><h3>{e(t["name"])}</h3>{pickrows(rows_)}</div>'
pbundles = {b['key']: {'title': b['title'].replace('“', '‘').replace('”', '’'), 'label': b.get('label', ''), 'speakers': b['speakers'], 'ideas': b.get('ideas', []), 'group_label': GROUPLAB.get(b['group'], '')} for j, b in BID.items()}
counsel = ''.join(f'<p class="q">“{qe(c["q"])}”<cite>{e(c["who"])} · {c["unit"]}</cite></p>' for c in D.get('counsel', []))
counsel_html = f'<details class="counsel"><summary>{e(D["president"])} also gave this direct counsel</summary><p class="note">These sentences are direct instructions rather than invitations, so they are not counted in the list above. They are his exact words.</p>{counsel}</details>' if counsel else ''
plan_body = crumb(conf_c, 'Your six-month plan') + f'''<div class="wrap" style="padding-bottom:70px"><header class="ph"><div class="kick">{e(LABEL)} · {MONTHS[0]} to {MONTHS[-1]}</div><h1>Your six-month plan</h1><p class="sub2">{len(D["bundles"])} direct invitations from this conference, in the speakers' own words, starting with President Oaks. Choose one to three, turn each into a specific commitment, and check in each week until the next conference.</p></header>
<div class="planhead"><div id="plansum"></div><div id="planacts" hidden><button class="tbtn" id="printplan">Print my plan</button><button class="tbtn" id="icsplan">Add weekly reminder to calendar</button><button class="tbtn" id="resetplan">Clear</button></div></div>
<div id="syncbox" class="syncbox" hidden></div>
<div id="planapp"><div id="thisweek"></div><div id="mine"></div><div id="notes" class="sec"></div>
<div class="sec" id="pickhead"><h2>Choose what to work on</h2><p class="science">Only direct invitations are listed: sentences where a speaker said “I invite,” “let us,” “please,” “I urge,” “I plead,” or the like. Each is shown in the speaker's exact words. Why turn one into a “when” and a “what”? People who decide exactly when and how they will act are much more likely to follow through than people who only intend to (Gollwitzer &amp; Sheeran, 2006).</p></div><div id="pick">{pick}{counsel_html}</div></div>
<p class="note" style="margin-top:30px">Your plan is saved in this browser on this device. It is stored online only if you choose to create a private link. <a href="/privacy/">Privacy</a></p></div>'''
write(f'{B}plan/', layout(f'Your six-month plan · {LABEL} · {NAME}', f'Every direct invitation from the {LABEL}, in the speakers\' own words, starting with President Oaks, turned into a personal six-month plan.', plan_body, f'{B}plan/', 'plan', {'bundles': pbundles, 'months': MONTHS, 'weeks': WEEKS, 'ics_start': first_sun.strftime('%Y%m%d')}))
# ================= NUMBERS =================
guess = ''.join(f'<button class="gcard" data-ans="{e(f[0])}" aria-pressed="false"><span class="num hid">? ? ?</span><span class="lbl">{e(f[1][:1].upper() + f[1][1:])}</span>' + (f'<span class="det" hidden>{e(f[2])}</span>' if len(f) > 2 else '') + '<span class="tap">Tap to reveal</span></button>' for f in D['facts'])
vmax = max(v[1] for v in D['vol']) or 1; lmax = max(l[1] for l in D['leaders']) or 1
vol = ''.join(f'<div class="bar"><span>{e(v)}</span><i><b style="width:{100 * n / vmax:.0f}%"></b></i><span class="v">{n}</span></div>' for v, n in D['vol'])
lead = ''.join(f'<div class="bar"><span>{e(n)}</span><i><b style="width:{100 * m / lmax:.0f}%"></b></i><span class="v">{m} ({q})</span></div>' for n, m, q in D['leaders'])
grp = '<tr><th>Group</th><th style="text-align:right">Talks</th><th style="text-align:right">Average words</th><th style="text-align:right">References to Christ per 1,000 words</th></tr>' + ''.join(f'<tr><td>{e(g[0])}</td><td style="text-align:right">{g[1]}</td><td style="text-align:right">{g[2]:,}</td><td style="text-align:right">{g[3]}</td></tr>' for g in D['groups'])
scrip = ''.join(f'<li>{e(s)}</li>' for s in D['scrip'])
num_body = crumb(conf_c, 'By the numbers') + head(e(LABEL), 'By the numbers', 'Counts from the official talk texts: who said what, how often, and which words carried the weekend.') + f'''<div class="wrap" style="padding-bottom:70px"><div class="stats">{"".join(stat(b, s) for b, s in STATS)}</div>
<div class="quiz" id="quiz" aria-live="polite" data-art="#qart"></div><template id="qart">{COMPASS}</template>
<h3 class="sub">Guess the number</h3><p class="note">Tap a card to reveal the answer.</p><div class="guess">{guess}</div>
<h3 class="sub">The words that carried the weekend</h3><p class="note">The 60 most-used content words. Bigger means said more often.</p><div class="cloud" id="cloud"></div>
<div class="two"><div class="panel"><h3>Scripture, by volume</h3>{vol}<ul class="plain">{scrip}</ul></div><div class="panel"><h3>Leaders most mentioned</h3>{lead}<p class="note" style="font-size:14px;margin:12px 0 0">Bar = talks mentioning the leader; parentheses = talks quoting them.</p></div></div>
<h3 class="sub">Who spoke, and for how long</h3><div class="panel scroll"><table>{grp}</table></div><p class="note" style="margin-top:12px">{e(D["groupnote"])}</p></div>'''
write(f'{B}numbers/', layout(f'By the numbers · {LABEL} · {NAME}', f'Word counts, the scriptures quoted, leaders cited, a word cloud, and a quiz from the {LABEL}.', num_body, f'{B}numbers/', 'numbers', {'quiz': D['quiz'], 'words': D['words']}))
# ================= HOW IT WORKS =================
RESEARCH = open(A('research_methods.html')).read().replace('__CHAIN__', f'{D["stats"]["units"]:,} passages → {D["stats"]["codes"]} codes → {D["stats"].get("categories", 26)} categories → {len(THS)} ') if os.path.exists(A('research_methods.html')) else ''
ex_pick = None
for t in THS:
    for x in t['examples']:
        for j, b in BID.items():
            if b.get('area') == t['id'] and b.get('ideas') and any(it['unit'] == x['unit'] and (it['q'][:40].lower() in x['q'].lower() or x['q'][:40].lower() in it['q'].lower()) for it in b['items']):
                ex_pick = (t, x, j, b); break
        if ex_pick: break
    if ex_pick: break
chain = ''
if ex_pick:
    t, x, j, b = ex_pick
    chain = ('<div class="chain">'
        f'<div class="lk"><span class="st">1 · The passage</span><p class="q2">“{qe(x["q"])}”</p><small><a href="{B}talks/{T[x["unit"][:3]]["slug"]}/">{e(x["who"])}</a> · passage {x["unit"]}</small></div>'
        f'<div class="lk"><span class="st">2 · The code</span><b>{e(x["code"])}</b><small>A short label for what the speaker is doing in this passage.</small></div>'
        f'<div class="lk"><span class="st">3 · The category</span><b>{e(x["cat"])}</b><small>Codes that belong together are grouped.</small></div>'
        f'<div class="lk"><span class="st">4 · The theme</span><b><a href="{B}themes/{t["slug"]}/">{e(t["name"])}</a></b><small>Categories that tell a bigger story become a theme.</small></div>'
        f'<div class="lk"><span class="st">5 · The direct invitation</span><b>“{qe(b["title"])}”</b><small>{asked(b)}.</small></div>'
        f'<div class="lk gold"><span class="st">6 · Your plan</span><b>“{e(b["ideas"][0])}”</b><small>One idea for making it specific.</small>{addbtn(j)}</div></div>')
nt = len({it['unit'][:3] for b in D['bundles'] for it in b['items']}); nq = sum(len(b['items']) for b in D['bundles'])
own_n = sum(1 for b in D['bundles'] if b['group'] == 'own')
def _inv_cell(t):
    items = [b for b in D['bundles'] if b.get('area') == t['id']]
    if not items: return '<span style="color:var(--muted)">No direct invitation; a theme to ponder</span>'
    return '<ul class="mini">' + ''.join(f'<li>{e(b.get("label") or b["title"])}</li>' for b in items) + '</ul>'
link_rows = ''.join(f'<tr><td><a href="{B}themes/{t["slug"]}/">{e(t["short"])}</a></td><td>{_inv_cell(t)}</td></tr>' for t in THS)
STEPS_HOW = [
    ('Read every line', f'All {len(ORD)} talks were divided into {D["stats"]["units"]:,} short passages, each holding a single idea, and every one was read.'),
    ("Tag what's said", f'Each passage got up to three short labels, called codes, naming what the speaker was doing: teaching a doctrine, telling a story, making a promise, extending an invitation. {D["stats"]["codes"]} codes in all.'),
    ('Group the tags', 'Codes that belong together were grouped into categories, and categories into ten broader themes. The themes came from the talks, not from a list decided in advance.'),
    ('Count with care', 'Every theme is backed by passages you can read. We count how many talks carried it, and in which sessions, so patterns rest on evidence rather than impressions.'),
    ('Find every direct invitation', 'Separately, every sentence where a speaker directly invited, urged, asked or pleaded with us to do something was collected, checked word for word, and linked to the theme it fits.'),
    ('Turn it into a plan', 'Those invitations become your six-month plan: choose a few, make them specific, and check in each week until the next conference.')]
CAN = ['Which ideas came up again and again, across many speakers.', 'How the weekend moved, such as trials on Saturday and treating each other well on Sunday.', 'Every place a speaker directly asked us to act, in their exact words.', 'Related passages from different talks, side by side.']
CANT = ['Tell you what the Lord wants you to focus on. That comes through prayer and the Spirit.', 'Speak for the speakers or for the Church. This is an independent study.', 'Replace the talks. Read, watch, and listen to them in full.', 'Give the only right grouping. Another careful reader might organize things differently; the themes are lenses for pondering, not the final word.']
asked_txt = (f'Only direct invitations count: sentences where a speaker says “I invite,” “let us,” “please,” “I urge,” “I plead,” “I ask you,” “I call upon,” or names what follows as an invitation. '
             f'Plain instructions (“Keep your covenants”), statements of truth, stories, “may we” wishes, and descriptions are not counted, however inspiring; counting them would make the list too long to act on. This conference yielded {len(D["bundles"])} direct invitations from {nt} talks, drawn from {nq} exact quotations, '
             f"beginning with President Oaks's {own_n}. Each is shown in the speaker's exact words. Invitations that are alike are grouped, and every speaker is named. President Oaks's direct instructions that are not phrased as invitations are listed separately at the end of the plan page.")
how_body = (crumb(conf_c, 'How it works') + head('How it works', 'How we read the talks', 'A simple explanation of qualitative coding, the careful, line-by-line reading researchers use to find patterns, and how those patterns connect to what we were asked to do.')
    + '<div class="wrap" style="padding-bottom:70px"><div class="steps">' + ''.join(f'<div class="step"><b>{e(a)}</b><span>{e(b_)}</span></div>' for a, b_ in STEPS_HOW) + '</div>'
    + RESEARCH + '<h3 class="sub">Follow one passage, start to finish</h3><p class="note">A real example from this conference, traced from the speaker\'s words to something you could do this week.</p>' + chain
    + '<div class="two" style="margin-top:46px"><div class="panel"><h3>What this can show you</h3><ul class="plain">' + ''.join(f'<li>{e(x)}</li>' for x in CAN) + '</ul></div>'
    + '<div class="panel"><h3>What it can\'t</h3><ul class="plain">' + ''.join(f'<li>{e(x)}</li>' for x in CANT) + '</ul></div></div>'
    + '<h3 class="sub">From themes to your next six months</h3><p class="note">Each theme, and the direct invitations that fit it. Pick a theme that speaks to you, then build your plan from its invitations.</p>'
    + f'<div class="scroll"><table class="mt">{link_rows}</table></div><p style="margin-top:18px"><a class="btn primary" href="{B}plan/">Build my six-month plan</a></p>'
    + f'<h3 class="sub">What counts as a direct invitation</h3><p style="max-width:72ch">{e(asked_txt)}</p>'
    + f'<h3 class="sub">Want the full details?</h3><p style="max-width:72ch">The complete research methodology covers the coding protocol, saturation, trustworthiness, theory mapping, limitations, and references, written for researchers.</p><p><a class="btn" href="{B}methodology/">Read the full methodology</a></p></div>')
write(f'{B}how-it-works/', layout(f'How it works · {LABEL} · {NAME}', 'A simple explanation of how the talks were read and coded, how the themes were found, and how they connect to what we were asked to do.', how_body, f'{B}how-it-works/', 'how'))
# ================= METHODOLOGY =================
M = D['method']; s_ = D['saturation']
W, Hh, x0, x1, top, lb, bt, bb = 900, 330, 40, 770, 24, 200, 232, 292
mc, mk, mn = max(r[2] for r in s_), max(r[3] for r in s_), max(r[1] for r in s_)
X = lambda i: x0 + (x1 - x0) * i / (len(s_) - 1); Yc = lambda v: lb - (lb - top) * v / mc; Yk = lambda v: lb - (lb - top) * v / mk; Yb = lambda v: bb - (bb - bt) * v / mn
g = f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="Cumulative codes and categories by talk, with new codes per talk"><line x1="{x0}" y1="{lb}" x2="{x1}" y2="{lb}" stroke="var(--rule)"/><line x1="{x0}" y1="{bb}" x2="{x1}" y2="{bb}" stroke="var(--rule)"/><text x="{x0}" y="{bt - 10}" font-size="12" fill="var(--muted)">New codes introduced by each talk (most: {mn})</text>'
for i, r in enumerate(s_):
    g += f'<rect x="{X(i) - 6:.1f}" y="{Yb(r[1]):.1f}" width="12" height="{bb - Yb(r[1]):.1f}" rx="2" fill="var(--navy2)"><title>{r[0]}: {r[1]} new codes</title></rect>'
    if i % 4 == 0 or i == len(s_) - 1: g += f'<text x="{X(i):.1f}" y="{Hh - 12}" font-size="12" text-anchor="middle" fill="var(--muted)">{r[0]}</text>'
g += '<polyline fill="none" stroke="var(--head)" stroke-width="2" points="' + ' '.join(f'{X(i):.1f},{Yc(r[2]):.1f}' for i, r in enumerate(s_)) + '"/><polyline fill="none" stroke="var(--gold)" stroke-width="3" points="' + ' '.join(f'{X(i):.1f},{Yk(r[3]):.1f}' for i, r in enumerate(s_)) + '"/>'
ki = next(i for i, r in enumerate(s_) if r[3] == mk)
g += f'<circle cx="{X(ki):.1f}" cy="{Yk(mk):.1f}" r="4.5" fill="var(--gold)"/><text x="{X(ki):.1f}" y="{Yk(mk) - 10:.1f}" font-size="12.5" text-anchor="middle" fill="var(--gold)">all {mk} categories by {s_[ki][0]}</text><text x="{x1 + 8}" y="{Yk(mk) + 4:.1f}" font-size="12.5" fill="var(--gold)">{mk} categories</text><text x="{x1 + 8}" y="{Yc(mc) + 18:.1f}" font-size="12.5" fill="var(--head)">{mc} codes</text></svg>'
tbl = lambda rows: '<div class="scroll"><table class="mt">' + ''.join(f'<tr><td>{e(a)}</td><td>{e(b_)}</td></tr>' for a, b_ in rows) + '</table></div>'
steps = ''.join(f'<div class="step"><b>{e(a)}</b><span>{e(b_)}</span></div>' for a, b_ in M['steps'])
cb = ''.join(f'<tr><td>{e(c["code"])}</td><td style="color:var(--muted)">{e(c["category"])}</td><td>{e(c["definition"])}</td><td style="color:var(--muted)">{e(c["include"])}</td><td style="color:var(--muted)">{e((c.get("exclude") or "—").replace("(-> ", "(see "))}</td></tr>' for c in D['codebook'])
th_rows = ''.join(f'<tr><td>{r[0]}</td><td>{e(r[1])}</td><td>{e(r[2])}</td><td>{e(r[3])}</td><td style="color:var(--muted)">{e(r[4])}</td></tr>' for r in D['theory'])
refs = ''.join(f'<li>{e(r)}</li>' for r in M['references']) + '<li>Gollwitzer, P. M., &amp; Sheeran, P. (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. Advances in Experimental Social Psychology, 38, 69–119. (Basis for the six-month plan design.)</li>'
meth = crumb(conf_c, f'<a href="{B}how-it-works/">How it works</a>', 'Full methodology') + head(e(LABEL), 'Full methodology', 'How a weekend of talks became the findings on this site, reported to the standard a peer-reviewed qualitative journal expects.') + f'''<div class="wrap" style="padding-bottom:70px">
<h3 class="sub" style="margin-top:0">The analytic process</h3><div class="steps">{steps}</div>
<h3 class="sub">Design at a glance</h3>{tbl(M["design"])}<h3 class="sub">Procedure in detail</h3>{tbl(M["paragraphs"])}
<h3 class="sub">Saturation</h3><p class="note">{e(M["saturation_note"])}</p><div class="satbox">{g}</div>
<h3 class="sub">A sample of the codebook</h3><p class="note">Six of the {D["stats"]["codes"]} codes. Every code carries a definition plus inclusion and exclusion rules, so a second coder can apply it the same way.</p><div class="scroll"><table class="cb mt"><tr><th>Code</th><th>Category</th><th>Definition</th><th>Include</th><th>Exclude</th></tr>{cb}</table></div>
<h3 class="sub">Trustworthiness</h3><p class="note">Lincoln and Guba's (1985) criteria for qualitative rigor, and the evidence for each in this study.</p>{tbl(M["trust"])}
<h3 class="sub">Theory, after the fact</h3><p class="note">{e(D["theorynote"])}</p><div class="scroll"><table class="mt"><tr><th>Theme</th><th>Category</th><th>Construct</th><th>Fit</th><th>Evidence</th></tr>{th_rows}</table></div>
<h3 class="sub">Talk summaries and plan ideas</h3><p style="max-width:72ch">Each talk's summary was written for this site from a full reading of its official text; any phrase in quotation marks was checked against the official text. The ideas offered on the plan page are suggestions written for this site to help make each invitation specific. They are not the speakers' words, and the invitations themselves are quoted exactly as published.</p>
<h3 class="sub">Reflexivity and the AI coder</h3><p style="max-width:72ch">{e(M["reflexivity"])}</p><h3 class="sub">Limitations</h3><ul class="plain">{"".join(f"<li>{e(l)}</li>" for l in M["limitations"])}</ul>
<h3 class="sub">Reporting standards</h3><p style="max-width:72ch">{e(M.get("standards", ""))}</p><h3 class="sub">References</h3><ul class="plain refs">{refs}</ul></div>'''
write(f'{B}methodology/', layout(f'Methodology · {LABEL} · {NAME}', f'How the {LABEL} was coded: two-cycle qualitative coding, saturation, trustworthiness, theory mapping, and limitations.', meth, f'{B}methodology/', 'how'))
# ================= ABOUT / ARCHIVE / 404 =================
about = open(A('about_template.html')).read(); ab = re.search(r'<div class="prose">(.*?)</div></div></main>', about, re.S).group(1).replace('href="/#signup"', 'href="#signup"')
write('/about/', layout(f'About · {NAME}', "Why this site exists: a neighbor's question, and a promise to remember what was said at general conference.", f'<div class="wrap" style="max-width:760px;padding-bottom:60px"><header class="ph"><div class="kick">About</div><h1 style="max-width:18ch">It started with a neighbor\'s question.</h1></header><div class="prose">{ab}</div></div>', '/about/'))
confs = sorted([d for d in os.listdir(out) if re.fullmatch(r'\d{4}-\d{2}', d)], reverse=True)
arch = ''.join(f'<a href="/{c}/"><b>{mnames[int(c[5:]) - 1]} {c[:4]} General Conference</b><small>Talks, themes, and the six-month plan</small><em>{"Latest" if j == 0 else ""}</em></a>' for j, c in enumerate(confs))
write('/conferences/', layout(f'All conferences · {NAME}', 'Every general conference studied on this site.', head('Archive', 'All conferences') + f'<div class="wrap" style="padding-bottom:60px"><div class="tl">{arch}</div></div>', '/conferences/'))
open(os.path.join(out, '404.html'), 'w').write(layout(f'Page not found · {NAME}', 'Page not found.', head('Page not found', "That page isn't here.") + f'<div class="wrap" style="padding-bottom:60px"><p>Try the <a href="{B}">latest conference</a>, the <a href="{B}talks/">talks</a>, or <a href="{B}plan/">your plan</a>.</p></div>', '/404.html'))
# ================= ASSETS =================
os.makedirs(os.path.join(out, 'assets'), exist_ok=True)
skip = '\n.skip{position:absolute;left:-999px;top:8px;background:var(--navy);color:var(--on-navy);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:8px}\n'
open(os.path.join(out, 'assets', 'site.css'), 'w').write((open(A('site_live.css')).read() + (open(A('site_v3.css')).read() if os.path.exists(A('site_v3.css')) else '')) if os.path.exists(A('site_live.css')) else re.sub(r'\n\s*', '\n', CSS + '\n' + open(A('subpage.css')).read() + '\n' + open(A('site_extra.css')).read() + skip))
open(os.path.join(out, 'assets', 'app.js'), 'w').write(open(A('app.js')).read())
try:
    og = f'<html><head><style>body{{margin:0;width:1200px;height:630px;display:grid;grid-template-columns:1.15fr .85fr;align-items:center;background:#fff;font-family:Georgia,serif;color:#13294b}}.t{{padding:0 40px 0 72px}}.k{{font:700 26px sans-serif;color:#b5852b}}h1{{font-size:68px;line-height:1.05;margin:14px 0 18px}}.b{{font-size:30px}}.b span{{color:#b5852b}}svg{{width:470px;height:auto}}</style></head><body><div class="t"><div class="k">General conference, studied</div><h1>What did they say in the last general conference?</h1><div class="b">{brand}</div></div>{ART}</body></html>'
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1200, 'height': 630}); pg.set_content(og); pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(out, 'og.png')); b.close()
except Exception as ex: print('share image skipped:', ex)
allp = sorted(set(['/'] + PAGES + [f'/{c}/' for c in confs]))
open(os.path.join(out, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n' + (f'Sitemap: {URL}/sitemap.xml\n' if URL else ''))
if URL: open(os.path.join(out, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{URL}{p}</loc></url>' for p in allp) + '</urlset>\n')
json.dump({"cleanUrls": True, "trailingSlash": True, "rewrites": [{"source": "/", "destination": B}],
           "redirects": [{"source": f"{B}list/", "destination": f"{B}plan/", "permanent": True}] + S.get("redirects", []),
           "headers": [{"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=3600, stale-while-revalidate=86400"}]},
                       {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}, {"key": "X-Frame-Options", "value": "SAMEORIGIN"}]}]},
          open(os.path.join(out, 'vercel.json'), 'w'), indent=1)
print(f'site written to {out}: {len(PAGES)} pages ({len(THS)} themes, {len(ORD)} talks)')
