# Fleet status snapshots

Each file transcribes one "Disposition of Forces" listing from the
COMSUBPAC (Task Force 17) war diary, which gives every boat's status on
a given date, usually the 1st, the 15th and the end of the month. Keep
the diary's own headings and wording; `status` is our short code for
the heading, used for colors on the map.

Status codes: patrol, refit, overhaul, modernization, training,
other_task_force.

A snapshot is a Documented Fact for its date. The map shades the
stretches between snapshots (and between a snapshot and a patrol's
departure or return) as inferred.

Exact start and end dates from other sources (a report's prologue, an
endorsement, DANFS) go in `periods.yml` and override the inference.

Boat names are matched to hull numbers through `boats` in
`../reference.yml`; boats not listed there are kept by name.
