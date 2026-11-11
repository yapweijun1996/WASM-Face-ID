# Review status: HOLD

- 110 images exist: 30 enrollment and 80 query images. All were derived from synthetic reference images; query filenames are separate, but generated edits share their identity reference with enrollment.
- All ten per-identity contact sheets and the master contact sheet were inspected visually by the assistant. An independent human review is outstanding; automated checks and AI visual inspection cannot prove identity.
- SFace same-identity scores (550 pairs): minimum 0.6695, median 0.8376, maximum 0.9725. Different-identity scores (5,445 pairs): minimum 0.0640, median 0.3317, maximum 0.6956. The overlap requires investigation and no threshold is inferred.
- Highest different-identity score: P004 `08_low_light.jpg` versus P008 `10_background.jpg` (0.6956); check those identities and related scores. Lowest same-identity score: P005 `07_glasses.jpg` versus `09_side_light.jpg` (0.6695).
- P008?P010 variant-to-condition mapping was reconstructed using SFace and visual contact sheets after an output transport limit; independent review is required.
- The apparent pose direction is opposite for left and right variants, but exact 20-degree angles were not measured.
- Applicable provider terms and image rights must be checked for internal testing, public redistribution, commercial demos and publication. The generation model version, seed and exact generation timestamps were not exposed.
- The dataset has no unknown identities and cannot measure unknown-person rejection; generated faces are not representative evidence for production performance.
