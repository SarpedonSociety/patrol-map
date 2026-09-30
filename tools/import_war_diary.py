"""Import COMSUBPAC war diary "Disposition of Forces" listings from the
vault transcriptions into sources/status/war-diary/.

    python tools/import_war_diary.py "<vault>/Primary Source/Task Force Seventeen"

Reads every .md file under the folder (YYYY-MM subfolders), finds each
"Disposition of Forces" listing and each "Changes:" entry, and writes

    sources/status/war-diary/<YYYY-MM-DD>.yml   one per listing
    sources/status/war-diary/changes.yml        dated changes of command

Only the diary's own words are carried over (headings, boat names, task
unit numbers, change entries), never transcriber notes. A listing whose
page gives no as-of date is dated by its place in the volume (first
listing = 1st of the month, a listing followed by the endorsement = last
day of the month, otherwise the 15th) and marked `date_stated: false`.
Re-run whenever the vault changes; the output is rebuilt from scratch.
"""
import calendar
import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sources" / "status" / "war-diary"

MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
START = re.compile(r"^\s*Disposition of Forces\b[^\n]*", re.M)
END = re.compile(
    r"^\s*(```|#|TRANSCRIBER NOTES|Approved|[-–]\s*\d+\s*[-–]\s*$|S\.\s*S\.\s*MURRAY|\*\*|>|\||---\s*$)", re.M
)
PATROL_HEAD = re.compile(r"Enroute patrol stations,?\s*on patrol,?\s*or\s*enroute from patrol stations\s*[.:]?", re.I)
HEAD = re.compile(r"(?<![A-Za-z])([A-Z][a-z][A-Za-z ,\-]*?)\s*:")
NAME = re.compile(r"^((?:[A-Z][A-Z0-9\-]*)(?:\s+[A-Z][A-Z0-9\-]*)*)\b(.*)$")
UNIT = re.compile(r"([A-Z][A-Z0-9\-]*(?:\s[A-Z][A-Z0-9\-]*)*)\s*\((\d+\.\d+(?:\.\d+)?)\)")
SIGNATURE = re.compile(r"Approved|LOCKWOOD|Chief of Staff", re.I)


def stated_date(line):
    m = re.search(r"\(\s*([A-Z][a-z]+)\s+(\d{1,2}),?\s+(\d{4})", line)
    if m and m.group(1).lower() in MONTHS:
        return date(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2)))
    m = re.search(r"\(\s*(\d{1,2})\s+([A-Z][a-z]+),?\s+(\d{4})", line)
    if m and m.group(2).lower() in MONTHS:
        return date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    return None


def sheet_before(text, pos):
    """Image sheet number of the page a listing sits on, from the nearest
    'Page N' heading or the file's source_file line."""
    best = None
    for m in re.finditer(r"^#*\s*Page\s+(\d+)\b|sheet\s+(\d+)|Page\s+(\d+)\.jpg", text[:pos], re.M | re.I):
        best = int(next(g for g in m.groups() if g))
    if best is None:
        m = re.search(r"source_files?:.*?Page\s+(\d+)", text)
        best = int(m.group(1)) if m else None
    return best


MULTIWORD_OK = re.compile(r"^(FLYING FISH|SEA [A-Z]+|[A-Z]+ [A-Z]+ (?:BAY|SOUND))$")


def classify(heading):
    h = re.sub(r"\s+", "", heading.lower())
    place = None
    m = re.search(r"\bat\s+([A-Z][A-Za-z ]+)$", heading) or re.search(r"(San Francisco Bay area|West Coast|Mare Island)", heading, re.I)
    if m:
        place = m.group(1).strip()
        place = "San Francisco Bay area" if place.lower() == "san francisco bay area" else place.title() if place.isupper() else place
    if "modernization" in h:
        return "modernization", "San Francisco Bay area" if "sanfrancisco" in h or not place else place
    if "overhaul" in h:
        return "overhaul", place
    if "refit" in h:
        return "refit", place
    if "patrol" in h:
        return "patrol", None
    if "training" in h:
        return "training", place
    if "othertaskforce" in h:
        return "other_task_force", None
    if h.startswith("enroute"):
        return "transit", None
    if h.startswith("miscellaneous"):
        return "miscellaneous", None
    return "other", place


def item_status(note):
    n = note.lower()
    if "enroute" in n:
        return "transit", None
    if "training" in n:
        return "training", ("West Coast" if "west coast" in n else None)
    m = re.search(r"\bat\s+([A-Z][A-Za-z ]+)", note)
    if m:
        return "miscellaneous", m.group(1).strip()
    return None, None


split_notes = []


def parse_listing(block):
    body = block.split("Submarines:", 1)[1] if "Submarines:" in block else block
    body = re.sub(r"\s+", " ", body).strip()
    body = re.sub(r"\b([A-Z]{2,})- ([A-Z]{2,})\b", r"\1\2", body)  # word broken across a line
    body = PATROL_HEAD.sub("Enroute patrol stations, on patrol, or enroute from patrol stations:", body)
    heads = list(HEAD.finditer(body))
    groups = []
    for i, h in enumerate(heads):
        heading = h.group(1).strip()
        content = body[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(body)].strip()
        status, place = classify(heading)
        group = {"heading": heading, "status": status}
        if place:
            group["place"] = place
        if status == "patrol":
            group["boats"] = {m.group(1).strip(): m.group(2) for m in UNIT.finditer(content)}
        else:
            boats, notes, item = [], {}, {}
            for piece in re.split(r",|;|\.\s|\.$|\b[Aa][Nn][Dd]\b", content):
                piece = piece.strip(" .")
                m = NAME.match(piece)
                if not m:
                    continue
                name, note = m.group(1).strip(), m.group(2).strip(" ,.")
                names = [name]
                if " " in name and not MULTIWORD_OK.match(name):
                    # Two boat names with the comma lost, e.g. "SILVERSIDES SCAMP".
                    names = name.split()
                    split_notes.append(f"'{name}' read as {len(names)} boats: {', '.join(names)}")
                boats += names
                if note:
                    notes[names[-1]] = note
                    st, pl = item_status(note)
                    if st:
                        item[names[-1]] = {"status": st, **({"place": pl} if pl else {})}
            group["boats"] = boats
            if notes:
                group["notes"] = notes
            if item:
                group["item_status"] = item
        groups.append(group)
    return groups


def parse_changes(text):
    out = []
    for sec in re.finditer(r"^\s*Changes:\s*$(.*?)(?=^\s*(```|TRANSCRIBER NOTES|#|---\s*$|[-–]\s*\d+\s*[-–]\s*$))", text, re.M | re.S):
        body = re.sub(r"[ \t]*\n[ \t]*\n?", "\n", sec.group(1))
        body = re.sub(r"\s+", " ", body)
        for m in re.finditer(r"([A-Z][a-z]+ \d{1,2}, \d{4})\s*-\s*(.*?)(?=[A-Z][a-z]+ \d{1,2}, \d{4}\s*-|$)", body):
            d = stated_date("(" + m.group(1))
            if d:
                out.append({"date": d.isoformat(), "text": m.group(2).strip()})
    return out


def main(folder):
    folder = Path(folder)
    listings, changes = {}, {}
    for path in sorted(folder.rglob("*.md")):
        month = re.search(r"(\d{4})-(\d{2})", str(path.relative_to(folder)))
        if not month:
            continue
        yr, mo = int(month.group(1)), int(month.group(2))
        text = path.read_text(encoding="utf-8", errors="replace")
        for c in parse_changes(text):
            changes[(c["date"], c["text"])] = c
        starts = [m for m in START.finditer(text)]
        undated_seen = 0
        for i, m in enumerate(starts):
            nxt = starts[i + 1].start() if i + 1 < len(starts) else len(text)
            rest = text[m.end():nxt]
            end = END.search(rest)
            block = rest[: end.start()] if end else rest
            if "Submarines:" not in block and not UNIT.search(block):
                continue
            d = stated_date(m.group(0))
            sheet = sheet_before(text, m.start())
            basis = "stated on the page"
            if d is None:
                if undated_seen == 0 and (sheet is None or sheet <= 5):
                    d, basis = date(yr, mo, 1), "not stated; first listing in the volume, taken as the 1st of the month"
                elif SIGNATURE.search(rest):
                    d, basis = date(yr, mo, calendar.monthrange(yr, mo)[1]), "not stated; listing closes the volume above the endorsement, taken as the last day of the month"
                else:
                    d, basis = date(yr, mo, 15), "not stated; mid-volume listing, taken as the 15th"
                undated_seen += 1
            split_notes.clear()
            groups = parse_listing(block)
            key = d.isoformat()
            entry = listings.setdefault(key, {
                "date": key, "date_stated": basis == "stated on the page", "date_basis": basis,
                "source": "Report for Commander Task Force Seventeen (Commander Submarine Force, Pacific Fleet), War Diary, Disposition of Forces",
                "sheets": [], "vault_files": [], "groups": [],
            })
            if sheet and sheet not in entry["sheets"]:
                entry["sheets"].append(sheet)
            rel = str(path.relative_to(folder)).replace("\\", "/")
            if rel not in entry["vault_files"]:
                entry["vault_files"].append(rel)
            # The same listing can be transcribed in two files; keep the first
            # copy of each heading, but add continuation pages.
            have = {g["heading"].lower() for g in entry["groups"]}
            entry["groups"] += [g for g in groups if g["heading"].lower() not in have]
            if split_notes:
                entry.setdefault("names_split", []).extend(split_notes)
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.yml"):
        old.unlink()
    for key, entry in sorted(listings.items()):
        seen, dup = {}, []
        for g in entry["groups"]:
            for b in (g["boats"] if isinstance(g["boats"], list) else list(g["boats"])):
                if b in seen and seen[b] != g["heading"]:
                    dup.append(f"{b} under both '{seen[b]}' and '{g['heading']}'")
                seen.setdefault(b, g["heading"])
        if dup:
            entry["listed_twice"] = dup
        header = ("# Generated by tools/import_war_diary.py from the vault transcription.\n"
                  "# Edit the vault, not this file, and re-run the importer.\n")
        (OUT / f"{key}.yml").write_text(header + yaml.safe_dump(entry, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
        n = sum(len(g["boats"]) for g in entry["groups"])
        print(f"{key}  {'stated ' if entry['date_stated'] else 'INFERRED'}  {len(entry['groups'])} groups  {n} boats  {', '.join(entry['vault_files'])}")
    ch = sorted(changes.values(), key=lambda c: c["date"])
    (OUT / "changes.yml").write_text(
        "# Generated by tools/import_war_diary.py: 'Changes:' entries from the war diary, verbatim.\n"
        + yaml.safe_dump(ch, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    print(f"{len(listings)} listings, {len(ch)} changes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/Task Force Seventeen")
