#!/usr/bin/env python3
"""Validate lessons_out/Txx.json. Usage: python3 validate_lesson.py T05   (exit 0 = pass)"""
import json,re,sys,os
R=os.path.dirname(os.path.abspath(__file__))+'/';tid=sys.argv[1]
segs=json.load(open(R+'segs.json'));U={u['unit_id']:u['text'] for u in segs['units']}
bank=json.load(open(R+'quote_bank.json'))
allrefs=[x for l in open(R+'scripture_refs.txt') if '|' in l for x in l.strip().split('|')[1].split(';') if x]
TR={'“':'"','”':'"','‘':"'",'’':"'",'—':'-','–':'-','\xa0':' ','…':'...'}
n=lambda s:re.sub(r'\s+',' ',''.join(TR.get(c,c) for c in s)).strip()
chap=lambda r:re.sub(r'[:,].*$','',n(r).replace('Doctrine and Covenants','D&C')).strip()
CH={chap(r) for r in allrefs}
SONGS=set(json.load(open(R+'songs.json')))
TALK=n(' '.join(v for k,v in U.items() if k.startswith(tid)));ALL=n(' '.join(U.values()))
errs=[]
try: L=json.load(open(R+f'lessons_out/{tid}.json'))
except Exception as e: print('FAIL cannot read json:',e);sys.exit(1)
def span(u):
    t,k=u.split('.');nx=f'{t}.{int(k)+1:02d}';return n(U.get(u,'')+' '+U.get(nx,''))
STR=lambda x,p,lo=1,hi=10**6: errs.append(f'{p}: must be a non-empty string') if not isinstance(x,str) or not (lo<=len(x.strip())<=hi) else None
for aud in ('adults','youth','children'):
    if aud not in L: errs.append(f'missing lesson: {aud}');continue
    l=L[aud];p=aud
    for f in ('title','big_idea','objective'): STR(l.get(f),f'{p}.{f}',5,260)
    for f,lo,hi in (('prepare',2,6),('takeaways',3,3),('act',2,4)):
        v=l.get(f)
        if not isinstance(v,list) or not (lo<=len(v)<=hi) or not all(isinstance(x,str) and x.strip() for x in v): errs.append(f'{p}.{f}: need {lo}-{hi} strings')
    sg=l.get('segments')
    if not isinstance(sg,list) or not (4<=len(sg)<=8): errs.append(f'{p}.segments: need 4-8 segments')
    else:
        tot=0
        for i,s in enumerate(sg):
            if not isinstance(s.get('minutes'),int) or s['minutes']<1: errs.append(f'{p}.segments[{i}].minutes must be a positive integer')
            else: tot+=s['minutes']
            STR(s.get('name'),f'{p}.segments[{i}].name',2,80)
            if not isinstance(s.get('steps'),list) or not (1<=len(s['steps'])<=6) or not all(isinstance(x,str) and x.strip() for x in s['steps']): errs.append(f'{p}.segments[{i}].steps: need 1-6 strings')
            if 'questions' in s and (not isinstance(s['questions'],list) or not all(isinstance(x,str) for x in s['questions'])): errs.append(f'{p}.segments[{i}].questions must be a list of strings')
            if aud=='children' and isinstance(s.get('minutes'),int) and s['minutes']>7: errs.append(f'{p}.segments[{i}]: children segments must be 7 minutes or less')
        if tot!=30: errs.append(f'{p}.segments minutes total {tot}, must be exactly 30')
    kq=l.get('key_quotes',[])
    if not (2<=len(kq)<=4): errs.append(f'{p}.key_quotes: need 2-4')
    for q in kq:
        u=q.get('unit','')
        if not u.startswith(tid+'.') or u not in U: errs.append(f'{p}.key_quotes: unit {u} is not a paragraph of this talk');continue
        if n(q.get('text','')) not in span(u): errs.append(f'{p}.key_quotes: not verbatim in {u}: {q.get("text","")[:80]}')
        if len(q.get('text','').split())>70: errs.append(f'{p}.key_quotes: over 70 words: {q["text"][:50]}')
    for q in l.get('invitations',[]):
        u=q.get('unit','')
        if not u.startswith(tid+'.') or u not in U or n(q.get('text','')) not in span(u): errs.append(f'{p}.invitations: not verbatim in {u}: {q.get("text","")[:80]}')
    aq=l.get('aligned_quotes',[])
    if not (1<=len(aq)<=2): errs.append(f'{p}.aligned_quotes: need 1-2')
    for q in aq:
        u=q.get('unit','');src=q.get('source','')
        STR(q.get('speaker'),f'{p}.aligned_quotes.speaker',3,80)
        if src=='this conference':
            if u.startswith(tid+'.'): errs.append(f'{p}.aligned_quotes: {u} is this talk; "this conference" quotes must come from another talk')
            elif not any(b['unit']==u and n(q.get('text',''))==n(b['text']) for b in bank): errs.append(f'{p}.aligned_quotes: must copy a quote_bank entry exactly (unit+text): {u} {q.get("text","")[:60]}')
        elif src=='quoted in this talk':
            if not u.startswith(tid+'.') or u not in U or n(q.get('text','')) not in span(u): errs.append(f'{p}.aligned_quotes: not verbatim in {u}: {q.get("text","")[:80]}')
        else: errs.append(f'{p}.aligned_quotes.source must be "this conference" or "quoted in this talk"')
    sc=l.get('scriptures',[])
    if not (2<=len(sc)<=4): errs.append(f'{p}.scriptures: need 2-4')
    for s in sc:
        if chap(s.get('ref','')) not in CH: errs.append(f'{p}.scriptures: "{s.get("ref")}" chapter was not cited anywhere in this conference; use a reference from the provided list')
        STR(s.get('use'),f'{p}.scriptures.use',5,300)
    for s in l.get('music',[]):
        if s not in SONGS: errs.append(f'{p}.music: "{s}" is not in the approved song list (songs.json); remove or replace')
    ad=l.get('adapt')
    if aud=='children':
        if not isinstance(ad,dict) or not all(isinstance(ad.get(k),str) and len(ad[k])>20 for k in ('younger','older')): errs.append('children.adapt must be {"younger": "...", "older": "..."}')
    elif not isinstance(ad,list) or not (1<=len(ad)<=3): errs.append(f'{p}.adapt: need a list of 1-3 strings')
    # any other double-quoted span of 6+ words anywhere in the lesson must be verbatim from the conference text
    blob=json.dumps({k:v for k,v in l.items() if k not in('key_quotes','aligned_quotes','invitations')},ensure_ascii=False)
    for q in re.findall(r'[“]([^”]{25,400})[”]',blob)+re.findall(r'\\"([^"\\]{25,400})\\"',blob):
        qq=n(q).strip(' .,;!?')
        if len(qq.split())>=6 and qq not in ALL and qq.lower() not in ALL.lower(): errs.append(f'{p}: quoted text is not verbatim from the conference talks (reword without quotation marks or quote exactly): {q[:80]}')
print('PASS' if not errs else 'FAIL\n- '+'\n- '.join(errs));sys.exit(1 if errs else 0)
