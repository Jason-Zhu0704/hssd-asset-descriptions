# HSSD Asset Descriptions

Structured dataset repository for HSSD asset retrieval.

## Repository Layout

- `data/raw/`
  - `hssd_asset_descriptions.jsonl`: latest repaired description records.
  - `hssd_asset_descriptions.with_images.jsonl`: descriptions with image-linked generation fields.
  - `hssd_asset_index.jsonl`: raw HSSD index metadata (asset_id/mesh_id/name/synset/buckets).
  - `object_categories.json`: coarse category mapping (`large_objects`, `small_objects`, etc.).

- `data/processed/`
  - `asset_index.jsonl`: normalized retrieval index with derived fields (slot/support/composite/clean text).
  - `asset_index_summary.json`: generation summary for `asset_index.jsonl`.

- `data/sqlite/`
  - `hssd_asset_descriptions.db`: SQLite mirror of `data/raw/hssd_asset_descriptions.jsonl` in table `hssd_assets`.

## Notes

- Canonical source for downstream retrieval is `data/raw/hssd_asset_descriptions.jsonl`.
- `data/processed/asset_index.jsonl` is the structured index for slot-aware retrieval and rerank.
