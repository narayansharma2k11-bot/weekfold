-- Run this AFTER the three edge functions are deployed (see SETUP-EMAIL.md, step 5).
-- Every hour it asks the "weekly" function to check weekfold.in for a new edition.
-- The function only sends when the edition number on the live site is newer than the last one sent,
-- so it is harmless to run hourly: the new edition goes out within an hour of you uploading it.
--
-- Replace the two placeholders before running:
--   YOUR-PROJECT-REF  → the id in your project URL, e.g. abcdefghijklmno (from https://abcdefghijklmno.supabase.co)
--   YOUR-CRON-SECRET  → the same CRON_SECRET you saved under Edge Functions › Secrets

select cron.unschedule('weekfold-weekly') where exists (select 1 from cron.job where jobname = 'weekfold-weekly');

select cron.schedule(
  'weekfold-weekly',
  '7 * * * *',
  $$
  select net.http_post(
    url     := 'https://YOUR-PROJECT-REF.supabase.co/functions/v1/weekly',
    headers := jsonb_build_object('Content-Type', 'application/json', 'x-cron-secret', 'YOUR-CRON-SECRET'),
    body    := '{}'::jsonb,
    timeout_milliseconds := 120000
  );
  $$
);
