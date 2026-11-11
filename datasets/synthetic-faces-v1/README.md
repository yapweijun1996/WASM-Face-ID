# Synthetic Faces v1 ? HOLD

This directory contains 110 synthetic benchmark images, but is not yet an approved benchmark. Ten identities are fictional labels. No real employee data is intended. `references/` contains ten generated master references and two pilot PNGs; they are not counted as benchmark images. Each identity has one derived front-facing JPEG and ten reference-conditioned variants. The derived JPEG uses the same generated image as its corresponding master reference. Empty folders may not be preserved by Git.

## Generation

Read `identities.json` and `generation-config.json`. Generate a master for each person, then use that master as the image-edit reference for every condition. Produce 512 ? 512 RGB JPEGs under the corresponding identity folder. Use `01`?`03` exclusively for enrollment and `04`?`11` exclusively for queries. Record the real provider, model/version, output rights, seed (only if available), timestamp, prompts and reference relationships in a provenance record before release. Names alone are not identity conditioning. The OpenAI built-in image tool supports reference edits but does not expose a model version or reproducible seed in this session; its identity preservation has not been independently verified. P001 left and right pose outputs have been regenerated to face opposite directions; exact angle and identity remain to be validated.

## Validation

Requires Python and Pillow. Run `python datasets/synthetic-faces-v1/validate.py` from the worktree. The report and manifest describe only files actually found, and the command exits nonzero while the dataset is HOLD. It checks expected identities, paths, split assignments, JPEG integrity, dimensions, RGB, exact SHA-256 duplicates and file counts. Missing files are errors. This does not establish visual uniqueness or identity.

For actual face checks, use an independently verified, licensed local model and supply `--adapter PATH`. The trusted Python adapter must expose `detect(image)` returning `[x, y, width, height]` pixel boxes, and `embed(image, box)` returning a numeric face embedding. It receives a Pillow RGB image and must run the real model, including its documented preprocessing and alignment. Do not use a mock for acceptance. No weights are downloaded. The validator reports score distributions and highest between-person similarities; calibrate thresholds independently. Bounding-box defaults are configurable, not a universal standard.

Labeled contact sheets exist for all ten identities and the master references. They were visually inspected by the assistant, but independent human review of consistency, crop, poses, and collisions is still pending. Automated embeddings are supporting evidence, not identity proof. The validator deliberately keeps HOLD pending human review and rights determination.

## Rights and limits

The applicable OpenAI terms depend on the account and service. Internal testing, public redistribution, commercial demos and published benchmark use each remain pending confirmation against those applicable terms and other rights. OpenAI's [individual terms](https://openai.com/policies/terms-of-use/) and [services agreement](https://openai.com/policies/services-agreement/) state output ownership subject to their terms and applicable law; they do not by themselves prove third-party rights or approve a dataset license.  This synthetic set has no unknown identities and cannot measure unknown-person rejection. Biometric thresholds and real-world performance require independent datasets and evaluation.

## Current review findings

P008?P010 output-to-condition mappings were reconstructed after the image tool response exceeded its transport limit, using SFace similarities and visual review; they require independent review. Pairwise SFace scores overlap across same- and different-identity comparisons. The highest different-identity pair involves P004 and P008; this is a review lead, not proof of a collision. Generated queries are edits derived from the same identity reference, rather than independent camera captures, and may overstate real-world performance.
