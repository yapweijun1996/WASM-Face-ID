# Synthetic Faces v1 ? HOLD

This isolated worktree contains a dataset preparation and validation scaffold, not a completed or approved benchmark. Ten identities are fictional labels. No real employee data is intended. `references/` contains ten generated master references and two pilot PNGs; they are not counted as benchmark images. Each identity has a derived front-facing JPEG, and P001 has ten additional reference-conditioned variants. All are pending review. Empty folders may not be preserved by Git.

## Generation

Read `identities.json` and `generation-config.json`. Generate a master for each person, then use that master as the image-edit reference for every condition. Produce 512 ? 512 RGB JPEGs under the corresponding identity folder. Use `01`?`03` exclusively for enrollment and `04`?`11` exclusively for queries. Record the real provider, model/version, output rights, seed (only if available), timestamp, prompts and reference relationships in a provenance record before release. Names alone are not identity conditioning. The OpenAI built-in image tool supports reference edits but does not expose a model version or reproducible seed in this session; its identity preservation has not been independently verified. Initial visual inspection suggests P001 left and right pose outputs point in the same direction; verify and regenerate as needed before acceptance.

## Validation

Requires Python and Pillow. Run `python datasets/synthetic-faces-v1/validate.py` from the worktree. The report and manifest describe only files actually found, and the command exits nonzero while the dataset is HOLD. It checks expected identities, paths, split assignments, JPEG integrity, dimensions, RGB, exact SHA-256 duplicates and file counts. Missing files are errors. This does not establish visual uniqueness or identity.

For actual face checks, use an independently verified, licensed local model and supply `--adapter PATH`. The trusted Python adapter must expose `detect(image)` returning `[x, y, width, height]` pixel boxes, and `embed(image, box)` returning a numeric face embedding. It receives a Pillow RGB image and must run the real model, including its documented preprocessing and alignment. Do not use a mock for acceptance. No weights are downloaded. The validator reports score distributions and highest between-person similarities; calibrate thresholds independently. Bounding-box defaults are configurable, not a universal standard.

Complete one labeled contact sheet per identity and a master sheet; manually review consistency, crop, poses, and collisions. Automated embeddings are supporting evidence, not identity proof. The validator deliberately keeps HOLD pending human review and rights determination.

## Rights and limits

The applicable OpenAI terms depend on the account and service. OpenAI's [individual terms](https://openai.com/policies/terms-of-use/) and [services agreement](https://openai.com/policies/services-agreement/) state output ownership subject to their terms and applicable law; they do not by themselves prove third-party rights or approve a dataset license. Internal testing, public redistribution, commercial demos, and published benchmarks remain unapproved here until the applicable agreement, policy and image rights are reviewed. This synthetic set has no unknown identities and cannot measure unknown-person rejection. Biometric thresholds and real-world performance require independent datasets and evaluation.
