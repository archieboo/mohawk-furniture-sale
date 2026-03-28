# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A furniture and arts sale site for Mohawk.

**Site Name**: Mohawk Furniture & Art Sale
**Contact Info:** bajia@me.com


## Website requirements

- The website should allow me to select between arts or furnitures, or if under furnitures toggle by room. 
- Overall it should be a simple but professional looking site, and the the esthetics of the website should be like [Westelm](https://www.westelm.com/shop/furniture/living-room-bookcases/)
- Features of website: 
    1. able to toggle between furniture or art; or by room type; only relevant listings are shown
    2. there should be an add to cart button. A user can add items to cart. When in cart, list each added item, with discription and thumnail photo, and show total. Rather than actual payment, have a button that generates a pdf that list the items in the cart, and the total. 
- Description of each art or furniture piece: 
    - all info should refer to the `./mohawk-furnitures/inventory.csv` file, and all photos files of furniture and art are also in `./mohawk-furnitures/` (the jpg files)
    - each item should include: photo, dimension, discription, room, price
    - each item should display its inventory ID in small, inconspicuous text below all other content (price, quantity, add-to-cart button)

- Inventory is maintained in a Google Spreadsheet (open access) and exported to CSV for use by the web frontend.

## Hosting

- The site will be hosted on **GitHub Pages** (static hosting only).
- All features must work without a backend or server-side processing.
- Implementation constraints:
  - Pure HTML/CSS/JS — no build tools, no server
  - CSV parsed client-side via `fetch()`
  - PDF generation must be client-side (e.g., jsPDF via CDN)
  - All assets (images, CSV) served as static files from the repository

## Repository Structure

```
mohawk-furnitures/
  inventory.csv               # Generated — do not edit manually
  IMG_*.jpg                   # Product images; filenames are referenced in the `img` column of the spreadsheet
scripts/
  export-inventory.py         # Downloads and normalizes inventory from Google Sheets
  watch-inventory.py          # Watches for changes, updates CSV, and reloads Chrome
  generate_pricing.py         # Regenerates pricing.html from inventory.csv + resale_prices.json
  resale_prices.json          # Suggested resale prices by item ID — edit this to adjust prices
pricing.html                  # Internal resale price reference (unlisted, not linked from main site)
```

**Google Spreadsheet:** https://docs.google.com/spreadsheets/d/1XcStNOGD14LMi8EZuNEQ8QO2llGNcES57u7gIBDTBco/edit?usp=sharing


## Image processing

For this step, I'm giving you permission to process the image jpg files for items listed in the csv file. Based on `ID` and `DESCRIPTION` can you take a look at the images (jpgs).

- **Goal**: make a thumnail from the jpg of each item, the thumnail is basicaly a crop of the jpg, focusing on just the item. The item should be based on the `ID` and `DESCRIPTION` of the item.
- **Thumnail Naming**: the naming convention should follow: tn-[ID].jpg (or png if you generated png file)
- You should ask me permission before you move on to the next item. 

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

### export-inventory.py

Downloads the Google Spreadsheet as CSV → `mohawk-furnitures/inventory.csv`.

- Fetches the sheet via Google Sheets CSV export URL (no auth required — sheet is open access).
- The `IMG` column must contain only the basename of the image file (e.g., `IMG_1521.jpg`), not a full path.
- The `ROOM` column is normalized during export according to these rules (case-insensitive matching):
  - **Bedroom**: any room value containing "bedroom"
  - **Living space**: family room, living room, lounge, library, game room — unless the item's description contains "desk", in which case → **Office**
  - **Dining**: dining room, kitchen
  - **Outdoor**: any room value containing "courtyard", "terrace", "patio", "garden", or "outdoor"
  - All other room values are passed through unchanged.

## Pricing Reference Page (`pricing.html`)

A separate internal page showing original vs. suggested resale prices. Not linked from the main site — accessible only by direct URL. Committed to the repo but unlisted.

### Files
- `scripts/resale_prices.json` — maps item ID → suggested resale price; edit this to change any price
- `scripts/generate_pricing.py` — reads `inventory.csv` + `resale_prices.json`, writes `pricing.html`
- Both `export-inventory.py` and `watch-inventory.py` call `generate_pricing.py` automatically after updating the CSV

### Main site integration (`index.html`)
- `index.html` fetches `scripts/resale_prices.json` at load time (alongside the CSV) and displays suggested prices on each product card
- Price is labeled **"Suggested price"** on cards; the subtitle highlights **"prices negotiable"** in accent gold
- Cart total is computed from suggested prices; shows `+` if any item lacks a price entry
- PDF includes the suggested price per item and a suggested total; footer reads "All prices are suggested and negotiable"
- If an item has no entry in `resale_prices.json`, it falls back to "Inquire for price"

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
