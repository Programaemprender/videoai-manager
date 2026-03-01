#!/usr/bin/env python3
"""
Sistema Inteligente de Reconocimiento Facial con Notificaciones
Detecta caras recurrentes y solicita identificación solo cuando vale la pena
"""

import cv2
import json
import os
import numpy as np
from pathlib import Path
from datetime import datetime
import hashlib

class RecurrentFaceDetector:
    def __init__(self, db_path="faces_tracking.json", min_videos=2, min_appearances=3):
        """
        Args:
            db_path: Archivo JSON para tracking de caras
            min_videos: Mínimo de videos diferentes donde debe aparecer
            min_appearances: Mínimo de apariciones totales
        """
        self.db_path = db_path
        self.min_videos = min_videos
        self.min_appearances = min_appearances
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Cargar base de datos
        self.tracking_db = self.load_tracking_db()
        self.identified_people = self.load_identified_people()
    
    def load_tracking_db(self):
        """Carga base de datos de caras detectadas"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {
            "unknown_faces": {},  # face_id: {videos: [], appearances: int, sample_path: str}
            "pending_identification": [],  # [face_id, ...]
            "identified_faces": {}  # face_id: person_name
        }
    
    def save_tracking_db(self):
        """Guarda base de datos"""
        with open(self.db_path, 'w') as f:
            json.dump(self.tracking_db, f, indent=2)
    
    def load_identified_people(self):
        """Carga lista de personas ya identificadas"""
        faces_db_path = "faces_database"
        if not os.path.exists(faces_db_path):
            return []
        
        return [d for d in os.listdir(faces_db_path) 
                if os.path.isdir(os.path.join(faces_db_path, d))]
    
    def extract_face_descriptor(self, face_img):
        """
        Extrae descriptor simple de la cara para comparación
        (Histograma normalizado de intensidad)
        """
        if face_img.size == 0:
            return None
        
        # Redimensionar a tamaño estándar
        face_resized = cv2.resize(face_img, (100, 100))
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY) if len(face_resized.shape) == 3 else face_resized
        
        # Calcular histograma
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        return hist
    
    def compare_faces(self, desc1, desc2, threshold=0.7):
        """
        Compara dos descriptores de caras
        Retorna True si son similares
        """
        if desc1 is None or desc2 is None:
            return False
        
        # Correlación de histogramas
        correlation = cv2.compareHist(desc1.astype(np.float32), 
                                      desc2.astype(np.float32), 
                                      cv2.HISTCMP_CORREL)
        
        return correlation > threshold
    
    def find_matching_face_id(self, face_descriptor):
        """
        Busca si esta cara ya existe en la base de datos
        Retorna face_id si existe, None si no
        """
        for face_id, data in self.tracking_db["unknown_faces"].items():
            # Cargar descriptor guardado
            if "descriptor" not in data:
                continue
            
            saved_desc = np.array(data["descriptor"])
            
            if self.compare_faces(face_descriptor, saved_desc):
                return face_id
        
        return None
    
    def generate_face_id(self, video_name, timestamp):
        """Genera ID único para una cara"""
        unique_str = f"{video_name}_{timestamp}_{datetime.now().isoformat()}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]
    
    def process_video(self, video_path, video_name=None):
        """
        Procesa un video y extrae caras
        Retorna lista de caras detectadas con metadata
        """
        if video_name is None:
            video_name = Path(video_path).stem
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"📹 Procesando: {video_name}")
        print(f"   Duración: {duration:.1f}s, {total_frames} frames")
        
        faces_in_video = []
        frame_count = 0
        
        # Procesar cada 30 frames (~0.5s a 60fps)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            if frame_count % 30 != 0:
                continue
            
            # Detectar caras
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(80, 80))
            
            for (x, y, w, h) in faces:
                # Extraer cara con margen
                margin = 30
                x1 = max(0, x - margin)
                y1 = max(0, y - margin)
                x2 = min(frame.shape[1], x + w + margin)
                y2 = min(frame.shape[0], y + h + margin)
                
                face_img = frame[y1:y2, x1:x2]
                
                if face_img.shape[0] < 80 or face_img.shape[1] < 80:
                    continue
                
                # Extraer descriptor
                descriptor = self.extract_face_descriptor(face_img)
                if descriptor is None:
                    continue
                
                # Buscar si esta cara ya existe
                face_id = self.find_matching_face_id(descriptor)
                
                timestamp = frame_count / fps
                
                if face_id is None:
                    # Nueva cara
                    face_id = self.generate_face_id(video_name, timestamp)
                    
                    # Guardar frame como sample
                    sample_folder = "face_samples"
                    os.makedirs(sample_folder, exist_ok=True)
                    sample_path = os.path.join(sample_folder, f"{face_id}_sample.jpg")
                    cv2.imwrite(sample_path, face_img)
                    
                    # Guardar screenshot completo del video
                    screenshot_path = os.path.join(sample_folder, f"{face_id}_scene.jpg")
                    cv2.imwrite(screenshot_path, frame)
                    
                    self.tracking_db["unknown_faces"][face_id] = {
                        "videos": [video_name],
                        "appearances": 1,
                        "first_seen": video_name,
                        "sample_path": sample_path,
                        "screenshot_path": screenshot_path,
                        "timestamp": timestamp,
                        "descriptor": descriptor.tolist()
                    }
                    
                    print(f"   ✓ Nueva cara detectada: {face_id}")
                
                else:
                    # Cara conocida
                    if video_name not in self.tracking_db["unknown_faces"][face_id]["videos"]:
                        self.tracking_db["unknown_faces"][face_id]["videos"].append(video_name)
                    
                    self.tracking_db["unknown_faces"][face_id]["appearances"] += 1
                    
                    print(f"   ✓ Cara conocida: {face_id} (aparición #{self.tracking_db['unknown_faces'][face_id]['appearances']})")
                
                faces_in_video.append(face_id)
        
        cap.release()
        self.save_tracking_db()
        
        return list(set(faces_in_video))  # Únicos
    
    def get_faces_pending_identification(self):
        """
        Retorna lista de caras que cumplen criterios para ser identificadas
        """
        pending = []
        
        for face_id, data in self.tracking_db["unknown_faces"].items():
            # Verificar si ya fue identificada
            if face_id in self.tracking_db["identified_faces"]:
                continue
            
            # Verificar si ya está en cola de identificación pendiente
            if face_id in self.tracking_db["pending_identification"]:
                continue
            
            # Criterios: aparece en múltiples videos Y suficientes veces
            num_videos = len(data["videos"])
            num_appearances = data["appearances"]
            
            if num_videos >= self.min_videos and num_appearances >= self.min_appearances:
                pending.append({
                    "face_id": face_id,
                    "videos": data["videos"],
                    "appearances": num_appearances,
                    "sample_path": data["sample_path"],
                    "screenshot_path": data["screenshot_path"],
                    "first_seen": data["first_seen"]
                })
        
        return pending
    
    def mark_as_pending(self, face_id):
        """Marca una cara como pendiente de identificación"""
        if face_id not in self.tracking_db["pending_identification"]:
            self.tracking_db["pending_identification"].append(face_id)
            self.save_tracking_db()
    
    def identify_face(self, face_id, person_name):
        """
        Registra la identificación de una cara
        """
        if face_id not in self.tracking_db["unknown_faces"]:
            print(f"❌ Face ID {face_id} no encontrado")
            return False
        
        # Marcar como identificada
        self.tracking_db["identified_faces"][face_id] = person_name
        
        # Remover de pendientes
        if face_id in self.tracking_db["pending_identification"]:
            self.tracking_db["pending_identification"].remove(face_id)
        
        self.save_tracking_db()
        
        print(f"✅ Cara {face_id} identificada como: {person_name}")
        return True
    
    def get_summary(self):
        """Retorna resumen del estado del sistema"""
        total_unknown = len(self.tracking_db["unknown_faces"])
        total_identified = len(self.tracking_db["identified_faces"])
        pending_count = len(self.get_faces_pending_identification())
        
        return {
            "total_faces_detected": total_unknown,
            "identified": total_identified,
            "pending_identification": pending_count,
            "known_people": len(self.identified_people)
        }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  Procesar video:")
        print("    python sistema_caras_recurrentes.py <video.mp4>")
        print()
        print("  Ver resumen:")
        print("    python sistema_caras_recurrentes.py --summary")
        print()
        print("  Ver caras pendientes:")
        print("    python sistema_caras_recurrentes.py --pending")
        print()
        print("  Identificar cara:")
        print("    python sistema_caras_recurrentes.py --identify <face_id> <nombre>")
        sys.exit(1)
    
    detector = RecurrentFaceDetector(min_videos=2, min_appearances=3)
    
    if sys.argv[1] == "--summary":
        summary = detector.get_summary()
        print("\n📊 Resumen del Sistema")
        print("=" * 50)
        print(f"Total caras detectadas: {summary['total_faces_detected']}")
        print(f"Caras identificadas: {summary['identified']}")
        print(f"Pendientes identificación: {summary['pending_identification']}")
        print(f"Personas conocidas: {summary['known_people']}")
    
    elif sys.argv[1] == "--pending":
        pending = detector.get_faces_pending_identification()
        
        if not pending:
            print("\n✅ No hay caras pendientes de identificación")
        else:
            print(f"\n👤 Caras pendientes de identificación: {len(pending)}")
            print("=" * 50)
            for face in pending:
                print(f"\nFace ID: {face['face_id']}")
                print(f"  Videos: {', '.join(face['videos'])}")
                print(f"  Apariciones: {face['appearances']}")
                print(f"  Primera vez: {face['first_seen']}")
                print(f"  Screenshot: {face['screenshot_path']}")
    
    elif sys.argv[1] == "--identify":
        if len(sys.argv) < 4:
            print("❌ Uso: python sistema_caras_recurrentes.py --identify <face_id> <nombre>")
            sys.exit(1)
        
        face_id = sys.argv[2]
        person_name = sys.argv[3]
        detector.identify_face(face_id, person_name)
    
    else:
        # Procesar video
        video_path = sys.argv[1]
        if not os.path.exists(video_path):
            print(f"❌ Video no encontrado: {video_path}")
            sys.exit(1)
        
        faces = detector.process_video(video_path)
        
        print(f"\n✅ Video procesado: {len(faces)} caras únicas detectadas")
        
        # Verificar si hay caras pendientes
        pending = detector.get_faces_pending_identification()
        if pending:
            print(f"\n⚠️ HAY {len(pending)} CARA(S) RECURRENTE(S) QUE NECESITAN IDENTIFICACIÓN")
            print("   Ejecuta: python sistema_caras_recurrentes.py --pending")
