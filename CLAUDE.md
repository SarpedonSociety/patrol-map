# COMSUBPAC Patrol Plot

Animated map of U.S. submarine war patrols, built from the war patrol
reports. A Sarpedon Society project, served as-is by GitHub Pages (`main`,
root). `README.md` is the full reference; this file is the working summary.
When they disagree, the README and the code win; fix this file.

## Layout

- `sources/` transcriptions and hand data. Scripts never edit it.
  - `reference.yml` boats, ports, landmarks, map place names
  - `inventory.yml` per-patrol status (missing / available / transcribed / verified / mapped)
  - `<hull>/P<nn>/` `patrol.yml` (hand), `gemini-NN.yml`, `contacts-NN.md`, `attacks-NN.md` (raw Gemini), `review.yml` (open questions)
  - `status/` fleet status between patrols; `war-diary/` is generated
- `tools/convert.py` sources/ -> data/ (needs Python 3 + pyyaml)
- `tools/import_war_diary.py` vault war diary -> `sources/status/war-diary/`
- `data/` generated: `manifest.json`, `status.json`, `patrols/*.json`. `base/land-50m.json` is third-party.
- `prompts/gemini-transcription.md` the Gemini prompt (three outputs)
- `index.html` the whole front end; loads data with `fetch`

Preview: `python -m http.server`, then http://localhost:8000.

## Rules

- Never hand-edit `data/` or `sources/status/war-diary/`. Fix the source, re-run.
- Save Gemini output exactly as given (fences and all): `gemini-01.yml`,
  `contacts-01.md`, `attacks-01.md`, numbered by batch. The converter
  combines batches in order. Never "clean up" these raw files.
- Corrections go in `patrol.yml`, which takes precedence over Gemini:
  `replaces: { date:, page: }` to swap an entry, `zone_fix: { K: L }`,
  `table_zones:`, hand `departure` / `arrival`.
- Transcription is verbatim. Do not correct, normalize or infer. Cells in
  ⟦ ⟧ and everything in a Flags column get checked against the report.
- Open questions go in `review.yml` (entries numbered through the whole
  `contacts.md`); delete a note once settled.
- Tonnage is entered by hand in `patrol.yml` `tonnage:` (`result` sunk or
  damaged; `basis` claimed / credited / postwar). Count each ship once.
- A new boat goes in `sources/reference.yml` `boats`; new ports in `ports`,
  labelled places in `places`, charted features in `landmarks`.
- Update the patrol's line in `sources/inventory.yml`.
- Tables titled density / bathythermograph / noon positions / positions are
  read as the boat's own positions: they join the track as dots and keep
  every column for the detail card.

## Adding a patrol

1. Gemini output -> `sources/<hull>/P<nn>/` (raw files above).
2. Write `patrol.yml` by hand: metadata, `period`, departure/arrival, tonnage, corrections.
3. Verify against the report; log open questions in `review.yml`.
4. `python tools/convert.py` (prints one line per patrol with its flag count).
5. Check in the browser, update `inventory.yml`, then commit `sources/` and `data/` together.

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

- One report per Gemini chat; a fresh chat per report.
- Work in short sessions (one patrol each) to keep context use low.
