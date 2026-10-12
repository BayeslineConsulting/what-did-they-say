#!/usr/bin/env python3
"""Deterministic metrics for one conference run.
Usage: python metrics.py segs.json out_metrics.json
segs.json comes from segment.py (talks + units). Lexicons live in ../references/."""
import json,re,sys,os
from collections import Counter,defaultdict
HERE=os.path.dirname(os.path.abspath(__file__))
segs=json.load(open(sys.argv[1]));out=sys.argv[2]
aliases=json.load(open(os.path.join(HERE,'..','references','aliases.json')))
books=json.load(open(os.path.join(HERE,'..','references','scripture_books.json')))
talks=segs['talks'];units=segs['units']
META=json.load(open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])),'meta.json'))) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])),'meta.json')) else {}
def ts2s(t):
    s=0
    for x in t.split(':'): s=s*60+float(x)
    return s
WORD=re.compile(r"[A-Za-z][A-Za-z'’-]*")
byt=defaultdict(list)
for u in units: byt[u['talk_id']].append(u)
CHRIST=re.compile(r"\b(Jesus Christ|Jesus|Christ|Savio[u]?r|Redeemer|Messiah|Jehovah|Son of God|Lord)\b")
INVITE=re.compile(r"\b(I invite|I urge|I plead|I encourage|let us|I ask you)\b",re.I)
PROMISE=re.compile(r"\bI (promise|bless you)\b",re.I)
STORY=re.compile(r"\b(I remember|years ago|when I was|my (wife|husband|mother|father|son|daughter|grandparents?|friend))\b",re.I)
tm=[]
for t in talks:
    us=byt[t['talk_id']];text=' '.join(u['text'] for u in us);w=len(WORD.findall(text))
    # duration: talk start to last block start + 60 s (blocks are ~1-2 min); flagged as estimate
    dur=META[t['talk_id']]['seconds']/60 if META.get(t['talk_id'],{}).get('seconds') else max(1,(ts2s(us[-1]['timestamp'])+60-ts2s(t['start']))/60)
    c=len(CHRIST.findall(text))
    tm.append(dict(talk_id=t['talk_id'],session=t['session'],speaker=t['speaker'],role=t.get('role',''),
        words=w,minutes_est=round(dur,1),wpm_est=round(w/dur),christ_refs=c,christ_per_1000=round(1000*c/max(w,1),1),
        invitations=len(INVITE.findall(text)),promises=len(PROMISE.findall(text)),
        story_markers=len(STORY.findall(text)),questions=text.count('?')))
vol_terms={'Old Testament':r'Old Testament','New Testament':r'New Testament','Book of Mormon':r'Book of Mormon','Doctrine and Covenants':r'Doctrine and Covenants|D&C','Pearl of Great Price':r'Pearl of Great Price'}
NUM=r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty)"
scrip=[];volm=Counter()
for u in units:
    tx=u['text']
    for v,pat in vol_terms.items(): volm[v]+=len(re.findall(pat,tx))
    for b in books:
        for m in re.finditer(r"\b(?:(?:1|2|3|4|First|Second|Third|Fourth) )?"+re.escape(b['name'])+r"\b",tx):
            if b['name']=='Mormon' and re.search(r'Book of\s*$',tx[:m.start()]): continue
            after=tx[m.end():m.end()+30]
            explicit=bool(re.match(r"\s*(?:chapter\s+)?"+NUM+r"\b",after,re.I))
            kind='explicit-reference' if explicit else ('figure-or-book' if b['person_name'] else 'book-mention')
            scrip.append(dict(unit_id=u['unit_id'],talk_id=u['talk_id'],book=b['name'],volume=b['volume'],kind=kind,
                context=tx[max(0,m.start()-50):m.end()+50]))
lead=[]
VERB=r".{0,90}\b(said|taught|stated|declared|reminded|counseled|asked|explained|warned|cautioned|wrote|invited|has said|pointed out)"
for u in units:
    for canon,pats in aliases.items():
        hit=next((p for p in pats if re.search(p,u['text'])),None)
        if hit: lead.append(dict(unit_id=u['unit_id'],talk_id=u['talk_id'],leader=canon,quoted=bool(re.search('(?:'+hit+')'+VERB,u['text']))))
STOP=set("the a an and of to in that is it we our us you your i he his him they their them for with as be are was this on by not but have has will can all or so from at my me do if what there when which who would were been one also more these those its it's into than then just about".split())
def grams(text,n=3):
    w=[x.lower().strip("'’") for x in WORD.findall(text)]
    return {' '.join(w[i:i+n]) for i in range(len(w)-n+1) if sum(x not in STOP for x in w[i:i+n])>=2}
gt=defaultdict(set)
for t in talks:
    for g in grams(' '.join(u['text'] for u in byt[t['talk_id']])): gt[g].add(t['talk_id'])
phr=sorted(([g,len(s),sorted(s)] for g,s in gt.items() if len(s)>=3),key=lambda x:-x[1])[:60]
CW=Counter()
for t in talks:
    CW.update({x.lower() for x in WORD.findall(' '.join(u['text'] for u in byt[t['talk_id']])) if len(x)>3 and x.lower() not in STOP})

# ---- word frequencies for the word cloud (content words, plurals merged)
FSTOP=set("""a about above after again against all also am an and any are as at be because been before being below between both but by can could did do does doing down during each few for from further had has have having he her here hers herself him himself his how i if in into is it its itself just me more most my myself no nor not now of off on once only or other our ours ourselves out over own same she should so some such than that the their theirs them themselves then there these they this those through to too under until up very was we were what when where which while who whom why will with would you your yours yourself yourselves us one even may might must shall let lets like also every many much yet though thus therefore ever never always often still another way things thing something someone said says say tell told came come comes coming go goes going went get gets got make makes made take takes took see saw seen know knew known think thought want wanted need needs felt feel feels became become becomes give gives gave given well really time times day days years year first second third two three four five today new back ask asked use used help upon amen brother sister dear yes oh okay mr elder president ye unto thee thy hath thou""".split())
def norm(w):
    w=w.lower().replace('’',"'");w=re.sub(r"'s$","",w)
    if w.endswith('ies') and len(w)>5: w=w[:-3]+'y'
    elif w.endswith('s') and not w.endswith(('ss','us','is')) and len(w)>4: w=w[:-1]
    return w
ALLTXT=' '.join(u['text'] for u in units)
WF=Counter(n for n in (norm(w) for w in re.findall(r"[A-Za-z][A-Za-z'’]+",ALLTXT) if len(w)>2 and w.lower() not in FSTOP) if n not in FSTOP)
cnt=lambda p:len(re.findall(p,ALLTXT,re.I))
FUN={'"Jesus Christ"':cnt(r'\bJesus Christ\b'),'"Christ" (any)':cnt(r'\bChrist\b'),'love/loved/loves/loving':cnt(r'\blov(e|ed|es|ing)\b'),
 'covenant(s)':cnt(r'\bcovenants?\b'),'temple(s)':cnt(r'\btemples?\b'),'"brothers and sisters"':cnt(r'brothers and sisters'),
 'Holy Ghost':cnt(r'Holy Ghost'),'pray/prayer forms':cnt(r'\bpray(er|ers|ed|ing|s)?\b'),'repent forms':cnt(r'\brepent\w*'),
 'joy forms':cnt(r'\bjoy\w*'),'peace forms':cnt(r'\bpeace\w*'),'phone or social media':cnt(r'phone|social media'),'question marks':ALLTXT.count('?'),
 'years mentioned':sorted(set(re.findall(r'\b(1[89]\d\d|20\d\d)\b',ALLTXT)))}

json.dump(dict(word_freq=WF.most_common(150),fun_counts=FUN,talk_metrics=tm,scripture=scrip,volume_mentions=volm,leaders=lead,phrases=phr,top_words=CW.most_common(80)),
    open(out,'w'),indent=1,ensure_ascii=False)
print(f"talks {len(tm)} | words {sum(x['words'] for x in tm)} | scripture hits {len(scrip)} | leader mentions {len(lead)} | phrases {len(phr)}")
