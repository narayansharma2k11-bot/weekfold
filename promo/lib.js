/* shared helpers for the Weekfold promo scenes */
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const E3=x=>1-Math.pow(1-x,3), E5=x=>1-Math.pow(1-x,5), IO=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const seg=(t,a,b,f=E3)=>f(clamp((t-a)/(b-a)));
const lerp=(a,b,k)=>a+(b-a)*k;
const el=(tag,cls,html,parent)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(html!=null)n.innerHTML=html;if(parent)parent.appendChild(n);return n;};
const CAT={World:'#1e3a6a',Politics:'#c0392b',Conflict:'#8e1b16',Business:'#b8860b',Tech:'#2f6fb5',Science:'#0b8a93',Climate:'#1f8a56',Sport:'#d9731a',Culture:'#7a4fd0',Health:'#0f9d8a'};
function proj(lat,lon){const l=lon*Math.PI/180,p=lat*Math.PI/180,p2=p*p,p4=p2*p2;const x=l*(0.8707-0.131979*p2+p4*(-0.013791+p4*(0.003971*p2-0.001529*p4)));const y=p*(1.007226+p2*(0.015085+p4*(-0.044475+0.028874*p2-0.005916*p4)));return[500+x*182.8,260-y*182.8];}
const DAYN=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
async function loadAll(){
  const D=await (await fetch('data.json')).json();
  const W=(await (await fetch('worldmap.txt')).text()).trim();
  const imgs=[...new Set(D.days.flatMap(d=>d.stories.map(s=>s.img)).filter(Boolean))];
  await Promise.all(imgs.map(u=>new Promise(r=>{const i=new Image();i.onload=i.onerror=r;i.src=u;})));
  return {D,W};
}
/* big captions: words blur in one by one, then leave together */
function Captions(stage){
  const items=[];
  return {
    add(t0,t1,html,o={}){
      const box=el('div','cap'+(o.cls?' '+o.cls:''),'',stage); box.style.top=(o.top!=null?o.top:200)+'px';
      if(o.size)box.style.fontSize=o.size+'px';
      const words=[];
      html.split(/(\s+)/).forEach(w=>{ if(/^\s+$/.test(w)){box.appendChild(document.createTextNode(' '));return;} const s=el('span','w',w,box); words.push(s); });
      items.push({t0,t1,box,words}); return box;
    },
    render(t){
      items.forEach(it=>{
        const on=t>=it.t0-.01&&t<=it.t1+.5; it.box.style.display=on?'block':'none'; if(!on)return;
        const out=seg(t,it.t1,it.t1+.4,E3);
        it.words.forEach((w,i)=>{const k=seg(t,it.t0+i*.08,it.t0+i*.08+.55,E3);
          const o=k*(1-out); w.style.opacity=o; w.style.filter=`blur(${(1-k)*14+out*10}px)`; w.style.transform=`translateY(${(1-k)*26-out*10}px)`;});
      });
    }
  };
}
function photo(parent,src,w,h,cls){const d=el('div','ph '+(cls||''),'',parent);d.style.width=w+'px';d.style.height=h+'px';if(src)d.style.backgroundImage=`url("${src}")`;return d;}
function logoSVG(sz){return `<svg width="${sz}" height="${sz}" viewBox="0 0 64 64"><g fill="none" stroke="#000" stroke-width="2.4"><rect x="10" y="8" width="42" height="42" transform="rotate(-6 31 29)"/><rect x="14" y="14" width="42" height="42" transform="rotate(4 35 35)" fill="#fff"/></g><path d="M22 26l5 16 5-12 5 12 5-16" fill="none" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/></svg>`;}
