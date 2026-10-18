# Service expansion — sub-services for future tasks

**Status:** design, agreed 2026-09-02. Extends SPEC.md §8.

## Why this exists

The 30 tasks in `tasks_source.xlsx` are the first batch, not the last. The service areas are
expected to stay fixed while the task count grows. If sub-services were added only as tasks
demanded them, every new batch would force a re-seed and a re-run of `verify_parity.py`, and
older task episodes would no longer be reproducible against the newer build.

So: build the sub-services **now**, seeded and functional, before the tasks that use them exist.

This also serves a second purpose that matters more than it looks. An agent asked to
"find the checked baggage allowance" on a site where `/baggage/allowance` is the only baggage
page has been handed the answer by the site's own poverty. On a site that also offers excess
fees, restricted items, sports equipment, musical instruments and a delayed-bag tracker, the
agent has to *choose*. Sub-services are the distractor set, and the distractor set is what the
benchmark actually measures.

## Design rules for every sub-service

1. **Genuinely functional.** Forms validate, submit, write a row, and render a confirmation
   with a reference number. No dead links, no "coming soon". A distractor that is visibly
   broken stops being a distractor.
2. **Deterministic and seeded.** Every lookup resolves against seeded rows. No sub-service
   invents data at request time.
3. **Task-shaped.** Each one must be able to carry a future task with no new infrastructure.
   Tagged below with its eval affordance:
   - `A` answer-match — seeded data with a unique, non-guessable answer
   - `S` state-check — writes a row a validator can assert on
   - `U` URL-match — a distinct terminal URL
   - `E` eligibility branch — same input space, different outcomes by seeded condition
4. **Payment boundary respected.** Every purchase sub-service terminates at `/review`
   per SPEC.md §9.4. No exceptions, including partner stubs.
5. **Reference-number sequences are reserved up front** (below), so a task batch added in six
   months does not collide with one added today.
6. **Both languages, always.** A sub-service added in English only would break §13 parity.

## Reserved reference-number prefixes

Sequential, seeded high-water mark, zero-padded to 6. Latin in both builds per §11.1.

| Prefix | Domain | Prefix | Domain |
|---|---|---|---|
| `MC-` | missing miles claim | `PIR-` | delayed/damaged baggage |
| `RF-` | refund request | `AS-` | assistance request |
| `CH-` | change request | `GR-` | group enquiry |
| `FB-` | feedback ticket | `CG-` | cargo shipment |
| `MD-` | medical clearance | `CP-` | compensation claim |
| `VC-` | voucher | `HD-` | held reservation |
| `CO-` | corporate enrolment | `SB-` | stopover booking |

## The expansion

Task-backed routes from §8 are listed for context in *italics*; **bold** rows are new.

### Booking & search (areas 1–3)
| Route | Aff. | Note |
|---|---|---|
| */book/search*, */book/results* | | tasks 1, 2 |
| **/book/multi-city** | A,S | up to 4 segments; §9.1 already requires the tab |
| **/book/flexible-dates** | A | ±3-day fare calendar grid around a search |
| **/book/fare-rules/`<class>`** | A | per-fare-family rules: change fee, refundability, miles % |
| **/book/hold** | S,U | hold a fare 48h against `FROZEN_NOW`; writes `held_reservations` |
| **/book/promo-code** | E | seeded valid / expired / route-ineligible / already-used codes |

### Manage booking (areas 4–6)
| Route | Aff. | Note |
|---|---|---|
| */manage/`<pnr>`/change*, */refund* | | tasks 6, 7 |
| **/manage/`<pnr>`/contact-details** | S | edit email/phone; APIS passport capture |
| **/manage/`<pnr>`/cancel** | E,S | cancel vs refund are different flows — a real trap |
| **/manage/`<pnr>`/receipt** | A,U | fare receipt / tax invoice breakdown |
| **/manage/`<pnr>`/itinerary.pdf** | U | printable itinerary, ReportLab, same as boarding pass |
| **/manage/`<pnr>`/change/route** | E,S | route change ≠ date change; different fee table |
| **/manage/`<pnr>`/change/same-day** | E | eligibility keyed to departure within 24h of `FROZEN_NOW` |
| **/manage/refund/status** | A | look up an `RF-` reference |

### Check-in & seats (areas 7–9)
| Route | Aff. | Note |
|---|---|---|
| */checkin*, */checkin/`<id>`/boarding-pass.pdf* | | tasks 8, 9 |
| **/checkin/`<id>`/change-seat** | S | post-check-in seat move |
| **/checkin/`<id>`/bags** | S | declare checked bags at check-in |
| **/checkin/`<id>`/cancel** | S | undo check-in; flips `segments.checked_in` back |
| **/checkin/`<id>`/boarding-pass/email** | U | stub send, confirmation page, no mail sent |
| **/manage/`<pnr>`/seats/legend** | A | seat characteristics key (exit, bassinet, recline-limited) |

### Baggage (areas 11–14)
| Route | Aff. | Note |
|---|---|---|
| */baggage/allowance*, */baggage/special*, */baggage/report* | | tasks 12, 14 |
| **/baggage/fees** | A | excess-weight and extra-piece fee table by route region |
| **/baggage/restricted-items** | A | searchable dangerous-goods list — strong answer-match |
| **/baggage/musical-instruments** | A,E | cabin vs hold vs extra-seat by dimension |
| **/baggage/report/status** | A | look up a `PIR-` reference |
| **/manage/`<pnr>`/baggage/bundles** | S | prepaid multi-bag bundles, cheaper than per-bag |

### Flight information (areas 15–19)
| Route | Aff. | Note |
|---|---|---|
| */flight-status*, */schedules*, */network*, */destinations*, */offers* | | tasks 3, 4 |
| **/flight-status/route** | A | by origin+destination rather than flight number |
| **/flight-status/departures/`<iata>`** | A | live-style airport board, seeded |
| **/flight-status/arrivals/`<iata>`** | A | as above |
| **/flight-status/subscribe** | S | status alerts for a flight; writes a row |
| **/schedules/seasonal** | A | routes that operate only part of the 180-day window |
| **/network/codeshare-partners** | A | which partner operates which codeshare — feeds §9.3 |
| **/network/new-routes** | A | launch dates inside the window |
| **/destinations/`<city>`/attractions** | A | city guide detail |
| **/offers/fare-calendar** | A | cheapest fare per day, 30-day grid |
| **/offers/`<id>`** | A,E | promo detail + T&C; some expired against `FROZEN_NOW` |

### Loyalty (areas 20–24)
| Route | Aff. | Note |
|---|---|---|
| */miles/join*, */claim*, */award-search*, */redeem* | | tasks 18, 19, 20 |
| **/miles/account/statement** | A | 2 years of seeded transactions, filterable by date |
| **/miles/account/tier-progress** | A,E | qualifying miles to next tier — per-member arithmetic |
| **/miles/account/nominees** | S | family/nominee list, add and remove |
| **/miles/award-chart** | A | region-pair miles table, cabin × season |
| **/miles/claim/status** | A | look up an `MC-` reference |
| **/miles/claim/partner** | S,E | partner-airline claim, different form and cutoff |
| **/miles/redeem/vouchers** | S | miles → voucher, terminates at review |
| **/miles/buy-miles** | S | miles purchase, terminates at review |

### On-board & lounges (areas 25–29)
| Route | Aff. | Note |
|---|---|---|
| */lounges*, */onboard/wifi*, */onboard/dining* | | tasks 16, 17, 21, 22 |
| **/lounges/`<id>`** | A | per-lounge detail: hours, location, amenities, access rules |
| **/lounges/eligibility** | E | checker: tier × cabin × fare class → yes/no/paid |
| **/onboard/wifi/coverage** | A | which aircraft types and routes are equipped |
| **/onboard/dining/menu/`<flight>`** | A | seeded menu per flight and cabin |
| **/onboard/dining/special-meals** | A | the 14 `special_meal_codes` with cutoff hours |
| **/onboard/entertainment/catalog** | A | searchable film/music list — excellent answer-match |

### Assistance, services, support (areas 30–40)
| Route | Aff. | Note |
|---|---|---|
| */help/allergies*, */help/contact*, */stopover* | | tasks 23, 24, 30 |
| **/help/medical-clearance** | S | MEDIF-style form; writes `MD-` reference |
| **/help/fitness-to-fly** | A,E | pregnancy, recent surgery, oxygen — branch by condition |
| **/services/assistance/wheelchair** | S,E | WCHR/WCHS/WCHC codes with different rules |
| **/services/assistance/status** | A | look up an `AS-` reference |
| **/services/pets** | A,E | cabin vs hold by weight and breed; fee table |
| **/services/minors** | A,E | age bands with different escort requirements |
| **/travel-requirements/`<from>`/`<to>`** | A,E | visa/passport/health matrix — very high task yield |
| **/cargo/quote**, **/cargo/track**, **/cargo/restrictions** | A,S | `CG-` reference |
| **/help/compensation-claim** | S,E | delay/cancellation claim, eligibility by delay hours |
| **/help/feedback/status** | A | look up an `FB-` reference |
| **/vouchers/buy**, **/vouchers/balance** | S,A | `VC-` reference; balance lookup by code |
| **/stopover/packages**, **/stopover/book** | A,S | detail + booking to review |

## Scale consequence — read this before approving

This is roughly **+95 routes** on top of §8, and it close to **doubles the build**. The
seed-data burden grows faster than the route count, because rules 2 and 3 mean each new route
needs seeded rows with unique answers, in both languages, and every one of them is subject to
§13 parity checking and §11.3 translation review.

That is the right trade if the task count is genuinely going to grow. It is a poor trade if it
does not — a benchmark environment nobody writes tasks against is just a large website.

The build order in SPEC.md §16 is unchanged. These sub-services are added **within** each
phase, not as a phase of their own, so the task-backed routes for a phase land first and the
phase's sub-services follow before moving on.
