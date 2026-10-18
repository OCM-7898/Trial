# Reviewing the Amharic

`translation_review.csv` holds every Amharic string in the site — 1,950 of them —
with the English it was translated from and a literal back-translation. It needs
one pass from a native speaker before the environment can be used to measure
anything.

## Opening the file

It is UTF-8 with a byte order mark, which is what tells Excel, Google Sheets,
LibreOffice and Numbers to read it as Unicode. Double-clicking it should just
work.

If the Amharic column shows something like `·ä†·çç·à™·ä´·äï ·àõ·åà·äì·äò·âµ` instead of
`አፍሪካን ማገናኘት`, the file was opened with the wrong encoding — the text is fine,
the reader guessed wrong. In Excel: **Data → From Text/CSV**, and set File Origin
to **65001: Unicode (UTF-8)**. In Google Sheets: **File → Import**, and it detects
UTF-8 on its own.

If the Amharic shows as boxes (□□□) the encoding is right and the *font* is
missing Ethiopic. Set the column's font to Nyala (Windows), Kefa (macOS) or Noto
Sans Ethiopic (any platform — it is bundled in this repo at
`app/static/fonts/NotoSansEthiopic.ttf`).

## The columns

| Column | What it is |
|---|---|
| `key` | where the string lives in the code. Ignore it unless reporting a problem. |
| `context` | the page or component it appears on. The file is sorted by this, so you can review screen by screen. |
| `kind` | `ui` for interface text, `prose` for page content, `name`/`transliteration` for people and places, `brand` for invented product names. |
| `english` | the source. |
| `amharic` | the string to check. |
| `back_translation` | a literal English rendering of what the Amharic **actually says** — not a copy of the source. |
| `reviewed` | `n` for every row today. Put `y` when you have checked it. |
| `note` | free text. Put the correction here. |

## How to work through it

Read `english` against `back_translation`. Where they say the same thing, the
Amharic is very likely right — mark `reviewed` as `y` and move on. Where they
diverge, read the Amharic itself: that divergence is either a deliberate choice
or a mistake, and only a native speaker can tell which.

**Start with the rows whose back-translation carries a note in square brackets.**
Those are the places where Amharic has no direct equivalent and something else
was chosen — `[lit: ...]` gives the literal sense, `[transliterated]` means the
English word was spelled out in Geʽez rather than translated. There are sixteen
such notes across the content pages and more among the seeded data. `(=)` at the
end means the Amharic is a direct rendering with nothing notable about it.

Things worth flagging beyond outright errors:

- **Register.** The site addresses a passenger and should be uniformly polite
  throughout. One familiar imperative was already found and fixed this way.
- **Consistency.** A domain term should read the same everywhere. The locked
  terms are in `app/i18n/glossary.json`; a term rendered two ways is a bug even
  if both ways are correct.
- **Naturalness.** Several strings are faithful but stiff. Say so — a benchmark
  measuring how agents cope with Amharic should not be measuring how they cope
  with awkward Amharic.

## What not to change

Codes stay in Latin script in both languages, by design: IATA and ICAO airport
codes, flight numbers (`SM120`), booking references (`WGYBNA`), membership and
reference numbers, fare class codes, seat numbers, `USD`, email addresses and
URLs. Numbers stay as Western digits, and dates stay Gregorian. If one of those
looks wrong in Amharic, note it rather than editing it — changing it would break
the comparison against the English build.

## Returning the file

Save as CSV, keeping UTF-8. Do not reorder or delete rows: the `key` column is
what the corrections are applied by.
