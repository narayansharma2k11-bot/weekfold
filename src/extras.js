/* Weekfold extras: Listen (your device's own voice, free, no account), story boxes (at a glance, where the reports
   differ, what to watch, what it could mean for India), words explained, timelines and share links.
   Data: WF_GLOSSARY and WF_TIMELINES are filled in by build.py. Nothing here talks to any server. */
(function(){
  var S = window.speechSynthesis, KEY = 'weekfoldVoice';
  var FEM = /female|serena|kate|libby|sonia|hazel|susan|fiona|martha|stephanie|samantha|karen|moira|tessa|amy|emma|zira|heera|neerja|catherine|isla|sara/i;
  var MAL = /male|daniel|george|ryan|arthur|oliver|thomas|james|harry|alfie|rishi|prabhat|ravi|hemant|gordon/i;
  function voices(){ return ((S && S.getVoices()) || []).filter(function(x){ return /^en/i.test(x.lang); }); }
  function pickVoice(){
    var saved = null; try { saved = localStorage.getItem(KEY); } catch (e) {}
    var v = voices();
    if (saved && saved !== 'auto'){ var m = v.filter(function(x){ return x.name === saved; })[0]; if (m) return m; }
    return v.filter(function(x){ return /^en[-_]GB/i.test(x.lang) && MAL.test(x.name) && !FEM.test(x.name); })[0]
      || v.filter(function(x){ return /^en[-_]GB/i.test(x.lang); })[0] || v.filter(function(x){ return /^en[-_]IN/i.test(x.lang); })[0] || v[0] || null;
  }
  function el(tag, attrs, kids){ var n = document.createElement(tag); if (attrs) for (var k in attrs){ if (k === 'text') n.textContent = attrs[k]; else if (k === 'cls') n.className = attrs[k]; else n.setAttribute(k, attrs[k]); } (kids || []).forEach(function(c){ if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); }); return n; }

  var active = null;
  function listenBar(text, label){
    var box = el('div', { cls:'listen' });
    if (!S || !window.SpeechSynthesisUtterance){ box.hidden = true; return box; }
    var play = el('button', { type:'button', cls:'lplay', text: label }), stop = el('button', { type:'button', cls:'lstop', text:'■ Stop' });
    var speed = el('select', { 'aria-label':'Reading speed' }); ['0.75', '1', '1.25', '1.5', '1.75', '2'].forEach(function(r){ var o = el('option', { value:r, text: r + '×' }); if (r === '1') o.selected = true; speed.appendChild(o); });
    var vsel = el('select', { 'aria-label':'Voice' }), msg = el('span', { cls:'lmsg' });
    stop.hidden = true;
    box.appendChild(play); box.appendChild(stop); box.appendChild(el('label', null, ['Speed ', speed])); box.appendChild(el('label', null, ['Voice ', vsel])); box.appendChild(msg);
    function fill(){
      var cur = 'auto'; try { cur = localStorage.getItem(KEY) || 'auto'; } catch (e) {}
      vsel.innerHTML = ''; vsel.appendChild(el('option', { value:'auto', text:'Auto (UK male if your device has one)' }));
      voices().forEach(function(x){ vsel.appendChild(el('option', { value: x.name, text: x.name + ' (' + x.lang + ')' })); });
      vsel.value = cur; if (vsel.value !== cur) vsel.value = 'auto'; shown();
    }
    function shown(){ var v = pickVoice(); msg.textContent = v ? 'Voice: ' + v.name + '. Free, read by your own device.' : 'Your device’s default voice. Free, read by your own device.'; }
    fill(); if (S.addEventListener) S.addEventListener('voiceschanged', fill); else S.onvoiceschanged = fill;
    vsel.addEventListener('change', function(){ try { localStorage.setItem(KEY, vsel.value); } catch (e) {} shown(); });
    var parts = text.match(/[^.!?]+[.!?]*/g) || [text], i = 0, on = false, gen = 0;
    function reset(){ on = false; i = 0; play.textContent = label; stop.hidden = true; if (active === box) active = null; }
    function next(g){
      if (!on || g !== gen) return; if (i >= parts.length){ reset(); return; }
      var u = new SpeechSynthesisUtterance(parts[i++].trim()), v = pickVoice(); if (v){ u.voice = v; u.lang = v.lang; }
      u.rate = parseFloat(speed.value) || 1; u.onend = function(){ next(g); }; u.onerror = function(){ if (g === gen) reset(); }; S.speak(u);
    }
    function start(){ if (active && active !== box) active.stopNow(); gen++; S.cancel(); on = true; active = box; play.textContent = '⏸ Pause'; stop.hidden = false; shown(); next(gen); }
    function pause(){ gen++; S.cancel(); on = false; if (i > 0) i--; play.textContent = '▶ Resume'; }
    box.stopNow = function(){ gen++; S.cancel(); reset(); };
    play.addEventListener('click', function(){ if (on) pause(); else start(); });
    stop.addEventListener('click', function(){ box.stopNow(); });
    return box;
  }
  function stopAll(){ if (active) active.stopNow(); else if (S) S.cancel(); }
  window.addEventListener('beforeunload', function(){ if (S) S.cancel(); });

  function storyText(s){ return [s.headline, s.dek].concat(s.body || []).concat(s.why ? ['Why it matters. ' + s.why] : []).map(function(x){ x = String(x).trim(); return /[.!?]$/.test(x) ? x : x + '.'; }).join(' '); }

  var FACT = [['who', 'Who'], ['what', 'What'], ['where', 'Where'], ['when', 'When'], ['why', 'Why'], ['how', 'How'], ['howMuch', 'How much']];
  function factsBox(s){
    var f = s.facts; if (!f) return null;
    var dl = el('dl');
    FACT.forEach(function(p){ if (f[p[0]]){ dl.appendChild(el('dt', { text: p[1] })); dl.appendChild(el('dd', { text: f[p[0]] })); } });
    return dl.children.length ? el('div', { cls:'xbox glance' }, [ el('b', { text:'At a glance' }), dl ]) : null;
  }
  function textBox(cls, title, txt, note){
    if (!txt) return null;
    var list = Array.isArray(txt) ? txt : [txt], kids = [ el('b', { text: title }) ];
    if (note) kids.push(el('span', { cls:'xnote', text: note }));
    list.forEach(function(t){ kids.push(el('p', { text: t })); });
    return el('div', { cls:'xbox ' + cls }, kids);
  }
  function rx(m){ return new RegExp('(^|[^a-z])' + m.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[^a-z])'); }
  function hay(s){ return (s.headline + ' ' + (s.dek || '') + ' ' + (s.body || []).join(' ')).toLowerCase(); }
  function words(s){
    var g = window.WF_GLOSSARY || [], t = hay(s), hits = g.filter(function(x){ return (x.match || [x.term]).some(function(m){ return rx(m).test(t); }); }).slice(0, 6);
    if (!hits.length) return null;
    var box = el('div', { cls:'xbox words' }, [ el('b', { text:'Words in this story' }) ]);
    hits.forEach(function(x){ box.appendChild(el('details', null, [ el('summary', { text: x.term }), el('p', { text: x.def }) ])); });
    box.appendChild(el('a', { href:'glossary.html', cls:'xmore', text:'All words explained →' }));
    return box;
  }
  function timelinesFor(s){
    var t = (s.headline + ' ' + (s.dek || '')).toLowerCase();
    return (window.WF_TIMELINES || []).filter(function(x){
      if (s.timeline) return [].concat(s.timeline).indexOf(x.slug) >= 0;
      return x.match.some(function(m){ return t.indexOf(m) >= 0; }) && !(x.exclude || []).some(function(m){ return t.indexOf(m) >= 0; });
    });
  }
  function tlBox(s){
    var tl = timelinesFor(s); if (!tl.length) return null;
    var box = el('div', { cls:'xbox tlx' }, [ el('b', { text:'How we got here' }) ]);
    tl.forEach(function(x){ box.appendChild(el('a', { href:'timeline-' + x.slug + '.html', text: x.title + ': every story so far →' })); });
    return box;
  }
  function shareRow(s, url){
    var t = s.headline + ' · Weekfold', e = encodeURIComponent;
    var row = el('div', { cls:'share' }, [ el('b', { text:'Share' }),
      el('a', { href:'https://wa.me/?text=' + e(t + ' ' + url), target:'_blank', rel:'noopener', text:'WhatsApp' }),
      el('a', { href:'https://t.me/share/url?url=' + e(url) + '&text=' + e(t), target:'_blank', rel:'noopener', text:'Telegram' }),
      el('a', { href:'https://x.com/intent/post?text=' + e(t) + '&url=' + e(url), target:'_blank', rel:'noopener', text:'X' }),
      el('a', { href:'mailto:?subject=' + e(t) + '&body=' + e(url), text:'Email' }) ]);
    var cp = el('button', { type:'button', text:'Copy link' });
    cp.addEventListener('click', function(){ function ok(){ cp.textContent = 'Copied'; setTimeout(function(){ cp.textContent = 'Copy link'; }, 1500); }
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(ok, function(){}); else { window.prompt('Copy this link:', url); } });
    row.appendChild(cp);
    if (navigator.share){ var ns = el('button', { type:'button', text:'More…' }); ns.addEventListener('click', function(){ navigator.share({ title: t, url: url }).catch(function(){}); }); row.appendChild(ns); }
    return row;
  }
  window.WFExtras = { listenBar: listenBar, stopAll: stopAll, storyText: storyText, factsBox: factsBox, textBox: textBox, words: words, tlBox: tlBox, shareRow: shareRow };
})();
