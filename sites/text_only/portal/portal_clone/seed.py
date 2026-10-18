import json
import os

DATA = os.path.join(os.path.dirname(__file__), "data")
TODAY = "2026-06-15"

SERVICES = [
    (1, "national-id", True),
    (2, "passport", True),
    (3, "civil-registration", True),
    (4, "land", True),
    (5, "electricity", True),
    (6, "exam-results", False),
    (7, "driving-licence", True),
    (8, "tax", True),
    (9, "pilgrimage", False),
    (10, "health", False),
    (11, "police-clearance", True),
    (12, "trade-licence", True),
    (13, "pension", True),
]

PASSWORD = "citizen1234"


def load(name, lang="en"):
    with open(os.path.join(DATA, "en", name + ".json"),
              encoding="utf-8") as f:
        rows = json.load(f)
    if lang != "en":
        path = os.path.join(DATA, lang, name + ".json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                overlay = {r["id"]: r for r in json.load(f)}
            rows = [{**r, **overlay.get(r["id"], {})} for r in rows]
    return rows


def content(lang="en"):
    with open(os.path.join(DATA, f"content_{lang}.json"),
              encoding="utf-8") as f:
        return json.load(f)


SCHEMA = """
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS citizens;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS locker_documents;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS passports;
DROP TABLE IF EXISTS licences;
DROP TABLE IF EXISTS civil_records;
DROP TABLE IF EXISTS geo_divisions;
DROP TABLE IF EXISTS geo_districts;
DROP TABLE IF EXISTS geo_upazilas;
DROP TABLE IF EXISTS land_mouzas;
DROP TABLE IF EXISTS land_khatians;
DROP TABLE IF EXISTS land_holdings;
DROP TABLE IF EXISTS land_tax_dues;
DROP TABLE IF EXISTS exam_boards;
DROP TABLE IF EXISTS exam_results;
DROP TABLE IF EXISTS tins;
DROP TABLE IF EXISTS vaccine_records;
DROP TABLE IF EXISTS meters;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS fee_schedules;
DROP TABLE IF EXISTS offices;
DROP TABLE IF EXISTS notices;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS record_overrides;

CREATE TABLE services (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, name TEXT,
    summary TEXT, description TEXT, requires_login INTEGER);
CREATE TABLE citizens (id INTEGER PRIMARY KEY, citizen_id TEXT UNIQUE,
    name TEXT, father_name TEXT, mother_name TEXT, dob TEXT,
    present_addr TEXT, perm_addr TEXT, mobile TEXT, email TEXT);
CREATE TABLE accounts (id INTEGER PRIMARY KEY, citizen_ref INTEGER,
    username TEXT UNIQUE, password TEXT, display_name TEXT);
CREATE TABLE locker_documents (id INTEGER PRIMARY KEY, account_id INTEGER,
    filename TEXT, doc_type TEXT, uploaded_date TEXT);
CREATE TABLE applications (id INTEGER PRIMARY KEY, service_id INTEGER,
    citizen_ref INTEGER, kind TEXT, ref_no TEXT, slip_no TEXT, status TEXT,
    submitted_date TEXT, detail TEXT);
CREATE TABLE passports (id INTEGER PRIMARY KEY, citizen_ref INTEGER,
    application_id TEXT, passport_no TEXT, pages INTEGER,
    validity_years INTEGER, delivery TEXT, status TEXT, applied_date TEXT);
CREATE TABLE licences (id INTEGER PRIMARY KEY, citizen_ref INTEGER,
    licence_no TEXT, reference_no TEXT, licence_class TEXT, status TEXT,
    issue_date TEXT, expiry_date TEXT);
CREATE TABLE civil_records (id INTEGER PRIMARY KEY, record_type TEXT,
    citizen_ref INTEGER, registration_no TEXT, person_name TEXT,
    father_name TEXT, mother_name TEXT, event_date TEXT,
    registered_date TEXT, place TEXT);
CREATE TABLE geo_divisions (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE geo_districts (id INTEGER PRIMARY KEY, division_id INTEGER,
    name TEXT);
CREATE TABLE geo_upazilas (id INTEGER PRIMARY KEY, district_id INTEGER,
    name TEXT);
CREATE TABLE land_mouzas (id INTEGER PRIMARY KEY, upazila_id INTEGER,
    name TEXT, jl_no TEXT);
CREATE TABLE land_khatians (id INTEGER PRIMARY KEY, mouza_id INTEGER,
    khatian_no TEXT, khatian_type TEXT, owner_name TEXT, father_name TEXT,
    plot_no TEXT, land_type TEXT, area_decimal INTEGER, share TEXT);
CREATE TABLE land_holdings (id INTEGER PRIMARY KEY, khatian_id INTEGER,
    holding_no TEXT, owner_ref INTEGER, assessed_value INTEGER);
CREATE TABLE land_tax_dues (id INTEGER PRIMARY KEY, holding_id INTEGER,
    fiscal_year TEXT, amount INTEGER, is_paid INTEGER);
CREATE TABLE exam_boards (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE exam_results (id INTEGER PRIMARY KEY, board_id INTEGER,
    exam TEXT, exam_year INTEGER, roll_no TEXT, registration_no TEXT,
    candidate_name TEXT, institution TEXT, gpa TEXT, result_status TEXT);
CREATE TABLE tins (id INTEGER PRIMARY KEY, tin_no TEXT,
    registered_name TEXT, circle TEXT, zone TEXT, is_active INTEGER);
CREATE TABLE vaccine_records (id INTEGER PRIMARY KEY, citizen_ref INTEGER,
    certificate_no TEXT, vaccine_name TEXT, doses INTEGER,
    registered_date TEXT, centre_name TEXT);
CREATE TABLE meters (id INTEGER PRIMARY KEY, account_id INTEGER,
    consumer_no TEXT, meter_no TEXT, meter_type TEXT, tariff TEXT,
    address TEXT, balance INTEGER);
CREATE TABLE bills (id INTEGER PRIMARY KEY, meter_id INTEGER, bill_no TEXT,
    period TEXT, units_kwh INTEGER, amount INTEGER, due_date TEXT,
    is_paid INTEGER);
CREATE TABLE fee_schedules (id INTEGER PRIMARY KEY, service_id INTEGER,
    category TEXT, variant TEXT, validity TEXT, delivery TEXT,
    amount INTEGER);
CREATE TABLE offices (id INTEGER PRIMARY KEY, service_id INTEGER,
    name TEXT, address TEXT);
CREATE TABLE notices (id INTEGER PRIMARY KEY, service_id INTEGER,
    ref_no TEXT, title TEXT, category TEXT, date TEXT);

CREATE TABLE submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT,
    citizen_ref INTEGER, ref_no TEXT, payload TEXT, created_date TEXT);
CREATE TABLE appointments (id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER, citizen_ref INTEGER, office TEXT, slot_date TEXT,
    slot_time TEXT, created_date TEXT);
CREATE TABLE payments (id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER, target_kind TEXT, ref TEXT, amount INTEGER,
    method TEXT, created_date TEXT);
CREATE TABLE record_overrides (id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT, field_name TEXT, record_id INTEGER, new_value TEXT,
    document TEXT, created_date TEXT);
"""


def seed(con, lang="en"):
    c = content(lang)

    def L(name):
        return load(name, lang)

    con.executescript(SCHEMA)

    for sid, slug, login in SERVICES:
        m = c[slug]
        con.execute("INSERT INTO services VALUES (?,?,?,?,?,?)",
                    (sid, slug, m["name"], m["summary"], m["description"],
                     int(login)))

    for r in L("citizens"):
        con.execute("INSERT INTO citizens VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (r["id"], r["citizen_id"], r["name"], r["father_name"],
                     r["mother_name"], r["dob"], r["present_addr"],
                     r["perm_addr"], r["mobile"], r["email"]))
    for r in L("accounts"):
        con.execute("INSERT INTO accounts VALUES (?,?,?,?,?)",
                    (r["id"], r["citizen_ref"], r["username"], PASSWORD,
                     r["display_name"]))
    for r in L("locker_documents"):
        con.execute("INSERT INTO locker_documents VALUES (?,?,?,?,?)",
                    (r["id"], r["account_id"], r["filename"], r["doc_type"],
                     r["uploaded_date"]))
    for r in L("applications"):
        con.execute("INSERT INTO applications VALUES (?,?,?,?,?,?,?,?,?)",
                    (r["id"], r["service_id"], r["citizen_ref"], r["kind"],
                     r["ref_no"], r["slip_no"], r["status"],
                     r["submitted_date"], r["detail"]))
    for r in L("passports"):
        con.execute("INSERT INTO passports VALUES (?,?,?,?,?,?,?,?,?)",
                    (r["id"], r["citizen_ref"], r["application_id"],
                     r["passport_no"], r["pages"], r["validity_years"],
                     r["delivery"], r["status"], r["applied_date"]))
    for r in L("licences"):
        con.execute("INSERT INTO licences VALUES (?,?,?,?,?,?,?,?)",
                    (r["id"], r["citizen_ref"], r["licence_no"],
                     r["reference_no"], r["licence_class"], r["status"],
                     r["issue_date"], r["expiry_date"]))
    for r in L("civil_records"):
        con.execute("INSERT INTO civil_records VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (r["id"], r["record_type"], r["citizen_ref"],
                     r["registration_no"], r["person_name"], r["father_name"],
                     r["mother_name"], r["event_date"], r["registered_date"],
                     r["place"]))
    for r in L("geo_divisions"):
        con.execute("INSERT INTO geo_divisions VALUES (?,?)",
                    (r["id"], r["name"]))
    for r in L("geo_districts"):
        con.execute("INSERT INTO geo_districts VALUES (?,?,?)",
                    (r["id"], r["division_id"], r["name"]))
    for r in L("geo_upazilas"):
        con.execute("INSERT INTO geo_upazilas VALUES (?,?,?)",
                    (r["id"], r["district_id"], r["name"]))
    for r in L("land_mouzas"):
        con.execute("INSERT INTO land_mouzas VALUES (?,?,?,?)",
                    (r["id"], r["upazila_id"], r["name"], r["jl_no"]))
    for r in L("land_khatians"):
        con.execute("INSERT INTO land_khatians VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (r["id"], r["mouza_id"], r["khatian_no"],
                     r["khatian_type"], r["owner_name"], r["father_name"],
                     r["plot_no"], r["land_type"], r["area_decimal"],
                     r["share"]))
    for r in L("land_holdings"):
        con.execute("INSERT INTO land_holdings VALUES (?,?,?,?,?)",
                    (r["id"], r["khatian_id"], r["holding_no"],
                     r["owner_ref"], r["assessed_value"]))
    for r in L("land_tax_dues"):
        con.execute("INSERT INTO land_tax_dues VALUES (?,?,?,?,?)",
                    (r["id"], r["holding_id"], r["fiscal_year"], r["amount"],
                     r["is_paid"]))
    for r in L("exam_boards"):
        con.execute("INSERT INTO exam_boards VALUES (?,?)",
                    (r["id"], r["name"]))
    for r in L("exam_results"):
        con.execute("INSERT INTO exam_results VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (r["id"], r["board_id"], r["exam"], r["exam_year"],
                     r["roll_no"], r["registration_no"], r["candidate_name"],
                     r["institution"], r["gpa"], r["result_status"]))
    for r in L("tins"):
        con.execute("INSERT INTO tins VALUES (?,?,?,?,?,?)",
                    (r["id"], r["tin_no"], r["registered_name"], r["circle"],
                     r["zone"], r["is_active"]))
    for r in L("vaccine_records"):
        con.execute("INSERT INTO vaccine_records VALUES (?,?,?,?,?,?,?)",
                    (r["id"], r["citizen_ref"], r["certificate_no"],
                     r["vaccine_name"], r["doses"], r["registered_date"],
                     r["centre_name"]))
    for r in L("meters"):
        con.execute("INSERT INTO meters VALUES (?,?,?,?,?,?,?,?)",
                    (r["id"], r["account_id"], r["consumer_no"],
                     r["meter_no"], r["meter_type"], r["tariff"],
                     r["address"], r["balance"]))
    for r in L("bills"):
        con.execute("INSERT INTO bills VALUES (?,?,?,?,?,?,?,?)",
                    (r["id"], r["meter_id"], r["bill_no"], r["period"],
                     r["units_kwh"], r["amount"], r["due_date"],
                     r["is_paid"]))
    for r in L("fee_schedules"):
        con.execute("INSERT INTO fee_schedules VALUES (?,?,?,?,?,?,?)",
                    (r["id"], r["service_id"], r["category"], r["variant"],
                     r["validity"], r["delivery"], r["amount"]))
    for r in L("offices"):
        con.execute("INSERT INTO offices VALUES (?,?,?,?)",
                    (r["id"], r.get("service_id"), r["name"], r["address"]))
    for r in L("notices"):
        con.execute("INSERT INTO notices VALUES (?,?,?,?,?,?)",
                    (r["id"], r["service_id"], r["ref_no"], r["title"],
                     r["category"], r["issued_date"]))

    con.commit()
