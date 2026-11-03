// Weekfold: one-click unsubscribe. Deploy as "unsubscribe" with "Verify JWT" turned OFF.
// GET  /unsubscribe?t=TOKEN  → shows a small confirmation page (from the link in the email footer)
// POST /unsubscribe?t=TOKEN  → Gmail/Apple "Unsubscribe" button (List-Unsubscribe-Post one-click)
import { createClient } from "npm:@supabase/supabase-js@2";

const SITE = (Deno.env.get("SITE_URL") || "https://weekfold.in").replace(/\/$/, "");
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

const page = (title: string, text: string) => new Response(
  `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title></head>
<body style="margin:0;background:#f4efe4;font-family:Georgia,serif;color:#0b0b0b"><div style="max-width:520px;margin:12vh auto;background:#fff;border:1px solid #e3ddd0;padding:36px 32px">
<div style="font-weight:900;font-size:30px">Weekfold</div><h1 style="font-size:24px;margin:22px 0 10px">${title}</h1>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:16px;line-height:1.6;color:#3d3b38">${text}</p>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:15px"><a href="${SITE}" style="color:#1f3a6e">Back to weekfold.in</a></p></div></body></html>`,
  { headers: { "Content-Type": "text/html; charset=utf-8" } });

Deno.serve(async (req) => {
  const t = new URL(req.url).searchParams.get("t") || "";
  if (!/^[0-9a-f-]{36}$/i.test(t)) return page("That link didn't work", "The unsubscribe link looks incomplete. Reply to any Weekfold email and we'll take you off the list by hand.");
  const { data, error } = await db.from("subscribers").update({ unsubscribed_at: new Date().toISOString() }).eq("token", t).is("unsubscribed_at", null).select("email");
  if (req.method === "POST") return new Response("ok");
  if (error) return page("Something went wrong", "Please try the link again in a minute.");
  return page("You're unsubscribed", (data && data.length ? "We won't email you again. " : "This address was already off the list. ")
    + `Changed your mind? Enter your email again on <a href="${SITE}" style="color:#1f3a6e">weekfold.in</a>.`);
});
