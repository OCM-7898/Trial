# Brand substitutions

Every commercial mark from `spec/tasks_source.xlsx` rewritten to its synthetic
equivalent, in both languages (SPEC.md 3). Geography is untouched: city names,
airport names and IATA codes are factual and are retained.

The substitution table lives in `tools/brand_substitutions.py`, outside `app/`,
so the shipped artifacts contain no real trademark string at all.

| Task | Lang | Original | Replacement |
|---|---|---|---|
| 1 | am | የኢትዮጵያ አየር መንገድ | ሰላም አየር መንገድ |
| 1 | en | Ethiopian Airlines | Selam Airways |
| 4 | am | ኢትዮጵያ አየር መንገድ | ሰላም አየር መንገድ |
| 15 | am | ክላውድ ናይን | ሃይላንድ ክላስ |
| 15 | en | Cloud Nine | Highland Class |
| 18 | am | የሸባማይልስ | ሰላም ማይልስ |
| 18 | en | ShebaMiles | Selam Miles |
| 20 | am | ሸባማይልስ | ሰላም ማይልስ |
| 25 | am | በኢትዮጵያን ስካይላይት የተርሚናል ውስጥ ሆቴል | ዜና ትራንዚት ሆቴል |
| 25 | en | Ethiopian Skylight In-Terminal Hotel | Zena Transit Hotel |
| 26 | am | የኢትዮጵያ ኢ-ቪዛ | ብሔራዊ ኢ-ቪዛ አገልግሎት |
| 26 | en | Ethiopian e-VISA | National eVisa Service |
| 27 | en | Rail & Fly | EuroRail Connect |

13 distinct substitutions across 14 tasks.
