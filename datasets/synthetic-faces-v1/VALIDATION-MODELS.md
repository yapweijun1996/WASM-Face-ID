# Local validation models

The current partial report used OpenCV 5.0.0, YuNet `face_detection_yunet_2023mar.onnx` and SFace `face_recognition_sface_2021dec.onnx`, with `opencv_adapter.py`. Files were obtained from the OpenCV Zoo and verified against the repository Git LFS SHA-256 pointers before use. The model files are not part of this dataset.

- YuNet: `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4` ([source](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)).
- SFace: `0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79` ([source](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface)).

The adapter detects on a 320-pixel image, scales face boxes and five landmarks back to the original, aligns with OpenCV `FaceRecognizerSF.alignCrop`, and produces L2-normalized vectors in the validator. The configured detector score threshold is 0.85. Similarity and face-size limits are experimental, not calibrated production thresholds. Source hashes establish file integrity only; they do not establish training-data rights, commercial eligibility or biometric reliability. Results depend on this detector and model and do not independently certify identities.

To run with independently obtained, hash-verified models in a local directory, set `WASM_FACE_VALIDATION_MODELS` to that directory and run `python datasets/synthetic-faces-v1/validate.py --adapter datasets/synthetic-faces-v1/opencv_adapter.py`. Model weights are intentionally not distributed here.
