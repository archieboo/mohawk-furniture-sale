# CLAUDE.md

Mohawk Furniture & Art Sale — static site hosted on GitHub Pages.

## Hosting

- The site will be hosted on **GitHub Pages** (static hosting only).
- All features must work without a backend or server-side processing.
- Implementation constraints:
  - Pure HTML/CSS/JS — no build tools, no server
  - CSV parsed client-side via `fetch()`
  - PDF generation must be client-side (e.g., jsPDF via CDN)
  - All assets (images, CSV) served as static files from the repository


## Running Scripts

Scripts use Python with the `ds` conda environment (requires pandas). Run from the repo root:

```bash
conda run -n ds python scripts/export-inventory.py
```

## Scripts

### Inventory update workflow

The inventory source is a Google Spreadsheet maintained manually. To pick up changes:

1. Edit the Google Spreadsheet directly.
2. Run `conda run -n ds python scripts/watch-inventory.py` (or `export-inventory.py`) to pull the latest data into `mohawk-furnitures/inventory.csv`.
3. Commit the updated CSV to publish the changes to the site.

`watch-inventory.py` can be run manually at any time to check for upstream changes — it fetches the latest sheet, reports what (if anything) changed, updates the CSV, and reloads the local Chrome tab if a diff is found.

## Pricing Reference Page (`pricing.html`)

A separate internal page showing original vs. suggested resale prices. Not linked from the main site — accessible only by direct URL. Committed to the repo but unlisted.

### Files
- `scripts/resale_prices.json` — maps item ID → suggested resale price; edit this to change any price
- `scripts/generate_pricing.py` — reads `inventory.csv` + `resale_prices.json`, writes `pricing.html`
- Both `export-inventory.py` and `watch-inventory.py` call `generate_pricing.py` automatically after updating the CSV

### Pricing logic
Items are 5–6 years old in great condition. Retention rates by brand tier:

| Brand tier | Retention |
|---|---|
| RH, Mitchell Gold+BW, Design Within Reach, Calligaris, Arhaus | 45–55% |
| Room&Board, West Elm | 42–50% |
| Generic/store-branded ("Dan Rak Design Purchased") | 37–42% |
| Art | 37–43% |
| Peloton equipment | ~47% (strong used market) |

**Hard cap: Furniture items (TYPE=Furniture) max out at 40% retention** — use `floor(orig × 0.4)`.
Art, Lighting, and Equipment are NOT subject to the 40% cap.
The cap is applied manually in `resale_prices.json`; `generate_pricing.py` does not enforce it automatically.

When adding a new furniture item to `resale_prices.json`, use `floor(orig × 0.4)` or lower as the resale price.

## File Scope

- Do not read or process image files (`*.jpg`, `*.png`, `*.gif`, `*.webp`, `*.svg`) unless explicitly asked.
