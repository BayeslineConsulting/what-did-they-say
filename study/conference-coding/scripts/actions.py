#!/usr/bin/env python3
"""Propose candidate invitations/directives for the six-month action list.
Usage: python actions.py RUN_DIR/segs.json > candidates.txt
Prints every sentence containing invitation language with its unit ID. Claude then reads each
talk's directive passages (list-style counsel is often missed by patterns), curates
RUN_DIR/actions.json as [[theme_id, plain-language action, unit_id, verbatim quote], ...]
and runs verify_quotes.py. Rules: members generally (flag subgroups in the action text),
no promises, the quote must be verbatim in that unit."""
import json,re,sys
d=json.load(open(sys.argv[1]));spk={t['talk_id']:t['speaker'] for t in d['talks']}
P=re.compile(r"\b(I invite|invite you|invite all|let us|let's|I urge|I plead|I encourage|please|may we|I challenge|I ask you|I call upon|we must|we should|we need to|first,|second,|third,|remember to|don't|do not|never)\b",re.I)
seen=set()
for u in d['units']:
    for s in re.split(r'(?<=[.?!])\s+',u['text']):
        if P.search(s) and (u['unit_id'],s) not in seen:
            seen.add((u['unit_id'],s));print(f"{u['unit_id']} | {spk[u['talk_id']][:28]} | {s.strip()[:240]}")
