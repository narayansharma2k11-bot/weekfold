<?php
// 1) In Hostinger File Manager, open public_html/api/inc/, COPY this file to config.php, then edit config.php.
// 2) Never share config.php: it holds your mailbox password. It is never part of the site zip, so uploads won't overwrite it.
return [
    'smtp_host'  => 'smtp.hostinger.com',
    'smtp_port'  => 465,                       // SSL
    'smtp_user'  => 'support@weekfold.in',
    'smtp_pass'  => 'PUT-THE-MAILBOX-PASSWORD-HERE',
    'from_email' => 'support@weekfold.in',
    'from_name'  => 'Weekfold',
    'site_url'   => 'https://weekfold.in',
    'daily_cap'  => 95,                        // Hostinger Starter allows 100 messages per 24 hours; keep a little spare
    'cron_key'   => 'CHANGE-ME-to-any-long-random-text',   // only needed if you ever call send.php from a web address
];
