import json,sys,os,glob,collections
RUN=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,RUN)
from validate_quiz import norm,check_q,numeric
lv=sys.argv[1];n=3 if lv=='easy' else 4;errs=[]
units={};sess={}
C=json.load(open(f'{RUN}/quiz_in/conference.json'))
for t in C['talks']: sess[t['id']]=t['session']
for f in glob.glob(f'{RUN}/lessons_in/T*.json'):
    for p in [x for x in json.load(open(f))['paragraphs'] if 'unit' in x]: units[p['unit']]=p['text']
alltext=norm(' '.join(units.values()))
try: Q=json.load(open(f'{RUN}/quiz_out/conference_{lv}.json'))['questions']
except Exception as ex: print('FAIL: cannot read output:',ex);sys.exit(1)
if len(Q)!=25: errs.append(f'needs exactly 25 questions, has {len(Q)}')
cnt=collections.Counter();facts=0;seen=set()
for i,q in enumerate(Q):
    tag=f'[{i+1}]'
    if q.get('kind')=='fact': facts+=1;check_q(q,n,units,alltext,errs,tag,need_unit=False)
    else:
        check_q(q,n,units,alltext,errs,tag)
        if not q.get('talk') or not str(q.get('unit','')).startswith(q['talk']+'.'): errs.append(f'{tag}: talk/unit mismatch')
        else: cnt[q['talk']]+=1
    k=norm(q.get('q',''))
    if k in seen: errs.append(f'{tag}: duplicate question')
    seen.add(k)
if facts>3: errs.append(f'{facts} fact questions; at most 3')
if len(cnt)<20: errs.append(f'only {len(cnt)} different talks; need at least 20')
for t,c in cnt.items():
    if c>2: errs.append(f'{t} has {c} questions; at most 2')
if len({sess[t] for t in cnt})<4: errs.append('not all four sessions covered')
if cnt['T27']+cnt['T37']<2: errs.append('need 2-3 questions on President Oaks (T27/T37)')
print('PASS' if not errs else 'FAIL\n'+'\n'.join(errs))
