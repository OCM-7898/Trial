import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

A = [
 ("ADD","HAAB","Addis Ababa","አዲስ አበባ","Bole International Airport","ቦሌ ዓለም አቀፍ አየር ማረፊያ","Ethiopia","ኢትዮጵያ","ET","africa","Africa/Addis_Ababa",3,8.9779,38.7993),
 ("DIR","HADR","Dire Dawa","ድሬዳዋ","Aba Tenna Dejazmach Yilma Airport","አባ ተና ደጃዝማች ይልማ አየር ማረፊያ","Ethiopia","ኢትዮጵያ","ET","africa","Africa/Addis_Ababa",1,9.6247,41.8542),
 ("BJR","HABD","Bahir Dar","ባህር ዳር","Bahir Dar Airport","ባህር ዳር አየር ማረፊያ","Ethiopia","ኢትዮጵያ","ET","africa","Africa/Addis_Ababa",1,11.6081,37.3216),
 ("MQX","HAMK","Mekelle","መቀሌ","Alula Aba Nega Airport","አሉላ አባ ነጋ አየር ማረፊያ","Ethiopia","ኢትዮጵያ","ET","africa","Africa/Addis_Ababa",1,13.4674,39.5335),
 ("GDQ","HAGN","Gondar","ጎንደር","Gondar Airport","ጎንደር አየር ማረፊያ","Ethiopia","ኢትዮጵያ","ET","africa","Africa/Addis_Ababa",1,12.5199,37.4340),
 ("JIM","HAJM","Jimma","ጅማ","Aba Segud Airport","አባ ሰጉድ አየር ማረፊያ","Ethiopia","ኢትዮጵያ","ET","africa","Africa/Addis_Ababa",1,7.6662,36.8166),
 ("AXU","HAAX","Axum","አክሱም","Axum Airport","አክሱም አየር ማረፊያ","Ethiopia","ኢትዮጵያ","ET","africa","Africa/Addis_Ababa",1,14.1468,38.7728),
 ("LLI","HALL","Lalibela","ላሊበላ","Lalibela Airport","ላሊበላ አየር ማረፊያ","Ethiopia","ኢትዮጵያ","ET","africa","Africa/Addis_Ababa",1,11.9750,38.9800),
 ("NBO","HKJK","Nairobi","ናይሮቢ","Jomo Kenyatta International Airport","ጆሞ ኬንያታ ዓለም አቀፍ አየር ማረፊያ","Kenya","ኬንያ","KE","africa","Africa/Nairobi",2,-1.3192,36.9278),
 ("MBA","HKMO","Mombasa","ሞምባሳ","Moi International Airport","ሞኢ ዓለም አቀፍ አየር ማረፊያ","Kenya","ኬንያ","KE","africa","Africa/Nairobi",1,-4.0348,39.5942),
 ("DAR","HTDA","Dar es Salaam","ዳሬሰላም","Julius Nyerere International Airport","ጁሊየስ ኒዬሬሬ ዓለም አቀፍ አየር ማረፊያ","Tanzania","ታንዛኒያ","TZ","africa","Africa/Dar_es_Salaam",3,-6.8781,39.2026),
 ("JRO","HTKJ","Kilimanjaro","ኪሊማንጃሮ","Kilimanjaro International Airport","ኪሊማንጃሮ ዓለም አቀፍ አየር ማረፊያ","Tanzania","ታንዛኒያ","TZ","africa","Africa/Dar_es_Salaam",1,-3.4294,37.0745),
 ("ZNZ","HTZA","Zanzibar","ዛንዚባር","Abeid Amani Karume International Airport","አቤድ አማኒ ካሩሜ ዓለም አቀፍ አየር ማረፊያ","Tanzania","ታንዛኒያ","TZ","africa","Africa/Dar_es_Salaam",2,-6.2220,39.2249),
 ("EBB","HUEN","Entebbe","እንተቤ","Entebbe International Airport","እንተቤ ዓለም አቀፍ አየር ማረፊያ","Uganda","ኡጋንዳ","UG","africa","Africa/Kampala",1,0.0424,32.4435),
 ("KGL","HRYR","Kigali","ኪጋሊ","Kigali International Airport","ኪጋሊ ዓለም አቀፍ አየር ማረፊያ","Rwanda","ሩዋንዳ","RW","africa","Africa/Kigali",1,-1.9686,30.1395),
 ("BJM","HBBA","Bujumbura","ቡጁምቡራ","Melchior Ndadaye International Airport","መልኪዮር ንዳዳዬ ዓለም አቀፍ አየር ማረፊያ","Burundi","ቡሩንዲ","BI","africa","Africa/Bujumbura",1,-3.3240,29.3185),
 ("JUB","HSSJ","Juba","ጁባ","Juba International Airport","ጁባ ዓለም አቀፍ አየር ማረፊያ","South Sudan","ደቡብ ሱዳን","SS","africa","Africa/Juba",1,4.8720,31.6010),
 ("KRT","HSSS","Khartoum","ካርቱም","Khartoum International Airport","ካርቱም ዓለም አቀፍ አየር ማረፊያ","Sudan","ሱዳን","SD","africa","Africa/Khartoum",1,15.5895,32.5532),
 ("MGQ","HCMM","Mogadishu","ሞቃዲሾ","Aden Adde International Airport","አደን አዴ ዓለም አቀፍ አየር ማረፊያ","Somalia","ሶማሊያ","SO","africa","Africa/Mogadishu",1,2.0144,45.3047),
 ("HGA","HCGH","Hargeisa","ሀርጌሳ","Hargeisa International Airport","ሀርጌሳ ዓለም አቀፍ አየር ማረፊያ","Somalia","ሶማሊያ","SO","africa","Africa/Mogadishu",1,9.5182,44.0887),
 ("JIB","HDAM","Djibouti","ጅቡቲ","Djibouti-Ambouli International Airport","ጅቡቲ-አምቡሊ ዓለም አቀፍ አየር ማረፊያ","Djibouti","ጅቡቲ","DJ","africa","Africa/Djibouti",1,11.5473,43.1595),
 ("ASM","HHAS","Asmara","አስመራ","Asmara International Airport","አስመራ ዓለም አቀፍ አየር ማረፊያ","Eritrea","ኤርትራ","ER","africa","Africa/Asmara",1,15.2919,38.9107),
 ("CAI","HECA","Cairo","ካይሮ","Cairo International Airport","ካይሮ ዓለም አቀፍ አየር ማረፊያ","Egypt","ግብጽ","EG","africa","Africa/Cairo",3,30.1219,31.4056),
 ("LOS","DNMM","Lagos","ላጎስ","Murtala Muhammed International Airport","ሙርታላ ሙሐመድ ዓለም አቀፍ አየር ማረፊያ","Nigeria","ናይጄሪያ","NG","africa","Africa/Lagos",2,6.5774,3.3212),
 ("ABV","DNAA","Abuja","አቡጃ","Nnamdi Azikiwe International Airport","ንናምዲ አዚኪዌ ዓለም አቀፍ አየር ማረፊያ","Nigeria","ናይጄሪያ","NG","africa","Africa/Lagos",2,9.0068,7.2632),
 ("ACC","DGAA","Accra","አክራ","Kotoka International Airport","ኮቶካ ዓለም አቀፍ አየር ማረፊያ","Ghana","ጋና","GH","africa","Africa/Accra",3,5.6052,-0.1668),
 ("ABJ","DIAP","Abidjan","አቢጃን","Port Bouet Airport","ፖርት ቡዌ አየር ማረፊያ","Cote d'Ivoire","ኮትዲቯር","CI","africa","Africa/Abidjan",1,5.2614,-3.9263),
 ("DKR","GOBD","Dakar","ዳካር","Blaise Diagne International Airport","ብሌዝ ዲያኝ ዓለም አቀፍ አየር ማረፊያ","Senegal","ሴኔጋል","SN","africa","Africa/Dakar",1,14.6700,-17.0733),
 ("BKO","GABS","Bamako","ባማኮ","Modibo Keita International Airport","ሞዲቦ ኬታ ዓለም አቀፍ አየር ማረፊያ","Mali","ማሊ","ML","africa","Africa/Bamako",1,12.5335,-7.9500),
 ("OUA","DFFD","Ouagadougou","ዋጋዱጉ","Thomas Sankara International Airport","ቶማስ ሳንካራ ዓለም አቀፍ አየር ማረፊያ","Burkina Faso","ቡርኪና ፋሶ","BF","africa","Africa/Ouagadougou",1,12.3532,-1.5124),
 ("DLA","FKKD","Douala","ዱዋላ","Douala International Airport","ዱዋላ ዓለም አቀፍ አየር ማረፊያ","Cameroon","ካሜሩን","CM","africa","Africa/Douala",1,4.0061,9.7195),
 ("FIH","FZAA","Kinshasa","ኪንሻሳ","N'djili International Airport","ንጂሊ ዓለም አቀፍ አየር ማረፊያ","DR Congo","ዲሞክራሲያዊ ኮንጎ","CD","africa","Africa/Kinshasa",2,-4.3858,15.4446),
 ("LAD","FNLU","Luanda","ሉዋንዳ","Quatro de Fevereiro Airport","ኳትሮ ዴ ፌቬሬሮ አየር ማረፊያ","Angola","አንጎላ","AO","africa","Africa/Luanda",2,-8.8584,13.2312),
 ("WDH","FYWH","Windhoek","ዊንድሁክ","Hosea Kutako International Airport","ሆሲያ ኩታኮ ዓለም አቀፍ አየር ማረፊያ","Namibia","ናሚቢያ","NA","africa","Africa/Windhoek",1,-22.4799,17.4709),
 ("GBE","FBSK","Gaborone","ጋቦሮኔ","Sir Seretse Khama International Airport","ሰር ሴሬትሴ ካማ ዓለም አቀፍ አየር ማረፊያ","Botswana","ቦትስዋና","BW","africa","Africa/Gaborone",1,-24.5553,25.9182),
 ("HRE","FVHA","Harare","ሀራሬ","Harare International Airport","ሀራሬ ዓለም አቀፍ አየር ማረፊያ","Zimbabwe","ዚምባብዌ","ZW","africa","Africa/Harare",1,-17.9318,31.0928),
 ("LUN","FLKK","Lusaka","ሉሳካ","Kenneth Kaunda International Airport","ኬኔት ካውንዳ ዓለም አቀፍ አየር ማረፊያ","Zambia","ዛምቢያ","ZM","africa","Africa/Lusaka",1,-15.3308,28.4526),
 ("LLW","FWKI","Lilongwe","ሊሎንግዌ","Kamuzu International Airport","ካሙዙ ዓለም አቀፍ አየር ማረፊያ","Malawi","ማላዊ","MW","africa","Africa/Blantyre",1,-13.7894,33.7810),
 ("MPM","FQMA","Maputo","ማፑቶ","Maputo International Airport","ማፑቶ ዓለም አቀፍ አየር ማረፊያ","Mozambique","ሞዛምቢክ","MZ","africa","Africa/Maputo",2,-25.9208,32.5726),
 ("TNR","FMMI","Antananarivo","አንታናናሪቮ","Ivato International Airport","ኢቫቶ ዓለም አቀፍ አየር ማረፊያ","Madagascar","ማዳጋስካር","MG","africa","Indian/Antananarivo",1,-18.7969,47.4788),
 ("MRU","FIMP","Port Louis","ፖርት ሉዊ","Sir Seewoosagur Ramgoolam International Airport","ሰር ሲውሳጉር ራምጉላም ዓለም አቀፍ አየር ማረፊያ","Mauritius","ሞሪሸስ","MU","africa","Indian/Mauritius",1,-20.4302,57.6836),
 ("SEZ","FSIA","Mahe","ማሄ","Seychelles International Airport","ሲሸልስ ዓለም አቀፍ አየር ማረፊያ","Seychelles","ሲሸልስ","SC","africa","Indian/Mahe",1,-4.6743,55.5218),
 ("JNB","FAOR","Johannesburg","ጆሃንስበርግ","O. R. Tambo International Airport","ኦ. አር. ታምቦ ዓለም አቀፍ አየር ማረፊያ","South Africa","ደቡብ አፍሪካ","ZA","africa","Africa/Johannesburg",2,-26.1392,28.2460),
 ("CPT","FACT","Cape Town","ኬፕ ታውን","Cape Town International Airport","ኬፕ ታውን ዓለም አቀፍ አየር ማረፊያ","South Africa","ደቡብ አፍሪካ","ZA","africa","Africa/Johannesburg",2,-33.9715,18.6021),
 ("DUR","FALE","Durban","ደርባን","King Shaka International Airport","ኪንግ ሻካ ዓለም አቀፍ አየር ማረፊያ","South Africa","ደቡብ አፍሪካ","ZA","africa","Africa/Johannesburg",1,-29.6144,31.1197),
 ("CMN","GMMN","Casablanca","ካዛብላንካ","Mohammed V International Airport","ሙሐመድ አምስተኛ ዓለም አቀፍ አየር ማረፊያ","Morocco","ሞሮኮ","MA","africa","Africa/Casablanca",2,33.3675,-7.5899),

 ("LHR","EGLL","London","ለንደን","Heathrow Airport","ሂዝሮው አየር ማረፊያ","United Kingdom","ዩናይትድ ኪንግደም","GB","europe","Europe/London",4,51.4700,-0.4543),
 ("CDG","LFPG","Paris","ፓሪስ","Charles de Gaulle Airport","ቻርለስ ደ ጎል አየር ማረፊያ","France","ፈረንሳይ","FR","europe","Europe/Paris",3,49.0097,2.5479),
 ("FRA","EDDF","Frankfurt","ፍራንክፈርት","Frankfurt Airport","ፍራንክፈርት አየር ማረፊያ","Germany","ጀርመን","DE","europe","Europe/Berlin",2,50.0379,8.5622),
 ("BRU","EBBR","Brussels","ብራሰልስ","Brussels Airport","ብራሰልስ አየር ማረፊያ","Belgium","ቤልጂየም","BE","europe","Europe/Brussels",1,50.9014,4.4844),
 ("AMS","EHAM","Amsterdam","አምስተርዳም","Schiphol Airport","ስኪፖል አየር ማረፊያ","Netherlands","ኔዘርላንድስ","NL","europe","Europe/Amsterdam",1,52.3105,4.7683),
 ("MAD","LEMD","Madrid","ማድሪድ","Adolfo Suarez Barajas Airport","አዶልፎ ሱዋሬዝ ባራሃስ አየር ማረፊያ","Spain","ስፔን","ES","europe","Europe/Madrid",4,40.4936,-3.5668),
 ("FCO","LIRF","Rome","ሮም","Fiumicino Airport","ፊዩሚቺኖ አየር ማረፊያ","Italy","ጣሊያን","IT","europe","Europe/Rome",4,41.8003,12.2389),
 ("MXP","LIMC","Milan","ሚላን","Malpensa Airport","ማልፔንሳ አየር ማረፊያ","Italy","ጣሊያን","IT","europe","Europe/Rome",2,45.6306,8.7281),
 ("VIE","LOWW","Vienna","ቪየና","Vienna International Airport","ቪየና ዓለም አቀፍ አየር ማረፊያ","Austria","ኦስትሪያ","AT","europe","Europe/Vienna",3,48.1103,16.5697),
 ("ATH","LGAV","Athens","አቴንስ","Athens International Airport","አቴንስ ዓለም አቀፍ አየር ማረፊያ","Greece","ግሪክ","GR","europe","Europe/Athens",1,37.9364,23.9445),
 ("IST","LTFM","Istanbul","ኢስታንቡል","Istanbul Airport","ኢስታንቡል አየር ማረፊያ","Turkiye","ቱርክ","TR","europe","Europe/Istanbul",1,41.2753,28.7519),

 ("DXB","OMDB","Dubai","ዱባይ","Dubai International Airport","ዱባይ ዓለም አቀፍ አየር ማረፊያ","United Arab Emirates","የተባበሩት አረብ ኤሜሬትስ","AE","middle_east","Asia/Dubai",3,25.2532,55.3657),
 ("DOH","OTHH","Doha","ዶሃ","Hamad International Airport","ሀማድ ዓለም አቀፍ አየር ማረፊያ","Qatar","ኳታር","QA","middle_east","Asia/Qatar",1,25.2731,51.6081),
 ("JED","OEJN","Jeddah","ጅዳ","King Abdulaziz International Airport","ኪንግ አብዱልአዚዝ ዓለም አቀፍ አየር ማረፊያ","Saudi Arabia","ሳውዲ አረቢያ","SA","middle_east","Asia/Riyadh",3,21.6796,39.1565),
 ("RUH","OERK","Riyadh","ሪያድ","King Khalid International Airport","ኪንግ ካሊድ ዓለም አቀፍ አየር ማረፊያ","Saudi Arabia","ሳውዲ አረቢያ","SA","middle_east","Asia/Riyadh",5,24.9576,46.6988),
 ("TLV","LLBG","Tel Aviv","ቴል አቪቭ","Ben Gurion Airport","ቤን ጉርዮን አየር ማረፊያ","Israel","እስራኤል","IL","middle_east","Asia/Jerusalem",2,32.0114,34.8867),
 ("AMM","OJAI","Amman","አማን","Queen Alia International Airport","ንግሥት አሊያ ዓለም አቀፍ አየር ማረፊያ","Jordan","ዮርዳኖስ","JO","middle_east","Asia/Amman",1,31.7226,35.9932),

 ("BOM","VABB","Mumbai","ሙምባይ","Chhatrapati Shivaji Maharaj International Airport","ቻትራፓቲ ሺቫጂ ማሃራጅ ዓለም አቀፍ አየር ማረፊያ","India","ህንድ","IN","asia","Asia/Kolkata",2,19.0887,72.8679),
 ("DEL","VIDP","Delhi","ደልሂ","Indira Gandhi International Airport","ኢንዲራ ጋንዲ ዓለም አቀፍ አየር ማረፊያ","India","ህንድ","IN","asia","Asia/Kolkata",3,28.5562,77.1000),
 ("PVG","ZSPD","Shanghai","ሻንጋይ","Pudong International Airport","ፑዶንግ ዓለም አቀፍ አየር ማረፊያ","China","ቻይና","CN","asia","Asia/Shanghai",2,31.1443,121.8083),
 ("HKG","VHHH","Hong Kong","ሆንግ ኮንግ","Hong Kong International Airport","ሆንግ ኮንግ ዓለም አቀፍ አየር ማረፊያ","China","ቻይና","CN","asia","Asia/Hong_Kong",2,22.3080,113.9185),
 ("BKK","VTBS","Bangkok","ባንኮክ","Suvarnabhumi Airport","ሱቫርናብሁሚ አየር ማረፊያ","Thailand","ታይላንድ","TH","asia","Asia/Bangkok",1,13.6900,100.7501),
 ("SIN","WSSS","Singapore","ሲንጋፖር","Changi Airport","ቻንጊ አየር ማረፊያ","Singapore","ሲንጋፖር","SG","asia","Asia/Singapore",4,1.3644,103.9915),
 ("ICN","RKSI","Seoul","ሴኡል","Incheon International Airport","ኢንቼዮን ዓለም አቀፍ አየር ማረፊያ","South Korea","ደቡብ ኮሪያ","KR","asia","Asia/Seoul",2,37.4602,126.4407),

 ("JFK","KJFK","New York","ኒው ዮርክ","John F. Kennedy International Airport","ጆን ኤፍ. ኬኔዲ ዓለም አቀፍ አየር ማረፊያ","United States","አሜሪካ","US","north_america","America/New_York",6,40.6413,-73.7781),
 ("IAD","KIAD","Washington","ዋሽንግተን","Dulles International Airport","ደለስ ዓለም አቀፍ አየር ማረፊያ","United States","አሜሪካ","US","north_america","America/New_York",1,38.9531,-77.4565),
 ("ORD","KORD","Chicago","ቺካጎ","O'Hare International Airport","ኦሄር ዓለም አቀፍ አየር ማረፊያ","United States","አሜሪካ","US","north_america","America/Chicago",4,41.9742,-87.9073),
 ("YYZ","CYYZ","Toronto","ቶሮንቶ","Toronto Pearson International Airport","ቶሮንቶ ፒርሰን ዓለም አቀፍ አየር ማረፊያ","Canada","ካናዳ","CA","north_america","America/Toronto",2,43.6777,-79.6248),

 ("GRU","SBGR","Sao Paulo","ሳኦ ፓውሎ","Guarulhos International Airport","ጓሩልሆስ ዓለም አቀፍ አየር ማረፊያ","Brazil","ብራዚል","BR","south_america","America/Sao_Paulo",3,-23.4356,-46.4731),
]

FIELDS = ("iata","icao","city_en","city_am","name_en","name_am","country_en",
          "country_am","country_code","region","timezone","terminal_count",
          "latitude","longitude")


def main() -> None:
    assert len(A) == 75, f"SPEC.md 12 wants 75 airports, got {len(A)}"
    codes = [r[0] for r in A]
    assert len(set(codes)) == 75, "duplicate IATA code"
    assert len(set(r[1] for r in A)) == 75, "duplicate ICAO code"

    out = pathlib.Path("spec/seed_data/airports.yaml")
    lines = [
        "# Generated by tools/make_airports.py -- edit there, not here.",
        "# Geography is factual (SPEC.md 3). Amharic names are transliterations",
        "# except where an established Amharic form exists. All appear in",
        "# spec/translation_review.csv for the native-speaker pass.",
        "airports:",
    ]
    for i, row in enumerate(A, start=1):
        lines.append(f"  - id: {i}")
        for field, value in zip(FIELDS, row):
            if isinstance(value, str):
                lines.append(f'    {field}: "{value}"')
            else:
                lines.append(f"    {field}: {value}")
    out.write_text("\n".join(lines) + "\n", "utf-8")
    by_region = {}
    for r in A:
        by_region[r[9]] = by_region.get(r[9], 0) + 1
    print(f"wrote {out} -- {len(A)} airports")
    for region, n in sorted(by_region.items(), key=lambda kv: -kv[1]):
        print(f"  {region:15s} {n}")


if __name__ == "__main__":
    main()
