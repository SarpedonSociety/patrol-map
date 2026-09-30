# Gemini transcription prompt — war patrol reports

Use this prompt for the first transcription pass. The output drops
straight into `sources/<hull>/P<nn>/` with no reformatting.

**Which pages to give it.** Don't send the whole report. Build one PDF
with only:

1. the first page of the COMSUBPAC endorsement (it carries the patrol
   report number and the date),
2. the narrative entries you've marked that give a position, a course
   change, the departure or the arrival (the first and last narrative
   entries usually hold departure and arrival), and any lifeguard duty:
   the station assignment, downed-aviator reports and rescues,
3. Part VIII, Anti-Submarine Measures, which summarizes every attack on
   the boat in more detail than the narrative,
4. the ship contact, aircraft contact and attack tables (if the report has
   no attack table, add the narrative around each attack, from the
   approach through any depth charging that followed),
5. any table that records the boat's own positions: density layer or
   bathythermograph observations, noon positions and the like.

Keep each page's Fold3 source sheet with it.

Paste everything between the lines, then attach that PDF.

**Batches.** For a long report, run the pages in batches. Save each
Gemini answer exactly as it comes (fences and all) in the patrol's folder:
OUTPUT 1 as `gemini-01.yml`, `gemini-02.yml` ..., OUTPUT 2 as
`contacts-01.md`, `contacts-02.md` .... The converter reads them in
order and combines them. Anything you enter by hand in `patrol.yml`
(departure, arrival, tonnage, corrections) takes precedence over the
batches.

**If the chat still struggles.** Run the prompt twice on the same PDF:
first add `Produce OUTPUT 1 only.` at the end, then in a new chat add
`Produce OUTPUT 2 only.`

---

You are transcribing selected pages of a WWII U.S. submarine war patrol
report for a research database. Accuracy is paramount. Never guess,
correct, or normalize the source text. Transcribe only what is on the
pages provided. The pages are a selection, so never infer what the
missing pages might say.

Produce TWO outputs, unless told below to produce only one.

OUTPUT FORMAT
Put each output inside its own fenced code block (```yaml for OUTPUT 1,
```markdown for OUTPUT 2) so it appears as plain text with a copy button.
Do not render the tables as formatted tables. In OUTPUT 1, put double
quotes around every `event` and `flags` value. Write nothing between or
after the code blocks except one line listing anything you could not
transcribe.

OUTPUT 1 — patrol.yml
Fill in this YAML from the pages provided. Leave a value blank if they
don't give it. Put anything uncertain in that entry's `flags`.

```yaml
boat:            # hull number in the form SS-236
patrol:          # patrol number as a numeral, e.g. 3
year:            # the year the patrol began, four digits
report:          # report title as typed
comsubpac_report_no:  # "COMSUBPAC PATROL REPORT NO." on the endorsement, if given
commanding_officer:
citation:        # from the Fold3 SOURCE INFORMATION sheets, if the PDF has them
  archive:       # "Content Source", e.g. NARA
  record_group:
  nara_catalog_id:
  nara_catalog_title:
  reel:
  micro_serial:  # "Micro Serial Number" of the report's first page
  file:
  serial:
  date:
fold3_images:    # report page number -> Fold3 image number, e.g. { 1: 267838530 }
default_hemisphere: { lat: N, lon: E }
departure: { port: , date: , time: , zone: , page: , flags: }
arrival:   { port: , date: , time: , zone: , page: , flags: }
events:          # every narrative entry provided
  - date:        # e.g. 10MAY
    time:        # e.g. 0805
    zone:        # zone letter only, e.g. L
    lat:         # verbatim, e.g. 33-13-30N
    lon:         # verbatim, e.g. 151-57-30E
    from:        # for a position given from a landmark: the landmark as typed, e.g. MINAMI JIMA
    bearing:     # as typed, e.g. NE, WSW, 045T
    distance:    # as typed, e.g. 9 miles
    bearing_is:  # from_landmark ("9 miles NE of X") or to_landmark ("X bearing 060, 2 miles": X bore 060 from the boat)
    tag:         # attack, gun, minefield, counterattack, rescue, rendezvous or notable (see below); otherwise blank
    title:       # tagged entries only: a short title of a few words, e.g. "Appendectomy at sea"
    part:        # the report part the entry comes from: I (narrative) or VIII (anti-submarine measures)
    charges:     # counterattacks only: number of depth charges or bombs, as typed
    damage:      # counterattacks only: damage to the boat, verbatim
    with:        # rendezvous only: the other boat or ship, as typed, e.g. GUARDFISH
    course:
    speed:
    event:       # verbatim; if longer than 25 words, summarize and start with [SUMMARY],
                 # except tagged entries (attack, gun, minefield, counterattack, rescue, rendezvous, notable): always in full
    page:
    flags:
```

The PDF may include a Fold3 "SOURCE INFORMATION" sheet after each scanned
page. Never transcribe these sheets as report content. Use them only to
fill `citation` (from the first sheet belonging to the patrol report,
not the endorsements) and `fold3_images`: the image number is the number
in the sheet's Source URL (fold3.com/image/<number>/...), and it belongs
to the scanned page just before the sheet. Key it by the page number
typed on that report page; skip pages with no typed page number.

Make one `events` entry for each narrative entry on the pages provided.

Use `from`, `bearing` and `distance` only for a position fixed from a
charted landmark. A contact's bearing from the boat ("smoke bearing 315",
"on the port bow") is not a position: leave it in `event`.

Positions given from a landmark ("9 miles NE of MINAMI JIMA", "1 mile
WSW of MEGANE IWA", "NOJIMA SAKI bearing 060, distant 2 miles") go in
`from`, `bearing` and `distance`, exactly as typed. Set `bearing_is` to
`from_landmark` when the position lies in that direction from the
landmark, or `to_landmark` when the report gives the landmark's bearing
from the boat. If you can't tell, leave it blank and quote the report's
wording in `flags`. Leave `lat` and `lon` blank for these. Never convert
them to latitude and longitude yourself.

Tag every narrative entry recording a torpedo attack with `tag: attack`,
a gun action with `tag: gun`, and mine laying with `tag: minefield`.
Use `minefield` only for entries where laying begins, ends or is
interrupted, and for a ship sunk or damaged by the mines; record any
positions, bearings or landmarks given.

Each entry's time is the one printed at the start of that entry. Never
move a time from one entry to another. If an entry's first line is a
heading (contact number, attack number, position) with its own time,
keep that time with that entry. Keep torpedoes fired, hits and results in
`event` as typed.

Tag every entry recording an enemy attack on the boat (depth charges,
bombs, gunfire) with `tag: counterattack`. Record the number of charges
in `charges` if the entry gives it, and any damage to the boat, verbatim,
in `damage`. Keep these entries in full.

For Part VIII (Anti-Submarine Measures), make one `events` entry per
incident, with `part: VIII` and `tag: counterattack`, its date and time
if given, `charges` and `damage`, and the full text in `event`. Record it
even if the narrative describes the same incident; the map combines them.

Tag with `tag: notable` any other entry a historian would want in full:
medical emergencies and operations, deaths, burials and injuries, men
lost overboard, fires, flooding, serious equipment casualties (a
torpedo stuck in a tube, a hot run, a jammed diving plane), groundings,
and encounters with friendly forces. Keep these entries in full.

Tag with `tag: rendezvous` an entry recording a meeting at sea with
another U.S. or Allied submarine or ship: a rendezvous, an exchange of
recognition signals with a named boat, or working the same convoy. Put
the other vessel's name, as typed, in `with`. Routine escorts into and out
of port are not rendezvous. Keep these entries in full.

Tag every entry about lifeguard duty with `tag: rescue`: the lifeguard
station assignment (record its position if given), reports of downed
aviators or planes, sightings of rafts or rubber boats, and pickups.
If the time zone is stated once for the whole narrative, or clocks are
reset partway through, apply that zone to the entries it covers and say
so in `flags`.
Put the departure and arrival entries in `departure` and `arrival` as
well.

OUTPUT 2 — contacts.md
Transcribe every table of ship contacts, aircraft contacts and attacks
(Parts V, VI and VII, and the tabular data at the end of the report),
and every table that records the boat's own positions (density layer or
bathythermograph observations, noon positions). Keep the report's title
for each table, since the title tells the map which kind it is.
Reproduce each table as the report lays it out:

- Put `### <table title as typed>` above each table, and a line
  `Page <n>` above it and wherever the table continues on a new page.
- Keep the report's own column headings, spelled as typed.
- If the report prints a table with attacks as columns (Attack 1, 2, 3
  across the top and fields down the side), keep that layout. The first
  heading must be `Attack`.
- Add a final `Flags` column (or, for attack-as-column tables, a final
  `Flags` row) for your notes on that entry.
- Copy any `Remarks:` line printed under a table onto its own line
  directly after the table, starting with `Remarks:`, keeping the
  report's footnote markers (#, *).

RULES
1. Transcribe exactly as typed, including misspellings. Do not add [sic].
   Beware of reading errors: on these carbon copies the typewriter's e, o
   and c look alike, as do 3/8, 5/6 and 1/7. Read each word as a whole.
   When the letters form a real word only one way ("Commenced", not
   "Commonced"; "patrol", not "petrol"), write that word. Keep a
   misspelling only when the letters are clearly legible as typed.
   Numbers can't be read as words: if a digit could be another digit,
   write your best reading in ⟦ ⟧ and flag it.
2. Keep times, zone letters and dates exactly as typed: 1723I 17MAY,
   0310(K) 10/4/43 and 1855 10/3/43 are all fine.
3. Keep positions as typed, including the separator between latitude
   and longitude.
4. If a gun action appears in a torpedo table, keep it where the report
   puts it and say so in Flags. If a contact table has a column saying
   whether each contact was attacked (Yes/No), keep it with its own
   heading.
5. If any character is illegible, overstruck or ambiguous, write your
   best reading, wrap it in ⟦ ⟧, and explain in Flags
   (e.g. "⟦5⟧00 — first digit faint, could be blank").
6. Flag internal inconsistencies without fixing them: tonnage that
   doesn't fit the ship category, missing zone letters, more hits than
   torpedoes, and similar.
7. Record page numbers with the `Page <n>` lines described above.
8. Leave cells blank when the source is blank. Never infer values.
9. Never use the | character inside a cell; write "/" instead.

---
