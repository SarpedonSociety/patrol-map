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
import math
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
# Hawaiian time (GMT minus 10.5), written "VW" in Pearl Harbor reports.
ZONES["VW"] = -10.5
ZONES["VX"] = -10.5   # Finback Patrol 5 types Hawaiian time VX

# Column headings seen so far, normalized -> field name.
# Covers the hand-transcription layouts and the Gemini prompt layout.
COLUMNS = {
    "timedate": "time_date", "time": "time", "zone": "zone", "date": "date",
    "latlong": "lat_long", "location": "lat_long", "position": "lat_long", "positions": "lat_long", "latverbatim": "lat", "lat": "lat",
    "longverbatim": "lon", "long": "lon", "lon": "lon",
    "page": "page", "type": "type", "initialrange": "initial_range",
    "estcourse": "course", "course": "course", "estspeed": "speed", "speed": "speed",
    "description": "description", "weapon": "weapon", "depth": "depth",
    "track": "track", "gyro": "gyro", "gryo": "gyro", "firingrange": "firing_range",
    "range": "firing_range", "hits": "hits", "remarks": "remarks", "flags": "flags",
    "altitude": "altitude", "alt": "altitude", "contactno": "contact_no", "no": "contact_no",
    "attack": "attack_no", "intrange": "initial_range", "minrange": "min_range", "beart": "bearing",
    "bear": "bearing", "bearing": "bearing", "crse": "course", "spd": "speed", "rks": "remarks",
    "lead": "lead", "timegct": "time", "locationlatlong": "lat_long", "datelocal": "date",
    "rangesighted": "initial_range", "rangeclosest": "min_range", "target": "type",
    "types": "type", "howcontacted": "contacted",
    # OCR typos in a heading ("Timo Date", "Typo") kept by the transcriber (Silversides Patrol 6).
    "timodate": "time_date", "timedato": "time_date", "timodato": "time_date", "typo": "type",
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
    ("attacked", "attack_no"), ("attackyes", "attack_no"),
    # "RANGE (1st TORPEDO)" in attack summaries; digits are stripped first.
    ("rangest", "firing_range"), ("speedtarget", "speed"), ("coursespeed", "course"),
    ("crsspd", "course"), ("crsespd", "course"),   # "Est. Crs&Spd", "Est. Crse&Spd": course and speed in one cell
]
# Tables that record the boat's own positions rather than contacts:
# density layer / bathythermograph observations, noon positions and the like.
FIX_SECTION = re.compile(r"density|bathythermo|noon position|own position|\bpositions\b", re.I)

# Narrative entry tags -> map marker kind and default title.
TAG_KIND = {"rescue": "rescue", "attack": "torpedo", "gun": "gun", "minefield": "minefield",
            "counterattack": "counterattack", "notable": "event", "rendezvous": "rendezvous"}
TAG_TITLE = {"rescue": "Aviator rescue", "attack": "Torpedo attack (narrative)", "gun": "Gun action (narrative)",
             "minefield": "Minefield laid", "counterattack": "Depth-charged", "notable": "Notable event",
             "rendezvous": "Rendezvous"}

UNCERTAIN = re.compile(r"⟦[^⟧]*⟧")


# ---------------------------------------------------------------- parsing

def read_tables(path):
    """Return every Markdown table in a file as dicts with the heading,
    page and any 'Remarks:' note that sits around it. A table whose first
    heading is 'Attack' (attacks as columns, as in the attack summary) is
    turned the right way round. Gemini's ``` fences are ignored."""
    tables, cur = [], None
    section, page = "", None
    for line in plain(path.read_text(encoding="utf-8")).splitlines():
        if line.strip().startswith("```"):
            continue
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
            heads = t["headers"]
            # A Flags column (the transcriber's notes, one per field) is not an
            # attack. Each note goes to the attacks it names ("Attack II A"),
            # or to every attack if it names none.
            flag_col = len(heads) - 1 if len(heads) > 2 and re.sub(r"[^a-z]", "", heads[-1].lower()) == "flags" else None
            attack_cols = [j for j in range(1, len(heads)) if j != flag_col]
            notes = {j: [] for j in attack_cols}
            if flag_col is not None:
                ids = {j: re.sub(r"\s+", "", heads[j]).upper() for j in attack_cols}
                for r in t["rows"]:
                    note = (r[flag_col] if flag_col < len(r) else "").strip()
                    if not note:
                        continue
                    named = {re.sub(r"\s+", "", m).upper() for m in re.findall(r"Attack\s+([IVX]+(?:\s+[A-Z](?![A-Za-z]))?|\d+(?:\s*\(?[a-z]\)?)?)", note)}
                    hit = [j for j in attack_cols if ids[j] in named]
                    if not named and re.match(r"heading\s", note, re.I):
                        continue   # a note on the table's own heading, not on any attack
                    for j in (hit or attack_cols):
                        notes[j].append(f"{r[0]}: {note}")
            labels = [heads[0]] + [r[0] for r in t["rows"]] + (["Flags"] if flag_col is not None else [])
            cols = []
            for j in attack_cols:
                col = [heads[j]] + [r[j] if j < len(r) else "" for r in t["rows"]]
                if flag_col is not None:
                    col.append("; ".join(notes[j]))
                cols.append(col)
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
    text = re.sub(r"(?<=[A-Z])\.", "", unbracket(plain(text)).strip().upper())
    text = re.sub(r"SOPT", "SEPT", text)   # e read as o
    text = re.sub(r"(?<![A-Z])\.*UG(?=\s*\d)", "AUG", text)   # a carbon copy that lost the A of "Aug"
    m = re.fullmatch(r"(\d{3,4})\s*\(?([A-Z])?\)?\s+(\d{1,2}\s*[A-Z]{3}[A-Z]*|[A-Z]{3}[A-Z]*\s*\d{1,2}"
                     r"|\d{1,2}/\d{1,2}/\d{2,4})", text)
    if not m:
        return None, None, None
    date = m.group(3).replace(" ", "")
    date = re.sub(r"^(\d{1,2}[A-Z]{3})[A-Z]*$", r"\1", date)
    return m.group(1).zfill(4), m.group(2), date


# Greek and Cyrillic letters that look like Latin ones turn up in OCR output.
HOMOGLYPHS = str.maketrans({"Ε": "E", "Ν": "N", "Ѕ": "S", "Е": "E", "Н": "H", "Α": "A", "В": "B",
                            "а": "a", "с": "c", "е": "e", "о": "o", "р": "p", "х": "x", "у": "y"})


def plain(text):
    if text is None:
        return text
    return re.sub(r"\[cite:[^\]]*\]", "", str(text)).translate(HOMOGLYPHS)


def unbracket(text):
    """Drop the ⟦ ⟧ uncertainty marks, keeping the reading inside them."""
    return re.sub(r"[⟦⟧]", "", str(text or ""))


def parse_coord(text, default_hemi, is_lat):
    """'33-13-30N' or '151-57' -> decimal degrees."""
    text = plain(text)
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
    text = re.sub(r"<br\s*/?>|;|\bLat\.?|\bLong\.?|\bLon\.?", " ", unbracket(plain(text)), flags=re.I)
    text = re.sub(r"\(\s*\)", " ", text)   # what's left of "(lat)" / "(long)" labels
    # "L-8°-32'(N) 134°-00(E)": drop the L- prefix and degree/minute marks,
    # and take the hemisphere out of its brackets.
    text = re.sub(r"^\s*L\s*-\s*", "", text)
    text = re.sub(r"(?<=\d)\s*°\s*-?\s*", "-", text).replace("'", "").replace("’", "")
    text = re.sub(r"\s*\(\s*([NSEW])\s*\)", r" \1", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    pair = re.fullmatch(r"(\d+-\d+(?:\.\d+)?(?:-\d+)?)\s*([NS])\.?\s+(\d+-\d+(?:\.\d+)?(?:-\d+)?)\s*([EW])?\.?", text, re.I)
    if pair:
        return pair.group(1) + pair.group(2).upper(), pair.group(3) + (pair.group(4) or "").upper(), None
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


WORD_NUMBERS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty".split())}


def read_attack_forms(path):
    """Read attacks-NN.md: the 1943 TORPEDO ATTACK DATA forms transcribed
    verbatim, one block per page under '### Torpedo attack data, attack n'
    or '### Torpedo data, attack n'. Returns {attack number: {...}}."""
    text = plain(path.read_text(encoding="utf-8"))
    text = "\n".join(l for l in text.splitlines() if not l.strip().startswith("```"))
    forms = {}
    for block in re.split(r"(?m)^###\s+", text)[1:]:
        head, _, body = block.partition("\n")
        m = re.search(r"attack\s*(?:no\.?\s*)?#?\s*(\w+)\s*$", head.strip(), re.I)
        if not m:
            continue
        key = m.group(1).lower()
        num = WORD_NUMBERS.get(key, key)
        page = re.search(r"(?m)^\s*Page\s+(\d+)", body)
        body = re.sub(r"(?m)^\s*Page\s+\d+\s*$\n?", "", body).rstrip()
        notes = [l.split(":", 1)[1].strip() for l in body.splitlines() if re.match(r"\s*Flags\s*:", l)]
        body = "\n".join(l for l in body.splitlines() if not re.match(r"\s*Flags\s*:", l)).strip("\n")
        f = forms.setdefault(str(num), {"num": str(num), "pages": [], "flags": []})
        f["flags"] += notes
        if page:
            f["pages"].append(page.group(1))
        kind = "torpedoes" if re.match(r"\s*torpedo\s+data", head, re.I) else "attack"
        f[kind] = body
    return forms


def form_fields(body):
    """'Label: value' lines of a verbatim form, with indented continuation
    lines joined on. Labels are lower-cased; ';' and ',' typed for ':' are
    accepted."""
    out, key = {}, None
    for line in body.splitlines():
        if line.strip() and not re.search(r"[a-z]", line):
            key = None   # a section heading such as OWN SHIP DATA
            continue
        m = re.match(r"\s*([A-Za-z][A-Za-z ()/.'-]{1,40}?)\s*[:;]\s+(.*)$", line)
        if m and not line.startswith("        "):
            key = re.sub(r"\s+", " ", m.group(1).strip().lower())
            out[key] = m.group(2).strip()
        elif key and line.strip() and line.startswith(" "):
            out[key] += " " + line.strip()
        elif not line.strip():
            key = None
    return out


def find_landmark(landmarks, name):
    """Look a landmark up as typed, then without a leading 'the',
    'entrance(s) to' or 'off' ('entrances to Malakal Harbor')."""
    key = str(name or "").strip().lower()
    if key in landmarks:
        return landmarks[key]
    bare = re.sub(r"^(?:the\s+|entrances?\s+to\s+(?:the\s+)?|off\s+)", "", key)
    return landmarks.get(bare)


def parse_date(date_str, year, first_month):
    """'10MAY' (year from patrol.yml) or '10/4/43' (M/D/YY) -> (y, m, d)."""
    d = plain(date_str or "").upper().replace(",", " ").replace(".", " ").strip()
    d = re.sub(r"^(\d{1,2})\s*-\s*\d{1,2}\b(?!\s*-)", r"\1", d)   # "28-31 December" -> first day (not "5-27-43")
    d = re.sub(r"\s+", " ", d)
    words = re.fullmatch(r"([A-Z]{3})[A-Z]*\.?\s+(\d{1,2})(?:\s+(\d{4}))?|(\d{1,2})\s+([A-Z]{3})[A-Z]*\.?(?:\s+(\d{4}))?", d)
    if words:
        mon = words.group(1) or words.group(5)
        day = words.group(2) or words.group(4)
        yr4 = words.group(3) or words.group(6)
        if mon in MONTHS:
            d = f"{int(day)}{mon}"
            if yr4:
                return int(yr4), MONTHS[mon], int(day)
    d = d.replace(" ", "")
    mw = re.fullmatch(r"([A-Z]{3})[A-Z]*(\d{1,2})", d)   # "MAY28", "JUNE1" (a date cell read with spaces removed)
    if mw and mw.group(1) in MONTHS:
        d = f"{int(mw.group(2))}{mw.group(1)}"
    dw = re.fullmatch(r"(\d{1,2})([A-Z]{3})[A-Z]+", d)   # "4JUNE", "11JULY"
    if dw and dw.group(2) in MONTHS:
        d = f"{int(dw.group(1))}{dw.group(2)}"
    m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", d)
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
    digits = re.sub(r"\D", "", time_str.split("-")[0]) if time_str else ""
    if time_str and len(digits) < 3:
        digits = ""
    digits = digits.zfill(4)[:4] if digits else ""
    hh, mm = (int(digits[:2]), int(digits[2:])) if digits else (12, 0)
    try:
        local = datetime(*ymd, hh % 24, mm % 60)
    except ValueError:
        return None
    offset = ZONES.get(zone or "", 0)
    return (local - timedelta(hours=offset)).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


POINTS = ["N", "NBE", "NNE", "NEBN", "NE", "NEBE", "ENE", "EBN", "E", "EBS", "ESE", "SEBE", "SE", "SEBS",
          "SSE", "SBE", "S", "SBW", "SSW", "SWBS", "SW", "SWBW", "WSW", "WBS", "W", "WBN", "WNW", "NWBW",
          "NW", "NWBN", "NNW", "NBW"]


def parse_bearing(text):
    """'NE', 'WSW', 'N by E', '045', '045T' -> degrees true, or None."""
    t = str(text or "").upper()
    for word, letter in (("NORTH", "N"), ("SOUTH", "S"), ("EAST", "E"), ("WEST", "W")):
        t = re.sub(rf"\b{word}(?:ERLY|WARD)?\b", letter, t)   # "north" -> N, "south east" -> SE
    t = re.sub(r"\s+", "", t).replace("BY", "B")
    if not t:
        return None
    m = re.fullmatch(r"(\d{1,3}(?:\.\d+)?)°?T?", t)
    if m:
        return float(m.group(1)) % 360
    return POINTS.index(t) * 11.25 if t in POINTS else None


NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty".split())}


def parse_distance(text):
    """'9 miles', '1.5', 'about two miles', '3000 yards' -> nautical miles, or None."""
    t = str(text or "").lower()
    for word, n in NUMBER_WORDS.items():
        t = re.sub(rf"\b{word}\b", str(n), t)
    m = re.search(r"(\d+(?:\.\d+)?)", t)
    if not m:
        return None
    value = float(m.group(1))
    return value / 2025.4 if "yard" in t or "yds" in t else value


def offset_position(lat, lon, bearing, nm):
    """Point nm nautical miles from lat/lon on a true bearing (short distances)."""
    rad = math.radians(bearing)
    dlat = nm * math.cos(rad) / 60
    dlon = nm * math.sin(rad) / (60 * math.cos(math.radians(lat)))
    return round(lat + dlat, 5), round(lon + dlon, 5)


def classify(fields, section):
    weapon = (fields.get("weapon") or "").upper()
    fired = fields.get("fired") or ""
    torpedo_words = re.search(r"\bmk\b|torp|\btor\b|torpex|\btnt\b", fired, re.I)
    if weapon.startswith("GUN") or (not torpedo_words and re.search(r'"|/|\brds?\b|rounds', fired, re.I)):
        return "gun"
    if weapon.startswith("TORP") or re.match(r"\s*\d+", fired):
        return "torpedo"
    remarks = f"{fields.get('remarks') or ''} {fields.get('description') or ''}"
    if re.search(r"battle surface|\brds\.? of|\brounds of", remarks, re.I):
        return "gun"
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


ORDINALS = {w: i for i, w in enumerate(
    "first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth "
    "fourteenth fifteenth sixteenth".split(), start=1)}


def load_yaml_text(path, gemini=False):
    """Read a YAML file as typed text. Accepts Gemini output pasted as-is,
    with a 'YAML' label and ``` fences around it."""
    text = path.read_text(encoding="utf-8")
    fenced = re.search(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1)
    if gemini:
        text = quote_text_fields(text)
    # BaseLoader keeps every value as typed text, so a time like 0700 isn't
    # read as an octal number.
    return blanks_to_none(yaml.load(text, Loader=yaml.BaseLoader)) or {}


TEXT_FIELDS = ("event", "flags", "report", "nara_catalog_title", "title", "note", "source")


def quote_text_fields(text):
    """Put quotes round free-text values Gemini left bare. Without them,
    '[SUMMARY] ...' or 'the following Marus: AIKOKU' break the YAML."""
    out = []
    for line in text.splitlines():
        m = re.match(r"^(\s*(?:-\s+)?)(%s):[ \t]+(.+?)\s*$" % "|".join(TEXT_FIELDS), line)
        v = m.group(3) if m else ""
        whole = re.fullmatch(r'"(?:[^"\\]|\\.)*"', v) or re.fullmatch(r"'(?:[^']|'')*'", v)
        if m and not whole and not re.match(r"^([{|>]|null$|~$)", v):
            value = m.group(3).replace("\\", "\\\\").replace('"', '\\"')
            line = f'{m.group(1)}{m.group(2)}: "{value}"'
        out.append(line)
    return "\n".join(out)


def merge_meta(manual, batches):
    """patrol.yml (hand-entered) wins; gemini-*.yml batches fill the gaps.
    Events and Fold3 image numbers from every file are combined."""
    out = {}
    for src in batches + [manual]:
        for key, value in src.items():
            if key in ("events",):
                continue
            if isinstance(value, dict):
                base = dict(out.get(key) or {})
                for k, v in value.items():
                    if v is not None and (src is manual or base.get(k) is None):
                        base[k] = v
                out[key] = base
            elif value is not None and (src is manual or out.get(key) is None):
                out[key] = value
    # A hand entry with `replaces: { date: ..., page: ... }` (or `time:`)
    # stands in for the Gemini entry it names, e.g. a summarized entry
    # transcribed again in full.
    targets = [e["replaces"] for e in (manual.get("events") or []) if isinstance(e.get("replaces"), dict)]

    def replaced(ev):
        for t in targets:
            if all(str(ev.get(k) or "").strip().lower() == str(v).strip().lower() for k, v in t.items() if v is not None):
                return True
        return False
    # A replacing hand entry takes the place of the entry it replaces, so a
    # missing zone letter is carried forward from the entries around it, not
    # from the end of the report. Other hand entries go at the end.
    manual_events = manual.get("events") or []
    placed = set()
    events = []
    for src in batches:
        for e in src.get("events") or []:
            if not replaced(e):
                events.append(e)
                continue
            for i, m in enumerate(manual_events):
                t = m.get("replaces") if isinstance(m.get("replaces"), dict) else None
                if i not in placed and t and all(str(e.get(k) or "").strip().lower() == str(v).strip().lower()
                                                  for k, v in t.items() if v is not None):
                    events.append(m)
                    placed.add(i)
    events += [m for i, m in enumerate(manual_events) if i not in placed]
    out["events"] = events
    return out


def normalize_meta(meta):
    hull = re.search(r"SS\s*-?\s*(\d+)", str(meta.get("boat") or ""), re.I)
    if hull:
        meta["boat"] = f"SS-{hull.group(1)}"
    pat = str(meta.get("patrol") or "").strip().lower()
    num = re.match(r"(\d+)", pat)
    meta["patrol"] = int(num.group(1)) if num else ORDINALS.get(pat.split()[0] if pat else "", 0)
    year = re.search(r"(19\d\d)", str(meta.get("year") or ""))
    meta["year"] = year.group(1) if year else None
    return meta


def build_patrol(folder, ref):
    manual = load_yaml_text(folder / "patrol.yml") if (folder / "patrol.yml").exists() else {}
    batches = [load_yaml_text(p, gemini=True) for p in sorted(folder.glob("gemini-*.yml"))]
    # A contacts batch can open with Gemini's OUTPUT 1 header (e.g. Fold3
    # image numbers for the table pages); use it when it's there.
    for path in sorted(folder.glob("contacts*.md")):
        try:
            head = load_yaml_text(path, gemini=True)
        except yaml.YAMLError:
            head = None
        if isinstance(head, dict):
            batches.append(head)
    meta = normalize_meta(merge_meta(manual, batches))
    review = {}
    if (folder / "review.yml").exists():
        review = yaml.safe_load((folder / "review.yml").read_text(encoding="utf-8")) or {}
    row_notes = {int(k): v for k, v in (review.get("rows") or {}).items()}

    hull = meta["boat"]
    num = int(meta["patrol"])
    if not num:
        raise SystemExit(f"{folder}: couldn't read the patrol number '{meta.get('patrol')}'.")
    pid = f"{hull}-P{num:02d}"
    period_start = str((meta.get("period") or {}).get("start") or "")
    year = int(meta.get("year") or period_start[:4] or 1942)
    hemi = meta.get("default_hemisphere") or {"lat": "N", "lon": "E"}
    boat = ref["boats"].get(hull, {})
    dep = meta.get("departure") or {}
    arr = meta.get("arrival") or {}
    first_month = None
    for candidate in [dep.get("date")] + [e.get("date") for e in (meta.get("events") or [])]:
        got = parse_date(str(candidate or ""), year, None)
        if got:
            first_month = got[1]
            break

    def when(date, time, zone):
        t = str(time).zfill(4) if time not in (None, "") else None
        return to_utc(str(date or ""), t, zone, year, first_month)

    records = []

    # Narrative events (Part I)
    landmarks = {k.lower(): v for k, v in (ref.get("landmarks") or {}).items()}
    zone_fix = {str(k).upper(): str(v).upper() for k, v in (meta.get("zone_fix") or {}).items()}
    for block in (dep, arr):
        if block.get("zone") and str(block["zone"]).upper() in zone_fix:
            block["zone"] = zone_fix[str(block["zone"]).upper()]
    last_event_zone = None
    for i, ev in enumerate(meta.get("events") or [], start=1):
        flags = [ev["flags"]] if ev.get("flags") else []
        ev = dict(ev)
        if not ev.get("zone"):
            if not ev.get("time") and ev.get("date"):
                flags.append("No time given; placed at noon GMT on that date.")
            if ev.get("time") and last_event_zone:
                ev["zone"] = last_event_zone
                flags.append(f"No zone letter on this entry; zone {last_event_zone} assumed from the previous entry.")
            elif ev.get("time"):
                flags.append("No time zone recorded; treated as GMT.")
        else:
            if not ev.get("time") and ev.get("date"):
                flags.append("No time given; placed at noon GMT on that date.")
            ev["zone"] = plain(ev["zone"]).strip().upper()
            if ev["zone"] in zone_fix:
                flags.append(f"Zone {ev['zone']} corrected to {zone_fix[ev['zone']]} (zone_fix in patrol.yml).")
                ev["zone"] = zone_fix[ev["zone"]]
            last_event_zone = ev["zone"]
        lat = parse_coord(str(ev.get("lat") or ""), hemi["lat"], True)
        lon = parse_coord(str(ev.get("lon") or ""), hemi["lon"], False)
        position_verbatim = " ".join(str(x) for x in (ev.get("lat"), ev.get("lon")) if x)
        derived = None
        if (lat is None or lon is None) and ev.get("from") and (ev.get("bearing") or ev.get("distance")):
            # Position given relative to a landmark, e.g. "9 miles NE of MINAMI JIMA"
            name = str(ev["from"]).strip()
            position_verbatim = f"{ev.get('distance') or ''} {ev.get('bearing') or ''} of {name}".strip()
            mark = find_landmark(landmarks, name)
            brg, dist = parse_bearing(plain(ev.get("bearing"))), parse_distance(ev.get("distance"))
            # "9 miles NE of X" gives the bearing from the landmark. "X bearing 240,
            # 2 miles" gives the landmark's bearing from the boat, so the boat is
            # on the reciprocal. Numeric bearings are usually the second kind.
            bearing_is = str(ev.get("bearing_is") or "").lower()
            numeric = brg is not None and re.fullmatch(r"\s*\d{1,3}(\.\d+)?\s*°?\s*T?\s*", str(ev.get("bearing")), re.I)
            if bearing_is == "to_landmark":
                brg = (brg + 180) % 360
            elif not bearing_is and numeric:
                flags.append(f"Read as 'bearing {ev.get('bearing')} from {name}'. If the report means {name} bore "
                             f"{ev.get('bearing')} from the boat, set bearing_is: to_landmark.")
            if not mark or mark.get("lat") in (None, "") or mark.get("lon") in (None, ""):
                flags.append(f"No position for landmark '{name}'. Add it to landmarks in sources/reference.yml.")
            elif dist is None and brg is not None:
                lat, lon = float(mark["lat"]), float(mark["lon"])
                derived = {"from": name, "bearing": brg, "distance_nm": None,
                           "landmark": {"lat": lat, "lon": lon}, "landmark_note": mark.get("note")}
                flags.append(f"Position given only as '{position_verbatim.strip()}' with no distance; placed at "
                             f"{name} itself, as a rough estimate.")
            elif brg is None or dist is None:
                flags.append(f"Could not read bearing '{ev.get('bearing')}' or distance '{ev.get('distance')}'.")
            else:
                lat, lon = offset_position(float(mark["lat"]), float(mark["lon"]), brg, dist)
                derived = {"from": name, "bearing": brg, "distance_nm": round(dist, 2),
                           "landmark": {"lat": float(mark["lat"]), "lon": float(mark["lon"])},
                           "landmark_note": mark.get("note")}
                flags.append(f"Position derived from '{position_verbatim}' using a modern landmark position; "
                             f"it is an estimate, not a position recorded in the report.")
                if mark.get("note"):
                    flags.append(f"Landmark: {mark['note']}")
        tag = str(ev.get("tag") or "").lower() or None
        marked = re.search(r"\(\s*\d+\s*(?:st|nd|rd|th)\s+attack\s*\)", f"{ev.get('flags') or ''} {ev.get('event') or ''}", re.I)
        if marked and not tag:
            flags.append(f"The report marks this entry {marked.group(0)} but it has no tag. "
                         f"Add tag: attack, gun or minefield.")
        records.append({
            "id": f"{pid}-N{i:02d}",
            "source": f"Part {str(ev.get('part')).upper()}" if ev.get("part") and str(ev.get("part")).upper() != "I" else "Part I narrative",
            "part": str(ev.get("part") or "I").upper(),
            "kind": TAG_KIND.get(tag, "event"),
            "page": ev.get("page"), "zone": ev.get("zone"),
            "local": " ".join(str(x) for x in (ev.get("time"), ev.get("zone"), ev.get("date")) if x),
            "utc": when(ev.get("date"), ev.get("time"), ev.get("zone")),
            "position_verbatim": position_verbatim, "derived": derived, "tag": tag,
            "local_date": list(parse_date(str(ev.get("date") or ""), year, first_month) or []),
            "has_time": bool(ev.get("time")),
            "lat": lat, "lon": lon,
            "type": "Narrative", "title": ev.get("title") or (
                "Ship hit by mines" if tag == "minefield" and re.search(r"attack\s*\)|\bsunk\b|\bdamaged\b", str(ev.get("event") or ""), re.I)
                else TAG_TITLE.get(tag, "Narrative entry")),
            "fields": {k: v for k, v in (("event", ev.get("event")), ("charges", ev.get("charges")),
                                          ("damage", ev.get("damage")), ("with", ev.get("with"))) if v},
            "flags": flags,
        })

    # Part VIII (anti-submarine measures) often describes the same incident as
    # the narrative. Fold such an entry into the narrative entry of the same
    # kind within 90 minutes, keeping its fuller account, instead of adding a
    # second marker.
    def minutes_apart(a, b):
        ta = datetime.fromisoformat(a.replace("Z", "+00:00"))
        tb = datetime.fromisoformat(b.replace("Z", "+00:00"))
        return abs((ta - tb).total_seconds()) / 60
    folded = []
    for rec in records:
        if rec.get("part") in (None, "I") or not rec["utc"]:
            continue
        same_day = [n for n in records if n.get("part") == "I" and n["kind"] == rec["kind"] and n["utc"]
                    and n.get("local_date") and n.get("local_date") == rec.get("local_date")]
        close = [n for n in records if n.get("part") == "I" and n["kind"] == rec["kind"] and n["utc"]
                 and rec.get("has_time") and minutes_apart(n["utc"], rec["utc"]) <= 90]
        pool = close or ([] if rec.get("has_time") else same_day)
        match = min(pool, key=lambda n: minutes_apart(n["utc"], rec["utc"]), default=None)
        if match:
            match["fields"][f"part_{rec['part'].lower()}"] = rec["fields"].get("event")
            for k in ("charges", "damage"):
                if rec["fields"].get(k) and not match["fields"].get(k):
                    match["fields"][k] = rec["fields"][k]
            if match["lat"] is None and rec["lat"] is not None:
                match["lat"], match["lon"] = rec["lat"], rec["lon"]
            match["flags"].append(f"Part {rec['part']} also describes this incident (page {rec.get('page') or '?'}); "
                                  f"its account is included here.")
            folded.append(rec)
    records = [r for r in records if r not in folded]

    # Contact, aircraft and attack tables (Parts V, VI and VII)
    # contacts.md, or batches contacts-01.md, contacts-02.md ... read in order.
    tables = [t for path in sorted(folder.glob("contacts*.md")) for t in read_tables(path)]
    entry = 0
    narrative_zones = [r["zone"] for r in records if r.get("zone")]
    default_zone = max(set(narrative_zones), key=narrative_zones.count) if narrative_zones else None
    last_zone = None
    has_summary = any(t.get("transposed") for t in tables)
    # "### Torpedoes, attack 3": the torpedo-by-torpedo list from a 1943
    # attack report. Not contacts; attached to that attack below.
    torpedo_lists = {}
    for table in tables:
        m = re.match(r"\s*torpedoes\s*,?\s*attack\s*(?:no\.?\s*)?#?\s*(\w+)", table["section"] or "", re.I)
        if m:
            torpedo_lists[m.group(1).upper()] = table
    for table in tables:
        if table in torpedo_lists.values():
            continue
        headers = table["headers"]
        names = [field_name(h) for h in headers]
        unknown = [h for h, n in zip(headers, names) if n is None]
        gct = any(re.search(r"\bG\.?[CM]\.?T\b", h, re.I) for h in headers)
        # patrol.yml can say which zone a table's times are in when the report
        # doesn't print it, e.g. table_zones: { SUMMARY OF SUBMARINE ATTACKS: Z }
        forced_zone = next((str(v).upper() for k, v in (meta.get("table_zones") or {}).items()
                            if str(k).lower() in (table["section"] or "").lower()), None)
        section = table["section"].strip() or "Contacts / attacks table"
        is_fix = bool(FIX_SECTION.search(section))
        if section.isupper():
            words = [w if re.fullmatch(r"[IVX]+\.?", w) else w.lower() for w in section.split()]
            source = " ".join(words)
            source = source[:1].upper() + source[1:]
        else:
            source = section
        last_position = None
        for n, cells in enumerate(table["rows"]):
            entry += 1
            f = {nm: (cells[i] if i < len(cells) else "") for i, nm in enumerate(names) if nm}
            extra = {h: (cells[i] if i < len(cells) else "") for i, (h, nm) in enumerate(zip(headers, names)) if nm is None}
            flags = [f"Heading(s) not recognized, kept as typed: {', '.join(unknown)}"] if unknown and n == 0 and not is_fix else []
            if f.get("flags"):
                flags.append(f"Transcriber: {f['flags']}")
            if entry in row_notes:
                flags.append(f"Review: {row_notes[entry]}")

            if "time_date" in f:
                t, z, d = parse_time_date(f["time_date"])
                if t is None:
                    only = re.fullmatch(r"\s*(\d{1,2}\s*[A-Za-z]{3}|\d{1,2}/\d{1,2}/\d{2,4})\s*", f["time_date"])
                    if only:
                        d = only.group(1).replace(" ", "").upper()
                    else:
                        flags.append(f"Could not read time/date '{f['time_date']}'.")
            else:
                time_cell = unbracket(plain(f.get("time", "")))
                t = (re.sub(r"\D", "", time_cell) or None)
                t = t.zfill(4)[:4] if t else None
                z = (f.get("zone") or "").strip().upper() or None
                zm = re.search(r"\(\s*([A-Z])\s*\)|\d\s*([A-Z])\b", time_cell.upper())
                if not z and zm:
                    z = zm.group(1) or zm.group(2)
                d = unbracket(plain(f.get("date") or "")).strip()
                both = re.fullmatch(r"(\d{4})\s+(.+)", d) if not t else None
                if both:
                    t, d = both.group(1), both.group(2)
                d = d.replace(" ", "").upper() or None
            if gct and z is None:
                z = "Z"
            if forced_zone and z is None:
                z = forced_zone
                flags.append(f"The table gives no zone; zone {z} set in patrol.yml (table_zones).")
            if t is None and d:
                flags.append("No time recorded; placed at noon GMT on that date.")
            if z is None and t is not None:
                if last_zone:
                    flags.append(f"No zone letter on this entry; zone {last_zone} assumed from the previous entry.")
                    z = last_zone
                elif default_zone:
                    flags.append(f"No zone letter on this entry; zone {default_zone} assumed from the narrative.")
                    z = default_zone
                else:
                    flags.append("No zone letter on this entry; treated as GMT.")
            if z and z not in ZONES:
                flags.append(f"Unknown zone letter '{z}'.")
            if not gct and not forced_zone:
                last_zone = z or last_zone

            derived_pos = None
            if "lat_long" in f:
                cell = f["lat_long"]
                if re.fullmatch(r"\s*(ditto|do\.?|\"|same)\s*", cell or "", re.I) and last_position:
                    flags.append(f"Position given as '{cell.strip()}'; the previous entry's position is used.")
                    cell = last_position
                pos_verbatim = cell
                rel = re.search(r"(?:about\s+)?([\d.]+|[a-z]+)\s+miles?\s+([NSEW]{1,3}|[NSEW]\s*by\s*[NSEW])\s+of\s+(.+)", plain(cell), re.I)
                off = re.fullmatch(r"\s*off\s+(.+?)\s*", plain(cell), re.I)
                if rel or off:
                    name = (rel.group(3) if rel else off.group(1)).strip().rstrip(".")
                    mark = find_landmark(landmarks, name)
                    lat_s = lon_s = None
                    if not mark or mark.get("lat") in (None, ""):
                        flags.append(f"No position for landmark '{name}'. Add it to landmarks in sources/reference.yml.")
                    elif rel and parse_distance(rel.group(1)) is not None and parse_bearing(rel.group(2)) is not None:
                        derived_pos = offset_position(float(mark["lat"]), float(mark["lon"]),
                                                      parse_bearing(rel.group(2)), parse_distance(rel.group(1)))
                        flags.append(f"Position derived from '{cell.strip()}' using a modern landmark position; an estimate.")
                    elif off:
                        derived_pos = (float(mark["lat"]), float(mark["lon"]))
                        flags.append(f"Position given only as '{cell.strip()}'; placed at {name} itself, as a rough estimate.")
                else:
                    lat_s, lon_s, pflag = split_lat_long(cell)
                    if pflag:
                        flags.append(pflag)
                    else:
                        last_position = cell
            else:
                lat_s, lon_s = f.get("lat"), f.get("lon")
                pos_verbatim = " ".join(x for x in (lat_s, lon_s) if x)
            for part in (lat_s, lon_s):
                if part and re.search(r"\d+-\d{1,2}-\d(?!\d)", part):
                    flags.append(f"'{part}' reads as degrees-minutes-seconds, but the last figure is a single "
                                 f"digit; it may be decimal minutes. Read here as seconds.")
            lat = parse_coord(UNCERTAIN.sub(lambda m: m.group(0)[1:-1], lat_s or ""), hemi["lat"], True)
            lon = parse_coord(UNCERTAIN.sub(lambda m: m.group(0)[1:-1], lon_s or ""), hemi["lon"], False)
            if derived_pos:
                lat, lon = derived_pos
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

            kind = "fix" if is_fix else classify(f, section)
            attacked = str(f.get("attack_no") or "").strip().lower()
            if attacked in ("yes", "y", "no", "n", "none", "-"):
                f.pop("attack_no")
                f["attacked"] = "Yes" if attacked in ("yes", "y") else "No"
                if f["attacked"] == "Yes" and kind == "sighting" and not has_summary:
                    remarks = f"{f.get('remarks') or ''} {f.get('description') or ''}".lower()
                    kind = "gun" if re.search(r"\bgun|\b3\"|shell", remarks) else "torpedo"
                    if kind == "torpedo":
                        flags.append("The table marks this contact as attacked but doesn't say how; "
                                     "shown as a torpedo attack. Check the narrative.")
            fired, hits = as_int(f.get("fired")), as_int(f.get("hits"))
            if kind == "torpedo" and fired is not None and hits is not None and hits > fired:
                flags.append(f"More hits ({hits}) than torpedoes fired ({fired}).")
            ir, fr = as_int(f.get("initial_range")), as_int(f.get("firing_range"))
            if kind == "torpedo" and ir and fr and fr > ir:
                flags.append(f"Firing range ({fr}) is greater than initial range ({ir}).")

            typ = re.sub(r"\s*<br\s*/?>\s*", " / ", unbracket(f.get("type", "")))
            if f.get("attack_no"):
                title = f"Attack {f['attack_no']}" + (f" · {typ}" if typ else "")
            elif f.get("contact_no"):
                label = "Aircraft" if kind == "aircraft" else "Contact"
                title = f"{label} {f['contact_no'].rstrip('.')}" + (f" · {typ}" if typ else "")
            else:
                title = typ
            zone_label = "GCT" if gct else z
            keep = {k: v for k, v in f.items()
                    if k not in ("time_date", "time", "zone", "date", "lat_long", "lat", "lon", "page",
                                 "flags", "attack_no", "contact_no") and v}
            keep.update({h: v for h, v in extra.items() if v})
            records.append({
                "id": f"{pid}-C{entry:02d}", "source": source, "row": entry, "kind": kind,
                "page": f.get("page") or table["page"], "zone": z,
                "local": " ".join(x for x in (t, zone_label, d) if x) if t else (f.get("time_date") or d or ""),
                "utc": to_utc(d or "", t, z, year, first_month), "has_time": bool(t),
                "local_date": list(parse_date(d or "", year, first_month) or []),
                "position_verbatim": pos_verbatim, "lat": lat, "lon": lon,
                "derived": {"from_table": True} if derived_pos else None,
                "type": typ, "title": title, "fields": keep, "flags": flags,
                "contact_no": f.get("contact_no"),
            })

    # TORPEDO ATTACK DATA forms transcribed verbatim (attacks-01.md ...).
    for path in sorted(folder.glob("attacks*.md")):
        for atk_num, form in read_attack_forms(path).items():
            entry += 1
            body = form.get("attack") or ""
            flags = [f"Transcriber: {n}" for n in form["flags"]]
            if entry in row_notes:
                flags.append(f"Review: {row_notes[entry]}")
            tm = re.search(r"Time\s*[:;,]?\s*(\d{4})\s*\(?\s*([A-Z])?\s*\)?", body, re.I)
            dm = re.search(r"Date\s*[:;,]?\s*([A-Za-z]+\.?\s*\d{1,2},?\s*\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", body, re.I)
            la = re.search(r"Lat\.?\s*[:;,]?\s*(\d+\s*-\s*\d+(?:\s*-\s*\d+)?)\s*\.?\s*([NS])", body, re.I)
            lo = re.search(r"Long\.?\s*[:;,]?\s*(\d+\s*-\s*\d+(?:\s*-\s*\d+)?)\s*\.?\s*([EW])", body, re.I)
            t = tm.group(1) if tm else None
            z = (tm.group(2) if tm and tm.group(2) else None)
            d = dm.group(1) if dm else None
            if not body:
                flags.append("Only the torpedo page of this attack was transcribed; no time or position.")
            if not t:
                flags.append("No time found on the form.")
            if z is None and t:
                z = default_zone
                flags.append(f"No zone letter on the form; zone {z} assumed from the narrative.")
            lat = parse_coord(re.sub(r"\s", "", la.group(1)) + la.group(2), hemi["lat"], True) if la else None
            lon = parse_coord(re.sub(r"\s", "", lo.group(1)) + lo.group(2), hemi["lon"], False) if lo else None
            if body and (lat is None or lon is None):
                flags.append("No usable position on the form.")
            ff = form_fields(body)
            pick = lambda *keys: next((ff[k] for k in ff for want in keys if k.startswith(want)), None)
            fields = {k: v for k, v in (
                ("description", pick("description")), ("sunk", pick("ship(s) sunk", "ships sunk")),
                ("damaged", pick("ship(s) damaged", "probably sunk", "ships damaged")),
                ("damage determined by", pick("damage determined")), ("target", pick("target draft")),
                ("own ship", pick("speed")), ("attack_type", pick("type attack")),
                ("form", body or None), ("torpedoes", form.get("torpedoes"))) if v}
            tf = re.search(r"Tubes?\s+Fired\s*[:;]\s*(.*)", form.get("torpedoes") or "", re.I)
            if tf and re.findall(r"#\s*\d+", tf.group(1)):
                fields["fired"] = str(len(re.findall(r"#\s*\d+", tf.group(1))))
            desc = fields.get("description") or ""
            records.append({
                "id": f"{pid}-A{entry:02d}", "source": "Torpedo attack data", "row": entry, "kind": "torpedo",
                "page": ", ".join(form["pages"]) or None, "zone": z,
                "local": " ".join(x for x in (t, z, d) if x) or "",
                "utc": to_utc(d or "", t, z, year, first_month) if d else None, "has_time": bool(t),
                "local_date": list(parse_date(d or "", year, first_month) or []),
                "position_verbatim": " ".join(m.group(0) for m in (la, lo) if m), "lat": lat, "lon": lon,
                "derived": None, "type": desc.split(".")[0][:60],
                "title": f"Attack {atk_num}" + (f" · {desc.split('.')[0][:48]}" if desc else ""),
                "fields": fields, "flags": flags,
            })

    for r in [r for r in records if r.get("source") == "Torpedo attack data" and not r.get("has_time")]:
        atk_num = str(r.get("title") or "").split(" · ")[0].replace("Attack", "").strip()
        n = next((x for x in records if not x.get("row") and x["kind"] in ("torpedo", "gun") and x.get("has_time") and x["utc"]
                  and re.search(rf"attack\s*(?:no\.?\s*)?#?\s*{re.escape(atk_num)}\b", str(x.get("title") or ""), re.I)), None)
        if n:
            r["utc"], r["zone"], r["has_time"], r["local"] = n["utc"], n.get("zone"), True, n["local"]
            r["local_date"] = n.get("local_date")
            r["flags"] = [f for f in r["flags"] if f != "No time found on the form."]
            r["flags"].append(f"Time from the narrative entry headed attack {atk_num} (page {n.get('page') or '?'}).")

    for atk_num, t in torpedo_lists.items():
        target = next((r for r in records if r.get("row") and r["kind"] in ("torpedo", "gun")
                       and re.fullmatch(rf"attack\s*\(?{re.escape(atk_num)}\)?", str(r.get("title") or "").split(" · ")[0], re.I)), None)
        lines = ["; ".join(f"{h}: {c}" for h, c in zip(t["headers"], row) if c and h.lower() != "flags") for row in t["rows"]]
        if target:
            target["fields"]["torpedoes"] = "\n".join(lines)
            notes = [row[i] for row in t["rows"] for i, h in enumerate(t["headers"]) if h.lower() == "flags" and i < len(row) and row[i]]
            target["flags"].extend(f"Transcriber (torpedoes): {n}" for n in notes)

    # An attack summary with dates but no times (Silversides Patrol 5): the
    # narrative's attack entries on the same report date supply the times, in
    # order, when the counts agree. The table keeps its positions.
    timeless = [r for r in records if r.get("row") and r["kind"] in ("torpedo", "gun") and not r.get("has_time")
                and r.get("local_date")]
    for day in sorted({tuple(r["local_date"]) for r in timeless}):
        rows = sorted((r for r in timeless if tuple(r["local_date"]) == day), key=lambda r: r["row"])
        told = sorted((r for r in records if not r.get("row") and r["kind"] in ("torpedo", "gun") and r.get("has_time")
                       and r["utc"] and tuple(r.get("local_date") or ()) == day), key=lambda r: r["utc"])
        if len(rows) != len(told):
            for r in rows:
                r["flags"].append(f"The attack table gives no time, and the narrative has {len(told)} attack "
                                  f"entr{'y' if len(told) == 1 else 'ies'} that day for {len(rows)} in the table, "
                                  f"so no times were taken from it.")
            continue
        for r, n in zip(rows, told):
            r["utc"], r["zone"], r["has_time"] = n["utc"], n.get("zone"), True
            r["local"] = n["local"]
            r["flags"] = [f for f in r["flags"] if not f.startswith("No time recorded")]
            r["flags"].append(f"The attack table gives no time; {n['local']} is from the narrative entry "
                              f"(page {n.get('page') or '?'}), matched in order.")

    # A ship contact table with dates but no times (Finback Patrol 5): a
    # narrative entry headed with the contact's number ("Contact #6-7")
    # supplies the time.
    refs = {}
    for n in records:
        if n.get("row") or not n.get("has_time") or not n["utc"]:
            continue
        text = f"{' '.join(str(f) for f in n['flags'])} {n['fields'].get('event') or ''}"
        for a, b in re.findall(r"Contact\s*(?:No\.?\s*)?[#(]\s*(\d+)(?:\s*-\s*(\d+))?", text, re.I):
            for k in range(int(a), int(b or a) + 1):
                refs.setdefault(k, n)
    for r in records:
        if not r.get("row") or r.get("has_time") or r["kind"] != "sighting":
            continue
        cno = re.match(r"\s*(\d+)", str(r.get("contact_no") or ""))
        n = refs.get(int(cno.group(1))) if cno else None
        if not n:
            continue
        r["utc"], r["zone"], r["has_time"], r["local"] = n["utc"], n.get("zone"), True, n["local"]
        r["flags"] = [f for f in r["flags"] if not f.startswith("No time recorded")]
        r["flags"].append(f"The table gives no time; {n['local']} is from the narrative entry for this contact "
                          f"(page {n.get('page') or '?'}).")

    # A rendezvous in the narrative and the contact-table row for the same
    # meeting (the other boat named in the row, within an hour) are one event:
    # the marker takes the table's position and keeps its details.
    met = []
    for rv in [r for r in records if r["kind"] == "rendezvous" and r["utc"]]:
        other = str(rv["fields"].get("with") or "").strip().lower()
        if not other:
            continue
        for c in records:
            if c in met or not c.get("row") or c["kind"] != "sighting" or not c["utc"]:
                continue
            text = " ".join(str(v) for v in [c.get("type")] + list(c["fields"].values())).lower()
            if other in text and minutes_apart(c["utc"], rv["utc"]) <= 60:
                if rv["lat"] is None and c["lat"] is not None:
                    rv["lat"], rv["lon"], rv["position_verbatim"] = c["lat"], c["lon"], c["position_verbatim"]
                    rv["flags"] = [f for f in rv["flags"] if not f.startswith("No position")]
                rv["fields"]["contact_table"] = "; ".join(f"{k.replace('_', ' ')}: {v}" for k, v in c["fields"].items())
                rv["flags"].append(f"{c['source']} entry {c['row']} records this meeting at {c['local']}; "
                                   f"its position is used here.")
                rv["flags"].extend(f for f in c["flags"] if f.startswith("Transcriber"))
                met.append(c)
    records = [r for r in records if r not in met]

    # A narrative attack and a contact-table row marked as attacked usually
    # describe the same attack: the table has the position, the narrative the
    # story. Fold the narrative entry into the nearest table row of the same
    # kind within 3 hours.
    table_attacks = [r for r in records if r.get("row") and r["kind"] in ("torpedo", "gun") and r["utc"]]
    story = []
    for rec in records:
        if rec.get("row") or rec["kind"] not in ("torpedo", "gun") or not rec["utc"]:
            continue
        near = [t for t in table_attacks if t["kind"] == rec["kind"] and minutes_apart(t["utc"], rec["utc"]) <= 180]
        target = min(near, key=lambda t: minutes_apart(t["utc"], rec["utc"]), default=None)
        if target:
            prior = target["fields"].get("narrative")
            target["fields"]["narrative"] = f"{prior}\n\n{rec['fields'].get('event')}" if prior else rec["fields"].get("event")
            target["flags"] = [f for f in target["flags"] if "doesn't say how" not in f]
            target["flags"].append(f"Narrative entry at {rec['local']} (page {rec.get('page') or '?'}) describes this attack; "
                                   f"its account is included here.")
            target["flags"].extend(f for f in rec["flags"] if not f.startswith("No position"))
            story.append(rec)
    records = [r for r in records if r not in story]

    records.sort(key=lambda x: (x["utc"] or "9999", x["id"]))

    # Departure and arrival
    def endpoint(block, label):
        if not block or not block.get("port"):
            return None
        wanted = str(block["port"]).lower().strip()
        port = next((v for k, v in ref["ports"].items() if k.lower() == wanted), None) or next(
            (v for k, v in ref["ports"].items() if wanted.startswith(k.lower()) or k.lower().startswith(wanted)), None)
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
        if rec["lat"] is None or rec["lon"] is None or not rec["utc"] or rec.get("derived"):
            continue
        if rec.get("row") and rec.get("has_time") is False:
            continue   # a table row with a date but no time can't be put in order along the track
        if track and track[-1]["lat"] == rec["lat"] and track[-1]["lon"] == rec["lon"]:
            continue
        track.append({"lat": rec["lat"], "lon": rec["lon"], "utc": rec["utc"], "basis": "documented", "ref": rec["id"]})
    if arrival and arrival["lat"] is not None and arrival["utc"]:
        track.append({"lat": arrival["lat"], "lon": arrival["lon"], "utc": arrival["utc"], "basis": "reference"})
    # With nothing transcribed between the ports, a line from port to port
    # would imply a route nobody recorded.
    if not any(t["basis"] != "reference" for t in track):
        track = []

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

    # Narrative entries with a time but no position: place them on the track
    # between the recorded positions either side (no more than 24 hours
    # apart), as an estimate.
    if len(track) >= 2:
        pts = [(datetime.fromisoformat(t["utc"].replace("Z", "+00:00")), t) for t in track]
        for rec in records:
            if rec["lat"] is not None or not rec["utc"] or rec["kind"] == "fix":
                continue
            when_ = datetime.fromisoformat(rec["utc"].replace("Z", "+00:00"))
            for (ta, a), (tb, b) in zip(pts, pts[1:]):
                # Only between fixes a day or less apart: over longer gaps the
                # straight line says too little about where the boat was.
                if ta <= when_ <= tb and (tb - ta) <= timedelta(hours=24):
                    f = 0 if tb == ta else (when_ - ta) / (tb - ta)
                    dlon = b["lon"] - a["lon"]
                    dlon = dlon - 360 if dlon > 180 else dlon + 360 if dlon < -180 else dlon
                    rec["lat"] = round(a["lat"] + (b["lat"] - a["lat"]) * f, 5)
                    rec["lon"] = round(a["lon"] + dlon * f, 5)
                    rec["derived"] = {"interpolated": True, "between": [a["utc"], b["utc"]]}
                    rec["flags"].append("No position in the report. Placed on the track between the recorded "
                                        f"positions at {a['utc'][:16].replace('T', ' ')} and "
                                        f"{b['utc'][:16].replace('T', ' ')} GMT, as an estimate.")
                    break

    # Minefields: group mine entries with positions lying within 20 miles of
    # each other and draw one estimated area per group.
    minefields = []
    for rec in sorted((r for r in records if r["kind"] == "minefield" and r["lat"] is not None), key=lambda r: r["utc"]):
        for mf in minefields:
            if abs(mf["lat"] - rec["lat"]) * 60 < 20 and abs(mf["lon"] - rec["lon"]) * 60 * math.cos(math.radians(rec["lat"])) < 20:
                mf["points"].append(rec)
                break
        else:
            minefields.append({"lat": rec["lat"], "lon": rec["lon"], "points": [rec]})
    for mf in minefields:
        pts = mf.pop("points")
        mf["lat"] = round(sum(p["lat"] for p in pts) / len(pts), 5)
        mf["lon"] = round(sum(p["lon"] for p in pts) / len(pts), 5)
        spread = max(math.hypot((p["lat"] - mf["lat"]) * 60, (p["lon"] - mf["lon"]) * 60 * math.cos(math.radians(mf["lat"])))
                     for p in pts)
        mf["radius_nm"] = round(max(2.0, spread + 1.0), 2)
        mf["utc"] = pts[0]["utc"]
        mf["refs"] = [p["id"] for p in pts]
        mf["estimated"] = any(p.get("derived") for p in pts) or len(pts) < 2
        mf["note"] = ("Estimated area around the positions of the mine entries in the report. "
                      "The report doesn't give the field's boundaries.")

    torps = [r for r in records if r["kind"] == "torpedo"]
    # Count attacks by the report's own numbering "(3rd Attack)" when present,
    # since one attack often runs over several tagged narrative entries.
    numbered = {}
    for r in records:
        m = re.search(r"\(\s*(\d+)\s*(?:st|nd|rd|th)\s+attack\s*\)", str(r["fields"].get("event") or ""), re.I)
        if m and r["kind"] in ("torpedo", "gun", "minefield"):
            numbered[int(m.group(1))] = r["kind"]
    summary = {
        "records": len(records),
        "sightings": sum(r["kind"] == "sighting" for r in records),
        "aircraft": sum(r["kind"] == "aircraft" for r in records),
        "torpedo_attacks": sum(k == "torpedo" for k in numbered.values()) if numbered else len(torps),
        "mine_attacks": sum(k == "minefield" for k in numbered.values()),
        "counterattacks": sum(r["kind"] == "counterattack" for r in records),
        "torpedoes_fired": sum(as_int(r["fields"].get("fired")) or 0 for r in torps),
        "gun_actions": sum(k == "gun" for k in numbered.values()) if numbered else sum(r["kind"] == "gun" for r in records),
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
        "summary": summary, "track": track, "records": records, "tonnage": tonnage, "minefields": minefields,
    }


STATUS_CODES = ("patrol", "refit", "overhaul", "modernization", "training", "other_task_force",
                "transit", "miscellaneous", "other")


def build_status(ref):
    """Fleet status from the war diary snapshots in sources/status/."""
    folder = SOURCES / "status"
    if not folder.exists():
        return None
    name_to_hull = {str(v.get("name", "")).upper(): k for k, v in (ref.get("boats") or {}).items()}
    observations, problems = [], []
    for path in sorted(folder.rglob("*.yml")):
        if path.name in ("index.yml", "periods.yml", "changes.yml"):
            continue
        snap = load_yaml_text(path)
        if not snap.get("date"):
            print(f"status: {path.name} skipped: no date yet")
            continue
        date = str(snap["date"])
        for group in snap.get("groups") or []:
            status = str(group.get("status") or "").lower()
            if status not in STATUS_CODES:
                problems.append(f"{path.name}: unknown status '{status}' for '{group.get('heading')}'")
            boats = group.get("boats") or []
            items = boats.items() if isinstance(boats, dict) else [(b, None) for b in boats]
            notes = group.get("notes") or {}
            per_item = group.get("item_status") or {}
            for name, unit in items:
                label = str(name).strip()
                hull = name_to_hull.get(label.upper())
                if not hull:
                    continue  # only boats on the map; the listing file keeps the rest
                own = per_item.get(label) or {}
                observations.append({
                    "date": date, "boat": hull, "name": label,
                    "status": own.get("status") or status, "place": own.get("place") or group.get("place"),
                    "unit": unit, "note": notes.get(label),
                    "heading": group.get("heading"), "source": snap.get("source"),
                    "date_stated": str(snap.get("date_stated", "true")).lower() != "false",
                    "date_basis": snap.get("date_basis"),
                    "sheets": snap.get("sheets") or ([snap["page"]] if snap.get("page") else []),
                    "fold3_image": snap.get("fold3_image"), "file": path.name,
                })
    periods = []
    if (folder / "periods.yml").exists():
        for p in load_yaml_text(folder / "periods.yml") or []:
            periods.append({k: p.get(k) for k in ("boat", "status", "place", "start", "end", "source")})
    index = load_yaml_text(folder / "index.yml") if (folder / "index.yml").exists() else []
    changes = []
    for path in sorted(folder.rglob("changes.yml")):
        for c in load_yaml_text(path) or []:
            text = str(c.get("text") or "")
            for name, hull in name_to_hull.items():
                if name and re.search(r"\b" + re.escape(name) + r"\b", text.upper()):
                    changes.append({"date": str(c.get("date")), "boat": hull, "text": text})
    for msg in problems:
        print("status:", msg)
    print(f"status: {len(observations)} observations, {len(periods)} dated periods")
    print(f"status: {len(changes)} changes of command for boats on the map")
    return {"observations": observations, "periods": periods, "index": index or [], "changes": changes}


def main(selected):
    ref = yaml.safe_load((SOURCES / "reference.yml").read_text(encoding="utf-8"))
    folders = sorted({p.parent for p in SOURCES.glob("*/*/patrol.yml")} | {p.parent for p in SOURCES.glob("*/*/gemini-*.yml")})
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
    status = build_status(ref)
    if status is not None:
        (OUT / "status.json").write_text(json.dumps(status, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps({
        "ports": ref.get("ports") or {},
        "places": ref.get("places") or [],
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "patrols": manifest,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"manifest: {len(manifest)} patrol(s)")


if __name__ == "__main__":
    main(sys.argv[1:])
