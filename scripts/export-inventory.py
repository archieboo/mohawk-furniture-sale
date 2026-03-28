#!/usr/bin/env python3
"""
export-inventory.py
Downloads the inventory Google Spreadsheet as CSV and normalizes it.

Usage: conda run -n ds python scripts/export-inventory.py
"""

import os
import sys
import yaml
import pandas as pd

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
