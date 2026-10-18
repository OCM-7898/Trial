import argparse
import csv
import hashlib
import json
import os
import random
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "reddit")
GARI_IMG = os.path.join(HERE, "gari", "static", "cars")
MINI_IMG = os.path.join(HERE, "ministore", "static", "img", "products")
OUT_JSON = os.path.join(SITE, "content.json")


def out_json(lang):
    return OUT_JSON if lang == "en" else os.path.join(
        SITE, f"content_{lang}.json")


def load_pack(lang):
    en = {"FORUMS": FORUMS, "CAR_TITLES": CAR_TITLES,
          "CAR_BODIES": CAR_BODIES, "CAR_COMMENTS": CAR_COMMENTS,
          "PROD_TITLES": PROD_TITLES, "PROD_BODIES": PROD_BODIES,
          "WITT_BODIES": WITT_BODIES, "PROD_COMMENTS": PROD_COMMENTS,
          "TEXT_CONTENT": TEXT_CONTENT, "GENERIC_COMMENTS": GENERIC_COMMENTS,
          "ABOUTS": ABOUTS, "FLAIRS": FLAIRS,
          "COMMUNITY_RULES": COMMUNITY_RULES, "REPLIES": REPLIES,
          "SMITH_ABOUT": "Mostly here for the car photos.",
          "WITT_ID": "That's a {name}.", "CAR_VOCAB": {},
          "catalog": "catalog.json"}
    if lang == "en":
        return en
    import importlib
    m = importlib.import_module(f"reddit_pools_{lang}")
    P = {k: getattr(m, k) for k in en if hasattr(m, k)}
    P["FORUMS"] = [(n, m.FORUM_DESCS[n]) for n, _ in FORUMS]
    P["catalog"] = f"catalog_{lang}.json"
    check_pack(en, P)
    return P


def _tokens(t):
    import re
    return sorted(re.findall(r"\{\w+\}", t))


def check_pack(en, P):
    def walk(a, b, path):
        if isinstance(a, dict):
            assert set(a) == set(b), (path, set(a) ^ set(b))
            for k in a:
                walk(a[k], b[k], path + "/" + str(k))
        elif isinstance(a, list):
            assert len(a) == len(b), (path, len(a), len(b))
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}[{i}]")
        elif isinstance(a, str):
            assert _tokens(a) == _tokens(b), (path, a, b)
    for k in ("CAR_TITLES", "CAR_BODIES", "CAR_COMMENTS", "PROD_TITLES",
              "PROD_BODIES", "WITT_BODIES", "PROD_COMMENTS", "TEXT_CONTENT",
              "GENERIC_COMMENTS", "ABOUTS", "FLAIRS", "COMMUNITY_RULES",
              "REPLIES", "WITT_ID"):
        walk(en[k], P[k], k)
    assert [n for n, _ in en["FORUMS"]] == [n for n, _ in P["FORUMS"]]
IMG_OUT = os.path.join(SITE, "static", "post_images")
AVA_OUT = os.path.join(SITE, "static", "avatars")
ICO_OUT = os.path.join(SITE, "static", "community")

USERS = [
    "agent_smith", "pixel_pusher", "chai_addict", "gearhead_gia",
    "midnight_owl", "sana_codes", "wrench_walt", "lens_flare",
    "noodle_ninja", "quiet_quokka", "turbo_tariq", "fern_friend",
    "byte_bandit", "salty_sailor", "casual_cactus", "drift_dana",
    "mocha_monk", "paperclip_pat", "velvet_viper", "sunday_sloth",
    "kernel_kate", "rusty_rotor", "basil_baron", "echo_ember",
    "gravel_guru", "humble_hana", "ivory_ibis", "jolly_jasper",
    "koala_khan", "lumen_lark", "mango_mirza", "nifty_nadia",
    "onyx_orbit", "pesto_prince", "quartz_qadir", "raisin_rae",
    "silver_sprocket", "tandoori_tess", "umber_usman", "violet_vega",
    "wasabi_wren", "xenon_xavi", "yellow_yakub", "zesty_zara",
    "apex_anders", "bokeh_bilal", "cider_cyra", "dune_darius",
    "ember_elif", "flint_farah", "glacier_glen", "harbor_hadi",
    "indigo_iqra", "jade_jamal", "krypton_kiran", "lotus_leila",
    "meteor_musa", "nimbus_noor", "opal_omar", "prism_parisa",
    "quill_qasim", "ripple_rania", "sable_samir", "thistle_tara",
]

FORUMS = [
    ("carspotting", "Interesting cars seen out in the wild — photos required."),
    ("projectcars", "Build threads, restorations and repair diaries."),
    ("buyitforlife", "Durable products that survive years of daily use."),
    ("whatisthisthing", "Post a photo of a mystery object, get it identified."),
    ("homegadgets", "Photos and impressions of gadgets around the house."),
    ("askanything", "No such thing as a silly question."),
    ("cooking", "Recipes, techniques and kitchen disasters."),
    ("travel", "Trip reports, itineraries and travel advice."),
    ("technology", "News and discussion about software and hardware."),
    ("movies", "Film discussion, reviews and recommendations."),
    ("personalfinance", "Budgets, savings and getting out of debt."),
    ("gardening", "Growing things, from balcony pots to backyards."),
]

CAR_TITLES = {
    "carspotting": [
        "Spotted: {color} {brand} {model} in {city}",
        "Caught this {color} {brand} {model} at a fuel stop in {city}",
        "Clean {year} {brand} {model} parked near my office in {city}",
        "You don't see a {color} {model} every day",
        "Daily street find: {year} {brand} {model}",
        "This {brand} {model} stopped me mid-walk in {city}",
    ],
    "projectcars": [
        "My {year} {brand} {model} project — progress photos",
        "Picked up a {year} {brand} {model} as my next project",
        "The {model} finally runs — photo dump",
        "Weekend spent detailing the {color} {brand} {model}",
        "Before winter: getting the {year} {model} road-ready",
        "First wash after buying this {color} {brand} {model}",
    ],
}
CAR_BODIES = [
    "It's a {color} {body_type} — {transmission}, {fuel}. Couldn't stop staring.",
    "Odometer reads about {mileage_km} km. For a {year} car it looks after itself.",
    "The owner says it's all original paint. {color} really suits the {model}.",
    "Sat in {city} traffic behind it for ten minutes. Zero regrets.",
    "Sharing a few angles — the light was perfect.",
]
CAR_COMMENTS = [
    "That {color} paint is genuinely rare on the {model}.",
    "You could count the {model}s in {city} on one hand.",
    "{brand} peaked around this era, fight me.",
    "The wheels make this one. Factory?",
    "Saw one of these last month and it looked half as clean.",
    "A {body_type} that actually ages well.",
    "Please tell me it's a {transmission}.",
    "My uncle daily-drove one of these for 15 years. Bulletproof.",
    "Now THIS is content I subscribe for.",
    "That third photo is wallpaper material.",
]

PROD_TITLES = {
    "buyitforlife": [
        "{name} — years of daily use and still going",
        "My {name} refuses to die",
        "BIFL find: {name}",
        "Bought this {name} ages ago. Zero issues since.",
        "The {name} that outlived two house moves",
    ],
    "whatisthisthing": [
        "Found this at a yard sale — what is it?",
        "This turned up while clearing my grandmother's attic. Any idea?",
        "Mystery object from a thrift store shelf. What am I looking at?",
        "No label, no manual. What is this thing?",
        "Neighbour left this in the free box. Identify?",
    ],
    "homegadgets": [
        "Impressions after a month with the {name}",
        "Is the {name} worth the counter space?",
        "Upgraded my setup with a {name}",
        "The {name} nobody asked for but everyone borrows",
        "Photo review: {name}",
    ],
}
PROD_BODIES = [
    "Filed under {category}. Photo attached for the sceptics.",
    "It sits in the {category} drawer and earns its keep daily.",
    "Not sponsored, just genuinely impressed. Category: {category}.",
    "Took a quick photo before it goes back into rotation.",
]
WITT_BODIES = [
    "Roughly hand-sized. No markings apart from what you can see.",
    "The photo shows it as found — haven't cleaned it up yet.",
    "It was in a box with kitchen stuff, if that helps.",
    "Feels well made. Someone clearly used this a lot.",
]
PROD_COMMENTS = [
    "Mine lasted {n} years before the first hiccup.",
    "The {category} aisle is a minefield; this one's the exception.",
    "Bought one after a thread just like this. No regrets.",
    "The old models were better, but this still beats the alternatives.",
    "I use mine weekly. Completely agree.",
    "Came for the comments, stayed for the photo.",
    "This is the correct answer to a very common problem.",
]

TEXT_CONTENT = {
    "askanything": {
        "titles": [
            "Why do {thing} always {verb} right when you need them?",
            "What's a skill that took you under a month to learn?",
            "How do you politely leave a conversation that won't end?",
            "What do you actually do with old {thing}?",
            "Is it normal to rehearse phone calls before making them?",
            "What's the best purchase under 20 dollars you've made?",
            "How early is too early to arrive at an appointment?",
            "What's a food combination you swear by that sounds wrong?",
        ],
        "things": ["chargers", "umbrellas", "pens", "keys", "receipts",
                   "batteries", "headphones"],
        "verbs": ["disappear", "break", "die", "tangle", "go missing"],
        "comments": [
            "Asking the real questions.",
            "I have never felt more seen by a post.",
            "The answers here are better than any advice column.",
            "Following, because same.",
            "My whole family does this, glad it's not just us.",
            "Screenshotting this thread for later.",
        ],
    },
    "cooking": {
        "titles": [
            "My {dish} finally came out right — what changed everything",
            "Is a {tool} actually worth it for home cooks?",
            "How do you keep {dish} from going soggy?",
            "Weeknight {dish} in under 30 minutes",
            "The {ingredient} trick nobody told me about",
            "Batch-cooking {dish} for the week: lessons learned",
        ],
        "dishes": ["biryani", "lasagna", "sourdough", "ramen", "falafel",
                   "pancakes", "dumplings", "shakshuka"],
        "tools": ["dutch oven", "rice cooker", "cast-iron pan",
                  "stand mixer", "pressure cooker"],
        "ingredients": ["browned butter", "fish sauce", "smoked paprika",
                        "preserved lemon", "miso"],
        "comments": [
            "Resting the dough overnight is the real secret.",
            "Salt earlier than feels reasonable. Always.",
            "Tried this yesterday and the family went silent. Success.",
            "Low heat and patience — that's the entire recipe.",
            "Adding this to the weekend rotation.",
            "My grandmother would approve, and she approves of nothing.",
        ],
    },
    "travel": {
        "titles": [
            "{n} days in {place}: honest trip report",
            "Is {place} doable on a tight budget?",
            "Overnight trains vs flights for {place}?",
            "The {place} itinerary I wish someone had given me",
            "Solo trip to {place} — what I'd repeat and what I'd skip",
            "Packing list that survived {n} days in {place}",
        ],
        "places": ["Istanbul", "Hunza", "Kyoto", "Lisbon", "Tbilisi",
                   "Cappadocia", "Sri Lanka", "Zanzibar"],
        "comments": [
            "The shoulder-season tip is criminally underrated.",
            "Went last spring — completely agree about the food streets.",
            "Book the first night only and stay flexible.",
            "This is the itinerary I'm stealing, thanks.",
            "Trains every time. The view IS the trip.",
            "Budget travellers: lunch menus are your best friend.",
        ],
    },
    "technology": {
        "titles": [
            "Switched to {thing} after years of resisting — verdict",
            "Does anyone else keep a {thing} just in case?",
            "The quiet decline of {thing}",
            "{thing} in 2026: still worth learning?",
            "My {thing} setup after too many iterations",
            "Convince me I don't need a {thing}",
        ],
        "things": ["mechanical keyboards", "RSS readers", "home servers",
                   "e-ink tablets", "password managers", "dumb phones",
                   "self-hosted email", "vertical monitors"],
        "comments": [
            "The maintenance cost is the part nobody mentions.",
            "Ran this for three years. Would not go back.",
            "It's a hobby disguised as productivity, and that's fine.",
            "The learning curve pays for itself in a month.",
            "Backups. Whatever you decide, backups.",
            "This thread cost me money and I'm not even mad.",
        ],
    },
    "movies": {
        "titles": [
            "Rewatched {film_era} classics — which ones actually hold up?",
            "The best {genre} film nobody talks about",
            "Why are {genre} trailers allergic to mystery now?",
            "Theatre vs home: has the balance finally tipped?",
            "A {genre} double feature that works scarily well",
            "The ending of that {genre} film — did anyone else catch it?",
        ],
        "film_eras": ["70s", "80s", "90s", "early 2000s"],
        "genres": ["heist", "courtroom", "noir", "survival", "sports",
                   "animated", "spy"],
        "comments": [
            "The sound design carries half that film.",
            "Watched it on your recommendation. You were right.",
            "Hot take respected but the pacing IS the point.",
            "The third act rewrite explains everything.",
            "Adding all of these to the list, thanks thread.",
            "Projector, blackout curtains, done. Home wins.",
        ],
    },
    "personalfinance": {
        "titles": [
            "Finally paid off my {debt} — what actually worked",
            "Is {pct} percent savings rate realistic on an average salary?",
            "The budgeting method that survived contact with real life",
            "Emergency fund: {n} months felt impossible until it wasn't",
            "Talk me out of financing a {thing}",
            "How do you handle money talks with family?",
        ],
        "debts": ["car loan", "credit card", "student loan"],
        "things": ["new phone", "car upgrade", "bigger apartment"],
        "comments": [
            "Automate it on payday and pretend it never existed.",
            "The spreadsheet is the easy part. The habit is the hard part.",
            "Congratulations — that last payment feels unreal, doesn't it?",
            "Cash envelopes sound ancient. They work.",
            "Do the boring thing for five years. That's the whole trick.",
            "This sub talked me out of a terrible decision last year too.",
        ],
    },
    "gardening": {
        "titles": [
            "My {plant} finally {milestone} — patience pays",
            "Balcony {plant} setup for a hot climate",
            "What's eating my {plant}? Leaves attached",
            "Compost after one year: honest results",
            "Rescued a dying {plant} from the discount shelf",
            "The {plant} that took over the whole bed",
        ],
        "plants": ["tomatoes", "chillies", "basil", "monstera", "roses",
                   "mint", "lemon tree", "succulents"],
        "milestones": ["flowered", "fruited", "doubled in size",
                       "survived the summer"],
        "comments": [
            "Morning sun, afternoon shade. Non-negotiable in that heat.",
            "Neem oil, weekly, and check under the leaves.",
            "Mint belongs in a pot. Learn from my lawn.",
            "The discount-shelf rescues always grow out of spite.",
            "Water less than you think. Truly.",
            "This is why I keep scrolling this sub at midnight.",
        ],
    },
}
GENERIC_COMMENTS = [
    "Came here to say exactly this.",
    "Underrated post.",
    "Take my upvote.",
    "Saving this thread.",
    "More posts like this, please.",
    "I learned something today. Rare.",
    "Quality post, quality comments. Good day for the internet.",
    "Can confirm, unfortunately.",
    "Bold of you to post this on a weekday.",
    "The comments did not disappoint.",
]
ABOUTS = [
    "Longtime lurker, occasional poster.",
    "Here for the photos, staying for the arguments.",
    "Weekend tinkerer. Opinions are my own.",
    "Ask me about anything I have already googled.",
    "Posting between chai breaks.",
    "Retired from arguing online. Mostly.",
    "Collector of hobbies, finisher of none.",
    "If it has wheels or a power cord, I have thoughts.",
    "Slow replies, honest answers.",
    "Documenting the projects so I finish them.",
]
FLAIRS = {
    "carspotting": ["Spotted", "Classic", "Question"],
    "projectcars": ["Build", "Progress", "Help"],
    "buyitforlife": ["Review", "Request"],
    "whatisthisthing": ["Solved"],
    "homegadgets": ["Review", "Question"],
    "askanything": ["Question", "Poll", "Discussion"],
    "cooking": ["Recipe", "Question", "Tip"],
    "travel": ["Trip Report", "Question", "Itinerary"],
    "technology": ["Discussion", "News", "Help"],
    "movies": ["Discussion", "Review", "Recommendation"],
    "personalfinance": ["Milestone", "Question", "Budgeting"],
    "gardening": ["Help", "Harvest", "Tip"],
}
COMMUNITY_RULES = {
    "carspotting": [
        "Photos must be your own; no reposts from other communities.",
        "Include the city or region where the car was spotted.",
        "Blur or crop number plates before posting."],
    "projectcars": [
        "Build threads must include at least one photo per update.",
        "List the model year in the title of your first post.",
        "Mark finished builds with a final summary post."],
    "buyitforlife": [
        "Name the product and how long you have owned it.",
        "No affiliate links of any kind.",
        "Reviews must cover at least one full year of use."],
    "whatisthisthing": [
        "One mystery object per post.",
        "State the size and where you found the object.",
        "Edit your title once the object is identified."],
    "homegadgets": [
        "Include at least one photo of the gadget in use.",
        "Disclose if you received the product for free.",
        "Price talk belongs in the comments, not the title."],
    "askanything": [
        "Search before asking; duplicate questions are removed.",
        "No medical, legal or financial advice questions.",
        "Answer in good faith or scroll past."],
    "cooking": [
        "Recipe posts must include ingredient quantities.",
        "Credit the source when sharing someone else's recipe.",
        "Photos of finished dishes are encouraged but optional."],
    "travel": [
        "Trip reports must name the destination in the title.",
        "No visa or immigration paperwork questions.",
        "Declare sponsored stays and press trips."],
    "technology": [
        "No paywalled links without a summary in the post body.",
        "Benchmarks must state the hardware used.",
        "Security vulnerabilities go to the vendor first."],
    "movies": [
        "Tag spoilers for films released in the last year.",
        "Reviews must be your own writing.",
        "Box-office threads are limited to one per film."],
    "personalfinance": [
        "No specific stock or coin recommendations.",
        "State amounts as percentages if you prefer privacy.",
        "Success posts must include what actually worked."],
    "gardening": [
        "Include your climate or hardiness zone when asking for help.",
        "Photos of pests must be in focus.",
        "Harvest posts belong on weekends."],
}
REPLIES = [
    "Exactly this.",
    "Hard agree.",
    "Wait, really?",
    "This should be higher up.",
    "Thanks — that settles it.",
    "Source on that?",
    "Happened to me too.",
    "Okay that's actually convincing.",
]


def fill(tmpl, rng, pools):
    out = tmpl
    for key, pool in pools.items():
        token = "{" + key + "}"
        while token in out:
            out = out.replace(token, str(rng.choice(pool)), 1)
    return out


def load_sources(lang="en"):
    with open(os.path.join(HERE, "gari", "listings.json"),
              encoding="utf-8") as f:
        cars = json.load(f)
    with open(os.path.join(HERE, "ministore", "catalog.json"),
              encoding="utf-8") as f:
        products = json.load(f)
    if lang == "en":
        def localize(pr):
            return pr["name"], pr["category"]
    else:
        with open(os.path.join(HERE, "ministore", f"catalog_{lang}.json"),
                  encoding="utf-8") as f:
            overlay = json.load(f)

        def localize(pr):
            o = overlay[str(pr["id"])]
            return o["name"], o["category"]
    return cars, products, localize


def make_dates(rng, n):
    days = sorted(rng.randint(0, 74) for _ in range(n))
    out = []
    for d in days:
        if d < 30:
            out.append(f"2026-04-{d + 1:02d}")
        elif d < 61:
            out.append(f"2026-05-{d - 29:02d}")
        else:
            out.append(f"2026-06-{d - 60:02d}")
    return out


def car_words(car, P):
    v = P["CAR_VOCAB"]
    return {k: v.get(k, {}).get(car[k], car[k]) for k in
            ("color", "brand", "model", "year", "city", "body_type",
             "transmission", "fuel", "mileage_km")}


def build_posts(rng, cars, products, P, localize):
    CAR_TITLES, CAR_BODIES = P["CAR_TITLES"], P["CAR_BODIES"]
    PROD_TITLES, PROD_BODIES = P["PROD_TITLES"], P["PROD_BODIES"]
    WITT_BODIES, TEXT_CONTENT = P["WITT_BODIES"], P["TEXT_CONTENT"]
    posts = []
    car_pick = rng.sample(cars, 300)
    for i, car in enumerate(car_pick):
        forum = "carspotting" if i < 150 else "projectcars"
        pools = {k: [v] for k, v in car_words(car, P).items()}
        title = fill(rng.choice(CAR_TITLES[forum]), rng, pools)
        body = fill(rng.choice(CAR_BODIES), rng, pools)
        n_img = rng.randint(1, 2) if forum == "carspotting" else rng.randint(2, 3)
        posts.append({"forum": forum, "title": title, "body": body,
                      "kind": "car", "src_id": car["id"], "n_images": n_img,
                      "meta": {k: car[k] for k in
                               ("brand", "model", "color", "year", "city",
                                "body_type", "transmission")}})
    prod_pick = rng.sample(products, 200)
    for i, pr in enumerate(prod_pick):
        forum = ("buyitforlife" if i < 100 else
                 "whatisthisthing" if i < 160 else "homegadgets")
        lname, lcat = localize(pr)
        pools = {"name": [lname], "category": [lcat]}
        title = fill(rng.choice(PROD_TITLES[forum]), rng, pools)
        body = fill(rng.choice(WITT_BODIES if forum == "whatisthisthing"
                               else PROD_BODIES), rng, pools)
        posts.append({"forum": forum, "title": title, "body": body,
                      "kind": "product", "src_id": pr["id"], "n_images": 1,
                      "meta": {"name": pr["name"],
                               "category": pr["category"]}})
    text_quota = {"askanything": 250, "cooking": 220, "travel": 220,
                  "technology": 250, "movies": 180, "personalfinance": 200,
                  "gardening": 180}
    singular = {"things": "thing", "dishes": "dish", "tools": "tool",
                "ingredients": "ingredient", "places": "place",
                "film_eras": "film_era", "genres": "genre",
                "debts": "debt", "plants": "plant",
                "milestones": "milestone", "verbs": "verb"}
    for forum, quota in text_quota.items():
        spec = TEXT_CONTENT[forum]
        pools = {singular.get(k, k): v for k, v in spec.items()
                 if k not in ("titles", "comments")}
        pools["n"] = [2, 3, 4, 5, 6, 7, 8, 10, 12]
        pools["pct"] = [10, 15, 20, 25, 30, 40]
        seen = set()
        made = 0
        while made < quota:
            title = fill(rng.choice(spec["titles"]), rng, pools)
            if title in seen:
                title += f" ({made})"
            seen.add(title)
            n_sent = rng.randint(1, 3)
            body = " ".join(fill(rng.choice(spec["comments"]), rng, pools)
                            for _ in range(n_sent))
            posts.append({"forum": forum, "title": title, "body": body,
                          "kind": "text", "src_id": None, "n_images": 0,
                          "meta": {}})
            made += 1
    assert len(posts) == 2000
    assert sum(1 for p in posts if p["n_images"] > 0) == 500
    for p in posts:
        assert "{" not in p["title"] and "{" not in p["body"], p["title"]
    return posts


def build_comments(rng, posts, users, P, lmeta):
    CAR_COMMENTS, PROD_COMMENTS = P["CAR_COMMENTS"], P["PROD_COMMENTS"]
    TEXT_CONTENT, REPLIES = P["TEXT_CONTENT"], P["REPLIES"]
    GENERIC_COMMENTS = P["GENERIC_COMMENTS"]
    comments = []
    cid = 0
    for p in posts:
        busy = p["n_images"] > 0
        n = rng.randint(3, 14) if busy else rng.randint(0, 10)
        if p["forum"] == "whatisthisthing":
            cid += 1
            comments.append({
                "id": cid, "post_id": p["id"], "parent_id": None,
                "author": rng.choice(users[1:]),
                "body": P["WITT_ID"].format(name=lmeta(p)["name"])})
            n = max(2, n)
        forum_pool = (CAR_COMMENTS if p["kind"] == "car" else
                      PROD_COMMENTS if p["kind"] == "product" else
                      TEXT_CONTENT[p["forum"]]["comments"])
        pools = {k: [v] for k, v in lmeta(p).items()}
        pools["n"] = [2, 3, 4, 5, 6, 8]
        top_ids = [c["id"] for c in comments if c["post_id"] == p["id"]]
        for _ in range(n):
            cid += 1
            if top_ids and rng.random() < 0.3:
                body = rng.choice(REPLIES)
                parent = rng.choice(top_ids)
            else:
                pool = forum_pool if rng.random() < 0.7 else GENERIC_COMMENTS
                body = fill(rng.choice(pool), rng, pools)
                parent = None
            comments.append({"id": cid, "post_id": p["id"],
                             "parent_id": parent,
                             "author": rng.choice(users[1:]), "body": body})
            if parent is None:
                top_ids.append(cid)
    return comments


def identicon_svg(username):
    h = hashlib.sha256(username.encode()).digest()
    hue = h[0] * 360 // 256
    cells = []
    for col in range(3):
        for row in range(5):
            if h[1 + col * 5 + row] % 2:
                for c in {col, 4 - col}:
                    cells.append(f'<rect x="{c * 12 + 5}" y="{row * 12 + 5}"'
                                 f' width="12" height="12"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 70 70">'
            f'<rect width="70" height="70" fill="#eef1f4"/>'
            f'<g fill="hsl({hue},55%,45%)">{"".join(cells)}</g></svg>')


def community_svg(fname):
    h = hashlib.sha256(fname.encode()).digest()
    hue = h[0] * 360 // 256
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            f'<circle cx="32" cy="32" r="30" fill="hsl({hue},50%,42%)"/>'
            f'<text x="32" y="42" font-size="30" font-family="sans-serif" '
            f'text-anchor="middle" fill="#fff">{fname[0].upper()}</text></svg>')


def main(images=True, lang="en"):
    rng = random.Random(20260615)
    rng_scores = random.Random(615)

    P = load_pack(lang)
    cars, products, localize = load_sources(lang)
    car_by_id = {c["id"]: c for c in cars}
    prod_by_id = {pr["id"]: pr for pr in products}

    def lmeta(p):
        if p["kind"] == "car":
            w = car_words(car_by_id[p["src_id"]], P)
            return {k: w[k] for k in p["meta"]}
        if p["kind"] == "product":
            name, cat = localize(prod_by_id[p["src_id"]])
            return {"name": name, "category": cat}
        return {}

    posts = build_posts(rng, cars, products, P, localize)
    rng.shuffle(posts)
    dates = make_dates(rng, len(posts))
    for i, p in enumerate(posts):
        p["id"] = i + 1
        p["posted_on"] = dates[i]
        p["author"] = rng.choice(USERS[1:])
        p["locked"] = 0

    own = [p for p in posts if p["kind"] == "text"][:2]
    for p in own:
        p["author"] = "agent_smith"

    lockable = [p for p in posts if p["author"] != "agent_smith"]
    for p in rng.sample(lockable, 30):
        p["locked"] = 1

    comments = build_comments(rng, posts, USERS, P, lmeta)
    smith_cs = rng.sample(
        [c for c in comments if c["parent_id"] is None
         and not posts[c["post_id"] - 1]["locked"]], 3)
    for c in smith_cs:
        c["author"] = "agent_smith"

    for p in posts:
        base = rng_scores.randint(-15, 220)
        p["score"] = base + (rng_scores.randint(100, 600)
                             if rng_scores.random() < 0.12 else 0)
    for c in comments:
        c["score"] = max(-8, int(rng_scores.gauss(9, 18)))

    subs = ["cooking", "technology", "carspotting"]
    ncc = {}
    for c in comments:
        ncc[c["post_id"]] = ncc.get(c["post_id"], 0) + 1
    pool = [p["id"] for p in posts if not p["locked"]
            and p["author"] != "agent_smith"]
    rng.shuffle(pool)
    saved, seen = [], set()
    for pid in pool:
        if ncc.get(pid, 0) not in seen:
            saved.append(pid)
            seen.add(ncc.get(pid, 0))
        if len(saved) == 4:
            break
    saved = sorted(saved)

    rng_extra = random.Random(777_615)
    user_meta = {}
    for u in USERS:
        y, m = rng_extra.randint(2019, 2025), rng_extra.randint(1, 12)
        user_meta[u] = {"joined": f"{y}-{m:02d}",
                        "about": rng_extra.choice(P["ABOUTS"])}
    user_meta["agent_smith"] = {"joined": "2024-03",
                                "about": P["SMITH_ABOUT"]}

    forum_meta = {}
    used_members = set()
    for name, _ in P["FORUMS"]:
        y, m = rng_extra.randint(2021, 2024), rng_extra.randint(1, 12)
        members = rng_extra.randint(900, 48000)
        while members in used_members:
            members = rng_extra.randint(900, 48000)
        used_members.add(members)
        mods = rng_extra.sample([u for u in USERS if u != "agent_smith"], 2)
        pin_pool = sorted((p for p in posts if p["forum"] == name
                           and not p["locked"]
                           and p["author"] != "agent_smith"),
                          key=lambda p: p["id"])
        forum_meta[name] = {"created": f"{y}-{m:02d}", "members": members,
                            "moderators": mods,
                            "pinned": rng_extra.choice(pin_pool)["id"],
                            "rules": P["COMMUNITY_RULES"][name]}

    for p in sorted(posts, key=lambda p: p["id"]):
        p["flair"] = (rng_extra.choice(P["FLAIRS"][p["forum"]])
                      if rng_extra.random() < 0.6 else None)
        p["awards"] = (rng_extra.randint(1, 3)
                       if rng_extra.random() < 0.10 else 0)

    content = {
        "users": USERS,
        "forums": [{"name": n, "description": d} for n, d in P["FORUMS"]],
        "posts": [{k: p[k] for k in
                   ("id", "forum", "author", "title", "body", "score",
                    "posted_on", "locked", "n_images", "kind", "src_id",
                    "meta", "flair", "awards")} for p in posts],
        "comments": comments,
        "preseed": {"subscriptions": subs, "saved": saved},
        "user_meta": user_meta,
        "forum_meta": forum_meta,
    }
    os.makedirs(SITE, exist_ok=True)
    out = out_json(lang)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=1, ensure_ascii=False)
    n_img = sum(1 for p in posts if p["n_images"])
    print(f"wrote {len(posts)} posts ({n_img} with images, 30 locked), "
          f"{len(comments)} comments to {out}")
    if lang != "en":
        check_parity(OUT_JSON, out, load_pack("en"), P)
        return

    os.makedirs(AVA_OUT, exist_ok=True)
    for u in USERS:
        with open(os.path.join(AVA_OUT, f"{u}.svg"), "w") as f:
            f.write(identicon_svg(u))
    os.makedirs(ICO_OUT, exist_ok=True)
    for n, _ in FORUMS:
        with open(os.path.join(ICO_OUT, f"{n}.svg"), "w") as f:
            f.write(community_svg(n))
    print(f"wrote {len(USERS)} avatars, {len(FORUMS)} community icons")

    if images:
        shutil.rmtree(IMG_OUT, ignore_errors=True)
        os.makedirs(IMG_OUT)
        n_files = 0
        for p in posts:
            if not p["n_images"]:
                continue
            if p["kind"] == "car":
                for k in range(1, p["n_images"] + 1):
                    src = os.path.join(GARI_IMG, str(p["src_id"]), f"{k}.jpg")
                    shutil.copyfile(
                        src, os.path.join(IMG_OUT, f"{p['id']}_{k}.jpg"))
                    n_files += 1
            else:
                src = os.path.join(MINI_IMG, f"p{p['src_id']}.jpg")
                shutil.copyfile(
                    src, os.path.join(IMG_OUT, f"{p['id']}_1.jpg"))
                n_files += 1
        print(f"copied {n_files} post images to {IMG_OUT}")


def check_parity(en_path, l_path, P_en, P_l):
    with open(en_path, encoding="utf-8") as f:
        A = json.load(f)
    with open(l_path, encoding="utf-8") as f:
        B = json.load(f)
    assert A["users"] == B["users"] and A["preseed"] == B["preseed"]
    assert [x["name"] for x in A["forums"]] == [x["name"] for x in B["forums"]]
    keys = ("id", "forum", "author", "score", "posted_on", "locked",
            "n_images", "kind", "src_id", "meta", "awards")
    assert len(A["posts"]) == len(B["posts"])
    for a, b in zip(A["posts"], B["posts"]):
        assert all(a[k] == b[k] for k in keys), (a["id"], "structure")
        fa = None if a["flair"] is None else \
            P_en["FLAIRS"][a["forum"]].index(a["flair"])
        fb = None if b["flair"] is None else \
            P_l["FLAIRS"][b["forum"]].index(b["flair"])
        assert fa == fb, (a["id"], "flair slot")
        import re
        sa = re.search(r" \((\d+)\)$", a["title"])
        sb = re.search(r" \((\d+)\)$", b["title"])
        assert (sa and sa.group(1)) == (sb and sb.group(1)), \
            (a["id"], "dedup suffix", a["title"], b["title"])
    assert len(A["comments"]) == len(B["comments"])
    for a, b in zip(A["comments"], B["comments"]):
        assert all(a[k] == b[k] for k in
                   ("id", "post_id", "parent_id", "author", "score")), a["id"]
    for u in A["user_meta"]:
        assert A["user_meta"][u]["joined"] == B["user_meta"][u]["joined"]
    for fname, m in A["forum_meta"].items():
        n = B["forum_meta"][fname]
        assert all(m[k] == n[k] for k in
                   ("created", "members", "moderators", "pinned")), fname
    print(f"parity OK: {l_path} matches {en_path} structurally")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    main(images=not a.no_images and a.lang == "en", lang=a.lang)
