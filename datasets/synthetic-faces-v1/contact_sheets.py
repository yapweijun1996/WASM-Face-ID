#!/usr/bin/env python3
"""Create only complete, labeled review sheets; report missing images."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
ROOT = Path(__file__).resolve().parent
people = json.loads((ROOT / "identities.json").read_text(encoding="utf-8"))
conditions = json.loads((ROOT / "generation-config.json").read_text(encoding="utf-8"))["conditions"]
out = ROOT / "contact-sheets"
out.mkdir(exist_ok=True)

def sheet(items, destination):
    columns, cell_w, cell_h = 4, 190, 220
    canvas = Image.new("RGB", (columns * cell_w, math.ceil(len(items) / columns) * cell_h), "white")
    draw = ImageDraw.Draw(canvas)
    for index, (label, path) in enumerate(items):
        x, y = index % columns * cell_w, index // columns * cell_h
        with Image.open(path) as image:
            thumb = ImageOps.contain(image.convert("RGB"), (180, 180))
            canvas.paste(thumb, (x + (cell_w-thumb.width)//2, y))
        draw.text((x+5, y+184), label, fill="black")
    canvas.save(destination, "PNG")

for person in people:
    folder = ROOT / "identities" / (person["identity_id"] + "_" + person["name"].replace(" ", "_"))
    items = [(person["identity_id"] + " " + c["filename"][:-4], folder / c["filename"]) for c in conditions]
    if all(path.is_file() for _, path in items):
        sheet(items, out / (person["identity_id"] + ".png"))
    else:
        print(person["identity_id"], "sheet not generated: incomplete images")
references = [(p["identity_id"], ROOT / "references" / (p["identity_id"] + "_" + p["name"].replace(" ", "_") + ".png")) for p in people]
if all(path.is_file() for _, path in references):
    sheet(references, out / "master.png")
else:
    print("Master sheet not generated: incomplete references")
