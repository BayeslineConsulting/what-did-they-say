#!/usr/bin/env python3
"""Render the doc's action-list section and per-theme coded-example tables as markdown.
Usage: python render_sections.py RUN_DIR MASTER_CODEBOOK.json OUT_DIR
Needs RUN_DIR/names.json ({talk_id: display name, '*' suffix for names as transcribed}),
actions.json, examples.txt, themes.json. Writes actions.md and examples_md.json."""
import json,os,sys
from collections import Counter
RUN,MCB,OUT=sys.argv[1:4];J=lambda f:json.load(open(os.path.join(RUN,f)))
TH=J('themes.json')['themes'];names=J('names.json');A=J('actions.json');M=json.load(open(MCB))['codes']
thname={t['id']:t['name'] for t in TH};cnt=Counter(a[0] for a in A);order=sorted(cnt,key=lambda t:(-cnt[t],t))
NT=len(J('segs.json')['talks'])
BU=J('bundles.json') if os.path.exists(os.path.join(RUN,'bundles.json')) else None
if BU:
    nm=lambda u:names[u[:3]]
    spk=lambda b:list(dict.fromkeys(nm(u) for u,q,r in b['items']))
    others=sorted(BU['others'],key=lambda b:-len(spk(b)))
    total=len(BU['oaks_own'])+len(BU['oaks_repeated'])+len(BU['others'])
    md=["## What to do in the next six months","",f"{total} things to do, drawn from {len(A)} invitations in {len({a[2][:3] for a in A})} of the {NT} talks. {BU['president']}'s invitations come first. Where several speakers gave the same challenge, it is one item with each speaker named. Every quoted phrase appears verbatim in the transcript; bracketed words correct a transcription error.",""]
    md+=[f"### Start here: {BU['president']}","","**His invitations this weekend**","","| What to do | In his words | Echoed by |","| --- | --- | --- |"]
    for b in BU['oaks_own']:
        lead=[f"\"{q}\" ({u})" for u,q,r in b['items'] if r=='lead'];ech=[x for x in spk(b) if 'Oaks' not in x]
        md.append(f"| {b['title']} | {' '.join(lead)} | {', '.join(ech) or '—'} |")
    md+=["","**His earlier invitations, repeated by other speakers this weekend**","","| What to do | In their words | Repeated by |","| --- | --- | --- |"]
    for b in BU['oaks_repeated']:
        lead=' '.join(f"\"{q}\" ({u})" for u,q,r in b['items'] if r=='lead');md.append(f"| {b['title']} | {lead} | {', '.join(spk(b))} |")
    for head,sel in [("Asked by several speakers",lambda b:len(spk(b))>1 and not b.get('audience')),("Also asked of everyone",lambda b:len(spk(b))==1 and not b.get('audience')),("For specific groups",lambda b:b.get('audience'))]:
        rows=[b for b in others if sel(b)]
        if not rows: continue
        md+=["",f"### {head}","","| What to do | Speakers | In their words |","| --- | --- | --- |"]
        for b in rows:
            u,q,r=b['items'][0];md.append(f"| {b['title']} | {', '.join(spk(b))} | \"{q}\" ({u}) |")
    md+=["","\\* Name as transcribed. Full quotes for every bundled item are in the workbook's Actions sheet and on the report page."]
    os.makedirs(OUT,exist_ok=True);open(os.path.join(OUT,'actions.md'),'w').write('\n'.join(md))
else:
  md=["## What to do in the next six months","",f"Speakers issued {len(A)} invitations and directives that apply to members generally, drawn from {len({a[2][:3] for a in A})} of the {NT} talks. They are grouped by theme, largest groups first. Every \"In their words\" phrase appears verbatim in the transcript at the unit shown; bracketed words correct an obvious transcription error.","","Promises are excluded. Items addressed to a specific group say so.",""]
  for th in order:
      md+=[f"### {thname[th]} ({cnt[th]})","","| What to do | Who | In their words |","| --- | --- | --- |"]+[f"| {act} | {names[u[:3]]} ({u}) | \"{q}\" |" for t,act,u,q in A if t==th]+[""]
  md.append("\\* Name as transcribed.")
  os.makedirs(OUT,exist_ok=True);open(os.path.join(OUT,'actions.md'),'w').write('\n'.join(md))
rows=[l.rstrip('\n').split('|',3) for l in open(os.path.join(RUN,'examples.txt')) if l.strip()];ex={}
for t in TH:
    rs=sorted([r for r in rows if r[0]==t['id']],key=lambda r:(t['categories'].index(M[r[1]]['category']),r[2]))
    ex[t['id']]='\n'.join([f"**Coded examples ({len(rs)}).** Grouped by category; each row is one coded unit.","","| Category | Code | Excerpt | Speaker (unit) |","| --- | --- | --- | --- |"]+[f"| {M[k]['category'][4:]} | {M[k]['code']} | \"{q}\" | {names[u[:3]]} ({u}) |" for th,k,u,q in rs])
json.dump(ex,open(os.path.join(OUT,'examples_md.json'),'w'),ensure_ascii=False,indent=1)
print('actions',len(A),'| examples',len(rows))
