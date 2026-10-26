/* shared map: WFMap(E, EDS, hrefFn) wires up #mapbox, #pins, #grat, #tip, #picked, #fbars, #sc-week, #sc-month, #map-count, #mapnote */
function WFMap(E, EDS, href){
  var NS = 'http://www.w3.org/2000/svg';
  function fmt(iso, o){ return new Date(iso + 'T12:00:00Z').toLocaleDateString('en-GB', Object.assign({ timeZone:'UTC' }, o)); }
  function el(tag, attrs, kids){ var n = document.createElement(tag); if (attrs) for (var k in attrs){ if (k === 'text') n.textContent = attrs[k]; else if (k === 'cls') n.className = attrs[k]; else n.setAttribute(k, attrs[k]); } (kids || []).forEach(function(c){ if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); }); return n; }
  function sv(tag, attrs){ var n = document.createElementNS(NS, tag); for (var k in attrs) n.setAttribute(k, attrs[k]); return n; }
  function txt(s){ return s.dek || s.summary || ''; }
  function stories(ed){ var a = []; ed.days.forEach(function(d){ [d.lead].concat(d.more || []).forEach(function(s, k){ a.push({ s: s, d: d, k: k, ed: ed }); }); }); return a; }
  var BRIGHT = { World:'#1e3a6a', Politics:'#c0392b', Conflict:'#8e1b16', Business:'#b8860b', Tech:'#2f6fb5', Science:'#0b8a93', Climate:'#1f8a56', Sport:'#d9731a', Culture:'#7a4fd0', Health:'#0f9d8a' };
  function bright(c){ return BRIGHT[c] || '#333'; }
  /* ================= THE MAP ================= */
  /* places named in stories -> [lat, lon]; checked in this order, so specific places come before countries */
  var PLACES = [
    ['Strait of Hormuz',26.6,56.3],['Hormuz',26.6,56.3],['Red Sea',20,38.5],['Gaza',31.4,34.4],['West Bank',31.9,35.2],['Tel Aviv',32.08,34.78],['Jerusalem',31.77,35.21],
    ['Kyiv',50.45,30.52],['Pryluky',50.59,32.39],['Kharkiv',49.99,36.23],['Odesa',46.48,30.72],['Moscow',55.75,37.62],['Duma',55.75,37.62],['Kremlin',55.75,37.62],
    ['Riyadh',24.71,46.68],['Abha',18.22,42.5],['Aden',12.79,45.03],['Sanaa',15.37,44.19],['Houthi',15.37,44.19],['Djibouti',11.6,43.15],['Dubai',25.2,55.27],['FlyDubai',25.2,55.27],['Doha',25.29,51.53],['Qatar',25.29,51.53],['Tehran',35.69,51.39],
    ['Erbil',36.19,44.01],['Baghdad',33.31,44.36],['Istanbul',41.01,28.98],['Ankara',39.93,32.86],
    ['Tigray',13.5,39.47],['Addis Ababa',9.03,38.74],['Johannesburg',-26.2,28.05],['Cape Town',-33.92,18.42],['Nairobi',-1.29,36.82],['Kenyan',-1.29,36.82],
    ['Peshawar',34.01,71.58],['Khyber',34.01,71.58],['Islamabad',33.68,73.05],['Delhi',28.61,77.21],['Mumbai',19.08,72.88],['RBI',19.08,72.88],['Modi',28.61,77.21],['Colombo',6.93,79.86],['Sri Lanka',7.87,80.77],
    ['Rakhine',20.15,92.9],['Myanmar',19.75,96.1],['Bangkok',13.75,100.5],['Thai',13.75,100.5],['Pinglu',21.95,108.62],['Qinzhou',21.95,108.62],['Beijing',39.9,116.4],['China Open',39.9,116.4],['Xi ',39.9,116.4],['Samsung',37.57,126.98],['Seoul',37.57,126.98],['Tokyo',35.68,139.69],['Japan',35.68,139.69],
    ['Brussels',50.85,4.35],[' EU ',50.85,4.35],['The Hague',52.08,4.3],['Criminal Court',52.08,4.3],['ICC',52.08,4.3],['Amsterdam',52.37,4.9],['Paris',48.86,2.35],['France',48.86,2.35],['French',48.86,2.35],['Le Pen',48.86,2.35],['Madrid',40.42,-3.7],['Spain',40.42,-3.7],['Sánchez',40.42,-3.7],['Villarreal',39.94,-0.1],
    ['London',51.51,-0.13],[' UK ',51.51,-0.13],['Britain',51.51,-0.13],['Sally Rooney',51.51,-0.13],['Saxony-Anhalt',52.13,11.63],['Mecklenburg',53.63,11.41],['Munich',48.14,11.58],['Berlin',52.52,13.4],['Germany',52.52,13.4],['Merz',52.52,13.4],['Klopp',52.52,13.4],
    ['Swiss',46.56,8.07],['Switzerland',46.56,8.07],['Serbia',44.79,20.45],['Vucic',44.79,20.45],['Latvia',56.95,24.11],['Stockholm',59.33,18.07],['Swedish Academy',59.33,18.07],['Nobel Peace',59.91,10.75],['Nobel',59.33,18.07],['Denmark',55.68,12.57],['Portugal',38.72,-9.14],
    ['Quebec',46.81,-71.21],['Québec',46.81,-71.21],['Ontario',43.65,-79.38],['Canadian',45.42,-75.7],
    ['UN General Assembly',40.75,-73.97],['General Assembly',40.75,-73.97],['at the UN',40.75,-73.97],['New York',40.71,-74.01],['Chicago',41.88,-87.63],['Illinois',41.76,-88.32],['Oregon',44.06,-121.31],['Florida',30.39,-86.5],['Fort Hood',31.13,-97.78],['Missouri',38.57,-92.17],['NASA',38.88,-77.02],
    ['White House',38.9,-77.04],['Washington',38.9,-77.04],['Supreme Court',38.89,-77.0],['Trump',38.9,-77.04],['Wall Street',40.71,-74.01],['US ',38.9,-77.04],['U.S.',38.9,-77.04],
    ['Baja California',24.14,-110.31],['Mexico',19.43,-99.13],['Panama',8.98,-79.52],['Costa Rica',9.93,-84.08],['El Salvador',13.69,-89.22],
    ['Brazil',-15.79,-47.88],['Lula',-15.79,-47.88],['Bolsonaro',-15.79,-47.88],['Vinícius',40.45,-3.69],['Real Madrid',40.45,-3.69],['Chile',-33.45,-70.67],['Robinson Crusoe',-33.64,-78.83],['Buenos Aires',-34.6,-58.38],
    ['Sydney',-33.87,151.21],['Australia',-35.28,149.13],
    ['Iran',35.69,51.39],['Israel',31.77,35.21],['Netanyahu',31.77,35.21],['Ukraine',50.45,30.52],['Russia',55.75,37.62],['Putin',55.75,37.62],['Saudi',24.71,46.68],['Yemen',15.37,44.19],['India',28.61,77.21],['Pakistan',33.68,73.05],['China',39.9,116.4],['Turkey',39.93,32.86],['Turkish',39.93,32.86],['South Africa',-25.75,28.19],['Ethiopia',9.03,38.74],['Iraq',33.31,44.36],['G7',45.5,9.2],['Oil',26.6,56.3],['Brent',26.6,56.3]
  ];
  function place(s){
    var t = ' ' + s.headline + ' ' + txt(s) + ' ';
    for (var i = 0; i < PLACES.length; i++){ if (t.indexOf(PLACES[i][0]) >= 0) return PLACES[i]; }
    return null;
  }
  function proj(lat, lon){
    var l = lon * Math.PI / 180, p = lat * Math.PI / 180, p2 = p * p, p4 = p2 * p2;
    var x = l * (0.8707 - 0.131979 * p2 + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4)));
    var y = p * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)));
    return [500 + x * 182.8, 260 - y * 182.8];
  }
  /* graticule */
  (function(){
    var g = document.getElementById('grat');
    for (var lat = -45; lat <= 75; lat += 30){ var d = ''; for (var lon = -180; lon <= 180; lon += 6){ var q = proj(lat, lon); d += (d ? 'L' : 'M') + q[0].toFixed(1) + ',' + q[1].toFixed(1); } g.appendChild(sv('path', { d: d, 'class':'grat' })); }
    for (var lo = -150; lo <= 180; lo += 30){ var d2 = ''; for (var la = -58; la <= 84; la += 4){ var q2 = proj(la, lo); d2 += (d2 ? 'L' : 'M') + q2[0].toFixed(1) + ',' + q2[1].toFixed(1); } g.appendChild(sv('path', { d: d2, 'class':'grat' })); }
  })();
  var pinsG = document.getElementById('pins'), tip = document.getElementById('tip'), picked = document.getElementById('picked'), mapbox = document.getElementById('mapbox');
  var scope = 'week', off = {}, PINS = [];
  function pool(){ return scope === 'week' ? stories(E) : EDS.slice(0, 4).reduce(function(a, ed){ return a.concat(ed.partial ? [] : stories(ed)); }, []); }
  function drawPins(){
    pinsG.innerHTML = ''; PINS = [];
    var seen = {};
    pool().forEach(function(x){
      var pl = place(x.s); if (!pl) return;
      var key = pl[1] + ',' + pl[2], n = seen[key] = (seen[key] || 0) + 1;
      var q = proj(pl[1], pl[2]), a = n * 2.4, r = n > 1 ? 10 + n * 2 : 0;
      var cx = q[0] + Math.cos(a) * r, cy = q[1] + Math.sin(a) * r;
      var g = sv('g', { 'class':'pin', tabindex:'0', role:'link', 'aria-label': x.s.category + ': ' + x.s.headline, transform:'translate(' + cx.toFixed(1) + ',' + cy.toFixed(1) + ')' });
      g.appendChild(sv('circle', { 'class':'ring', r:'10', stroke: bright(x.s.category), style:'animation-delay:' + (Math.random() * 2.4).toFixed(2) + 's' }));
      g.appendChild(sv('circle', { 'class':'dot', r:'8', fill: bright(x.s.category) }));
      g._x = x; g._p = [cx, cy];
      g.addEventListener('mouseenter', function(){ showTip(g); });
      g.addEventListener('focus', function(){ showTip(g); });
      g.addEventListener('mouseleave', hideTip);
      g.addEventListener('blur', hideTip);
      g.addEventListener('click', function(){ pick(g); });
      g.addEventListener('keydown', function(e){ if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); pick(g); } });
      pinsG.appendChild(g); PINS.push(g);
    });
    applyFilter(); bars();
  }
  function showTip(g){
    var x = g._x, r = mapbox.getBoundingClientRect(), k2 = r.width / 1000;
    tip.innerHTML = ''; tip.appendChild(el('p', { cls:'c', text: x.s.category + ' · ' + fmt(x.d.date, { weekday:'short', day:'numeric', month:'short' }) })); tip.appendChild(el('b', { text: x.s.headline })); tip.appendChild(el('span', { text: 'Click the pin to read it' }));
    var left = g._p[0] * k2 + 14, top = g._p[1] * k2 - 10;
    if (left + 300 > r.width) left = Math.max(6, g._p[0] * k2 - 314);
    tip.style.left = left + 'px'; tip.style.top = Math.max(6, Math.min(top, r.height - 120)) + 'px'; tip.classList.add('on');
  }
  function hideTip(){ tip.classList.remove('on'); }
  function pick(g){
    PINS.forEach(function(p){ p.classList.toggle('on', p === g); });
    var x = g._x; picked.innerHTML = '';
    picked.appendChild(el('span', { cls:'c', text: x.s.category + ' · ' + fmt(x.d.date, { weekday:'long', day:'numeric', month:'long' }) }));
    picked.appendChild(el('b', { text: x.s.headline }));
    picked.appendChild(el('p', { text: txt(x.s) }));
    picked.appendChild(el('a', { href: href(x), text: 'Read the story →' }));
  }
  function applyFilter(){ PINS.forEach(function(p){ p.classList.toggle('off', !!off[p._x.s.category]); }); var vis = PINS.filter(function(p){ return !off[p._x.s.category]; }).length; document.getElementById('map-count').textContent = vis + ' stories pinned'; }
  var fb = document.getElementById('fbars');
  function bars(){
    var counts = {}, all = pool(); all.forEach(function(x){ counts[x.s.category] = (counts[x.s.category] || 0) + 1; });
    var cats = Object.keys(counts).sort(function(a, b){ return counts[b] - counts[a]; }), max = counts[cats[0]] || 1;
    fb.innerHTML = '';
    cats.forEach(function(c){
      var fill = el('span', { cls:'fill', style:'background:' + bright(c) });
      var b = el('button', { cls:'fbar', type:'button', 'aria-pressed': String(!off[c]), title:'Show or hide ' + c }, [ el('span', { text: c }), el('span', { cls:'track' }, [ fill ]), el('span', { cls:'n', text: String(counts[c]) }) ]);
      b.addEventListener('click', function(){ off[c] = !off[c]; b.setAttribute('aria-pressed', String(!off[c])); applyFilter(); });
      fb.appendChild(b);
      requestAnimationFrame(function(){ setTimeout(function(){ fill.style.width = (counts[c] / max * 100) + '%'; }, 60); });
    });
    var pinned = PINS.length;
    document.getElementById('mapnote').textContent = pinned + ' of ' + all.length + ' stories have a place on the map. Tap a section to hide or show it.';
  }
  function setScope(s){ scope = s; document.getElementById('sc-week').setAttribute('aria-pressed', String(s === 'week')); document.getElementById('sc-month').setAttribute('aria-pressed', String(s !== 'week')); drawPins(); }
  document.getElementById('sc-week').addEventListener('click', function(){ setScope('week'); });
  document.getElementById('sc-month').addEventListener('click', function(){ setScope('month'); });
  drawPins();

}
