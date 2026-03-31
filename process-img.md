# Image Processing

Create thumbnails for each item in `mohawk-furnitures/inventory.csv`.

## Mapping

- **Source**: `IMG` column → file in `mohawk-furnitures/` (e.g. `IMG_1521.jpg`)
- **Output**: `tn-[ID].jpg` in `mohawk-furnitures/` (e.g. `tn-Fl3-library-organ-ottoman.jpg`)
- **Subject**: `ID` + `DESCRIPTION` together describe the item to crop to

## Cropping rules

- Keep the item fully visible — no clipping of edges.
- Center the item with a small margin of surrounding context.
- Crop only — no color correction, sharpening, or background removal.

## Notes

- Skip rows where `IMG` is blank or the source file doesn't exist.
- Only read/process image files when working on this task.
