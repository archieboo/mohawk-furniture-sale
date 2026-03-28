#!/usr/bin/env python3
"""
export-inventory.py
Downloads the inventory Google Spreadsheet as CSV and normalizes it.

Usage: conda run -n ds python scripts/export-inventory.py
"""

import os
import re
import sys
import yaml
import pandas as pd

FRACTION_MAP = {
    0.125: '⅛', 0.25: '¼', 0.333: '⅓', 0.375: '⅜',
    0.5:   '½', 0.625: '⅝', 0.667: '⅔', 0.75:  '¾', 0.875: '⅞',
}
_EXISTING_FRACS = '½¼¾⅓⅔⅛⅜⅝⅞'
_NUM = r'(\d+(?:\.\d+)?(?:[½¼¾⅓⅔⅛⅜⅝⅞])?|\d*[½¼¾⅓⅔⅛⅜⅝⅞])'

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_SCRIPT_DIR, "config.yml")) as _f:
    _cfg = yaml.safe_load(_f)

SHEET_ID = _cfg["sheet_id"]
EXPORT_URL = _cfg["export_url"]
OUT = "mohawk-furnitures/inventory.csv"


def normalize_img(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return val
    s = str(val).strip()
    if not s:
        return val
    # Strip trailing ".0" from numeric values read as float
    if s.endswith('.0') and s[:-2].isdigit():
        s = s[:-2]
    base = os.path.basename(s)
    if "." not in base:
        base = "IMG_" + base + ".jpg"
    return base


def _to_frac(s):
    if any(c in s for c in _EXISTING_FRACS):
        return s.strip()
    try:
        val = float(s)
    except ValueError:
        return s.strip()
    int_part = int(val)
    dec = round(val - int_part, 3)
    if dec == 0:
        return str(int_part)
    closest = min(FRACTION_MAP, key=lambda k: abs(k - dec))
    if abs(closest - dec) < 0.02:
        return (str(int_part) if int_part else '') + FRACTION_MAP[closest]
    return s.strip()


def normalize_dimension(val):
    if not isinstance(val, str) or not val.strip():
        return val
    s = val.strip().replace('"', '').replace('\u201c', '').replace('\u201d', '')
    if re.search(r'\bdia', s, re.IGNORECASE):
        dia_m = re.search(_NUM + r'\s*(?:dia(?:m\.?)?)', s, re.IGNORECASE)
        h_m   = re.search(_NUM + r'\s*h\b', s, re.IGNORECASE)
        if dia_m:
            parts = [_to_frac(dia_m.group(1)) + 'Dia']
            if h_m:
                parts.append(_to_frac(h_m.group(1)) + 'H')
            return ' x '.join(parts) + ' (in)'
    w_m = re.search(_NUM + r'\s*w\b', s, re.IGNORECASE)
    d_m = re.search(_NUM + r'\s*d\b', s, re.IGNORECASE)
    h_m = re.search(_NUM + r'\s*h\b', s, re.IGNORECASE)
    if any([w_m, d_m, h_m]):
        parts = []
        if w_m: parts.append(_to_frac(w_m.group(1)) + 'W')
        if h_m: parts.append(_to_frac(h_m.group(1)) + 'H')
        if d_m: parts.append(_to_frac(d_m.group(1)) + 'D')
        return ' x '.join(parts) + ' (in)'
    return s


def normalize_room(room, desc):
    if not isinstance(room, str):
        return room
    r = room.lower().strip()
    d = desc.lower().strip() if isinstance(desc, str) else ""
    if "bedroom" in r:
        return "Bedroom"
    if r in ("family room", "living room", "lounge", "library", "game room"):
        return "Office" if "desk" in d else "Living space"
    if r in ("dining room", "kitchen"):
        return "Dining"
    if any(w in r for w in ("courtyard", "terrace", "patio", "garden", "outdoor")):
        return "Outdoor"
    return room


def main():
    print("Downloading from Google Sheets...")
    df = pd.read_csv(EXPORT_URL)

    if df.empty:
        print("ERROR: empty CSV", file=sys.stderr)
        sys.exit(1)

    print("Normalizing columns...")

    # Uppercase all column headers
    df.columns = df.columns.str.strip().str.upper()

    cols = {c.lower(): c for c in df.columns}

    if "img" in cols:
        df[cols["img"]] = df[cols["img"]].apply(normalize_img)

    if "dimension" in cols:
        df[cols["dimension"]] = df[cols["dimension"]].apply(normalize_dimension)

    if "room" in cols:
        desc_col = cols.get("description")
        desc = df[desc_col] if desc_col else pd.Series("", index=df.index)
        df[cols["room"]] = [
            normalize_room(r, d) for r, d in zip(df[cols["room"]], desc)
        ]

    df.to_csv(OUT, index=False)
    print(f"Exported {len(df) + 1} rows (including header) to {OUT}")


if __name__ == "__main__":
    main()
