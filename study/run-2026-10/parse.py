import json,re,sys
from bs4 import BeautifulSoup
RAW='/home/claude/fetch/raw/out/'
slugs=[s.strip() for s in '''12gong 13runia 14causse 15sikahema 16hathaway 17soares 18douglas 19christofferson
21renlund 22farnes 23chigbundu 24giuffra 25morgan 26fale 27kearon 28dunn 29eyring 210rasband
41eyring 42chibota 43andersen 44fantone 45dube 46cook 47kyungu 48schmeil 49oaks
51uchtdorf 52munoz-spannaus 53villanueva 54bednar 55lebethoa 56sinclair 57stevenson 58reid 59gilbert 510oaks'''.split()]
SESS={'1':'Sat AM','2':'Sat PM','4':'Sun AM','5':'Sun PM'}
talks=[];units=[];meta={}
def clean(el):
    for s in el.select('a.note-ref, sup.marker'): s.decompose()
    t=el.get_text(' ',strip=False)
    t=t.replace('\xa0',' ');t=re.sub(r'\s+',' ',t).strip()
    t=re.sub(r'\s+([,.;:!?”’)\]])',r'\1',t);t=re.sub(r'([“‘(\[])\s+',r'\1',t)
    return t
for n,s in enumerate(slugs,1):
    d=json.load(open(RAW+s+'.json'));tid=f'T{n:02d}'
    soup=BeautifulSoup(d['content']['body'],'lxml')
    v=soup.find('video')
    title=clean(soup.find('h1'));an=soup.select_one('.author-name');ar=soup.select_one('.author-role');k=soup.select_one('.kicker')
    author=re.sub(r'^By\s+','',clean(an)) if an else '';role=clean(ar) if ar else ''
    bb=soup.select_one('.body-block');k_=0;heads=[]
    for fg in bb.find_all('figure'): fg.decompose()
    for el in bb.find_all(['p','h2','h3','li','div'],recursive=True):
        if el.name in('h2','h3'): heads.append((k_+1,clean(el)));continue
        cl=el.get('class') or []
        if el.name=='div' and 'poetry' not in cl: continue
        if el.name!='div' and el.find_parent(class_='poetry'): continue
        if el.name=='p' and el.find_parent('li'): continue
        if el.name=='li' and el.find_parent('footer'): continue
        t=clean(el)
        if not t: continue
        if len(t)<25 and k_>0:
            units[-1]['text']+=' '+t;continue
        k_+=1;units.append(dict(unit_id=f'{tid}.{k_:02d}',talk_id=tid,session=SESS[s[0]],timestamp='',text=t,pid=el.get('data-aid','')))
    fns=[]
    for key,f in (d['content'].get('footnotes') or {}).items():
        fns.append(dict(marker=f['marker'],pid=f.get('pid',''),text=clean(BeautifulSoup(f['text'],'lxml')),refs=[(r.get('type',''),r.get('text','').replace('\xa0',' '),r.get('href','').replace('&amp;','&')) for r in f.get('referenceUris',[])]))
    dur=int(v['data-duration'])/1000 if v else None
    talks.append(dict(talk_id=tid,session=SESS[s[0]],file=s,start='',speaker=author,role=role,name_confidence='official',units=k_))
    meta[tid]=dict(slug=s,title=title,author=author,role=role,kicker=clean(k) if k else '',seconds=dur,duration=v['data-duration-string'] if v else '',
        video_desc=v.get('data-video-description','') if v else '',poster=v.get('poster','') if v else '',url=f'https://www.churchofjesuschrist.org/study/general-conference/2026/10/{s}?lang=eng',heads=heads,footnotes=fns,tags=sorted({e.name for e in bb.find_all(True)}))
json.dump(dict(conference='2026-10',talks=talks,units=units),open('segs.json','w'),ensure_ascii=False,indent=0)
json.dump(meta,open('meta.json','w'),ensure_ascii=False,indent=1)
import collections
W=re.compile(r"[A-Za-z][A-Za-z'’-]*")
tot=0
for t in talks:
    us=[u for u in units if u['talk_id']==t['talk_id']];w=sum(len(W.findall(u['text'])) for u in us);tot+=w
    m=meta[t['talk_id']]
    print(t['talk_id'],t['session'],f"{t['units']:3d}u {w:5d}w {m['duration']:>6} fn{len(m['footnotes']):3d}",t['speaker'],'|',t['role'],'|',m['title'],'| last:',us[-1]['text'][-45:])
print(len(talks),len(units),tot, collections.Counter(x for m in meta.values() for x in m['tags']))
