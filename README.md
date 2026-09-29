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
tools/convert.py              Turns sources/ into data/
data/
  manifest.json               List of patrols on the map (generated)
  patrols/SS-236-P01.json     One file per patrol (generated)
  base/land-50m.json          Coastlines (Natural Earth via world-atlas)
prompts/gemini-transcription.md   First-pass transcription prompt
index.html                    The map
```

## Adding a patrol

1. Build a PDF of the pages that matter: the first page of the COMSUBPAC
   endorsement, the narrative entries with positions, course changes,
   departure and arrival, and the contact and attack tables (keep each
   page's Fold3 source sheet). Run it through Gemini with
   `prompts/gemini-transcription.md`. It returns a `patrol.yml` and a
   `contacts.md` with the report's tables.
2. Save both in a new folder, e.g. `sources/SS-283/P03/`.
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

Entries tagged `rescue` (lifeguard duty) get their own marker.

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
