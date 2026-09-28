# Gemini transcription prompt — war patrol reports

Use this prompt for the first transcription pass. The output drops
straight into `sources/<hull>/P<nn>/` with no reformatting.

Paste everything between the lines, then attach the report pages.

---

You are transcribing a WWII U.S. submarine war patrol report for a
research database. Accuracy is paramount. Never guess, correct, or
normalize the source text.

Produce TWO outputs.

OUTPUT 1 — patrol.yml
Fill in this YAML from the report. Leave a value blank if the report
doesn't give it. Put anything uncertain in that entry's `flags`.

```yaml
boat:            # hull number, e.g. SS-236
patrol:          # patrol number
year:
report:          # report title as typed
commanding_officer:
default_hemisphere: { lat: N, lon: E }
departure: { port: , date: , time: , zone: , page: , flags: }
arrival:   { port: , date: , time: , zone: , page: , flags: }
miles_steamed:   # Part XIII, verbatim
fuel_expended:   # Part XIV, verbatim
events:          # Part I narrative, plus Parts VI and VIII if they give positions
  - date:        # e.g. 10MAY
    time:        # e.g. 0805
    zone:        # zone letter only, e.g. L
    lat:         # verbatim, e.g. 33-13-30N
    lon:         # verbatim, e.g. 151-57-30E
    course:
    speed:
    event:       # verbatim; if longer than 25 words, summarize and start with [SUMMARY]
    page:
    flags:
```

Include a narrative entry in `events` if it states a position, a course
change, a departure, an arrival or a rendezvous, or if it records an
attack, casualty, burial or other significant event.

OUTPUT 2 — contacts.md
Transcribe every table of ship contacts, aircraft contacts and attacks
(Parts V, VI and VII, and the tabular data at the end of the report).
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
2. Keep times, zone letters and dates exactly as typed: 1723I 17MAY,
   0310(K) 10/4/43 and 1855 10/3/43 are all fine.
3. Keep positions as typed, including the separator between latitude
   and longitude.
4. If a gun action appears in a torpedo table, keep it where the report
   puts it and say so in Flags.
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
