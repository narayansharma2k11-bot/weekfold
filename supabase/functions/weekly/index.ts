// Weekfold: email each new edition to the whole list, once.
// Deploy as "weekly" with "Verify JWT" turned OFF; it is protected by the x-cron-secret header instead.
// Called every hour by pg_cron (schedule.sql). It reads newsletter/latest.json from the live site and
// only sends to people whose last_edition_sent is older than that edition, so:
//   • nobody gets the same edition twice (including people who signed up after it went live),
//   • if Resend's daily limit is hit, the rest are sent automatically on the next runs.
// Secrets: RESEND_API_KEY, FROM_EMAIL, SITE_URL, CRON_SECRET
import { createClient } from "npm:@supabase/supabase-js@2";

const SITE = (Deno.env.get("SITE_URL") || "https://weekfold.in").replace(/\/$/, "");
const FROM = Deno.env.get("FROM_EMAIL") || "Weekfold <news@weekfold.in>";
const RESEND = Deno.env.get("RESEND_API_KEY") || "";
const SECRET = Deno.env.get("CRON_SECRET") || "";
const FN_BASE = (Deno.env.get("SUPABASE_URL") || "") + "/functions/v1";
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const INTRO = "Here's this week's Weekfold: the stories that still mattered by Sunday, one page for every day.";

Deno.serve(async (req) => {
  if (!SECRET || req.headers.get("x-cron-secret") !== SECRET) return new Response("forbidden", { status: 403 });
  if (!RESEND) return new Response("RESEND_API_KEY missing", { status: 500 });

  const meta = await (await fetch(`${SITE}/newsletter/latest.json?t=${Date.now()}`)).json();
  const number = Number(meta.number), subject = String(meta.subject);
  const html = await (await fetch(`${SITE}/${meta.email || "newsletter/latest-email.html"}?t=${Date.now()}`)).text();
  if (!number || !html.includes("{{UNSUBSCRIBE_URL}}")) return new Response("edition email not found on site", { status: 502 });

  // Only editions newer than the newest one already started go out (so re-uploading an old zip never re-sends)
  const { data: last } = await db.from("sent_editions").select("number").order("number", { ascending: false }).limit(1).maybeSingle();
  if (last && last.number > number) return new Response(JSON.stringify({ skipped: "site shows an older edition", site: number, last: last.number }));
  await db.from("sent_editions").upsert({ number, subject }, { onConflict: "number", ignoreDuplicates: true });

  let total = 0, stopped = "";
  for (let round = 0; round < 50; round++) {
    const { data: rows, error } = await db.from("subscribers").select("id, email, token")
      .is("unsubscribed_at", null).or(`last_edition_sent.is.null,last_edition_sent.lt.${number}`).limit(100);
    if (error) { stopped = "db: " + error.message; break; }
    if (!rows || !rows.length) break;
    const batch = rows.map((r) => {
      const unsub = `${FN_BASE}/unsubscribe?t=${r.token}`;
      return {
        from: FROM, to: [r.email], subject,
        html: html.replaceAll("{{INTRO}}", INTRO).replaceAll("{{UNSUBSCRIBE_URL}}", unsub),
        headers: { "List-Unsubscribe": `<${unsub}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
      };
    });
    const r = await fetch("https://api.resend.com/emails/batch", {
      method: "POST", headers: { Authorization: `Bearer ${RESEND}`, "Content-Type": "application/json" }, body: JSON.stringify(batch),
    });
    if (!r.ok) { stopped = `resend ${r.status}: ${(await r.text()).slice(0, 300)}`; break; }   // e.g. daily limit: resumes next hour
    await db.from("subscribers").update({ last_edition_sent: number }).in("id", rows.map((x) => x.id));
    total += rows.length;
  }
  const { data: cur } = await db.from("sent_editions").select("recipients").eq("number", number).single();
  await db.from("sent_editions").update({ recipients: (cur?.recipients || 0) + total, ...(stopped ? {} : { finished_at: new Date().toISOString() }) }).eq("number", number);
  return new Response(JSON.stringify({ edition: number, sent_now: total, stopped: stopped || null }), { headers: { "Content-Type": "application/json" } });
});
