import re

LEX_HI = {
    "with": "सहित", "and": "और", "for": "के लिए", "of": "का",
    "to": "से",
    "set": "सेट", "pack": "पैक", "piece": "पीस", "pieces": "पीस",
    "size": "साइज़", "in": "इन", "per": "प्रति",
    "inch": "इंच", "inches": "इंच", "cm": "सेमी", "mm": "मिमी",
    "ft": "फीट", "feet": "फीट", "kg": "किग्रा", "g": "ग्राम",
    "ml": "मिली", "l": "ली", "oz": "औंस", "litre": "लीटर",
    "liter": "लीटर", "gram": "ग्राम", "meter": "मीटर", "metre": "मीटर",
    "black": "काला", "white": "सफ़ेद", "red": "लाल", "blue": "नीला",
    "green": "हरा", "yellow": "पीला", "brown": "भूरा", "grey": "स्लेटी",
    "gray": "स्लेटी", "pink": "गुलाबी", "orange": "नारंगी",
    "purple": "बैंगनी", "silver": "चांदी", "golden": "सुनहरा",
    "gold": "गोल्ड", "beige": "बेज", "ivory": "आइवरी", "navy": "नेवी",
    "multicolour": "बहुरंगी", "multicolor": "बहुरंगी", "dark": "गहरा",
    "light": "हल्का", "natural": "प्राकृतिक", "clear": "पारदर्शी",
    "steel": "स्टील", "stainless": "स्टेनलेस", "wood": "लकड़ी",
    "wooden": "लकड़ी का", "glass": "काँच", "plastic": "प्लास्टिक",
    "cotton": "सूती", "leather": "चमड़ा", "metal": "धातु",
    "ceramic": "सिरेमिक", "bamboo": "बांस", "silk": "रेशमी",
    "wool": "ऊनी", "rubber": "रबर", "paper": "कागज़", "iron": "लोहा",
    "brass": "पीतल", "copper": "तांबा", "marble": "संगमरमर",
    "fabric": "कपड़ा", "velvet": "मखमल", "linen": "लिनन",
    "chair": "कुर्सी", "table": "मेज़", "lamp": "लैंप", "bed": "पलंग",
    "pillow": "तकिया", "cushion": "गद्दी", "blanket": "कंबल",
    "sheet": "चादर", "sheets": "चादरें", "towel": "तौलिया",
    "curtain": "पर्दा", "rug": "गलीचा", "carpet": "कालीन",
    "shelf": "शेल्फ़", "mirror": "आईना", "clock": "घड़ी",
    "watch": "घड़ी", "bottle": "बोतल", "cup": "कप", "mug": "मग",
    "plate": "प्लेट", "plates": "प्लेटें", "bowl": "कटोरा",
    "spoon": "चम्मच", "knife": "चाकू", "pan": "कड़ाही",
    "pot": "बर्तन", "jar": "मर्तबान", "tray": "ट्रे", "box": "डिब्बा",
    "bag": "थैला", "basket": "टोकरी", "brush": "ब्रश", "soap": "साबुन",
    "oil": "तेल", "tea": "चाय", "coffee": "कॉफ़ी", "sugar": "चीनी",
    "salt": "नमक", "rice": "चावल", "flour": "आटा", "honey": "शहद",
    "spice": "मसाला", "spices": "मसाले", "nuts": "मेवे",
    "seeds": "बीज", "dog": "कुत्ता", "cat": "बिल्ली", "pet": "पालतू",
    "bird": "पक्षी", "fish": "मछली", "toy": "खिलौना",
    "toys": "खिलौने", "game": "खेल", "ball": "गेंद", "doll": "गुड़िया",
    "book": "किताब", "pen": "कलम", "pencil": "पेंसिल",
    "notebook": "नोटबुक", "chart": "चार्ट", "card": "कार्ड",
    "cards": "कार्ड", "plant": "पौधा", "plants": "पौधे",
    "flower": "फूल", "garden": "बगीचा", "seed": "बीज",
    "shoes": "जूते", "shoe": "जूता", "socks": "मोज़े",
    "shirt": "कमीज़", "cover": "कवर", "case": "केस",
    "stand": "स्टैंड", "holder": "होल्डर", "organizer": "ऑर्गनाइज़र",
    "organiser": "ऑर्गनाइज़र", "cleaner": "क्लीनर", "filter": "फ़िल्टर",
    "charger": "चार्जर", "cable": "केबल", "battery": "बैटरी",
    "batteries": "बैटरियाँ", "light": "लाइट", "bulb": "बल्ब",
    "candle": "मोमबत्ती", "frame": "फ़्रेम", "wall": "दीवार",
    "door": "दरवाज़ा", "window": "खिड़की", "kitchen": "रसोई",
    "office": "दफ़्तर", "home": "घर", "baby": "शिशु",
    "kids": "बच्चों का", "men": "पुरुषों का", "women": "महिलाओं का",
    "large": "बड़ा", "small": "छोटा", "big": "बड़ा", "mini": "मिनी",
    "new": "नया", "soft": "मुलायम", "hard": "कठोर", "round": "गोल",
    "square": "चौकोर", "fresh": "ताज़ा", "dry": "सूखा",
    "organic": "जैविक", "premium": "प्रीमियम", "classic": "क्लासिक",
    "modern": "आधुनिक", "portable": "पोर्टेबल", "foldable": "फोल्डेबल",
    "adjustable": "समायोज्य", "waterproof": "जलरोधी",
    "rechargeable": "रिचार्जेबल", "wireless": "वायरलेस",
    "whole": "साबुत", "pure": "शुद्ध", "double": "डबल",
    "single": "सिंगल", "twin": "ट्विन", "king": "किंग",
    "queen": "क्वीन", "extra": "एक्स्ट्रा", "heavy": "भारी",
    "duty": "ड्यूटी", "free": "फ़्री", "anti": "एंटी",
    "non": "नॉन", "multi": "मल्टी",
}

EXC_HI = {
    "mouse": "माउस", "keyboard": "कीबोर्ड", "usb": "यूएसबी",
    "led": "एलईडी", "lcd": "एलसीडी", "hdmi": "एचडीएमआई",
    "wifi": "वाईफ़ाई", "bluetooth": "ब्लूटूथ", "headphones": "हेडफ़ोन",
    "headphone": "हेडफ़ोन", "earphones": "इयरफ़ोन", "speaker": "स्पीकर",
    "speakers": "स्पीकर", "camera": "कैमरा", "tripod": "ट्राइपॉड",
    "microphone": "माइक्रोफ़ोन", "laptop": "लैपटॉप", "tablet": "टैबलेट",
    "phone": "फ़ोन", "smartphone": "स्मार्टफ़ोन", "gaming": "गेमिंग",
    "mat": "मैट", "yoga": "योग", "dumbbell": "डम्बल",
    "kettlebell": "केटलबेल", "cricket": "क्रिकेट",
    "football": "फ़ुटबॉल", "basketball": "बास्केटबॉल",
    "badminton": "बैडमिंटन", "tennis": "टेनिस", "gym": "जिम",
    "fitness": "फ़िटनेस", "exercise": "एक्सरसाइज़",
    "resistance": "रेज़िस्टेंस", "band": "बैंड", "bands": "बैंड",
    "sofa": "सोफ़ा", "cushions": "गद्दियाँ", "mattress": "गद्दा",
    "recliner": "रिक्लाइनर", "ottoman": "ऑटोमन", "stool": "स्टूल",
    "desk": "डेस्क", "drawer": "दराज़", "wardrobe": "अलमारी",
    "bookshelf": "बुकशेल्फ़", "planter": "प्लांटर", "vase": "फूलदान",
    "skillet": "स्किलेट", "griddle": "तवा", "cooker": "कुकर",
    "blender": "ब्लेंडर", "mixer": "मिक्सर", "grinder": "ग्राइंडर",
    "toaster": "टोस्टर", "kettle": "केतली", "thermos": "थर्मस",
    "tiffin": "टिफ़िन", "lunch": "लंच", "dinner": "डिनर",
    "chocolate": "चॉकलेट", "cookies": "कुकीज़", "biscuit": "बिस्कुट",
    "biscuits": "बिस्कुट", "juice": "जूस", "masala": "मसाला",
    "leash": "पट्टा", "collar": "कॉलर", "harness": "हार्नेस",
    "aquarium": "एक्वेरियम", "kennel": "केनेल", "litter": "लिटर",
    "shampoo": "शैम्पू", "grooming": "ग्रूमिंग", "treats": "ट्रीट्स",
    "puzzle": "पहेली", "blocks": "ब्लॉक्स", "lego": "लेगो",
    "teddy": "टेडी", "bear": "भालू", "marker": "मार्कर",
    "markers": "मार्कर", "stapler": "स्टेपलर", "folder": "फ़ोल्डर",
    "files": "फ़ाइलें", "file": "फ़ाइल", "envelope": "लिफ़ाफ़ा",
    "envelopes": "लिफ़ाफ़े", "diary": "डायरी", "planner": "प्लानर",
    "calculator": "कैलकुलेटर", "printer": "प्रिंटर",
    "adapter": "अडैप्टर", "charging": "चार्जिंग", "power": "पावर",
    "wire": "तार", "remote": "रिमोट", "security": "सिक्योरिटी",
    "sensor": "सेंसर", "alarm": "अलार्म", "digital": "डिजिटल",
    "electric": "इलेक्ट्रिक", "electronic": "इलेक्ट्रॉनिक",
    "automatic": "स्वचालित", "manual": "मैनुअल",
    "type": "टाइप", "wide": "वाइड", "ruled": "रूल्ड",
    "composition": "कंपोज़िशन", "playstation": "प्लेस्टेशन",
    "controller": "कंट्रोलर", "century": "सेंचुरी",
    "customizable": "कस्टमाइज़ेबल", "daybed": "डेबेड",
    "sauce": "सॉस", "marinara": "मैरिनारा", "sodium": "सोडियम",
    "balance": "बैलेंस", "pump": "पंप", "singles": "सिंगल्स",
    "flute": "फ़्लूट", "swirl": "स्वर्ल", "uptown": "अपटाउन",
    "essentials": "एसेंशियल्स", "silicone": "सिलिकॉन",
    "tufted": "टफ़्टेड", "mix": "मिक्स", "low": "लो",
    "water": "वॉटर", "pad": "पैड", "food": "फ़ूड",
    "strathwood": "स्ट्रैथवुड", "vedaka": "वेदका", "drink": "ड्रिंक",
    "board": "बोर्ड", "high": "हाई", "cut": "कट",
    "compact": "कॉम्पैक्ट", "family": "फ़ैमिली", "tree": "ट्री",
    "shredder": "श्रेडर", "erase": "इरेज़", "patio": "पैटियो",
    "amazon": "अमेज़न", "cross": "क्रॉस", "mid": "मिड",
    "outdoor": "आउटडोर", "weight": "वेट", "foam": "फ़ोम",
    "kit": "किट", "mesh": "मेश", "storage": "स्टोरेज",
    "travel": "ट्रैवल", "chicken": "चिकन", "strap": "स्ट्रैप",
    "bar": "बार", "folding": "फ़ोल्डिंग", "dining": "डाइनिंग",
    "port": "पोर्ट", "tier": "टियर", "collection": "कलेक्शन",
    "tower": "टावर", "furniture": "फ़र्नीचर",
    "scratching": "स्क्रैचिंग", "binder": "बाइंडर",
    "credit": "क्रेडिट", "aluminum": "एल्युमिनियम",
    "aluminium": "एल्युमिनियम", "stick": "स्टिक",
    "glasses": "गिलास", "seat": "सीट", "basic": "बेसिक",
    "lid": "ढक्कन", "bags": "थैले", "standing": "स्टैंडिंग",
}

_HI_EXTRA = {
    "paws": "पॉज़", "umbrella": "छाता", "alkaline": "एल्कलाइन",
    "industrial": "इंडस्ट्रियल", "copy": "कॉपी", "cheese": "चीज़",
    "print": "प्रिंट", "zip": "ज़िप", "wild": "वाइल्ड",
    "accessories": "एक्सेसरीज़", "grill": "ग्रिल", "long": "लंबा",
    "heater": "हीटर", "contemporary": "कंटेम्पररी", "tape": "टेप",
    "cage": "पिंजरा", "onez": "वनज़", "base": "बेस",
    "multipurpose": "बहुउद्देशीय", "thick": "मोटा", "area": "एरिया",
    "sectional": "सेक्शनल", "farmhouse": "फ़ार्महाउस", "bright": "चमकीला",
    "amazonfresh": "अमेज़नफ़्रेश", "mount": "माउंट", "computer": "कंप्यूटर",
    "traditional": "पारंपरिक", "wine": "वाइन", "old": "पुराना",
    "stoneware": "स्टोनवेयर", "cast": "कास्ट", "solid": "सॉलिड",
    "symactive": "सिमएक्टिव", "sya": "सिया", "belfit": "बेलफ़िट",
    "hanging": "लटकने वाला", "post": "पोस्ट", "cream": "क्रीम",
    "dogs": "कुत्तों", "lithium": "लिथियम", "magnetic": "मैग्नेटिक",
    "rack": "रैक", "drinkware": "ड्रिंकवेयर", "room": "रूम",
    "essential": "एसेंशियल", "wicker": "विकर", "accent": "एक्सेंट",
    "panel": "पैनल", "ground": "ग्राउंड", "medium": "मीडियम",
    "recycled": "रीसाइकल्ड", "slime": "स्लाइम", "edition": "एडिशन",
    "universal": "यूनिवर्सल", "everyday": "एवरीडे", "cell": "सेल",
    "lightweight": "हल्का", "grip": "ग्रिप", "hand": "हैंड",
    "easel": "ईज़ल", "powder": "पाउडर", "container": "कंटेनर",
    "hot": "हॉट", "feeder": "फ़ीडर", "thermal": "थर्मल", "pound": "पाउंड",
    "market": "मार्केट", "all": "ऑल", "weather": "वेदर",
    "headboard": "हेडबोर्ड", "canvas": "कैनवास", "tiger": "टाइगर",
    "cats": "बिल्लियों", "apple": "एप्पल", "watt": "वॉट",
    "carrying": "कैरिंग", "floor": "फ़्लोर", "platform": "प्लेटफ़ॉर्म",
    "duvet": "डुवेट", "art": "आर्ट", "side": "साइड",
    "decorative": "सजावटी", "color": "कलर", "colour": "कलर",
    "carrier": "कैरियर", "legal": "लीगल", "putty": "पुट्टी",
    "brake": "ब्रेक", "crate": "क्रेट", "roast": "रोस्ट", "car": "कार",
    "fire": "फ़ायर", "or": "या", "vinyl": "विनाइल",
    "compostable": "कम्पोस्टेबल", "fashioned": "फ़ैशंड", "combo": "कॉम्बो",
    "sandwich": "सैंडविच", "hose": "होज़", "backpack": "बैकपैक",
    "training": "ट्रेनिंग", "ring": "रिंग", "top": "टॉप",
    "hardwood": "हार्डवुड", "rustic": "रस्टिक", "whiteboard": "व्हाइटबोर्ड",
    "unicorn": "यूनिकॉर्न", "lash": "लैश", "ears": "कान", "paint": "पेंट",
    "elevated": "ऊँचा", "recipe": "रेसिपी", "popular": "लोकप्रिय",
    "roasted": "रोस्टेड", "ergonomic": "एर्गोनॉमिक", "vintage": "विंटेज",
    "cookware": "कुकवेयर", "disposable": "डिस्पोज़ेबल", "salad": "सलाद",
    "swivel": "स्विवेल", "net": "नेट", "golf": "गोल्फ़", "foot": "फ़ुट",
    "indoor": "इनडोर", "bolster": "बोल्स्टर", "casual": "कैज़ुअल",
    "plush": "प्लश", "loveseat": "लवसीट", "nailhead": "नेलहेड",
    "geometric": "ज्यामितीय", "pendant": "पेंडेंट", "open": "ओपन",
    "trim": "ट्रिम", "grid": "ग्रिड", "lounge": "लाउंज", "finish": "फ़िनिश",
    "basics": "बेसिक्स", "pit": "पिट", "litter": "लिटर", "dal": "दाल",
    "micro": "माइक्रो", "ceiling": "सीलिंग", "headset": "हेडसेट",
    "style": "स्टाइल", "flat": "फ़्लैट", "height": "हाइट", "deep": "डीप",
    "handle": "हैंडल", "vacuum": "वैक्यूम", "serving": "सर्विंग",
    "insulated": "इंसुलेटेड", "pads": "पैड", "fatigue": "फ़टीग",
    "sided": "साइडेड", "tool": "टूल", "pasta": "पास्ता", "party": "पार्टी",
    "coolers": "कूलर", "replacement": "रिप्लेसमेंट", "by": "बाय",
    "belt": "बेल्ट", "pocket": "पॉकेट", "on": "ऑन", "chairs": "कुर्सियाँ",
    "swatch": "स्वैच", "sateen": "सैटीन", "end": "एंड", "living": "लिविंग",
    "sconce": "स्कॉन्स", "upholstered": "अपहोल्स्टर्ड", "sisal": "सिसल",
    "primary": "प्राइमरी", "presentation": "प्रेज़ेंटेशन", "adult": "एडल्ट",
    "washable": "धोने योग्य", "dividers": "डिवाइडर", "letter": "लेटर",
    "dual": "ड्यूल", "control": "कंट्रोल", "capacity": "कैपेसिटी",
    "displayport": "डिस्प्लेपोर्ट", "bundle": "बंडल", "clip": "क्लिप",
    "neoprene": "नियोप्रीन", "full": "फ़ुल", "bean": "बीन",
    "pressure": "प्रेशर", "pods": "पॉड", "cups": "कप", "cooler": "कूलर",
    "ounce": "औंस", "street": "स्ट्रीट", "bowls": "कटोरे",
    "dispenser": "डिस्पेंसर", "potato": "आलू", "milk": "दूध",
    "glitter": "ग्लिटर", "dumbbells": "डम्बल", "french": "फ़्रेंच",
    "padded": "पैडेड", "rope": "रस्सी", "space": "स्पेस", "pouch": "पाउच",
    "quality": "क्वालिटी", "density": "डेंसिटी", "soccer": "सॉकर",
    "stripe": "स्ट्राइप", "printed": "प्रिंटेड", "counter": "काउंटर",
    "arm": "आर्म", "reversible": "रिवर्सिबल", "legs": "लेग्स", "back": "बैक",
    "lounger": "लाउंजर", "throw": "थ्रो", "chandelier": "झूमर",
    "photo": "फ़ोटो", "journal": "जर्नल", "wirebound": "वायरबाउंड",
    "house": "हाउस", "puppy": "पपी", "condo": "कॉन्डो", "kennel": "केनेल",
    "kitten": "किटन", "peanut": "मूँगफली", "glue": "गोंद", "tab": "टैब",
    "adhesive": "चिपकने वाला", "permanent": "परमानेंट", "beans": "बीन्स",
    "android": "एंड्रॉइड", "ear": "ईयर", "pre": "प्री", "charged": "चार्ज्ड",
    "display": "डिस्प्ले", "wired": "वायर्ड", "nintendo": "निन्टेंडो",
    "station": "स्टेशन", "play": "प्ले", "mobile": "मोबाइल",
    "iphone": "आईफ़ोन", "gel": "जेल", "easy": "ईज़ी", "one": "वन",
    "collapsible": "फ़ोल्डेबल", "anodized": "एनोडाइज़्ड", "gloves": "दस्ताने",
    "tritan": "ट्राइटन", "drinking": "ड्रिंकिंग",
    "compartment": "कम्पार्टमेंट", "blend": "ब्लेंड", "stemless": "स्टेमलेस",
    "meal": "मील", "block": "ब्लॉक", "stitched": "सिला हुआ", "gear": "गियर",
    "step": "स्टेप", "picnic": "पिकनिक", "barbell": "बारबेल",
    "framed": "फ़्रेम्ड", "microfiber": "माइक्रोफ़ाइबर",
    "microfibre": "माइक्रोफ़ाइबर", "shag": "शैग", "oversized": "ओवरसाइज़्ड",
    "fitted": "फ़िटेड", "stone": "पत्थर", "couch": "काउच", "made": "मेड",
    "bath": "बाथ", "college": "कॉलेज", "chaise": "शेज़", "bistro": "बिस्ट्रो",
    "rattan": "रतन", "falkner": "फ़ॉकनर", "lights": "लाइट्स", "can": "कैन",
    "week": "सप्ताह", "copier": "कॉपियर", "compatible": "कम्पैटिबल",
    "tin": "टिन", "eye": "आई", "trouncer": "ट्राउंसर", "rex": "रेक्स",
    "penguin": "पेंगुइन", "eyes": "आँखें", "ash": "ऐश", "stamp": "स्टैम्प",
    "painter": "पेंटर", "posts": "पोस्ट", "jerky": "जर्की",
    "liquid": "लिक्विड", "pens": "पेन", "chips": "चिप्स", "split": "स्प्लिट",
    "lightning": "लाइटनिंग", "connector": "कनेक्टर",
    "commercial": "कमर्शियल", "bradford": "ब्रैडफ़ोर्ड", "armless": "आर्मलेस",
    "polyester": "पॉलिएस्टर", "ready": "रेडी", "foods": "फ़ूड्स",
    "cobb": "कॉब", "reprint": "रीप्रिंट", "sailing": "सेलिंग",
    "ship": "शिप", "patent": "पेटेंट", "metallic": "मेटैलिक", "ink": "इंक",
    "keychain": "कीचेन", "peeler": "पीलर", "roller": "रोलर",
    "wiper": "वाइपर", "tumbler": "टम्बलर", "bench": "बेंच",
    "cabinet": "कैबिनेट", "hanger": "हैंगर", "hangers": "हैंगर",
    "scale": "स्केल", "timer": "टाइमर", "opener": "ओपनर",
    "strainer": "छन्नी", "whisk": "व्हिस्क", "spatula": "स्पैचुला",
    "ladle": "करछुल", "tongs": "चिमटा", "grater": "कद्दूकस",
    "colander": "छलनी", "apron": "एप्रन", "napkins": "नैपकिन",
    "napkin": "नैपकिन", "sponge": "स्पंज", "sponges": "स्पंज",
    "trash": "ट्रैश", "garbage": "कचरा", "laundry": "लॉन्ड्री",
    "hamper": "हैम्पर", "shower": "शावर", "toilet": "टॉयलेट", "sink": "सिंक",
    "faucet": "नल", "spray": "स्प्रे", "sprayer": "स्प्रेयर",
    "watering": "वॉटरिंग", "nozzle": "नोज़ल", "shovel": "फावड़ा",
    "rake": "रेक", "pruner": "प्रूनर", "pruning": "प्रूनिंग",
    "shears": "कैंची", "scissors": "कैंची", "gnome": "नोम",
    "fountain": "फ़व्वारा", "solar": "सोलर", "lantern": "लालटेन",
    "string": "स्ट्रिंग", "fairy": "फ़ेयरी", "bulbs": "बल्ब", "chew": "च्यू",
    "squeaky": "स्क्वीकी", "bone": "हड्डी", "kibble": "किबल", "bed": "बेड",
    "beds": "बेड", "litterbox": "लिटरबॉक्स", "scratcher": "स्क्रैचर",
    "perch": "पर्च", "hutch": "हच", "terrarium": "टेरारियम",
    "hamster": "हैम्स्टर", "rabbit": "खरगोश", "wheel": "पहिया",
    "bell": "घंटी", "action": "एक्शन", "figure": "फ़िगर",
    "figures": "फ़िगर", "building": "बिल्डिंग", "bricks": "ब्रिक्स",
    "craft": "क्राफ़्ट", "crayons": "क्रेयॉन", "coloring": "कलरिंग",
    "colouring": "कलरिंग", "sticker": "स्टिकर", "stickers": "स्टिकर",
    "playset": "प्लेसेट", "racing": "रेसिंग", "dinosaur": "डायनासोर",
    "robot": "रोबोट", "kite": "पतंग", "bubble": "बबल", "bubbles": "बबल",
    "chalk": "चॉक", "paperback": "पेपरबैक", "hardcover": "हार्डकवर",
    "novel": "उपन्यास", "cookbook": "कुकबुक", "guide": "गाइड",
    "atlas": "एटलस", "dictionary": "शब्दकोश", "sketchbook": "स्केचबुक",
    "highlighter": "हाइलाइटर", "highlighters": "हाइलाइटर", "eraser": "रबर",
    "ruler": "स्केल", "clips": "क्लिप", "staples": "स्टेपल",
    "labels": "लेबल", "label": "लेबल", "index": "इंडेक्स", "sticky": "स्टिकी",
    "notes": "नोट्स", "notepad": "नोटपैड", "notepads": "नोटपैड",
    "clipboard": "क्लिपबोर्ड", "lamination": "लैमिनेशन",
    "laminating": "लैमिनेटिंग", "pouches": "पाउच", "toner": "टोनर",
    "cartridge": "कार्ट्रिज", "ream": "रीम", "sheets": "शीट", "sheet": "शीट",
    "machine": "मशीन", "handi": "हांडी", "roti": "रोटी", "tawa": "तवा",
    "chowder": "चाउडर", "clam": "क्लैम", "spoons": "चम्मच", "forks": "काँटे",
    "fork": "काँटा", "knives": "चाकू", "cutlery": "कटलरी", "kadai": "कड़ाही",
    "idli": "इडली", "dosa": "डोसा", "chapati": "चपाती", "quilt": "रज़ाई",
    "bedsheet": "बेडशीट", "pillowcase": "तकिया कवर", "mixing": "मिक्सिंग",
    "baking": "बेकिंग", "cake": "केक",
}
for _k, _v in _HI_EXTRA.items():
    EXC_HI.setdefault(_k, _v)

_HI_VOWELS_IND = {"a": "अ", "e": "ए", "i": "इ", "o": "ओ", "u": "उ",
                  "aa": "आ", "ee": "ई", "oo": "ऊ", "ai": "ऐ",
                  "au": "औ", "ea": "ई", "ou": "आउ", "ay": "े",
                  "aw": "ॉ", "ow": "ाउ"}
_HI_MATRA = {"a": "", "e": "े", "i": "ि", "o": "ो", "u": "ु",
             "aa": "ा", "ee": "ी", "oo": "ू", "ai": "ै", "au": "ौ",
             "ea": "ी", "ou": "ाउ", "ay": "े", "aw": "ॉ", "ow": "ाउ"}
_HI_CONS = {"b": "ब", "c": "क", "d": "ड", "f": "फ़", "g": "ग",
            "h": "ह", "j": "ज", "k": "क", "l": "ल", "m": "म",
            "n": "न", "p": "प", "q": "क", "r": "र", "s": "स",
            "t": "ट", "v": "व", "w": "व", "x": "क्स", "y": "य",
            "z": "ज़", "ch": "च", "sh": "श", "th": "थ", "ph": "फ",
            "wh": "व", "ck": "क", "gh": "घ", "kh": "ख", "bh": "भ",
            "dh": "ध", "qu": "क्व"}


def _hi_translit(word):
    w = word.lower()

    w = re.sub(r"ation$", "eshan", w)
    w = re.sub(r"[st]ion$", "shan", w)
    w = re.sub(r"ture$", "char", w)
    w = re.sub(r"([bcdfghjklmnpqrstvwxz])le$", r"\1al", w)
    w = re.sub(r"a([bcdfghjklmnpqrstvwxz])e$", r"e\1", w)
    w = re.sub(r"i([bcdfghjklmnpqrstvwxz])e$", r"ai\1", w)
    w = re.sub(r"o([bcdfghjklmnpqrstvwxz])e$", r"o\1", w)
    w = re.sub(r"u([bcdfghjklmnpqrstvwxz])e$", r"oo\1", w)
    w = re.sub(r"ce$", "s", w)
    w = re.sub(r"c([eiy])", r"s\1", w)
    w = re.sub(r"er$", "ar", w)
    w = re.sub(r"ow$", "o", w)
    w = re.sub(r"y$", "ee", w)
    w = re.sub(r"^u", "a", w)
    w = re.sub(r"(.)\1", r"\1", w)

    units, i = [], 0
    keys2 = {k for k in list(_HI_CONS) + list(_HI_MATRA) if len(k) == 2}
    while i < len(w):
        pair = w[i:i + 2]
        if pair in keys2:
            units.append(pair)
            i += 2
        else:
            units.append(w[i])
            i += 1
    out, prev_cons = [], False
    for j, u in enumerate(units):
        if u in ("n", "m") and j + 1 < len(units) \
                and units[j + 1] in _HI_CONS and prev_cons is False \
                and j > 0:
            out.append("ं")
            prev_cons = False
            continue
        if u in _HI_CONS:
            if prev_cons:
                out.append("्")
            out.append(_HI_CONS[u])
            prev_cons = True
        elif u in _HI_MATRA:
            if prev_cons:
                out.append(_HI_MATRA[u])
            else:
                out.append(_HI_VOWELS_IND.get(u, u))
            prev_cons = False
        else:
            out.append(u)
            prev_cons = False
    return "".join(out)


def _brand_caps(word, exc):
    return (word.isupper() and len(word) >= 4
            and word.lower() not in ("hdmi", "wifi", "usb", "led"))


def _hi_word(word):
    lw = word.lower()
    if _brand_caps(word, EXC_HI):
        return word
    if lw in LEX_HI:
        return LEX_HI[lw]
    if lw in EXC_HI:
        return EXC_HI[lw]
    if not re.search(r"[a-zA-Z]", word):
        return word
    if word.isupper() and len(word) >= 2:
        return word
    if len(lw) <= 2 and lw not in ("tv",):
        return word
    return _hi_translit(word)


LEX_BN = {
    "with": "সহ", "and": "ও", "for": "এর জন্য", "of": "এর",
    "to": "থেকে", "set": "সেট", "pack": "প্যাক", "piece": "পিস",
    "pieces": "পিস", "size": "সাইজ", "in": "ইন", "per": "প্রতি",
    "inch": "ইঞ্চি", "inches": "ইঞ্চি", "cm": "সেমি", "mm": "মিমি",
    "ft": "ফুট", "feet": "ফুট", "kg": "কেজি", "g": "গ্রাম",
    "ml": "মিলি", "l": "লি", "oz": "আউন্স", "litre": "লিটার",
    "liter": "লিটার", "gram": "গ্রাম", "meter": "মিটার",
    "metre": "মিটার",
    "black": "কালো", "white": "সাদা", "red": "লাল", "blue": "নীল",
    "green": "সবুজ", "yellow": "হলুদ", "brown": "বাদামি",
    "grey": "ধূসর", "gray": "ধূসর", "pink": "গোলাপি",
    "orange": "কমলা", "purple": "বেগুনি", "silver": "রুপালি",
    "golden": "সোনালি", "gold": "গোল্ড", "beige": "বেজ",
    "ivory": "আইভরি", "navy": "নেভি", "multicolour": "বহুরঙা",
    "multicolor": "বহুরঙা", "dark": "গাঢ়", "light": "হালকা",
    "natural": "প্রাকৃতিক", "clear": "স্বচ্ছ",
    "steel": "স্টিল", "stainless": "স্টেইনলেস", "wood": "কাঠ",
    "wooden": "কাঠের", "glass": "কাচ", "plastic": "প্লাস্টিক",
    "cotton": "সুতি", "leather": "চামড়া", "metal": "ধাতু",
    "ceramic": "সিরামিক", "bamboo": "বাঁশ", "silk": "রেশমি",
    "wool": "উলের", "rubber": "রাবার", "paper": "কাগজ",
    "iron": "লোহা", "brass": "পিতল", "copper": "তামা",
    "marble": "মার্বেল", "fabric": "কাপড়", "velvet": "মখমল",
    "linen": "লিনেন",
    "chair": "চেয়ার", "table": "টেবিল", "lamp": "ল্যাম্প",
    "bed": "খাট", "pillow": "বালিশ", "cushion": "কুশন",
    "blanket": "কম্বল", "sheet": "চাদর", "sheets": "চাদর",
    "towel": "তোয়ালে", "curtain": "পর্দা", "rug": "গালিচা",
    "carpet": "কার্পেট", "shelf": "শেল্ফ", "mirror": "আয়না",
    "clock": "ঘড়ি", "watch": "ঘড়ি", "bottle": "বোতল",
    "cup": "কাপ", "mug": "মগ", "plate": "প্লেট",
    "plates": "প্লেট", "bowl": "বাটি", "spoon": "চামচ",
    "knife": "ছুরি", "pan": "কড়াই", "pot": "পাত্র",
    "jar": "বয়াম", "tray": "ট্রে", "box": "বাক্স",
    "bag": "ব্যাগ", "basket": "ঝুড়ি", "brush": "ব্রাশ",
    "soap": "সাবান", "oil": "তেল", "tea": "চা", "coffee": "কফি",
    "sugar": "চিনি", "salt": "লবণ", "rice": "চাল", "flour": "আটা",
    "honey": "মধু", "spice": "মসলা", "spices": "মসলা",
    "nuts": "বাদাম", "seeds": "বীজ", "dog": "কুকুর",
    "cat": "বিড়াল", "pet": "পোষা", "bird": "পাখি", "fish": "মাছ",
    "toy": "খেলনা", "toys": "খেলনা", "game": "খেলা",
    "ball": "বল", "doll": "পুতুল", "book": "বই", "pen": "কলম",
    "pencil": "পেন্সিল", "notebook": "নোটবুক", "chart": "চার্ট",
    "card": "কার্ড", "cards": "কার্ড", "plant": "গাছ",
    "plants": "গাছ", "flower": "ফুল", "garden": "বাগান",
    "seed": "বীজ", "shoes": "জুতা", "shoe": "জুতা",
    "socks": "মোজা", "shirt": "শার্ট", "cover": "কভার",
    "case": "কেস", "stand": "স্ট্যান্ড", "holder": "হোল্ডার",
    "organizer": "অর্গানাইজার", "organiser": "অর্গানাইজার",
    "cleaner": "ক্লিনার", "filter": "ফিল্টার", "charger": "চার্জার",
    "cable": "কেবল", "battery": "ব্যাটারি",
    "batteries": "ব্যাটারি", "bulb": "বাল্ব",
    "candle": "মোমবাতি", "frame": "ফ্রেম", "wall": "দেয়াল",
    "door": "দরজা", "window": "জানালা", "kitchen": "রান্নাঘর",
    "office": "অফিস", "home": "ঘর", "baby": "শিশু",
    "kids": "শিশুদের", "men": "পুরুষদের", "women": "নারীদের",
    "large": "বড়", "small": "ছোট", "big": "বড়", "mini": "মিনি",
    "new": "নতুন", "soft": "নরম", "hard": "শক্ত", "round": "গোল",
    "square": "চৌকো", "fresh": "তাজা", "dry": "শুকনো",
    "organic": "জৈব", "premium": "প্রিমিয়াম", "classic": "ক্লাসিক",
    "modern": "আধুনিক", "portable": "পোর্টেবল",
    "foldable": "ভাঁজযোগ্য", "adjustable": "সমন্বয়যোগ্য",
    "waterproof": "জলরোধী", "rechargeable": "রিচার্জেবল",
    "wireless": "ওয়্যারলেস", "whole": "আস্ত", "pure": "খাঁটি",
    "double": "ডাবল", "single": "সিঙ্গেল", "twin": "টুইন",
    "king": "কিং", "queen": "কুইন", "extra": "এক্সট্রা",
    "heavy": "ভারী", "duty": "ডিউটি", "free": "ফ্রি",
    "anti": "অ্যান্টি", "non": "নন", "multi": "মাল্টি",
    "board": "বোর্ড", "high": "হাই", "cut": "কাট",
    "compact": "কমপ্যাক্ট", "family": "ফ্যামিলি", "tree": "গাছ",
    "outdoor": "আউটডোর", "weight": "ওজন", "foam": "ফোম",
    "kit": "কিট", "mesh": "মেশ", "storage": "স্টোরেজ",
    "travel": "ভ্রমণ", "chicken": "মুরগি", "strap": "স্ট্র্যাপ",
    "bar": "বার", "folding": "ভাঁজ করা", "dining": "ডাইনিং",
    "port": "পোর্ট", "tier": "স্তর", "collection": "কালেকশন",
    "tower": "টাওয়ার", "furniture": "আসবাব",
    "binder": "বাইন্ডার", "credit": "ক্রেডিট",
    "aluminum": "অ্যালুমিনিয়াম", "aluminium": "অ্যালুমিনিয়াম",
    "stick": "স্টিক", "glasses": "গ্লাস", "seat": "সিট",
    "basic": "বেসিক", "lid": "ঢাকনা", "bags": "ব্যাগ",
    "standing": "স্ট্যান্ডিং", "water": "ওয়াটার", "food": "ফুড",
    "mix": "মিক্স", "low": "লো", "mat": "ম্যাট", "pad": "প্যাড",
    "mid": "মিড", "cross": "ক্রস", "amazon": "আমাজন",
    "patio": "প্যাটিও", "shredder": "শ্রেডার", "erase": "মোছার",
    "scratching": "আঁচড়ানোর",
}

EXC_BN = {
    "mouse": "মাউস", "keyboard": "কীবোর্ড", "usb": "ইউএসবি",
    "led": "এলইডি", "hdmi": "এইচডিএমআই", "wifi": "ওয়াইফাই",
    "bluetooth": "ব্লুটুথ", "headphones": "হেডফোন",
    "headphone": "হেডফোন", "earphones": "ইয়ারফোন",
    "speaker": "স্পিকার", "speakers": "স্পিকার", "camera": "ক্যামেরা",
    "tripod": "ট্রাইপড", "microphone": "মাইক্রোফোন",
    "laptop": "ল্যাপটপ", "tablet": "ট্যাবলেট", "phone": "ফোন",
    "gaming": "গেমিং", "yoga": "যোগ", "dumbbell": "ডাম্বেল",
    "kettlebell": "কেটলবেল", "cricket": "ক্রিকেট",
    "football": "ফুটবল", "basketball": "বাস্কেটবল",
    "badminton": "ব্যাডমিন্টন", "tennis": "টেনিস", "gym": "জিম",
    "fitness": "ফিটনেস", "exercise": "ব্যায়াম",
    "resistance": "রেজিস্ট্যান্স", "band": "ব্যান্ড",
    "bands": "ব্যান্ড", "sofa": "সোফা", "mattress": "তোশক",
    "recliner": "রিক্লাইনার", "ottoman": "অটোমান", "stool": "টুল",
    "desk": "ডেস্ক", "drawer": "দেরাজ", "wardrobe": "আলমারি",
    "bookshelf": "বুকশেল্ফ", "planter": "প্ল্যান্টার",
    "vase": "ফুলদানি", "skillet": "স্কিলেট", "griddle": "তাওয়া",
    "cooker": "কুকার", "blender": "ব্লেন্ডার", "mixer": "মিক্সার",
    "grinder": "গ্রাইন্ডার", "toaster": "টোস্টার",
    "kettle": "কেটলি", "thermos": "থার্মোস", "lunch": "লাঞ্চ",
    "dinner": "ডিনার", "chocolate": "চকলেট", "cookies": "কুকিজ",
    "biscuit": "বিস্কুট", "biscuits": "বিস্কুট", "juice": "জুস",
    "masala": "মসলা", "leash": "লিশ", "collar": "কলার",
    "harness": "হারনেস", "aquarium": "অ্যাকোয়ারিয়াম",
    "shampoo": "শ্যাম্পু", "grooming": "গ্রুমিং",
    "treats": "ট্রিটস", "puzzle": "ধাঁধা", "blocks": "ব্লক",
    "teddy": "টেডি", "bear": "ভালুক", "marker": "মার্কার",
    "markers": "মার্কার", "stapler": "স্টেপলার",
    "folder": "ফোল্ডার", "files": "ফাইল", "file": "ফাইল",
    "envelope": "খাম", "envelopes": "খাম", "diary": "ডায়েরি",
    "planner": "প্ল্যানার", "calculator": "ক্যালকুলেটর",
    "printer": "প্রিন্টার", "adapter": "অ্যাডাপ্টার",
    "charging": "চার্জিং", "power": "পাওয়ার", "wire": "তার",
    "remote": "রিমোট", "security": "সিকিউরিটি",
    "sensor": "সেন্সর", "alarm": "অ্যালার্ম", "digital": "ডিজিটাল",
    "electric": "ইলেকট্রিক", "electronic": "ইলেকট্রনিক",
    "automatic": "স্বয়ংক্রিয়", "manual": "ম্যানুয়াল",
    "type": "টাইপ", "wide": "ওয়াইড", "ruled": "রুলড",
    "composition": "কম্পোজিশন", "playstation": "প্লেস্টেশন",
    "controller": "কন্ট্রোলার", "century": "সেঞ্চুরি",
    "customizable": "কাস্টমাইজেবল", "daybed": "ডেবেড",
    "sauce": "সস", "marinara": "মারিনারা", "sodium": "সোডিয়াম",
    "balance": "ব্যালেন্স", "pump": "পাম্প", "singles": "সিঙ্গেলস",
    "flute": "ফ্লুট", "swirl": "সোয়ার্ল", "uptown": "আপটাউন",
    "essentials": "এসেনশিয়ালস", "silicone": "সিলিকন",
    "tufted": "টাফটেড", "strathwood": "স্ট্র্যাথউড",
    "vedaka": "বেদাকা", "drink": "ড্রিংক", "business": "বিজনেস",
    "gummed": "গামড",
}

EXC_BN.update({
    "paws": "পজ", "umbrella": "ছাতা", "alkaline": "অ্যালকালাইন",
    "industrial": "ইন্ডাস্ট্রিয়াল", "copy": "কপি", "cheese": "চিজ",
    "print": "প্রিন্ট", "zip": "জিপ", "wild": "ওয়াইল্ড",
    "accessories": "অ্যাকসেসরিজ", "grill": "গ্রিল", "long": "লম্বা",
    "heater": "হিটার", "contemporary": "কনটেম্পোরারি", "tape": "টেপ",
    "cage": "খাঁচা", "onez": "ওয়ানজ", "base": "বেস",
    "multipurpose": "বহুমুখী", "thick": "মোটা", "area": "এরিয়া",
    "sectional": "সেকশনাল", "farmhouse": "ফার্মহাউস", "bright": "উজ্জ্বল",
    "amazonfresh": "আমাজনফ্রেশ", "mount": "মাউন্ট", "computer": "কম্পিউটার",
    "traditional": "ঐতিহ্যবাহী", "wine": "ওয়াইন", "old": "পুরনো",
    "stoneware": "স্টোনওয়্যার", "cast": "কাস্ট", "solid": "সলিড",
    "symactive": "সিমঅ্যাকটিভ", "sya": "সিয়া", "belfit": "বেলফিট",
    "hanging": "ঝোলানো", "post": "পোস্ট", "cream": "ক্রিম",
    "dogs": "কুকুর", "lithium": "লিথিয়াম", "magnetic": "ম্যাগনেটিক",
    "rack": "র‍্যাক", "drinkware": "ড্রিংকওয়্যার", "room": "রুম",
    "essential": "এসেনশিয়াল", "wicker": "বেতের", "accent": "অ্যাকসেন্ট",
    "panel": "প্যানেল", "ground": "গ্রাউন্ড", "medium": "মিডিয়াম",
    "recycled": "রিসাইকেলড", "slime": "স্লাইম", "edition": "এডিশন",
    "universal": "ইউনিভার্সাল", "everyday": "এভরিডে", "cell": "সেল",
    "lightweight": "হালকা ওজনের", "grip": "গ্রিপ", "hand": "হ্যান্ড",
    "easel": "ইজেল", "powder": "পাউডার", "container": "কন্টেইনার",
    "hot": "হট", "feeder": "ফিডার", "thermal": "থার্মাল",
    "pound": "পাউন্ড", "market": "মার্কেট", "all": "অল",
    "weather": "ওয়েদার", "headboard": "হেডবোর্ড", "canvas": "ক্যানভাস",
    "tiger": "টাইগার", "cats": "বিড়াল", "apple": "অ্যাপল",
    "watt": "ওয়াট", "carrying": "ক্যারিং", "floor": "ফ্লোর",
    "platform": "প্ল্যাটফর্ম", "duvet": "ডুভেট", "art": "আর্ট",
    "side": "সাইড", "decorative": "ডেকোরেটিভ", "color": "কালার",
    "colour": "কালার", "carrier": "ক্যারিয়ার", "legal": "লিগ্যাল",
    "putty": "পুটি", "brake": "ব্রেক", "crate": "ক্রেট",
    "roast": "রোস্ট", "car": "কার", "fire": "ফায়ার", "or": "বা",
    "vinyl": "ভিনাইল", "compostable": "কম্পোস্টেবল",
    "fashioned": "ফ্যাশনড", "combo": "কম্বো", "sandwich": "স্যান্ডউইচ",
    "hose": "হোস", "backpack": "ব্যাকপ্যাক", "training": "ট্রেনিং",
    "ring": "রিং", "top": "টপ", "hardwood": "হার্ডউড",
    "rustic": "রাস্টিক", "whiteboard": "হোয়াইটবোর্ড",
    "unicorn": "ইউনিকর্ন", "lash": "ল্যাশ", "ears": "কান",
    "paint": "পেইন্ট", "elevated": "উঁচু", "recipe": "রেসিপি",
    "popular": "জনপ্রিয়", "roasted": "রোস্টেড", "ergonomic": "এরগোনমিক",
    "vintage": "ভিনটেজ", "cookware": "কুকওয়্যার",
    "disposable": "ডিসপোজেবল", "salad": "সালাদ", "swivel": "সুইভেল",
    "net": "নেট", "golf": "গলফ", "foot": "ফুট", "indoor": "ইনডোর",
    "bolster": "বলস্টার", "casual": "ক্যাজুয়াল", "plush": "প্লাশ",
    "loveseat": "লাভসিট", "nailhead": "নেইলহেড", "geometric": "জ্যামিতিক",
    "pendant": "পেনডেন্ট", "open": "ওপেন", "trim": "ট্রিম",
    "grid": "গ্রিড", "lounge": "লাউঞ্জ", "finish": "ফিনিশ",
    "basics": "বেসিকস", "pit": "পিট", "litter": "লিটার", "dal": "ডাল",
    "micro": "মাইক্রো", "ceiling": "সিলিং", "headset": "হেডসেট",
    "style": "স্টাইল", "flat": "ফ্ল্যাট", "height": "হাইট",
    "deep": "ডিপ", "handle": "হ্যান্ডেল", "vacuum": "ভ্যাকুয়াম",
    "serving": "সার্ভিং", "insulated": "ইনসুলেটেড", "pads": "প্যাড",
    "fatigue": "ফ্যাটিগ", "sided": "সাইডেড", "tool": "টুল",
    "pasta": "পাস্তা", "party": "পার্টি", "coolers": "কুলার",
    "replacement": "রিপ্লেসমেন্ট", "by": "বাই", "belt": "বেল্ট",
    "pocket": "পকেট", "on": "অন", "chairs": "চেয়ার", "swatch": "সোয়াচ",
    "sateen": "সাটিন", "end": "এন্ড", "living": "লিভিং",
    "sconce": "স্কন্স", "upholstered": "আপহোলস্টার্ড", "sisal": "সিসাল",
    "primary": "প্রাইমারি", "presentation": "প্রেজেন্টেশন",
    "adult": "অ্যাডাল্ট", "washable": "ওয়াশেবল", "dividers": "ডিভাইডার",
    "letter": "লেটার", "dual": "ডুয়াল", "control": "কন্ট্রোল",
    "capacity": "ক্যাপাসিটি", "displayport": "ডিসপ্লেপোর্ট",
    "bundle": "বান্ডেল", "clip": "ক্লিপ", "neoprene": "নিওপ্রিন",
    "full": "ফুল", "bean": "বিন", "pressure": "প্রেশার", "pods": "পড",
    "cups": "কাপ", "cooler": "কুলার", "ounce": "আউন্স",
    "street": "স্ট্রিট", "bowls": "বাটি", "dispenser": "ডিসপেনসার",
    "potato": "আলু", "milk": "দুধ", "glitter": "গ্লিটার",
    "dumbbells": "ডাম্বেল", "french": "ফ্রেঞ্চ", "padded": "প্যাডেড",
    "rope": "দড়ি", "space": "স্পেস", "pouch": "পাউচ",
    "quality": "কোয়ালিটি", "density": "ডেনসিটি", "soccer": "সকার",
    "stripe": "স্ট্রাইপ", "printed": "প্রিন্টেড", "counter": "কাউন্টার",
    "arm": "আর্ম", "reversible": "রিভার্সিবল", "legs": "লেগস",
    "back": "ব্যাক", "lounger": "লাউঞ্জার", "throw": "থ্রো",
    "chandelier": "ঝাড়বাতি", "photo": "ফটো", "journal": "জার্নাল",
    "wirebound": "ওয়্যারবাউন্ড", "house": "হাউস", "puppy": "পাপি",
    "condo": "কন্ডো", "kennel": "কেনেল", "kitten": "কিটেন",
    "peanut": "চিনাবাদাম", "glue": "আঠা", "tab": "ট্যাব",
    "adhesive": "আঠালো", "permanent": "পার্মানেন্ট", "beans": "বিনস",
    "android": "অ্যান্ড্রয়েড", "ear": "ইয়ার", "pre": "প্রি",
    "charged": "চার্জড", "display": "ডিসপ্লে", "wired": "ওয়্যার্ড",
    "nintendo": "নিনটেন্ডো", "station": "স্টেশন", "play": "প্লে",
    "mobile": "মোবাইল", "iphone": "আইফোন", "gel": "জেল", "easy": "ইজি",
    "one": "ওয়ান", "collapsible": "ভাঁজযোগ্য", "anodized": "অ্যানোডাইজড",
    "gloves": "গ্লাভস", "tritan": "ট্রাইটান", "drinking": "ড্রিংকিং",
    "compartment": "কম্পার্টমেন্ট", "blend": "ব্লেন্ড",
    "stemless": "স্টেমলেস", "meal": "মিল", "block": "ব্লক",
    "stitched": "সেলাই করা", "gear": "গিয়ার", "step": "স্টেপ",
    "picnic": "পিকনিক", "barbell": "বারবেল", "framed": "ফ্রেমড",
    "microfiber": "মাইক্রোফাইবার", "microfibre": "মাইক্রোফাইবার",
    "shag": "শ্যাগ", "oversized": "ওভারসাইজড", "fitted": "ফিটেড",
    "stone": "পাথর", "couch": "কাউচ", "made": "মেড", "bath": "বাথ",
    "college": "কলেজ", "chaise": "শেজ", "bistro": "বিস্ত্রো",
    "rattan": "র‍্যাটান", "falkner": "ফকনার", "lights": "লাইট",
    "can": "ক্যান", "week": "সপ্তাহ", "copier": "কপিয়ার",
    "compatible": "কম্প্যাটিবল", "tin": "টিন", "eye": "আই",
    "trouncer": "ট্রাউন্সার", "rex": "রেক্স", "penguin": "পেঙ্গুইন",
    "eyes": "চোখ", "ash": "অ্যাশ", "stamp": "স্ট্যাম্প",
    "painter": "পেইন্টার", "posts": "পোস্ট", "jerky": "জার্কি",
    "liquid": "লিকুইড", "pens": "কলম", "chips": "চিপস", "split": "স্প্লিট",
    "lightning": "লাইটনিং", "connector": "কানেক্টর",
    "commercial": "কমার্শিয়াল", "bradford": "ব্র্যাডফোর্ড",
    "armless": "আর্মলেস", "polyester": "পলিয়েস্টার", "ready": "রেডি",
    "foods": "ফুডস", "cobb": "কব", "reprint": "রিপ্রিন্ট",
    "sailing": "সেইলিং", "ship": "শিপ", "patent": "পেটেন্ট",
    "metallic": "মেটালিক", "ink": "ইংক", "keychain": "কিচেইন",
    "peeler": "পিলার", "roller": "রোলার", "wiper": "ওয়াইপার",
    "tumbler": "টাম্বলার", "bench": "বেঞ্চ", "cabinet": "ক্যাবিনেট",
    "hanger": "হ্যাঙ্গার", "hangers": "হ্যাঙ্গার", "scale": "স্কেল",
    "timer": "টাইমার", "opener": "ওপেনার", "strainer": "ছাঁকনি",
    "whisk": "হুইস্ক", "spatula": "খুন্তি", "ladle": "হাতা",
    "tongs": "চিমটা", "grater": "গ্রেটার", "colander": "ঝাঁঝরি",
    "apron": "অ্যাপ্রন", "napkins": "ন্যাপকিন", "napkin": "ন্যাপকিন",
    "sponge": "স্পঞ্জ", "sponges": "স্পঞ্জ", "trash": "ট্র্যাশ",
    "garbage": "গার্বেজ", "laundry": "লন্ড্রি", "hamper": "হ্যাম্পার",
    "shower": "শাওয়ার", "toilet": "টয়লেট", "sink": "সিঙ্ক",
    "faucet": "ফসেট", "spray": "স্প্রে", "sprayer": "স্প্রেয়ার",
    "watering": "ওয়াটারিং", "nozzle": "নজল", "shovel": "বেলচা",
    "rake": "রেক", "pruner": "প্রুনার", "pruning": "প্রুনিং",
    "shears": "কাঁচি", "scissors": "কাঁচি", "gnome": "নোম",
    "fountain": "ফোয়ারা", "solar": "সোলার", "lantern": "লণ্ঠন",
    "string": "স্ট্রিং", "fairy": "ফেয়ারি", "bulbs": "বাল্ব",
    "chew": "চিউ", "squeaky": "স্কুইকি", "bone": "হাড়",
    "kibble": "কিবল", "bed": "বেড", "beds": "বেড", "litterbox": "লিটারবক্স",
    "scratcher": "স্ক্র্যাচার", "perch": "পার্চ", "hutch": "হাচ",
    "terrarium": "টেরারিয়াম", "hamster": "হ্যামস্টার", "rabbit": "খরগোশ",
    "wheel": "চাকা", "bell": "ঘণ্টা", "action": "অ্যাকশন",
    "figure": "ফিগার", "figures": "ফিগার", "building": "বিল্ডিং",
    "bricks": "ব্রিক", "craft": "ক্রাফট", "crayons": "ক্রেয়ন",
    "coloring": "কালারিং", "colouring": "কালারিং", "sticker": "স্টিকার",
    "stickers": "স্টিকার", "playset": "প্লেসেট", "racing": "রেসিং",
    "remote-control": "রিমোট-কন্ট্রোল", "dinosaur": "ডাইনোসর",
    "robot": "রোবট", "kite": "ঘুড়ি", "bubble": "বাবল",
    "bubbles": "বাবল", "chalk": "চক", "paperback": "পেপারব্যাক",
    "hardcover": "হার্ডকভার", "novel": "উপন্যাস", "cookbook": "রান্নার বই",
    "guide": "গাইড", "atlas": "অ্যাটলাস", "dictionary": "অভিধান",
    "sketchbook": "স্কেচবুক", "highlighter": "হাইলাইটার",
    "highlighters": "হাইলাইটার", "eraser": "রাবার", "ruler": "স্কেল",
    "clips": "ক্লিপ", "staples": "স্টেপল", "labels": "লেবেল",
    "label": "লেবেল", "index": "ইনডেক্স", "sticky": "স্টিকি",
    "notes": "নোটস", "notepad": "নোটপ্যাড", "notepads": "নোটপ্যাড",
    "legal-pad": "লিগ্যাল প্যাড", "clipboard": "ক্লিপবোর্ড",
    "lamination": "ল্যামিনেশন", "laminating": "ল্যামিনেটিং",
    "pouches": "পাউচ", "toner": "টোনার", "cartridge": "কার্ট্রিজ",
    "ream": "রিম", "sheets": "শিট", "sheet": "শিট",
    "machine": "মেশিন", "handi": "হাঁড়ি", "roti": "রুটি", "tawa": "তাওয়া",
    "chowder": "চাউডার", "clam": "ক্ল্যাম", "spoons": "চামচ",
    "forks": "কাঁটাচামচ", "fork": "কাঁটাচামচ", "knives": "ছুরি",
    "cutlery": "কাটলারি", "kadai": "কড়াই", "pressure-cooker": "প্রেশার কুকার",
    "idli": "ইডলি", "dosa": "দোসা", "chapati": "চাপাতি", "masala": "মসলা",
    "quilt": "কাঁথা", "bedsheet": "বিছানার চাদর", "pillowcase": "বালিশের কভার",
    "mixing": "মিক্সিং", "baking": "বেকিং", "cake": "কেক", "tea-set": "চা সেট",
})

EXC_BN.update({
    "screw": "স্ক্রু", "macbook": "ম্যাকবুক", "air": "এয়ার",
    "highball": "হাইবল", "splitter": "স্প্লিটার", "ethernet": "ইথারনেট",
    "bagley": "ব্যাগলি", "giant": "জায়ান্ট", "feather": "ফেদার",
    "oatmeal": "ওটমিল", "blank": "ব্ল্যাংক", "converter": "কনভার্টার",
    "weights": "ওয়েটস", "cart": "কার্ট", "fan": "ফ্যান",
    "pitchers": "পিচার", "brita": "ব্রিটা", "coriander": "ধনিয়া",
    "textured": "টেক্সচারড", "tortilla": "টর্টিলা",
    "fairtrade": "ফেয়ারট্রেড", "plug": "প্লাগ", "kickstand": "কিকস্ট্যান্ড",
    "england": "ইংল্যান্ড", "turkey": "টার্কি", "mandala": "মান্ডালা",
    "component": "কম্পোনেন্ট", "cord": "কর্ড", "over": "ওভার",
    "ear": "ইয়ার", "handcart": "হ্যান্ডকার্ট", "extendable": "এক্সটেন্ডেবল",
    "filters": "ফিল্টার", "lamb": "ল্যাম্ব", "refillable": "রিফিলেবল",
    "arendale": "অ্যারেন্ডেল", "swiveling": "সুইভেলিং",
    "transport": "ট্রান্সপোর্ট", "suction": "সাকশন",
    "amazonbasics": "AmazonBasics", "microwave": "মাইক্রোওয়েভ",
    "bedroom": "বেডরুম", "turquoise": "টারকোয়েজ", "blk": "ব্ল্যাক",
    "sided": "সাইডেড", "performance": "পারফরম্যান্স", "volt": "ভোল্ট",
    "weightlifting": "ওয়েটলিফটিং", "the": "দ্য", "in-a-row": "ইন-এ-রো",
    "dry-erase": "ড্রাই-ইরেজ", "sheet": "শিট", "sheets": "শিট",
    "weather": "ওয়েদার", "micro": "মাইক্রো", "one": "ওয়ান",
    "fatigue": "ফ্যাটিগ", "charged": "চার্জড", "pre": "প্রি",
    "coconut": "নারকেল", "olive": "অলিভ", "fruit": "ফল", "ipad": "আইপ্যাড",
    "mic": "মাইক", "protective": "প্রোটেক্টিভ", "switch": "সুইচ",
    "monitor": "মনিটর", "coin": "কয়েন", "xbox": "এক্সবক্স",
    "sleeve": "স্লিভ", "italian": "ইতালিয়ান", "safety": "সেফটি",
    "poly": "পলি", "shaker": "শেকার", "clamshell": "ক্ল্যামশেল",
    "drainage": "ড্রেনেজ", "ramp": "র‍্যাম্প", "soup": "স্যুপ",
    "expandable": "এক্সপ্যান্ডেবল", "butter": "বাটার", "pike": "পাইক",
    "lids": "ঢাকনা", "rod": "রড", "pepper": "গোলমরিচ", "gift": "গিফট",
    "corn": "ভুট্টা", "baseball": "বেসবল", "interlocking": "ইন্টারলকিং",
    "grain": "শস্য", "gymnastics": "জিমন্যাস্টিকস", "medicine": "ওষুধ",
    "handles": "হ্যান্ডেল", "lifting": "লিফটিং", "jump": "জাম্প",
    "workout": "ওয়ার্কআউট", "goal": "গোল", "lock": "লক",
    "curtains": "পর্দা", "comforter": "কমফর্টার", "height": "হাইট",
    "cube": "কিউব", "egyptian": "মিশরীয়", "runner": "রানার",
    "fixture": "ফিক্সচার", "blackout": "ব্ল্যাকআউট", "heather": "হিদার",
    "equivalent": "ইকুইভ্যালেন্ট", "percent": "পার্সেন্ট", "decor": "ডেকর",
    "stackable": "স্ট্যাকেবল", "frosted": "ফ্রস্টেড", "two": "টু",
    "chilli": "মরিচ", "subject": "সাবজেক্ট", "tins": "টিন",
    "puppet": "পাপেট", "fox": "ফক্স", "rabbit": "খরগোশ",
    "backyard": "ব্যাকইয়ার্ড", "rainbow": "রেইনবো", "pastel": "প্যাস্টেল",
    "pcs": "পিস", "bichon": "বিশন", "cooling": "কুলিং",
    "activity": "অ্যাক্টিভিটি", "level": "লেভেল", "salmon": "স্যামন",
    "sweet": "মিষ্টি", "cave": "কেভ", "beef": "বিফ", "animal": "প্রাণী",
    "pencils": "পেন্সিল", "laminator": "ল্যামিনেটর",
    "correction": "কারেকশন", "trail": "ট্রেইল", "flavored": "ফ্লেভারড",
    "allegro": "অ্যালেগ্রো", "vanilla": "ভ্যানিলা", "original": "অরিজিনাল",
    "chunks": "চাংকস", "devices": "ডিভাইস", "extension": "এক্সটেনশন",
    "chronograph": "ক্রোনোগ্রাফ", "resin": "রেজিন", "dynamic": "ডায়নামিক",
    "privacy": "প্রাইভেসি", "screen": "স্ক্রিন", "male": "মেল",
    "resistant": "রেজিস্ট্যান্ট", "wrist": "রিস্ট", "vertical": "ভার্টিকাল",
    "desktop": "ডেস্কটপ", "sports": "স্পোর্টস", "jack": "জ্যাক",
    "shelving": "শেলভিং", "tomato": "টমেটো", "dinnerware": "ডিনারওয়্যার",
    "dust": "ডাস্ট", "odour": "গন্ধ", "containers": "কন্টেইনার",
    "hammered": "হ্যামারড", "lead": "লিড", "modular": "মডুলার",
    "tiles": "টাইলস", "jug": "জগ", "practice": "প্র্যাকটিস",
    "volleyball": "ভলিবল", "durable": "টেকসই", "camping": "ক্যাম্পিং",
    "canopy": "ক্যানোপি", "junior": "জুনিয়র", "pool": "পুল",
    "pilates": "পিলাটিস", "loop": "লুপ", "pull": "পুল", "cast": "কাস্ট",
    "equipment": "ইকুইপমেন্ট", "hood": "হুড", "layer": "লেয়ার",
    "topping": "টপিং", "ladder": "মই", "grips": "গ্রিপ", "memory": "মেমোরি",
    "raised": "রেইজড", "ice": "আইস", "camano": "কামানো", "bonded": "বন্ডেড",
    "thread": "থ্রেড", "percale": "পারকেল", "edgewest": "এজওয়েস্ট",
    "global": "গ্লোবাল", "luxury": "লাক্সারি", "curved": "কার্ভড",
    "rectangular": "আয়তাকার", "engineered": "ইঞ্জিনিয়ারড",
    "pockets": "পকেট", "sorter": "সর্টার", "narrow": "ন্যারো",
    "astonica": "অ্যাস্টোনিকা", "gas": "গ্যাস", "patina": "প্যাটিনা",
    "hammock": "হ্যামক", "barbecue": "বারবিকিউ", "dried": "শুকনো",
    "purpose": "পারপাস", "message": "মেসেজ", "instant": "ইনস্ট্যান্ট",
    "playpen": "প্লেপেন", "puppies": "কুকুরছানা", "lifelong": "লাইফলং",
    "waste": "ওয়েস্ট", "shredded": "শ্রেডেড", "american": "আমেরিকান",
    "spiral": "স্পাইরাল", "snack": "স্ন্যাক", "frozen": "ফ্রোজেন",
    "pizza": "পিৎজা", "urad": "উরাদ", "virgin": "ভার্জিন",
    "cheddar": "চেডার", "cranberry": "ক্র্যানবেরি", "seasoning": "সিজনিং",
    "gan": "GaN", "lash": "ল্যাশ", "rex": "রেক্স", "port": "পোর্ট",
})
LEX_BN.update({"sheet": "শিট", "sheets": "শিট"})

_BN_VOWELS_IND = {"a": "অ", "e": "এ", "i": "ই", "o": "ও", "u": "উ",
                  "aa": "আ", "ee": "ঈ", "oo": "উ", "ai": "আই",
                  "au": "অ", "ea": "ঈ", "ou": "আউ", "ay": "ে",
                  "aw": "অ", "ow": "াও"}
_BN_MATRA = {"a": "া", "e": "ে", "i": "ি", "o": "ো", "u": "ু",
             "aa": "া", "ee": "ী", "oo": "ু", "ai": "াই", "au": "",
             "ea": "ী", "ou": "াউ", "ay": "ে", "aw": "", "ow": "াও"}
_BN_CONS = {"b": "ব", "c": "ক", "d": "ড", "f": "ফ", "g": "গ",
            "h": "হ", "j": "জ", "k": "ক", "l": "ল", "m": "ম",
            "n": "ন", "p": "প", "q": "ক", "r": "র", "s": "স",
            "t": "ট", "v": "ভ", "w": "ওয়", "x": "ক্স", "y": "য়",
            "z": "জ", "ch": "চ", "sh": "শ", "th": "থ", "ph": "ফ",
            "wh": "ওয়", "ck": "ক", "gh": "ঘ", "kh": "খ",
            "bh": "ভ", "dh": "ধ", "qu": "কোয়"}


def _phonology(w):
    w = re.sub(r"ation$", "eshan", w)
    w = re.sub(r"[st]ion$", "shan", w)
    w = re.sub(r"ture$", "char", w)
    w = re.sub(r"([bcdfghjklmnpqrstvwxz])le$", r"\1al", w)
    w = re.sub(r"a([bcdfghjklmnpqrstvwxz])e$", r"e\1", w)
    w = re.sub(r"i([bcdfghjklmnpqrstvwxz])e$", r"ai\1", w)
    w = re.sub(r"o([bcdfghjklmnpqrstvwxz])e$", r"o\1", w)
    w = re.sub(r"u([bcdfghjklmnpqrstvwxz])e$", r"oo\1", w)
    w = re.sub(r"ce$", "s", w)
    w = re.sub(r"c([eiy])", r"s\1", w)
    w = re.sub(r"er$", "ar", w)
    w = re.sub(r"ow$", "o", w)
    w = re.sub(r"y$", "ee", w)
    w = re.sub(r"^u", "a", w)
    w = re.sub(r"(.)\1", r"\1", w)
    return w


def _bn_translit(word):
    w = _phonology(word.lower())
    units, i = [], 0
    keys2 = {k for k in list(_BN_CONS) + list(_BN_MATRA) if len(k) == 2}
    while i < len(w):
        pair = w[i:i + 2]
        if pair in keys2:
            units.append(pair)
            i += 2
        else:
            units.append(w[i])
            i += 1
    out, prev_cons = [], False
    for u in units:
        if u in _BN_CONS:
            if prev_cons:
                out.append("্")
            out.append(_BN_CONS[u])
            prev_cons = True
        elif u in _BN_MATRA:
            if prev_cons:
                if u != "a":
                    out.append(_BN_MATRA[u])
            else:
                out.append(_BN_VOWELS_IND.get(u, u))
            prev_cons = False
        else:
            out.append(u)
            prev_cons = False
    return "".join(out)


def _bn_word(word):
    lw = word.lower()
    if _brand_caps(word, EXC_BN):
        return word
    if lw in LEX_BN:
        return LEX_BN[lw]
    if lw in EXC_BN:
        return EXC_BN[lw]
    if not re.search(r"[a-zA-Z]", word):
        return word
    if word.isupper() and len(word) >= 2:
        return word
    if len(lw) <= 2 and lw not in ("tv",):
        return word
    return _bn_translit(word)


LEX_UR = {
    "with": "کے ساتھ", "and": "اور", "for": "کے لیے", "of": "کا",
    "to": "سے", "set": "سیٹ", "pack": "پیک", "piece": "پیس",
    "pieces": "پیس", "size": "سائز", "in": "ان", "per": "فی",
    "inch": "انچ", "inches": "انچ", "cm": "سینٹی میٹر", "mm": "ملی میٹر",
    "ft": "فٹ", "feet": "فٹ", "foot": "فٹ", "kg": "کلوگرام", "g": "گرام",
    "ml": "ملی لیٹر", "l": "لیٹر", "oz": "اونس", "litre": "لیٹر",
    "liter": "لیٹر", "gram": "گرام", "meter": "میٹر", "metre": "میٹر",
    "black": "کالا", "white": "سفید", "red": "سرخ", "blue": "نیلا",
    "green": "سبز", "yellow": "پیلا", "brown": "بھورا",
    "grey": "سرمئی", "gray": "سرمئی", "pink": "گلابی",
    "orange": "نارنجی", "purple": "جامنی", "silver": "چاندی",
    "golden": "سنہری", "gold": "گولڈ", "beige": "بیج",
    "ivory": "ہاتھی دانت", "navy": "نیوی", "multicolour": "کثیر رنگ",
    "multicolor": "کثیر رنگ", "dark": "گہرا", "light": "ہلکا",
    "natural": "قدرتی", "clear": "شفاف",
    "steel": "اسٹیل", "stainless": "اسٹین لیس", "wood": "لکڑی",
    "wooden": "لکڑی کا", "glass": "شیشہ", "plastic": "پلاسٹک",
    "cotton": "سوتی", "leather": "چمڑا", "metal": "دھات",
    "ceramic": "سیرامک", "bamboo": "بانس", "silk": "ریشمی",
    "wool": "اونی", "rubber": "ربڑ", "paper": "کاغذ",
    "iron": "لوہا", "brass": "پیتل", "copper": "تانبا",
    "marble": "سنگ مرمر", "fabric": "کپڑا", "velvet": "مخمل",
    "linen": "لینن",
    "chair": "کرسی", "table": "میز", "lamp": "لیمپ", "bed": "پلنگ",
    "pillow": "تکیہ", "cushion": "گدی", "blanket": "کمبل",
    "sheet": "چادر", "sheets": "چادریں", "towel": "تولیہ",
    "curtain": "پردہ", "rug": "قالینچہ", "carpet": "قالین",
    "shelf": "شیلف", "mirror": "آئینہ", "clock": "گھڑی",
    "watch": "گھڑی", "bottle": "بوتل", "cup": "کپ", "mug": "مگ",
    "plate": "پلیٹ", "plates": "پلیٹیں", "bowl": "پیالہ",
    "spoon": "چمچ", "knife": "چاقو", "pan": "کڑاہی",
    "pot": "برتن", "jar": "مرتبان", "tray": "ٹرے", "box": "ڈبہ",
    "bag": "تھیلا", "basket": "ٹوکری", "brush": "برش",
    "soap": "صابن", "oil": "تیل", "tea": "چائے", "coffee": "کافی",
    "sugar": "چینی", "salt": "نمک", "rice": "چاول", "flour": "آٹا",
    "honey": "شہد", "spice": "مصالحہ", "spices": "مصالحے",
    "nuts": "میوے", "seeds": "بیج", "dog": "کتا", "cat": "بلی",
    "pet": "پالتو", "bird": "پرندہ", "fish": "مچھلی",
    "toy": "کھلونا", "toys": "کھلونے", "game": "کھیل",
    "ball": "گیند", "doll": "گڑیا", "book": "کتاب", "pen": "قلم",
    "pencil": "پنسل", "notebook": "نوٹ بک", "chart": "چارٹ",
    "card": "کارڈ", "cards": "کارڈ", "plant": "پودا",
    "plants": "پودے", "flower": "پھول", "garden": "باغ",
    "seed": "بیج", "shoes": "جوتے", "shoe": "جوتا",
    "socks": "موزے", "shirt": "قمیض", "cover": "کور",
    "case": "کیس", "stand": "اسٹینڈ", "holder": "ہولڈر",
    "organizer": "آرگنائزر", "organiser": "آرگنائزر",
    "cleaner": "کلینر", "filter": "فلٹر", "charger": "چارجر",
    "cable": "کیبل", "battery": "بیٹری", "batteries": "بیٹریاں",
    "bulb": "بلب", "candle": "موم بتی", "frame": "فریم",
    "wall": "دیوار", "door": "دروازہ", "window": "کھڑکی",
    "kitchen": "باورچی خانہ", "office": "دفتر", "home": "گھر",
    "baby": "شیرخوار", "kids": "بچوں کا", "men": "مردوں کا",
    "women": "خواتین کا",
    "large": "بڑا", "small": "چھوٹا", "big": "بڑا", "mini": "منی",
    "new": "نیا", "soft": "نرم", "hard": "سخت", "round": "گول",
    "square": "چوکور", "fresh": "تازہ", "dry": "خشک",
    "organic": "نامیاتی", "premium": "پریمیم", "classic": "کلاسک",
    "modern": "جدید", "portable": "پورٹیبل",
    "foldable": "تہہ ہونے والا", "adjustable": "قابلِ ترتیب",
    "waterproof": "واٹر پروف", "rechargeable": "ری چارج ایبل",
    "wireless": "وائرلیس", "whole": "ثابت", "pure": "خالص",
    "double": "ڈبل", "single": "سنگل", "twin": "ٹوئن",
    "king": "کنگ", "queen": "کوئین", "extra": "ایکسٹرا",
    "heavy": "بھاری", "duty": "ڈیوٹی", "free": "فری",
    "anti": "اینٹی", "non": "نان", "multi": "ملٹی",
    "board": "بورڈ", "high": "ہائی", "cut": "کٹ",
    "compact": "کومپیکٹ", "family": "فیملی", "tree": "درخت",
    "outdoor": "آؤٹ ڈور", "weight": "وزن", "foam": "فوم",
    "kit": "کٹ", "mesh": "جالی", "storage": "اسٹوریج",
    "travel": "سفری", "chicken": "چکن", "strap": "پٹا",
    "bar": "بار", "folding": "فولڈنگ", "dining": "ڈائننگ",
    "port": "پورٹ", "tier": "منزلہ", "collection": "کلیکشن",
    "tower": "ٹاور", "furniture": "فرنیچر", "binder": "بائنڈر",
    "credit": "کریڈٹ", "aluminum": "المونیم",
    "aluminium": "المونیم", "stick": "اسٹک", "glasses": "گلاس",
    "seat": "سیٹ", "basic": "بنیادی", "lid": "ڈھکن",
    "bags": "تھیلے", "standing": "اسٹینڈنگ", "water": "واٹر",
    "food": "فوڈ", "mix": "مکس", "low": "لو", "mat": "میٹ",
    "pad": "پیڈ", "mid": "مڈ", "cross": "کراس", "amazon": "ایمیزون",
    "patio": "پیٹیو", "shredder": "شریڈر", "erase": "مٹانے کا",
    "scratching": "کھرچنے کا",
}

EXC_UR = {
    "mouse": "ماؤس", "keyboard": "کی بورڈ", "usb": "یو ایس بی",
    "led": "ایل ای ڈی", "hdmi": "ایچ ڈی ایم آئی",
    "wifi": "وائی فائی", "bluetooth": "بلوٹوتھ",
    "headphones": "ہیڈفون", "headphone": "ہیڈفون",
    "earphones": "ایئرفون", "speaker": "اسپیکر",
    "speakers": "اسپیکر", "camera": "کیمرہ", "tripod": "ترپائی",
    "microphone": "مائیکروفون", "laptop": "لیپ ٹاپ",
    "tablet": "ٹیبلٹ", "phone": "فون", "gaming": "گیمنگ",
    "yoga": "یوگا", "dumbbell": "ڈمبل", "kettlebell": "کیٹل بیل",
    "cricket": "کرکٹ", "football": "فٹ بال",
    "basketball": "باسکٹ بال", "badminton": "بیڈمنٹن",
    "tennis": "ٹینس", "gym": "جم", "fitness": "فٹنس",
    "exercise": "ورزش", "resistance": "ریزسٹنس", "band": "بینڈ",
    "bands": "بینڈ", "sofa": "صوفہ", "mattress": "گدا",
    "recliner": "ریکلائنر", "ottoman": "اوٹومن", "stool": "اسٹول",
    "desk": "ڈیسک", "drawer": "دراز", "wardrobe": "الماری",
    "bookshelf": "بک شیلف", "planter": "گملا", "vase": "گلدان",
    "skillet": "اسکیلیٹ", "griddle": "توا", "cooker": "کوکر",
    "blender": "بلینڈر", "mixer": "مکسر", "grinder": "گرائنڈر",
    "toaster": "ٹوسٹر", "kettle": "کیتلی", "thermos": "تھرماس",
    "lunch": "لنچ", "dinner": "ڈنر", "chocolate": "چاکلیٹ",
    "cookies": "کوکیز", "biscuit": "بسکٹ", "biscuits": "بسکٹ",
    "juice": "جوس", "masala": "مصالحہ", "leash": "پٹہ",
    "collar": "کالر", "harness": "ہارنس",
    "aquarium": "ایکویریم", "shampoo": "شیمپو",
    "grooming": "گرومنگ", "treats": "ٹریٹس", "puzzle": "پزل",
    "blocks": "بلاکس", "teddy": "ٹیڈی", "bear": "بھالو",
    "marker": "مارکر", "markers": "مارکر", "stapler": "اسٹیپلر",
    "folder": "فولڈر", "files": "فائلیں", "file": "فائل",
    "envelope": "لفافہ", "envelopes": "لفافے", "diary": "ڈائری",
    "planner": "پلانر", "calculator": "کیلکولیٹر",
    "printer": "پرنٹر", "adapter": "اڈاپٹر", "charging": "چارجنگ",
    "power": "پاور", "wire": "تار", "remote": "ریموٹ",
    "security": "سیکیورٹی", "sensor": "سینسر", "alarm": "الارم",
    "digital": "ڈیجیٹل", "electric": "الیکٹرک",
    "electronic": "الیکٹرانک", "automatic": "خودکار",
    "manual": "مینوئل", "type": "ٹائپ", "wide": "وائڈ",
    "ruled": "رولڈ", "composition": "کمپوزیشن",
    "playstation": "پلے اسٹیشن", "controller": "کنٹرولر",
    "century": "سنچری", "customizable": "کسٹمائز ایبل",
    "daybed": "ڈے بیڈ", "sauce": "ساس", "marinara": "مارینارا",
    "sodium": "سوڈیم", "balance": "بیلنس", "pump": "پمپ",
    "singles": "سنگلز", "flute": "فلوٹ", "swirl": "سورل",
    "uptown": "اپ ٹاؤن", "essentials": "ایسنشلز",
    "silicone": "سلیکون", "tufted": "ٹفٹڈ",
    "strathwood": "اسٹریتھ وڈ", "vedaka": "ویداکا",
    "drink": "ڈرنک", "business": "بزنس", "gummed": "گمڈ",
}

_UR_EXTRA = {
    "paws": "پاز", "umbrella": "چھتری", "alkaline": "الکلائن",
    "industrial": "انڈسٹریل", "copy": "کاپی", "cheese": "چیز",
    "print": "پرنٹ", "zip": "زپ", "wild": "وائلڈ",
    "accessories": "ایکسیسریز", "grill": "گرل", "long": "لمبا",
    "heater": "ہیٹر", "contemporary": "کنٹیمپریری", "tape": "ٹیپ",
    "cage": "پنجرہ", "onez": "ونز", "base": "بیس",
    "multipurpose": "کثیر المقاصد", "thick": "موٹا", "area": "ایریا",
    "sectional": "سیکشنل", "farmhouse": "فارم ہاؤس", "bright": "روشن",
    "amazonfresh": "ایمیزون فریش", "mount": "ماؤنٹ", "computer": "کمپیوٹر",
    "traditional": "روایتی", "wine": "وائن", "old": "پرانا",
    "stoneware": "اسٹون ویئر", "cast": "کاسٹ", "solid": "سالڈ",
    "symactive": "سِم ایکٹو", "sya": "سیا", "belfit": "بیل فٹ",
    "hanging": "لٹکنے والا", "post": "پوسٹ", "cream": "کریم",
    "dogs": "کتوں", "lithium": "لیتھیم", "magnetic": "میگنیٹک",
    "rack": "ریک", "drinkware": "ڈرنک ویئر", "room": "روم",
    "essential": "ایسنشل", "wicker": "بید", "accent": "ایکسنٹ",
    "panel": "پینل", "ground": "گراؤنڈ", "medium": "میڈیم",
    "recycled": "ری سائیکلڈ", "slime": "سلائم", "edition": "ایڈیشن",
    "universal": "یونیورسل", "everyday": "ایوری ڈے", "cell": "سیل",
    "lightweight": "ہلکا", "grip": "گرپ", "hand": "ہینڈ",
    "easel": "ایزل", "powder": "پاؤڈر", "container": "کنٹینر",
    "hot": "ہاٹ", "feeder": "فیڈر", "thermal": "تھرمل", "pound": "پاؤنڈ",
    "market": "مارکیٹ", "all": "آل", "weather": "ویدر",
    "headboard": "ہیڈ بورڈ", "canvas": "کینوس", "tiger": "ٹائیگر",
    "cats": "بلیوں", "apple": "ایپل", "watt": "واٹ", "carrying": "کیرینگ",
    "floor": "فلور", "platform": "پلیٹ فارم", "duvet": "ڈوویٹ",
    "art": "آرٹ", "side": "سائیڈ", "decorative": "آرائشی",
    "color": "کلر", "colour": "کلر", "carrier": "کیریئر", "legal": "لیگل",
    "putty": "پٹی", "brake": "بریک", "crate": "کریٹ", "roast": "روسٹ",
    "car": "کار", "fire": "فائر", "or": "یا", "vinyl": "وینائل",
    "compostable": "کمپوسٹ ایبل", "fashioned": "فیشنڈ", "combo": "کومبو",
    "sandwich": "سینڈوچ", "hose": "ہوز", "backpack": "بیک پیک",
    "training": "ٹریننگ", "ring": "رنگ", "top": "ٹاپ",
    "hardwood": "ہارڈ ووڈ", "rustic": "رسٹک", "whiteboard": "وائٹ بورڈ",
    "unicorn": "یونیکورن", "lash": "لیش", "ears": "کان", "paint": "پینٹ",
    "elevated": "اونچا", "recipe": "ریسیپی", "popular": "مقبول",
    "roasted": "روسٹڈ", "ergonomic": "ارگونومک", "vintage": "ونٹیج",
    "cookware": "کک ویئر", "disposable": "ڈسپوزیبل", "salad": "سلاد",
    "swivel": "سوئیول", "net": "نیٹ", "golf": "گولف", "foot": "فٹ",
    "indoor": "انڈور", "bolster": "بولسٹر", "casual": "کیژول",
    "plush": "پلش", "loveseat": "لو سیٹ", "nailhead": "نیل ہیڈ",
    "geometric": "جیومیٹرک", "pendant": "پینڈنٹ", "open": "اوپن",
    "trim": "ٹرم", "grid": "گرڈ", "lounge": "لاؤنج", "finish": "فنش",
    "basics": "بیسکس", "pit": "پٹ", "litter": "لٹر", "dal": "دال",
    "micro": "مائیکرو", "ceiling": "سیلنگ", "headset": "ہیڈسیٹ",
    "style": "اسٹائل", "flat": "فلیٹ", "height": "ہائٹ", "deep": "ڈیپ",
    "handle": "ہینڈل", "vacuum": "ویکیوم", "serving": "سرونگ",
    "insulated": "انسولیٹڈ", "pads": "پیڈز", "fatigue": "فٹیگ",
    "sided": "سائیڈڈ", "tool": "ٹول", "pasta": "پاستا", "party": "پارٹی",
    "coolers": "کولر", "replacement": "ری پلیسمنٹ", "by": "بائے",
    "belt": "بیلٹ", "pocket": "پاکٹ", "on": "آن", "chairs": "کرسیاں",
    "swatch": "سواچ", "sateen": "سیٹین", "end": "اینڈ", "living": "لیونگ",
    "sconce": "اسکونس", "upholstered": "اپہولسٹرڈ", "sisal": "سیسل",
    "primary": "پرائمری", "presentation": "پریزنٹیشن", "adult": "ایڈلٹ",
    "washable": "دھونے کے قابل", "dividers": "ڈیوائیڈر", "letter": "لیٹر",
    "dual": "ڈوئل", "control": "کنٹرول", "capacity": "کیپیسٹی",
    "displayport": "ڈسپلے پورٹ", "bundle": "بنڈل", "clip": "کلپ",
    "neoprene": "نیوپرین", "full": "فل", "bean": "بین",
    "pressure": "پریشر", "pods": "پوڈز", "cups": "کپ", "cooler": "کولر",
    "ounce": "اونس", "street": "اسٹریٹ", "bowls": "پیالے",
    "dispenser": "ڈسپنسر", "potato": "آلو", "milk": "دودھ",
    "glitter": "گلٹر", "dumbbells": "ڈمبلز", "french": "فرینچ",
    "padded": "پیڈڈ", "rope": "رسی", "space": "اسپیس", "pouch": "پاؤچ",
    "quality": "کوالٹی", "density": "ڈینسٹی", "soccer": "ساکر",
    "stripe": "اسٹرائپ", "printed": "پرنٹڈ", "counter": "کاؤنٹر",
    "arm": "آرم", "reversible": "ریورسیبل", "legs": "لیگز", "back": "بیک",
    "lounger": "لاؤنجر", "throw": "تھرو", "chandelier": "فانوس",
    "photo": "فوٹو", "journal": "جرنل", "wirebound": "وائر باؤنڈ",
    "house": "ہاؤس", "puppy": "پپی", "condo": "کونڈو", "kennel": "کینل",
    "kitten": "کٹن", "peanut": "مونگ پھلی", "glue": "گوند", "tab": "ٹیب",
    "adhesive": "چپکنے والا", "permanent": "پرماننٹ", "beans": "بینز",
    "android": "اینڈرائیڈ", "ear": "ایئر", "pre": "پری", "charged": "چارجڈ",
    "display": "ڈسپلے", "wired": "وائرڈ", "nintendo": "نینٹینڈو",
    "station": "اسٹیشن", "play": "پلے", "mobile": "موبائل",
    "iphone": "آئی فون", "gel": "جیل", "easy": "ایزی", "one": "ون",
    "collapsible": "فولڈ ایبل", "anodized": "اینوڈائزڈ", "gloves": "دستانے",
    "tritan": "ٹرائٹن", "drinking": "ڈرنکنگ", "compartment": "کمپارٹمنٹ",
    "blend": "بلینڈ", "stemless": "اسٹیم لیس", "meal": "میل",
    "block": "بلاک", "stitched": "سلا ہوا", "gear": "گیئر", "step": "اسٹیپ",
    "picnic": "پکنک", "barbell": "باربیل", "framed": "فریمڈ",
    "microfiber": "مائیکرو فائبر", "microfibre": "مائیکرو فائبر",
    "shag": "شیگ", "oversized": "اوور سائزڈ", "fitted": "فٹڈ",
    "stone": "پتھر", "couch": "کاؤچ", "made": "میڈ", "bath": "باتھ",
    "college": "کالج", "chaise": "شیز", "bistro": "بسٹرو",
    "rattan": "رتن", "falkner": "فاکنر", "lights": "لائٹس", "can": "کین",
    "week": "ہفتہ", "copier": "کاپیئر", "compatible": "کمپیٹیبل",
    "tin": "ٹن", "eye": "آئی", "trouncer": "ٹراؤنسر", "rex": "ریکس",
    "penguin": "پینگوئن", "eyes": "آنکھیں", "ash": "ایش", "stamp": "اسٹیمپ",
    "painter": "پینٹر", "posts": "پوسٹ", "jerky": "جرکی",
    "liquid": "لیکوئڈ", "pens": "پین", "chips": "چپس", "split": "اسپلٹ",
    "lightning": "لائٹننگ", "connector": "کنیکٹر", "commercial": "کمرشل",
    "bradford": "بریڈفورڈ", "armless": "آرم لیس", "polyester": "پالیسٹر",
    "ready": "ریڈی", "foods": "فوڈز", "cobb": "کوب", "reprint": "ری پرنٹ",
    "sailing": "سیلنگ", "ship": "شپ", "patent": "پیٹنٹ",
    "metallic": "میٹالک", "ink": "انک", "keychain": "کی چین",
    "peeler": "پیلر", "roller": "رولر", "wiper": "وائپر",
    "tumbler": "ٹمبلر", "bench": "بینچ", "cabinet": "کیبنٹ",
    "hanger": "ہینگر", "hangers": "ہینگر", "scale": "اسکیل",
    "timer": "ٹائمر", "opener": "اوپنر", "strainer": "چھلنی",
    "whisk": "وِسک", "spatula": "اسپیچولا", "ladle": "کفگیر",
    "tongs": "چمٹا", "grater": "گریٹر", "colander": "چھلنی",
    "apron": "ایپرن", "napkins": "نیپکن", "napkin": "نیپکن",
    "sponge": "اسپنج", "sponges": "اسپنج", "trash": "ٹریش",
    "garbage": "کچرا", "laundry": "لانڈری", "hamper": "ہیمپر",
    "shower": "شاور", "toilet": "ٹوائلٹ", "sink": "سنک", "faucet": "نل",
    "spray": "اسپرے", "sprayer": "اسپریئر", "watering": "واٹرنگ",
    "nozzle": "نوزل", "shovel": "بیلچہ", "rake": "ریک", "pruner": "پرونر",
    "pruning": "پروننگ", "shears": "قینچی", "scissors": "قینچی",
    "gnome": "نوم", "fountain": "فوارہ", "solar": "سولر",
    "lantern": "لالٹین", "string": "اسٹرنگ", "fairy": "فیری",
    "bulbs": "بلب", "chew": "چیو", "squeaky": "اسکویکی", "bone": "ہڈی",
    "kibble": "کبل", "bed": "بیڈ", "beds": "بیڈ", "litterbox": "لٹر باکس",
    "scratcher": "اسکریچر", "perch": "پرچ", "hutch": "ہچ",
    "terrarium": "ٹیریریم", "hamster": "ہیمسٹر", "rabbit": "خرگوش",
    "wheel": "پہیہ", "bell": "گھنٹی", "action": "ایکشن", "figure": "فگر",
    "figures": "فگر", "building": "بلڈنگ", "bricks": "برکس",
    "craft": "کرافٹ", "crayons": "کریون", "coloring": "کلرنگ",
    "colouring": "کلرنگ", "sticker": "اسٹیکر", "stickers": "اسٹیکر",
    "playset": "پلے سیٹ", "racing": "ریسنگ", "dinosaur": "ڈائنوسار",
    "robot": "روبوٹ", "kite": "پتنگ", "bubble": "ببل", "bubbles": "ببل",
    "chalk": "چاک", "paperback": "پیپر بیک", "hardcover": "ہارڈ کور",
    "novel": "ناول", "cookbook": "کک بک", "guide": "گائیڈ",
    "atlas": "اٹلس", "dictionary": "لغت", "sketchbook": "اسکیچ بک",
    "highlighter": "ہائی لائٹر", "highlighters": "ہائی لائٹر",
    "eraser": "ربڑ", "ruler": "اسکیل", "clips": "کلپ", "staples": "اسٹیپل",
    "labels": "لیبل", "label": "لیبل", "index": "انڈیکس", "sticky": "اسٹکی",
    "notes": "نوٹس", "notepad": "نوٹ پیڈ", "notepads": "نوٹ پیڈ",
    "clipboard": "کلپ بورڈ", "lamination": "لیمینیشن",
    "laminating": "لیمینیٹنگ", "pouches": "پاؤچ", "toner": "ٹونر",
    "cartridge": "کارٹریج", "ream": "ریم", "sheets": "شیٹ", "sheet": "شیٹ",
    "machine": "مشین", "handi": "ہانڈی", "roti": "روٹی", "tawa": "توا",
    "chowder": "چاؤڈر", "clam": "کلیم", "spoons": "چمچ", "forks": "کانٹے",
    "fork": "کانٹا", "knives": "چھریاں", "cutlery": "کٹلری",
    "kadai": "کڑاہی", "idli": "اڈلی", "dosa": "ڈوسا", "chapati": "چپاتی",
    "quilt": "رضائی", "bedsheet": "بیڈ شیٹ", "pillowcase": "تکیے کا غلاف",
    "mixing": "مکسنگ", "baking": "بیکنگ", "cake": "کیک", "macbook": "میک بک",
}
for _k, _v in _UR_EXTRA.items():
    EXC_UR.setdefault(_k, _v)

_UR_CONS = {"b": "ب", "c": "ک", "d": "ڈ", "f": "ف", "g": "گ",
            "h": "ہ", "j": "ج", "k": "ک", "l": "ل", "m": "م",
            "n": "ن", "p": "پ", "q": "ک", "r": "ر", "s": "س",
            "t": "ٹ", "v": "و", "w": "و", "x": "کس", "y": "ی",
            "z": "ز", "ch": "چ", "sh": "ش", "th": "تھ", "ph": "ف",
            "wh": "و", "ck": "ک", "gh": "گھ", "kh": "کھ",
            "bh": "بھ", "dh": "دھ", "qu": "کو"}
_UR_VOWEL_MED = {"a": "ی", "e": "ی", "i": "", "o": "ا", "u": "",
                 "aa": "ا", "ee": "ی", "oo": "و", "ai": "ائ",
                 "au": "ا", "ea": "ی", "ou": "اؤ", "ay": "ے",
                 "aw": "ا", "ow": "و"}
_UR_VOWEL_INIT = {"a": "ا", "e": "ای", "i": "ا", "o": "او", "u": "ا",
                  "aa": "آ", "ee": "ای", "oo": "او", "ai": "آئ",
                  "au": "آ", "ea": "ای", "ou": "آؤ", "ay": "اے",
                  "aw": "آ", "ow": "او"}


def _ur_translit(word):
    w = _phonology(word.lower())
    w = re.sub(r"a(r)", r"aa\1", w)
    w = re.sub(r"o(r)", r"aa\1", w)
    units, i = [], 0
    keys2 = {k for k in list(_UR_CONS) + list(_UR_VOWEL_MED)
             if len(k) == 2}
    while i < len(w):
        pair = w[i:i + 2]
        if pair in keys2:
            units.append(pair)
            i += 2
        else:
            units.append(w[i])
            i += 1
    out = []
    for j, u in enumerate(units):
        if u in _UR_CONS:
            out.append(_UR_CONS[u])
        elif u in _UR_VOWEL_MED:
            if j == 0:
                out.append(_UR_VOWEL_INIT[u])
            elif j == len(units) - 1 and u in ("a", "e"):
                out.append("ہ" if u == "a" else "ی")
            else:
                out.append(_UR_VOWEL_MED[u])
        else:
            out.append(u)
    s = "".join(out)
    if re.match(r"^s[bcdfghjklmnpqrstvwxz]", w):
        s = "ا" + s
    return s


def _ur_word(word):
    lw = word.lower()
    if _brand_caps(word, EXC_UR):
        return word
    if lw in LEX_UR:
        return LEX_UR[lw]
    if lw in EXC_UR:
        return EXC_UR[lw]
    if not re.search(r"[a-zA-Z]", word):
        return word
    if word.isupper() and len(word) >= 2:
        return word
    if len(lw) <= 2 and lw not in ("tv",):
        return word
    return _ur_translit(word)


LEX_AM = {
    "with": "በ", "and": "እና", "for": "ለ", "of": "የ",
    "to": "ወደ", "set": "ስብስብ", "pack": "ፓክ", "piece": "ቁራጭ",
    "pieces": "ቁርጥራጮች", "size": "መጠን", "in": "ኢን", "per": "በአንድ",
    "inch": "ኢንች", "inches": "ኢንች", "cm": "ሴሜ", "mm": "ሚሜ",
    "ft": "ጫማ", "feet": "ጫማ", "foot": "እግር", "kg": "ኪግ",
    "g": "ግራም", "ml": "ሚሊ", "l": "ሊትር", "oz": "አውንስ",
    "litre": "ሊትር", "liter": "ሊትር", "gram": "ግራም",
    "meter": "ሜትር", "metre": "ሜትር",
    "black": "ጥቁር", "white": "ነጭ", "red": "ቀይ", "blue": "ሰማያዊ",
    "green": "አረንጓዴ", "yellow": "ቢጫ", "brown": "ቡናማ",
    "grey": "ግራጫ", "gray": "ግራጫ", "pink": "ሮዝ",
    "orange": "ብርቱካናማ", "purple": "ሐምራዊ", "silver": "ብር",
    "golden": "ወርቃማ", "gold": "ወርቅ", "beige": "ቤዥ",
    "ivory": "የዝሆን ጥርስ", "navy": "ጥቁር ሰማያዊ",
    "multicolour": "ባለብዙ ቀለም", "multicolor": "ባለብዙ ቀለም",
    "dark": "ጥቁር", "light": "ቀላል", "natural": "ተፈጥሯዊ",
    "clear": "ግልጽ",
    "steel": "ብረት", "stainless": "የማይዝግ", "wood": "እንጨት",
    "wooden": "የእንጨት", "glass": "መስታወት", "plastic": "ፕላስቲክ",
    "cotton": "ጥጥ", "leather": "ቆዳ", "metal": "ብረታ ብረት",
    "ceramic": "ሴራሚክ", "bamboo": "ቀርከሃ", "silk": "ሐር",
    "wool": "ሱፍ", "rubber": "ላስቲክ", "paper": "ወረቀት",
    "iron": "ብረት", "brass": "ናስ", "copper": "መዳብ",
    "marble": "እምነበረድ", "fabric": "ጨርቅ", "velvet": "ከፈይ",
    "linen": "በፍታ",
    "chair": "ወንበር", "table": "ጠረጴዛ", "lamp": "መብራት",
    "bed": "አልጋ", "pillow": "ትራስ", "cushion": "ትራስ ወንበር",
    "blanket": "ብርድ ልብስ", "sheet": "አንሶላ", "sheets": "አንሶላዎች",
    "towel": "ፎጣ", "curtain": "መጋረጃ", "rug": "ምንጣፍ",
    "carpet": "ምንጣፍ", "shelf": "መደርደሪያ", "mirror": "መስታወት",
    "clock": "ሰዓት", "watch": "የእጅ ሰዓት", "bottle": "ጠርሙስ",
    "cup": "ኩባያ", "mug": "ማግ", "plate": "ሳህን",
    "plates": "ሳህኖች", "bowl": "ጎድጓዳ ሳህን", "spoon": "ማንኪያ",
    "knife": "ቢላዋ", "pan": "መጥበሻ", "pot": "ድስት",
    "jar": "ማሰሮ", "tray": "ትሪ", "box": "ሳጥን",
    "bag": "ቦርሳ", "basket": "ቅርጫት", "brush": "ብሩሽ",
    "soap": "ሳሙና", "oil": "ዘይት", "tea": "ሻይ", "coffee": "ቡና",
    "sugar": "ስኳር", "salt": "ጨው", "rice": "ሩዝ", "flour": "ዱቄት",
    "honey": "ማር", "spice": "ቅመም", "spices": "ቅመማ ቅመም",
    "nuts": "ለውዝ", "seeds": "ዘሮች", "dog": "ውሻ", "cat": "ድመት",
    "pet": "የቤት እንስሳ", "bird": "ወፍ", "fish": "ዓሣ",
    "toy": "መጫወቻ", "toys": "መጫወቻዎች", "game": "ጨዋታ",
    "ball": "ኳስ", "doll": "አሻንጉሊት", "book": "መጽሐፍ",
    "pen": "ብዕር", "pencil": "እርሳስ", "notebook": "ደብተር",
    "chart": "ቻርት", "card": "ካርድ", "cards": "ካርዶች",
    "plant": "ተክል", "plants": "ተክሎች", "flower": "አበባ",
    "garden": "አትክልት ስፍራ", "seed": "ዘር", "shoes": "ጫማዎች",
    "shoe": "ጫማ", "socks": "ካልሲዎች", "shirt": "ሸሚዝ",
    "cover": "ሽፋን", "case": "መያዣ", "stand": "ማቆሚያ",
    "holder": "መያዣ", "organizer": "ማደራጃ", "organiser": "ማደራጃ",
    "cleaner": "ማጽጃ", "filter": "ማጣሪያ", "charger": "ቻርጀር",
    "cable": "ገመድ", "battery": "ባትሪ", "batteries": "ባትሪዎች",
    "bulb": "አምፖል", "candle": "ሻማ", "frame": "ፍሬም",
    "wall": "ግድግዳ", "door": "በር", "window": "መስኮት",
    "kitchen": "ወጥ ቤት", "office": "ቢሮ", "home": "ቤት",
    "baby": "ሕፃን", "kids": "የልጆች", "men": "የወንዶች",
    "women": "የሴቶች",
    "large": "ትልቅ", "small": "ትንሽ", "big": "ትልቅ", "mini": "ሚኒ",
    "new": "አዲስ", "soft": "ለስላሳ", "hard": "ጠንካራ",
    "round": "ክብ", "square": "አራት ማዕዘን", "fresh": "ትኩስ",
    "dry": "ደረቅ", "organic": "ኦርጋኒክ", "premium": "ፕሪሚየም",
    "classic": "ክላሲክ", "modern": "ዘመናዊ", "portable": "ተንቀሳቃሽ",
    "foldable": "የሚታጠፍ", "adjustable": "የሚስተካከል",
    "waterproof": "ውሃ የማያስገባ", "rechargeable": "ዳግም የሚሞላ",
    "wireless": "ገመድ አልባ", "whole": "ሙሉ", "pure": "ንጹህ",
    "double": "ድርብ", "single": "ነጠላ", "twin": "መንትያ",
    "king": "ኪንግ", "queen": "ኩዊን", "extra": "ተጨማሪ",
    "heavy": "ከባድ", "duty": "ሥራ", "free": "ነፃ",
    "anti": "ፀረ", "non": "ኖን", "multi": "ባለብዙ",
    "board": "ቦርድ", "high": "ከፍተኛ", "cut": "መቁረጫ",
    "compact": "ጥቅጥቅ", "family": "ቤተሰብ", "tree": "ዛፍ",
    "outdoor": "የውጭ", "weight": "ክብደት", "foam": "ስፖንጅ",
    "kit": "ኪት", "mesh": "መረብ", "storage": "ማከማቻ",
    "travel": "የጉዞ", "chicken": "ዶሮ", "strap": "ማሰሪያ",
    "bar": "ባር", "folding": "የሚታጠፍ", "dining": "የመመገቢያ",
    "port": "ፖርት", "tier": "እርከን", "collection": "ስብስብ",
    "tower": "ግንብ", "furniture": "የቤት ዕቃ", "binder": "ማያያዣ",
    "credit": "ክሬዲት", "aluminum": "አሉሚኒየም",
    "aluminium": "አሉሚኒየም", "stick": "ስቲክ", "glasses": "ብርጭቆዎች",
    "seat": "መቀመጫ", "basic": "መሠረታዊ", "lid": "ክዳን",
    "bags": "ቦርሳዎች", "standing": "ቆሞ", "water": "ውሃ",
    "food": "ምግብ", "mix": "ድብልቅ", "low": "ዝቅተኛ", "mat": "ምንጣፍ",
    "pad": "ፓድ", "mid": "መካከለኛ", "cross": "መስቀለኛ",
    "amazon": "አማዞን", "patio": "በረንዳ", "shredder": "መቁረጫ ማሽን",
    "erase": "ማጥፊያ", "scratching": "መፋቂያ",
}

EXC_AM = {
    "mouse": "ማውስ", "keyboard": "ኪቦርድ", "usb": "ዩኤስቢ",
    "led": "ኤልኢዲ", "hdmi": "ኤችዲኤምአይ", "wifi": "ዋይፋይ",
    "bluetooth": "ብሉቱዝ", "headphones": "ሄድፎን",
    "headphone": "ሄድፎን", "earphones": "ኢርፎን", "speaker": "ስፒከር",
    "speakers": "ስፒከሮች", "camera": "ካሜራ", "tripod": "ትራይፖድ",
    "microphone": "ማይክሮፎን", "laptop": "ላፕቶፕ", "tablet": "ታብሌት",
    "phone": "ስልክ", "gaming": "ጌሚንግ", "yoga": "ዮጋ",
    "dumbbell": "ደምበል", "kettlebell": "ኬትልቤል",
    "cricket": "ክሪኬት", "football": "እግር ኳስ",
    "basketball": "ቅርጫት ኳስ", "badminton": "ባድሚንተን",
    "tennis": "ቴኒስ", "gym": "ጂም", "fitness": "ፊትነስ",
    "exercise": "የአካል ብቃት", "resistance": "ሬዚስታንስ",
    "band": "ባንድ", "bands": "ባንዶች", "sofa": "ሶፋ",
    "mattress": "ፍራሽ", "recliner": "ሪክላይነር", "ottoman": "ኦቶማን",
    "stool": "በርጩማ", "desk": "ዴስክ", "drawer": "መሳቢያ",
    "wardrobe": "ቁም ሳጥን", "bookshelf": "የመጽሐፍ መደርደሪያ",
    "planter": "የአበባ ማስቀመጫ", "vase": "የአበባ ማስቀመጫ",
    "skillet": "መጥበሻ", "griddle": "ምጣድ", "cooker": "ማብሰያ",
    "blender": "ብሌንደር", "mixer": "ማደባለቂያ", "grinder": "መፍጫ",
    "toaster": "ቶስተር", "kettle": "ጀበና", "thermos": "ቴርሞስ",
    "lunch": "ምሳ", "dinner": "እራት", "chocolate": "ቸኮሌት",
    "cookies": "ኩኪስ", "biscuit": "ብስኩት", "biscuits": "ብስኩቶች",
    "juice": "ጭማቂ", "masala": "ማሳላ", "leash": "ማሰሪያ ገመድ",
    "collar": "አንገትጌ", "harness": "ማሰሪያ",
    "aquarium": "አኳሪየም", "shampoo": "ሻምፑ", "grooming": "ማስዋቢያ",
    "treats": "መክሰስ", "puzzle": "እንቆቅልሽ", "blocks": "ብሎኮች",
    "teddy": "ቴዲ", "bear": "ድብ", "marker": "ማርከር",
    "markers": "ማርከሮች", "stapler": "ማያያዣ መሣሪያ",
    "folder": "ፎልደር", "files": "ፋይሎች", "file": "ፋይል",
    "envelope": "ፖስታ", "envelopes": "ፖስታዎች", "diary": "ማስታወሻ ደብተር",
    "planner": "ፕላነር", "calculator": "ካልኩሌተር",
    "printer": "ፕሪንተር", "adapter": "አዳፕተር", "charging": "ቻርጅንግ",
    "power": "ፓወር", "wire": "ሽቦ", "remote": "ሪሞት",
    "security": "ደህንነት", "sensor": "ሴንሰር", "alarm": "አላርም",
    "digital": "ዲጂታል", "electric": "ኤሌክትሪክ",
    "electronic": "ኤሌክትሮኒክ", "automatic": "አውቶማቲክ",
    "manual": "ማንዋል", "type": "ታይፕ", "wide": "ሰፊ",
    "ruled": "መስመር ያለው", "composition": "ኮምፖዚሽን",
    "playstation": "ፕሌይስቴሽን", "controller": "መቆጣጠሪያ",
    "century": "ክፍለ ዘመን", "customizable": "የሚበጅ",
    "daybed": "ዴይቤድ", "sauce": "ሶስ", "marinara": "ማሪናራ",
    "sodium": "ሶዲየም", "balance": "ሚዛን", "pump": "ፓምፕ",
    "singles": "ነጠላዎች", "flute": "ፍሉት", "swirl": "ጥምዝ",
    "uptown": "አፕታውን", "essentials": "መሠረታዊ ዕቃዎች",
    "silicone": "ሲሊኮን", "tufted": "የተሰፋ",
    "strathwood": "ስትራዝውድ", "vedaka": "ቬዳካ", "drink": "መጠጥ",
    "business": "ቢዝነስ", "gummed": "ሙጫ ያለው",
}

_AM_EXTRA = {
    "paws": "ፓውስ", "umbrella": "ጃንጥላ", "alkaline": "አልካላይን",
    "industrial": "ኢንዱስትሪያል", "copy": "ኮፒ", "cheese": "አይብ",
    "print": "ፕሪንት", "zip": "ዚፕ", "wild": "ዋይልድ",
    "accessories": "አክሰሰሪዎች", "grill": "ግሪል", "long": "ረጅም",
    "heater": "ማሞቂያ", "contemporary": "ዘመናዊ", "tape": "ቴፕ",
    "cage": "ኬጅ", "onez": "ዋንዝ", "base": "ቤዝ", "multipurpose": "ሁለገብ",
    "thick": "ወፍራም", "area": "ኤሪያ", "sectional": "ሴክሽናል",
    "farmhouse": "ፋርምሀውስ", "bright": "ደማቅ", "amazonfresh": "አማዞንፍሬሽ",
    "mount": "ማውንት", "computer": "ኮምፒውተር", "traditional": "ባህላዊ",
    "wine": "ወይን", "old": "አሮጌ", "stoneware": "ስቶንዌር", "cast": "ካስት",
    "solid": "ጠንካራ", "symactive": "ሲምአክቲቭ", "sya": "ሲያ",
    "belfit": "ቤልፊት", "hanging": "ተንጠልጣይ", "post": "ፖስት",
    "cream": "ክሬም", "dogs": "ውሾች", "lithium": "ሊቲየም",
    "magnetic": "ማግኔቲክ", "rack": "መደርደሪያ", "drinkware": "መጠጫ ዕቃ",
    "room": "ክፍል", "essential": "አስፈላጊ", "wicker": "ዊከር",
    "accent": "አክሰንት", "panel": "ፓነል", "ground": "ግራውንድ",
    "medium": "መካከለኛ", "recycled": "ሪሳይክልድ", "slime": "ስላይም",
    "edition": "እትም", "universal": "ዩኒቨርሳል", "everyday": "ዕለታዊ",
    "cell": "ሴል", "lightweight": "ቀላል", "grip": "ግሪፕ", "hand": "እጅ",
    "easel": "ኢዝል", "powder": "ዱቄት", "container": "ኮንቴነር",
    "hot": "ትኩስ", "feeder": "መመገቢያ", "thermal": "ተርማል",
    "pound": "ፓውንድ", "market": "ገበያ", "all": "ሁሉም", "weather": "ዌዘር",
    "headboard": "ሄድቦርድ", "canvas": "ካንቫስ", "tiger": "ነብር",
    "cats": "ድመቶች", "apple": "አፕል", "watt": "ዋት", "carrying": "መያዣ",
    "floor": "ወለል", "platform": "ፕላትፎርም", "duvet": "ዱቬት",
    "art": "ጥበብ", "side": "ጎን", "decorative": "ማስጌጫ", "color": "ቀለም",
    "colour": "ቀለም", "carrier": "ካሪየር", "legal": "ሊጋል", "putty": "ፑቲ",
    "brake": "ብሬክ", "crate": "ክሬት", "roast": "ሮስት", "car": "መኪና",
    "fire": "እሳት", "or": "ወይም", "vinyl": "ቪኒል",
    "compostable": "ኮምፖስት የሚሆን", "fashioned": "ፋሽንድ", "combo": "ኮምቦ",
    "sandwich": "ሳንድዊች", "hose": "ሆዝ", "backpack": "ቦርሳ",
    "training": "ስልጠና", "ring": "ቀለበት", "top": "ቶፕ",
    "hardwood": "ሃርድውድ", "rustic": "ራስቲክ", "whiteboard": "ዋይትቦርድ",
    "unicorn": "ዩኒኮርን", "lash": "ላሽ", "ears": "ጆሮዎች", "paint": "ፔይንት",
    "elevated": "ከፍ ያለ", "recipe": "ሬሲፒ", "popular": "ታዋቂ",
    "roasted": "የተጠበሰ", "ergonomic": "ኤርጎኖሚክ", "vintage": "ቪንቴጅ",
    "cookware": "የማብሰያ ዕቃ", "disposable": "የሚጣል", "salad": "ሰላጣ",
    "swivel": "ስዊቭል", "net": "ኔት", "golf": "ጎልፍ", "foot": "ፉት",
    "indoor": "የቤት ውስጥ", "bolster": "ቦልስተር", "casual": "ካዥዋል",
    "plush": "ፕላሽ", "loveseat": "ላቭሲት", "nailhead": "ኔልሄድ",
    "geometric": "ጂኦሜትሪክ", "pendant": "ፔንዳንት", "open": "ክፍት",
    "trim": "ትሪም", "grid": "ግሪድ", "lounge": "ላውንጅ", "finish": "ፊኒሽ",
    "basics": "ቤዚክስ", "pit": "ፒት", "litter": "ሊተር", "dal": "ዳል",
    "micro": "ማይክሮ", "ceiling": "ጣሪያ", "headset": "ሄድሴት",
    "style": "ስታይል", "flat": "ጠፍጣፋ", "height": "ቁመት", "deep": "ጥልቅ",
    "handle": "እጀታ", "vacuum": "ቫኩም", "serving": "ማቅረቢያ",
    "insulated": "ኢንሱሌትድ", "pads": "ፓድስ", "fatigue": "ድካም",
    "sided": "ጎን ያለው", "tool": "መሳሪያ", "pasta": "ፓስታ", "party": "ፓርቲ",
    "coolers": "ኩለር", "replacement": "መተኪያ", "by": "በ", "belt": "ቀበቶ",
    "pocket": "ኪስ", "on": "ላይ", "chairs": "ወንበሮች", "swatch": "ስዋች",
    "sateen": "ሳቲን", "end": "ኤንድ", "living": "ሊቪንግ", "sconce": "ስኮንስ",
    "upholstered": "የተሸፈነ", "sisal": "ሲሳል", "primary": "ዋና",
    "presentation": "ፕሬዘንቴሽን", "adult": "አዋቂ", "washable": "የሚታጠብ",
    "dividers": "መከፋፈያ", "letter": "ሌተር", "dual": "ድርብ",
    "control": "ኮንትሮል", "capacity": "አቅም", "displayport": "ዲስፕሌይፖርት",
    "bundle": "ጥቅል", "clip": "ክሊፕ", "neoprene": "ኒዮፕሪን", "full": "ሙሉ",
    "bean": "ቢን", "pressure": "ፕሬሸር", "pods": "ፖድስ", "cups": "ኩባያዎች",
    "cooler": "ኩለር", "ounce": "አውንስ", "street": "ስትሪት", "bowls": "ሳህኖች",
    "dispenser": "ዲስፔንሰር", "potato": "ድንች", "milk": "ወተት",
    "glitter": "ግሊተር", "dumbbells": "ደምቤል", "french": "ፈረንሳይኛ",
    "padded": "ፓድድ", "rope": "ገመድ", "space": "ስፔስ", "pouch": "ፓውች",
    "quality": "ጥራት", "density": "ዴንሲቲ", "soccer": "እግር ኳስ",
    "stripe": "ስትራይፕ", "printed": "የታተመ", "counter": "ካውንተር",
    "arm": "አርም", "reversible": "ሪቨርሲብል", "legs": "እግሮች", "back": "ጀርባ",
    "lounger": "ላውንጀር", "throw": "ትሮው", "chandelier": "ቻንደሊየር",
    "photo": "ፎቶ", "journal": "ጆርናል", "wirebound": "ዋየርባውንድ",
    "house": "ቤት", "puppy": "ቡችላ", "condo": "ኮንዶ", "kennel": "ኬኔል",
    "kitten": "ኪተን", "peanut": "ኦቾሎኒ", "glue": "ሙጫ", "tab": "ታብ",
    "adhesive": "ማጣበቂያ", "permanent": "ቋሚ", "beans": "ባቄላ",
    "android": "አንድሮይድ", "ear": "ኢር", "pre": "ፕሪ", "charged": "ቻርጅድ",
    "display": "ዲስፕሌይ", "wired": "ዋየርድ", "nintendo": "ኒንቴንዶ",
    "station": "ስቴሽን", "play": "ፕሌይ", "mobile": "ሞባይል",
    "iphone": "አይፎን", "gel": "ጄል", "easy": "ቀላል", "one": "ዋን",
    "collapsible": "የሚታጠፍ", "anodized": "አኖዳይዝድ", "gloves": "ጓንቶች",
    "tritan": "ትሪታን", "drinking": "መጠጫ", "compartment": "ኮምፓርትመንት",
    "blend": "ብሌንድ", "stemless": "ስቴምለስ", "meal": "ምግብ", "block": "ብሎክ",
    "stitched": "የተሰፋ", "gear": "ጊር", "step": "ስቴፕ", "picnic": "ፒክኒክ",
    "barbell": "ባርቤል", "framed": "ፍሬምድ", "microfiber": "ማይክሮፋይበር",
    "microfibre": "ማይክሮፋይበር", "shag": "ሻግ", "oversized": "ትልቅ መጠን",
    "fitted": "ፊትድ", "stone": "ድንጋይ", "couch": "ካውች", "made": "ሜድ",
    "bath": "ባዝ", "college": "ኮሌጅ", "chaise": "ሼዝ", "bistro": "ቢስትሮ",
    "rattan": "ራታን", "falkner": "ፎክነር", "lights": "መብራቶች", "can": "ካን",
    "week": "ሳምንት", "copier": "ኮፒየር", "compatible": "ተኳሃኝ", "tin": "ቲን",
    "eye": "አይን", "trouncer": "ትራውንሰር", "rex": "ሬክስ", "penguin": "ፔንግዊን",
    "eyes": "አይኖች", "ash": "አሽ", "stamp": "ስታምፕ", "painter": "ፔይንተር",
    "posts": "ፖስቶች", "jerky": "ጀርኪ", "liquid": "ፈሳሽ", "pens": "እስክሪብቶዎች",
    "chips": "ቺፕስ", "split": "ስፕሊት", "lightning": "ላይትኒንግ",
    "connector": "ኮኔክተር", "commercial": "ኮሜርሻል", "bradford": "ብራድፎርድ",
    "armless": "አርምለስ", "polyester": "ፖሊስተር", "ready": "ሬዲ",
    "foods": "ፉድስ", "cobb": "ኮብ", "reprint": "ሪፕሪንት", "sailing": "ሴይሊንግ",
    "ship": "መርከብ", "patent": "ፓተንት", "metallic": "ሜታሊክ", "ink": "ኢንክ",
    "keychain": "ኪቼይን", "peeler": "ፒለር", "roller": "ሮለር", "wiper": "ዋይፐር",
    "tumbler": "ተምብለር", "bench": "ቤንች", "cabinet": "ካቢኔት",
    "hanger": "ሃንገር", "hangers": "ሃንገር", "scale": "ሚዛን", "timer": "ታይመር",
    "opener": "መክፈቻ", "strainer": "ማጣሪያ", "whisk": "ዊስክ",
    "spatula": "ስፓቱላ", "ladle": "ላድል", "tongs": "ቶንግስ", "grater": "መፍጫ",
    "colander": "ኮላንደር", "apron": "ሽርጥ", "napkins": "ናፕኪን",
    "napkin": "ናፕኪን", "sponge": "ስፖንጅ", "sponges": "ስፖንጅ",
    "trash": "ቆሻሻ", "garbage": "ቆሻሻ", "laundry": "ላውንድሪ",
    "hamper": "ሃምፐር", "shower": "ሻወር", "toilet": "ሽንት ቤት", "sink": "ሲንክ",
    "faucet": "ቧንቧ", "spray": "ስፕሬይ", "sprayer": "ስፕሬየር",
    "watering": "ውሃ ማጠጫ", "nozzle": "ኖዝል", "shovel": "አካፋ", "rake": "ሬክ",
    "pruner": "ፕሩነር", "pruning": "መከርከሚያ", "shears": "መቀስ",
    "scissors": "መቀስ", "gnome": "ኖም", "fountain": "ፏፏቴ", "solar": "ሶላር",
    "lantern": "ፋኖስ", "string": "ስትሪንግ", "fairy": "ፌሪ", "bulbs": "አምፖሎች",
    "chew": "ቹ", "squeaky": "ስኩዊኪ", "bone": "አጥንት", "kibble": "ኪብል",
    "bed": "አልጋ", "beds": "አልጋዎች", "litterbox": "ሊተርቦክስ",
    "scratcher": "ስክራቸር", "perch": "ፐርች", "hutch": "ሃች",
    "terrarium": "ቴራሪየም", "hamster": "ሃምስተር", "rabbit": "ጥንቸል",
    "wheel": "ጎማ", "bell": "ደወል", "action": "አክሽን", "figure": "ፊገር",
    "figures": "ፊገሮች", "building": "ግንባታ", "bricks": "ጡቦች",
    "craft": "ክራፍት", "crayons": "ክሬዮን", "coloring": "ቀለም መቀባት",
    "colouring": "ቀለም መቀባት", "sticker": "ስቲከር", "stickers": "ስቲከሮች",
    "playset": "ፕሌይሴት", "racing": "ሬሲንግ", "dinosaur": "ዳይኖሰር",
    "robot": "ሮቦት", "kite": "ካይት", "bubble": "ባብል", "bubbles": "ባብልስ",
    "chalk": "ጠመኔ", "paperback": "ፔፐርባክ", "hardcover": "ሃርድከቨር",
    "novel": "ልብወለድ", "cookbook": "የምግብ አዘገጃጀት መጽሐፍ", "guide": "መመሪያ",
    "atlas": "አትላስ", "dictionary": "መዝገበ ቃላት", "sketchbook": "ስኬችቡክ",
    "highlighter": "ሃይላይተር", "highlighters": "ሃይላይተር", "eraser": "ላጲስ",
    "ruler": "ማስመሪያ", "clips": "ክሊፖች", "staples": "ስቴፕልስ",
    "labels": "ሌብሎች", "label": "ሌብል", "index": "ኢንዴክስ", "sticky": "ስቲኪ",
    "notes": "ማስታወሻዎች", "notepad": "ኖትፓድ", "notepads": "ኖትፓድ",
    "clipboard": "ክሊፕቦርድ", "lamination": "ላሚኔሽን",
    "laminating": "ላሚኔቲንግ", "pouches": "ፓውች", "toner": "ቶነር",
    "cartridge": "ካርትሪጅ", "ream": "ሪም", "sheets": "ሺት", "sheet": "ሺት",
    "machine": "ማሽን", "handi": "ሃንዲ", "roti": "ሮቲ", "tawa": "ታዋ",
    "chowder": "ቻውደር", "clam": "ክላም", "spoons": "ማንኪያዎች",
    "forks": "ሹካዎች", "fork": "ሹካ", "knives": "ቢላዎች", "cutlery": "ካትለሪ",
    "kadai": "ካዳይ", "idli": "ኢድሊ", "dosa": "ዶሳ", "chapati": "ቻፓቲ",
    "quilt": "ብርድ ልብስ", "bedsheet": "አንሶላ", "pillowcase": "የትራስ ልብስ",
    "mixing": "ሚክሲንግ", "baking": "መጋገሪያ", "cake": "ኬክ", "macbook": "ማክቡክ",
}
for _k, _v in _AM_EXTRA.items():
    EXC_AM.setdefault(_k, _v)

_AM_BASE = {"b": "በ", "c": "ከ", "d": "ደ", "f": "ፈ", "g": "ገ",
            "h": "ሀ", "j": "ጀ", "k": "ከ", "l": "ለ", "m": "መ",
            "n": "ነ", "p": "ፐ", "q": "ቀ", "r": "ረ", "s": "ሰ",
            "t": "ተ", "v": "ቨ", "w": "ወ", "y": "የ", "z": "ዘ",
            "ch": "ቸ", "sh": "ሸ", "th": "ተ", "ph": "ፈ",
            "wh": "ወ", "ck": "ከ", "gh": "ገ", "kh": "ከ",
            "bh": "በ", "dh": "ደ", "qu": "ቀ"}
_AM_VIDX = {"a": 3, "aa": 3, "e": 4, "ee": 2, "i": 2, "o": 6,
            "u": 1, "ea": 2, "ay": 4, "aw": 6, "au": 6, "ow": 6}
_AM_INIT = {"a": "አ", "aa": "አ", "e": "ኤ", "ee": "ኢ", "i": "ኢ",
            "o": "ኦ", "u": "ኡ", "ea": "ኢ", "ay": "ኤ", "aw": "አው",
            "au": "አው", "ow": "ኦ", "ai": "አይ", "ou": "አው"}


def _fidel(base, idx):
    return chr(ord(base) + idx)


def _am_translit(word):
    w = _phonology(word.lower())
    units, i = [], 0
    keys2 = {k for k in (list(_AM_BASE) + list(_AM_VIDX) + ["ai", "ou"])
             if len(k) == 2}
    while i < len(w):
        pair = w[i:i + 2]
        if pair in keys2:
            units.append(pair)
            i += 2
        else:
            units.append(w[i])
            i += 1
    out = []
    i = 0
    while i < len(units):
        u = units[i]
        if u in _AM_BASE:
            base = _AM_BASE[u]
            nxt = units[i + 1] if i + 1 < len(units) else None
            if u == "x":
                pass
            if nxt in _AM_VIDX:
                out.append(_fidel(base, _AM_VIDX[nxt]))
                i += 2
                continue
            if nxt == "ai":
                out.append(_fidel(base, 3))
                out.append("ይ")
                i += 2
                continue
            if nxt == "ou":
                out.append(_fidel(base, 3))
                out.append("ው")
                i += 2
                continue
            out.append(_fidel(base, 5))
            i += 1
        elif u == "x":
            out.append("ክስ")
            i += 1
        elif u in _AM_INIT:
            out.append(_AM_INIT[u])
            i += 1
        else:
            out.append(u)
            i += 1
    return "".join(out)


def _am_word(word):
    lw = word.lower()
    if _brand_caps(word, EXC_AM):
        return word
    if lw in LEX_AM:
        return LEX_AM[lw]
    if lw in EXC_AM:
        return EXC_AM[lw]
    if not re.search(r"[a-zA-Z]", word):
        return word
    if word.isupper() and len(word) >= 2:
        return word
    if len(lw) <= 2 and lw not in ("tv",):
        return word
    return _am_translit(word)


_WORD_FN = {"hi": _hi_word, "bn": _bn_word, "ur": _ur_word,
            "am": _am_word}


def translate_name(lang, text):
    fn = _WORD_FN.get(lang)
    if fn is None:
        raise NotImplementedError(lang)
    parts = re.split(r"([A-Za-z]+(?:'s)?)", text)
    return "".join(fn(p[:-2] if p.endswith("'s") else p)
                   if re.fullmatch(r"[A-Za-z]+(?:'s)?", p or "")
                   else p for p in parts)


DESC_PHRASES_HI = {
    "Ships in plain recyclable packaging.":
        "सादे पुनर्चक्रण-योग्य पैकेजिंग में भेजा जाता है।",
    "Backed by a 30-day return window.":
        "30-दिन की वापसी सुविधा के साथ।",
    "Restocked weekly.": "हर सप्ताह फिर से स्टॉक किया जाता है।",
    "Popular in its category.": "अपनी श्रेणी में लोकप्रिय।",
    "Sold and dispatched from our own warehouse.":
        "हमारे अपने गोदाम से बेचा और भेजा जाता है।",
    "Covered by the standard one-year guarantee.":
        "मानक एक-वर्षीय गारंटी के साथ।",
}

CATEGORY_HI = {
    "Electronics": "इलेक्ट्रॉनिक्स", "Kitchen": "रसोई",
    "Sports": "खेल-कूद", "Home": "घर-गृहस्थी", "Garden": "बगीचा",
    "Books": "किताबें-कागज़", "Toys": "खिलौने", "Pets": "पालतू",
    "Office": "दफ़्तर", "Grocery": "किराना",
}

DESC_PHRASES_BN = {
    "Ships in plain recyclable packaging.":
        "সাধারণ পুনর্ব্যবহারযোগ্য প্যাকেজিংয়ে পাঠানো হয়।",
    "Backed by a 30-day return window.":
        "৩০-দিনের ফেরত সুবিধাসহ।",
    "Restocked weekly.": "প্রতি সপ্তাহে নতুন করে স্টক করা হয়।",
    "Popular in its category.": "নিজের বিভাগে জনপ্রিয়।",
    "Sold and dispatched from our own warehouse.":
        "আমাদের নিজস্ব গুদাম থেকে বিক্রি ও পাঠানো হয়।",
    "Covered by the standard one-year guarantee.":
        "মানসম্মত এক বছরের গ্যারান্টিসহ।",
}

CATEGORY_BN = {
    "Electronics": "ইলেকট্রনিক্স", "Kitchen": "রান্নাঘর",
    "Sports": "খেলাধুলা", "Home": "ঘর-গৃহস্থালি", "Garden": "বাগান",
    "Books": "বই-কাগজ", "Toys": "খেলনা", "Pets": "পোষা প্রাণী",
    "Office": "অফিস", "Grocery": "মুদি",
}

DESC_PHRASES_UR = {
    "Ships in plain recyclable packaging.":
        "سادہ قابلِ ری سائیکل پیکنگ میں بھیجا جاتا ہے۔",
    "Backed by a 30-day return window.":
        "30 دن کی واپسی کی سہولت کے ساتھ۔",
    "Restocked weekly.": "ہر ہفتے دوبارہ اسٹاک کیا جاتا ہے۔",
    "Popular in its category.": "اپنی کیٹیگری میں مقبول۔",
    "Sold and dispatched from our own warehouse.":
        "ہمارے اپنے گودام سے فروخت اور روانہ کیا جاتا ہے۔",
    "Covered by the standard one-year guarantee.":
        "معیاری ایک سالہ گارنٹی کے ساتھ۔",
}

CATEGORY_UR = {
    "Electronics": "الیکٹرانکس", "Kitchen": "باورچی خانہ",
    "Sports": "کھیل", "Home": "گھر", "Garden": "باغ",
    "Books": "کتابیں و کاغذ", "Toys": "کھلونے",
    "Pets": "پالتو جانور", "Office": "دفتر", "Grocery": "کریانہ",
}

DESC_PHRASES_AM = {
    "Ships in plain recyclable packaging.":
        "በቀላል እንደገና ጥቅም ላይ በሚውል ማሸጊያ ይላካል።",
    "Backed by a 30-day return window.":
        "የ30 ቀን የመመለሻ ጊዜ አለው።",
    "Restocked weekly.": "በየሳምንቱ እንደገና ይሞላል።",
    "Popular in its category.": "በምድቡ ውስጥ ተወዳጅ።",
    "Sold and dispatched from our own warehouse.":
        "ከራሳችን መጋዘን ይሸጣል እንዲሁም ይላካል።",
    "Covered by the standard one-year guarantee.":
        "መደበኛ የአንድ ዓመት ዋስትና አለው።",
}

CATEGORY_AM = {
    "Electronics": "ኤሌክትሮኒክስ", "Kitchen": "ወጥ ቤት",
    "Sports": "ስፖርት", "Home": "ቤት", "Garden": "አትክልት",
    "Books": "መጻሕፍትና ወረቀት", "Toys": "መጫወቻዎች",
    "Pets": "የቤት እንስሳት", "Office": "ቢሮ", "Grocery": "ሸቀጣሸቀጥ",
}

COLOUR_LABEL = {"hi": "रंग", "bn": "রং", "ur": "رنگ", "am": "ቀለም"}
MATERIAL_LABEL = {"hi": "सामग्री", "bn": "উপাদান", "ur": "میٹریل",
                  "am": "ቁሳቁስ"}
