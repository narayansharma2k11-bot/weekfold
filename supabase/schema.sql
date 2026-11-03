-- Weekfold email list. Paste this whole file into Supabase › SQL Editor › New query › Run.
-- Safe to run more than once.

create extension if not exists citext;
create extension if not exists pg_net;
create extension if not exists pg_cron;

-- Everyone who has entered their email on weekfold.in
create table if not exists public.subscribers (
  id                 uuid primary key default gen_random_uuid(),
  email              citext not null unique,
  source             text,                                   -- which form: landing, home, dialog …
  created_at         timestamptz not null default now(),
  unsubscribed_at    timestamptz,                            -- set when they click Unsubscribe
  last_edition_sent  integer,                                -- newest edition number they have been emailed
  token              uuid not null default gen_random_uuid(),-- secret for their one-click unsubscribe link
  ip_hash            text                                    -- hashed IP, only used to stop bulk sign-up abuse
);
create index if not exists subscribers_active_idx on public.subscribers (last_edition_sent) where unsubscribed_at is null;
create index if not exists subscribers_ip_idx on public.subscribers (ip_hash, created_at);

-- One row per edition that has gone out to the list
create table if not exists public.sent_editions (
  number      integer primary key,
  subject     text,
  started_at  timestamptz not null default now(),
  finished_at timestamptz,
  recipients  integer not null default 0
);

-- Lock both tables: the website never reads or writes them directly.
-- Only the edge functions (which use the service role key, server-side) can touch them.
alter table public.subscribers   enable row level security;
alter table public.sent_editions enable row level security;
revoke all on public.subscribers, public.sent_editions from anon, authenticated;

-- Handy view for you in the Table Editor
create or replace view public.subscriber_counts with (security_invoker = true) as
select count(*) filter (where unsubscribed_at is null) as active,
       count(*) filter (where unsubscribed_at is not null) as unsubscribed,
       count(*) filter (where created_at > now() - interval '7 days') as joined_last_7_days
from public.subscribers;
revoke all on public.subscriber_counts from anon, authenticated;
