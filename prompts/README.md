# Gemini transcription prompts

There are three prompts, one per kind of page, each run in its **own fresh
chat** with its own PDF:

| Prompt | PDF to attach | Save the answer as |
| --- | --- | --- |
| `1-narrative.md` | the endorsement's first page, the narrative (Part I) and Part VIII | `gemini-01.yml` |
| `2-tables.md` | the contact, aircraft and attack tables, and any table of the boat's own positions | `contacts-01.md` |
| `3-attack-forms.md` | the TORPEDO ATTACK DATA forms (1943 reports), both pages of each attack | `attacks-01.md` |

Save each answer exactly as Gemini gives it, fences and all, in
`sources/<hull>/P<nn>/`. A long report can go in batches: `gemini-02.yml`,
`contacts-02.md`, `attacks-02.md` and so on; the converter reads them in
order. Hand entries in `patrol.yml` (departure, arrival, tonnage,
corrections) take precedence over all of them.

**Which pages.** Don't send the whole report.

- Narrative PDF: the first page of the COMSUBPAC endorsement (it carries
  the patrol report number and date); the narrative entries that give a
  position, a course change, the departure or the arrival; every attack,
  from the approach through any depth charging; lifeguard duty; and Part
  VIII, Anti-Submarine Measures, if it says more than "nothing new". Keep
  each page's Fold3 source sheet with it: the prompt reads the citation
  and Fold3 image numbers from those sheets.
- Tables PDF: Parts V, VI and VII and any tabular data at the end, plus
  density layer, bathythermograph or noon position tables.
- Attack forms PDF: both pages of every TORPEDO ATTACK DATA form. Check
  that each attack's target-data page is there; without it the attack has
  no time or position of its own.

**Why separate chats.** Late in a long chat Gemini's flags filled with
garbled "typed ..." readings, and once it answered with an earlier
report's transcription. A fresh chat on the same pages came back clean.
Each prompt also carries only the instructions for its own pages.

**Check the torpedo pages.** On Trigger patrol 6, Gemini swapped two tube
numbers, reordered a spread and added values to a blank line on one
torpedo page while the serial numbers were right. Compare the Tubes Fired,
Hit or Miss, Actuation and Type Spread lines against the scan before the
data goes into a shot chart.

**Editing the prompts.** The three files are generated. Edit
`prompts/parts/` (one part per task, and `rules.md`, shared by all three),
then run `python tools/build_prompts.py`.
