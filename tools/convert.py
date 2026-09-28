#!/usr/bin/env python3
"""
Build the patrol map data from the transcriptions in sources/.

    python tools/convert.py            # rebuild every patrol
    python tools/convert.py SS-236/P01 # rebuild one patrol

For each folder sources/<hull>/<patrol>/ it reads:
    patrol.yml    metadata, departure/arrival, narrative events (Part I)
    contacts.md   the contact and attack table (Parts V and VII), verbatim
    review.yml    optional reviewer notes attached to table rows

and writes:
    data/patrols/<hull>-<patrol>.json
    data/manifest.json   (list of every patrol on the map)

Nothing in sources/ is ever modified. Verbatim readings are kept alongside
the parsed values, and anything the script had to interpret is flagged.
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
OUT = ROOT / "data"

MONTHS = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}

# Nautical time zone letters -> hours ahead of GMT (J is not used).
ZONES = {"Z": 0}
for i, letter in enumerate("ABCDEFGHI"):
    ZONES[letter] = i + 1
for i, letter in enumerate("KLM"):
    ZONES[letter] = i + 10
for i, letter in enumerate("NOPQRSTUVWXY"):
    ZONES[letter] = -(i + 1)

# Column headings seen so far, normalized -> field name.
# Covers the hand-transcription layouts and the Gemini prompt layout.
COLUMNS = {
    "timedate": "time_date", "time": "time", "zone": "zone", "date": "date",
    "latlong": "lat_long", "location": "lat_long", "latverbatim": "lat", "lat": "lat",
    "longverbatim": "lon", "long": "lon", "lon": "lon",
    "page": "page", "type": "type", "initialrange": "initial_range",
    "estcourse": "course", "course": "course", "estspeed": "speed", "speed": "speed",
    "description": "description", "weapon": "weapon", "depth": "depth",
    "track": "track", "gyro": "gyro", "gryo": "gyro", "firingrange": "firing_range",
    "range": "firing_range", "hits": "hits", "remarks": "remarks", "flags": "flags",
    "altitude": "altitude", "contactno": "contact_no", "attack": "attack_no",
}
# Fallback: first keyword found in the normalized heading wins.
KEYWORDS = [
    ("timedate", "time_date"), ("torpedoesfired", "fired"), ("torpsfired", "fired"),
    ("torpfired", "fired"), ("roundsfired", "fired"), ("numbersunk", "sunk"),
    ("damaged", "damaged"), ("typeoftarget", "type"), ("typeofattack", "attack_type"),
    ("draft", "draft"), ("depthsetting", "depth"), ("boworstern", "tube"),
    ("trackangle", "track"), ("gyro", "gyro"), ("targetspeed", "speed"),
    ("interval", "interval"), ("spread", "spread"), ("satisfactory", "performance"),
    ("performance", "performance"), ("initialrange", "initial_range"),
]
UNCERTAIN = re.compile(r"⟦[^⟧]*⟧")


# ---------------------------------------------------------------- parsing

def read_tables(path):
    """Return every Markdown table in a file as dicts with the heading,
    page and any 'Remarks:' note that sits around it. A table whose first
    heading is 'Attack' (attacks as columns, as in the attack summary) is
    turned the right way round."""
    tables, cur = [], None
    section, page = "", None
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text.startswith("|"):
            cells = [c.strip() for c in text.strip("|").split("|")]
            if cur is None:
                cur = {"headers": cells, "rows": [], "section": section, "page": page, "notes": []}
                tables.append(cur)
            elif all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            else:
                cur["rows"].append(cells)
            continue
        cur_done, cur = cur, None
        if not text:
            continue
        m = re.search(r"\bpage\s+(\d+)", text, re.I)
        if m:
            page = m.group(1)
        heading = text.lstrip("#").strip()
        if text.startswith("#") and not re.fullmatch(r"page\s+\d+.*", heading, re.I):
            section = heading
        if re.match(r"remarks\s*:", text, re.I):
            target = cur_done or (tables[-1] if tables else None)
            if target:
                target["notes"].append(re.sub(r"^remarks\s*:\s*", "", text, flags=re.I))
    for t in tables:
        if t["headers"] and re.sub(r"[^a-z]", "", t["headers"][0].lower()) == "attack":
            labels = [t["headers"][0]] + [r[0] for r in t["rows"]]
            cols = []
            for j in range(1, len(t["headers"])):
                cols.append([t["headers"][j]] + [r[j] if j < len(r) else "" for r in t["rows"]])
            t["headers"], t["rows"], t["transposed"] = labels, cols, True
    return tables


def field_name(heading):
    key = re.sub(r"[^a-z]", "", heading.lower())
    if key in COLUMNS:
        return COLUMNS[key]
    for word, name in KEYWORDS:
        if word in key:
            return name
    return None


def parse_time_date(text):
    """'0805L 10MAY', '0310(K) 10/4/43', '1855 10/3/43' -> (time, zone, date)."""
    m = re.fullmatch(r"(\d{3,4})\s*\(?([A-Z])?\)?\s+(\d{1,2}\s*[A-Z]{3}|\d{1,2}/\d{1,2}/\d{2,4})",
                     text.strip().upper())
    if not m:
        return None, None, None
    return m.group(1).zfill(4), m.group(2), m.group(3).replace(" ", "")


def parse_coord(text, default_hemi, is_lat):
    """'33-13-30N' or '151-57' -> decimal degrees."""
    if not text:
        return None
    hemi = re.search(r"[NSEW]", text.upper())
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text)]
    if not nums:
        return None
    value = nums[0] + (nums[1] / 60 if len(nums) > 1 else 0) + (nums[2] / 3600 if len(nums) > 2 else 0)
    letter = hemi.group(0) if hemi else default_hemi
    if letter in ("S", "W"):
        value = -value
    limit = 90 if is_lat else 180
    return round(value, 5) if abs(value) <= limit else None


def split_lat_long(text):
    """Split a combined 'Lat/Long' cell. Returns (lat, lon, flag)."""
    text = text.strip()
    parts = text.split()
    if len(parts) == 2:
        return parts[0], parts[1], None
    nums = re.findall(r"\d+", text)
    if len(nums) == 4:  # e.g. 33-20-140-52
        lat, lon = f"{nums[0]}-{nums[1]}", f"{nums[2]}-{nums[3]}"
        return lat, lon, f"Lat and long run together in the transcription ({text}); read as {lat} / {lon}."
    if len(nums) == 6:
        lat, lon = "-".join(nums[:3]), "-".join(nums[3:])
        return lat, lon, f"Lat and long run together in the transcription ({text}); read as {lat} / {lon}."
    return None, None, f"Could not read a position from '{text}'."


def parse_date(date_str, year, first_month):
    """'10MAY' (year from patrol.yml) or '10/4/43' (M/D/YY) -> (y, m, d)."""
    d = (date_str or "").upper().replace(" ", "")
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", d)
    if m:
        y = int(m.group(3))
        return (y + 1900 if y < 100 else y), int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(\d{1,2})([A-Z]{3})", d)
    if not m or m.group(2) not in MONTHS:
        return None
    month = MONTHS[m.group(2)]
    yr = year + (1 if first_month and month < first_month - 6 else 0)
    return yr, month, int(m.group(1))


def to_utc(date_str, time_str, zone, year, first_month):
    """Build a GMT timestamp from report date, time and zone letter."""
    ymd = parse_date(date_str, year, first_month)
    if not ymd:
        return None
    hh, mm = (int(time_str[:2]), int(time_str[2:])) if time_str else (12, 0)
    local = datetime(*ymd, hh % 24, mm % 60)
    offset = ZONES.get(zone or "", 0)
    return (local - timedelta(hours=offset)).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def classify(fields, section):
    weapon = (fields.get("weapon") or "").upper()
    fired = fields.get("fired") or ""
    if weapon.startswith("GUN") or re.search(r'"|/|\brds?\b|rounds', fired, re.I):
        return "gun"
    if weapon.startswith("TORP") or re.match(r"\s*\d+", fired):
        return "torpedo"
    if "altitude" in fields or "AIRCRAFT" in section.upper():
        return "aircraft"
    return "sighting"


def as_int(text):
    m = re.match(r"\s*(\d+)", text or "")
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- building

def blanks_to_none(value):
    if isinstance(value, dict):
        return {k: blanks_to_none(v) for k, v in value.items()}
    if isinstance(value, list):
        return [blanks_to_none(v) for v in value]
    return None if value == "" else value


def build_patrol(folder, ref):
    # BaseLoader keeps every value as typed text, so a time like 0700 isn't
    # read as an octal number.
    meta = blanks_to_none(yaml.load((folder / "patrol.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader))
    review = {}
    if (folder / "review.yml").exists():
        review = yaml.safe_load((folder / "review.yml").read_text(encoding="utf-8")) or {}
    row_notes = {int(k): v for k, v in (review.get("rows") or {}).items()}

    hull = meta["boat"]
    num = int(meta["patrol"])
    pid = f"{hull}-P{num:02d}"
    period_start = str((meta.get("period") or {}).get("start") or "")
    year = int(meta.get("year") or period_start[:4] or 1942)
    hemi = meta.get("default_hemisphere") or {"lat": "N", "lon": "E"}
    boat = ref["boats"].get(hull, {})
    dep = meta.get("departure") or {}
    arr = meta.get("arrival") or {}
    first_month = None
    if dep.get("date"):
        dm = re.search(r"[A-Z]{3}", str(dep["date"]).upper())
        first_month = MONTHS.get(dm.group(0)) if dm else None

    def when(date, time, zone):
        t = str(time).zfill(4) if time not in (None, "") else None
        return to_utc(str(date or ""), t, zone, year, first_month)

    records = []

    # Narrative events (Part I)
    for i, ev in enumerate(meta.get("events") or [], start=1):
        flags = [ev["flags"]] if ev.get("flags") else []
        if not ev.get("zone"):
            flags.append("No time zone recorded; treated as GMT.")
        lat = parse_coord(str(ev.get("lat") or ""), hemi["lat"], True)
        lon = parse_coord(str(ev.get("lon") or ""), hemi["lon"], False)
        records.append({
            "id": f"{pid}-N{i:02d}", "source": "Part I narrative", "kind": "event",
            "page": ev.get("page"), "zone": ev.get("zone"),
            "local": " ".join(str(x) for x in (ev.get("time"), ev.get("zone"), ev.get("date")) if x),
            "utc": when(ev.get("date"), ev.get("time"), ev.get("zone")),
            "position_verbatim": " ".join(str(x) for x in (ev.get("lat"), ev.get("lon")) if x),
            "lat": lat, "lon": lon,
            "type": "Narrative", "title": ev.get("title") or "Narrative entry",
            "fields": {"event": ev.get("event")},
            "flags": flags,
        })

    # Contact, aircraft and attack tables (Parts V, VI and VII)
    contacts = folder / "contacts.md"
    tables = read_tables(contacts) if contacts.exists() else []
    entry = 0
    last_zone = None
    for table in tables:
        headers = table["headers"]
        names = [field_name(h) for h in headers]
        unknown = [h for h, n in zip(headers, names) if n is None]
        gct = any(re.search(r"\bG[CM]T\b", h, re.I) for h in headers)
        section = table["section"].strip() or "Contacts / attacks table"
        source = section[:1].upper() + section[1:].lower() if section.isupper() else section
        for n, cells in enumerate(table["rows"]):
            entry += 1
            f = {nm: (cells[i] if i < len(cells) else "") for i, nm in enumerate(names) if nm}
            flags = [f"Unrecognized heading(s) ignored: {', '.join(unknown)}"] if unknown and n == 0 else []
            if f.get("flags"):
                flags.append(f"Transcriber: {f['flags']}")
            if entry in row_notes:
                flags.append(f"Review: {row_notes[entry]}")

            if "time_date" in f:
                t, z, d = parse_time_date(f["time_date"])
                if t is None:
                    flags.append(f"Could not read time/date '{f['time_date']}'.")
            else:
                t = re.sub(r"\D", "", f.get("time", "")) or None
                z = (f.get("zone") or "").strip().upper() or None
                d = (f.get("date") or "").replace(" ", "").upper() or None
            if gct and z is None:
                z = "Z"
            if z is None and t is not None:
                if last_zone:
                    flags.append(f"No zone letter on this entry; zone {last_zone} assumed from the previous entry.")
                    z = last_zone
                else:
                    flags.append("No zone letter on this entry; treated as GMT.")
            if z and z not in ZONES:
                flags.append(f"Unknown zone letter '{z}'.")
            if not gct:
                last_zone = z or last_zone

            if "lat_long" in f:
                lat_s, lon_s, pflag = split_lat_long(f["lat_long"])
                pos_verbatim = f["lat_long"]
                if pflag:
                    flags.append(pflag)
            else:
                lat_s, lon_s = f.get("lat"), f.get("lon")
                pos_verbatim = " ".join(x for x in (lat_s, lon_s) if x)
            for part in (lat_s, lon_s):
                if part and re.search(r"\d+-\d{1,2}-\d(?!\d)", part):
                    flags.append(f"'{part}' reads as degrees-minutes-seconds, but the last figure is a single "
                                 f"digit; it may be decimal minutes. Read here as seconds.")
            lat = parse_coord(UNCERTAIN.sub(lambda m: m.group(0)[1:-1], lat_s or ""), hemi["lat"], True)
            lon = parse_coord(UNCERTAIN.sub(lambda m: m.group(0)[1:-1], lon_s or ""), hemi["lon"], False)
            if lat is None or lon is None:
                flags.append("No usable position.")

            for key, value in f.items():
                if UNCERTAIN.search(value or ""):
                    flags.append(f"Uncertain reading in {key.replace('_', ' ')}: {value}")

            # Footnotes like "# Should have been 3 hits, * see VII ..." attach
            # only to entries carrying that marker.
            for note in table["notes"]:
                for mark, text in re.findall(r"([#*†‡])\s*([^#*†‡]+)", note):
                    if any(mark in c for c in cells[1:] if table.get("transposed")) or \
                       (not table.get("transposed") and any(mark in c for c in cells)):
                        flags.append(f"Report note {mark}: {text.strip().rstrip(',')}")

            kind = classify(f, section)
            fired, hits = as_int(f.get("fired")), as_int(f.get("hits"))
            if kind == "torpedo" and fired is not None and hits is not None and hits > fired:
                flags.append(f"More hits ({hits}) than torpedoes fired ({fired}).")
            ir, fr = as_int(f.get("initial_range")), as_int(f.get("firing_range"))
            if kind == "torpedo" and ir and fr and fr > ir:
                flags.append(f"Firing range ({fr}) is greater than initial range ({ir}).")

            typ = f.get("type", "")
            if f.get("attack_no"):
                title = f"Attack {f['attack_no']}" + (f" · {typ}" if typ else "")
            elif f.get("contact_no"):
                title = f"Contact {f['contact_no']}" + (f" · {typ}" if typ else "")
            else:
                title = typ
            zone_label = "GCT" if gct else z
            keep = {k: v for k, v in f.items()
                    if k not in ("time_date", "time", "zone", "date", "lat_long", "lat", "lon", "page",
                                 "flags", "attack_no", "contact_no") and v}
            records.append({
                "id": f"{pid}-C{entry:02d}", "source": source, "row": entry, "kind": kind,
                "page": f.get("page") or table["page"], "zone": z,
                "local": " ".join(x for x in (t, zone_label, d) if x) if t else f.get("time_date", ""),
                "utc": to_utc(d or "", t, z, year, first_month),
                "position_verbatim": pos_verbatim, "lat": lat, "lon": lon,
                "type": typ, "title": title, "fields": keep, "flags": flags,
            })

    records.sort(key=lambda x: (x["utc"] or "9999", x["id"]))

    # Departure and arrival
    def endpoint(block, label):
        if not block or not block.get("port"):
            return None
        port = ref["ports"].get(block["port"])
        flags = [block["flags"]] if block.get("flags") else []
        if not port:
            flags.append(f"No reference position for port '{block['port']}' in sources/reference.yml.")
        if not block.get("time"):
            flags.append("Time not recorded; placed at noon.")
        return {
            "label": label, "port": block["port"],
            "utc": when(block.get("date"), block.get("time"), block.get("zone")),
            "local": " ".join(str(x) for x in (block.get("time"), block.get("zone"), block.get("date")) if x),
            "lat": port["lat"] if port else None, "lon": port["lon"] if port else None,
            "page": block.get("page"), "flags": flags,
        }

    departure = endpoint(dep, "Departed")
    arrival = endpoint(arr, "Arrived")

    # Track: every documented position in time order, anchored at the ports.
    track = []
    if departure and departure["lat"] is not None and departure["utc"]:
        track.append({"lat": departure["lat"], "lon": departure["lon"], "utc": departure["utc"], "basis": "reference"})
    for rec in records:
        if rec["lat"] is None or rec["lon"] is None or not rec["utc"]:
            continue
        if track and track[-1]["lat"] == rec["lat"] and track[-1]["lon"] == rec["lon"]:
            continue
        track.append({"lat": rec["lat"], "lon": rec["lon"], "utc": rec["utc"], "basis": "documented", "ref": rec["id"]})
    if arrival and arrival["lat"] is not None and arrival["utc"]:
        track.append({"lat": arrival["lat"], "lon": arrival["lon"], "utc": arrival["utc"], "basis": "reference"})

    # Tonnage for the scoreboard
    tonnage = []
    for i, t in enumerate(meta.get("tonnage") or [], start=1):
        result = str(t.get("result") or "").lower()
        basis = str(t.get("basis") or "").lower()
        tons = as_int(str(t.get("tons") or ""))
        # No ships key: one ship. A blank ships value: count not recorded (totals).
        ships = as_int(str(t["ships"])) if t.get("ships") is not None else (None if "ships" in t else 1)
        flags = []
        if result not in ("sunk", "damaged"):
            flags.append(f"Result '{t.get('result')}' should be sunk or damaged.")
        if basis not in ("claimed", "credited", "postwar"):
            flags.append(f"Basis '{t.get('basis')}' should be claimed, credited or postwar.")
        if tons is None:
            flags.append("No tonnage figure.")
        utc = when(t.get("date"), t.get("time"), t.get("zone")) if t.get("date") else None
        tonnage.append({
            "id": f"{pid}-T{i:02d}", "utc": utc, "target": t.get("target"), "name": t.get("name"),
            "result": result, "tons": tons, "ships": ships, "basis": basis, "source": t.get("source"), "flags": flags,
        })

    torps = [r for r in records if r["kind"] == "torpedo"]
    summary = {
        "records": len(records),
        "sightings": sum(r["kind"] == "sighting" for r in records),
        "aircraft": sum(r["kind"] == "aircraft" for r in records),
        "torpedo_attacks": len(torps),
        "torpedoes_fired": sum(as_int(r["fields"].get("fired")) or 0 for r in torps),
        "gun_actions": sum(r["kind"] == "gun" for r in records),
        "flagged": sum(bool(r["flags"]) for r in records)
                   + sum(bool(e and e["flags"]) for e in (departure, arrival)),
    }
    times = [p["utc"] for p in track] + [r["utc"] for r in records if r["utc"]]
    period = meta.get("period") or {}
    for key in ("start", "end"):
        if period.get(key):
            m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(period[key]))
            if m:
                times.append(f"{period[key]}T12:00:00Z")
    for t in tonnage:
        if t["utc"] is None and times:
            t["utc"] = max(times)
    return {
        "id": pid, "boat": hull, "name": boat.get("name", hull), "class": boat.get("class"),
        "patrol": num, "year": year, "report": meta.get("report"),
        "commanding_officer": meta.get("commanding_officer"),
        "citation": {k: v for k, v in (meta.get("citation") or {}).items() if v not in (None, "")},
        "fold3_images": {str(k): str(v) for k, v in (meta.get("fold3_images") or {}).items() if v},
        "miles_steamed": meta.get("miles_steamed"), "fuel_expended": meta.get("fuel_expended"),
        "start": min(times) if times else None, "end": max(times) if times else None,
        "departure": departure, "arrival": arrival,
        "report_found": str(meta.get("report_found", "yes")).lower() not in ("no", "false"),
        "summary": summary, "track": track, "records": records, "tonnage": tonnage,
    }


def main(selected):
    ref = yaml.safe_load((SOURCES / "reference.yml").read_text(encoding="utf-8"))
    folders = sorted(p.parent for p in SOURCES.glob("*/*/patrol.yml"))
    if selected:
        folders = [f for f in folders if any(str(f).endswith(s) for s in selected)]
    (OUT / "patrols").mkdir(parents=True, exist_ok=True)
    for folder in folders:
        patrol = build_patrol(folder, ref)
        if not patrol["start"]:
            print(f"{patrol['id']}  skipped: no dates. Add period: {{start: YYYY-MM-DD, end: YYYY-MM-DD}} to patrol.yml")
            (OUT / "patrols" / f"{patrol['id']}.json").unlink(missing_ok=True)
            continue
        path = OUT / "patrols" / f"{patrol['id']}.json"
        path.write_text(json.dumps(patrol, indent=1, ensure_ascii=False), encoding="utf-8")
        s = patrol["summary"]
        print(f"{patrol['id']}  {patrol['name']:<12} {s['records']:>3} records  "
              f"{s['torpedo_attacks']} torpedo attacks  {s['gun_actions']} gun  {s['flagged']} flagged")

    # Manifest always lists every built patrol, not just the ones rebuilt now.
    manifest = []
    for path in sorted((OUT / "patrols").glob("*.json")):
        p = json.loads(path.read_text(encoding="utf-8"))
        manifest.append({k: p[k] for k in ("id", "boat", "name", "class", "patrol", "year", "start", "end", "summary")}
                        | {"file": f"patrols/{path.name}"})
    (OUT / "manifest.json").write_text(json.dumps({
        "places": ref.get("places") or [],
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "patrols": manifest,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"manifest: {len(manifest)} patrol(s)")


if __name__ == "__main__":
    main(sys.argv[1:])
