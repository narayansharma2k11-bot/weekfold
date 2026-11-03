// Weekfold: save an email and send this week's edition straight away (no confirmation step).
// Deploy as the "subscribe" edge function with "Verify JWT" turned OFF (the website calls it directly).
// Secrets: RESEND_API_KEY, FROM_EMAIL (e.g. "Weekfold <news@weekfold.in>"), SITE_URL (https://weekfold.in)
import { createClient } from "npm:@supabase/supabase-js@2";

const SITE = (Deno.env.get("SITE_URL") || "https://weekfold.in").replace(/\/$/, "");
const FROM = Deno.env.get("FROM_EMAIL") || "Weekfold <news@weekfold.in>";
const RESEND = Deno.env.get("RESEND_API_KEY") || "";
const FN_BASE = (Deno.env.get("SUPABASE_URL") || "") + "/functions/v1";
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

const ALLOWED = [SITE, SITE.replace("://", "://www."), "http://localhost:8775", "http://127.0.0.1:8775"];
function cors(req: Request) {
  const o = req.headers.get("origin") || "";
  return {
    "Access-Control-Allow-Origin": ALLOWED.includes(o) ? o : SITE,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, apikey, authorization, x-client-info",
    "Vary": "Origin",
  };
}
const json = (req: Request, status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors(req), "Content-Type": "application/json" } });

async function sha(s: string) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s + "|weekfold"));
  return Array.from(new Uint8Array(d)).map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}

async function latestEdition() {
  const meta = await (await fetch(`${SITE}/newsletter/latest.json?t=${Date.now()}`)).json();
  const html = await (await fetch(`${SITE}/${meta.email || "newsletter/latest-email.html"}?t=${Date.now()}`)).text();
  return { number: Number(meta.number), subject: String(meta.subject), html };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors(req) });
  if (req.method !== "POST") return json(req, 405, { error: "method" });

  let body: Record<string, string> = {};
  try { body = await req.json(); } catch { return json(req, 400, { error: "bad_request" }); }
  // Honeypot: real people never fill the hidden "website" field
  if (body.website) return json(req, 200, { status: "new" });
  const email = String(body.email || "").trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 254) return json(req, 400, { error: "invalid_email" });
  const source = String(body.source || "site").slice(0, 40);

  // Light abuse guard: at most 5 sign-ups per IP per hour
  const ip = (req.headers.get("x-forwarded-for") || "").split(",")[0].trim();
  const ipHash = ip ? await sha(ip) : null;
  if (ipHash) {
    const since = new Date(Date.now() - 3600_000).toISOString();
    const { count } = await db.from("subscribers").select("id", { count: "exact", head: true }).eq("ip_hash", ipHash).gte("created_at", since);
    if ((count || 0) >= 5) return json(req, 429, { error: "too_many" });
  }

  // Save (or re-activate) the subscriber
  const { data: existing, error: selErr } = await db.from("subscribers").select("id, token, unsubscribed_at, last_edition_sent").eq("email", email).maybeSingle();
  if (selErr) return json(req, 500, { error: "db" });
  let row = existing, status = "new";
  if (existing && !existing.unsubscribed_at) {
    status = "already";
  } else if (existing) {
    status = "back";
    const { data, error } = await db.from("subscribers").update({ unsubscribed_at: null, source }).eq("id", existing.id).select("id, token, unsubscribed_at, last_edition_sent").single();
    if (error) return json(req, 500, { error: "db" });
    row = data;
  } else {
    const { data, error } = await db.from("subscribers").insert({ email, source, ip_hash: ipHash }).select("id, token, unsubscribed_at, last_edition_sent").single();
    if (error) return json(req, 500, { error: "db" });
    row = data;
  }

  // Send this week's edition now (skipped if they already got it)
  let sent = false;
  try {
    const ed = await latestEdition();
    if (RESEND && row && (row.last_edition_sent ?? 0) < ed.number) {
      const unsub = `${FN_BASE}/unsubscribe?t=${row.token}`;
      const intro = status === "back"
        ? "Welcome back to Weekfold. Here's this week's edition. The next one arrives on Sunday."
        : "Welcome to Weekfold. Here's this week's edition, so you don't have to wait for Sunday. A new one arrives every Sunday.";
      const r = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${RESEND}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          from: FROM, to: [email], subject: ed.subject,
          html: ed.html.replaceAll("{{INTRO}}", intro).replaceAll("{{UNSUBSCRIBE_URL}}", unsub),
          headers: { "List-Unsubscribe": `<${unsub}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
        }),
      });
      if (r.ok) {
        sent = true;
        await db.from("subscribers").update({ last_edition_sent: ed.number }).eq("id", row.id);
      } else console.error("resend", r.status, await r.text());
    }
  } catch (e) { console.error("welcome", e); }

  return json(req, 200, { status, sent });
});
