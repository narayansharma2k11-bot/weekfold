# Weekfold email: Supabase + Resend (no confirmation step)

What happens once this is set up:

- Someone types their email on weekfold.in → it is saved in your Supabase `subscribers` table → they get **this week's edition by email straight away**. No confirmation link.
- Every hour, Supabase checks weekfold.in. When you upload a new edition, everyone on the list gets it **once**, within the hour.
- Every email has an **Unsubscribe** link, plus the one-click Unsubscribe button Gmail and Apple Mail show.
- Typing the same email twice doesn't send twice. Bots are filtered by a hidden field and a limit of 5 sign-ups per connection per hour.

Takes about 20 minutes. You need: a free Supabase account, a free Resend account, and Hostinger (for 3–4 DNS records).

---

## 1. Create the Supabase project

1. Go to supabase.com → **New project**. Name: `weekfold`. Region: **South Asia (Mumbai)**. Save the database password somewhere safe.
2. When it's ready, open **SQL Editor → New query**, paste everything in `supabase/schema.sql`, press **Run**. You should see "Success".
3. Open **Table Editor**: you'll see `subscribers` and `sent_editions` (both empty).

## 2. Set up Resend (the email sender)

1. Sign up at resend.com.
2. **Domains → Add domain →** `weekfold.in`. Region: closest offered.
3. Resend shows 3–4 DNS records (MX + TXT on `send.weekfold.in`, a DKIM TXT on `resend._domainkey`, and optionally DMARC).
4. In **Hostinger → Domains → weekfold.in → DNS / Nameservers → DNS records**, add each record exactly as Resend shows it (Type, Name, Value). These don't touch your website or any existing email.
5. Back in Resend press **Verify**. DNS can take 5 minutes to a few hours. Wait for **Verified**.
6. **API Keys → Create API key** (permission: Sending access). Copy it (starts with `re_`).

Free plan: 3,000 emails a month, **100 a day**. If the list grows past 100, the Sunday send continues automatically the next day.

## 3. Add the secrets to Supabase

Supabase → **Edge Functions → Secrets** (or Project Settings → Edge Functions). Add:

| Name | Value |
|---|---|
| `RESEND_API_KEY` | the `re_…` key from Resend |
| `FROM_EMAIL` | `Weekfold <news@weekfold.in>` |
| `SITE_URL` | `https://weekfold.in` |
| `CRON_SECRET` | any long random password you make up (e.g. 30 random letters) |

## 4. Create the three edge functions

Supabase → **Edge Functions → Deploy a new function → Via editor**. Do this three times:

| Function name | Paste the code from | "Verify JWT" / "Enforce JWT" |
|---|---|---|
| `subscribe` | `supabase/functions/subscribe/index.ts` | **OFF** |
| `unsubscribe` | `supabase/functions/unsubscribe/index.ts` | **OFF** |
| `weekly` | `supabase/functions/weekly/index.ts` | **OFF** (it checks `CRON_SECRET` itself) |

Names must be exactly these. If the editor creates JWT verification ON by default, open the function's **Details/Settings** and turn it off.

## 5. Turn on the hourly send

SQL Editor → New query → paste `supabase/schedule.sql`. Replace `YOUR-PROJECT-REF` (the random id in your project URL) and `YOUR-CRON-SECRET` (the same value as step 3). Run.

## 6. Connect the website

Send Claude your **Project URL** (Project Settings → API, looks like `https://abcdefghijklmno.supabase.co`). It goes into `config.json` as `newsletter.supabase_url`, the site is rebuilt, and you upload the new zip as usual. Nothing else from Supabase is needed on the website; the keys stay inside Supabase.

## 7. Test it

1. On weekfold.in, enter your own email. The box should say **"You're in! This week's edition is on its way…"**
2. Check your inbox (and Promotions). The edition should arrive within a minute.
3. Supabase → Table Editor → `subscribers`: your row is there with `last_edition_sent` = this week's number.
4. Click **Unsubscribe** in the email → "You're unsubscribed" page; the row gets an `unsubscribed_at` date.

## Moving your Buttondown subscribers over (optional)

Buttondown → Subscribers → Export CSV. Supabase → Table Editor → `subscribers` → Insert → **Import data from CSV**, mapping only the `email` column. They'll get the current edition on the next hourly run, then every Sunday.

## Day to day

- Upload the Sunday zip as usual. The email goes out by itself within an hour.
- See who's subscribed: Table Editor → `subscribers`, or the `subscriber_counts` view.
- See what was sent: `sent_editions` (edition number, when, how many).
- Check for errors: Edge Functions → `weekly` → Logs.
