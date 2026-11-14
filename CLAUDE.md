# COMSUBPAC Patrol Plot

Animated map of U.S. submarine war patrols, built from the war patrol
reports. A Sarpedon Society project, served as-is by GitHub Pages (`main`,
root). `README.md` is the full reference; this file is the working summary.
When they disagree, the README and the code win; fix this file.

## Layout

- `sources/` transcriptions and hand data. Scripts never edit it.
  - `reference.yml` boats, ports, landmarks, map place names
  - `inventory.yml` per-patrol status (missing / available / transcribed / verified / mapped)
  - `index/INDEX_SS.<hull>.<n>.md` Matt's per-patrol index notes from the vault, copied unchanged; converter attaches them as `index` and prints mismatches
  - `<hull>/P<nn>/` `patrol.yml` (hand), `gemini-NN.yml` (narrative), `contacts-NN.md` (tables), `attacks-NN.md`
    (attack forms), `review.yml` (open questions). The three transcription files keep these names whatever
    produced them: raw Gemini on the older patrols, the local OCR pipeline (below) from Silversides 9 on.
  - `status/` fleet status between patrols; `war-diary/` is generated
- `tools/convert.py` sources/ -> data/ (needs Python 3 + pyyaml)
- `tools/import_war_diary.py` vault war diary -> `sources/status/war-diary/`
- `tools/range-bearing.html` browser plotter for "N miles, bearing X from LANDMARK" entries; reads `landmarks` from `reference.yml`, outputs `patrol.yml` event entries
- `data/` generated: `manifest.json`, `status.json`, `patrols/*.json`. `base/land-50m.json` is third-party.
- `prompts/gemini-transcription.md` the Gemini prompt (three outputs); it also defines the format of the three files
- `media/<hull>/P<nn>/` drawings from the reports (crops of the Fold3 download), listed under `figures:` in `patrol.yml`
- `sketches/<hull>-P<nn>.html` an animated version of a report drawing (README, "Animated drawings"). One hand-written,
  self-contained page per drawing, not generated; `animation:` on the figure in `patrol.yml` links it from the lightbox.
  `?embed` for iframes on sarpedon.org, `&t=<seconds>` to open at one attack. First: Trigger Patrol 6 (`SS-237-P06.html`)
- `index.html` the whole front end; loads data with `fetch`. `?patrol=SS-236-P06` opens on one patrol;
  `&embed` adds map-and-timeline only, for iframes in the sarpedon.org patrol histories (README)

Preview: `python -m http.server`, then http://localhost:8000.

## Rules

- Never hand-edit `data/` or `sources/status/war-diary/`. Fix the source, re-run.
- Gemini patrols: save Gemini output exactly as given (fences and all): `gemini-01.yml`,
  `contacts-01.md`, `attacks-01.md`, numbered by batch. The converter
  combines batches in order. Never "clean up" these raw files.
- Local OCR patrols: the raw files are the OCR notes in `qwen-bonsai-outputs/` (never edited);
  the three source files are Claude's transcription from them (see Transcription pipeline).
- Corrections go in `patrol.yml`, which takes precedence over Gemini:
  `replaces: { date:, page: }` to swap an entry, `zone_fix: { K: L }`,
  `table_zones:`, hand `departure` / `arrival`.
  Table cell wrong in `contacts-NN.md`: `row_fixes: { <entry no.>: { <heading>: <value> } }`.
  A figure the report itself types impossibly (28-20 N among fixes at 25 N): keep it as typed and plot a
  best guess with `row_estimates: { <entry no.>: { <heading>: { value:, note: } } }`; the record is flagged
  "Editorial estimate, not the report's figure" with the typed value and the note (Silversides Patrol 11).
  Text wrong on an attack form: `form_fixes: [{ attack: n, old:, new: }]`.
  Both add a "Corrected by hand" flag; the raw files stay as saved.
- Tables and attack forms can be transcribed by Claude from the scan JPGs instead of Gemini (Silversides and Trigger
  Patrol 8): the file opens with a note saying so, uses the same names (`contacts-NN.md`, `attacks-NN.md`), and the
  Gemini read is kept beside it as `check-contacts-NN.md` / `check-attacks-NN.md`, which the converter ignores.
- Transcription is verbatim. Do not correct, normalize or infer. Cells in
  ⟦ ⟧ and everything in a Flags column get checked against the report.
- Open questions go in `review.yml` (entries numbered through the whole
  `contacts.md`); delete a note once settled.
- Tonnage is entered by hand in `patrol.yml` `tonnage:` (`result` sunk or
  damaged; `basis` claimed / credited / postwar). Count each ship once.
- Torpedo attack result (solid = at least one hit, hollow = none) comes from
  the report's hits column; otherwise `patrol.yml` `results: { A13: miss }`,
  keyed by the id on the detail card. Hand entries win; duds count as misses.
- A new boat goes in `sources/reference.yml` `boats`; new ports in `ports`,
  labelled places in `places`, charted features in `landmarks`.
- Update the patrol's line in `sources/inventory.yml`.
- Tables titled density / bathythermograph / noon positions / positions are
  read as the boat's own positions: they join the track as dots and keep
  every column for the detail card.

## Transcription pipeline (local OCR, from Silversides 9 on)

The plan is to do the whole Gato class this way, working from collated PDFs of each boat's reports.
1. Every page JPG of a complete report is read by two local models: Qwen3-VL-8B (primary) and
   Ternary-Bonsai-2-27B (check). The results are compiled into one note per patrol:
   `C:\Users\uncle\Desktop\ClaudeCode\qwen-bonsai-outputs\<hull>-<Boat>\<hull> <Boat> - War Patrol NN - OCR.md`.
   For each page it holds the Qwen working text, the number and text disagreements («» marks
   the spots), and Bonsai's full read. The frontmatter lists pages where a model ran away or
   was cut off (`needs_hand_or_gemini`, `bonsai_cut_off`).
2. Claude reads the whole note and gives Matt a numbered list of reads to check against the scan.
   The list covers:
   - every gap left by a runaway or cut-off;
   - every disagreement touching a date, time, zone, position, course or speed, tube or hit;
   - positions that imply an implausible speed or conflict with the narrative;
   - density, bathythermograph and position tables, whose rows join the track. The two
     reads often pair latitudes and longitudes with the wrong rows there, so ask for whole
     tables when they are scrambled.

   Settle without asking only what the report itself fixes (sequence of times, column totals).
3. Matt types the readings. Claude writes `gemini-01.yml`, `contacts-01.md`, `attacks-01.md` in
   the usual formats (`prompts/gemini-transcription.md`), verbatim to the report, not to either
   model:
   - where the models agree, take the Qwen text;
   - where they disagree, use Matt's reading, or for plain character garble (`ISTA NDS`,
     `Surfacd`), the read the other model and the context support;
   - flag every hand reading as "Read by hand from the scan";
   - a discrepancy inside the report itself still stays as typed (`row_estimates`,
     `review.yml`).
4. Provenance header: YAML frontmatter at the top of all three files, then a short prose note. In
   `gemini-NN.yml` the YAML itself must sit inside a ```yaml fence: the loader reads only the fenced
   block, so the frontmatter and prose outside it are ignored (unfenced, a `---` block would break it).
   Do not write "page N" in the header: the table reader takes it as a page number.
   Silversides 9 (`sources/SS-236/P09/`) is the worked example.
   ```
   transcription: Claude, from local OCR (two reads compared) and hand readings
   ocr_note: qwen-bonsai-outputs/<hull>-<Boat>/<hull> <Boat> - War Patrol NN - OCR.md
   ocr_primary: qwen3-vl-8b-instruct
   ocr_verify: ternary-bonsai-2-27b
   hand_reads: Matt, <date>
   compiled: <date>
   ```
5. No `check-*` files: the second read already lives in the OCR note.

## Adding a patrol

1. Transcription files -> `sources/<hull>/P<nn>/`: raw Gemini output, or the OCR pipeline above.
2. Write `patrol.yml` by hand: metadata, `period`, departure/arrival, tonnage, corrections.
3. Verify against the report; log open questions in `review.yml`.
4. `python tools/convert.py` (prints one line per patrol with its flag count).
5. Check in the browser, update `inventory.yml`, then commit `sources/` and `data/` together.

## Animated drawings (`sketches/`)

Worked example: `sketches/SS-237-P06.html` (Dornin's sketch of the 21 September 1943 convoy attack).
- Everything is traced in pixel coordinates on the cleaned scan (`media/.../attack-sketch-cleaned.jpg`, shown underneath),
  so a point can be checked against the drawing. Tracks are lists of traced points; a vessel always points along its track.
- Evidence by line style: solid = attack forms, dashed = traced from the drawing, dotted = inferred. Say in the notes
  under the player what is inferred (speed along a track, anything the drawing does not show).
- Where the drawing and the forms differ (hull heading at a firing position), follow the drawing and note the form's figure.
- Captions: the report's own words, read from the scan, with the page; mark anything else as a summary (`q: false`).
  Never quote a `[SUMMARY]` entry from a transcription as the report's words.
- Timing is in seconds of action (`s`). Playback slows automatically so each caption can be read (`READ_WPS`).
- Bump the "rev." number shown beside the controls on every change, so a stale browser copy is obvious.
- After writing files to Matt's computer, read them back and compare: a write can report success without landing.

## Vault

The transcription source material lives in the Gato vault, outside this repo:
`C:\Users\uncle\Desktop\Gato-class-vault\Gato-Class\`.
- `Gemini Transcriptions\<Boat>\<Number word>\` holds Gemini outputs as
  saved from chat (e.g. `Silversides\Five\gemini-01.yml.md`,
  `Contacts.md`). The repo copies drop the `.md` suffix and use the
  numbered names above.
- Vault access is approved, read and write. **Never delete anything.**
- A factual inconsistency worth investigating gets a callout note, not a
  silent fix. Record it, don't resolve it.

## Working notes

Checking a new patrol (lessons from Silversides 7, Trigger 7, Finback 7):
- Before saving Gemini output: every narrative entry needs a date (the
  converter carries one forward, flagged); no `[cite: N]`, CJK or Cyrillic
  in dates (a chat that ran too long: rerun in a fresh chat); page range
  matches the PDF sent (no duplicated batch).
- Contact tables are often in GCT (Z) while the narrative is in a zone
  letter: convert and cross-check times and positions both ways. Where
  they disagree, ask Matt to read the scan; he answers with hand readings.
- Hand readings go in `patrol.yml` (`row_fixes`, `form_fixes`, `replaces`) on Gemini patrols;
  on OCR patrols they go straight into Claude's transcription, flagged.
  A discrepancy inside the report itself stays as typed, with the evidence
  in `review.yml`.
- After converting, check: every record has a time, torpedoes fired match
  the forms, and no track leg needs an implausible speed.
- Matt's index note for the patrol (`sources/index/`) gives report number,
  dates, bases, miles and fuel; the converter prints any mismatch.

Gemini notes (older patrols only):
- Send Gemini JPG page images, not the stitched PDF: Gemini reads a PDF's hidden
  OCR text layer (identical misspellings across fresh chats, degree signs read
  as 0, `[cite: N]` markers). Finback 8 was rerun from images.
- One report per Gemini chat; a fresh chat per report.
- Two-part reports (an Addenda with its own page and attack numbering, Trigger 10): give the Addenda's narrative
  pages as A1, A2 ...; head its attack forms with the next free number ('attack 2') and say so in Flags.
- Torpedoes fired come from every "Tubes Fired" line of a form (all pages), typed "#1 #2" or bare "6 5 4".
- Work in short sessions (one patrol each) to keep context use low.
