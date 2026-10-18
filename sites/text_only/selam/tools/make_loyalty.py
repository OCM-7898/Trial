import pathlib
import random
import sqlite3
import sys
from datetime import timedelta

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.clock import FROZEN_TODAY, WINDOW_START

SEED = 18_19_20

TIERS = {"blue": (0, 5), "silver": (25_000, 4), "gold": (50_000, 4), "platinum": (100_000, 2)}

TIER_ORDER = ("blue", "silver", "gold", "platinum")


def band(tier: str) -> tuple[int, int]:
    floor = TIERS[tier][0]
    index = TIER_ORDER.index(tier)
    ceiling = TIERS[TIER_ORDER[index + 1]][0] if index + 1 < len(TIER_ORDER) else 250_000
    return floor, ceiling

AWARD_BANDS = [(1500, 15_000, 35_000), (3500, 25_000, 60_000),
               (6500, 40_000, 95_000), (100_000, 60_000, 140_000)]


def award_price(distance_km: int, cabin: str) -> int:
    for limit, economy, business in AWARD_BANDS:
        if distance_km <= limit:
            return economy if cabin == "economy" else business
    return AWARD_BANDS[-1][1 if cabin == "economy" else 2]


def main() -> None:
    rng = random.Random(SEED)
    names = yaml.safe_load((ROOT / "spec/seed_data/names.yaml").read_text("utf-8"))
    conn = sqlite3.connect(ROOT / "data" / "seed.db")

    members, transactions = [], []
    member_id = transaction_id = 1
    counter = 0

    for tier, (floor, count) in TIERS.items():
        for _ in range(count):
            counter += 1
            given = rng.choice(names["given_female"] if rng.random() < 0.5 else names["given_male"])
            family = rng.choice(names["family"])

            floor, ceiling = band(tier)
            target = rng.randint(floor + 1_000, ceiling - 1_500)

            history, balance, qualifying = [], 0, 0
            months = [m for m in range(24, 0, -1) if rng.random() >= 0.45]
            for month in months:
                earn = rng.choice([1200, 1850, 2400, 3100, 4600, 5800])
                if qualifying + earn > target:
                    continue
                posted = FROZEN_TODAY - timedelta(days=month * 30 + rng.randint(0, 20))
                if posted < WINDOW_START - timedelta(days=400):
                    continue
                history.append({
                    "posted_on": posted.isoformat(), "kind": "flight",
                    "description_en": "Flight miles", "description_am": "የበረራ ማይሎች",
                    "flight_no": f"SM{rng.randint(100, 263)}",
                    "miles": earn, "qualifying_miles": earn,
                })
                balance += earn
                qualifying += earn

            remainder = target - qualifying
            if remainder > 0:
                history.append({
                    "posted_on": (FROZEN_TODAY - timedelta(days=rng.randint(30, 300))).isoformat(),
                    "kind": "flight",
                    "description_en": "Flight miles", "description_am": "የበረራ ማይሎች",
                    "flight_no": f"SM{rng.randint(100, 263)}",
                    "miles": remainder, "qualifying_miles": remainder,
                })
                balance += remainder
                qualifying += remainder

            if rng.random() < 0.4:
                spend = rng.choice([15_000, 25_000, 40_000])
                if balance > spend:
                    history.append({
                        "posted_on": (FROZEN_TODAY - timedelta(days=rng.randint(20, 400))).isoformat(),
                        "kind": "redeem",
                        "description_en": "Award ticket redemption",
                        "description_am": "የሽልማት ትኬት መቤዠት",
                        "flight_no": None, "miles": -spend, "qualifying_miles": 0,
                    })
                    balance -= spend

            members.append({
                "id": member_id, "member_no": f"SM{counter:08d}",
                "first_name_en": given[0], "first_name_am": given[1],
                "last_name_en": family[0], "last_name_am": family[1],
                "email": f"{given[0].lower()}.{family[0].lower()}{counter}@example.com",
                "tier": tier, "miles_balance": balance, "qualifying_miles": qualifying,
                "joined_on": (FROZEN_TODAY - timedelta(days=rng.randint(400, 2600))).isoformat(),
                "country_code": "ET", "created_at_runtime": False,
            })
            for entry in sorted(history, key=lambda h: h["posted_on"]):
                transactions.append({"id": transaction_id, "member_id": member_id, **entry})
                transaction_id += 1
            member_id += 1

    AWARD_ROUTES = ["NBO", "DXB", "LHR", "JNB", "LOS", "FRA", "DAR", "CAI", "BOM", "IAD"]
    placeholders = ",".join("?" for _ in AWARD_ROUTES)
    flights = conn.execute(f"""
        select f.id, r.distance_km, a.rows_business
        from flights f join routes r on r.id = f.route_id
        join aircraft_types a on a.id = f.aircraft_id
        join airports ao on ao.id = r.origin_id
        join airports ad on ad.id = r.destination_id
        where f.date > ? and f.status = 'scheduled'
          and (ao.iata in ({placeholders}) or ad.iata in ({placeholders}))
          and (ao.iata = 'ADD' or ad.iata = 'ADD')
        order by f.date, f.id
    """, (FROZEN_TODAY.isoformat(), *AWARD_ROUTES, *AWARD_ROUTES)).fetchall()

    award, award_id = [], 1
    for flight_id, distance, rows_business in flights:
        award.append({"id": award_id, "flight_id": flight_id, "cabin": "economy",
                      "miles_required": award_price(distance, "economy"),
                      "taxes_usd": float(round(30 + distance * 0.012)),
                      "seats": rng.randint(0, 6)})
        award_id += 1
        if rows_business and award_id <= 400:
            award.append({"id": award_id, "flight_id": flight_id, "cabin": "business",
                          "miles_required": award_price(distance, "business"),
                          "taxes_usd": float(round(60 + distance * 0.02)),
                          "seats": rng.randint(0, 3)})
            award_id += 1
        if award_id > 400:
            break

    for entry in members:
        floor, ceiling = band(entry["tier"])
        assert floor <= entry["qualifying_miles"] < ceiling, (
            f"{entry['member_no']} is {entry['tier']} with "
            f"{entry['qualifying_miles']:,} qualifying miles, outside [{floor:,}, {ceiling:,})"
        )

    by_member: dict[int, dict[str, int]] = {}
    for row in transactions:
        totals = by_member.setdefault(row["member_id"], {"miles": 0, "qualifying": 0})
        totals["miles"] += row["miles"]
        totals["qualifying"] += row["qualifying_miles"]
    for entry in members:
        totals = by_member[entry["id"]]
        assert totals["miles"] == entry["miles_balance"], (
            f"{entry['member_no']}: statement sums to {totals['miles']:,} "
            f"but the balance says {entry['miles_balance']:,}")
        assert totals["qualifying"] == entry["qualifying_miles"], (
            f"{entry['member_no']}: qualifying miles disagree with the statement")
    bookable = sum(1 for a in award if a["seats"] > 0)
    assert bookable > 100, f"only {bookable} award rows have seats; task 20 needs choices"

    by_route: dict[str, int] = {}
    for entry in award:
        if entry["seats"] > 0:
            by_route[str(entry["flight_id"])] = by_route.get(str(entry["flight_id"]), 0) + 1
    assert len(by_route) >= 100, (
        f"only {len(by_route)} distinct flights have award seats; searches will "
        "mostly come back empty and the feature will read as broken")

    out = ROOT / "spec/seed_data/loyalty.yaml"
    out.write_text("# Generated by tools/make_loyalty.py -- edit there, not here.\n"
                   + yaml.safe_dump({"loyalty_members": members,
                                     "miles_transactions": transactions,
                                     "award_inventory": award},
                                    sort_keys=False, allow_unicode=True), "utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    print(f"  members       {len(members)} across {len(TIERS)} tiers")
    print(f"  transactions  {len(transactions)} ({len(transactions)/len(members):.0f} per member)")
    print(f"  award rows    {len(award)}, {bookable} with seats available")
    for tier in TIERS:
        rows = [m for m in members if m["tier"] == tier]
        span = f"{min(m['qualifying_miles'] for m in rows):,}-{max(m['qualifying_miles'] for m in rows):,}"
        print(f"    {tier:9s} {len(rows)} members, qualifying {span}")


if __name__ == "__main__":
    main()
