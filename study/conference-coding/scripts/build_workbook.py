#!/usr/bin/env python3
"""Build the coding workbook for one conference run.

Usage: python build_workbook.py RUN_DIR MASTER_CODEBOOK.json HISTORY_IN.json|none OUT_DIR

RUN_DIR holds: segs.json, assign.txt, themes.json, memos.json, scripture_refs.txt, metrics.json,
               and optionally new_codes.json (codes created this run, same fields as the master).
Writes to OUT_DIR: conference-<id>-coding.xlsx, master_codebook.json (updated), history.json (updated).
Every count in the workbook is a live formula over Codes_Long / Units / Scripture."""
import json,re,sys,os,statistics as st
from collections import defaultdict,Counter
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
RUN,MCB,HIN,OUT=sys.argv[1:5]
J=lambda f:json.load(open(os.path.join(RUN,f)))
segs=J('segs.json');TH=J('themes.json');MEMO=J('memos.json');MET=J('metrics.json')
CONF=segs['conference'];master=json.load(open(MCB))
new=J('new_codes.json') if os.path.exists(os.path.join(RUN,'new_codes.json')) else {}
# ---- codebook merge (hybrid rule: master + flagged new codes)
codes=dict(master['codes']);cats=dict(master['categories'])
for k,v in new.get('codes',{}).items():
    if k in codes: sys.exit(f'new code key {k} already in master')
    codes[k]=dict(v,added_run=CONF)
for c,v in new.get('categories',{}).items(): cats.setdefault(c,v)
A={}
for ln in open(os.path.join(RUN,'assign.txt')):
    ln=ln.strip()
    if not ln or ln.startswith('#'): continue
    rng,*keys=ln.split();m=re.match(r'(T\d\d)\.(\d\d)(?:-(\d\d))?$',rng)
    if not m: sys.exit('bad range '+ln)
    for k in keys:
        if k not in codes: sys.exit(f'unknown code key {k} in: {ln} (add it to new_codes.json)')
    if len(keys)>3: sys.exit('more than 3 codes: '+ln)
    for n in range(int(m.group(2)),int(m.group(3) or m.group(2))+1):
        uid=f'{m.group(1)}.{n:02d}'
        if uid in A: sys.exit('unit coded twice: '+uid)
        A[uid]=keys
U={u['unit_id']:u for u in segs['units']};missing=[u for u in U if u not in A]
if missing: sys.exit(f'{len(missing)} units uncoded, e.g. {missing[:5]}')
used=set(k for v in A.values() for k in v)
for k in used: codes[k]['last_seen_run']=CONF
cat2th={c:t['id'] for t in TH['themes'] for c in t['categories']};cat2th[TH['rhetoric_category']]='RM'
for k in used:
    if codes[k]['category'] not in cat2th: sys.exit(f"category {codes[k]['category']} not assigned to a theme in themes.json")
th=lambda k:cat2th[codes[k]['category']]
TALKS=segs['talks'];TIDS=[t['talk_id'] for t in TALKS];THIDS=[t['id'] for t in TH['themes']];N=len(U);NT=len(TALKS)
SES=list(dict.fromkeys(t['session'] for t in TALKS))
F=Font(name='Arial',size=10);B=Font(name='Arial',size=10,bold=True);HF=Font(name='Arial',size=10,bold=True,color='FFFFFF')
HFILL=PatternFill('solid',fgColor='1F3864');Y=PatternFill('solid',fgColor='FFFF00')
wb=Workbook()
def sheet(name,headers,widths):
    ws=wb.create_sheet(name)
    for i,h in enumerate(headers,1):
        c=ws.cell(1,i,h);c.font=HF;c.fill=HFILL;c.alignment=Alignment(wrap_text=True,vertical='center')
    for i,w in enumerate(widths,1): ws.column_dimensions[L(i)].width=w
    ws.freeze_panes='B2';return ws
def put(ws,r,vals,wrap=False,c0=1):
    for i,v in enumerate(vals,c0):
        c=ws.cell(r,i,v);c.font=F
        if wrap:c.alignment=Alignment(wrap_text=True,vertical='top')
def f(ws,r,c,formula,fmt=None):
    x=ws.cell(r,c,formula);x.font=F
    if fmt:x.number_format=fmt
# Codes_Long
cl=sheet('Codes_Long',['unit_id','talk_id','session','code','category','theme'],[10,8,9,34,30,8]);r=2
for u in segs['units']:
    for k in A[u['unit_id']]: put(cl,r,[u['unit_id'],u['talk_id'],u['session'],codes[k]['code'],codes[k]['category'],th(k)]);r+=1
NL=r-1;R=lambda c:f"Codes_Long!${c}$2:${c}${NL}"
# Units
us=sheet('Units',['unit_id','talk_id','session','timestamp','speaker','text','code_1','code_2','code_3']+THIDS+['primary_theme'],[9,7,8,11,24,80,24,24,24]+[6]*len(THIDS)+[10])
spk={t['talk_id']:t['speaker'] for t in TALKS};TC0=10
for i,u in enumerate(segs['units'],2):
    ks=[codes[k]['code'] for k in A[u['unit_id']]]+['']*3
    put(us,i,[u['unit_id'],u['talk_id'],u['session'],u['timestamp'],spk[u['talk_id']],u['text']]+ks[:3])
    for j,t in enumerate(THIDS): f(us,i,TC0+j,f'=IF(COUNTIFS({R("A")},$A{i},{R("F")},"{t}")>0,1,0)')
    nr=[th(k) for k in A[u['unit_id']] if th(k)!='RM'];put(us,i,[nr[0] if nr else 'RM'],c0=TC0+len(THIDS))
NU=N+1;ucol=lambda j:L(TC0+j)
# Theme_x_Talk
LT=L(1+NT);tt=sheet('Theme_x_Talk',['theme']+TIDS+['talks present','units'],[8]+[5]*NT+[9,8])
for r,t in enumerate(THIDS,2):
    put(tt,r,[t])
    for c,tid in enumerate(TIDS,2): f(tt,r,c,f'=SUMIFS(Units!{ucol(r-2)}$2:{ucol(r-2)}${NU},Units!$B$2:$B${NU},{L(c)}$1)')
    f(tt,r,NT+2,f'=COUNTIF(B{r}:{LT}{r},">0")');f(tt,r,NT+3,f'=SUM(B{r}:{LT}{r})')
NTH=len(THIDS)+1
# Theme_x_Session
tx=sheet('Theme_x_Session',['theme']+[s+' units' for s in SES]+['total']+[s+' share' for s in SES],[8]+[11]*(2*len(SES)+1))
for r,t in enumerate(THIDS,2):
    put(tx,r,[t])
    for j,s in enumerate(SES): f(tx,r,2+j,f'=SUMIFS(Units!{ucol(r-2)}$2:{ucol(r-2)}${NU},Units!$C$2:$C${NU},"{s}")')
    tc=2+len(SES);f(tx,r,tc,f'=SUM(B{r}:{L(tc-1)}{r})')
    for j in range(len(SES)): f(tx,r,tc+1+j,f'=IF(${L(tc)}{r}=0,0,{L(2+j)}{r}/${L(tc)}{r})','0%')
# Talks
ts=sheet('Talks',['talk_id','session','start','speaker','calling','name confidence','file','units','themes present','primary theme','words','Christ refs / 1,000 words','scripture refs'],[7,8,12,38,30,22,40,7,9,10,8,10,9])
for i,t in enumerate(TALKS,2):
    tm=next(x for x in MET['talk_metrics'] if x['talk_id']==t['talk_id'])
    put(ts,i,[t['talk_id'],t['session'],t['start'],t['speaker'],t['role'],t['name_confidence'],t['file']])
    f(ts,i,8,f'=COUNTIF(Units!$B$2:$B${NU},A{i})');col=L(i)
    f(ts,i,9,f'=COUNTIF(Theme_x_Talk!{col}$2:{col}${NTH},">0")')
    f(ts,i,10,f'=INDEX(Theme_x_Talk!$A$2:$A${NTH},MATCH(MAX(Theme_x_Talk!{col}$2:{col}${NTH}),Theme_x_Talk!{col}$2:{col}${NTH},0))')
    put(ts,i,[tm['words'],tm['christ_per_1000']],c0=11);f(ts,i,13,f'=COUNTIF(Scripture!$A:$A,A{i})')
# Codebook
keys=sorted(codes,key=lambda k:(codes[k]['category'],codes[k]['code']))
cb=sheet('Codebook',['code','key','method','definition','include','exclude','category','theme (this run)','status','added run','last seen','units','talks'],[30,5,9,46,36,36,26,8,13,9,9,7,7])
LC=L(1+NT)
for i,k in enumerate(keys,2):
    v=codes[k];cat=v['category']
    put(cb,i,[v['code'],k,v['method'],v['definition'],v['include'],v['exclude'],cat,cat2th.get(cat,'(unused)'),None,v['added_run'],v.get('last_seen_run','')],wrap=True)
    f(cb,i,12,f'=COUNTIF({R("D")},A{i})');f(cb,i,13,f'=COUNTIF(Code_x_Talk!B{i}:{LC}{i},">0")')
    f(cb,i,9,f'=IF(J{i}="{CONF}","new this run",IF(K{i}<>"{CONF}","dormant",IF(M{i}>=2,"active",IF(L{i}>=3,"talk-specific","provisional"))))')
cx=sheet('Code_x_Talk',['code']+TIDS+['total'],[30]+[5]*NT+[7])
for i,k in enumerate(keys,2):
    put(cx,i,[codes[k]['code']])
    for c in range(2,NT+2): f(cx,i,c,f'=COUNTIFS({R("D")},$A{i},{R("B")},{L(c)}$1)')
    f(cx,i,NT+2,f'=SUM(B{i}:{LC}{i})')
# Categories
ca=sheet('Categories',['category','theme (this run)','codes','code occurrences','theory construct','theory source','justification'],[28,9,60,10,34,30,60])
bycat=defaultdict(list)
for k in keys: bycat[codes[k]['category']].append(codes[k]['code'])
for i,c in enumerate(sorted(cats),2):
    put(ca,i,[c,cat2th.get(c,'(unused)'),'; '.join(bycat[c]),None,cats[c].get('theory_construct',''),cats[c].get('theory_source',''),cats[c].get('justification','')],wrap=True)
    f(ca,i,4,f'=COUNTIF({R("E")},A{i})')
# Themes
tm_=sheet('Themes',['theme','name','claim','categories','talks (of %d)'%NT,'units','share of units','sessions present','anchor excerpt'],[7,32,60,40,9,8,9,9,40])
for i,t in enumerate(TH['themes'],2):
    put(tm_,i,[t['id'],t['name'],t['claim'],'; '.join(t['categories'])],wrap=True)
    f(tm_,i,5,f'=INDEX(Theme_x_Talk!${L(NT+2)}$2:${L(NT+2)}${NTH},MATCH(A{i},Theme_x_Talk!$A$2:$A${NTH},0))')
    f(tm_,i,6,f'=SUM(Units!{ucol(i-2)}$2:{ucol(i-2)}${NU})');f(tm_,i,7,f'=F{i}/{N}','0.0%')
    f(tm_,i,8,f'=COUNTIF(Theme_x_Session!B{i}:{L(1+len(SES))}{i},">0")');put(tm_,i,[t['anchor']],wrap=True,c0=9)
# Scripture
VOLMAP=J('scripture_vol.json') if os.path.exists(os.path.join(RUN,'scripture_vol.json')) else {}
SR=[]
for ln in open(os.path.join(RUN,'scripture_refs.txt')):
    if '|' not in ln: continue
    t,refs=ln.strip().split('|')
    for ref in [x.strip() for x in refs.split(';') if x.strip()]:
        book=re.sub(r'\s+\d[\d:–\-, ]*$','',ref);vol=VOLMAP.get(t+'|'+ref,'Old Testament')
        SR.append([t,ref,book,re.sub(r':.*','',ref),vol])
sc=sheet('Scripture',['talk_id','reference','book','chapter','volume'],[8,26,20,20,22])
for i,row in enumerate(SR,2): put(sc,i,row)
VOLS=['Old Testament','New Testament','Book of Mormon','Doctrine and Covenants','Pearl of Great Price'];NS=len(SR)+1
sv=sheet('Scripture_Summary',['volume','references','share','talks citing'],[24,11,9,11])
for i,v in enumerate(VOLS,2):
    put(sv,i,[v]);f(sv,i,2,f'=COUNTIF(Scripture!$E$2:$E${NS},A{i})');f(sv,i,3,f'=B{i}/SUM($B$2:$B$6)','0%')
    f(sv,i,4,f'=SUMPRODUCT((Scripture!$E$2:$E${NS}=A{i})/COUNTIFS(Scripture!$A$2:$A${NS},Scripture!$A$2:$A${NS},Scripture!$E$2:$E${NS},Scripture!$E$2:$E${NS}))','0')
chap=Counter(r[3] for r in SR);ct=defaultdict(set)
for r in SR: ct[r[3]].add(r[0])
put(sv,9,['Chapters cited in 2+ talks','talks','',''])
for c in sv[9]: c.font=B
for j,(c,_) in enumerate(sorted(((c,len(s)) for c,s in ct.items() if len(s)>1),key=lambda x:-x[1]),10):
    put(sv,j,[c]);f(sv,j,2,f'=SUMPRODUCT((Scripture!$D$2:$D${NS}=A{j})/COUNTIFS(Scripture!$A$2:$A${NS},Scripture!$A$2:$A${NS},Scripture!$D$2:$D${NS},Scripture!$D$2:$D${NS}))','0')
# Leaders
ld=sheet('Leaders',['talk_id','unit_id','leader','quoted (verb nearby)'],[8,9,26,12])
for i,x in enumerate(MET['leaders'],2): put(ld,i,[x['talk_id'],x['unit_id'],x['leader'],'yes' if x['quoted'] else 'no'])
NLd=len(MET['leaders'])+1;names=sorted({x['leader'] for x in MET['leaders']})
ls=sheet('Leaders_Summary',['leader','talks mentioning','talks quoting'],[26,12,12])
for i,n in enumerate(names,2):
    put(ls,i,[n])
    f(ls,i,2,f'=SUMPRODUCT((Leaders!$C$2:$C${NLd}=A{i})/COUNTIFS(Leaders!$A$2:$A${NLd},Leaders!$A$2:$A${NLd},Leaders!$C$2:$C${NLd},Leaders!$C$2:$C${NLd}))','0')
    f(ls,i,3,f'=SUMPRODUCT((Leaders!$C$2:$C${NLd}=A{i})*(Leaders!$D$2:$D${NLd}="yes")/COUNTIFS(Leaders!$A$2:$A${NLd},Leaders!$A$2:$A${NLd},Leaders!$C$2:$C${NLd},Leaders!$C$2:$C${NLd},Leaders!$D$2:$D${NLd},Leaders!$D$2:$D${NLd}))','0')
# Talk metrics + phrases
mk=['talk_id','session','speaker','words','minutes_est','christ_refs','christ_per_1000','invitations','promises','story_markers','questions']
tmet=sheet('Talk_Metrics',mk,[7,8,34,8,9,9,10,9,8,9,9])
for i,x in enumerate(MET['talk_metrics'],2): put(tmet,i,[x[k] for k in mk])
r=len(MET['talk_metrics'])+3;put(tmet,r,['TOTAL','','']);f(tmet,r,4,f'=SUM(D2:D{r-2})')
put(tmet,r+1,['note','','minutes_est = talk start to last transcript block + 60 s; approximate. Christ refs count Jesus, Christ, Savior, Redeemer, Messiah, Jehovah, Son of God, Lord.'])
ph=sheet('Phrases',['three-word phrase','talks using it','talk ids'],[30,10,80])
for i,p in enumerate(MET['phrases'],2): put(ph,i,[p[0],p[1],', '.join(p[2])])
# Memos, log, reliability
mm=sheet('Memos',['talk_id','speaker','memo'],[7,36,120])
for i,t in enumerate(TALKS,2): put(mm,i,[t['talk_id'],t['speaker'],MEMO.get(t['talk_id'],'')],wrap=True)
lg=sheet('Codebook_Log',['run','action','code','rationale'],[8,12,34,100])
logs=new.get('log',[])+[[CONF,'added',codes[k]['code'],'New code this run (hybrid rule).'] for k in new.get('codes',{})]
for i,l in enumerate(logs,2): put(lg,i,l,wrap=True)
rel_t=TH.get('reliability_talk',TIDS[min(4,NT-1)])
rl=sheet('Reliability',['unit_id','text','second rater: primary theme (fill)','Claude primary theme','agree?'],[9,90,22,16,8])
samp=[u for u in segs['units'] if u['talk_id']==rel_t]
for i,u in enumerate(samp,2):
    put(rl,i,[u['unit_id'],u['text']]);rl.cell(i,3).fill=Y
    nr=[th(k) for k in A[u['unit_id']] if th(k)!='RM'];put(rl,i,[nr[0] if nr else 'RM'],c0=4)
    f(rl,i,5,f'=IF(C{i}="","",IF(C{i}=D{i},1,0))')
last=len(samp)+1;dv=DataValidation(type='list',formula1='"'+','.join(THIDS+['RM'])+'"',allow_blank=True);rl.add_data_validation(dv);dv.add(f'C2:C{last}')
rl.column_dimensions['D'].hidden=True;r=last+2
put(rl,r,['Code column C blind (D is hidden), then unhide D.']);rl.cell(r,1).font=B
r+=2;put(rl,r,['Rated units']);f(rl,r,2,f'=COUNTA(C2:C{last})')
put(rl,r+1,['% agreement']);f(rl,r+1,2,f'=IF(B{r}=0,"",SUM(E2:E{last})/B{r})','0.0%')
k0=r+5;opts=THIDS+['RM']
for j,o in enumerate(opts):
    rr=k0+j;put(rl,rr,[o]);f(rl,rr,2,f'=IF($B${r}=0,0,COUNTIF($C$2:$C${last},A{rr})/$B${r})')
    f(rl,rr,3,f'=IF($B${r}=0,0,COUNTIFS($D$2:$D${last},A{rr},$C$2:$C${last},"<>")/$B${r})');f(rl,rr,4,f'=B{rr}*C{rr}')
put(rl,r+2,['Expected (pe)']);f(rl,r+2,2,f'=SUM(D{k0}:D{k0+len(opts)-1})')
put(rl,r+3,["Cohen's kappa"]);f(rl,r+3,2,f'=IF(OR(B{r}=0,B{r+2}=1),"",(B{r+1}-B{r+2})/(1-B{r+2}))','0.00')

# Actions, examples, word frequencies, fun facts
if os.path.exists(os.path.join(RUN,'actions.json')):
    ac=sheet('Actions',['theme','what to do','talk','unit','speaker','in their words (verbatim)'],[8,46,7,9,26,70])
    for i,(t,act,u,q) in enumerate(json.load(open(os.path.join(RUN,'actions.json'))),2): put(ac,i,[t,act,u[:3],u,spk[u[:3]],q],wrap=True)
if os.path.exists(os.path.join(RUN,'examples.txt')):
    te=sheet('Theme_Examples',['theme','category','code','unit','speaker','excerpt (verbatim)'],[8,24,26,9,26,70]);r=2
    for ln in open(os.path.join(RUN,'examples.txt')):
        if not ln.strip(): continue
        t,k,u,q=ln.rstrip('\n').split('|',3);put(te,r,[t,codes[k]['category'],codes[k]['code'],u,spk[u[:3]],q],wrap=True);r+=1
wf=sheet('Word_Frequencies',['word (plurals merged)','uses','rank'],[24,8,7])
for i,(w,n) in enumerate(MET.get('word_freq',[]),2): put(wf,i,[w,n]);f(wf,i,3,f'=RANK(B{i},$B$2:$B${len(MET.get("word_freq",[]))+1})')
ff=sheet('Fun_Facts',['count of','value'],[30,60])
for i,(k,v) in enumerate(MET.get('fun_counts',{}).items(),2): put(ff,i,[k,', '.join(v) if isinstance(v,list) else v])

# ---- run summary + history
thu=defaultdict(set);tht=defaultdict(set);catu=Counter()
for uid,ks in A.items():
    for k in ks: thu[th(k)].add(uid);tht[th(k)].add(U[uid]['talk_id']);catu[codes[k]['category']]+=1
tw=[x for x in MET['talk_metrics']]
summary=dict(conference=CONF,label=segs.get('label',CONF),talks=NT,units=N,words=sum(x['words'] for x in tw),
    median_christ_per_1000=st.median(x['christ_per_1000'] for x in tw if x['words']>=500),
    themes=[dict(id=t['id'],name=t['name'],talks=len(tht[t['id']]),units=len(thu[t['id']])) for t in TH['themes']],
    category_share={c:round(n/sum(catu.values()),4) for c,n in catu.items()},
    scripture_volumes=dict(Counter(r[4] for r in SR)),
    leaders_mentioned={n:len({x['talk_id'] for x in MET['leaders'] if x['leader']==n}) for n in names},
    new_codes=len(new.get('codes',{})))
hist=json.load(open(HIN)) if HIN!='none' and os.path.exists(HIN) else []
hist=[h for h in hist if h['conference']!=CONF]+[summary];hist.sort(key=lambda h:h['conference'])
hs=sheet('History',['conference','talks','units','words','median Christ / 1,000','themes (talks)','OT','NT','BoM','D&C','PGP','new codes'],[11,7,7,8,10,80,6,6,6,6,6,8])
for i,h in enumerate(hist,2):
    sv_=h['scripture_volumes']
    put(hs,i,[h['conference'],h['talks'],h['units'],h['words'],h['median_christ_per_1000'],'; '.join(f"{t['name']} ({t['talks']})" for t in h['themes'])]+[sv_.get(v,0) for v in VOLS]+[h['new_codes']],wrap=True)
hj=wb.create_sheet('History_JSON');hj['A1']=json.dumps(hist);hj.sheet_state='hidden'
# README first
rd=wb.active;rd.title='README';rd.column_dimensions['A'].width=110
lines=[f"{segs.get('label',CONF)} General Conference — coding workbook (run {CONF})","",
f"{NT} addresses, {N} meaning units, {NL-1} code applications, {len(SR)} scripture references, {summary['words']:,} words.",
"Method: Saldaña first-cycle coding (Initial, In Vivo, Process) against a master codebook; new codes flagged 'new this run'; axial categories; selective themes as claims; theory mapped afterward.",
"Status: new this run · active (≥2 talks) · talk-specific (1 talk, ≥3 units) · provisional (1 talk, ≤2 units) · dormant (in master, not used this run).",
"Scripture references are taken from the official footnotes and in-text citations (distinct references per talk); see the Scripture sheet. Leader mentions and Talk_Metrics are produced by script.",
"History holds one row per conference run; History_JSON (hidden) is what the next run reads.","",
"Source: the official talk texts published by the Church (units = published paragraphs; section headings, footnotes and picture captions excluded). Caveats: single coder; descriptive counts only."]
for i,t in enumerate(lines,1):
    c=rd.cell(i,1,t);c.font=B if i==1 else F;c.alignment=Alignment(wrap_text=True)
order=['README','Themes','Actions','Theme_Examples','Talks','Units','Codebook','Categories','Theme_x_Talk','Theme_x_Session','Code_x_Talk','Codes_Long','Scripture','Scripture_Summary','Leaders','Leaders_Summary','Talk_Metrics','Phrases','Word_Frequencies','Fun_Facts','History','History_JSON','Codebook_Log','Memos','Reliability']
wb._sheets=[wb[s] for s in order]
os.makedirs(OUT,exist_ok=True)
xl=os.path.join(OUT,f'conference-{CONF}-coding.xlsx');wb.save(xl)
master_out=dict(version=CONF,codes=codes,categories=cats)
json.dump(master_out,open(os.path.join(OUT,'master_codebook.json'),'w'),indent=1,ensure_ascii=False)
json.dump(hist,open(os.path.join(OUT,'history.json'),'w'),indent=1,ensure_ascii=False)
json.dump(summary,open(os.path.join(RUN,'run_summary.json'),'w'),indent=1,ensure_ascii=False)
print('wrote',xl,'| code rows',NL-1,'| scripture',len(SR),'| history runs',len(hist))
