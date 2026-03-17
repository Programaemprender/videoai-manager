#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de limpieza automática de caras irrelevantes
Ejecuta después de procesar lotes grandes de videos
"""

import sys
import io
import json
import os
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TRACKING_DB_PATH = "faces_tracking.json"
MAX_UNKNOWN_FACES = 50  # Límite de caras en cache
MIN_VIDEOS_TO_KEEP = 1  # Mantener solo si aparece en 1+ videos
MIN_APPEARANCES_TO_KEEP = 2  # Mantener solo si aparece 2+ veces

def load_tracking_db():
    """Carga base de datos de tracking"""
    if os.path.exists(TRACKING_DB_PATH):
        with open(TRACKING_DB_PATH, 'r') as f:
            return json.load(f)
    return {"unknown_faces": {}, "pending_identification": [], "identified_faces": {}}

def save_tracking_db(db):
    """Guarda base de datos"""
    with open(TRACKING_DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def cleanup_irrelevant_faces():
    """
    Limpia caras irrelevantes del cache
    """
    db = load_tracking_db()
    
    unknown_faces = db["unknown_faces"]
    identified_faces = db["identified_faces"]
    pending = db["pending_identification"]
    
    print(f"\n{'='*60}")
    print("LIMPIEZA DE CARAS IRRELEVANTES")
    print(f"{'='*60}\n")
    print(f"Caras sin identificar: {len(unknown_faces)}")
    print(f"Caras identificadas: {len(identified_faces)}")
    print(f"Caras pendientes notificación: {len(pending)}\n")
    
    # 1. ELIMINAR CARAS YA IDENTIFICADAS DEL CACHE
    faces_to_remove = []
    for face_id in unknown_faces.keys():
        if face_id in identified_faces:
            faces_to_remove.append(face_id)
    
    if faces_to_remove:
        print(f"[1/3] Eliminando {len(faces_to_remove)} caras ya identificadas...")
        for face_id in faces_to_remove:
            # Eliminar archivos
            data = unknown_faces[face_id]
            if os.path.exists(data.get("sample_path", "")):
                os.remove(data["sample_path"])
            if os.path.exists(data.get("screenshot_path", "")):
                os.remove(data["screenshot_path"])
            
            del unknown_faces[face_id]
            print(f"  ✓ Eliminada: {face_id} ({identified_faces[face_id]})")
    else:
        print("[1/3] No hay caras identificadas en cache ✓\n")
    
    # 2. ELIMINAR CARAS DE 1 SOLO VIDEO CON POCAS APARICIONES
    faces_to_remove = []
    for face_id, data in unknown_faces.items():
        num_videos = len(data["videos"])
        num_appearances = data["appearances"]
        
        # Irrelevante si: 1 video Y <2 apariciones
        if num_videos < MIN_VIDEOS_TO_KEEP or num_appearances < MIN_APPEARANCES_TO_KEEP:
            # No eliminar si está pendiente de notificación
            if face_id not in pending:
                faces_to_remove.append(face_id)
    
    if faces_to_remove:
        print(f"\n[2/3] Eliminando {len(faces_to_remove)} caras irrelevantes (1 video, <2 apariciones)...")
        for face_id in faces_to_remove:
            data = unknown_faces[face_id]
            
            # Eliminar archivos
            if os.path.exists(data.get("sample_path", "")):
                os.remove(data["sample_path"])
            if os.path.exists(data.get("screenshot_path", "")):
                os.remove(data["screenshot_path"])
            
            del unknown_faces[face_id]
            print(f"  ✓ Eliminada: {face_id} (videos: {len(data['videos'])}, apariciones: {data['appearances']})")
    else:
        print("\n[2/3] No hay caras irrelevantes para eliminar ✓\n")
    
    # 3. SI HAY DEMASIADAS CARAS, ELIMINAR LAS MENOS RECURRENTES
    if len(unknown_faces) > MAX_UNKNOWN_FACES:
        print(f"\n[3/3] Cache lleno ({len(unknown_faces)} > {MAX_UNKNOWN_FACES}). Eliminando las menos recurrentes...")
        
        # Ordenar por recurrencia (videos × apariciones)
        sorted_faces = sorted(
            unknown_faces.items(),
            key=lambda x: len(x[1]["videos"]) * x[1]["appearances"]
        )
        
        # Eliminar las menos recurrentes
        num_to_remove = len(unknown_faces) - MAX_UNKNOWN_FACES
        faces_to_remove = sorted_faces[:num_to_remove]
        
        for face_id, data in faces_to_remove:
            # No eliminar si está pendiente
            if face_id in pending:
                continue
            
            # Eliminar archivos
            if os.path.exists(data.get("sample_path", "")):
                os.remove(data["sample_path"])
            if os.path.exists(data.get("screenshot_path", "")):
                os.remove(data["screenshot_path"])
            
            del unknown_faces[face_id]
            print(f"  ✓ Eliminada: {face_id} (score: {len(data['videos'])}×{data['appearances']})")
    else:
        print(f"\n[3/3] Cache OK ({len(unknown_faces)} ≤ {MAX_UNKNOWN_FACES}) ✓\n")
    
    # GUARDAR CAMBIOS
    db["unknown_faces"] = unknown_faces
    save_tracking_db(db)
    
    print(f"\n{'='*60}")
    print("LIMPIEZA COMPLETADA")
    print(f"{'='*60}\n")
    print(f"Caras sin identificar (después): {len(unknown_faces)}")
    print(f"Espacio liberado: ~{len(faces_to_remove) * 200}KB\n")

if __name__ == "__main__":
    cleanup_irrelevant_faces()
