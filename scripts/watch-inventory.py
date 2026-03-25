#!/usr/bin/env python3
"""
watch-inventory.py
Fetches the latest inventory from Google Sheets, shows what changed,
updates inventory.csv if there are differences, and reloads Chrome.

Usage: conda run -n ds python scripts/watch-inventory.py
"""

import os
import subprocess
import sys
import tempfile

import yaml
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(SCRIPT_DIR, "config.yml")) as _f:
    _cfg = yaml.safe_load(_f)

SHEET_ID = _cfg["sheet_id"]
EXPORT_URL = _cfg["export_url"]
CSV_FILE = os.path.join(SCRIPT_DIR, "..", "mohawk-furnitures", "inventory.csv")


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
    return room


def fetch_and_normalize():
    df = pd.read_csv(EXPORT_URL)
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
    return df


def read_csv(path):
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
        if "id" not in df.columns:
            return {}
        return {row["id"]: row.to_dict() for _, row in df.iterrows() if row.get("id")}
    except FileNotFoundError:
        return {}


def show_diff(old_path, new_df):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        new_df.to_csv(f.name, index=False)
        new_path = f.name

    try:
        old = read_csv(old_path)
        new_df_str = new_df.astype(str).fillna("")
        if "id" not in new_df_str.columns:
            print("No 'id' column found; skipping diff.")
            return True
        new = {
            row["id"]: row.to_dict()
            for _, row in new_df_str.iterrows()
            if row.get("id")
        }

        added = set(new) - set(old)
        removed = set(old) - set(new)
        common = set(old) & set(new)
        changes = 0

        for id_ in sorted(added):
            print(f"  + ADDED:   {id_} — {new[id_].get('description', '').strip()}")
            changes += 1

        for id_ in sorted(removed):
            print(f"  - REMOVED: {id_} — {old[id_].get('description', '').strip()}")
            changes += 1

        for id_ in sorted(common):
            diffs = [
                f"{field}: '{old[id_].get(field, '').strip()}' → '{new[id_].get(field, '').strip()}'"
                for field in new[id_]
                if old[id_].get(field, "").strip() != new[id_].get(field, "").strip()
            ]
            if diffs:
                print(f"  ~ CHANGED: {id_} — {new[id_].get('description', '').strip()}")
                for d in diffs:
                    print(f"             {d}")
                changes += 1

        if changes == 0:
            print("No changes detected.")
            return False

        return True
    finally:
        os.unlink(new_path)


def reload_chrome():
    script = """
    tell application "Google Chrome"
      repeat with w in windows
        repeat with t in tabs of w
          if URL of t starts with "file://" and URL of t contains "mohawk-furniture-sale" then
            reload t
          end if
        end repeat
      end repeat
    end tell
    """
    subprocess.run(["osascript", "-e", script], check=False)


def main():
    print("Fetching latest inventory from Google Sheets...")
    new_df = fetch_and_normalize()

    has_changes = show_diff(CSV_FILE, new_df)

    if not has_changes:
        sys.exit(0)

    print("\nUpdating inventory.csv...")
    new_df.to_csv(CSV_FILE, index=False)

    print("Reloading Chrome...")
    reload_chrome()

    print("Done.")


if __name__ == "__main__":
    main()
