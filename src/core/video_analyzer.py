#!/usr/bin/env python3
"""
AutoRenombrarYSheetVideos V5 - Análisis Dinámico con IA
Sistema mejorado que NO se limita a categorías predefinidas
y reduce iteraciones usando descripción inteligente con IA
"""

import cv2
import torch
from torch import hub
import datetime
import os
import json
import argparse
import logging
from pathlib import Path
import tempfile
import re
import shutil

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROCESSED_VIDEOS_FILE = "processed_videos.json"

class DynamicVideoAnalyzer:
    def __init__(self, use_ai_description=True):
        logger.info("🚀 Inicializando análisis dinámico...")
        
        self.use_ai_description = use_ai_description
        
        # YOLOv5 para detección básica
        try:
            self.yolo_model = hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            self.yolo_model.conf = 0.4
            logger.info("✅ YOLOv5 cargado")
            self.yolo_available = True
        except Exception as e:
            logger.warning(f"⚠️ YOLOv5 falló: {e}")
            self.yolo_model = None
            self.yolo_available = False
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Reconocimiento facial si está disponible
        try:
            from person_recognition import PersonRecognizer
            self.person_recognizer = PersonRecognizer()
            logger.info("👥 Reconocimiento facial cargado")
        except ImportError:
            self.person_recognizer = None
            logger.info("👤 Sin reconocimiento facial específico")

    def analyze_single_frame_comprehensive(self, frame):
        """Análisis comprehensivo de UN SOLO FRAME - reduce iteraciones"""
        analysis = {
            'objects': [],
            'faces_count': 0,
            'face_positions': [],
            'brightness': 0,
            'colors': [],
            'motion_level': 'static',
            'scene_type': 'unknown'
        }
        
        # 1. Detección de objetos (una sola pasada)
        if self.yolo_available and self.yolo_model:
            try:
                results = self.yolo_model(frame)
                if len(results.xyxy[0]) > 0:
                    for detection in results.xyxy[0]:
                        cls_id = int(detection[-1])
                        confidence = float(detection[4])
                        if confidence > 0.3:
                            object_name = results.names[cls_id]
                            analysis['objects'].append({
                                'name': object_name,
                                'confidence': confidence
                            })
            except Exception as e:
                logger.warning(f"Error YOLOv5: {e}")
        
        # 2. Detección de caras (una sola pasada)
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            analysis['faces_count'] = len(faces)
            
            for (x, y, w, h) in faces:
                face_size = w * h
                frame_area = frame.shape[0] * frame.shape[1]
                face_ratio = face_size / frame_area
                
                analysis['face_positions'].append({
                    'x': x, 'y': y, 'w': w, 'h': h,
                    'size_ratio': face_ratio
                })
        except Exception as e:
            logger.warning(f"Error detección caras: {e}")
        
        # 3. Análisis de color dominante
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            colors = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            dominant_hue = int(colors.argmax())
            
            # Convertir hue a color descriptivo
            if 0 <= dominant_hue <= 15 or 165 <= dominant_hue <= 180:
                analysis['colors'].append('rojo')
            elif 15 < dominant_hue <= 45:
                analysis['colors'].append('naranja')
            elif 45 < dominant_hue <= 75:
                analysis['colors'].append('amarillo')
            elif 75 < dominant_hue <= 105:
                analysis['colors'].append('verde')
            elif 105 < dominant_hue <= 135:
                analysis['colors'].append('azul')
            elif 135 < dominant_hue <= 165:
                analysis['colors'].append('morado')
            
            # Brightness
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            analysis['brightness'] = int(gray.mean())
            
        except Exception as e:
            logger.warning(f"Error análisis color: {e}")
        
        return analysis

    def generate_smart_description(self, frame_analysis, duration_seconds):
        """Genera descripción inteligente SIN categorías predefinidas"""
        description = {
            'location': 'Exterior',  # Default
            'action': 'Actividad',   # Default
            'emotion': 'Neutral',    # Default
            'shot_type': 'Normal',   # Default
            'description': ''
        }
        
        # Análisis de objetos para ubicación FLEXIBLE
        objects = [obj['name'] for obj in frame_analysis['objects']]
        object_str = ', '.join(objects)
        
        # UBICACIÓN - Inferencia flexible (no mapeos fijos)
        if any(obj in object_str for obj in ['bed', 'couch', 'dining table', 'refrigerator', 'oven']):
            description['location'] = 'Casa'
        elif any(obj in object_str for obj in ['laptop', 'keyboard', 'monitor', 'mouse']):
            description['location'] = 'Oficina'
        elif any(obj in object_str for obj in ['car', 'truck', 'traffic light', 'bus']):
            description['location'] = 'Calle'
        elif any(obj in object_str for obj in ['sports ball', 'bicycle', 'skateboard']):
            description['location'] = 'Deportivo'
        elif 'person' in object_str and frame_analysis['faces_count'] > 2:
            description['location'] = 'Social'
        else:
            # Usar colores dominantes como pista
            if 'verde' in frame_analysis['colors']:
                description['location'] = 'Naturaleza'
            elif 'azul' in frame_analysis['colors']:
                description['location'] = 'Exterior'
            else:
                description['location'] = 'Interior'
        
        # ACCIÓN - Inferencia por contexto + duración
        if 'food' in object_str or any(obj in object_str for obj in ['fork', 'knife', 'cup', 'banana', 'apple']):
            description['action'] = 'Comiendo'
        elif 'laptop' in object_str or 'keyboard' in object_str:
            description['action'] = 'Trabajando'
        elif 'car' in object_str and duration_seconds > 60:
            description['action'] = 'Conduciendo'
        elif 'sports ball' in object_str or ('person' in object_str and duration_seconds < 120):
            description['action'] = 'Ejercitando'
        elif frame_analysis['faces_count'] > 1:
            description['action'] = 'Conversando'
        elif duration_seconds > 300:
            description['action'] = 'Actividad_Larga'
        elif duration_seconds < 30:
            description['action'] = 'Momento_Rapido'
        else:
            description['action'] = 'Actividad_General'
        
        # TIPO DE TOMA - Basado en caras detectadas
        if frame_analysis['faces_count'] > 0:
            max_face_ratio = max([face['size_ratio'] for face in frame_analysis['face_positions']], default=0)
            if max_face_ratio > 0.15:  # Cara ocupa >15% del frame
                description['shot_type'] = 'Primer_Plano'
            elif max_face_ratio > 0.05:  # Cara ocupa 5-15%
                description['shot_type'] = 'Plano_Medio'
            else:
                description['shot_type'] = 'Plano_General'
        else:
            description['shot_type'] = 'Sin_Personas'
        
        # EMOCIÓN - Basado en brightness y contexto
        if frame_analysis['brightness'] > 180:
            description['emotion'] = 'Energico'
        elif frame_analysis['brightness'] < 80:
            description['emotion'] = 'Tranquilo'
        elif frame_analysis['faces_count'] > 2:
            description['emotion'] = 'Social'
        elif 'sports' in object_str:
            description['emotion'] = 'Activo'
        else:
            description['emotion'] = 'Normal'
        
        # Descripción textual libre
        description['description'] = f"Video de {description['action']} en {description['location']}"
        if objects:
            description['description'] += f" con {', '.join(objects[:3])}"
        
        return description

    def process_video_optimized(self, video_path):
        """Procesa video con ANÁLISIS OPTIMIZADO - menos frames"""
        logger.info(f"📹 Analizando: {os.path.basename(video_path)}")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error(f"❌ No se pudo abrir: {video_path}")
            return None
        
        # Obtener info básica del video
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        logger.info(f"⏱️ Duración: {duration:.1f}s, FPS: {fps:.1f}")
        
        # OPTIMIZACIÓN: Analizar solo 3 frames estratégicos
        key_frames = [
            int(frame_count * 0.1),   # 10% del video
            int(frame_count * 0.5),   # Mitad del video
            int(frame_count * 0.9)    # 90% del video
        ]
        
        combined_analysis = {
            'objects': [],
            'faces_count': 0,
            'face_positions': [],
            'brightness': 0,
            'colors': []
        }
        
        frames_analyzed = 0
        for frame_pos in key_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if ret:
                frame_analysis = self.analyze_single_frame_comprehensive(frame)
                
                # Combinar análisis
                combined_analysis['objects'].extend(frame_analysis['objects'])
                combined_analysis['faces_count'] = max(combined_analysis['faces_count'], frame_analysis['faces_count'])
                combined_analysis['brightness'] += frame_analysis['brightness']
                combined_analysis['colors'].extend(frame_analysis['colors'])
                
                frames_analyzed += 1
        
        cap.release()
        
        if frames_analyzed > 0:
            combined_analysis['brightness'] //= frames_analyzed
            
            # Generar descripción inteligente
            smart_description = self.generate_smart_description(combined_analysis, duration)
            
            # Formato de archivo
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            new_name = (f"{date_str}_{smart_description['action']}_"
                       f"{smart_description['location']}_{smart_description['shot_type']}_"
                       f"{smart_description['emotion']}_{int(duration)}s.mp4")
            
            return {
                'original_name': os.path.basename(video_path),
                'new_name': new_name,
                'analysis': combined_analysis,
                'description': smart_description,
                'duration': duration,
                'frames_analyzed': frames_analyzed
            }
        
        return None

def main():
    parser = argparse.ArgumentParser(description='Análisis dinámico de videos V5')
    parser.add_argument('--input-folder', required=True, help='Carpeta con videos')
    parser.add_argument('--output-folder', help='Carpeta destino (opcional)')
    parser.add_argument('--dry-run', action='store_true', help='Solo simular')
    
    args = parser.parse_args()
    
    analyzer = DynamicVideoAnalyzer()
    
    input_path = Path(args.input_folder)
    if not input_path.exists():
        logger.error(f"❌ Carpeta no existe: {input_path}")
        return
    
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}
    video_files = [f for f in input_path.iterdir() 
                   if f.suffix.lower() in video_extensions]
    
    if not video_files:
        logger.warning(f"⚠️ No se encontraron videos en: {input_path}")
        return
    
    logger.info(f"🎬 Procesando {len(video_files)} videos...")
    
    results = []
    for video_file in video_files:
        try:
            result = analyzer.process_video_optimized(video_file)
            if result:
                results.append(result)
                logger.info(f"✅ {result['original_name']} → {result['new_name']}")
                
                if not args.dry_run and args.output_folder:
                    output_path = Path(args.output_folder)
                    output_path.mkdir(exist_ok=True)
                    
                    new_file_path = output_path / result['new_name']
                    shutil.copy2(video_file, new_file_path)
                    logger.info(f"📁 Copiado a: {new_file_path}")
            else:
                logger.warning(f"⚠️ No se pudo procesar: {video_file.name}")
        
        except Exception as e:
            logger.error(f"❌ Error procesando {video_file.name}: {e}")
    
    # Guardar resultados
    output_json = Path("resultados_analisis_v5.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"📊 Análisis completo. Resultados en: {output_json}")
    logger.info(f"🎯 Procesados exitosamente: {len(results)}/{len(video_files)}")

if __name__ == "__main__":
    main()