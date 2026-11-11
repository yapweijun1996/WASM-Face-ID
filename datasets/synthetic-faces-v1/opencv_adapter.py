import os
import cv2
import numpy as np
from pathlib import Path
ROOT=Path(os.environ["WASM_FACE_VALIDATION_MODELS"]).resolve()
detector=cv2.FaceDetectorYN.create(str(ROOT/"face_detection_yunet_2023mar.onnx"),"",(320,320),0.85,0.3,5000)
recognizer=cv2.FaceRecognizerSF.create(str(ROOT/"face_recognition_sface_2021dec.onnx"),"")
last_faces=[]
def detect(image):
    global last_faces
    rgb=np.asarray(image.convert("RGB"))
    bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
    detector.setInputSize((320,320))
    small=cv2.resize(bgr,(320,320))
    _,faces=detector.detect(small)
    if faces is None:
        last_faces=[]
        return []
    scale_x=bgr.shape[1]/320
    scale_y=bgr.shape[0]/320
    last_faces=[]
    for face in faces:
        face=face.copy()
        face[0:14:2]*=scale_x
        face[1:14:2]*=scale_y
        last_faces.append(face)
    return [face[:4].tolist() for face in last_faces]
def embed(image,box):
    if len(last_faces)!=1: raise ValueError("Expected exactly one face")
    bgr=cv2.cvtColor(np.asarray(image.convert("RGB")),cv2.COLOR_RGB2BGR)
    aligned=recognizer.alignCrop(bgr,last_faces[0])
    return recognizer.feature(aligned).flatten().tolist()
