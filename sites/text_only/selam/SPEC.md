# SPEC.md — Airline Web Agent Benchmark Environment (English + Amharic)

This file is the complete build brief. You are building a self-hosted, deterministic, programmatically
evaluable clone of a major African flag-carrier airline website, in two language builds, for use as a
WebArena / VisualWebArena-style agent benchmark environment.

Read this whole file before writing code. Do not ask the user questions that are answered here.

---

## 0. Inputs you are given

| Input | Location | Use |
|---|---|---|
| Task list spreadsheet | `./spec/tasks_source.xlsx` (sheet `Amharic-EthiopianAirline`) | 30 benchmark tasks, columns: `ID, Service, Task, Question, Task (Amharic), Eval Type, Complexity, Notes` |
| Reference site | `https://www.ethiopianairlines.com/en-us/` | Visual and information-architecture reference **only** |

The Amharic column in the spreadsheet is human-vetted. **It is the authoritative source for domain
terminology.** Mine it first (see §11).

---

## 1. Research purpose (why the constraints are what they are)

This environment measures whether web agents perform worse in a low-resource language when the
underlying site is held structurally constant. Two builds are produced that are **identical in every
respect except the language of every user-visible string**. Agent success rate is compared across them.

Every design decision below serves one of four requirements:

1. **Determinism** — the same action from the same start state always produces the same result.
2. **Resettability** — state returns exactly to seed between episodes.
3. **Programmatic evaluability** — every task has a machine-checkable success condition.
4. **Language isolation** — an agent running the Amharic build cannot reach, read, or infer English
   content, and vice versa.

---

## 2. Non-negotiable rules

- **No network calls at runtime.** Everything is local. No CDN fonts, no external images, no map tiles,
  no analytics. The apps must run fully offline.
- **No real brands.** See §3.
- **No language toggle.** There is no `?lang=`, no `/en/` `/am/` prefix, no cookie, no header, no
  environment variable, no admin page, and no UI control that changes language at runtime. Each build
  is monolingual and physically contains only one language's strings.
- **No live dates.** All date logic derives from a frozen clock (§7).
- **No randomness at request time.** Any pseudo-randomness (e.g. seat availability) is seeded and baked
  into the database at seed time, never generated per request.
- **No payment execution.** Payment flows terminate at a review page (§9.4).
- **No Docker.** Plain Python, `pip install -r requirements.txt`, `python run.py`.

---

## 3. Brand map (copyright / trademark avoidance)

The real airline's marks must not appear anywhere in either build. Geography stays real (city names,
airport names, IATA airport codes) because it is factual and is needed for realistic Amharic content.
Commercial brands are replaced.

Define these in a single module `app/brand.py` so the user can change them by editing one file.

| Real entity | Synthetic replacement | Amharic |
|---|---|---|
| Ethiopian Airlines | **Selam Airways** | ሰላም አየር መንገድ |
| Airline code | **SM** (flight numbers `SM 100`–`SM 999`) | SM (leave Latin) |
| ShebaMiles | **Selam Miles** | ሰላም ማይልስ |
| Cloud Nine (business) | **Highland Class** | ሃይላንድ ክላስ |
| Economy | **Selam Economy** / **Economy Flex** | — |
| Ethiopian Skylight In-Terminal Hotel | **Zena Transit Hotel** | ዜና ትራንዚት ሆቴል |
| Wi-Fi service | **SkyLink Wi-Fi** | ስካይሊንክ ዋይ-ፋይ |
| Car rental partner | **RiftDrive** | ሪፍት ድራይቭ |
| Insurance partner | **SafeVoyage Travel Cover** | ሴፍቮያጅ የጉዞ መድን |
| Rail partner | **EuroRail Connect** | ዩሮሬል ኮኔክት |
| e-Visa portal | **National eVisa Service** | ብሔራዊ ኢ-ቪዛ አገልግሎት |
| Lounges | **Highland Lounge**, **Selam Sky Lounge** | ሃይላንድ ላውንጅ / ሰላም ስካይ ላውንጅ |

**Consequence you must handle:** the spreadsheet task text says "Ethiopian Airlines" and
"ኢትዮጵያ አየር መንገድ" and names ShebaMiles / Cloud Nine / Skylight. When you generate task configs (§14),
rewrite every brand mention to the synthetic equivalent in **both** languages. Record the substitutions
in `spec/brand_substitutions.md`.

**Logo:** design an original SVG wordmark + roundel for Selam Airways. Simple geometric shapes only. Do
not trace, recolour, or derive from the reference site's logo.

---

## 4. Delivery model — and why (this answers the user's open question)

Build **one source repository**, plus an **export step** that emits **two fully independent, monolingual
zips**. Each zip is self-contained and contains no trace of the other language.

```
selam-airways-en.zip     → runs on port 7770, DB file selam_en.db
selam-airways-am.zip     → runs on port 7771, DB file selam_am.db
```

Rationale:

- *Single source* prevents structural drift. Two hand-maintained trees would diverge within days, and any
  divergence destroys the experiment — a measured performance gap could then be a structure gap, not a
  language gap.
- *Export-time stripping* gives the isolation the user asked for. `export.py` copies the tree, resolves
  every translation call at build time into baked strings, then **deletes the entire locale directory and
  the i18n machinery from the artifact**. The shipped Amharic zip contains no English UI strings, no
  `en.json`, no toggle code, no fallback path. An agent that reads the filesystem or guesses at query
  parameters finds nothing.
- *Separate DB files and ports* prevent cross-language state leakage when both are run on one machine.

Cross-run agent memory is a harness concern, not a site concern: run each language in a fresh agent
session and call `POST /reset` between episodes.

### 4.1 URL policy (documented decision)

**URL paths are identical ASCII in both builds** (`/booking/passengers`, not a Geʽez-script path).

Reasons: it keeps URL-match evaluations byte-identical across languages; percent-encoded Geʽez paths would
be a genuine structural difference and therefore a confound; and real Amharic-facing sites use Latin
slugs. Path segments are opaque tokens, not readable content. If the user later wants Amharic slugs,
change `SLUGS` in `app/routes_map.py` — everything else reads from it.

---

## 5. Stack and repository layout

**Stack:** Python 3.11, Flask, SQLAlchemy, SQLite, Jinja2, WTForms, ReportLab (PDF boarding pass),
vanilla JS (no build tooling, no npm), one hand-written stylesheet.

**Frontend fidelity:** look-alike rebuild with our own CSS — *not* a carbon copy of the reference markup.
Match the reference site's layout conventions, component vocabulary (hero search widget, tabbed
booking panel, card grids, breadcrumb + left-nav on content pages, mega-footer) and general feel. Use
scraped photography where photography is needed (§10). Do not copy the reference site's CSS files.

```
selam-airways/
├── SPEC.md
├── README.md
├── requirements.txt              # pinned
├── run.py                        # dev server entrypoint
├── export.py                     # produces the two monolingual zips
├── verify_parity.py              # proves the two builds are structurally identical
├── seed.py                       # builds seed.db from spec/seed_data/
├── app/
│   ├── __init__.py               # app factory
│   ├── brand.py
│   ├── clock.py                  # FROZEN_TODAY
│   ├── config.py
│   ├── models/                   # SQLAlchemy models, one module per domain
│   ├── blueprints/               # one per service area (§8)
│   ├── services/                 # pricing, availability, eligibility, seatmap, miles
│   ├── i18n/
│   │   ├── __init__.py           # t() helper, build-time resolvable
│   │   ├── en.json
│   │   ├── am.json
│   │   └── glossary.json         # locked domain terms, §11
│   ├── templates/
│   ├── static/
│   │   ├── css/  js/  img/  fonts/
│   └── routes_map.py             # SLUGS: canonical path constants
├── spec/
│   ├── tasks_source.xlsx
│   ├── seed_data/                # YAML/CSV inputs to seed.py
│   ├── brand_substitutions.md
│   └── translation_review.csv    # §11.3
├── tasks/
│   ├── tasks_en.json
│   ├── tasks_am.json
│   └── validators/               # one module per state-check task
├── data/
│   └── seed.db                   # checked in, generated by seed.py
└── tests/
```

---

## 6. Data model

SQLAlchemy models grouped by domain. Every table has a stable integer or string PK that is **assigned in
`seed.py`, never auto-generated at runtime for seeded rows** — validators reference these IDs.

**Network & inventory**
`airports` (iata, icao, city_en/city_am, country, timezone, terminal_count) ·
`routes` (origin, destination, distance_km, operating_days, block_time_min) ·
`aircraft_types` (code, name, cabin_layout_json) ·
`flights` (flight_no, route_id, date, dep_time, arr_time, aircraft_type, status, gate, terminal_dep,
terminal_arr, wifi_equipped, has_lounge_access) ·
`fare_classes` (code, cabin, refundable, changeable, change_fee, baggage_rule_id, miles_earn_pct) ·
`fares` (flight_id, fare_class, price_usd, seats_available)

**Booking**
`bookings` (pnr, surname, email, status, created_on, currency, total_paid, booked_channel) ·
`passengers` (booking_id, first_name, last_name, type[adult/child/infant], dob, loyalty_number,
special_meal, assistance_code, allergy_note) ·
`segments` (booking_id, flight_id, fare_class, checked_in, seat_number, baggage_allowance_kg) ·
`seat_maps` (aircraft_type, seat_no, row, col, cabin, is_exit, is_aisle, is_window, extra_legroom,
price_usd) ·
`seat_assignments` (segment_id, passenger_id, seat_no, paid_amount) ·
`change_requests`, `refund_requests` (booking_id, status, eligibility_reason, quoted_amount, fee,
reference_no) ·
`checkins` (segment_id, passenger_id, checked_in_at, boarding_pass_id, ineligibility_code) ·
`boarding_passes` (id, pdf_path, barcode_payload, gate, boarding_time, sequence_no)

**Ancillaries**
`baggage_rules` (route_region, cabin, pax_type, checked_pieces, checked_kg, cabin_kg, cabin_dims) ·
`special_baggage_items` (category, item, max_kg, fee_usd, notes) ·
`baggage_purchases` · `upgrade_offers` (segment_id, target_cabin, price_usd, miles_price, benefits_json,
eligibility_code) · `wifi_packages` (flight_id, name, mb, duration_min, price_usd) ·
`wifi_purchases` · `meals` (flight_id, cabin, menu_json) · `special_meal_codes` (code, name, description,
cutoff_hours) · `meal_requests` · `lounges` (airport, terminal, name, hours, location_desc,
access_rules_json, walk_in_price_usd) · `lounge_purchases` · `insurance_products` (name, coverage_json,
price_pct, price_min_usd) · `insurance_purchases`

**Loyalty**
`loyalty_members` (member_no, first_name, last_name, tier, miles_balance, qualifying_miles, joined_on,
email, password_hash) · `miles_transactions` · `award_inventory` (flight_id, cabin, miles_required,
taxes_usd, seats) · `missing_miles_claims` (member_no, ticket_no, flight_no, date, status, reference_no)

**Partners & services**
`hotel_rooms`, `hotel_bookings` (Zena Transit Hotel) · `car_offers`, `car_bookings` ·
`rail_connections` (arrival_city, rail_destination, operator, journey_min, ticket_type, booking_note) ·
`visa_types` (name, eligibility, documents_json, fee_usd, processing_days) ·
`stopover_packages` (min_layover_h, max_layover_h, cabin_required, hotel/transfer/lounge/tour options)

**Content & support**
`content_pages` (slug, title, body_html, category) — CMS table for all policy/help/static pages ·
`contact_offices` (country, city, phone, hours, email, channels_json, emergency_phone) ·
`faqs` · `promotions` · `feedback_tickets` (reference_no, category, status) · `vouchers` ·
`cargo_shipments` · `assistance_requests` · `group_enquiries` · `newsletter_subscriptions`

**Auth**
`users` (loyalty login), `sessions`. Booking retrieval uses PNR + surname, no password.

---

## 7. Determinism

### 7.1 Frozen clock
`app/clock.py` exposes `today()`, `now()`, `is_past(dt)`. All application code, templates and validators
use these — **`datetime.now()` is banned outside `clock.py`**. Add a test that greps for violations.

```python
FROZEN_TODAY = date(2026, 3, 16)   # verify this is a Monday; if not, shift to the nearest Monday
FROZEN_NOW   = datetime(2026, 3, 16, 9, 0, 0)  # Africa/Addis_Ababa
```

Every relative-time behaviour (check-in opens 48h before departure, change fee waived >72h out, refund
window, boarding pass availability, seat-selection cutoff) is computed against `FROZEN_NOW`.

### 7.2 Schedule window
Flights are seeded for **180 days centred on `FROZEN_TODAY`** (90 back, 90 forward), so both past-flight
tasks (missing miles claim) and future-flight tasks work.

### 7.3 Reset
`POST /reset` (no auth, no CSRF) copies `data/seed.db` over the live DB, clears the uploads/generated
directory (boarding pass PDFs), and drops all sessions. Returns `{"status":"ok","seed_hash":"<sha256>"}`.
Must complete in under 2 seconds. `GET /reset/status` returns the current hash so a harness can assert a
clean state before an episode.

### 7.4 Pricing
Prices are static per `(flight_id, fare_class)` in the DB. No dynamic pricing, no time-decay, no
inventory-driven price changes. Ancillary prices are fixed per row. Currency is USD everywhere, in both
builds (a currency selector would be a confound — do not add one).

---

## 8. Site map — 40 service areas

Twenty-two are exercised by the 30 tasks; the remaining eighteen are **functional distractors** that exist
so the agent has a realistic space to search and can plausibly go wrong. Distractors must be genuinely
functional (forms submit, searches return seeded results, confirmations render) — not dead links.

Task-backed areas are marked with the task IDs they serve.

| # | Area | Base route | Tasks |
|---|---|---|---|
| 1 | Home / hero search widget | `/` | 1,2 |
| 2 | Flight search & fare selection | `/book/search`, `/book/results` | 1,2 |
| 3 | Booking: passengers → seats → extras → review | `/book/passengers`, `/book/review` | 2 |
| 4 | Manage booking (PNR + surname) | `/manage`, `/manage/<pnr>` | 5,6,7,10,13,15,22 |
| 5 | Flight change | `/manage/<pnr>/change` | 6 |
| 6 | Refund request | `/manage/<pnr>/refund` | 7 |
| 7 | Online check-in | `/checkin` | 8,9 |
| 8 | Boarding pass | `/checkin/<id>/boarding-pass.pdf` | 8 |
| 9 | Seat selection / preferred seats | `/manage/<pnr>/seats` | 10,11 |
| 10 | Cabin upgrade (Highland Class) | `/manage/<pnr>/upgrade` | 15 |
| 11 | Extra baggage purchase | `/manage/<pnr>/baggage` | 13 |
| 12 | Baggage allowance calculator | `/baggage/allowance` | 12 |
| 13 | Special & sports baggage rules | `/baggage/special` | 14 |
| 14 | Delayed / damaged baggage report | `/baggage/report` | — |
| 15 | Flight status | `/flight-status` | 3 |
| 16 | Timetable / schedules | `/schedules` | 4 |
| 17 | Route map & network | `/network` | — |
| 18 | Destinations guide (city pages) | `/destinations/<city>` | — |
| 19 | Promotions & fare calendar | `/offers` | — |
| 20 | Loyalty enrollment | `/miles/join` | 18 |
| 21 | Loyalty dashboard | `/miles/account` | — |
| 22 | Missing miles claim | `/miles/claim` | 19 |
| 23 | Award ticket search | `/miles/award-search` | 20 |
| 24 | Miles redemption (upgrades, vouchers) | `/miles/redeem` | — |
| 25 | Lounge information | `/lounges` | 17 |
| 26 | Lounge access purchase | `/lounges/purchase` | 16 |
| 27 | On-board Wi-Fi | `/onboard/wifi` | 21 |
| 28 | In-flight dining & special meals | `/onboard/dining` | 22 |
| 29 | In-flight entertainment | `/onboard/entertainment` | — |
| 30 | Allergy & medical policy | `/help/allergies` | 23 |
| 31 | Special assistance requests | `/services/assistance` | — |
| 32 | Unaccompanied minors & pets | `/services/minors-pets` | — |
| 33 | Group booking enquiry | `/services/groups` | — |
| 34 | Corporate travel programme | `/services/corporate` | — |
| 35 | Cargo quote & tracking | `/cargo` | — |
| 36 | Stopover programme | `/stopover` | 24 |
| 37 | Travel requirements advisory | `/travel-requirements` | — |
| 38 | Help centre & contact directory | `/help`, `/help/contact` | 30 |
| 39 | Feedback & complaints | `/help/feedback` | — |
| 40 | Gift vouchers | `/vouchers` | — |

**Partner stubs** (own layouts, own headers, same host, clearly a different site):
`/partners/zena-hotel` (25) · `/partners/evisa` (26) · `/partners/eurorail` (27) ·
`/partners/riftdrive` (28) · `/partners/safevoyage` (29).

Each partner stub has its own nav and visual identity so URL-match and "did the agent leave the airline
site" evaluations are unambiguous. Entry to each is via a link on the airline site (a "Partner services"
hub at `/partners` plus contextual links in the relevant flows).

---

## 9. Behaviour specifications for the hard flows

### 9.1 Search & booking (tasks 1, 2)
Round-trip, one-way and multi-city tabs. Inputs: origin, destination, dates, passenger counts
(adult/child/infant), cabin. Results page shows outbound and return fare grids with at least three fare
families per cabin, sortable by price / duration / departure time, filterable by stops and time-of-day.
Booking proceeds: results → passenger details (validated forms) → seats (optional) → extras → **review**.
The review page displays a full price breakdown and a Pay button that is present but inert (§9.4).

### 9.2 Manage booking (tasks 5, 6, 7, 10, 13, 15, 22)
Retrieval by PNR + surname. Seeded PNRs must cover, deliberately, every branch the tasks need:

- fully refundable / non-refundable / partially refundable
- changeable free / changeable with fee / not changeable
- eligible for check-in / ineligible for at least three distinct reasons (see 9.3)
- upgrade-eligible / upgrade-unavailable (cabin full) / upgrade-not-offered (fare class excluded)
- with and without seats already assigned
- booked on the website (online refund eligible) vs booked via agent (offline only) — task 7 needs this

### 9.3 Check-in (tasks 8, 9)
Opens 48h before departure, closes 2h before. Ineligibility codes each with a distinct on-screen message:
`TOO_EARLY`, `CLOSED`, `INFANT_ON_LAP`, `SPECIAL_ASSISTANCE_REQUIRED`, `UNACCOMPANIED_MINOR`,
`DOCUMENT_CHECK_REQUIRED`, `CODESHARE_OPERATED_BY_PARTNER`, `GROUP_BOOKING`. Task 9 requires that at
least one seeded PNR hits one of these. Successful check-in generates a real PDF boarding pass via
ReportLab at a stable path, with a deterministic barcode payload (`PNR|SEG|SEQ`), and marks
`segments.checked_in = True`.

### 9.4 Payment boundary (tasks 2, 6, 7, 10, 13, 16, 21, 25, 28, 29)
Every purchase flow ends at a review page whose URL contains `/review`. The Pay button renders in a normal
enabled style but its handler shows an inline notice — do not disable it visually, or agents will read the
UI as broken. No card fields anywhere. No payment ever succeeds; there is no confirmation-of-payment page.
For state-check tasks the success condition is a **pending/draft row in the DB plus arrival at the review
URL**, never a completed payment.

### 9.5 Loyalty (tasks 18, 19, 20)
Enrollment creates a `loyalty_members` row and returns a membership number in a deterministic sequence
(`SM` + zero-padded counter starting from the seed high-water mark) — validators depend on this being
predictable. Missing-miles claims return a reference number `MC-<6 digits>`, also sequential. Award search
reads `award_inventory` and reports miles + taxes.

### 9.6 Stopover (task 24)
Eligibility rule, stated explicitly on the page: connection through Addis Ababa with a layover between 8
and 72 hours, on a single booking, in any cabin. Eligible itineraries show hotel, airport transfer, lounge
and city-tour options from `stopover_packages`.

### 9.7 Content pages
All policy, help, baggage-rules and advisory text lives in `content_pages` and renders through one
template. This makes the Amharic build a data translation, not a template fork.

---

## 10. Assets

Write `tools/fetch_assets.py` (run once at build time, not at runtime):

1. Crawl the reference site for photography only — destination imagery, cabin interiors, aircraft
   exteriors, lounge and food photography, hero banners.
2. **Reject anything containing the reference airline's marks**: logos, liveried tails, branded signage,
   uniformed staff with visible logos, cabin shots with branded headrests. When in doubt, discard.
   Manually review the fetched set and log every kept file in `static/img/MANIFEST.md` with source URL and
   a one-line description.
3. Downscale to max 1600px wide, convert to WebP with JPEG fallback, strip EXIF.
4. All aircraft and airline branding in the built site — logo, roundel, tail art, favicon, boarding pass
   header, lounge signage — is **original SVG you create**.
5. Add `NOTICE.md` at the repo root: photographic assets retrieved from a public airline website for
   non-commercial academic benchmarking, not redistributed publicly, all trademarks removed, all brand
   names fictional.
6. Bundle a Geʽez-capable open-licence font (Noto Sans Ethiopic, SIL OFL) locally in `static/fonts/`.
   The English build uses the same font stack so text rendering is not a confound.

Placeholder images are acceptable where the crawl yields nothing usable — generate flat-colour SVG
placeholders with a caption, and use the same placeholder in both builds.

---

## 11. Internationalisation

### 11.1 Mechanism
Every user-visible string goes through `t("key")`. No literal user-visible text in templates or Python.
Add a test that fails on any non-whitespace text node in a template that isn't a `t()` call or a variable.

Seeded *content* is translated too: `content_pages`, city names, airport names, meal names, policy prose,
lounge descriptions, contact office details, passenger names, promotion copy, validation and error
messages, PDF boarding pass labels, email-style confirmations, `<title>` tags, alt text, and placeholder
text. `seed.py` writes both `_en` and `_am` columns; `export.py` drops the unused column.

**Stays Latin/numeric in both builds:** IATA and ICAO codes, flight numbers, PNRs, ticket numbers,
membership numbers, reference numbers, fare class codes, seat numbers, currency code `USD`, email
addresses, URL paths.

### 11.2 Glossary (mandatory)
`app/i18n/glossary.json` locks one Amharic rendering per English domain term. Any term in the glossary
must render identically everywhere. Seed it from the spreadsheet's vetted Amharic column — extract at
minimum:

| English | Amharic (from spreadsheet) |
|---|---|
| round-trip | የደርሶ መልስ |
| booking reference | የቦታ ማስያዣ ማጣቀሻ |
| reservation / booking | የቦታ ማስያዣ |
| boarding pass | የመሳፈሪያ ፈቃድ |
| online check-in | የመስመር ላይ ቼክ-ኢን |
| checked baggage | የተመዘገበ ሻንጣ |
| cabin baggage | የእጅ ሻንጣ |
| aisle seat | የመተላለፊያ መቀመጫ |
| extra legroom | ተጨማሪ የእግር ቦታ |
| stopover | ማቆያ |
| lounge | ላውንጅ |
| travel insurance | የጉዞ መድን |
| refund | ተመላሽ ክፍያ |
| cabin class | የጉዞ ክፍል |
| itinerary | የጉዞ ዝርዝር |
| flight status | የበረራ ሁኔታ |
| fare difference | የታሪፍ ልዩነት |
| passenger | ተሳፋሪ |

Extend by reading every Amharic cell in the spreadsheet. Where the spreadsheet gives a rendering, that
rendering wins over anything you would generate.

**Transliteration rule for brands:** the spreadsheet transliterates rather than translates brand names
(ShebaMiles → ሸባማይልስ, Cloud Nine → ክላውድ ናይን). Apply the same rule to our synthetic brands:
Selam Miles → ሰላም ማይልስ, Highland Class → ሃይላንድ ክላስ, SkyLink → ስካይሊንክ.

### 11.3 Review artefact
Emit `spec/translation_review.csv` with columns `key, context (page/component), english, amharic,
back_translation, reviewed[y/n]`. Every generated Amharic string appears here. `back_translation` is your
literal English rendering of what the Amharic actually says, so a reviewer can spot errors without
reading both columns in full. Sort by page so review can be done screen by screen.

### 11.4 Dates and numbers
Gregorian calendar, Arabic (Western) numerals, Amharic month and weekday names. No Ethiopian calendar, no
Geʽez numerals. Times in 24-hour format. Time zone labels transliterated. Date format in the Amharic
build: `16 መጋቢት 2026` style — a fixed format string in `app/i18n/formats.py`, mirrored by a fixed
English format `16 March 2026` so that answer-match evaluation is symmetric.

---

## 12. Seed data

Written as YAML/CSV in `spec/seed_data/`, compiled by `seed.py` into `data/seed.db`. `seed.py` must be
idempotent and deterministic — same inputs, byte-identical DB, verified by hash in CI.

Scale targets:

| Entity | Count |
|---|---|
| Airports | 75 (Africa-weighted, plus Europe, Middle East, Asia, North America) |
| Routes | 140 |
| Flights | 180-day window; ~60 departures/day |
| Fare classes | 9 across 2 cabins |
| Bookings (PNRs) | 60, covering every branch in §9.2 |
| Passengers | ~110 |
| Loyalty members | 15 across 4 tiers, with 2 years of miles history each |
| Lounges | 14 across 8 airports |
| Aircraft types / seat maps | 6 |
| Special baggage items | 40 |
| Special meal codes | 14 |
| Content pages | 120+ |
| Contact offices | 45 countries |
| Award inventory rows | 400 |
| Hotel rooms | 5 types × 180 days |
| Promotions | 12 |

Passenger names in the Amharic build are Amharic-script Ethiopian names; in the English build the same
people appear in Latin transliteration. Same underlying person, same PNR, same row ID.

---

## 13. Parity verification

`verify_parity.py` runs both exported builds and asserts they are structurally identical. It fails the
build on any mismatch. Checks:

1. **Route table equality** — identical set of `(rule, methods, endpoint)` across builds.
2. **DOM skeleton equality** — for every route in a crawl list, render the page in both builds, strip all
   text nodes and attribute *values* except `id`/`class`/`name`/`type`/`href`, hash the resulting tag tree,
   compare. Any structural divergence is a bug.
3. **Element count equality** — per page: forms, inputs, buttons, links, images.
4. **Database parity** — identical table set, identical row counts, identical PK sets per table.
5. **Language purity** — the Amharic build contains no Latin-script user-visible text outside the
   whitelist in §11.1; the English build contains no Geʽez codepoints at all. Scan rendered HTML, not
   source.
6. **Isolation** — no route, query parameter, cookie, or header in either build changes the language;
   assert `en.json`/`am.json`/the i18n module are absent from the exported artifacts.

Write the crawl list to `spec/parity_routes.txt`; it must cover every route in §8 plus each partner stub.

---

## 14. Task configs

Generate `tasks/tasks_en.json` and `tasks/tasks_am.json` from the spreadsheet. **Same 30 IDs, same order,
same structure — only `intent` and `reference_answer` differ by language.**

Instantiate every placeholder against the seed data. "the specified travel dates" becomes concrete dates;
"the supplied booking reference" becomes a real seeded PNR. Choose values that make the task
non-degenerate: the answer should not be guessable without using the site.

```json
{
  "task_id": 1,
  "service": "Flight booking",
  "language": "en",
  "sites": ["selam"],
  "start_url": "http://localhost:7770/",
  "intent": "Find Selam Airways round-trip flights from Addis Ababa (ADD) to Nairobi (NBO) departing 12 April 2026 and returning 19 April 2026 for one adult, and report the available flight numbers and their prices.",
  "eval": {
    "eval_types": ["string_match"],
    "reference_answers": {
      "must_include": ["SM 308", "SM 309", "USD 412", "USD 468"]
    }
  },
  "require_reset": true,
  "complexity": "Medium",
  "notes": "Search + filters"
}
```

For `state-check` tasks add a validator:

```json
"eval": {
  "eval_types": ["program_html", "db_state"],
  "validator": "tasks.validators.task_13_extra_baggage",
  "validator_args": {"pnr": "QK7T2M", "expected_extra_kg": 23, "expected_charge_usd": 120}
}
```

Each validator is a Python function `validate(db_session, final_url, page_html) -> (bool, str)` returning
pass/fail plus a human-readable reason. Validators query the DB directly — they never scrape.

Rules for validators:
- Assert the *intended* state change and assert that *no unintended* change occurred (e.g. baggage added
  but no payment recorded, no other booking touched).
- For payment-boundary tasks, assert `final_url` matches the review URL **and** that the pending row
  exists **and** that no `*_purchases` row is marked paid.
- Never depend on wall-clock time; use `app.clock`.

Also emit `tasks/README.md` explaining how to run one episode: reset → launch agent with intent →
run validator → record result.

---

## 15. Build and run

```bash
pip install -r requirements.txt
python seed.py                    # regenerates data/seed.db
python run.py --lang en --port 7770
python export.py                  # writes dist/selam-airways-en.zip and dist/selam-airways-am.zip
python verify_parity.py           # must pass before shipping
```

Each exported zip contains: source with strings baked, its own `seed.db`, `requirements.txt`,
`static/`, its own `tasks_*.json` and validators, `NOTICE.md`, and a `README.md` whose entire content is
in that build's language, with a three-line quickstart:

```bash
pip install -r requirements.txt
python run.py
# open http://localhost:7770
```

The zip must run on a clean machine with Python 3.11 and no network access. Test this.

---

## 16. Build order

1. Skeleton: app factory, config, clock, brand, routes_map, base template, CSS, i18n plumbing.
2. Models + `seed.py` + seed data for network, flights, fares. Verify determinism by hash.
3. Search → results → booking → review (tasks 1, 2). This exercises the most machinery; get it right first.
4. Manage booking + all its sub-flows (tasks 5, 6, 7, 10, 11, 13, 15, 22).
5. Check-in + boarding pass PDF (tasks 8, 9).
6. Flight status, schedules, baggage rules, allergy, lounges, contact (tasks 3, 4, 12, 14, 17, 23, 30).
7. Loyalty (tasks 18, 19, 20), Wi-Fi (21), lounge purchase (16), stopover (24).
8. Partner stubs (tasks 25–29).
9. The 18 distractor service areas.
10. Asset pipeline, logo design.
11. Amharic pass: extract glossary from spreadsheet, translate `en.json` and all seeded content, emit
    `translation_review.csv`.
12. `export.py`, `verify_parity.py`, task configs, validators, tests.

Commit at the end of each phase with a message naming the phase.

---

## 17. Acceptance checklist

- [ ] Both zips run offline on a clean machine, no Docker, no network.
- [ ] `verify_parity.py` passes all six checks.
- [ ] No language toggle exists; the Amharic artifact contains zero English UI strings.
- [ ] `POST /reset` restores byte-identical DB state; hash matches after 20 consecutive full task runs.
- [ ] `grep -r "datetime.now\|date.today" app/` returns only `app/clock.py`.
- [ ] All 30 tasks have concrete instantiated intents in both languages, and every state-check task has a
      validator that passes on a correct manual run and fails on a plausible near-miss.
- [ ] No real airline trademark appears in code, content, filenames, alt text, or images.
- [ ] `spec/translation_review.csv` covers every Amharic string with a back-translation.
- [ ] 40 service areas reachable from the navigation; no dead links; every form submits and confirms.
- [ ] Boarding pass PDF downloads and renders Geʽez text correctly in the Amharic build.

---

## 18. Open items for the user

Flag these in your final summary rather than deciding silently:

1. Confirm the Selam Airways name and `SM` code, or swap them in `app/brand.py`.
2. `spec/translation_review.csv` needs a native-speaker pass before the Amharic build is used for
   measurement — the numbers are not valid until it is reviewed.
3. Any task whose spreadsheet wording could not be made non-degenerate against seed data, with your
   proposed rewording.
