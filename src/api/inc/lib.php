<?php
// Weekfold mailer: SQLite subscriber list + plain SMTP sending through the Hostinger mailbox. No external libraries.
function wf_cfg() {
    static $c = null;
    if ($c === null) {
        $f = __DIR__ . '/config.php';
        if (!is_file($f)) { http_response_code(500); header('Content-Type: application/json'); echo json_encode(['error' => 'not_configured']); exit; }
        $c = require $f;
    }
    return $c;
}

function wf_db() {
    static $db = null;
    if ($db) return $db;
    $dir = dirname(__DIR__, 3) . '/weekfold-data';           // one folder ABOVE public_html, not reachable from the web
    if (!is_dir($dir) && !@mkdir($dir, 0750, true) || !is_writable($dir)) {
        $dir = __DIR__ . '/data'; if (!is_dir($dir)) @mkdir($dir, 0750, true);   // fallback (inc/ is blocked by .htaccess)
    }
    $db = new PDO('sqlite:' . $dir . '/subscribers.sqlite');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->exec('CREATE TABLE IF NOT EXISTS subs (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, token TEXT NOT NULL, status TEXT NOT NULL DEFAULT "active", source TEXT, created INTEGER, last_edition INTEGER NOT NULL DEFAULT 0)');
    $db->exec('CREATE TABLE IF NOT EXISTS sendlog (ts INTEGER NOT NULL)');
    $db->exec('CREATE TABLE IF NOT EXISTS hits (ip TEXT, ts INTEGER)');
    return $db;
}

function wf_quota_left() {
    $db = wf_db(); $cap = (int)(wf_cfg()['daily_cap'] ?? 95);
    $db->exec('DELETE FROM sendlog WHERE ts < ' . (time() - 86400));
    $n = (int)$db->query('SELECT COUNT(*) FROM sendlog')->fetchColumn();
    return max(0, $cap - $n);
}

function wf_latest() {
    $root = dirname(__DIR__, 2);
    $j = json_decode(@file_get_contents($root . '/newsletter/latest.json'), true);
    $h = @file_get_contents($root . '/newsletter/latest-email.html');
    return ($j && $h) ? ['number' => (int)$j['number'], 'subject' => $j['subject'], 'html' => $h] : null;
}

function wf_smtp_send($to, $subject, $html, $text, $unsubUrl) {
    $c = wf_cfg();
    $fp = @stream_socket_client('ssl://' . $c['smtp_host'] . ':' . $c['smtp_port'], $en, $es, 25);
    if (!$fp) throw new Exception("SMTP connect failed: $es");
    stream_set_timeout($fp, 25);
    $rd = function () use ($fp) { $o = ''; while (($l = fgets($fp, 515)) !== false) { $o .= $l; if (strlen($l) < 4 || $l[3] === ' ') break; } return $o; };
    $cmd = function ($s, $ok) use ($fp, $rd) { if ($s !== null) fwrite($fp, $s . "\r\n"); $r = $rd(); if (strpos($ok, substr($r, 0, 3)) === false) throw new Exception('SMTP: ' . trim($r)); return $r; };
    try {
        $cmd(null, '220'); $cmd('EHLO weekfold.in', '250');
        $cmd('AUTH LOGIN', '334'); $cmd(base64_encode($c['smtp_user']), '334'); $cmd(base64_encode($c['smtp_pass']), '235');
        $cmd('MAIL FROM:<' . $c['from_email'] . '>', '250'); $cmd('RCPT TO:<' . $to . '>', '250 251'); $cmd('DATA', '354');
        $b = 'wf' . bin2hex(random_bytes(8));
        $enc = function ($s) { return '=?UTF-8?B?' . base64_encode($s) . '?='; };
        $hdr = "From: " . $enc($c['from_name']) . " <{$c['from_email']}>\r\nTo: <$to>\r\nSubject: " . $enc($subject) . "\r\nDate: " . date('r') .
            "\r\nMessage-ID: <" . bin2hex(random_bytes(10)) . "@weekfold.in>\r\nMIME-Version: 1.0\r\nList-Unsubscribe: <$unsubUrl>\r\nList-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n" .
            "Content-Type: multipart/alternative; boundary=\"$b\"\r\n\r\n";
        $body = "--$b\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($text)) .
            "--$b\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($html)) . "--$b--\r\n";
        fwrite($fp, $hdr . $body . "\r\n.\r\n"); $cmd(null, '250');
        $cmd('QUIT', '221 250');
    } finally { fclose($fp); }
}

function wf_send_edition($sub, $ed, $intro) {
    $c = wf_cfg(); $u = rtrim($c['site_url'], '/') . '/api/unsubscribe.php?t=' . $sub['token'];
    $html = str_replace(['{{UNSUBSCRIBE_URL}}', '{{INTRO}}'], [$u, htmlspecialchars($intro)], $ed['html']);
    $text = trim(html_entity_decode(strip_tags(preg_replace('/<(br|\/p|\/div|\/tr|\/h\d)[^>]*>/i', "\n", $html)))) ;
    $text = preg_replace("/\n{3,}/", "\n\n", $text) . "\n\nUnsubscribe: $u\n";
    wf_smtp_send($sub['email'], $ed['subject'], $html, $text, $u);
    $db = wf_db();
    $db->prepare('UPDATE subs SET last_edition = ? WHERE id = ?')->execute([$ed['number'], $sub['id']]);
    $db->prepare('INSERT INTO sendlog (ts) VALUES (?)')->execute([time()]);
}
