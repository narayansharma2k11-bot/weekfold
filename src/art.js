/* Story pictures.
   Every story names a Wikipedia article (image.wiki). At build time GitHub downloads that article's free-licensed lead photo
   into the site itself (see scripts/fetch_photos.py), so pictures are always loaded from Weekfold's own files, never from
   another website. WF_PHOTOS maps the article name to the local file, its photographer and its licence.
   A story without a photo shows a plain labelled tile instead. */
window.WFArt = { paintAll: function () {} };

window.WFPhoto = (function () {
  var P = (typeof WF_PHOTOS === 'object' && WF_PHOTOS) || {};
  var TONE = { world: '#1e3a6a', politics: '#4b0f0d', conflict: '#2b2b2b', business: '#786b27', sport: '#1f5c3f', climate: '#0b6f78', tech: '#3b2f7a', science: '#3b2f7a', culture: '#8c1d18', health: '#145c3a' };
  function tile(story) {
    var t = document.createElement('div');
    t.className = 'fb'; t.setAttribute('aria-hidden', 'true');
    t.style.setProperty('--fb', TONE[String(story.category || '').toLowerCase()] || '#10224a');
    var s = document.createElement('span'); s.textContent = story.category || 'Weekfold'; t.appendChild(s);
    return t;
  }
  function make(story, w, h, seed, opts) {
    opts = opts || {};
    var box = document.createElement('div');
    box.className = 'ph is-art' + (opts.cls ? ' ' + opts.cls : '');
    box.style.aspectRatio = w + ' / ' + h;
    var fb = tile(story);
    box.appendChild(fb);
    var im = story && story.image, p = im && im.wiki ? P[String(im.wiki).trim().replace(/ /g, '_')] : null;
    if (p && p.src) {
      var img = new Image();
      img.alt = (im && im.caption) || story.headline || ''; img.decoding = 'async'; img.width = w; img.height = h;
      if (!opts.eager) img.loading = 'lazy';
      img.onload = function () {
        box.classList.remove('is-art');
        if (fb.parentNode) fb.parentNode.removeChild(fb);
        if (!opts.noCredit) { var cr = document.createElement('span'); cr.className = 'credit'; cr.textContent = 'Photo: ' + (p.credit || 'Wikimedia Commons') + (p.license ? ' · ' + p.license : ''); box.appendChild(cr); }
        box.dispatchEvent(new CustomEvent('wf-photo', { detail: { credit: p.credit, license: p.license, page: p.page } }));
      };
      img.onerror = function () { if (img.parentNode) img.parentNode.removeChild(img); };
      img.src = p.src; box.appendChild(img);
    }
    return box;
  }
  return { make: make };
})();
