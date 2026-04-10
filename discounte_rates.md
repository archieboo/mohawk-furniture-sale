# Resale Discount Rates

Items are 5–6 years old, great condition. Suggested resale prices are stored in
`scripts/resale_prices.json` and displayed on the site and in `pricing.html`.

## Formula

```
suggested_price = floor(original_price × retention_rate)
```

For **Furniture** items, the result is additionally capped at 40% of original:

```
suggested_price = min(floor(orig × rate), floor(orig × 0.40))
```

Art, Lighting, and Equipment are **not** subject to the 40% cap.

## Retention Rates by Brand Tier

| Brand / Category | Retention Rate |
|---|---|
| RH, Mitchell Gold+Bob Williams, Design Within Reach, Calligaris, Arhaus | 45–55% (cap brings Furniture to 40%) |
| Room&Board, West Elm | 42–50% (cap brings Furniture to 40%) |
| Generic / store-branded ("Dan Rak Design Purchased") | 37–42% |
| Art | 37–43% |
| Lighting | 37–40% |
| Peloton equipment | ~47–49% (strong used market, no cap) |

## Observed Rates (from current resale_prices.json)

Most items land at **~38–40%** after the furniture cap. Notable exceptions:

| Item | Type | Rate | Note |
|---|---|---|---|
| Peloton bike | Equipment | 46.9% | No cap |
| Peloton tread | Equipment | 48.9% | No cap |
| Room&Board foyer console | Furniture | 50% | Set above cap — review |

## How to Add or Update a Price

1. Find the item's original price (`PRICE` column in `inventory.csv`).
2. Look up brand tier in the table above to pick a retention rate.
3. Compute `floor(orig × rate)`.
4. If `TYPE = Furniture`, also compute `floor(orig × 0.40)` and take the lower value.
5. Add or update the entry in `scripts/resale_prices.json`: `"ITEM-ID": price`.
6. Run `conda run -n ds python scripts/generate_pricing.py` to regenerate `pricing.html`.

## Items Needing Review (as of 2026-04-09)

Original prices were lowered in the spreadsheet; resale prices now exceed originals:

| ID | New Original | Current Resale | Action |
|---|---|---|---|
| `Fl1-familyroom-end-table` | $125 | $200 | Recompute — Room&Board Furniture → $50 |
| `Fl1-kitchen-bar-stool` | $125 | $185 | Recompute — generic Furniture → $50 |
| `Fl1-livingroom-table-lamp` | $179 | $135 | Recompute — generic Lighting → $67 |
