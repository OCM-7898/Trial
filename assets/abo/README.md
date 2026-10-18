# assets/abo — vendored product images

2,348 JPEG catalog photos (256px, ~22 MB) from the **Amazon Berkeley
Objects (ABO) dataset**, licensed **CC BY 4.0** (see
LICENSE-CC-BY-4.0.txt). This is the subset actually used by this repo —
the full archive is 398k images / 3 GB and is NOT needed here.

Files are stored by ABO image id: `images/<image_id>.jpg`. Which
product uses which image is recorded in `sites/visual/ATTRIBUTIONS.csv`
(Ministore, 2,565 products). The eight reference photos of the visual N/A
trap tasks (ABO items the shop does not sell) are in `assets/trap_photos/`,
with their own ATTRIBUTIONS.csv.

## Rebuilding the sites' static images (no downloads needed)

    python assets/abo/sync_images.py

copies each manifest row's image from here to that site's
`static/img/products/p<product_id>.jpg`. The repo is self-contained:
serving, task building, and gates never read anything outside it.

## Re-SELECTING the catalog (downloads needed)

Only `sites/visual/build_catalog.py` — which picks a NEW product
selection from the full dataset — needs the original archives
(`abo-listings.tar`, `abo-images-small.tar` from
amazon-berkeley-objects.s3.amazonaws.com, extracted in ~/Downloads).
It refreshes this folder and the manifests as it runs.

Attribution: Amazon Berkeley Objects (ABO) Dataset, CC BY 4.0,
https://amazon-berkeley-objects.s3.amazonaws.com/index.html
