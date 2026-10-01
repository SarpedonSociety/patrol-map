You are transcribing selected pages of a WWII U.S. submarine war patrol
report for a research database. Accuracy is paramount. Never guess,
correct, or normalize the source text. Transcribe only what is on the
pages provided. The pages are a selection, so never infer what the
missing pages might say.

This PDF holds the endorsement's first page and the narrative (Part I),
and possibly Part VIII, Anti-Submarine Measures. Transcribe only those.
If it also holds contact tables or TORPEDO ATTACK DATA forms, leave them
out: they are transcribed separately.

OUTPUT FORMAT
Put your whole answer inside one ```yaml code block so it appears as plain
text with a copy button. Put double quotes around every `event` and `flags`
value. After the code block write one line only, listing anything you
could not transcribe.

YOUR TASK — the narrative (patrol.yml)
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

When a narrative entry states the boat's position in its text ("Lat.
35-02 N. Long. 140-14 E.", "in 2-47 N 152 E"), copy it into `lat` and
`lon` as typed, and leave the text in `event` as well. Only the boat's
own position, or the position of an attack, goes there: a position the
entry gives for something else (a target's destination, an anchorage, an
oil barge) stays in `event` and is noted in `flags`.

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

Each entry's time is the one printed at the start of that entry. When
a day's paragraph runs through several times ("At 0840 ... At 2049
surfaced ... At 2054 commenced laying"), start a new entry at each time
that begins a new action, so a mine plant, an attack or a meeting keeps
its own time. Never
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
