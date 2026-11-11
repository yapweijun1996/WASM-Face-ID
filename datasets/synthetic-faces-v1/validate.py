#!/usr/bin/env python3
"""Validate actual dataset files. No models are downloaded or inferred."""
import argparse
import hashlib
import importlib.util
import json
import math
import statistics
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent


def load_adapter(path):
    if not path:
        return None
    spec = importlib.util.spec_from_file_location("face_validation_adapter", path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load adapter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path, help="Trusted local detector/embedding adapter; see README")
    parser.add_argument("--min-face-fraction", type=float, default=0.20)
    parser.add_argument("--margin-fraction", type=float, default=0.01)
    args = parser.parse_args()
    if not 0 < args.min_face_fraction < 1 or not 0 <= args.margin_fraction < .5:
        parser.error("Invalid face size or margin")
    identities = json.loads((ROOT / "identities.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "generation-config.json").read_text(encoding="utf-8"))
    adapter = load_adapter(args.adapter)
    errors, entries, hashes, vectors = [], [], {}, []
    folders = list((ROOT / "identities").iterdir())
    if len(identities) != 10 or len({x["identity_id"] for x in identities}) != 10:
        errors.append("Expected exactly 10 distinct identities")
    expected_dirs = {x["identity_id"] + "_" + x["name"].replace(" ", "_") for x in identities}
    if {x.name for x in folders if x.is_dir()} != expected_dirs:
        errors.append("Identity folders do not match registry")
    expected = {c["filename"] for c in config["conditions"]}
    if len(expected) != 11 or [c["dataset_split"] for c in config["conditions"]] != ["enrollment"] * 3 + ["recognition_test"] * 8:
        errors.append("Invalid expected filenames or split definitions")
    faces_checked, embeddings_checked = 0, 0
    for person in identities:
        directory = ROOT / "identities" / (person["identity_id"] + "_" + person["name"].replace(" ", "_"))
        files = {p.name for p in directory.iterdir() if p.is_file()} if directory.exists() else set()
        if files != expected:
            errors.append(f"{person['identity_id']}: missing {sorted(expected - files)}, unexpected {sorted(files - expected)}")
        for condition in config["conditions"]:
            path = directory / condition["filename"]
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT).as_posix()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest in hashes:
                errors.append(f"Duplicate SHA-256: {relative} and {hashes[digest]}")
            hashes[digest] = relative
            try:
                with Image.open(path) as im:
                    im.verify()
                with Image.open(path) as im:
                    im.load()
                    if im.format != "JPEG" or im.mode != "RGB" or im.size != (512, 512):
                        errors.append(f"{relative}: expected RGB JPEG 512x512, got {im.format} {im.mode} {im.size}")
                    rgb = im.copy()
                    width, height = im.size
            except Exception as exc:
                errors.append(f"{relative}: corrupt or unreadable: {type(exc).__name__}: {exc}")
                continue
            entry = {**person, "image_path": relative, "image_condition":condition["description"], "dataset_split":condition["dataset_split"], "synthetic":True, "width":width, "height":height, "sha256":digest, "generation_model":None, "generation_seed":None, "generation_timestamp":None, "license":None, "commercial_usage_status":"unverified"}
            entries.append(entry)
            if adapter:
                try:
                    boxes = adapter.detect(rgb)
                    faces_checked += 1
                    if len(boxes) != 1:
                        errors.append(f"{relative}: detector returned {len(boxes)} faces")
                        continue
                    x, y, w, h = map(float, boxes[0])
                    if not all(math.isfinite(v) for v in (x, y, w, h)) or min(w, h) < 512 * args.min_face_fraction or x < 512 * args.margin_fraction or y < 512 * args.margin_fraction or x + w > 512 * (1 - args.margin_fraction) or y + h > 512 * (1 - args.margin_fraction):
                        errors.append(f"{relative}: invalid, small or edge-cropped face box {boxes[0]}")
                    v = [float(q) for q in adapter.embed(rgb, boxes[0])]
                    norm = math.sqrt(sum(q*q for q in v))
                    if not v or not math.isfinite(norm) or norm == 0:
                        raise ValueError("Invalid embedding")
                    vectors.append((person["identity_id"], relative, [q/norm for q in v]))
                    embeddings_checked += 1
                except Exception as exc:
                    errors.append(f"{relative}: adapter failed: {type(exc).__name__}: {exc}")
    actual_files = list((ROOT / "identities").rglob("*.jpg"))
    if len(actual_files) != 110 or len(entries) != 110:
        errors.append(f"Expected 110 JPEGs; found {len(actual_files)}, readable expected files {len(entries)}")
    within, between = [], []
    for i, (identity, path, vector) in enumerate(vectors):
        for other, other_path, other_vector in vectors[i + 1:]:
            if len(vector) != len(other_vector):
                errors.append(f"Embedding dimensions differ: {path}, {other_path}")
                continue
            score = sum(a*b for a,b in zip(vector,other_vector))
            (within if identity == other else between).append((score,path,other_path))
    def distribution(pairs):
        values = sorted(x[0] for x in pairs)
        if not values:
            return None
        return {"count":len(values), "min":values[0], "median":statistics.median(values), "max":values[-1]}
    collisions = sorted(between, reverse=True)[:10]
    report = {"status":"HOLD", "expected_images":110, "actual_jpeg_count":len(actual_files), "valid_manifest_entries":len(entries), "face_detection_checked":faces_checked, "embeddings_checked":embeddings_checked, "within_identity_cosine":distribution(within), "between_identity_cosine":distribution(between), "highest_between_identity_pairs":collisions, "collision_interpretation":"Review high-similarity pairs after independently calibrating a threshold; top pairs alone are not confirmed collisions.", "manual_review":"NOT COMPLETED", "license_review":"NOT COMPLETED", "adapter":str(args.adapter) if args.adapter else None, "errors":errors, "missing_checks": ([] if adapter and faces_checked == 110 and embeddings_checked == 110 else ["actual face detection and recognition embedding validation"]) + ["manual identity consistency review", "applicable provider terms and redistribution approval"]}
    (ROOT / "manifest.json").write_text(json.dumps({"status":"HOLD", "images":entries}, indent=2)+"\n", encoding="utf-8")
    (ROOT / "validation-report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status":report["status"], "images":len(entries), "errors":len(errors), "missing_checks":report["missing_checks"]}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
