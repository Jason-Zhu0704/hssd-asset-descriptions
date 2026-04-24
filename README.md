# HSSD Asset Descriptions

Preprocessed artifacts for HSSD asset retrieval and description workflows.

## Files

- `hssd_asset_descriptions.jsonl`  
  Canonical per-asset description records (one JSON object per line).

- `hssd_asset_descriptions.db`  
  SQLite version of the descriptions (`hssd_assets` table) for fast querying.

- `hssd_asset_descriptions.with_images.jsonl`  
  Description records enriched with image-related fields used during generation/debug.

- `hssd_asset_index.jsonl`  
  Asset index metadata (asset IDs, mesh IDs, categories/synsets, names).

- `object_categories.json`  
  Category mapping file used by SceneSmith preprocessing/retrieval pipeline.

## Notes

- This repository stores only compact preprocessed metadata and description artifacts.
- Raw HSSD mesh assets (`objects/*.glb`, `stages/*.glb`) are hosted separately in the HSSD models dataset repository.
