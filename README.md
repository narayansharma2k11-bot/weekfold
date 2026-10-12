# Weekfold

The world's week, folded into one free edition every Sunday. Made by Narayan Sharma.

## What's in this folder
| Path | What it is |
|---|---|
| `docs/` | **The website.** Your host serves this folder. It is rebuilt automatically, so don't edit it by hand. |
| `data/editions/` | One file per weekly edition (`41.json`, `40.json`, …). This is the only thing that changes each week. |
| `src/` | Page templates, the photo/illustration script and the subscribe/sign-in script. |
| `config.json` | Your settings: site address, newsletter, Google sign-in, contact email. |
| `build.py` | Turns `src/` + `data/` + `config.json` into `docs/`. It also checks every edition (7 days, 2+ sources per story). |
| `scripts/send_newsletter.py` + `.github/workflows/newsletter.yml` | Create the Sunday email in Buttondown when a new edition is pushed. |
| `WEEKLY_UPDATE.md` | The rules the Sunday update follows: dates, format, sourcing, photos. |

Each week, `build.py` also writes `docs/newsletter/latest.md` (the email text), `feed.xml` (RSS), `sitemap.xml` and `privacy.html`.

---

## Launch: what you need
| | Cost | Needed for |
|---|---|---|
| GitHub account | Free | Holding the site's files. Free hosting with GitHub Pages. Lets Claude update the site every Sunday. |
| Buttondown account | Free up to 100 subscribers | Collecting emails and sending the Sunday newsletter. |
| Your own domain, e.g. weekfold.com | About $10–15 a year (optional) | A proper address instead of `username.github.io/weekfold`. |
| Google Cloud project | Free (optional) | "Continue with Google" sign-in. The site works without it. |

### Step 1: Put the code on GitHub (about 10 minutes)
1. Sign up at github.com and click **New repository**. Name it `weekfold` and make it **Public**. Free GitHub Pages hosting needs a public repository.
2. Click **uploading an existing file** and drag in everything inside this folder. Make sure the hidden `.github` folder goes too: on a Mac, press **Cmd + Shift + .** in Finder to show it. Click **Commit changes**.

### Step 2: Turn on the website (2 minutes)
**GitHub Pages:** in the repository go to **Settings › Pages**, set Source to *Deploy from a branch*, Branch to **main** and the folder to **/docs**, then click Save. After a minute your site is live at `https://<your-username>.github.io/weekfold/`.

*Or Netlify:* click **Add new site › Import from Git**, choose the repository, leave the build command empty and set the publish directory to `docs`.

Then open `config.json` on GitHub (pencil icon), set `"site_url"` to your live address without a trailing slash, and commit. Claude will rebuild `docs/` with it on the next update, or you can ask Claude to do it straight away.

### Step 3: Email subscribers (15 minutes)
1. Sign up at buttondown.com. Set your newsletter name to **Weekfold** and add your sender details.
2. Copy your Buttondown **username** into `config.json` → `"newsletter": {"provider": "buttondown", "username": "..."}`. The site's Subscribe forms then add people to your list, and Buttondown emails each person a confirmation link.
3. In Buttondown, open **Settings › API** and copy the API key. In GitHub, go to **Settings › Secrets and variables › Actions**:
   - **Secrets** tab: add `BUTTONDOWN_API_KEY` with that key.
   - **Variables** tab: add `NEWSLETTER_MODE` = `draft`.
4. Every Sunday, when the new edition is pushed, the email is created in Buttondown as a **draft**. Check it and press Send. Once you trust it, change `NEWSLETTER_MODE` to `send` and it goes out by itself.

Buttondown's free plan covers 100 subscribers. Beyond that you pay Buttondown, or switch to Kit (free up to 10,000 subscribers): set `"provider": "kit", "form_id": "..."` in `config.json` and paste `docs/newsletter/latest.html` into a Kit broadcast each week. Kit's free plan has no API, so that step stays manual.

### Step 4: Google sign-in (optional, 15 minutes)
Today sign-in only greets the reader and fills in their email for one-tap subscribe. You can launch without it; the Sign in button stays hidden until you set it up.
1. In console.cloud.google.com, create a project. Set up the **OAuth consent screen** (External, app name Weekfold).
2. Go to **APIs & Services › Credentials › Create credentials › OAuth client ID**. Choose *Web application* and add your site address under **Authorised JavaScript origins**.
3. Paste the client ID into `config.json` → `"google_client_id"`.

### Step 5: Automatic Sunday updates by Claude
Tell Claude the repository name (for example `narayan/weekfold`) and ask it to connect the Sunday task. From then on, every Sunday at 1:23 AM IST it researches the week, adds `data/editions/<next>.json`, runs `build.py` and pushes. Your host redeploys the site and the newsletter workflow creates the email.

### Own domain (optional)
Buy the domain (for example from Cloudflare, Namecheap or Porkbun). Put it in `config.json` → `"custom_domain"`. Then follow GitHub's guide *Managing a custom domain for your GitHub Pages site*: add DNS records at your registrar, then turn on **Enforce HTTPS**.

---

## Photos and copyright
News agencies and newspapers (Reuters, AP, AFP, BBC, Al Jazeera and others) don't allow free reuse of their photos, so Weekfold never uses them. Each story names a Wikipedia article. The page shows that article's lead photo **if it is public domain, CC0, CC BY or CC BY-SA**, and credits the photographer and licence under the picture. Only if no free photo exists does it fall back to a generated illustration. Spot-check a few photos after launch. This is not legal advice.
