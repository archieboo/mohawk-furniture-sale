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

- Inventory is manually maintained in an Apple Numbers spreadsheet and exported to CSV for use by the web frontend.

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
  mohawk-furnitures.numbers   # Source of truth for inventory data (1 sheet, 1 table)
  inventory.csv               # Generated — do not edit manually
  IMG_*.jpg                   # Product images; filenames are referenced in the `img` column of the Numbers table
scripts/
  *.applescript               # Automation scripts, run via `osascript`
```

## Running Scripts

All scripts live in `./scripts/` and are executed headlessly from the terminal:

```bash
osascript scripts/<script-name>.applescript
```

## Scripts

### export-inventory.applescript

Exports `mohawk-furnitures/mohawk-furnitures.numbers` → `mohawk-furnitures/inventory.csv`.

- Exports the single table's data only (no table name header row).
- The `img` column must contain only the basename of the image file (e.g., `IMG_1521.jpg`), not a full path.
- The `room` column is normalized during export according to these rules (case-insensitive matching):
  - **Bedroom**: any room value containing "bedroom"
  - **Living space**: familyroom, lounge, library, game room — unless the item's description contains "desk", in which case → **Office**
  - **Dining**: dining room, kitchen
  - All other room values are passed through unchanged.

## File Scope

- Do not read or process image files (`*.jpg`, `*.png`, `*.gif`, `*.webp`, `*.svg`) unless explicitly asked.
