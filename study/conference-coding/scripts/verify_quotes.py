#!/usr/bin/env python3
"""Verify that every quotation is verbatim in the transcript.
Usage:
  python verify_quotes.py RUN_DIR            checks actions.json and examples.txt (quote in unit; example unit carries the code)
  python verify_quotes.py RUN_DIR doc.md     also checks every "quoted" span of 4+ words in an exported doc
Bracketed editorial corrections like "segment [sacrament]" are ignored when matching. Exit code 1 on any failure."""
import json,re,sys,os
RUN=sys.argv[1];segs=json.load(open(os.path.join(RUN,'segs.json')));U={u['unit_id']:u['text'] for u in segs['units']}
ALL=' '.join(U.values());bad=[]
def span(u):
    """Unit text plus the next unit, so a quote may run across a transcript segment break."""
    t,n=u.split('.');nx=f'{t}.{int(n)+1:02d}'
    return re.sub(r'\s+',' ',U.get(u,'')+' '+U.get(nx,''))
strip=lambda q:re.sub(r'\s*\[[^\]]*\]','',q).replace('\\','').strip()
A={}
for ln in open(os.path.join(RUN,'assign.txt')):
    if not ln.strip(): continue
    rng,*ks=ln.split();m=re.match(r'(T\d\d)\.(\d\d)(?:-(\d\d))?',rng)
    for n in range(int(m.group(2)),int(m.group(3) or m.group(2))+1): A[f'{m.group(1)}.{n:02d}']=ks
if os.path.exists(os.path.join(RUN,'actions.json')):
    for th,act,u,q in json.load(open(os.path.join(RUN,'actions.json'))):
        if q not in span(u) and strip(q) not in span(u): bad.append(('action',u,q))
if os.path.exists(os.path.join(RUN,'bundles.json')):
    BU=json.load(open(os.path.join(RUN,'bundles.json')));covered=set()
    for b in BU['oaks_own']+BU['oaks_repeated']+BU['others']:
        for u,q,r in b['items']:
            covered.add(u)
            if q not in span(u) and strip(q) not in span(u): bad.append(('bundle',u,q))
    if os.path.exists(os.path.join(RUN,'actions.json')):
        for th,act,u,q in json.load(open(os.path.join(RUN,'actions.json'))):
            if u not in covered: bad.append(('action-not-in-any-bundle',u,act))
if os.path.exists(os.path.join(RUN,'examples.txt')):
    for ln in open(os.path.join(RUN,'examples.txt')):
        if not ln.strip(): continue
        th,k,u,q=ln.rstrip('\n').split('|',3)
        if q not in U.get(u,'') and strip(q) not in U.get(u,''): bad.append(('example-quote',u,q))
        if k not in A.get(u,[]): bad.append(('example-code',u,k))
if len(sys.argv)>2:
    md=open(sys.argv[2]).read();n=0
    for q in re.findall(r'"([^"]{12,400})"',md):
        q2=strip(q).rstrip('.,').replace('...','…')
        parts=[p.strip(' .,') for p in q2.split('…') if len(p.split())>=4]
        for p in parts:
            n+=1
            if p not in ALL: bad.append(('doc',p[:80]))
    print('doc quotes checked:',n)
print('FAILURES:' if bad else 'all quotes verified', *bad, sep='\n')
sys.exit(1 if bad else 0)
