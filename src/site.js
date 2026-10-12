/* Weekfold site services: email subscribe + optional Google sign-in.
   Settings come from config.json (injected by build.py as WF_CONFIG). Anything not configured is
   hidden or says so plainly, so the live site never pretends to do something it doesn't. */
var WFSite = (function () {
  var C = (typeof WF_CONFIG === 'object' && WF_CONFIG) || {};
  var N = C.newsletter || {};
  var CONTACT = C.contact_email || '';

  function endpoint() {
    if (N.provider === 'buttondown' && N.username) return { action: 'https://buttondown.com/api/emails/embed-subscribe/' + encodeURIComponent(N.username), field: 'email', extra: { embed: '1' } };
    if (N.provider === 'kit' && N.form_id) return { action: 'https://app.kit.com/forms/' + encodeURIComponent(N.form_id) + '/subscriptions', field: 'email_address', extra: {} };
    if (N.action) return { action: N.action, field: N.field || 'email', extra: {} };
    return null;
  }

  function postInNewTab(ep, email) {
    var f = document.createElement('form'); f.method = 'post'; f.action = ep.action; f.target = '_blank'; f.style.display = 'none';
    var add = function (k, v) { var i = document.createElement('input'); i.type = 'hidden'; i.name = k; i.value = v; f.appendChild(i); };
    add(ep.field, email); Object.keys(ep.extra).forEach(function (k) { add(k, ep.extra[k]); });
    document.body.appendChild(f); f.submit(); f.remove();
  }

  function subscribe(email, msg, after) {
    var ep = endpoint();
    if (!ep) {
      msg.className = 'msg';
      msg.textContent = '';
      msg.appendChild(document.createTextNode('Email sign-ups open very soon. '));
      if (CONTACT) { var a = document.createElement('a'); a.href = 'mailto:' + CONTACT + '?subject=' + encodeURIComponent('Add me to Weekfold') + '&body=' + encodeURIComponent('Please add ' + email + ' to the Sunday email.'); a.textContent = 'Email us to be added'; a.style.textDecoration = 'underline'; msg.appendChild(a); msg.appendChild(document.createTextNode('.')); }
      return;
    }
    msg.className = 'msg'; msg.textContent = 'Subscribing…';
    var body = new URLSearchParams(); body.append(ep.field, email); Object.keys(ep.extra).forEach(function (k) { body.append(k, ep.extra[k]); });
    fetch(ep.action, { method: 'POST', mode: 'no-cors', body: body }).then(function () {
      msg.className = 'msg'; msg.textContent = 'Almost done: check your inbox and tap the confirmation link. ' + (after || '');
    }).catch(function () {
      postInNewTab(ep, email);
      msg.className = 'msg'; msg.textContent = 'Finish subscribing in the tab that just opened.';
    });
  }

  function wireForm(formId, inputId, msgId, after) {
    var f = document.getElementById(formId), i = document.getElementById(inputId), m = document.getElementById(msgId);
    if (!f || !i || !m) return;
    var u = user(); if (u && u.email && !i.value) i.value = u.email;
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!i.value || !i.checkValidity()) { m.className = 'msg err'; m.textContent = 'Enter an email address like name@example.com.'; i.focus(); return; }
      subscribe(i.value.trim(), m, after);
    });
  }

  /* ---------- Google sign-in (Google Identity Services, no server needed) ---------- */
  function user() { try { return JSON.parse(localStorage.getItem('wf-user') || 'null'); } catch (e) { return null; } }
  function setUser(u) { try { if (u) localStorage.setItem('wf-user', JSON.stringify(u)); else localStorage.removeItem('wf-user'); } catch (e) {} }
  function decode(jwt) {
    try { var p = jwt.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'); while (p.length % 4) p += '=';
      var j = JSON.parse(decodeURIComponent(atob(p).split('').map(function (c) { return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2); }).join('')));
      return { name: j.name || '', given: j.given_name || (j.name || '').split(' ')[0], email: j.email || '', picture: j.picture || '' };
    } catch (e) { return null; }
  }

  function paintHeader() {
    var u = user();
    document.querySelectorAll('[data-open="signin"]').forEach(function (b) {
      if (!b.dataset.label) b.dataset.label = b.textContent.trim();
      b.textContent = u ? ('Hi, ' + (u.given || 'reader')) : b.dataset.label;
    });
  }

  function paintDialog(after) {
    var d = document.getElementById('dlg-signin'); if (!d) return;
    var box = d.querySelector('.dlg'); var u = user();
    var gb = document.getElementById('google-btn'), note = document.getElementById('google-note');
    var acct = d.querySelector('.acct'); if (acct) acct.remove();
    if (u) {
      if (gb) gb.hidden = true; if (note) note.hidden = true;
      acct = document.createElement('div'); acct.className = 'acct';
      acct.innerHTML = '<p class="lede" style="margin:0 0 12px"></p><div style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn btn-red" type="button" data-sub>Get the Sunday email</button><button class="btn" type="button" data-out>Sign out</button></div><p class="msg" role="status" style="margin-top:10px"></p>';
      acct.querySelector('.lede').textContent = 'Signed in as ' + (u.name || u.email) + (u.email ? ' (' + u.email + ')' : '') + '.';
      acct.querySelector('[data-out]').addEventListener('click', function () { setUser(null); if (window.google && google.accounts) google.accounts.id.disableAutoSelect(); paintHeader(); paintDialog(after); });
      acct.querySelector('[data-sub]').addEventListener('click', function () { subscribe(u.email, acct.querySelector('.msg'), after); });
      box.insertBefore(acct, box.querySelector('.fine'));
    } else if (gb) { gb.hidden = false; }
  }

  function initGoogle(after) {
    var id = C.google_client_id;
    var opens = document.querySelectorAll('[data-open="signin"]');
    if (!id) { opens.forEach(function (b) { var li = b.closest('li'); (li || b).hidden = true; }); return; }
    var gb = document.getElementById('google-btn');
    var holder = document.createElement('div'); holder.id = 'google-btn'; holder.style.minHeight = '44px';
    if (gb) gb.replaceWith(holder);
    var s = document.createElement('script'); s.src = 'https://accounts.google.com/gsi/client'; s.async = true; s.defer = true;
    s.onload = function () {
      google.accounts.id.initialize({ client_id: id, callback: function (r) { var u = decode(r.credential); if (u) { setUser(u); paintHeader(); paintDialog(after); } } });
      google.accounts.id.renderButton(holder, { theme: 'outline', size: 'large', shape: 'pill', text: 'continue_with', width: 300 });
    };
    s.onerror = function () { var n = document.getElementById('google-note'); if (n) { n.textContent = 'Google sign-in could not load. Check your connection and try again.'; n.hidden = false; } };
    document.head.appendChild(s);
    paintHeader(); paintDialog(after);
  }

  function init(opts) {
    opts = opts || {};
    var after = opts.next ? 'The next edition arrives ' + opts.next + '.' : '';
    document.querySelectorAll('[data-open]').forEach(function (b) { b.addEventListener('click', function () { var d = document.getElementById('dlg-' + b.getAttribute('data-open')); if (d && d.showModal) d.showModal(); }); });
    document.querySelectorAll('dialog').forEach(function (d) { d.addEventListener('click', function (e) { if (e.target === d || e.target.closest('[data-close]')) d.close(); }); });
    wireForm('inline-sub', 'inline-email', 'inline-msg', after);
    wireForm('dlg-sub-form', 'dlg-email', 'dlg-msg', after);
    initGoogle(after);
  }
  return { init: init, config: C };
})();
