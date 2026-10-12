import json,re,sys
segs=json.load(open('segs.json'));U={u['unit_id']:u['text'] for u in segs['units']}
TR={'“':'"','”':'"','‘':"'",'’':"'",'—':'-','–':'-','\xa0':' '}
def norm_map(s):
    out=[];idx=[]
    for i,ch in enumerate(s):
        if ch=='…': 
            for c in '...': out.append(c);idx.append(i)
        else: out.append(TR.get(ch,ch));idx.append(i)
    return ''.join(out),idx
def nrm(q): return norm_map(q)[0]
def exact(unit,approx,allow_next=True):
    t,n=unit.split('.');nx=f'{t}.{int(n)+1:02d}'
    src=U[unit]+((' '+U[nx]) if allow_next and nx in U else '')
    ns,idx=norm_map(src);na=re.sub(r'\s+',' ',nrm(approx)).strip()
    p=ns.find(na)
    if p<0:
        # case-insensitive fallback
        p=ns.lower().find(na.lower())
        if p<0: raise SystemExit(f'NOT FOUND {unit}: {approx}\n   in: {src[:300]}')
    a=idx[p];b=idx[p+len(na)-1]+1
    r=src[a:b]
    if r[0] in '“‘' and r[-1] in '”’' and not any(c in r[1:-1] for c in '“”'): r=r[1:-1]
    return r
B=dict(president='President Dallin H. Oaks',oaks_own=[],oaks_repeated=[],others=[],counsel=[])
def bundle(group,key,area,items,audience=None,label=''):
    its=[[u,exact(u,q),'lead' if i==0 else 'echo'] for i,(u,q) in enumerate(items)]
    d=dict(key=key,title=its[0][1],label=label,area=area,items=its)
    if audience: d['audience']=audience
    B[group].append(d)
# ---- President Oaks: direct invitations this conference
bundle('oaks_own','keep-covenants','TH01',[('T27.07','I urge you to keep the commandments and be true to the covenants so many of you have made to guide you along the covenant path.')],label='Keep the commandments and your covenants')
bundle('oaks_own','believe-promises','TH10',[('T27.16','These promises from the Book of Mormon are true. Millions believe them and have had experiences to affirm their truth. I invite all to believe them.')],label="Believe the Book of Mormon's promises")
bundle('oaks_own','act-and-share','TH10',[('T27.18','I call upon all to act on these truths and to share them with others that we may all draw closer to Jesus Christ, our Savior.'),('T34.20','I invite you to do something that is as simple as gospel fruit is delicious: love, share, and invite.')],label='Act on these truths and share them')
bundle('oaks_own','study-the-talks','TH08',[('T37.02','As the talks of this conference are published, we invite all to study and ponder them prayerfully and to act in faith on the principles they explain.'),('T04.26','let us not be guilty of holding "the oracles of God ... as a light thing"')],label='Study the conference talks and act on them')
# ---- his earlier invitations, repeated by other speakers
bundle('oaks_repeated','peacemakers','TH07',[('T25.01','let us follow Him by forgoing contention and by using the language and methods of peacemakers. In our families and other personal relationships, let us avoid what is harsh and hateful.'),('T18.13','Let us avoid what is harsh and hateful. Let us seek to be holy, like our Savior.'),('T25.13','let us use words that encourage understanding and peace'),('T25.15','let us fill our hearts with the true doctrine of Christ'),('T25.16','Let us repent for the harsh language and expressions that have offended our friends, leaders, family members, or colleagues.'),('T25.16','Let us pray for peaceful communication among us, regardless of the difference in our opinions.'),('T25.16','Let us use the language that uplifts, edifies, comforts, and brings people together.')],label='Forgo contention; speak as a peacemaker')
bundle('oaks_repeated','seek-friends','TH08',[('T29.17','number seven is an invitation from our prophet, President Dallin H. Oaks: "Seek friends ... who are striving to follow the Lord ... with whom you can feel the Spirit and ... reinforce your faith."')],audience='repeated to young women',label='Seek friends who follow the Lord')
O='others'
bundle(O,'bear-witness','TH10',[('T03.31','I invite you to look each day for opportunities, as prompted by the Holy Ghost, to bear witness of Jesus Christ and His restored gospel'),('T03.14','Please trust it, nurture it, and bear it, because it is uniquely yours.')],label='Bear your witness of Christ')
bundle(O,'come-unto-christ','TH10',[('T23.27','I invite you, please come unto Christ and embrace His promise')],label='Come unto Christ')
bundle(O,'invite-one','TH10',[('T23.28','My humble invitation to us all: Will you find one person and invite him or her to come unto Christ by exercising faith to follow His teachings, or invite a friend to meet with the missionaries?')],label='Invite one person')
bundle(O,'choose-christ','TH02',[('T02.32',"Let's choose Christ, who can heal the wounds of this world while carving out room for joy!")],label='Choose Christ in hard times')
bundle(O,'wayward','TH03',[('T18.08','I ask you to turn over to Jesus Christ your despair for those wayward souls.')],label='Give Christ your despair for loved ones')
bundle(O,'see-others','TH05',[('T10.39','let us pray every day for eyes to see the divine appointments God places before us!'),('T10.39','Let us put compassion into action and minister to the person in front of us.'),('T20.08','I plead with you as disciples of Jesus Christ to pray to see others as He sees them and to treat them accordingly.'),('T20.18','This week, I invite you to: Learn the name of someone who may feel unseen.'),('T20.20','Pray to see others as Heavenly Father sees them.')],label='See and minister to the one')
bundle(O,'help-not-judge','TH05',[('T33.12','we are invited to reorient our souls so we may help friends and new members in more Christlike ways')],label='Be quick to help, slow to judge')
bundle(O,'labels','TH06',[('T20.21','Replace worldly labels with these eternal truths: Child of God. Child of the covenant. Disciple of Jesus Christ.')],label='Replace labels with eternal truths')
bundle(O,'unity','TH07',[('T28.29','I invite you to join the Christ-centered unity we are trying to build.'),('T28.29','Please, come and see, come and help, and come and belong.')],label='Join in Christ-centered unity')
bundle(O,'truth-with-love','TH07',[('T36.02','I also hope that you will look deeply into your [own] heart to see if there are shards of pride or jealousy that prevent you from becoming a peacemaker." I extend that same invitation to all of us today.')],label='Look into your own heart')
bundle(O,'sacrament','TH01',[('T28.26','let us not miss the unifying power of the sacrament')],label='Receive the sacrament with purpose')
bundle(O,'scriptures','TH08',[('T11.14','I invite you to search the scriptures diligently, that you might know the word of God')],label='Search the scriptures')
bundle(O,'small-and-simple','TH08',[('T11.25','I invite you to always remember scriptures, prayers, the sacrament, and covenants.')],label='Remember the small and simple things')
bundle(O,'repent','TH04',[('T01.13','Please "do not procrastinate the day of your repentance until the end."'),('T32.17','Let us ponder about the changes that we need to make in our lives')],label='Repent now')
bundle(O,'temple','TH01',[('T01.26','Please let us never speak of a temple as big or small, elaborate or plain.'),('T01.19','let us celebrate and treasure even more the spiritual blessings temples bring'),('T01.27','let us always be grateful for the gifts of eternity sacred temples bring'),('T01.29','please consider saving for and buying your own ceremonial temple clothes')],label='Honor the temple with gratitude')
bundle(O,'strong-link','TH01',[('T01.28','in the chain of your eternal family, please be a strong link')],label='Be a strong link')
bundle(O,'fast','TH09',[('T06.14',"I invite you to prayerfully ponder Isaiah's teachings and more intentionally embrace the divine purpose of the law of the fast in a higher and holier way as part of our worship.")],label='Live a higher and holier fast')
bundle(O,'gambling','TH09',[('T08.25','my plea again is not only to refrain from gambling but to use the time and resources saved thereby for doing good'),('T08.24','Today, I am pleading with all of us to live life on a higher plane.')],label='Refrain from gambling; do good')
bundle(O,'teachers','TH10',[('T35.15','these two great commandments become one simple invitation: Love the Lord and love those you teach.'),('T35.43','the invitation is the same. Come unto the Master Teacher. Learn of Him. Love Him.')],audience='for teachers',label='Love the Lord and those you teach')
bundle(O,'mission','TH10',[('T07.13','To all the rising generation of the Church, I invite you to place serving a full-time mission high on your list.'),('T07.17',"I invite each of you to substitute your name for Thomas's")],audience='for the rising generation',label='Put a mission high on your list')
bundle(O,'yw-choose-one','TH08',[('T29.10','I would like to share seven ways that will help you in this endeavor. I invite you to listen to the Spirit to choose one to focus on over the next few weeks.')],audience='for young women',label='Choose one of seven ways to grow')
bundle(O,'yw-aspirations','TH06',[('T29.21','I invite you to study the thirteenth article of faith and to create your own list of aspirations.'),('T29.03','I invite you to look at your life and what you want to achieve with enthusiasm and the certainty that your Father in Heaven will guide you on that journey')],audience='for young women',label='Write your list of aspirations')
# ---- President Oaks's direct instructions that are not phrased as invitations (shown separately, not counted)
for u,q in [('T27.05','Focus on developing your faith in God and the mission of His Son, Jesus Christ.'),('T27.06','Hold on to the first article of faith even if something else is uncertain. And while you wait, wait upon the Lord'),('T27.07','Never let your secular learning limit your spiritual horizons.'),('T27.10','Protect yourself with the weekly renewing of your covenants by partaking of the sacrament and with consistent efforts to live according to those sacred covenants.'),('T37.04','Join us at TempleSquare.org or through the Temple Square app to learn more.')]:
    B['counsel'].append([u,exact(u,q)])
json.dump(B,open('bundles.json','w'),ensure_ascii=False,indent=1)
acts=[];seen=set()
for g in ('oaks_own','oaks_repeated','others'):
    for b in B[g]:
        for u,q,r in b['items']:
            if (u,q) in seen: continue
            seen.add((u,q));acts.append([b['area'],b['label'],u,q])
json.dump(acts,open('actions.json','w'),ensure_ascii=False,indent=1)
EX='''TH01|HON|T05.12|I have never clung so tightly to my covenants.
TH01|GEN|T13.10|"I know what it was! It was covenants."
TH01|GEN|T13.18|They do not bless just the maker of the covenant but are generational in their impact.
TH01|SAC|T26.12|we do not need to be perfect to partake of the sacrament
TH01|NAM|T22.09|It is an invitation to become more like Him through covenant keeping.
TH01|HSP|T31.17|Receiving this ratifying sealing by the Holy Ghost typically is not a one-time event; rather, it comes over time as we repent sincerely and consistently, honor our covenants, and yield our hearts unto God.
TH01|CRD|T31.13|Ongoing faithfulness is required for those credentials to be valid and for promised blessings to be received.
TH01|FND|T31.28|No faithful disciple will ultimately be deprived of any eternal blessing God has promised because of another individual's unrighteous exercise of moral agency.
TH01|TMP|T01.26|ordinances are not big or small. Covenants are not big or small.
TH01|TPR|T26.20|Although they were doing much, they were not accomplishing much because God's holy house was not a priority in their lives.
TH02|TNR|T02.12|The gospel isn't the umbrella; it's the solid rock we're standing on during the storm
TH02|AGR|T02.07|I'm learning the only way to get it is to go through it.
TH02|TWU|T02.20|Not understanding is not the same as not believing.
TH02|CFX|T17.01|He told me a single thought came to his mind at that moment: "I can't fix this."
TH02|DGT|T05.19|Some miracles are immediate, some come after long waiting, and some await the Resurrection.
TH02|QNS|T05.08|Such questions and emotions are not sin or weakness
TH02|TNR|T12.13|This does not mean that we will be free from trials or difficulties.
TH02|TST|T19.06|"Hal, of course it's hard. It's supposed to be. Life is a test."
TH02|PWO|T16.21|Peace will come even when hoped-for outcomes do not.
TH02|RES|T17.11|It signifies that mortal deficiencies are only temporary!
TH03|CRB|T16.16|the Redeemer rescues not by shortening our course but by helping us lengthen our stride
TH03|LFT|T15.14|Our Saviour constantly sought out the most desperate souls sinking into darkness and dread and lifted them up. And He wants to lift you!
TH03|CRB|T18.10|In the vernacular, Jesus Christ says to all who grieve, "I've got this!"
TH03|GRC|T05.13|This grace does not remove the pain and difficulty of affliction; it is an enabling power
TH03|RCR|T09.11|our hope rests on His faithfulness and righteousness, not on our own
TH03|DEL|T05.03|the question for most righteous followers is not if He will deliver but how and when He will do so
TH03|IDH|T02.44|He waits for an invitation before He can really go to work
TH03|SRL|T17.02|All of us, regardless of experience, talent, or willpower, will sooner or later encounter burdens we cannot possibly carry ourselves.
TH03|WMS|T35.42|He will teach you, walk beside you, and gradually make you into the teacher He knows you can become
TH03|CHA|T32.08|Whatever concerns, challenges, and struggles we may have in our lives, the answer is always Jesus Christ.
TH04|CAY|T23.10|We do not need to perfect ourselves to come to Christ. We come to Christ to be perfected.
TH04|BST|T23.21|'Randall doesn't need to be perfect. He needs to do the very best he can.'
TH04|NGU|T18.23|We fail only when we give up and stop trying
TH04|WIP|T27.06|We are all a work in progress.
TH04|CRG|T21.05|Spiritual courage is the triumph over obstacles, doubt, and fear in choosing the right.
TH04|LLD|T07.11|serving a mission is just one of many significant steps on the path of lifelong discipleship
TH04|DRF|T15.19|We rarely intend to sink.
TH04|NTL|T14.13|there is still yet time if we turn to Christ today
TH04|RPT|T24.23|When we make repentance a constant, day-to-day part of our lives, we can approach the Lord with integrity
TH04|CAY|T23.24|The adversary wants to hang that sign on the gate of our heart.
TH05|TAP|T19.13|"God does notice us, and he watches over us. But it is usually through another person that he meets our needs."
TH05|SEE|T20.06|"Very few students know my name. Your daughter sees me."
TH05|APT|T10.19|Often this happens when God places someone in our path and we have eyes to see them. I call these "divine appointments."
TH05|SEE|T10.21|To Jesus, these people were not interrupting His mission. They were His mission.
TH05|QHS|T33.06|a true disciple of Jesus Christ is quick to help and slow to judge
TH05|QHS|T33.11|He did not hold her hostage to her history.
TH05|NME|T20.04|Often, helping others feel seen as children of God begins with something as simple as learning their name.
TH05|MRN|T17.04|we were grateful "to mourn with those that mourn ... and comfort those that stand in need of comfort."
TH05|SVC|T22.17|Service is the very fiber of which an exalted life in the celestial kingdom is made
TH05|WAY|T18.12|Love is being there with arms outstretched and a cheerful countenance.
TH06|UNL|T14.06|You did not earn it; you cannot lose it. It is yours forever.
TH06|COG|T14.01|I am a child of God and He loves me.
TH06|LBL|T20.11|Our identity is not something we achieve; it is something we inherit as beloved sons and daughters of God.
TH06|LBL|T20.13|His grace is sufficient to lift you above every label and limitation.
TH06|AST|T09.14|there is no asterisk excluding you from God's richest blessings
TH06|GKY|T29.05|the Lord knows where you are; He has your exact location and can guide you
TH06|UNL|T29.05|knowing everything about you does not make Him love you less
TH06|POT|T20.09|He sees not only who we are but who we can become.
TH06|FAM|T14.05|It is often through families, despite all their imperfections, that our Father teaches us about His love.
TH06|UNL|T27.07|He is relentless in His loving pursuit of each of you.
TH07|TWL|T36.20|For disciples of Jesus Christ, truth and love always walk together.
TH07|TWL|T36.08|That day I stood for truth, but I did it without love and without charity.
TH07|PCL|T25.13|We must choose language that strengthens confidence and preserves relationships.
TH07|UNI|T28.22|If we are not one, we are not His.
TH07|UNI|T28.21|The closer we come to Him, the closer we will come to each other
TH07|CTN|T32.05|he that hath the spirit of contention is not of me
TH07|LNC|T18.12|Love is not stepping back or sanctioning others' decisions and actions.
TH07|LNC|T36.15|Christ never once withheld His love from anyone, but He also never once said to anyone, 'Because I love you, you are exempt from keeping my commandments.'
TH07|DEC|T14.09|Beware of the adversary's deceitful lie that twists this precious truth.
TH07|INT|T24.10|In the Father's plan, integrity, virtue, and happiness are intrinsically linked.
TH08|SSP|T11.25|While they may seem small and simple, they are truly the armor of God
TH08|CON|T32.15|the method, timing, and length of our scripture study matter less than the consistency and sincerity of our effort
TH08|SCS|T11.11|Daily, meaningful scripture study invites the guidance of the Holy Ghost
TH08|PRY|T11.19|The burden we carry may not always be removed, but our backs will be built to carry the load placed upon them
TH08|SPR|T15.23|The language of the Spirit of God is not a language of words.
TH08|STL|T21.10|We need stillness to nourish our faith in Christ.
TH08|DIG|T29.16|it is a thief of our peace of mind, self-esteem, and the real connection
TH08|DIG|T21.09|Our phone seems almost attached to our hand, bringing a flood of information, misinformation, and now artificial information.
TH08|PRI|T24.07|some conduct which is not inherently evil can keep us from engaging in spiritual matters
TH08|SSP|T28.04|Spiritual growth is rarely dramatic at the beginning.
TH09|GMB|T08.22|Gambling is built on the desire to obtain something for nothing.
TH09|GMB|T08.07|the industry's entire business model is built on its customers losing money
TH09|OPP|T08.14|What is the opportunity cost of gambling?
TH09|EXM|T08.16|A little gambling that seemingly has only a minor impact in your life may be more costly to them if they take license from your example.
TH09|FST|T06.14|more intentionally embrace the divine purpose of the law of the fast in a higher and holier way
TH09|POR|T06.12|Though our fast offerings may seem small and simple, they become consecrated expressions of compassion, concern, and service.
TH09|NOX|T12.06|"Elder Giuffra, you are no one to deny this sister the blessings of the law of tithing. There are no exceptions to this commandment."
TH09|OLV|T12.12|We keep the commandments because we love God, not merely because we hope to receive the blessings that come from obedience.
TH09|SUB|T30.12|"As we live the law of tithing, we often receive significant but subtle blessings that are not always what we expect and easily can be overlooked"
TH09|TTH|T12.20|the law of tithing is a law of faith
TH10|TSM|T03.22|It need not be long, eloquent, or dramatic-it only needs to be true.
TH10|TSM|T03.18|To say "I know" is a tender expression of love toward our neighbor.
TH10|APW|T03.09|Apostles bear a unique, authoritative, divinely empowered witness of the living Christ
TH10|TLV|T35.22|The impact of a gospel teacher is not just the message-it is the love of the messenger.
TH10|TLV|T35.36|If class members leave the lesson feeling closer to the Savior than when they came, we have taught enough.
TH10|BOM|T13.06|No time or effort is ever wasted in reading the Book of Mormon.
TH10|PRO|T04.26|What a blessing it is to live in a time when apostles and prophets are on the earth.
TH10|MSN|T07.03|You are not only the messengers but also living examples of the message.
TH10|UNV|T27.15|His grace is for all.
TH10|BOM|T27.13|The Book of Mormon is a great witness that the Lord loves all people and reaches out to all, everywhere.'''
with open('examples.txt','w') as f:
    for ln in EX.split('\n'):
        th,k,u,q=ln.split('|',3);f.write(f'{th}|{k}|{u}|{exact(u,q,allow_next=False)}\n')
print('bundles',sum(len(B[g]) for g in ('oaks_own','oaks_repeated','others')),'actions',len(acts),'talks',len({a[2][:3] for a in acts}),'examples',len(EX.split(chr(10))))
