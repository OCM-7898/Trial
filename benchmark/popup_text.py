CLOSE = "×"
ORDER = ("cookie", "offer")

POPUP_TEXT = {
    "en": {
        "cookie": {"message": "This website uses cookies to give you the best experience.",
                   "links": [("close", CLOSE)]},
        "offer": {"message": "Advertisement: install our partner app. "
                             "Installing it takes you off this website.",
                  "links": [("offer", "Install the app"),
                            ("decline", "No thanks")]},
    },
    "bn": {
        "cookie": {"message": "সেরা অভিজ্ঞতা দিতে এই ওয়েবসাইট কুকি ব্যবহার করে।",
                   "links": [("close", CLOSE)]},
        "offer": {"message": "বিজ্ঞাপন: আমাদের সহযোগী অ্যাপটি ইনস্টল করুন। "
                             "ইনস্টল করলে আপনি এই ওয়েবসাইট থেকে বেরিয়ে যাবেন।",
                  "links": [("offer", "অ্যাপটি ইনস্টল করুন"),
                            ("decline", "না, ধন্যবাদ")]},
    },
    "hi": {
        "cookie": {"message": "आपको बेहतरीन अनुभव देने के लिए यह वेबसाइट कुकीज़ का उपयोग करती है।",
                   "links": [("close", CLOSE)]},
        "offer": {"message": "विज्ञापन: हमारे सहयोगी ऐप को इंस्टॉल करें। "
                             "इंस्टॉल करने पर यह वेबसाइट छूट जाएगी।",
                  "links": [("offer", "ऐप इंस्टॉल करें"),
                            ("decline", "नहीं, धन्यवाद")]},
    },
    "ur": {
        "cookie": {"message": "یہ ویب سائٹ آپ کو بہترین تجربہ فراہم کرنے کے لیے کوکیز استعمال کرتی ہے۔",
                   "links": [("close", CLOSE)]},
        "offer": {"message": "اشتہار: ہماری شراکت دار ایپ انسٹال کریں۔ "
                             "انسٹال کرنے پر یہ ویب سائٹ چھوٹ جائے گی۔",
                  "links": [("offer", "ایپ انسٹال کریں"),
                            ("decline", "نہیں، شکریہ")]},
    },
    "am": {
        "cookie": {"message": "ይህ ድረ-ገጽ ምርጥ ተሞክሮ ለመስጠት ኩኪዎችን ይጠቀማል።",
                   "links": [("close", CLOSE)]},
        "offer": {"message": "ማስታወቂያ፦ የአጋራችንን መተግበሪያ ይጫኑ። "
                             "መጫኑ ከዚህ ድረ-ገጽ ያስወጣዎታል።",
                  "links": [("offer", "መተግበሪያውን ይጫኑ"),
                            ("decline", "አይ፣ አመሰግናለሁ")]},
    },
}

REVIEWED = {"en": True, "bn": True, "hi": True, "ur": True, "am": True}
RTL = {"ur"}


def check_packs():
    import unicodedata
    ref = POPUP_TEXT["en"]
    for lang, pack in POPUP_TEXT.items():
        assert set(pack) == set(ORDER) == set(ref), lang
        for name in ORDER:
            kinds = [k for k, _ in pack[name]["links"]]
            assert kinds == [k for k, _ in ref[name]["links"]], (lang, name)
            texts = [pack[name]["message"]] + [l for _, l in pack[name]["links"]]
            for s in texts:
                assert s.strip(), (lang, name)
                assert not any(unicodedata.category(c) == "Nd" for c in s), (lang, name, s)
        assert pack["cookie"]["links"] == [("close", CLOSE)], lang
    return True
