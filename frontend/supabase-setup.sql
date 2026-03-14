-- Run this in Supabase Dashboard → SQL Editor
-- Creates the users table for Pitch app profiles

create table if not exists public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  phone text not null,
  first_name text not null default '',
  character_id text,
  signal_enabled boolean not null default true,
  liquid_api_key text,
  liquid_api_secret text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Enable Row Level Security
alter table public.users enable row level security;

-- Users can only read/update their own row
create policy "Users can view own profile"
  on public.users for select
  using (auth.uid() = id);

create policy "Users can update own profile"
  on public.users for update
  using (auth.uid() = id);

create policy "Users can insert own profile"
  on public.users for insert
  with check (auth.uid() = id);

-- Service role can do anything (for clear-database.sh)
create policy "Service role full access"
  on public.users for all
  using (auth.role() = 'service_role');

-- Auto-update updated_at
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger on_users_updated
  before update on public.users
  for each row execute function public.handle_updated_at();
