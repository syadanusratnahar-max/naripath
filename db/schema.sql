-- NariPath database schema (Supabase / PostgreSQL)
-- Load order: run this file, then import db/resources.json into public.resources.

create type data_type as enum ('A_public_source', 'B_demo', 'C_provider_verified');
-- Status shown to users. A source URL alone never makes a listing provider_confirmed.
create type listing_status as enum ('public_source', 'awaiting_confirmation', 'provider_confirmed', 'needs_review', 'demo');
create type cost_type as enum ('free', 'paid', 'unknown');

create table public.resources (
  id                  text primary key,
  pillar              text not null check (pillar in (
                        'education-career','health-wellbeing','rights-legal',
                        'personal-digital-safety','financial-independence','everyday-community')),
  data_type           data_type not null default 'A_public_source',
  status              listing_status not null default 'public_source',
  not_found           text[] not null default '{}',  -- fields searched for and not publicly available, e.g. {phone}
  location            text not null,            -- district slug or 'nationwide'
  cost                cost_type not null default 'unknown',
  life_stages         text[] not null default '{}',
  name_en             text not null,
  name_bn             text not null,
  org_en              text not null,
  org_bn              text not null,
  description_en      text not null,
  description_bn      text not null,
  eligibility_en      text,                     -- null = not published (Gap Finder flags it)
  eligibility_bn      text,
  required_documents  jsonb not null default '[]',   -- [{en, bn}]
  phone               text,
  email               text,
  website             text,
  facebook            text,
  address_en          text,
  address_bn          text,
  caution_en          text,                     -- shown as "Please note"
  caution_bn          text,
  sources             jsonb not null default '[]',   -- [{en, bn, url}] at least one for type A
  last_checked        date not null,
  next_review         date not null,
  -- Type C only: who verified it and how
  verified_by         text,
  verification_note   text,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now(),
  constraint type_a_needs_source check (data_type <> 'A_public_source' or jsonb_array_length(sources) > 0),
  constraint type_c_needs_reviewer check (data_type <> 'C_provider_verified' or verified_by is not null),
  constraint confirmed_needs_reviewer check (status <> 'provider_confirmed' or verified_by is not null)
);

create index resources_pillar_idx   on public.resources (pillar);
create index resources_location_idx on public.resources (location);
create index resources_review_idx   on public.resources (next_review);
create index resources_search_idx   on public.resources using gin (
  to_tsvector('simple', name_en || ' ' || name_bn || ' ' || org_en || ' ' || org_bn || ' ' || description_en || ' ' || description_bn)
);

-- Anonymous "Report a problem" submissions. No names, phone numbers or free text: only a fixed reason.
create table public.listing_reports (
  id           bigint generated always as identity primary key,
  resource_id  text not null references public.resources(id) on delete cascade,
  reason       text not null check (reason in ('contact','outdated','closed','wrong')),
  created_at   timestamptz not null default now()
);

-- Row-level security: anyone can read listings and file a report; only admins can change listings.
alter table public.resources       enable row level security;
alter table public.listing_reports enable row level security;

create policy "public can read resources"  on public.resources       for select using (true);
create policy "public can file reports"    on public.listing_reports for insert with check (true);
-- Admin write policies: add once Supabase Auth roles are set up, e.g.
-- create policy "admins manage resources" on public.resources for all
--   using (auth.jwt() ->> 'role' = 'admin') with check (auth.jwt() ->> 'role' = 'admin');

-- Gap Finder view: listings overdue for review, missing eligibility, or with no direct contact.
create view public.gap_finder as
select id, name_en, location,
       status,
       next_review < current_date                                  as review_overdue,
       not_found                                                   as checked_not_available,
       eligibility_en is null                                      as missing_eligibility,
       (phone is null and email is null and website is null and facebook is null) as no_direct_contact,
       (select count(*) from public.listing_reports lr where lr.resource_id = r.id) as user_reports
from public.resources r;
