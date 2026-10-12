-- Email sign-ups for What Did They Say? (run once in the site's Supabase project)
create table if not exists public.subscribers (
  id bigint generated always as identity primary key,
  email text not null unique check (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$' and length(email) <= 254),
  first_name text check (first_name is null or length(first_name) <= 80),
  source text check (source is null or length(source) <= 40),
  created_at timestamptz not null default now(),
  unsubscribed_at timestamptz
);
alter table public.subscribers enable row level security;
-- The public site may only add a row; it can never read, change, or delete the list.
create policy "public can subscribe" on public.subscribers for insert to anon with check (unsubscribed_at is null);
