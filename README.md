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

## Retrieval Code

### 1) Build per-category indices

```bash
python scripts/04_build_indices.py \
  --input data/processed/asset_index.jsonl \
  --output-dir data/indices
```

### 2) Run slot-aware retrieval

```bash
python scripts/05_retrieve_for_scene.py \
  --request data/indices/examples/slot_request_bedroom.json \
  --indices-dir data/indices \
  --slot-categories configs/slot_categories.json \
  --negative-terms configs/negative_terms.json \
  --top-k 10 \
  --output data/indices/examples/retrieval_result_bedroom.json
```

Core logic:
- category gating via `configs/slot_categories.json`
- clean-text token similarity + support/style/color/quality scores
- negative-term penalties + composite penalties
- pair binding for `count>1` and `pairing=same_asset`
