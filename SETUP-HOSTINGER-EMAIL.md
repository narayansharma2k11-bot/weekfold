# Hostinger email setup (subscribe + weekly send)

Subscribing sends the latest edition straight away from support@weekfold.in. A Hostinger cron job sends each new edition to everyone who hasn't had it, within the mailbox limit of 100 messages per 24 hours (the code uses 95 to leave room).

## One-time setup (about 5 minutes)
1. Upload and extract `weekfold-site.zip` into `public_html` (overwrite). This adds the `api/` folder.
2. File Manager > `public_html/api/inc/` > copy `config.sample.php` to `config.php`, edit it, replace `PUT-THE-MAILBOX-PASSWORD-HERE` with the support@weekfold.in password, set `cron_key` to any long random text, save.
3. hPanel > Advanced > Cron Jobs > add: every hour (minute 0, other fields `*`), command:
   `php /home/<your-hostinger-user>/domains/weekfold.in/public_html/api/send.php`
   (the real path is shown at the top of File Manager / on the Cron Jobs page.)
4. Test: subscribe on weekfold.in with your own address; the edition arrives within a minute.

## Notes
- The subscriber list is a file one level above `public_html` (`weekfold-data/subscribers.sqlite`). Back it up now and then (File Manager > download).
- `config.php` and the list are never in the zip, so weekly uploads never overwrite them.
- Beyond roughly 100 subscribers a new edition takes more than a day to reach everyone (the cap is per 24 hours). At that point move to Resend or Brevo.
- Every email has a one-click unsubscribe (`api/unsubscribe.php`).
