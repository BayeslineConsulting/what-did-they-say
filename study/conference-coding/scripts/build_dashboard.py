#!/usr/bin/env python3
"""Render the cross-conference trend dashboard from history.json.
Usage: python build_dashboard.py history.json out.html
Self-contained page (Google Fonts only) that follows published-artifact rules."""
import json,sys
hist=json.load(open(sys.argv[1]))
html=r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>General Conference themes over time</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#f6f7f5;--panel:#ffffff;--ink:#1c2733;--muted:#5b6672;--rule:#dde1e4;--bar:#c9d0d6;--gold:#a8822a;--sage:#5e7d6f;
 box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12171d;--panel:#1a2129;--ink:#e6e9ec;--muted:#9aa4ae;--rule:#2b343e;--bar:#3a4652;--gold:#d2a94a;--sage:#8fb3a3;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#12171d;--panel:#1a2129;--ink:#e6e9ec;--muted:#9aa4ae;--rule:#2b343e;--bar:#3a4652;--gold:#d2a94a;--sage:#8fb3a3;color-scheme:dark}
html{scroll-padding-top:env(safe-area-inset-top,0px)}*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 "Public Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:980px;margin:0 auto;padding:40px 24px 64px}
h1,h2{font-family:Literata,Georgia,"Times New Roman",serif;font-weight:600;letter-spacing:-.01em;margin:0}
h1{font-size:clamp(28px,4.4vw,42px);line-height:1.12;max-width:20ch}
h2{font-size:22px;margin:48px 0 6px}
.lede{color:var(--muted);max-width:62ch;margin:12px 0 0}
.bar-row{display:grid;grid-template-columns:minmax(0,1fr) 220px 48px;gap:12px;align-items:center;padding:10px 0;border-top:1px solid var(--rule)}
.bar-row .name{font-weight:600}.bar-row .claim{color:var(--muted);font-size:14px;margin-top:2px}
.track{height:10px;background:var(--rule);border-radius:5px;overflow:hidden}.fill{height:100%;background:var(--bar)}
.bar-row:first-child .fill{background:var(--gold)}
.num{font-family:Literata,Georgia,serif;font-size:20px;text-align:right}
.facts{display:flex;flex-wrap:wrap;gap:28px;margin:26px 0 0}.facts div{min-width:120px}
.facts b{display:block;font-family:Literata,Georgia,serif;font-size:30px;font-weight:600}.facts span{color:var(--muted);font-size:14px}
select{margin-top:0;font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--rule);border-radius:6px;padding:6px 10px;margin-top:18px}
select:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.chart{overflow-x:auto;background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:16px;margin-top:12px}
.chart svg{display:block;width:100%;height:auto}#trend svg{min-width:560px;max-width:720px}
.note{color:var(--muted);font-size:14px;margin-top:8px;max-width:70ch}
.two{display:grid;grid-template-columns:1fr 1fr;gap:24px}@media(max-width:760px){.two{grid-template-columns:1fr}.bar-row{grid-template-columns:1fr 90px 40px}}
</style></head><body><main>
<h1 id="headline">Conference themes, coded the same way every six months</h1>
<p class="lede" id="lede"></p>
<p><label for="pick" class="note">Conference </label><select id="pick"></select></p>
<div class="facts" id="facts"></div>
<h2>Themes, ranked by how many talks carry them</h2>
<p class="note">Each theme is a claim from second-cycle coding. Bar = share of talks with at least one coded unit.</p>
<div id="themes"></div>
<div class="two">
<section><h2>Scripture by volume</h2><p class="note">Share of identified references, one bar per conference.</p><div class="chart" id="scrip"></div></section>
<section><h2>Most-cited leaders</h2><p class="note">Talks mentioning each leader, selected conference.</p><div class="chart" id="lead"></div></section>
</div>
<h2>Category emphasis over time</h2>
<p class="note" id="trendnote">Share of all code applications per category. Categories persist across conferences through the master codebook, so these are comparable; themes are re-derived each time.</p>
<div class="chart" id="trend"></div>
</main>
<script>
const H=__HISTORY__;
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pick=document.getElementById('pick');
H.forEach((h,i)=>{const o=document.createElement('option');o.value=i;o.textContent=h.label||h.conference;pick.appendChild(o)});
pick.value=H.length-1;pick.onchange=render;
function bars(el,items,max){ // items:[label,value]
 const w=560,rh=26,hgt=items.length*rh+10;let s=`<svg viewBox="0 0 ${w} ${hgt}" role="img" aria-label="bar chart">`;
 items.forEach(([l,v],i)=>{const y=i*rh+4,bw=(w-230)*v/max;
  s+=`<text x="0" y="${y+15}" fill="${css('--ink')}" font-size="13">${esc(l)}</text><rect x="190" y="${y+4}" width="${bw}" height="14" rx="3" fill="${i==0?css('--gold'):css('--bar')}"><title>${esc(l)}: ${v}</title></rect><text x="${196+bw}" y="${y+15}" fill="${css('--muted')}" font-size="12">${v}</text>`});
 el.innerHTML=s+'</svg>';}
function render(){
 const h=H[pick.value];
 document.getElementById('lede').textContent=`${h.label||h.conference}: ${h.talks} talks, ${h.units} coded units, ${h.words.toLocaleString('en-US')} words. ${H.length} conference${H.length>1?'s':''} on record.`;
 const sv=h.scripture_volumes,ns=Object.values(sv).reduce((a,b)=>a+b,0);
 document.getElementById('facts').innerHTML=[[h.talks,'talks'],[h.words.toLocaleString('en-US'),'words'],[ns,'scripture references'],[h.median_christ_per_1000,'median references to Christ per 1,000 words (talks over 500 words)'],[h.new_codes,'new codes this run']].map(([b,s])=>`<div><b>${b}</b><span>${s}</span></div>`).join('');
 const th=[...h.themes].sort((a,b)=>b.talks-a.talks);
 document.getElementById('themes').innerHTML=th.map(t=>`<div class="bar-row"><div><div class="name">${esc(t.name)}</div><div class="claim">${t.units} coded units</div></div><div class="track"><div class="fill" style="width:${100*t.talks/h.talks}%"></div></div><div class="num">${t.talks}</div></div>`).join('');
 const L=Object.entries(h.leaders_mentioned).sort((a,b)=>b[1]-a[1]).slice(0,8);bars(document.getElementById('lead'),L,Math.max(...L.map(x=>x[1])));
 // scripture stacked 100% bars across conferences
 const V=['Old Testament','New Testament','Book of Mormon','Doctrine and Covenants','Pearl of Great Price'];
 const shades=[.25,.45,1,.7,.15];const w=560,rh=30;let s=`<svg viewBox="0 0 ${w} ${H.length*rh+44}" role="img" aria-label="scripture share by volume">`;
 H.forEach((c,i)=>{let x=110;const tot=V.reduce((a,v)=>a+(c.scripture_volumes[v]||0),0)||1;s+=`<text x="0" y="${i*rh+19}" font-size="13" fill="${css('--ink')}">${esc(c.conference)}</text>`;
  V.forEach((v,j)=>{const n=c.scripture_volumes[v]||0,bw=(w-120)*n/tot;s+=`<rect x="${x}" y="${i*rh+6}" width="${bw}" height="18" fill="${css('--sage')}" fill-opacity="${shades[j]}"><title>${v}: ${n} (${Math.round(100*n/tot)}%)</title></rect>`;if(bw>34)s+=`<text x="${x+4}" y="${i*rh+19}" font-size="11" fill="${css('--ink')}">${Math.round(100*n/tot)}%</text>`;x+=bw});});
 let lx=0;V.forEach((v,j)=>{s+=`<rect x="${lx}" y="${H.length*rh+16}" width="10" height="10" fill="${css('--sage')}" fill-opacity="${shades[j]}"/><text x="${lx+14}" y="${H.length*rh+25}" font-size="11" fill="${css('--muted')}">${v.replace('Doctrine and Covenants','D&C').replace('Pearl of Great Price','PGP')}</text>`;lx+=v.length>16?70:105});
 document.getElementById('scrip').innerHTML=s+'</svg>';
 // category trend
 const tr=document.getElementById('trend');const cats=Object.keys(h.category_share).filter(c=>!c.includes('rhetorical')).sort((a,b)=>h.category_share[b]-h.category_share[a]).slice(0,8);
 if(H.length<2){bars(tr,cats.map(c=>[c.replace(/^C\d+ /,''),Math.round(1000*h.category_share[c])/10]),Math.max(...cats.map(c=>100*h.category_share[c])));
  document.getElementById('trendnote').textContent='Baseline: the top categories by share of code applications (%). Lines across conferences appear once a second conference is coded.';return;}
 const W=860,Hh=300,x0=40,x1=W-200,y=v=>Hh-30-(Hh-60)*v/Math.max(...H.flatMap(c=>cats.map(k=>c.category_share[k]||0)));
 const labs=[];let g=`<svg viewBox="0 0 ${W} ${Hh}" role="img" aria-label="category share over time">`;
 H.forEach((c,i)=>{const X=x0+(x1-x0)*i/(H.length-1);g+=`<text x="${X}" y="${Hh-8}" font-size="12" text-anchor="middle" fill="${css('--muted')}">${esc(c.conference)}</text>`});
 cats.forEach((k,j)=>{const col=j==0?css('--gold'):css('--bar');const pts=H.map((c,i)=>[x0+(x1-x0)*i/(H.length-1),y(c.category_share[k]||0)]);
  g+=`<polyline fill="none" stroke="${col}" stroke-width="${j==0?3:1.5}" points="${pts.map(p=>p.join(',')).join(' ')}"><title>${esc(k)}</title></polyline>`;labs.push({k,y:pts[pts.length-1][1],j,v:h.category_share[k]})});
 labs.sort((a,b)=>a.y-b.y);for(let i=1;i<labs.length;i++)if(labs[i].y-labs[i-1].y<15)labs[i].y=labs[i-1].y+15;
 labs.forEach(l=>{g+=`<text x="${x1+8}" y="${l.y+4}" font-size="12" fill="${l.j==0?css('--ink'):css('--muted')}">${esc(l.k.replace(/^C\d+ /,''))} ${(100*l.v).toFixed(1)}%</text>`});
 tr.innerHTML=g+'</svg>';}
render();matchMedia('(prefers-color-scheme: dark)').addEventListener('change',render);
</script></body></html>'''
open(sys.argv[2],'w').write(html.replace('__HISTORY__',json.dumps(hist)))
print('wrote',sys.argv[2],'with',len(hist),'conference(s)')
