<?php
// Run by a Hostinger cron job (hourly). Sends the newest edition to everyone who hasn't had it yet, within the daily cap.
require __DIR__ . '/inc/lib.php';
if (PHP_SAPI !== 'cli' && (($_GET['key'] ?? '') !== (wf_cfg()['cron_key'] ?? '#'))) { http_response_code(403); exit('forbidden'); }
header('Content-Type: text/plain');
$ed = wf_latest(); if (!$ed) exit("No edition found.\n");
$left = wf_quota_left(); $db = wf_db();
$st = $db->prepare('SELECT * FROM subs WHERE status = "active" AND last_edition < ? ORDER BY id LIMIT ?'); $st->bindValue(1, $ed['number'], PDO::PARAM_INT); $st->bindValue(2, $left, PDO::PARAM_INT); $st->execute();
$sent = 0; $fail = 0;
foreach ($st->fetchAll(PDO::FETCH_ASSOC) as $s) {
    try { wf_send_edition($s, $ed, 'Here is this week\'s edition of Weekfold.'); $sent++; }
    catch (Throwable $e) { $fail++; error_log('weekfold send ' . $s['email'] . ': ' . $e->getMessage()); if (strpos($e->getMessage(), 'SMTP') === 0 && $fail >= 3) break; }
    sleep(2);
}
$rem = (int)$db->query('SELECT COUNT(*) FROM subs WHERE status = "active" AND last_edition < ' . (int)$ed['number'])->fetchColumn();
echo "Edition {$ed['number']}: sent $sent, failed $fail, still waiting $rem, quota left " . wf_quota_left() . "\n";
