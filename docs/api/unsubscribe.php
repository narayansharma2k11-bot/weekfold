<?php
require __DIR__ . '/inc/lib.php';
$t = preg_replace('/[^a-f0-9]/', '', (string)($_GET['t'] ?? $_POST['t'] ?? ''));
$done = false;
if ($t && $_SERVER['REQUEST_METHOD'] === 'POST') { wf_db()->prepare('UPDATE subs SET status = "unsubscribed" WHERE token = ?')->execute([$t]); $done = true; }
header('Content-Type: text/html; charset=utf-8');
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Unsubscribe | Weekfold</title>
<style>body{font:18px/1.6 Georgia,serif;max-width:480px;margin:12vh auto;padding:0 20px;color:#111}h1{font-size:30px}button{font:700 14px sans-serif;letter-spacing:.06em;text-transform:uppercase;background:#8c1d18;color:#fff;border:2px solid #000;padding:14px 22px;cursor:pointer}a{color:#10224a}</style></head><body>
<?php if ($done): ?><h1>You're unsubscribed.</h1><p>No more Weekfold emails. Changed your mind? You can sign up again any time at <a href="/">weekfold.in</a>.</p>
<?php elseif ($t): ?><h1>Unsubscribe from Weekfold?</h1><p>You'll stop getting the weekly edition.</p><form method="post"><input type="hidden" name="t" value="<?= htmlspecialchars($t) ?>"><button type="submit">Yes, unsubscribe me</button></form>
<?php else: ?><h1>Link not recognised.</h1><p>Email <a href="mailto:weekfoldsupport@gmail.com">weekfoldsupport@gmail.com</a> and we'll remove you by hand.</p><?php endif; ?>
</body></html>
