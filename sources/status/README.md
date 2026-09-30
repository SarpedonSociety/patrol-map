# Fleet status

What each boat was doing between patrols, from the COMSUBPAC (Commander
Task Force Seventeen) war diary and other dated sources.

## war-diary/ (generated)

One file per "Disposition of Forces" listing (`YYYY-MM-DD.yml`), plus
`changes.yml` with the diary's dated changes of command. These are built
from the transcriptions in the Gato vault
(`Primary Source/Task Force Seventeen/YYYY-MM/`) by

    python tools/import_war_diary.py "<vault>/Primary Source/Task Force Seventeen"

Don't edit them by hand: correct the vault transcription and re-run the
importer, then `python tools/convert.py`. Only the diary's own words come
across (headings, boat names, task unit numbers, notes such as "enroute
Mare Island to Pearl"); transcriber notes stay in the vault.

Listings usually fall on the 1st, the 15th and the last day of the month.
Where the page states its date ("Disposition of Forces: (June 15, 1943)")
that date is used. Where it doesn't, the importer dates it by position in
the volume and marks it `date_stated: false` with the reasoning in
`date_basis`: the first listing (sheet 4) is the 1st of the month, a
listing closed by the endorsement is the last day, anything else the
15th. The map draws those listings with a dashed tick.

Each file also records:
- `listed_twice`: a boat the diary lists under two headings on the same
  date (it happens: HALIBUT at both Pearl and Midway on 15 August 1943).
  Both entries are kept.
- `names_split`: two names run together without a comma
  ("SILVERSIDES SCAMP"), read as two boats. Check against the scan.

Headings map to status codes for the map's colors: patrol, refit,
overhaul, modernization, training, other_task_force, transit (the
"Enroute ... to ..." headings and "enroute" notes under Miscellaneous),
miscellaneous, other.

## periods.yml (by hand)

Exact start and end dates from other sources (a report's prologue, an
endorsement, DANFS), each with its source. These draw solid and take
precedence over the war diary shading.

## index.yml (by hand)

The Task Organization legend: what each task group number meant, by
period.

A listing is a Documented Fact for its date. The shading between
listings, and between a listing and a patrol's departure or return, is
inference, and the map labels it so. Boats are matched to hull numbers
through `boats` in `../reference.yml`; only those boats reach the map.
