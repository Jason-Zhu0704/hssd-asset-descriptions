#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from retrieval.engine import load_json, retrieve_slot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Slot-aware retrieval over per-category indices")
    parser.add_argument("--request", type=Path, required=True, help="JSON request file")
    parser.add_argument("--indices-dir", type=Path, default=Path("data/indices"))
    parser.add_argument("--slot-categories", type=Path, default=Path("configs/slot_categories.json"))
    parser.add_argument("--negative-terms", type=Path, default=Path("configs/negative_terms.json"))
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    req = load_json(args.request)
    slot_categories = load_json(args.slot_categories)
    negative_terms = load_json(args.negative_terms)

    if isinstance(req, dict) and "slots" in req:
        outputs = [
            retrieve_slot(
                indices_dir=args.indices_dir,
                slot_request=slot,
                slot_categories=slot_categories,
                negative_terms=negative_terms,
                top_k=args.top_k,
            )
            for slot in req["slots"]
        ]
        result = {"results": outputs}
    else:
        result = retrieve_slot(
            indices_dir=args.indices_dir,
            slot_request=req,
            slot_categories=slot_categories,
            negative_terms=negative_terms,
            top_k=args.top_k,
        )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
