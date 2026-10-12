#!/usr/bin/env python3
"""Build the interactive conference report page (single self-contained HTML).
Usage: python build_report_page.py RUN_DIR MASTER_CODEBOOK.json HISTORY.json OUT.html
Reads from RUN_DIR: segs.json, assign.txt, themes.json, actions.json, examples.txt, names.json,
metrics.json, scripture_refs.txt, report_content.json (authored notes, fun facts, theory, method).
Every number on the page is computed here or comes from report_content.json; nothing is typed into the template."""
import json,re,sys,os
from collections import defaultdict,Counter
RUN,MCB,HIST,OUT=sys.argv[1:5];J=lambda f:json.load(open(os.path.join(RUN,f)))
segs=J('segs.json');TH=J('themes.json')['themes'];names=J('names.json');RC=J('report_content.json');MET=J('metrics.json')
M=json.load(open(MCB))['codes'];hist=json.load(open(HIST))
A={}
for ln in open(os.path.join(RUN,'assign.txt')):
    if not ln.strip(): continue
    rng,*ks=ln.split();m=re.match(r'(T\d\d)\.(\d\d)(?:-(\d\d))?',rng)
    for n in range(int(m.group(2)),int(m.group(3) or m.group(2))+1): A[f'{m.group(1)}.{n:02d}']=ks
U={u['unit_id']:u for u in segs['units']};cat2={c:t['id'] for t in TH for c in t['categories']}
SES=list(dict.fromkeys(t['session'] for t in segs['talks']))
tth=defaultdict(Counter)
themes=[]
for t in TH:
    units=set();talks=set();ses=Counter();codes=defaultdict(set)
    for uid,ks in A.items():
        hit=[k for k in ks if cat2.get(M[k]['category'])==t['id']]
        if hit:
            units.add(uid);talks.add(U[uid]['talk_id']);ses[U[uid]['session']]+=1;tth[U[uid]['talk_id']][t['id']]+=1
            for k in hit: codes[M[k]['code']].add(U[uid]['talk_id'])
    ex=[]
    for ln in open(os.path.join(RUN,'examples.txt')):
        if not ln.strip(): continue
        th,k,u,q=ln.rstrip('\n').split('|',3)
        if th==t['id']: ex.append(dict(cf=M[k]['category'],cat=M[k]['category'][4:],code=M[k]['code'],q=q,who=names[u[:3]],unit=u))
    ex.sort(key=lambda e:(t['categories'].index(e['cf']),e['unit']))
    themes.append(dict(id=t['id'],n=int(t['id'][2:]),name=t['name'],short=RC.get('short',{}).get(t['id'],t['name'].split(':')[0]),claim=t['claim'],anchor=t['anchor'],talks=len(talks),units=len(units),
        sessions=[ses.get(s,0) for s in SES],lead=[[c,len(v)] for c,v in sorted(codes.items(),key=lambda x:-len(x[1]))[:4]],
        note=RC['notes'].get(t['id'],''),examples=ex))
cap={'christ':'Christ','jesus':'Jesus','god':'God','lord':'Lord','savior':'Savior','father':'Father','holy':'Holy','spirit':'Spirit','book':'Book','mormon':'Mormon','ghost':'Ghost','son':'Son','heavenly':'Heavenly','church':'Church'}
wf=[[cap.get(w,w),n] for w,n in MET['word_freq'][:60]]
acts=[dict(theme=t,act=a,unit=u,who=names[u[:3]],q=q) for t,a,u,q in J('actions.json')]
QUOTING=json.load(open(os.path.join(RUN,'quoting.json'))) if os.path.exists(os.path.join(RUN,'quoting.json')) else {}
BU=J('bundles.json');IDEAS=json.load(open(os.path.join(RUN,'plan_ideas.json'))) if os.path.exists(os.path.join(RUN,'plan_ideas.json')) else {}
def rb(b,group):
    its=[dict(unit=u,q=q,role=r,who=names[u[:3]],session=U[u]['session']) for u,q,r in b['items']]
    for i in its:
        if i['unit'] in QUOTING: i['via']=QUOTING[i['unit']]
    return dict(group=group,key=b.get('key',b['title']),label=b.get('label',''),ideas=IDEAS.get(b.get('key',b['title']),IDEAS.get(b['title'],[])),title=b['title'],area=b.get('area',''),audience=b.get('audience',''),items=its,speakers=list(dict.fromkeys(i['who'] for i in its)))
others=BU['others']
bundles=[rb(b,'own') for b in BU['oaks_own']]+[rb(b,'repeated') for b in BU['oaks_repeated']]+[rb(b,'multi' if len({names[u[:3]] for u,q,r in b['items']})>1 and not b.get('audience') else ('audience' if b.get('audience') else 'single')) for b in others]
VOLMAP=json.load(open(os.path.join(RUN,'scripture_vol.json'))) if os.path.exists(os.path.join(RUN,'scripture_vol.json')) else {}
vol=Counter()
for ln in open(os.path.join(RUN,'scripture_refs.txt')):
    if '|' not in ln: continue
    for r in ln.strip().split('|')[1].split(';'):
        r=r.strip()
        if not r: continue
        v=VOLMAP.get(ln.split('|')[0]+'|'+r,'Old Testament')
        vol[v]+=1
words=sum(x['words'] for x in MET['talk_metrics'])
import unicodedata
def slug(x): return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().lower())).strip('-')
for t in themes: t['slug']=slug(t['short'])
sref={}
for ln in open(os.path.join(RUN,'scripture_refs.txt')):
    if '|' in ln: k,v=ln.strip().split('|',1);sref[k]=[r.strip() for r in v.split(';') if r.strip()]
SESN={'Sat AM':'Saturday morning session','Sat PM':'Saturday afternoon session','Sun AM':'Sunday morning session','Sun PM':'Sunday afternoon session'}
OPT=lambda f,d:json.load(open(os.path.join(RUN,f))) if os.path.exists(os.path.join(RUN,f)) else d
TMETA=OPT('talkmeta.json',{});SUMM=OPT('summaries.json',{});LINKS=OPT('links.json',{});IDEAS=OPT('plan_ideas.json',{})
TM={x['talk_id']:x for x in MET['talk_metrics']};clean=lambda n:re.sub(r"\s*\((?:as transcribed|uncertain)[^)]*\)",'',n).replace("'",'').strip();cnt=Counter(clean(t['speaker']) for t in segs['talks']);talks=[]
for t in segs['talks']:
    m=TM[t['talk_id']];sp=clean(t['speaker']);sl=slug(sp)+('-'+slug(SESN.get(t['session'],t['session']).replace(' session','')) if cnt[sp]>1 else '')
    tmx=TMETA.get(t['talk_id'],{});sl=tmx.get('slug',sl)
    talks.append(dict(id=t['talk_id'],slug=sl,title=tmx.get('title',''),speaker=sp+('*' if '*' in names[t['talk_id']] else ''),short=names[t['talk_id']],role=tmx.get('role',t['role']),session=t['session'],session_name=SESN.get(t['session'],t['session']),
      uncertain='*' in names[t['talk_id']],words=m['words'],minutes=m['minutes_est'],christ=m['christ_per_1000'],questions=m['questions'],
      summary=SUMM.get(t['talk_id'],''),video=LINKS.get(t['talk_id'],{}),units=sum(1 for u in U if u.startswith(t['talk_id']+'.')),themes=[[k,v] for k,v in tth[t['talk_id']].most_common()],scripture=sref.get(t['talk_id'],[])))
sat=[];seen=set();cats=set()
for t in [x['talk_id'] for x in segs['talks']]:
    ks={k for u,v in A.items() if u.startswith(t+'.') for k in v};new=ks-seen;seen|=ks;cats|={M[k]['category'] for k in ks}
    sat.append([t,len(new),len(seen),len(cats)])
cbs=[dict(code=M[k]['code'],method=M[k]['method'],definition=M[k]['definition'],include=M[k]['include'],exclude=M[k]['exclude'],category=M[k]['category'][4:]) for k in RC.get('codebook_sample',[]) if k in M]
LESSONS={}
for t in segs['talks']:
    f=os.path.join(RUN,'lessons_out',t['talk_id']+'.json')
    if os.path.exists(f): LESSONS[t['talk_id']]=json.load(open(f))
for e in themes:
    for x in e['examples']:
        if x['unit'] in QUOTING: x['via']=QUOTING[x['unit']]
for a in acts:
    if a['unit'] in QUOTING: a['via']=QUOTING[a['unit']]
COUNSEL=[dict(unit=u,q=q,who=names[u[:3]]) for u,q in BU.get('counsel',[])]
DATA=dict(lessons=LESSONS,counsel=COUNSEL,quoting=QUOTING,talks=talks,sessnames=SESN,site=RC.get('site',{}),five=RC.get('five_min',[]),quiz=RC.get('quiz',[]),icons=RC.get('icons',{}),saturation=sat,codebook=cbs,conf=segs['conference'],label=RC['label'],subtitle=RC['subtitle'],lead=RC['lead'],arc=RC['arc'],sessions=SES,
  stats=dict(talks=len(segs['talks']),speakers=len({t['speaker'] for t in segs['talks']}),words=words,units=len(U),apps=sum(len(v) for v in A.values()),
             codes=len({k for v in A.values() for k in v}),categories=len({M[k]['category'] for v in A.values() for k in v}),actions=len(acts),scripture=sum(vol.values())),
  themes=themes,actions=acts,bundles=bundles,president=BU['president'],words=wf,facts=RC['fun_facts'],groups=RC['speaker_groups'],groupnote=RC['speaker_note'],
  vol=[[v,vol.get(v,0)] for v in ['New Testament','Book of Mormon','Doctrine and Covenants','Old Testament','Pearl of Great Price']],
  scrip=RC['scripture_highlights'],leaders=RC['leaders'],theory=RC['theory'],theorynote=RC['theory_note'],method=RC['method'],history=hist)
html=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets','report_template.html')).read()
json.dump(DATA,open(OUT.rsplit('.',1)[0]+'.json','w'),ensure_ascii=False)
open(OUT,'w').write(html.replace('__DATA__',json.dumps(DATA,ensure_ascii=False).replace('</','<\\/')))
print('wrote',OUT,'| themes',len(themes),'| actions',len(acts),'| examples',sum(len(t['examples']) for t in themes),'| history',len(hist))
