<?php
require __DIR__ . '/inc/lib.php';
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['error' => 'method']); exit; }
$in = json_decode(file_get_contents('php://input'), true) ?: [];
$email = strtolower(trim((string)($in['email'] ?? '')));
if (!empty($in['website'])) { echo json_encode(['status' => 'ok']); exit; }                // hidden field: bots fill it, people don't
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 200) { http_response_code(400); echo json_encode(['error' => 'invalid_email']); exit; }
$db = wf_db(); $ip = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . 'wf');
$db->exec('DELETE FROM hits WHERE ts < ' . (time() - 3600));
$st = $db->prepare('SELECT COUNT(*) FROM hits WHERE ip = ?'); $st->execute([$ip]);
if ((int)$st->fetchColumn() >= 8) { http_response_code(429); echo json_encode(['error' => 'rate_limited']); exit; }
$db->prepare('INSERT INTO hits (ip, ts) VALUES (?, ?)')->execute([$ip, time()]);
$st = $db->prepare('SELECT * FROM subs WHERE email = ?'); $st->execute([$email]); $sub = $st->fetch(PDO::FETCH_ASSOC);
if ($sub && $sub['status'] === 'active') { echo json_encode(['status' => 'already']); exit; }
if ($sub) { $db->prepare('UPDATE subs SET status = "active", last_edition = 0 WHERE id = ?')->execute([$sub['id']]); }
else { $db->prepare('INSERT INTO subs (email, token, source, created) VALUES (?, ?, ?, ?)')->execute([$email, bin2hex(random_bytes(16)), substr((string)($in['source'] ?? 'site'), 0, 40), time()]); }
$st->execute([$email]); $sub = $st->fetch(PDO::FETCH_ASSOC);
$status = 'queued';
$ed = wf_latest();
if ($ed && wf_quota_left() > 0) {
    try { wf_send_edition($sub, $ed, "Welcome to Weekfold! Here is the latest edition, and a new one lands every Sunday."); $status = 'ok'; }
    catch (Throwable $e) { error_log('weekfold welcome: ' . $e->getMessage()); }
}
echo json_encode(['status' => $status]);
