#!/bin/bash
# Checks if the Numbers inventory file has changed since last run.
# If so, shows what changed, re-exports CSV, and reloads Chrome. Then exits.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NUMBERS_FILE="$SCRIPT_DIR/../mohawk-furnitures/mohawk-furnitures.numbers"
EXPORT_SCRIPT="$SCRIPT_DIR/export-inventory.applescript"
CSV_FILE="$SCRIPT_DIR/../mohawk-furnitures/inventory.csv"
STAMP_FILE="$SCRIPT_DIR/.inventory-last-modified"
TEMP_CSV=$(mktemp /tmp/inventory-new.XXXXXX.csv)

CURRENT_MOD=$(stat -f "%m" "$NUMBERS_FILE")
LAST_MOD=$(cat "$STAMP_FILE" 2>/dev/null)

if [ "$CURRENT_MOD" = "$LAST_MOD" ]; then
  echo "No changes detected. Exiting."
  exit 0
fi

echo "Numbers file has changed. Exporting new CSV to compare..."
osascript "$EXPORT_SCRIPT" "$NUMBERS_FILE" "$TEMP_CSV" > /dev/null

# Compare old vs new CSV and report differences
python3 - "$CSV_FILE" "$TEMP_CSV" <<'EOF'
import csv, sys

def read_csv(path):
    try:
        with open(path, newline='') as f:
            rows = list(csv.DictReader(f))
        return {r['id']: r for r in rows if r.get('id')}
    except FileNotFoundError:
        return {}

old_path, new_path = sys.argv[1], sys.argv[2]
old = read_csv(old_path)
new = read_csv(new_path)

old_ids = set(old)
new_ids = set(new)

added   = new_ids - old_ids
removed = old_ids - new_ids
common  = old_ids & new_ids

changes = 0

for id in sorted(added):
    print(f"  + ADDED:   {id} — {new[id].get('Description', '').strip()}")
    changes += 1

for id in sorted(removed):
    print(f"  - REMOVED: {id} — {old[id].get('Description', '').strip()}")
    changes += 1

for id in sorted(common):
    diffs = []
    for field in new[id]:
        ov, nv = old[id].get(field, '').strip(), new[id].get(field, '').strip()
        if ov != nv:
            diffs.append(f"{field}: '{ov}' → '{nv}'")
    if diffs:
        print(f"  ~ CHANGED: {id} — {new[id].get('Description', '').strip()}")
        for d in diffs:
            print(f"             {d}")
        changes += 1

if changes == 0:
    print("  (no row-level differences found)")

EOF

echo ""
echo "Re-exporting CSV..."
cp "$TEMP_CSV" "$CSV_FILE"
rm "$TEMP_CSV"

echo "Reloading Chrome..."
osascript -e '
  tell application "Google Chrome"
    repeat with w in windows
      repeat with t in tabs of w
        if URL of t starts with "file://" and URL of t contains "mohawk-furniture-sale" then
          reload t
        end if
      end repeat
    end repeat
  end tell
'

echo "$CURRENT_MOD" > "$STAMP_FILE"
echo "Done."
