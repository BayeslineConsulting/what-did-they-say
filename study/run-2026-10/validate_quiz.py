import json,sys,re,os
RUN=os.path.dirname(os.path.abspath(__file__))
def norm(s):
    s=s.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('—','-').replace('–','-').replace(' ',' ').replace('…','...')
    return re.sub(r'\s+',' ',s).strip().lower()
def quotes(s): return re.findall(r'[“"]([^“”"]+)[”"]',s)
BAN=['all of the above','none of the above','both a and','a and b','a and c','b and c','neither of']
def numeric(o): return bool(re.fullmatch(r'[\s\d,.$%]+(\s*(years?|days?|miles?|times|people|percent|months?|weeks?|hours?|minutes?|talks|temples|members))?',o.strip().lower())) or o.strip().lower() in ('one','two','three','four','five','six','seven','eight','nine','ten','twelve')
def check_q(q,n,units,alltext,errs,tag,need_unit=True):
    for k in ('q','options','a','why'):
        if k not in q: errs.append(f'{tag}: missing {k}'); return
    if len(q['options'])!=n: errs.append(f'{tag}: needs {n} options, has {len(q["options"])}')
    if not isinstance(q['a'],int) or not 0<=q['a']<len(q['options']): errs.append(f'{tag}: bad answer index'); return
    if len(set(norm(o) for o in q['options']))!=len(q['options']): errs.append(f'{tag}: duplicate options')
    if len(q['q'])>220: errs.append(f'{tag}: question over 220 chars')
    if len(q['why'])>320 or len(q['why'])<25: errs.append(f'{tag}: why must be 25-320 chars ({len(q["why"])})')
    for o in q['options']:
        if len(o)>110: errs.append(f'{tag}: option over 110 chars')
        if any(b in norm(o) for b in BAN): errs.append(f'{tag}: banned option wording "{o}"')
    L=[len(o) for o in q['options']];c=L[q['a']];rest=[x for i,x in enumerate(L) if i!=q['a']]
    if c>max(rest)*1.35 and c-max(rest)>12: errs.append(f'{tag}: correct option is noticeably the longest; even the lengths')
    u=q.get('unit')
    if need_unit or u:
        if u not in units: errs.append(f'{tag}: unit {u} not found')
    for s in [q['q'],q['why']]+q['options']:
        for qt in quotes(s):
            if len(qt.split())>4:
                t=norm(qt).rstrip('.,;:!?')
                t=re.sub(r'\s*\.\.\.\s*',' ... ',t)
                parts=[p.strip(' .,;:') for p in t.split(' ... ') if p.strip()]
                if not all(p in alltext for p in parts): errs.append(f'{tag}: quotation not found word for word: "{qt[:70]}"')
if __name__=='__main__':
    tid=sys.argv[1];errs=[]
    T=json.load(open(f'{RUN}/lessons_in/{tid}.json'))
    units={p['unit']:p['text'] for p in T['paragraphs'] if 'unit' in p};alltext=norm(' '.join(units.values()))
    try: Q=json.load(open(f'{RUN}/quiz_out/{tid}.json'))
    except Exception as ex: print('FAIL: cannot read output:',ex);sys.exit(1)
    nums=0;seen=set()
    for lv,n in (('easy',3),('medium',4),('hard',4)):
        qs=Q.get(lv,[])
        if len(qs)!=5: errs.append(f'{lv}: needs exactly 5 questions, has {len(qs)}')
        us=[]
        for i,q in enumerate(qs):
            tag=f'{lv}[{i+1}]';check_q(q,n,units,alltext,errs,tag)
            if 'options' in q and isinstance(q.get('a'),int) and q['a']<len(q['options']) and numeric(q['options'][q['a']]): nums+=1
            us.append(q.get('unit'))
            k=norm(q.get('q',''))
            if k in seen: errs.append(f'{tag}: duplicate question')
            seen.add(k)
        if len(set(us))<4: errs.append(f'{lv}: questions should draw on at least 4 different paragraphs')
        nots=sum(1 for q in qs if re.search(r'\b(NOT|EXCEPT|not one of|did not)\b',q.get('q','')))
        if nots>1: errs.append(f'{lv}: more than one NOT/EXCEPT question')
    if nums>1: errs.append(f'{nums} questions have a number as the answer; at most 1 allowed')
    print('PASS' if not errs else 'FAIL\n'+'\n'.join(errs))
