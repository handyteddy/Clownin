# Video Face Overlay App
# Full Stack Implementation (Frontend + Backend)

## Backend - FastAPI (Python)
# Features:
# - Extract faces from uploaded video
# - Display faces for selection
# - Apply selected overlay (clown, comical, political, alien, zombie, anonymous, custom)
# - Process video & return downloadable result

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
import cv2
import numpy as np
import shutil
import os
from typing import List, Optional
from uuid import uuid4

app = FastAPI()

UPLOAD_FOLDER = "uploads/"
OVERLAY_FOLDER = "overlays/"
PROCESSED_FOLDER = "processed/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(OVERLAY_FOLDER, exist_ok=True)

OVERLAYS = {
    "clown": "overlays/clown.png",
    "political": "overlays/political.png",
    "comical": "overlays/comical.png",
    "alien": "overlays/alien.png",
    "zombie": "overlays/zombie.png",
    "anonymous": "overlays/anonymous.png"
}

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    file_path = f"{UPLOAD_FOLDER}{uuid4()}.{file_ext}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file_path}

@app.post("/upload_overlay/")
async def upload_overlay(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    file_path = f"{OVERLAY_FOLDER}{uuid4()}.{file_ext}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"overlay_path": file_path}

@app.post("/extract_faces/")
def extract_faces(video_path: str):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Unable to open video"}
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    frame_faces = []
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            face_path = f"{UPLOAD_FOLDER}face_{count}.jpg"
            cv2.imwrite(face_path, face)
            frame_faces.append(face_path)
            count += 1
    cap.release()
    return {"faces": frame_faces}

@app.post("/apply_overlay/")
def apply_overlay(video_path: str, face_index: List[int], overlay_type: str, custom_overlay: Optional[str] = None):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Unable to open video"}
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_path = f"{PROCESSED_FOLDER}{uuid4()}.mp4"
    out = cv2.VideoWriter(out_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))
    
    overlay_img_path = custom_overlay if custom_overlay else OVERLAYS.get(overlay_type, OVERLAYS["clown"])
    overlay_img = cv2.imread(overlay_img_path, cv2.IMREAD_UNCHANGED)
    if overlay_img is None:
        return {"error": "Overlay image not found"}
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        for i, (x, y, w, h) in enumerate(faces):
            if i in face_index:
                overlay_resized = cv2.resize(overlay_img, (w, h))
                if overlay_resized.shape[2] == 4:
                    alpha_channel = overlay_resized[:, :, 3] / 255.0
                    for c in range(3):
                        frame[y:y+h, x:x+w, c] = (1 - alpha_channel) * frame[y:y+h, x:x+w, c] + alpha_channel * overlay_resized[:, :, c]
                else:
                    frame[y:y+h, x:x+w] = overlay_resized[:, :, :3]
        out.write(frame)
    
    cap.release()
    out.release()
    return {"processed_video": out_path}
