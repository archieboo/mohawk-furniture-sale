#!/usr/bin/env python3
"""
generate_pricing.py
Reads inventory.csv and resale_prices.json, writes pricing.html.
Called automatically by export-inventory.py and watch-inventory.py.

Usage: conda run -n ds python scripts/generate_pricing.py
"""

import json
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT   = os.path.join(SCRIPT_DIR, "..")
CSV_FILE    = os.path.join(REPO_ROOT, "mohawk-furnitures", "inventory.csv")
PRICES_FILE = os.path.join(SCRIPT_DIR, "resale_prices.json")
OUT_FILE    = os.path.join(REPO_ROOT, "pricing.html")


def parse_price(val):
    if not isinstance(val, str) or not val.strip():
        return None
    try:
        return int(float(val.replace(",", "").strip()))
    except ValueError:
        return None


def build_items_js(csv_path, resale_prices):
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    df.columns = df.columns.str.strip().str.upper()

    lines = []
    skipped = []
    for _, row in df.iterrows():
        item_id = row.get("ID", "").strip()
        if not item_id:
            continue

        room      = row.get("ROOM", "").strip()
        item_type = row.get("TYPE", "").strip()
        desc      = row.get("DESCRIPTION", "").strip()
        brand     = row.get("BRAND", "").strip()
        avail     = (row.get("AVAIL", "Y").strip().upper() or "Y")

        try:
            qty = int(float(row.get("QUANTITY", "1") or "1"))
        except (ValueError, TypeError):
            qty = 1

        orig   = parse_price(row.get("PRICE", ""))
        resale = resale_prices.get(item_id)

        if orig is None or resale is None:
            skipped.append(item_id)
            continue

        def esc(s):
            return s.replace("\\", "\\\\").replace("'", "\\'")

        lines.append(
            f"  {{ id:'{esc(item_id)}', room:'{esc(room)}', type:'{esc(item_type)}', "
            f"qty:{qty}, desc:'{esc(desc)}', brand:'{esc(brand)}', "
            f"orig:{orig}, resale:{resale}, avail:'{avail}' }}"
        )

    if skipped:
        print(f"  Note: {len(skipped)} item(s) skipped (no resale price): {', '.join(skipped)}")

    return "[\n" + ",\n".join(lines) + "\n]"


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Mohawk Sale — Resale Price Reference</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Georgia', serif;
      background: #faf9f7;
      color: #2c2c2c;
      font-size: 14px;
      line-height: 1.5;
    }

    header {
      background: #2c2c2c;
      color: #fff;
      padding: 32px 48px;
    }
    header h1 {
      font-size: 22px;
      font-weight: normal;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    header p {
      margin-top: 8px;
      color: #aaa;
      font-family: 'Helvetica Neue', sans-serif;
      font-size: 13px;
    }

    .note {
      background: #f0ece4;
      border-left: 3px solid #b5925a;
      padding: 14px 48px;
      font-family: 'Helvetica Neue', sans-serif;
      font-size: 13px;
      color: #555;
    }

    .controls {
      padding: 18px 48px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: center;
      background: #fff;
      border-bottom: 1px solid #e5e0d8;
    }
    .controls label {
      font-family: 'Helvetica Neue', sans-serif;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #888;
      margin-right: 4px;
    }
    .controls select, .controls input {
      border: 1px solid #d5cfc6;
      background: #faf9f7;
      padding: 6px 10px;
      font-size: 13px;
      font-family: 'Helvetica Neue', sans-serif;
      color: #2c2c2c;
      border-radius: 2px;
    }

    .summary {
      padding: 14px 48px;
      font-family: 'Helvetica Neue', sans-serif;
      font-size: 13px;
      color: #666;
      background: #faf9f7;
    }

    main { padding: 0 48px 48px; }

    table { width: 100%; border-collapse: collapse; margin-top: 16px; }
    thead th {
      text-align: left;
      padding: 10px 12px;
      font-family: 'Helvetica Neue', sans-serif;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #888;
      border-bottom: 2px solid #e0dbd2;
      white-space: nowrap;
      cursor: pointer;
      user-select: none;
    }
    thead th:hover { color: #2c2c2c; }
    thead th.sort-asc::after  { content: ' ↑'; }
    thead th.sort-desc::after { content: ' ↓'; }

    tbody tr { border-bottom: 1px solid #ede9e2; transition: background 0.1s; }
    tbody tr:hover { background: #f5f2ec; }
    tbody tr.unavailable { opacity: 0.45; }

    td { padding: 11px 12px; vertical-align: top; }
    .td-id { font-family: 'Courier New', monospace; font-size: 11px; color: #aaa; white-space: nowrap; }
    .td-desc { max-width: 280px; }
    .td-desc .desc-main { font-size: 13px; }
    .td-desc .desc-brand { font-family: 'Helvetica Neue', sans-serif; font-size: 11px; color: #999; margin-top: 2px; }
    .td-room, .td-type, .td-qty { font-family: 'Helvetica Neue', sans-serif; font-size: 12px; color: #666; white-space: nowrap; }
    .td-price  { font-family: 'Helvetica Neue', sans-serif; font-size: 13px; text-align: right; white-space: nowrap; color: #888; }
    .td-resale { font-family: 'Helvetica Neue', sans-serif; font-size: 14px; font-weight: 600; text-align: right; white-space: nowrap; color: #2c7a3c; }
    .td-pct    { font-family: 'Helvetica Neue', sans-serif; font-size: 12px; text-align: right; white-space: nowrap; color: #b5925a; }
    .badge-avail { display: inline-block; padding: 2px 7px; border-radius: 10px; font-family: 'Helvetica Neue', sans-serif; font-size: 10px; letter-spacing: 0.04em; text-transform: uppercase; }
    .badge-y { background: #e6f4ea; color: #2c7a3c; }
    .badge-n { background: #fce8e8; color: #9e3333; }

    tfoot td {
      padding: 14px 12px;
      font-family: 'Helvetica Neue', sans-serif;
      font-size: 13px;
      border-top: 2px solid #e0dbd2;
      font-weight: 600;
    }

    @media (max-width: 768px) {
      header, .note, .controls, .summary, main { padding-left: 16px; padding-right: 16px; }
      .td-id, .td-room, .td-type { display: none; }
    }
  </style>
</head>
<body>

<header>
  <h1>Mohawk Furniture &amp; Art — Resale Price Reference</h1>
  <p>Internal pricing guide &middot; Not the public sale site</p>
</header>

<div class="note">
  Suggested resale prices are based on 5–6 years of age in great condition. Estimates reflect typical secondary-market retention by brand tier (40–55% for premium brands; 35–40% for store-branded pieces). Art and rugs priced conservatively. Peloton equipment reflects strong used-market demand. Edit <code>scripts/resale_prices.json</code> to adjust any price.
</div>

<div class="controls">
  <label>Room</label>
  <select id="filterRoom">
    <option value="">All rooms</option>
    <option>Living space</option>
    <option>Bedroom</option>
    <option>Dining</option>
    <option>Office</option>
    <option>Outdoor</option>
    <option>Gym</option>
  </select>

  <label style="margin-left:12px">Type</label>
  <select id="filterType">
    <option value="">All types</option>
    <option>Furniture</option>
    <option>Art</option>
    <option>Lighting</option>
    <option>Equipment</option>
  </select>

  <label style="margin-left:12px">Search</label>
  <input type="text" id="search" placeholder="description, brand…" style="width:200px" />
</div>

<div class="summary" id="summary"></div>

<main>
  <table id="priceTable">
    <thead>
      <tr>
        <th data-col="id">ID</th>
        <th data-col="desc">Description</th>
        <th data-col="room">Room</th>
        <th data-col="type">Type</th>
        <th data-col="qty" style="text-align:right">Qty</th>
        <th data-col="orig" style="text-align:right">Original</th>
        <th data-col="resale" style="text-align:right">Suggested Resale</th>
        <th data-col="pct" style="text-align:right">Retention</th>
        <th data-col="avail" style="text-align:center">Avail</th>
      </tr>
    </thead>
    <tbody id="tableBody"></tbody>
    <tfoot>
      <tr>
        <td colspan="5"></td>
        <td id="footOrig" style="text-align:right"></td>
        <td id="footResale" style="text-align:right;color:#2c7a3c"></td>
        <td colspan="2"></td>
      </tr>
    </tfoot>
  </table>
</main>

<script>
const ITEMS = ITEMS_PLACEHOLDER;

const fmt = n => '$' + n.toLocaleString();
const pct = (r, o) => Math.round(r / o * 100) + '%';

let sortCol = null, sortDir = 1;

function filteredItems() {
  const room   = document.getElementById('filterRoom').value;
  const type   = document.getElementById('filterType').value;
  const search = document.getElementById('search').value.toLowerCase();
  return ITEMS.filter(it => {
    if (room   && it.room !== room) return false;
    if (type   && it.type !== type) return false;
    if (search && !it.desc.toLowerCase().includes(search) &&
                  !it.brand.toLowerCase().includes(search) &&
                  !it.id.toLowerCase().includes(search)) return false;
    return true;
  });
}

function render() {
  const items = filteredItems();

  if (sortCol) {
    items.sort((a, b) => {
      let av = a[sortCol], bv = b[sortCol];
      if (typeof av === 'string') av = av.toLowerCase();
      if (typeof bv === 'string') bv = bv.toLowerCase();
      return av < bv ? -sortDir : av > bv ? sortDir : 0;
    });
  }

  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  let totalOrig = 0, totalResale = 0;

  items.forEach(it => {
    const tr = document.createElement('tr');
    if (it.avail === 'N') tr.classList.add('unavailable');
    tr.innerHTML = `
      <td class="td-id">${it.id}</td>
      <td class="td-desc">
        <div class="desc-main">${it.desc}</div>
        ${it.brand ? `<div class="desc-brand">${it.brand}</div>` : ''}
      </td>
      <td class="td-room">${it.room}</td>
      <td class="td-type">${it.type}</td>
      <td class="td-qty" style="text-align:right">${it.qty}</td>
      <td class="td-price">${fmt(it.orig)}</td>
      <td class="td-resale">${fmt(it.resale)}</td>
      <td class="td-pct">${pct(it.resale, it.orig)}</td>
      <td style="text-align:center"><span class="badge-avail badge-${it.avail.toLowerCase()}">${it.avail === 'Y' ? 'Yes' : 'No'}</span></td>
    `;
    tbody.appendChild(tr);
    totalOrig   += it.orig;
    totalResale += it.resale;
  });

  document.getElementById('summary').textContent =
    `${items.length} of ${ITEMS.length} items shown`;
  document.getElementById('footOrig').textContent   = fmt(totalOrig);
  document.getElementById('footResale').textContent = fmt(totalResale);
}

document.querySelectorAll('thead th[data-col]').forEach(th => {
  th.addEventListener('click', () => {
    const col = th.dataset.col;
    if (sortCol === col) sortDir *= -1;
    else { sortCol = col; sortDir = 1; }
    document.querySelectorAll('thead th').forEach(h => h.classList.remove('sort-asc','sort-desc'));
    th.classList.add(sortDir === 1 ? 'sort-asc' : 'sort-desc');
    render();
  });
});

['filterRoom','filterType','search'].forEach(id =>
  document.getElementById(id).addEventListener('input', render)
);

render();
</script>
</body>
</html>
"""


def main():
    with open(PRICES_FILE) as f:
        resale_prices = json.load(f)

    items_js = build_items_js(CSV_FILE, resale_prices)
    html = HTML_TEMPLATE.replace("ITEMS_PLACEHOLDER", items_js)

    with open(OUT_FILE, "w") as f:
        f.write(html)

    print(f"Generated {OUT_FILE}")


if __name__ == "__main__":
    main()
