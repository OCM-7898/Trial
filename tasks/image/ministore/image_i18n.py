SEP = {"en": ", ", "bn": ", ", "hi": ", ", "ur": "، ", "am": "፣ "}
QUOTE = {"en": ("‘", "’"), "bn": ("‘", "’"), "hi": ("‘", "’"),
         "ur": ("‘", "’"), "am": ("«", "»")}

TPL = {
 "en": {
  "A1_price": "The photo shows a product sold in this shop. It is one of: {cands}. What is its price?",
  "A2_wishlist": "Add the product shown in the photo to your wishlist. It is one of: {cands}.",
  "A3_buy": "Buy {one} of the product shown in the photo and have it shipped to '{addr}'. It is one of: {cands}. Complete the checkout so the order is placed.",
  "A4_brand": "Which brand sells the product shown in the photo? It is one of: {cands}.",
  "A5_reviews": "How many reviews does the product shown in the photo have? It is one of: {cands}.",
  "A6_not_sold": "Find the product shown in the photo in this shop and report its price. If the shop does not sell it, answer N/A.",
  "B1_pack": "Open the product page of {name}. According to its photo, how many units come in the pack?",
 },
 "bn": {
  "A1_price": "ছবিতে এই দোকানে বিক্রি হওয়া একটি পণ্য দেখানো হয়েছে। এটি এগুলোর একটি: {cands}। এর দাম কত?",
  "A2_wishlist": "ছবিতে দেখানো পণ্যটি আপনার উইশলিস্টে যোগ করুন। এটি এগুলোর একটি: {cands}।",
  "A3_buy": "ছবিতে দেখানো পণ্যটির {one}টি কিনুন এবং '{addr}' ঠিকানায় পাঠান। এটি এগুলোর একটি: {cands}। অর্ডারটি সম্পূর্ণ করতে চেকআউট শেষ করুন।",
  "A4_brand": "ছবিতে দেখানো পণ্যটি কোন ব্র্যান্ড বিক্রি করে? এটি এগুলোর একটি: {cands}।",
  "A5_reviews": "ছবিতে দেখানো পণ্যটির কতগুলো রিভিউ আছে? এটি এগুলোর একটি: {cands}।",
  "A6_not_sold": "ছবিতে দেখানো পণ্যটি এই দোকানে খুঁজে এর দাম জানান। দোকানে এটি বিক্রি না হলে N/A উত্তর দিন।",
  "B1_pack": "{name}-এর পণ্য পাতা খুলুন। এর ছবি অনুযায়ী প্যাকে কয়টি ইউনিট আছে?",
 },
 "hi": {
  "A1_price": "फ़ोटो में इस दुकान में बिकने वाला एक उत्पाद दिखाया गया है। यह इनमें से एक है: {cands}। इसकी कीमत क्या है?",
  "A2_wishlist": "फ़ोटो में दिखाए गए उत्पाद को अपनी विशलिस्ट में जोड़ें। यह इनमें से एक है: {cands}।",
  "A3_buy": "फ़ोटो में दिखाए गए उत्पाद का {one} नग खरीदें और उसे '{addr}' पर भिजवाएँ। यह इनमें से एक है: {cands}। ऑर्डर पूरा करने के लिए चेकआउट पूरा करें।",
  "A4_brand": "फ़ोटो में दिखाया गया उत्पाद कौन-सा ब्रांड बेचता है? यह इनमें से एक है: {cands}।",
  "A5_reviews": "फ़ोटो में दिखाए गए उत्पाद की कितनी समीक्षाएँ हैं? यह इनमें से एक है: {cands}।",
  "A6_not_sold": "फ़ोटो में दिखाए गए उत्पाद को इस दुकान में ढूँढें और उसकी कीमत बताएँ। अगर दुकान इसे नहीं बेचती, तो N/A उत्तर दें।",
  "B1_pack": "{name} का उत्पाद पृष्ठ खोलें। उसकी फ़ोटो के अनुसार पैक में कितनी इकाइयाँ हैं?",
 },
 "ur": {
  "A1_price": "تصویر میں اس دکان پر بکنے والی ایک پروڈکٹ دکھائی گئی ہے۔ یہ ان میں سے ایک ہے: {cands}۔ اس کی قیمت کیا ہے؟",
  "A2_wishlist": "تصویر میں دکھائی گئی پروڈکٹ کو اپنی وش لسٹ میں شامل کریں۔ یہ ان میں سے ایک ہے: {cands}۔",
  "A3_buy": "تصویر میں دکھائی گئی پروڈکٹ کا {one} عدد خریدیں اور اسے '{addr}' پر بھجوائیں۔ یہ ان میں سے ایک ہے: {cands}۔ آرڈر مکمل کرنے کے لیے چیک آؤٹ مکمل کریں۔",
  "A4_brand": "تصویر میں دکھائی گئی پروڈکٹ کون سا برانڈ بیچتا ہے؟ یہ ان میں سے ایک ہے: {cands}۔",
  "A5_reviews": "تصویر میں دکھائی گئی پروڈکٹ کے کتنے ریویوز ہیں؟ یہ ان میں سے ایک ہے: {cands}۔",
  "A6_not_sold": "تصویر میں دکھائی گئی پروڈکٹ کو اس دکان میں تلاش کریں اور اس کی قیمت بتائیں۔ اگر دکان اسے نہیں بیچتی تو N/A جواب دیں۔",
  "B1_pack": "{name} کا پروڈکٹ صفحہ کھولیں۔ اس کی تصویر کے مطابق پیک میں کتنے یونٹ ہیں؟",
 },
 "am": {
  "A1_price": "ፎቶው በዚህ ሱቅ የሚሸጥ አንድ ምርት ያሳያል። ከእነዚህ አንዱ ነው፦ {cands}። ዋጋው ስንት ነው?",
  "A2_wishlist": "በፎቶው የሚታየውን ምርት ወደ የምኞት ዝርዝርዎ ያክሉ። ከእነዚህ አንዱ ነው፦ {cands}።",
  "A3_buy": "በፎቶው የሚታየውን ምርት {one} ይግዙና ወደ '{addr}' እንዲላክ ያድርጉ። ከእነዚህ አንዱ ነው፦ {cands}። ትዕዛዙ እንዲመዘገብ ክፍያውን ያጠናቅቁ።",
  "A4_brand": "በፎቶው የሚታየውን ምርት የሚሸጠው የትኛው ብራንድ ነው? ከእነዚህ አንዱ ነው፦ {cands}።",
  "A5_reviews": "በፎቶው የሚታየው ምርት ስንት ግምገማዎች አሉት? ከእነዚህ አንዱ ነው፦ {cands}።",
  "A6_not_sold": "በፎቶው የሚታየውን ምርት በዚህ ሱቅ ውስጥ ፈልገው ዋጋውን ይግለጹ። ሱቁ ካልሸጠው N/A ብለው ይመልሱ።",
  "B1_pack": "የ{name}ን የምርት ገጽ ይክፈቱ። በፎቶው መሠረት በጥቅሉ ውስጥ ስንት አሃዶች አሉ?",
 },
}

_KEYS = set(TPL["en"])
for _l, _t in TPL.items():
    assert set(_t) == _KEYS, _l
    import re as _re
    for _k in _KEYS:
        assert set(_re.findall(r"\{(\w+)\}", _t[_k])) == set(_re.findall(r"\{(\w+)\}", TPL["en"][_k])), (_l, _k)
