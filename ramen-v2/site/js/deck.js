(() => {
  'use strict';
  const D = window.RAMEN_DATA, ps = D.products;
  const RED = '#b63e2b', TEAL = '#287a73', INK = '#252622', MUTED = '#66665f', LINE = '#d6cec0';
  const staticMode = new URLSearchParams(location.search).has('static');
  if (staticMode) document.body.classList.add('static');
  const fmt = (x, d = 0) => Number(x).toLocaleString('ko-KR', {maximumFractionDigits:d, minimumFractionDigits:d});
  const has = (p, ...keys) => keys.every(k => p[k] != null);
  const NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs, parent, text) {
    const e = document.createElementNS(NS, tag);
    for (const [k,v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function txt(svg, x, y, value, opts = {}) {
    return el('text', {x,y,fill:MUTED,'font-size':22,'dominant-baseline':'middle',...opts}, svg, value);
  }
  function svgHost(host, description) {
    const w = host.clientWidth, h = host.clientHeight;
    const svg = el('svg', {viewBox:`0 0 ${w} ${h}`,width:'100%',height:'100%',role:'img','aria-label':description});
    el('title', {}, svg, description);
    host.replaceChildren(svg);
    return {svg,w,h};
  }
  function bars(host, items, options = {}) {
    const {svg,w,h} = svgHost(host, options.title || host.getAttribute('aria-label'));
    const labelWidth = options.labelWidth || 155;
    const left = labelWidth, right = w - 118, top = 18, base = h - 45;
    const max = options.max || Math.ceil(Math.max(...items.map(p=>p.value))*1.12/100)*100;
    const scale = (right-left)/max;
    for (let i=0;i<=4;i++) {
      const x=left+(right-left)*i/4;
      el('line',{x1:x,x2:x,y1:top,y2:base,stroke:LINE},svg);
      txt(svg,x,base+25,fmt(max*i/4),{'text-anchor':'middle','font-size':19});
    }
    const slot=(base-top)/items.length;
    items.forEach((p,i)=>{
      const y=top+slot*(i+.5), bh=Math.min(39,slot*.57);
      txt(svg,left-18,y,p.label,{'text-anchor':'end','font-size':options.labelSize||23,fill:INK});
      const bar=el('rect',{x:left,y:y-bh/2,width:p.value*scale,height:bh,fill:p.color||RED,class:'bar'},svg);
      el('title',{},bar,`${p.label}: ${fmt(p.value,options.decimals||0)} ${options.unit||''}`);
      txt(svg,left+p.value*scale+13,y,fmt(p.value,options.decimals||0),{fill:INK,'font-size':23,'font-weight':700});
    });
  }
  function vertical(host, items, options={}) {
    const {svg,w,h} = svgHost(host, host.getAttribute('aria-label'));
    const left=90,right=w-22,top=40,base=h-65;
    const max=Math.ceil(Math.max(...items.map(p=>p.value))*1.18/100)*100;
    for(let i=0;i<=4;i++) {
      const value=max*i/4,y=base-(base-top)*i/4;
      el('line',{x1:left,x2:right,y1:y,y2:y,stroke:LINE},svg);
      txt(svg,left-15,y,fmt(value),{'text-anchor':'end','font-size':21});
    }
    const slot=(right-left)/items.length,bw=Math.min(slot*.40,110);
    items.forEach((p,i)=>{
      const cx=left+slot*(i+.5),y=base-p.value/max*(base-top);
      el('rect',{x:cx-bw/2,y,width:bw,height:base-y,fill:p.color||RED},svg);
      txt(svg,cx,y-18,fmt(p.value,options.decimals||0),{'text-anchor':'middle',fill:INK,'font-size':25,'font-weight':700});
      txt(svg,cx,base+29,p.label,{'text-anchor':'middle',fill:INK,'font-size':23});
    });
  }
  function scatter(host, points, xkey, ykey, xlabel, ylabel, options={}) {
    const {svg,w,h}=svgHost(host,host.getAttribute('aria-label'));
    const left=102,right=w-40,top=44,base=h-83;
    const xv=points.map(p=>p[xkey]), yv=points.map(p=>p[ykey]);
    const domain=(v)=>{const mi=Math.min(...v),ma=Math.max(...v),span=ma-mi||1;return [Math.max(0,mi-span*.14),ma+span*.14];};
    const [xmin,xmax]=domain(xv),[ymin,ymax]=domain(yv);
    const X=v=>left+(v-xmin)/(xmax-xmin)*(right-left),Y=v=>base-(v-ymin)/(ymax-ymin)*(base-top);
    for(let i=0;i<=4;i++) {
      const x=left+(right-left)*i/4,y=base-(base-top)*i/4;
      el('line',{x1:left,x2:right,y1:y,y2:y,stroke:LINE},svg);
      txt(svg,x,base+25,fmt(xmin+(xmax-xmin)*i/4),{'text-anchor':'middle','font-size':19});
      txt(svg,left-14,y,fmt(ymin+(ymax-ymin)*i/4),{'text-anchor':'end','font-size':19});
    }
    txt(svg,(left+right)/2,h-12,xlabel,{'text-anchor':'middle','font-size':22,fill:INK});
    txt(svg,left,15,ylabel,{'font-size':22,fill:INK});
    const mx=xv.reduce((a,b)=>a+b)/xv.length,my=yv.reduce((a,b)=>a+b)/yv.length;
    const slope=xv.reduce((s,x,i)=>s+(x-mx)*(yv[i]-my),0)/xv.reduce((s,x)=>s+(x-mx)**2,0);
    const trendx=[Math.min(...xv),Math.max(...xv)];
    const id='clip-'+host.dataset.chart;
    const defs=el('defs',{},svg),clip=el('clipPath',{id},defs);
    el('rect',{x:left,y:top,width:right-left,height:base-top},clip);
    el('line',{x1:X(trendx[0]),x2:X(trendx[1]),y1:Y(my+slope*(trendx[0]-mx)),y2:Y(my+slope*(trendx[1]-mx)),stroke:MUTED,'stroke-width':2,'stroke-dasharray':'8 7','clip-path':`url(#${id})`},svg);
    points.forEach((p)=>{
      const samePrice=options.highlight && p['개당가격_원']===1080;
      const c=el('circle',{cx:X(p[xkey]),cy:Y(p[ykey]),r:p.is_outlier?10:8,fill:samePrice?TEAL:RED,opacity:samePrice?1:.72,stroke:'#f5f0e6','stroke-width':2},svg);
      el('title',{},c,`${p['브랜드']} ${p['제품명']} / ${fmt(p[xkey],1)} / ${fmt(p[ykey],1)}`);
      if(samePrice) txt(svg,X(p[xkey])+14,Y(p[ykey])+(p['중량_g']===65?20:-20),`${p['중량_g']}g`,{fill:TEAL,'font-size':23,'font-weight':700});
      if(options.highlight && p.is_outlier) txt(svg,X(p[xkey])-14,Y(p[ykey])-23,'치즈불닭 · 포함',{'text-anchor':'end',fill:RED,'font-size':21});
    });
  }
  const meanItems=(stats,key)=>stats.filter(p=>p[key].n).map(p=>({label:`${p.label} (n=${p[key].n})`,value:p[key].mean}));
  const builders={
    brandCount:h=>bars(h,D.brand_stats.map(p=>({label:p.label,value:p.n})),{max:16}),
    priceBrand:h=>vertical(h,meanItems(D.brand_stats,'개당가격_원')),
    price100:h=>vertical(h,meanItems(D.brand_stats,'100g당_가격_원')),
    priceWeight:h=>scatter(h,ps.filter(p=>has(p,'개당가격_원','중량_g')),'개당가격_원','중량_g','個당 가격 (원/개)'.replace('個','개'),'중량 (g)',{highlight:true}),
    kcal:h=>bars(h,ps.filter(p=>has(p,'열량_kcal')).sort((a,b)=>a['열량_kcal']-b['열량_kcal']).map(p=>({label:`${p['브랜드']} ${p['제품명'].replace('아리 모던누들 ','').replace('팔도 ','')}`,value:p['열량_kcal']})),{labelWidth:450,labelSize:23,max:600,unit:'kcal/개'}),
    priceKcal:h=>scatter(h,ps.filter(p=>has(p,'개당가격_원','열량_kcal')),'개당가격_원','열량_kcal','개당 가격 (원/개)','열량 (kcal/개)'),
    sodiumBrand:h=>vertical(h,meanItems(D.brand_stats,'나트륨_mg')),
    weightSodium:h=>scatter(h,ps.filter(p=>has(p,'중량_g','나트륨_mg')),'중량_g','나트륨_mg','중량 (g)','나트륨 (mg/개)'),
    categorySodium:h=>vertical(h,meanItems(D.category_stats,'나트륨_mg').map((p,i)=>({...p,color:i?TEAL:RED}))),
    categorySugar:h=>{
      const items=meanItems(D.category_stats,'당류_g').map((p,i)=>({...p,color:i?TEAL:RED}));
      bars(h,items,{max:12,decimals:1,labelWidth:160});
    },
    valueRank:h=>{
      const a=ps.filter(p=>has(p,'100g당_가격_원')).sort((a,b)=>a['100g당_가격_원']-b['100g당_가격_원']);
      bars(h,[...a.slice(0,5),...a.slice(-5)].map((p,i)=>({label:`${p['브랜드']} ${p['제품명']}`,value:p['100g당_가격_원'],color:i<5?TEAL:RED})),{labelWidth:470,labelSize:23,max:3000,unit:'원/100g'});
    }
  };
  const slides=[...document.querySelectorAll('.slide')];
  const deck=document.getElementById('deck');
  let current=-1;
  function renderAll(){document.querySelectorAll('[data-chart]').forEach(h=>builders[h.dataset.chart](h));}
  function goTo(index){
    const i=Math.max(0,Math.min(slides.length-1,index));
    if(i===current)return;
    current=i;
    slides.forEach((s,k)=>{s.classList.toggle('is-active',k===i);s.setAttribute('aria-hidden',String(k!==i));s.inert=k!==i;});
    document.getElementById('curNo').textContent=i+1;
    document.getElementById('progressBar').style.width=`${(i+1)/slides.length*100}%`;
    document.getElementById('prevBtn').disabled=i===0;
    document.getElementById('nextBtn').disabled=i===slides.length-1;
    document.querySelectorAll('#steps span').forEach((s,k)=>s.classList.toggle('on',k===[0,0,1,1,2,2,2,2,2,3,3,4][i]));
    history.replaceState(null,'',`#${i+1}`);
  }
  function fit(){
    const reserve=document.querySelector('.hud').getBoundingClientRect().height;
    const scale=Math.min(innerWidth/1920,(innerHeight-reserve)/1080);
    deck.style.transform=`translateY(${-reserve/2}px) scale(${scale})`;
  }
  async function fullscreen(){
    try {if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}
    catch(e){document.getElementById('fsBtn').setAttribute('aria-label','이 브라우저에서 전체화면을 사용할 수 없습니다');}
  }
  document.getElementById('prevBtn').onclick=()=>goTo(current-1);
  document.getElementById('nextBtn').onclick=()=>goTo(current+1);
  document.getElementById('fsBtn').onclick=fullscreen;
  addEventListener('keydown',e=>{
    if(e.altKey||e.ctrlKey||e.metaKey||/INPUT|TEXTAREA|SELECT/.test(e.target.tagName))return;
    if(e.target.closest('button,a')&&(e.key===' '||e.key==='Enter'))return;
    if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();goTo(current+1);}
    else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();goTo(current-1);}
    else if(e.key==='Home'){e.preventDefault();goTo(0);}
    else if(e.key==='End'){e.preventDefault();goTo(slides.length-1);}
    else if(e.key.toLowerCase()==='f')fullscreen();
  });
  let startX=0;
  addEventListener('touchstart',e=>{startX=e.touches[0].clientX;},{passive:true});
  addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-startX;if(Math.abs(dx)>65)goTo(current+(dx<0?1:-1));},{passive:true});
  addEventListener('resize',fit);
  addEventListener('hashchange',()=>goTo((Number(location.hash.slice(1))||1)-1));
  addEventListener('beforeprint',()=>{
    slides.forEach(s=>{s.inert=false;s.removeAttribute('aria-hidden');});
    renderAll();
  });
  addEventListener('afterprint',()=>slides.forEach((s,k)=>{s.inert=k!==current;s.setAttribute('aria-hidden',String(k!==current));}));
  renderAll();fit();goTo((Number(location.hash.slice(1))||1)-1);
})();
