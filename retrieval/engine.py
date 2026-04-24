from __future__ import annotations

import json
import re

from dataclasses import dataclass
from pathlib import Path


TOKEN_RE = re.compile(r"[a-z0-9_\-]{2,}")


@dataclass
class CandidateScore:
    asset_id: str
    slot_category: str
    score: float
    reason: str


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def tokenize(text: str) -> set[str]:
    return set(TOKEN_RE.findall((text or "").lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def negative_hits(text: str, terms: list[str]) -> list[str]:
    t = (text or "").lower()
    return [term for term in terms if term.lower() in t]


def build_indices(processed_index_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    by_slot: dict[str, list[dict]] = {}

    with processed_index_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            cat = rec.get("slot_category", "unknown")
            by_slot.setdefault(cat, []).append(rec)

    stats = {}
    for cat, rows in by_slot.items():
        path = out_dir / f"{cat}.jsonl"
        with path.open("w", encoding="utf-8") as wf:
            for r in rows:
                wf.write(json.dumps(r, ensure_ascii=False) + "\n")
        stats[cat] = len(rows)

    manifest = {
        "categories": sorted(by_slot.keys()),
        "counts": stats,
        "total": sum(stats.values()),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def retrieve_slot(
    indices_dir: Path,
    slot_request: dict,
    slot_categories: dict,
    negative_terms: dict,
    top_k: int = 10,
) -> dict:
    slot_id = slot_request["slot_id"]
    target_category = slot_request["target_category"]
    allowed = set(slot_request.get("allowed_categories") or slot_categories.get(target_category) or [target_category])
    support_target = slot_request.get("support_class")
    style_pref = [s.lower() for s in slot_request.get("style_preference") or []]

    query_text = " ".join(
        [
            target_category,
            " ".join(style_pref),
            " ".join(slot_request.get("negative_terms") or []),
        ]
    )
    query_tokens = tokenize(query_text)

    candidates: list[CandidateScore] = []

    for cat in allowed:
        file_path = indices_dir / f"{cat}.jsonl"
        if not file_path.exists():
            continue
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                text = rec.get("retrieval_clean_text", "")
                text_tokens = tokenize(text)

                category_score = 1.0 if rec.get("slot_category") in allowed else 0.0
                semantic_score = jaccard(query_tokens, text_tokens)

                support_score = 0.5
                if support_target:
                    support_score = 1.0 if rec.get("support_class") == support_target else 0.0

                style_score = 0.0
                asset_styles = [s.lower() for s in rec.get("style_tags") or []]
                if style_pref:
                    style_score = 1.0 if any(s in asset_styles for s in style_pref) else 0.0

                color_score = 0.0
                if slot_request.get("color_preference"):
                    pref = slot_request["color_preference"].lower()
                    colors = [c.lower() for c in rec.get("color_tags") or []]
                    color_score = 1.0 if pref in colors else 0.0

                quality = rec.get("quality_flags") or {}
                quality_score = 1.0 if quality.get("status") == "success" else 0.0
                quality_score *= float(quality.get("category_confidence") or 0.0)

                neg_list = list(negative_terms.get(target_category, [])) + list(slot_request.get("negative_terms") or [])
                hits = negative_hits(text, neg_list)
                neg_penalty = min(1.0, 0.25 * len(hits))

                composite_penalty = 0.2 if rec.get("is_composite") else 0.0

                score = (
                    0.30 * category_score
                    + 0.22 * semantic_score
                    + 0.12 * style_score
                    + 0.08 * support_score
                    + 0.05 * color_score
                    + 0.05 * quality_score
                    - neg_penalty
                    - composite_penalty
                )

                reason = (
                    f"category={rec.get('slot_category')}; semantic={semantic_score:.2f}; "
                    f"support={rec.get('support_class')}; style={asset_styles}; "
                    f"neg_hits={hits}; composite={rec.get('is_composite')}"
                )
                candidates.append(
                    CandidateScore(
                        asset_id=rec["asset_id"],
                        slot_category=rec.get("slot_category", "unknown"),
                        score=score,
                        reason=reason,
                    )
                )

    candidates.sort(key=lambda c: c.score, reverse=True)
    top = candidates[:top_k]

    result = {
        "slot_id": slot_id,
        "target_category": target_category,
        "top_candidates": [
            {
                "asset_id": c.asset_id,
                "slot_category": c.slot_category,
                "score": round(c.score, 4),
                "reason": c.reason,
            }
            for c in top
        ],
    }

    # Pair binding support
    if int(slot_request.get("count", 1)) > 1 and slot_request.get("pairing") == "same_asset":
        result["pair_binding"] = {
            "count": int(slot_request["count"]),
            "pairing": "same_asset",
            "selected_asset_id": top[0].asset_id if top else None,
        }

    return result
