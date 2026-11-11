#!/usr/bin/env python3
"""Validate synthetic portrait variants and create contact sheets and reports."""
import hashlib
import importlib.util
import json
import math
import statistics
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
MODEL_ADAPTER = ROOT.parent / "synthetic-faces-v1" / "opencv_adapter.py"
people = json.loads((ROOT / "identities.json").read_text(encoding="utf-8"))
conditions = json.loads((ROOT / "generation-config.json").read_text(encoding="utf-8"))["conditions"]
spec = importlib.util.spec_from_file_location("face_adapter", MODEL_ADAPTER)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
errors, entries, seen, vectors = [], [], {}, []
(ROOT / "contact-sheets").mkdir(exist_ok=True)
for person in people:
    pid = person["identity_id"]
    items = []
    for index, condition in enumerate(conditions):
        path = ROOT / person["image_path"] if index == 0 else ROOT / "variants" / pid / condition["filename"]
        if not path.exists():
            errors.append(f"{pid}: missing {condition['filename']}")
            continue
        rel = path.relative_to(ROOT).as_posix()
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if sha in seen:
            errors.append(f"Duplicate: {rel}, {seen[sha]}")
        seen[sha] = rel
        try:
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                im.load()
                if im.format != "JPEG" or im.mode != "RGB" or im.size != (512,512):
                    errors.append(f"{rel}: invalid JPEG format, RGB or dimensions")
                rgb = im.convert("RGB")
            boxes = adapter.detect(rgb)
            if len(boxes) != 1:
                errors.append(f"{rel}: {len(boxes)} detected faces")
            else:
                x,y,w,h = boxes[0]
                if min(w,h) < 102.4 or min(x,y) < 5.12 or x+w > 506.88 or y+h > 506.88:
                    errors.append(f"{rel}: small or edge-cropped face {boxes[0]}")
                v = [float(x) for x in adapter.embed(rgb, boxes[0])]
                norm = math.sqrt(sum(x*x for x in v))
                if not math.isfinite(norm) or norm == 0:
                    errors.append(f"{rel}: invalid embedding")
                else:
                    vectors.append((pid,rel,[x/norm for x in v]))
            entries.append({"identity_id":pid,"name":person["name"],"gender":person["gender"],"nationality":person["nationality"],"prompted_background":person["prompted_background"],"image_path":rel,"image_condition":condition["description"],"dataset_split":condition["dataset_split"],"sha256":sha,"synthetic":True,"width":512,"height":512,"generation_provider":"OpenAI built-in image generation","generation_model":None,"generation_seed":None,"generation_timestamp":None,"license":None,"commercial_usage_status":"pending review"})
            items.append((condition["filename"],path))
        except Exception as exc:
            errors.append(f"{rel}: validation error {type(exc).__name__}: {exc}")
    if len(items) == 11:
        canvas = Image.new("RGB",(760,660),"white")
        draw = ImageDraw.Draw(canvas)
        for i,(label,path) in enumerate(items):
            x=(i%4)*190;y=(i//4)*220
            with Image.open(path) as im:
                thumb=ImageOps.contain(im.convert("RGB"),(180,180))
                canvas.paste(thumb,(x+(190-thumb.width)//2,y))
            draw.text((x+4,y+184),pid+" "+label[:-4],fill="black")
        canvas.save(ROOT / "contact-sheets" / (pid+".png"))
expected_paths = {ROOT / p["image_path"] for p in people}
expected_paths.update(ROOT / "variants" / p["identity_id"] / c["filename"] for p in people for c in conditions[1:])
actual_paths = set((ROOT / "images").rglob("*.jpg")) | set((ROOT / "variants").rglob("*.jpg"))
for extra in sorted(actual_paths - expected_paths):
    errors.append(f"Unexpected image: {extra.relative_to(ROOT).as_posix()}")
if len(conditions) != 11 or [c["dataset_split"] for c in conditions] != ["enrollment"] * 3 + ["recognition_test"] * 8:
    errors.append("Expected 3 enrollment and 8 recognition conditions")
if len(people) != 10 or len({p["identity_id"] for p in people}) != 10:
    errors.append("Expected 10 distinct identities")
if len(entries) != 110:
    errors.append(f"Expected 110 images, found {len(entries)}")
within,between=[],[]
for i,(pid,path,v) in enumerate(vectors):
    for other,other_path,w in vectors[i+1:]:
        score=sum(a*b for a,b in zip(v,w))
        (within if pid==other else between).append((score,path,other_path))
def summary(pairs):
    values=sorted(x[0] for x in pairs)
    return {"count":len(values),"min":values[0],"median":statistics.median(values),"max":values[-1]} if values else None
report={"status":"HOLD","identity_count":len(people),"images_checked":len(entries),"embeddings_checked":len(vectors),"errors":errors,"within_identity_cosine":summary(within),"between_identity_cosine":summary(between),"lowest_within_identity_pairs":sorted(within)[:10],"highest_between_identity_pairs":sorted(between,reverse=True)[:10],"similarity_ranges_overlap": bool(within and between and min(x[0] for x in within) <= max(x[0] for x in between)),"manual_review":"PENDING","rights_review":"PENDING","note":"No universal matching threshold; embeddings and synthetic edits do not prove identity or real-world performance."}
(ROOT/"manifest.json").write_text(json.dumps({"status":"HOLD","images":entries},indent=2)+"\n",encoding="utf-8")
(ROOT/"validation-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":"HOLD","images":len(entries),"embeddings":len(vectors),"errors":len(errors)},indent=2))
raise SystemExit(1 if errors else 0)
