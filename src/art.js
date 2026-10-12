/* Weekfold story art: riso-style duotone halftones generated per story (no photos needed). */
window.WFArt = (function () {
  var PAL = {
    world:    ['#E9EEF8', '#1A2747', '#D92D20'],
    politics: ['#EFEAF6', '#22183F', '#D92D20'],
    conflict: ['#F2ECE6', '#2A1F17', '#C2410C'],
    business: ['#E8F3EC', '#123528', '#1F8A5B'],
    tech:     ['#ECE9F8', '#1F1747', '#6A45DB'],
    science:  ['#E3F2F3', '#0E363C', '#0D8A93'],
    health:   ['#E6F4EE', '#0F3A2A', '#169B62'],
    sport:    ['#FFEFE0', '#3A1C05', '#E5700A'],
    climate:  ['#E3EFFA', '#0D2A45', '#2477C4'],
    culture:  ['#FBEBE8', '#3A1313', '#D92D20']
  };
  function palFor(cat) {
    var c = (cat || '').toLowerCase();
    if (/business|market|econom|money|trade/.test(c)) return PAL.business;
    if (/tech/.test(c)) return PAL.tech;
    if (/science|space/.test(c)) return PAL.science;
    if (/health/.test(c)) return PAL.health;
    if (/sport/.test(c)) return PAL.sport;
    if (/climate|weather|environment/.test(c)) return PAL.climate;
    if (/culture|art|books|film|music/.test(c)) return PAL.culture;
    if (/conflict|war|security/.test(c)) return PAL.conflict;
    if (/politic|election/.test(c)) return PAL.politics;
    return PAL.world;
  }
  function motifFor(cat, text) {
    var t = ((cat || '') + ' ' + (text || '')).toLowerCase();
    if (/hurricane|storm|cyclone|typhoon|tornado/.test(t)) return 'spiral';
    if (/nobel|prize|award|medal|trophy|champion/.test(t)) return 'medal';
    if (/oil|crude|diesel|fuel|opec|gas price/.test(t)) return 'drop';
    if (/elect|vote|ballot|poll|referendum/.test(t)) return 'ballot';
    if (/missile|attack|strike|war|houthi|drone|bomb|shoot|troops|ceasefire|military/.test(t)) return 'target';
    if (/neutrino|physic|atom|chemi|molecul|particle|quantum/.test(t)) return 'atom';
    if (/brain|neuro|optogen|health|medic|virus|vaccine|disease|cell/.test(t)) return 'cells';
    if (/\bai\b|artificial|tech|google|chip|phone|apple|software|cyber|gemini|openai/.test(t)) return 'chip';
    if (/market|stock|share|index|econom|trade|tariff|bank|rate|inflation|dollar|earnings|business/.test(t)) return 'chart';
    if (/sport|cup|match|cricket|football|soccer|olymp|games|tennis|race|league/.test(t)) return 'ball';
    if (/book|literat|poet|novel|film|music|art|museum|culture/.test(t)) return 'pages';
    if (/climate|weather|flood|heat|drought|ocean|wildfire|earthquake/.test(t)) return 'waves';
    return 'globe';
  }
  function rng(seed) {
    var s = 2166136261 >>> 0, str = String(seed || 'x');
    for (var i = 0; i < str.length; i++) { s ^= str.charCodeAt(i); s = Math.imul(s, 16777619) >>> 0; }
    return function () { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return (s % 100000) / 100000; };
  }
  function grad(ctx, x, y, r, a, b) {
    var g = ctx.createRadialGradient(x - r * 0.35, y - r * 0.35, r * 0.05, x, y, r);
    g.addColorStop(0, 'rgba(0,0,0,' + a + ')'); g.addColorStop(1, 'rgba(0,0,0,' + b + ')');
    return g;
  }
  var M = {
    globe: function (c, W, H, r) {
      var cx = W * (0.55 + r() * 0.15), cy = H * 0.55, R = H * 0.46;
      c.fillStyle = grad(c, cx, cy, R, 0.15, 0.85); c.beginPath(); c.arc(cx, cy, R, 0, 7); c.fill();
      c.strokeStyle = 'rgba(0,0,0,.9)'; c.lineWidth = W * 0.008;
      for (var i = 1; i < 6; i++) { c.beginPath(); c.ellipse(cx, cy, R * i / 6, R, 0, 0, 7); c.stroke(); }
      for (var j = -2; j <= 2; j++) { c.beginPath(); c.ellipse(cx, cy + j * R * 0.33, R * Math.cos(j * 0.36), R * 0.12, 0, 0, 7); c.stroke(); }
    },
    chart: function (c, W, H, r) {
      var n = 9, bw = W / (n * 1.6), up = r() > 0.4;
      for (var i = 0; i < n; i++) {
        var h = H * (0.15 + (up ? i / n : (n - i) / n) * 0.55 + r() * 0.15);
        var g = c.createLinearGradient(0, H - h, 0, H); g.addColorStop(0, 'rgba(0,0,0,.85)'); g.addColorStop(1, 'rgba(0,0,0,.2)');
        c.fillStyle = g; c.fillRect(W * 0.08 + i * bw * 1.6, H - h, bw, h);
      }
      c.strokeStyle = 'rgba(0,0,0,1)'; c.lineWidth = W * 0.018; c.lineJoin = 'round'; c.beginPath();
      for (var k = 0; k <= 10; k++) { var y = H * (up ? 0.75 - k * 0.055 : 0.2 + k * 0.055) + (r() - 0.5) * H * 0.12; k ? c.lineTo(W * 0.05 + k * W * 0.09, y) : c.moveTo(W * 0.05, y); }
      c.stroke();
    },
    spiral: function (c, W, H, r) {
      var cx = W * 0.55, cy = H * 0.5;
      for (var a = 0; a < 26; a += 0.05) {
        var rr = 4 + a * H * 0.019, x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr * 0.8;
        c.fillStyle = 'rgba(0,0,0,' + (0.9 - a / 34) + ')'; c.beginPath(); c.arc(x, y, W * 0.012 + a * 0.6, 0, 7); c.fill();
      }
      c.fillStyle = '#fff'; c.beginPath(); c.arc(cx, cy, H * 0.06, 0, 7); c.fill();
    },
    drop: function (c, W, H, r) {
      var cx = W * 0.5, cy = H * 0.58, R = H * 0.28;
      c.fillStyle = grad(c, cx, cy, R * 1.4, 0.2, 0.95);
      c.beginPath(); c.moveTo(cx, cy - R * 1.7); c.bezierCurveTo(cx + R * 0.4, cy - R, cx + R, cy - R * 0.4, cx + R, cy);
      c.arc(cx, cy, R, 0, Math.PI); c.bezierCurveTo(cx - R, cy - R * 0.4, cx - R * 0.4, cy - R, cx, cy - R * 1.7); c.fill();
      c.strokeStyle = 'rgba(0,0,0,.55)'; c.lineWidth = W * 0.008;
      for (var i = 1; i < 4; i++) { c.beginPath(); c.ellipse(cx, H * 0.93, R * (1 + i * 0.7), R * 0.12 * i, 0, 0, 7); c.stroke(); }
    },
    medal: function (c, W, H, r) {
      var cx = W * 0.5, cy = H * 0.6, R = H * 0.28;
      c.fillStyle = 'rgba(0,0,0,.55)';
      c.beginPath(); c.moveTo(cx - R * 0.9, -5); c.lineTo(cx - R * 0.15, cy - R * 0.6); c.lineTo(cx - R * 0.5, cy - R * 0.9); c.lineTo(cx - R * 1.5, -5); c.fill();
      c.beginPath(); c.moveTo(cx + R * 0.9, -5); c.lineTo(cx + R * 0.15, cy - R * 0.6); c.lineTo(cx + R * 0.5, cy - R * 0.9); c.lineTo(cx + R * 1.5, -5); c.fill();
      c.fillStyle = grad(c, cx, cy, R, 0.25, 0.95); c.beginPath(); c.arc(cx, cy, R, 0, 7); c.fill();
      c.strokeStyle = 'rgba(255,255,255,.9)'; c.lineWidth = W * 0.01; c.beginPath(); c.arc(cx, cy, R * 0.72, 0, 7); c.stroke();
      c.fillStyle = 'rgba(255,255,255,.9)'; c.beginPath();
      for (var i = 0; i < 10; i++) { var a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? R * 0.22 : R * 0.5; c.lineTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr); }
      c.fill();
    },
    ballot: function (c, W, H, r) {
      var bx = W * 0.28, by = H * 0.42, bw = W * 0.44, bh = H * 0.5;
      c.fillStyle = 'rgba(0,0,0,.35)'; c.save(); c.translate(W * 0.5, H * 0.3); c.rotate(-0.12);
      c.fillRect(-W * 0.12, -H * 0.25, W * 0.24, H * 0.36); c.fillStyle = 'rgba(0,0,0,.9)';
      c.fillRect(-W * 0.08, -H * 0.15, W * 0.16, H * 0.025); c.fillRect(-W * 0.08, -H * 0.08, W * 0.1, H * 0.025); c.restore();
      var g = c.createLinearGradient(bx, by, bx + bw, by + bh); g.addColorStop(0, 'rgba(0,0,0,.95)'); g.addColorStop(1, 'rgba(0,0,0,.45)');
      c.fillStyle = g; c.fillRect(bx, by, bw, bh); c.fillStyle = '#fff'; c.fillRect(bx + bw * 0.25, by + bh * 0.08, bw * 0.5, H * 0.03);
    },
    target: function (c, W, H, r) {
      var cx = W * (0.4 + r() * 0.25), cy = H * 0.5;
      for (var i = 6; i > 0; i--) { c.fillStyle = 'rgba(0,0,0,' + (i % 2 ? 0.85 : 0.2) + ')'; c.beginPath(); c.arc(cx, cy, i * H * 0.075, 0, 7); c.fill(); }
      c.strokeStyle = 'rgba(0,0,0,.9)'; c.lineWidth = W * 0.007;
      c.beginPath(); c.moveTo(0, cy); c.lineTo(W, cy); c.moveTo(cx, 0); c.lineTo(cx, H); c.stroke();
      c.lineWidth = W * 0.012; c.setLineDash([W * 0.02, W * 0.015]);
      for (var k = 0; k < 3; k++) { c.beginPath(); c.moveTo(W * (0.95 - k * 0.05), H * 0.05); c.quadraticCurveTo(W * (0.8 - k * 0.1), H * (0.05 + k * 0.1), cx, cy); c.stroke(); }
      c.setLineDash([]);
    },
    atom: function (c, W, H, r) {
      var cx = W * 0.52, cy = H * 0.5;
      c.strokeStyle = 'rgba(0,0,0,.85)'; c.lineWidth = W * 0.013;
      for (var i = 0; i < 3; i++) { c.beginPath(); c.ellipse(cx, cy, W * 0.3, H * 0.12, i * Math.PI / 3, 0, 7); c.stroke(); }
      c.fillStyle = grad(c, cx, cy, H * 0.1, 0.3, 1); c.beginPath(); c.arc(cx, cy, H * 0.1, 0, 7); c.fill();
      for (var k = 0; k < 3; k++) { var a = r() * 6.28; c.fillStyle = 'rgba(0,0,0,.95)'; c.beginPath(); c.arc(cx + Math.cos(k * 2.1 + a) * W * 0.28, cy + Math.sin(k * 2.1 + a) * H * 0.2, H * 0.035, 0, 7); c.fill(); }
    },
    cells: function (c, W, H, r) {
      for (var i = 0; i < 9; i++) {
        var x = W * (0.15 + r() * 0.75), y = H * (0.15 + r() * 0.7), R = H * (0.08 + r() * 0.2);
        c.fillStyle = grad(c, x, y, R, 0.05, 0.8); c.beginPath(); c.arc(x, y, R, 0, 7); c.fill();
        c.fillStyle = 'rgba(0,0,0,.9)'; c.beginPath(); c.arc(x + R * 0.2, y + R * 0.1, R * 0.25, 0, 7); c.fill();
      }
      c.strokeStyle = 'rgba(0,0,0,.7)'; c.lineWidth = W * 0.005;
      for (var k = 0; k < 6; k++) { c.beginPath(); c.moveTo(W * r(), H * r()); c.bezierCurveTo(W * r(), H * r(), W * r(), H * r(), W * r(), H * r()); c.stroke(); }
    },
    chip: function (c, W, H, r) {
      var s = H * 0.5, x = W * 0.5 - s / 2, y = H * 0.5 - s / 2;
      c.strokeStyle = 'rgba(0,0,0,.6)'; c.lineWidth = W * 0.006;
      for (var i = 0; i < 14; i++) { var yy = H * (0.05 + i * 0.065); c.beginPath(); c.moveTo(0, yy); c.lineTo(W * 0.2, yy); c.lineTo(W * 0.25, yy + H * 0.05); c.stroke(); c.beginPath(); c.moveTo(W, yy); c.lineTo(W * 0.8, yy); c.lineTo(W * 0.75, yy - H * 0.05); c.stroke(); }
      c.fillStyle = 'rgba(0,0,0,.9)';
      for (var p = 0; p < 7; p++) { var o = s * (0.1 + p * 0.13); c.fillRect(x + o, y - s * 0.12, s * 0.05, s * 0.12); c.fillRect(x + o, y + s, s * 0.05, s * 0.12); c.fillRect(x - s * 0.12, y + o, s * 0.12, s * 0.05); c.fillRect(x + s, y + o, s * 0.12, s * 0.05); }
      var g = c.createLinearGradient(x, y, x + s, y + s); g.addColorStop(0, 'rgba(0,0,0,.95)'); g.addColorStop(1, 'rgba(0,0,0,.4)');
      c.fillStyle = g; c.fillRect(x, y, s, s); c.strokeStyle = 'rgba(255,255,255,.9)'; c.lineWidth = W * 0.008; c.strokeRect(x + s * 0.2, y + s * 0.2, s * 0.6, s * 0.6);
    },
    ball: function (c, W, H, r) {
      c.strokeStyle = 'rgba(0,0,0,.45)'; c.lineWidth = W * 0.012;
      for (var i = 0; i < 6; i++) { c.beginPath(); c.ellipse(W * 0.5, H * 1.25, W * (0.35 + i * 0.09), H * (0.55 + i * 0.12), 0, Math.PI, 0); c.stroke(); }
      var cx = W * 0.62, cy = H * 0.42, R = H * 0.24;
      c.fillStyle = grad(c, cx, cy, R, 0.1, 0.9); c.beginPath(); c.arc(cx, cy, R, 0, 7); c.fill();
      c.strokeStyle = 'rgba(255,255,255,.95)'; c.lineWidth = W * 0.008;
      c.beginPath(); c.arc(cx - R * 1.1, cy, R * 0.9, -0.9, 0.9); c.stroke(); c.beginPath(); c.arc(cx + R * 1.1, cy, R * 0.9, Math.PI - 0.9, Math.PI + 0.9); c.stroke();
    },
    pages: function (c, W, H, r) {
      var cx = W * 0.5, by = H * 0.85;
      for (var i = 0; i < 9; i++) {
        var t = i / 8, a = 0.25 + t * 0.5;
        c.fillStyle = 'rgba(0,0,0,' + (0.2 + Math.abs(t - 0.5) * 1.3) + ')';
        c.beginPath(); c.moveTo(cx, by); c.quadraticCurveTo(cx - (0.5 - t) * W * 0.6, H * 0.3, cx - (0.5 - t) * W * 0.85, H * (0.2 + Math.abs(t - 0.5) * 0.4));
        c.lineTo(cx - (0.5 - t) * W * 0.85 + W * 0.02, H * (0.24 + Math.abs(t - 0.5) * 0.4)); c.quadraticCurveTo(cx - (0.5 - t) * W * 0.5, H * 0.4, cx, by); c.fill();
      }
    },
    waves: function (c, W, H, r) {
      for (var i = 0; i < 9; i++) {
        c.strokeStyle = 'rgba(0,0,0,' + (0.25 + i * 0.08) + ')'; c.lineWidth = H * 0.035; c.beginPath();
        for (var x = 0; x <= W; x += W / 60) { var y = H * (0.15 + i * 0.09) + Math.sin(x / W * 9 + i * 0.8) * H * 0.04; x ? c.lineTo(x, y) : c.moveTo(x, y); }
        c.stroke();
      }
      c.fillStyle = grad(c, W * 0.78, H * 0.22, H * 0.15, 0.4, 0.95); c.beginPath(); c.arc(W * 0.78, H * 0.22, H * 0.15, 0, 7); c.fill();
    }
  };
  function draw(canvas, opts) {
    var W = canvas.width, H = canvas.height, ctx = canvas.getContext('2d');
    if (!ctx) return;
    var pal = palFor(opts.category), motif = opts.motif || motifFor(opts.category, opts.text), r = rng(opts.seed || opts.text);
    var off = document.createElement('canvas'); off.width = W; off.height = H;
    var o = off.getContext('2d'); o.fillStyle = '#fff'; o.fillRect(0, 0, W, H);
    (M[motif] || M.globe)(o, W, H, r);
    var data = o.getImageData(0, 0, W, H).data;
    function tone(x, y) { x = Math.max(0, Math.min(W - 1, x | 0)); y = Math.max(0, Math.min(H - 1, y | 0)); var i = (y * W + x) * 4; return 1 - (data[i] * 0.3 + data[i + 1] * 0.59 + data[i + 2] * 0.11) / 255; }
    ctx.fillStyle = pal[0]; ctx.fillRect(0, 0, W, H);
    var cell = Math.max(5, W / 80);
    /* accent layer: 45° screen, slightly mis-registered like a riso print */
    ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = pal[2];
    var dx = W * 0.018, dy = H * 0.012, c2 = cell * 1.25;
    for (var y = -c2; y < H + c2; y += c2 * 0.7071) for (var x = -c2; x < W + c2; x += c2) {
      var xx = x + ((Math.round(y / (c2 * 0.7071)) % 2) ? c2 / 2 : 0), t = tone(xx - dx, y - dy);
      t = Math.min(1, t * 1.15 + 0.06); if (t < 0.04) continue;
      ctx.beginPath(); ctx.arc(xx, y, c2 * 0.62 * Math.sqrt(t), 0, 7); ctx.fill();
    }
    /* ink layer: square grid, only the deeper tones */
    ctx.fillStyle = pal[1];
    for (var y2 = cell / 2; y2 < H; y2 += cell) for (var x2 = cell / 2; x2 < W; x2 += cell) {
      var t2 = tone(x2, y2); t2 = Math.pow(t2, 1.7); if (t2 < 0.05) continue;
      ctx.beginPath(); ctx.arc(x2, y2, cell * 0.55 * Math.sqrt(t2), 0, 7); ctx.fill();
    }
    ctx.globalCompositeOperation = 'source-over';
    /* paper grain */
    var rg = rng('grain' + W), id = ctx.getImageData(0, 0, W, H), d = id.data;
    for (var i = 0; i < d.length; i += 4) { var n = (rg() - 0.5) * 18; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    ctx.putImageData(id, 0, 0);
  }
  function paintAll(root) {
    var list = (root || document).querySelectorAll('canvas[data-art]:not([data-done])');
    for (var i = 0; i < list.length; i++) {
      var cv = list[i];
      try { draw(cv, { category: cv.getAttribute('data-cat'), text: cv.getAttribute('data-art'), seed: cv.getAttribute('data-seed') }); cv.setAttribute('data-done', '1'); } catch (e) {}
    }
  }
  return { draw: draw, paintAll: paintAll, motifFor: motifFor };
})();

/* Story photos: each story names a Wikipedia article; the page loads that article's free-licensed lead photo
   (and its author/licence) from the Wikipedia API. Until a photo arrives, or if it can't load, a generated
   illustration is shown instead. */
window.WFPhoto = (function () {
  var API = 'https://en.wikipedia.org/w/api.php?format=json&formatversion=2&origin=*&action=query';
  var cache = {}, waiting = {}, queue = [], timer = null, failed = false;
  try { cache = JSON.parse(localStorage.getItem('wf-photos-v2') || '{}') || {}; } catch (e) { cache = {}; }
  /* Only public-domain, CC0 and plain CC BY (attribution) files are shown; anything share-alike, non-commercial, no-derivatives or unlabelled falls back to an illustration. */
  function okLicense(l) {
    l = (l || '').trim().toLowerCase();
    if (!l) return false;
    if (/^(public domain|pd[ -]|cc0|cc zero|no restrictions)/.test(l)) return true;
    return /^cc[ -]by[ -][0-9.]+(\s(us|au|nz|ca|uk|in|ie|de|nl|fr|es|it))?$/.test(l);
  }
  function save() { try { localStorage.setItem('wf-photos-v2', JSON.stringify(cache)); } catch (e) {} }
  function strip(h) { var d = document.createElement('div'); d.innerHTML = h || ''; return (d.textContent || '').replace(/\s+/g, ' ').trim(); }
  function getJSON(url) { return fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function flush() {
    timer = null;
    var titles = queue.splice(0, 50); if (!titles.length) return;
    getJSON(API + '&redirects=1&prop=pageimages&piprop=thumbnail|name&pithumbsize=1280&pilicense=free&titles=' + encodeURIComponent(titles.join('|'))).then(function (j) {
      var q = j.query || {}, map = {};
      (q.normalized || []).forEach(function (n) { map[n.to] = n.from; });
      (q.redirects || []).forEach(function (n) { map[n.to] = map[n.from] || n.from; });
      var found = {}, files = [];
      (q.pages || []).forEach(function (pg) {
        var orig = map[pg.title] || pg.title; if (map[orig]) orig = map[orig];
        if (pg.thumbnail && pg.pageimage) { found[orig] = { src: pg.thumbnail.source, file: pg.pageimage }; files.push('File:' + pg.pageimage); }
      });
      var done = function () {
        titles.forEach(function (t) { var key = t.replace(/ /g, '_'); cache[key] = found[t] || found[t.replace(/_/g, ' ')] || { none: true }; deliver(key); });
        save();
      };
      if (!files.length) return done();
      getJSON(API + '&prop=imageinfo&iiprop=extmetadata&iiextmetadatafilter=Artist|LicenseShortName&titles=' + encodeURIComponent(files.join('|'))).then(function (k) {
        var meta = {};
        ((k.query || {}).pages || []).forEach(function (pg) { var ii = (pg.imageinfo || [])[0]; if (!ii) return; var em = ii.extmetadata || {}; meta[pg.title.replace(/^File:/, '').replace(/ /g, '_')] = { credit: strip((em.Artist || {}).value), license: (em.LicenseShortName || {}).value || '' }; });
        Object.keys(found).forEach(function (t) { var f = found[t], m = meta[f.file.replace(/ /g, '_')] || {}; f.credit = m.credit || ''; f.license = m.license || ''; if (!okLicense(f.license)) { delete found[t]; } });
        done();
      }, done);
    }).catch(function () { failed = true; titles.forEach(function (t) { deliver(t.replace(/ /g, '_')); }); });
    if (queue.length) timer = setTimeout(flush, 10);
  }
  function want(title, cb) {
    var key = title.replace(/ /g, '_');
    if (cache[key]) return cb(cache[key]);
    if (failed) return cb(null);
    (waiting[key] = waiting[key] || []).push(cb);
    if (waiting[key].length === 1) { queue.push(key); if (!timer) timer = setTimeout(flush, 30); }
  }
  function deliver(key) { var cbs = waiting[key] || []; delete waiting[key]; cbs.forEach(function (cb) { cb(cache[key] && !cache[key].none ? cache[key] : null); }); }
  function fallback(story, w, h, seed) {
    var c = document.createElement('canvas');
    c.width = Math.min(w, 1200); c.height = Math.round(c.width * h / w);
    c.setAttribute('data-art', story.headline || ''); c.setAttribute('data-cat', story.category || ''); c.setAttribute('data-seed', seed || story.headline || '');
    c.setAttribute('aria-hidden', 'true');
    return c;
  }
  function filePage(file) { return 'https://commons.wikimedia.org/wiki/File:' + encodeURIComponent(String(file).replace(/ /g, '_')); }
  function make(story, w, h, seed, opts) {
    opts = opts || {};
    var box = document.createElement('div');
    box.className = 'ph is-art' + (opts.cls ? ' ' + opts.cls : '');
    box.style.aspectRatio = w + ' / ' + h;
    box.appendChild(fallback(story, w, h, seed));
    var im = story && story.image;
    if (im && im.wiki && window.fetch) {
      want(im.wiki, function (p) {
        if (!p) return;
        var img = new Image();
        img.alt = im.caption || story.headline || ''; img.decoding = 'async'; img.width = w; img.height = h;
        img.style.opacity = '0'; img.style.transition = 'opacity .4s';
        img.onload = function () {
          img.style.opacity = '1'; box.classList.remove('is-art');
          if (!opts.noCredit) { var cr = document.createElement('span'); cr.className = 'credit'; cr.textContent = 'Photo: ' + (p.credit || 'Wikimedia Commons') + (p.license ? ' · ' + p.license : ''); box.appendChild(cr); }
          box.dispatchEvent(new CustomEvent('wf-photo', { detail: { credit: p.credit, license: p.license, page: filePage(p.file) } }));
        };
        img.src = p.src; box.appendChild(img);
      });
    }
    return box;
  }
  return { make: make };
})();
