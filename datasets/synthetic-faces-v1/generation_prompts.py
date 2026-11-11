#!/usr/bin/env python3
"""Print a reproducible prompt plan; no service calls or model downloads."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent
people = json.loads((root / "identities.json").read_text(encoding="utf-8"))
config = json.loads((root / "generation-config.json").read_text(encoding="utf-8"))
for p in people:
    print(f"\n{p['identity_id']} {p['name']} ({p['gender']})")
    print("MASTER:", config['master_prompt'], "Subject:", p['gender'], p['intended_visual_profile'])
    for c in config['conditions']:
        print(c['filename'], "[", c['dataset_split'], "]:", config['variant_prompt'], c['description'])
