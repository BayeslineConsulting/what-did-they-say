#!/usr/bin/env python3
"""Split session transcripts into talks and meaning units.

Two modes:
  propose  python segment.py propose session1.txt [session2.txt ...]
           Prints candidate talk starts (conducting announcements, first long line
           after an 'Amen') so Claude can write manifest.json. Nothing is written.
  build    python segment.py build manifest.json segs.json
           Uses manifest.json (talk start timestamps + speakers) to write segs.json.

Transcript format handled: 'Speaker Name (MM:SS.mmm)' header lines followed by text
(diarized ASR export). Plain text without timestamps also works: every line is a unit
and the manifest 'start' is a unique substring of the talk's first sentence."""
import re,sys,json
HDR=re.compile(r'^(.{1,60}?) \(([\d:.]+)\)\s*$')
def lines_of(path):
    cur=None;out=[]
    for ln in open(path,encoding='utf-8',errors='replace'):
        ln=ln.rstrip('\n'); m=HDR.match(ln)
        if m: cur=m.group(2); out.append((cur,True,'')); continue
        if ln.strip(): out.append((cur,False,ln.strip()))
    return out
AMEN=re.compile(r"(name of[^.]{0,60}(Jesus Christ|Master Teacher)[^.]{0,20}[.,]?\s*(Amen|amen)\.?\s*$)|(\b[Aa]men\.\s*$)")
ANN=re.compile(r"(will (now )?(hear|speak|address)|followed by|concluding speaker|will then (speak|address))",re.I)
def propose(paths):
    for p in paths:
        print('=====',p); prev_amen=True
        for ts,hdr,ln in lines_of(p):
            if hdr or not ln: continue
            if ANN.search(ln): print(f'  [ANNOUNCE {ts}] {ln[:160]}')
            if prev_amen and len(ln)>120: print(f'  [START? {ts}] {ln[:110]}'); prev_amen=False
            if AMEN.search(ln): print(f'  [END {ts}] ...{ln[-70:]}'); prev_amen=True
def build(manifest,out):
    M=json.load(open(manifest));units=[];talks=[];attached=[];n_t=0
    for s in M['sessions']:
        rows=lines_of(s['file'])
        for k,t in enumerate(s['talks']):
            n_t+=1; tid=f"T{n_t:02d}"
            i0=next(i for i,r in enumerate(rows) if (r[0]==t['start'] and r[1]) or (t['start'] in r[2]))
            nxt=s['talks'][k+1]['start'] if k+1<len(s['talks']) else None
            n=0
            for i in range(i0,len(rows)):
                ts,hdr,ln=rows[i]
                if nxt and i>i0 and ((ts==nxt and hdr) or (nxt in ln)): break
                if hdr or not ln: continue
                if len(ln)<25:
                    if n>0: units[-1]['text']+=' '+ln; attached.append((tid,ln))
                    continue
                n+=1; units.append(dict(unit_id=f"{tid}.{n:02d}",talk_id=tid,session=s['label'],timestamp=ts or '',text=ln))
                if AMEN.search(ln): break
            talks.append(dict(talk_id=tid,session=s['label'],file=s['file'].split('/')[-1],start=t['start'],speaker=t['speaker'],
                              role=t.get('role',''),name_confidence=t.get('name_confidence','high'),units=n))
    json.dump(dict(conference=M['conference'],talks=talks,units=units),open(out,'w'),ensure_ascii=False,indent=0)
    print(f"{len(talks)} talks, {len(units)} units; {len(attached)} short lines attached to the preceding unit")
    for t in talks: print(t['talk_id'],t['session'],t['units'],t['speaker'],'| last:',[u for u in units if u['talk_id']==t['talk_id']][-1]['text'][-60:])
if __name__=='__main__':
    if sys.argv[1]=='propose': propose(sys.argv[2:])
    else: build(sys.argv[2],sys.argv[3])
