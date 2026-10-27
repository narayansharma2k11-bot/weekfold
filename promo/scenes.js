/* Each scene: build(stage, data) -> {dur, render(t)} ; t in seconds. 1080x1920 canvas. */
const SCENES={};

/* ---------- 1. Brand: the week folded into one edition ---------- */
SCENES.fold=({D},stage)=>{
  const cap=Captions(stage);
  const cards=D.days.map((d,i)=>{
    const c=el('div','card','',stage); c.style.cssText='left:140px;top:560px;width:800px;height:1060px;padding:34px 38px;';
    const s=d.stories[0];
    el('div','',`<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:3px double #000;padding-bottom:12px"><span class="serif" style="font-weight:900;font-size:40px">Weekfold</span><span class="src">${DAYN[i]} ${+d.date.slice(8)} Oct</span></div>`,c);
    photo(c,s.img,724,470).style.marginTop='22px';
    el('div','kick',s.cat,c).style.margin='22px 0 10px';
    el('div','hl',s.h,c);
    el('div','src',s.src,c).style.marginTop='16px';
    return c;
  });
  cap.add(.2,2.6,'Seven days of news.');
  cap.add(2.9,5.4,'Folded into one edition.',{cls:'serif-cap'});
  cap.add(5.7,8.6,'Every Sunday. <em>Free.</em>',{cls:'serif-cap'});
  const stack=el('div','','',stage); stack.style.cssText='position:absolute;left:0;top:0;width:1080px;height:1920px;';
  const brand=el('div','','',stage); brand.style.cssText='position:absolute;left:0;right:0;top:0;height:1920px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;background:#fff;z-index:30;';
  el('div','',logoSVG(170),brand); el('div','serif','Weekfold',brand).style.cssText='font-weight:900;font-size:150px;letter-spacing:-.03em';
  el('div','','weekfold.in',brand).style.cssText='font:500 44px Inter;color:#555;letter-spacing:.02em';
  return {dur:11.2,render(t){
    cap.render(t);
    cards.forEach((c,i)=>{
      const k=seg(t,.3+i*.28,.3+i*.28+.9,E5);           // slide in from right, fanned
      const g=seg(t,3.0,4.6,IO);                          // gather into one stack
      const x0=1200, x1=140+(i-3)*44, y1=560+(i-3)*22, r1=(i-3)*2.2;
      const x=lerp(lerp(x0,x1,k),140,g), y=lerp(lerp(600,y1,k),560,g), r=lerp(lerp(8,r1,k),0,g);
      const fade=1-seg(t,8.6,9.4);
      c.style.transform=`translate(${x-140}px,${y-560}px) rotate(${r}deg)`;
      c.style.opacity=k*fade; c.style.zIndex=10+i;
    });
    const b=seg(t,9.0,9.9,E3); brand.style.opacity=b; brand.style.transform=`translateY(${(1-b)*30}px)`;
  }};
};

/* ---------- 2. Map: where the news happened ---------- */
SCENES.map=({D,W},stage)=>{
  const cap=Captions(stage);
  cap.add(.2,3.0,'Every story has a place.',{top:150});
  cap.add(3.3,6.6,'Tap a pin. Read what happened.',{top:150,cls:'small'});
  cap.add(9.4,12.6,'The week on the map.',{top:150,cls:'serif-cap'});
  const box=el('div','','',stage); box.style.cssText='position:absolute;left:40px;top:640px;width:1000px;height:450px;background:#dfeaf2;border:2px solid #000;transform-origin:center;';
  const pins=D.days.flatMap(d=>d.stories).filter(s=>s.lat!=null);
  box.innerHTML=`<svg viewBox="0 0 1000 450" width="1000" height="450"><path d="${W}" fill="#f7f3e8" stroke="#9a9484" stroke-width=".6"/><g id="pins">${pins.map((s,i)=>{const q=proj(s.lat,s.lon);return `<g class="pin" transform="translate(${q[0].toFixed(1)},${q[1].toFixed(1)})"><circle class="ring" r="10" fill="none" stroke="${CAT[s.cat]}" stroke-width="2"/><circle class="dot" r="8" fill="${CAT[s.cat]}" stroke="#fff" stroke-width="2.2"/></g>`;}).join('')}</g></svg>`;
  const P=[...box.querySelectorAll('.pin')];
  const tip=el('div','card','',stage); tip.style.cssText='left:90px;top:1180px;width:900px;padding:34px 40px;';
  const picks=[pins.find(s=>s.h.startsWith('Iran')),pins.find(s=>s.h.startsWith('Brazil')),pins.find(s=>s.h.startsWith('Oslo'))].filter(Boolean);
  const cur=el('div','cursor',`<svg viewBox="0 0 24 24" width="44" height="44"><path d="M4 2l16 9-7 2-3 7z" fill="#fff" stroke="#000" stroke-width="1.6" stroke-linejoin="round"/></svg>`,stage);
  return {dur:13,render(t){
    cap.render(t);
    const z=lerp(1,1.9,seg(t,3.4,5.0,IO));
    const si=Math.min(picks.length-1,Math.floor(Math.max(0,t-4.2)/1.9));
    const s=picks[Math.max(0,si)], q=s?proj(s.lat,s.lon):[500,225];
    const zoomed=seg(t,3.4,5.0,IO), back=seg(t,9.2,10.4,IO);
    const Z=lerp(1,1.9,zoomed*(1-back));
    const tx=(500-q[0])*(Z-1)*(1000/1000), ty=(225-q[1])*(Z-1);
    box.style.transform=`translate(${tx}px,${ty}px) scale(${Z})`;
    P.forEach((p,i)=>{const k=seg(t,.4+i*.12,.4+i*.12+.5,E5);p.style.opacity=k;const d=p.querySelector('.dot');d.setAttribute('r',(8*k*(s===pins[i]&&zoomed>.5?1.6:1)).toFixed(2));const r=p.querySelector('.ring');const ph=((t*0.9+i*.37)%1);r.setAttribute('r',(8+ph*18).toFixed(1));r.setAttribute('opacity',(1-ph)*.7*k);});
    const show=t>4.2&&t<9.2; tip.style.opacity=show?seg(t,4.2+si*1.9,4.2+si*1.9+.35):0; tip.style.transform=`translateY(${(1-seg(t,4.2+si*1.9,4.2+si*1.9+.5))*20}px)`;
    if(s){tip.innerHTML=`<div class="kick">${s.cat}</div><div class="hl" style="margin-top:12px">${s.h}</div><div class="src" style="margin-top:14px">${s.src}</div>`;}
    const bx=40+500+tx, by=640+225+ty; const cx=s?bx+(q[0]-500)*Z:540, cy=s?by+(q[1]-225)*Z:865;
    const cv=seg(t,3.0,3.6)*(1-seg(t,9.0,9.5)); cur.style.opacity=cv; cur.style.left=(cx+6)+'px'; cur.style.top=(cy+6)+'px';
  }};
};

/* ---------- 3. Games: the mini + the word ---------- */
SCENES.games=({D},stage)=>{
  const cap=Captions(stage);
  cap.add(.2,3.2,'A new mini crossword. Every day.',{top:150,cls:'small'});
  cap.add(7.6,10.6,'And a word to guess.',{top:150,cls:'small'});
  cap.add(13.6,16.2,'Play free at <em>weekfold.in</em>',{top:150,cls:'small serif-cap'});
  const grid=['WHEAT','A#L#O','SPEED','T#C#A','ENTRY'], nums={'0,0':1,'0,2':2,'0,4':3,'2,0':4,'4,0':5};
  const cw=el('div','','',stage); cw.style.cssText='position:absolute;left:140px;top:560px;width:800px;';
  const g=el('div','','',cw); g.style.cssText='display:grid;grid-template-columns:repeat(5,150px);border:4px solid #000;width:758px;background:#000;gap:3px;';
  const cells=[];
  for(let r=0;r<5;r++)for(let c=0;c<5;c++){const d=el('div','','',g);const blk=grid[r][c]=='#';d.style.cssText=`height:150px;background:${blk?'#000':'#fff'};position:relative;font:700 86px/150px Inter;text-align:center;`;if(nums[r+','+c])el('span','',nums[r+','+c],d).style.cssText='position:absolute;left:8px;top:6px;font:600 24px/1 Inter;';const l=el('span','','',d);cells.push({r,c,blk,d,l});}
  const clue=el('div','card','',stage); clue.style.cssText='left:140px;top:1360px;width:800px;padding:30px 36px;';
  const order=[[0,0,'1 Across · Grain that becomes bread flour','WHEAT',[0,1]],[0,0,'1 Down · Rubbish','WASTE',[1,0]],[0,4,'3 Down · This very day','TODAY',[1,0]],[2,0,'4 Across · Velocity','SPEED',[0,1]],[0,2,'2 Down · Choose by ballot','ELECT',[1,0]],[4,0,'5 Across · Way in, or a contest submission','ENTRY',[0,1]]];
  // word game
  const wg=el('div','','',stage); wg.style.cssText='position:absolute;left:0;width:1080px;top:520px;display:flex;flex-direction:column;align-items:center;gap:14px;opacity:0';
  const ans='FOLDS', guesses=['CRANE','SOLID','FOLDS'];
  const tiles=guesses.map(gs=>{const row=el('div','','',wg);row.style.cssText='display:flex;gap:12px';return gs.split('').map(ch=>{const tt=el('div','',ch,row);tt.style.cssText='width:160px;height:160px;border:4px solid #d3d6da;font:700 84px/152px Inter;text-align:center;color:#111;';return tt;});});
  const kb=el('div','','',wg); kb.style.cssText='margin-top:30px;display:flex;flex-direction:column;gap:12px;align-items:center';
  ['QWERTYUIOP','ASDFGHJKL','ZXCVBNM'].forEach(r=>{const row=el('div','','',kb);row.style.cssText='display:flex;gap:10px';r.split('').forEach(ch=>{el('div','',ch,row).style.cssText='width:86px;height:112px;background:#d3d6da;border-radius:8px;font:700 36px/112px Inter;text-align:center';});});
  const KEYS=[...kb.querySelectorAll('div > div')];
  function score(g){const r=['a','a','a','a','a'],left={};for(let i=0;i<5;i++){if(g[i]===ans[i])r[i]='c';else left[ans[i]]=(left[ans[i]]||0)+1;}for(let i=0;i<5;i++){if(r[i]==='c')continue;if(left[g[i]]>0){r[i]='p';left[g[i]]--;}}return r;}
  const COL={c:'#6aaa64',p:'#c9b458',a:'#787c7e'};
  return {dur:17,render(t){
    cap.render(t);
    const cwIn=seg(t,.1,.8,E5), cwOut=seg(t,6.8,7.5,E3);
    cw.style.opacity=cwIn*(1-cwOut); cw.style.transform=`translateY(${(1-cwIn)*40}px) scale(${1-cwOut*.06})`;
    clue.style.opacity=cwIn*(1-cwOut);
    cells.forEach(c=>{if(!c.blk){c.d.style.background='#fff';c.l.textContent='';}});
    let ct=1.0, curClue='';
    order.forEach(([r0,c0,txt,word,dir])=>{
      const t0=ct, per=.17; ct+=per*5+.35;
      if(t>=t0-.3&&t<ct) curClue=txt;
      for(let i=0;i<5;i++){const cell=cells[(r0+dir[0]*i)*5+c0+dir[1]*i]; if(t>=t0+i*per){cell.l.textContent=word[i];} if(t>=t0-.3&&t<ct){cell.d.style.background=(t>=t0+i*per-per&&t<t0+i*per+.02)?'#ffda00':'#a7d8ff';}}
    });
    if(t>ct) cells.forEach(c=>{if(!c.blk)c.d.style.background='#d9f2dc';});
    clue.innerHTML=`<div class="kick">${t>ct?'Solved':'Clue'}</div><div class="hl" style="margin-top:10px;font-size:40px">${t>ct?'Nicely done. Back tomorrow for a new one.':curClue}</div>`;
    const wIn=seg(t,7.7,8.4,E5), wOut=seg(t,16.2,16.9); wg.style.opacity=wIn*(1-wOut); wg.style.transform=`translateY(${(1-wIn)*40}px)`;
    const best={};
    tiles.forEach((row,gi)=>{const base=8.6+gi*1.6; const sc=score(guesses[gi]); row.forEach((tt,i)=>{const typed=t>=base+i*.1; tt.style.opacity=typed?1:0; const fl=seg(t,base+.6+i*.12,base+.6+i*.12+.4); if(fl>0){const k=fl<.5?1-fl*2:(fl-.5)*2; tt.style.transform=`rotateX(${(1-k)*90}deg)`; if(fl>=.5){tt.style.background=COL[sc[i]];tt.style.borderColor=COL[sc[i]];tt.style.color='#fff';best[guesses[gi][i]]=(best[guesses[gi][i]]==='c'?'c':sc[i]);} } else {tt.style.transform='';tt.style.background='#fff';tt.style.borderColor=typed?'#878a8c':'#d3d6da';tt.style.color='#111';}});});
    KEYS.forEach(k=>{const b=best[k.textContent];k.style.background=b?COL[b]:'#d3d6da';k.style.color=b?'#fff':'#111';});
  }};
};

/* ---------- 4. Day by day: flip through the week ---------- */
SCENES.days=({D},stage)=>{
  const cap=Captions(stage);
  cap.add(.2,2.4,'One page for every day.',{top:150,cls:'small'});
  cap.add(11.2,14.0,'Read it in one sitting.',{top:150,cls:'small serif-cap'});
  const rail=el('div','','',stage); rail.style.cssText='position:absolute;left:0;width:1080px;top:420px;display:flex;justify-content:center;gap:12px;';
  const chips=DAYN.map((n,i)=>{const c=el('div','',n.slice(0,3),rail);c.style.cssText='width:120px;height:60px;border:2px solid #000;font:700 26px/56px Inter;text-align:center;background:#fff';return c;});
  const pages=D.days.map((d,i)=>{
    const p=el('div','card','',stage); p.style.cssText='left:90px;top:540px;width:900px;height:1180px;padding:40px 44px;opacity:0;';
    el('div','',`<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:3px solid #000;padding-bottom:12px"><span class="serif" style="font-weight:700;font-size:54px">${DAYN[i]}</span><span class="src">${+d.date.slice(8)} October · Day ${i+1} of 7</span></div>`,p);
    const s=d.stories[0]; photo(p,s.img,812,440).style.marginTop='24px';
    el('div','kick',s.cat,p).style.margin='20px 0 8px'; el('div','hl',s.h,p);
    const more=el('div','','',p); more.style.cssText='margin-top:26px;border-top:1px solid #ddd;padding-top:18px;display:flex;flex-direction:column;gap:14px';
    d.stories.slice(1).forEach(m=>{el('div','',`<span class="kick" style="font-size:18px">${m.cat}</span><div class="serif" style="font-weight:700;font-size:30px;line-height:1.2;margin-top:4px">${m.h}</div>`,more);});
    return p;
  });
  return {dur:14.6,render(t){
    cap.render(t);
    const per=1.35, start=1.6;
    const idx=clamp(Math.floor((t-start)/per),0,6);
    chips.forEach((c,i)=>{const on=i===idx&&t>=start;c.style.background=on?'#000':'#fff';c.style.color=on?'#fff':'#000';});
    pages.forEach((p,i)=>{const a=start+i*per, k=seg(t,a,a+.5,E5), out=seg(t,a+per,a+per+.5,E3); const vis=i===6?k*(1-seg(t,13.4,14.2)):k*(1-out); p.style.opacity=vis; p.style.transform=`translateX(${(1-k)*120-out*120}px) rotate(${(1-k)*2-out*2}deg)`; p.style.zIndex=10+i;});
  }};
};

/* ---------- 5. Sections + subscribe ---------- */
SCENES.sections=({D},stage)=>{
  const cap=Captions(stage);
  cap.add(.2,2.8,'Ten sections.',{top:150});
  cap.add(3.0,6.2,'Every story sourced.',{top:150});
  cap.add(6.4,9.6,'No ads. No paywall.',{top:150});
  cap.add(10.0,13.5,'Get it every <em>Sunday.</em>',{top:150,cls:'serif-cap'});
  const stories=D.days.flatMap(d=>d.stories).filter(s=>s.img);
  const cats=[...new Set(stories.map(s=>s.cat))];
  const grid=el('div','','',stage); grid.style.cssText='position:absolute;left:60px;top:520px;width:960px;display:grid;grid-template-columns:1fr 1fr;gap:28px;';
  const tiles=cats.slice(0,6).map(c=>{const s=stories.find(x=>x.cat===c);const t=el('div','','',grid);t.style.cssText=`border-top:6px solid ${CAT[c]};padding-top:14px;opacity:0`;photo(t,s.img,466,250);el('div','kick',c,t).style.margin='14px 0 6px';el('div','hl',s.h,t).style.cssText='font-size:26px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden';return t;});
  const form=el('div','card','',stage); form.style.cssText='left:90px;top:520px;width:900px;padding:60px 56px;opacity:0;';
  form.innerHTML=`<div class="serif" style="font-weight:700;font-size:64px;line-height:1.1">Get Weekfold every <em style="color:#1d3a6b">Sunday.</em></div><div class="src" style="font-size:28px;margin-top:18px">One email a week with the new edition. Free, one-click unsubscribe.</div><div style="margin-top:40px;border:3px solid #000;height:92px;font:400 32px/86px Inter;padding:0 24px;color:#333" id="inp"></div><div class="btn" style="margin-top:26px;width:100%;height:92px;font-size:30px">Subscribe free</div><div class="src" style="margin-top:34px;text-align:center;font-size:30px;color:#111;font-weight:600">weekfold.in</div>`;
  const inp=form.querySelector('#inp'); const typed='you@example.com';
  const sources=el('div','','',stage); sources.style.cssText='position:absolute;left:60px;right:60px;top:1760px;text-align:center;font:400 30px/1.5 Inter;color:#666;opacity:0';
  sources.textContent='Al Jazeera · Reuters · Associated Press · Africanews · Electrek · Democracy Now!';
  return {dur:15,render(t){
    cap.render(t);
    tiles.forEach((tl,i)=>{const k=seg(t,.4+i*.14,.4+i*.14+.6,E5), out=seg(t,9.5,10.1); tl.style.opacity=k*(1-out); tl.style.transform=`translateY(${(1-k)*40}px)`;});
    sources.style.opacity=seg(t,3.2,3.8)*(1-seg(t,9.3,9.8));
    const fk=seg(t,10.1,10.8,E5); form.style.opacity=fk; form.style.transform=`translateY(${(1-fk)*40}px)`;
    const n=Math.floor(clamp((t-11.0)/1.3)*typed.length); inp.textContent=typed.slice(0,n)+((t*2|0)%2&&t>10.8&&t<13.5?'|':'');
  }};
};
