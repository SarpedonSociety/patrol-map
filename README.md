# COMSUBPAC Patrol Plot

An animated chart of U.S. submarine war patrols in the Pacific, built
directly from the war patrol reports. A project of The Sarpedon Society.

Every point on the map is a position recorded in a patrol report. The
dashed track joins those points in time order; where a boat went between
them isn't recorded, and the map doesn't pretend otherwise.

## How it fits together

```
sources/                      Transcriptions. Never edited by the scripts.
  reference.yml               Boats, port positions, map place names
  inventory.yml               Every patrol report: found, missing, transcribed, mapped
  SS-236/P01/
    patrol.yml                Metadata, departure/arrival, Part I events
    contacts.md               Contact, aircraft and attack tables, verbatim
    review.yml                Open questions for the verification pass
  SS-283/P03/                 Tinosa, War Patrol 3
  status/                     COMSUBPAC war diary "Disposition of Forces" listings,
                              task group index, dated refit/overhaul periods
tools/convert.py              Turns sources/ into data/
data/
  manifest.json               List of patrols on the map (generated)
  status.json                 Fleet status between patrols (generated)
  patrols/SS-236-P01.json     One file per patrol (generated)
  base/land-50m.json          Coastlines (Natural Earth via world-atlas)
prompts/                      Gemini transcription prompts (see prompts/README.md)
index.html                    The map
```

## Adding a patrol

1. Build PDFs of the pages that matter, one for the narrative, one for the
   tables and, for 1943 reports, one for the TORPEDO ATTACK DATA forms, and
   run each through its own prompt in `prompts/` in a fresh Gemini chat
   (see `prompts/README.md`).
2. Save the outputs in the patrol's folder, e.g. `sources/SS-283/P03/`,
   exactly as Gemini gives them: `gemini-01.yml` ... for the narrative,
   `contacts-01.md` ... for the tables and `attacks-01.md` ... for the forms. The
   converter combines the batches in order. Hand entries in `patrol.yml`
   (departure, arrival, tonnage, corrections) take precedence, so the
   Gemini files can stay untouched as the raw transcription.
3. Verify: check every cell wrapped in ⟦ ⟧ and everything in the Flags
   column against the report. Put questions you can't settle yet in
   `review.yml`.
4. If the boat is new, add it to `boats` in `sources/reference.yml`. Add
   any new port to `ports`, and any place the map should label to `places`.
5. Add the patrol's tonnage to the `tonnage` list in `patrol.yml` by hand
   (see below).
6. Run `python tools/convert.py` (needs Python 3 and `pip install pyyaml`).
   It prints a one-line summary per patrol, including how many entries
   are flagged.
7. Commit `sources/` and `data/` together.

The converter reads every table in `contacts.md`, in whatever layout the
report uses:

- one combined contact/attack table (Silversides Patrol 1),
- separate ship contact, aircraft contact and attack tables (Tinosa
  Patrol 3), including attack summaries printed with attacks as columns,
- the column layout from the Gemini prompt.

It recognizes columns by their headings, allowing for the report's own
typos. A heading it doesn't recognize is flagged on the map, not
silently dropped. Times and dates can be `0805L 10MAY`, `0310(K) 10/4/43`
or `1855 10/3/43` (a table whose heading says GCT is read as GMT).

In `review.yml`, entries are numbered through the whole of
`contacts.md` in order, across all its tables. The map shows each
entry's number in its source line.

If the attack summary gives dates but no times (Silversides Patrol 5),
the narrative's attack entries on the same date supply the times, in
order, as long as the counts agree; otherwise each attack is flagged.
Hawaiian time, typed `VW` (or `VX`), is read as GMT minus 10½ hours.

A ship contact table with dates but no times (Finback Patrol 5) takes each
contact's time from the narrative entry headed with its number ("Contact
#6-7"). Table rows that still have no time show on the map on their date
but stay off the track, since they can't be put in order along it. When a
table's times are in a zone the report doesn't print, `patrol.yml` can set
it: `table_zones: { SUMMARY OF SUBMARINE ATTACKS: Z }`.

Reports from mid-1943 give each attack on a TORPEDO ATTACK DATA form (a
target-data page and a torpedo-data page) instead of a summary table. Gemini
transcribes those pages verbatim into `attacks-01.md` (prompt
`3-attack-forms.md`). The converter takes the attack's time, zone, date, latitude and
longitude from the form's "Time: ... Lat. ... Long. ..." line and the target
and damage lines from the rest, and keeps both pages as typed in the detail
card, tube by tube, for the torpedo research.

## Tonnage scoreboard

The map ranks boats by tonnage sunk as of the date on the timeline, so
they overtake one another as the war goes on. Each patrol's figures come
from the `tonnage` list in its `patrol.yml`, one line per ship:

```yaml
tonnage:
  - { date: 10/6/43, time: 0913, zone: Z, target: AO, result: sunk, tons: 10000,
      basis: claimed, source: "Attack 8, page 23" }
```

- `result` is `sunk` or `damaged`. Damaged tonnage shows under the bar
  but isn't ranked.
- `basis` is `claimed` (the captain's claim in the report), `credited`
  (COMSUBPAC's credit in the endorsement) or `postwar` (JANAC or later).
  The map never adds different bases together; when more than one is
  entered, a menu switches between them.
- Without a date, the ship counts at the end of the patrol.
- `ships` is the number of ships in the line (default 1). Leave it blank
  for a patrol total where the count isn't recorded.
- A patrol with no surviving report can still count: give its
  `patrol.yml` `report_found: no`, a `period` with start and end dates,
  and its tonnage. It appears on the scoreboard but draws nothing on the
  chart (see `sources/SS-230/P02`).
- Count each ship once. If several attacks claim the same ship, enter it
  at the attack that sank it.

## Positions from landmarks

Reports often give a position as a bearing and distance from a charted
feature ("9 miles NE of MINAMI JIMA"). In `patrol.yml` such an entry has
`from`, `bearing` and `distance` in place of `lat` and `lon`. The
converter works out the position from the landmark's entry under
`landmarks` in `sources/reference.yml`. These positions show on the map
with a dashed outline, are flagged as estimates, and stay off the track
line, since the report didn't record them as the boat's own position.

Entries tagged `rescue` (lifeguard duty) get their own marker. So do
entries tagged `counterattack` (depth charges, bombs or gunfire against
the boat), which can also carry `charges` (how many) and `damage` (what
the boat suffered, verbatim).

Entries from Part VIII (Anti-Submarine Measures) carry `part: VIII`. When
one describes the same incident as a narrative entry of the same kind
within 90 minutes, the converter folds it into that entry: its account,
charge count and damage appear in the same detail card, not as a second
marker. Part VIII incidents the narrative doesn't mention stay as their
own entries.

A contact table with an attacked Yes/No column shows the "Yes" rows as
attacks, unless the report also has an attack summary table, which then
supplies the attacks (the contact rows stay contacts). If the table doesn't say how, they're shown as torpedo attacks
and flagged to check against the narrative. A narrative attack entry within
three hours of such a row is folded into it: the marker sits at the
table's recorded position and the detail card carries the narrative.

Entries tagged `rendezvous` (a meeting at sea with another U.S. or Allied
boat, such as Silversides and Guardfish exchanging recognition signals on
19 June 1943) get their own marker, and `with` names the other vessel. When
the contact table records the same meeting (the other boat named in the row,
within an hour), the marker takes the table's position and the row's
details, and the row isn't drawn separately. The two boats aren't linked on
the map.

Entries tagged `notable` (medical emergencies, casualties, equipment
casualties and the like) are kept in full. Dated entries with no
position still appear in the patrol log, marked as not shown on the
chart.

A hand entry in `patrol.yml` with `replaces: { date: 22 December, page: 1 }`
(any fields of the Gemini entry, as Gemini wrote them) takes that entry's
place, e.g. to put back in full an entry Gemini summarized. It keeps that
entry's position in the narrative, so a missing zone letter is taken from
the entries around it.

If Gemini labels the narrative with the wrong zone, `zone_fix: { K: L }`
in `patrol.yml` corrects it for every narrative entry.

## Between patrols: refit, overhaul and training

The fleet status strip under the map shows each boat as a row: patrols
(solid; outlined where not yet transcribed), and what the boat was doing
in between. That comes from `sources/status/` (see its README):

- **War diary listings.** Each COMSUBPAC "Disposition of Forces" listing
  is one file, generated from the vault transcriptions by
  `tools/import_war_diary.py`, listing boats under the war diary's own
  headings ("Under refit at Pearl Harbor", "Enroute patrol stations..."
  and so on). Each listing shows as a tick (dashed where the page gives no
  date and the importer dated it by position); the diary's changes of
  command show as diamonds. The status it gives is drawn lightly for up to 8 days
  either side, or through to the next listing that says the same thing.
  That spread is inference, and the map labels it so.
- **Dated periods.** A refit or overhaul with start and end dates from a
  patrol report, the endorsement or DANFS goes in `periods.yml` with its
  source. These draw solid and take precedence over the inferred spread.

While a boat is in port, the chart shows it at that port with its
status, and the scoreboard shows a status chip. See `sources/status/README.md`.

## Entries without a position

A narrative entry with a time but no position is placed on the track
between the recorded positions either side, as long as those are no more
than 24 hours apart. It shows with a dashed outline and a flag saying
it's an estimate. Over longer gaps the straight line says too little
about where the boat was, so those entries stay in the data but off the
chart.

## Recorded positions of the boat

A table whose title mentions density layers, bathythermograph
observations, noon positions or positions is read as the boat's own
positions, not as contacts. Its rows join the track line as small dots,
stay out of the patrol log, and keep all their columns (layer depth,
temperature and so on) for the detail card.

## What gets flagged

The map shows a "review" marker on any entry with an open question.
Flags come from four places:

- **The transcriber:** Gemini's Flags column and anything in `patrol.yml`.
- **The reviewer:** notes in `review.yml`. Delete a note once it's settled.
- **The report:** footnotes printed under a table (`# Should have been 3
  hits`), attached to the entries that carry the marker.
- **The converter:** missing zone letters (the previous entry's zone is
  assumed), run-together coordinates, more hits than torpedoes fired, a
  firing range greater than the initial range, a position whose last
  figure looks like decimal minutes rather than seconds, unrecognized
  column headings, and positions it can't read.

Times are converted from the report's zone letter to GMT so patrols in
different zones play back on one timeline. When several patrols are
shown, playback skips the gaps between them.

## Focusing on one patrol

Click a patrol's track to bring it forward: the other patrols dim, the
patrol log lists only that patrol, and a chip at the top left of the map
names it. Click the track again, click empty sea, press Esc or use the
chip's × to show everything again. With a patrol in focus, opening a
marker on a dimmed patrol moves the focus to that patrol.

A focused patrol also gets a dotted box around its patrol area (its
contacts and attacks, leaving out sightings more than 400 nm from the rest,
which are usually on passage). Clicking the box zooms in and opens the first
entry in the area; the card's Previous and Next buttons (or the arrow keys)
step through every charted entry of the patrol in time order, moving the
timeline with them.

## Viewing it locally

The map loads its data with `fetch`, so it needs a web server:

```
python -m http.server
```

then open http://localhost:8000.

## Publishing

GitHub Pages can serve this repository as it is (Settings → Pages →
Deploy from branch → `main`, root). On a free GitHub plan the repository
must be public for Pages to work.

## Sources

Patrol reports: U.S. Navy war patrol reports, WWII. Coastlines: Natural
Earth, public domain, via the `world-atlas` package.
