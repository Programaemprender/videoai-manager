#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline V6 Completo - Prepara frames para análisis GPT-4V
OpenClaw ejecutará el análisis con la herramienta image
"""

import sys
import io
import os
import json
import cv2
from datetime import datetime
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SERVICE_ACCOUNT_FILE = r'C:\Users\achun\.openclaw\workspace\.secrets\google-service-account-tupibox.json'
SCOPES_DRIVE = ['https://www.googleapis.com/auth/drive']

# Configuración
if len(sys.argv) < 2:
    print("Uso: python pipeline_v6_complete.py <FILE_ID>")
    sys.exit(1)

FILE_ID = sys.argv[1]
TEMP_DIR = "temp_v6_frames"
os.makedirs(TEMP_DIR, exist_ok=True)

print(f"[*] Pipeline V6 - GPT-4 Vision Analysis\n")
print(f"[*] File ID: {FILE_ID}\n")

# 1. DESCARGAR VIDEO
print("[1/3] Descargando video...")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES_DRIVE
)
drive_service = build('drive', 'v3', credentials=credentials)

file_info = drive_service.files().get(fileId=FILE_ID, fields='name,size').execute()
original_name = file_info['name']
size_mb = int(file_info.get('size', 0)) / 1024 / 1024

print(f"  Archivo: {original_name}")
print(f"  Tamaño: {size_mb:.1f} MB")

temp_video_path = os.path.join(TEMP_DIR, f"video_{FILE_ID}.mp4")
request = drive_service.files().get_media(fileId=FILE_ID)

with open(temp_video_path, 'wb') as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

print(f"  [OK] Descargado\n")

# 2. EXTRAER FRAMES
print("[2/3] Extrayendo frames clave...")

cap = cv2.VideoCapture(temp_video_path)

fps = cap.get(cv2.CAP_PROP_FPS) or 30
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps

print(f"  Duración: {duration:.1f}s")
print(f"  FPS: {fps:.1f}")

# 3 frames estratégicos
positions = [
    int(frame_count * 0.2),
    int(frame_count * 0.5),
    int(frame_count * 0.8)
]

frame_paths = []
for i, pos in enumerate(positions, 1):
    cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
    ret, frame = cap.read()
    
    if ret:
        frame_path = os.path.join(TEMP_DIR, f"frame_{i}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_paths.append(frame_path)
        print(f"  [OK] Frame {i} extraído")

cap.release()

# 3. PREPARAR METADATA PARA OPENCLAW
print("\n[3/3] Preparando metadata para análisis GPT-4V...")

metadata = {
    "file_id": FILE_ID,
    "original_name": original_name,
    "duration": duration,
    "frames": [os.path.abspath(f) for f in frame_paths],
    "temp_video": os.path.abspath(temp_video_path),
    "analysis_prompt": """Analiza esta imagen de un video y responde SOLO con un JSON válido (sin markdown, sin ```json):

{
  "location": "Una de: Playa, Casa, Oficina_Yeppo, Calle_Santiago, Gym, Parque, Montana, Naturaleza, Restaurant, Rio, Mall",
  "action": "Una de: Caminar, Correr, Comer, Trabajar, Ejercitar, Descansar, Conversar, Conducir, Ciclismo, Cocinar, Nadar, Estudiar",
  "emotion": "Una de: Energia, Calma, Alegria, Concentracion, Relax, Esfuerzo, Logro",
  "shot_type": "Una de: Closeup, TerceraPersona, POV",
  "persons_count": número de personas visibles,
  "description": "Descripción breve en español (max 100 caracteres)"
}

Criterios:
- Playa: mar, océano, arena, costa
- Caminar: velocidad normal/lenta
- Correr: ejercicio cardiovascular intenso
- Closeup: rostro >40% del frame
- TerceraPersona: persona visible desde afuera
- POV: perspectiva primera persona
- Energia: movimiento activo
- Calma: escena tranquila

Responde SOLO el JSON."""
}

metadata_path = os.path.join(TEMP_DIR, "metadata.json")
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"  [OK] Metadata guardada: {metadata_path}")
print(f"\n[OK] Frames listos para análisis GPT-4V")
print(f"\nFrames extraídos:")
for i, frame in enumerate(frame_paths, 1):
    print(f"  {i}. {frame}")

print(f"\n[NEXT] OpenClaw analizará estos frames con GPT-4V")
print(f"       Metadata: {metadata_path}")
