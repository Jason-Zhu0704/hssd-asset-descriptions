#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from retrieval.engine import build_indices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build per-category JSONL indices from processed asset_index.jsonl")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/asset_index.jsonl"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/indices"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_indices(args.input, args.output_dir)
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
