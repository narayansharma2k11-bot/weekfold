const LOGO=`<svg viewBox="0 0 80 80"><g fill="none" stroke="currentColor"><rect x="12" y="10" width="54" height="54" stroke-width="4" transform="rotate(-6 39 37)"/><rect x="15" y="14" width="54" height="54" stroke-width="4" transform="rotate(4 42 41)"/><path d="M20 28L28 54L40 26L52 54L60 28" stroke-width="7" stroke-linejoin="round"/></g></svg>`;
const chip=()=>`<div class="chip"><i>${LOGO}</i>Weekfold</div>`;
const url=(t)=>`<div class="url">${t||'weekfold.in'}</div>`;
function spark(x,y,c,s){s=s||44;return `<svg class="spark" style="left:${x}px;top:${y}px;width:${s}px;height:${s}px" viewBox="0 0 40 40"><path d="M20 2 C22 14 26 18 38 20 C26 22 22 26 20 38 C18 26 14 22 2 20 C14 18 18 14 20 2Z" fill="${c||'#f7c948'}"/></svg>`}
function dot(x,y,c,s){return `<div style="position:absolute;left:${x}px;top:${y}px;width:${s}px;height:${s}px;border-radius:50%;background:${c}"></div>`}
// hand-drawn arrow from (x1,y1) to (x2,y2) with bend
function arrow(x1,y1,x2,y2,bend,col){bend=bend||.25;col=col||'#2a2830';const mx=(x1+x2)/2,my=(y1+y2)/2,dx=x2-x1,dy=y2-y1;const cx=mx-dy*bend,cy=my+dx*bend;
 const a=Math.atan2(y2-cy,x2-cx),L=30,s1=a+Math.PI*0.82,s2=a-Math.PI*0.82;
 return `<svg style="position:absolute;left:0;top:0;width:1080px;height:1920px;pointer-events:none;overflow:visible"><path d="M${x1} ${y1} Q${cx} ${cy} ${x2} ${y2}" fill="none" stroke="${col}" stroke-width="5" stroke-linecap="round"/><path d="M${x2+L*Math.cos(s1)} ${y2+L*Math.sin(s1)} L${x2} ${y2} L${x2+L*Math.cos(s2)} ${y2+L*Math.sin(s2)}" fill="none" stroke="${col}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>`}
const M=(x,y,size,o)=>`<div class="m" style="left:${x}px;top:${y}px">${mascot(Object.assign({size},o))}</div>`;
const hl=(y,t,fs)=>`<h1 class="hl" style="top:${y}px;${fs?'font-size:'+fs+'px':''}">${t}</h1>`;
const sub=(y,t)=>`<p class="sub" style="top:${y}px">${t}</p>`;
const note=(x,y,t,rot)=>`<div class="note" style="left:${x}px;top:${y}px;transform:rotate(${rot||-4}deg)">${t}</div>`;
function story(id,cls,inner){return `<div class="story ${cls}" id="${id}">${chip()}${inner}${url()}</div>`}
const head=(y,t,s,fs)=>`<div class="head" style="top:${y}px"><h1 style="${fs?'font-size:'+fs+'px':''}">${t}</h1>${s?`<p>${s}</p>`:''}</div>`;
const phone=(x,y,w,src,rot)=>`<div class="ph" style="left:${x}px;top:${y}px;width:${w}px;transform:rotate(${rot||0}deg)"><img src="${src}"></div>`;
const quiz=(x,y,w,q,opts,ok,rot)=>`<div class="card qz" style="left:${x}px;top:${y}px;width:${w}px;transform:rotate(${rot||0}deg)"><span class="qt">QUICK QUIZ</span><div class="qq">${q}</div>${opts.map((o,i)=>`<div class="qo${i===ok?' ok':''}"><b>${'ABCD'[i]}</b>${o}${i===ok?'<em>✓</em>':''}</div>`).join('')}</div>`;
const facts=(x,y,w,rows,rot)=>`<div class="card fc" style="left:${x}px;top:${y}px;width:${w}px;transform:rotate(${rot||0}deg)">${rows.map(r=>`<div><strong style="color:${r[2]||'#121212'}">${r[0]}</strong><span>${r[1]}</span></div>`).join('')}</div>`;
function kb(x,y,st){st=st||{};const R=['QWERTYUIOP','ASDFGHJKL','ZXCVBNM'];return `<div class="kb" style="left:${x}px;top:${y}px">${R.map(r=>`<div>${[...r].map(c=>`<i class="${st[c]||''}">${c}</i>`).join('')}</div>`).join('')}</div>`}
const pills=(x,y,w,items,hi)=>`<div class="pills" style="left:${x}px;top:${y}px;width:${w}px">${items.map((t,i)=>`<span class="${i===hi?'on':''}">${t}</span>`).join('')}</div>`;
