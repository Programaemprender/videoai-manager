#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Reprocesamiento Inteligente con Confirmación GPT-4V
Solo actualiza videos después de confirmar que la nueva categoría aplica
"""

import sys
import io
import json
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HISTORIAL_FILE = "historial_procesamiento.json"
PENDIENTES_FILE = "reprocesamiento_pendiente.json"

def load_historial():
    """Carga historial de videos procesados"""
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"videos": []}

def generar_reporte_reanalisis(tipo_categoria, categoria_vieja, categoria_nueva):
    """
    Genera reporte de videos que PODRÍAN actualizarse
    OpenClaw re-analizará frames para confirmar
    """
    print(f"\n{'='*60}")
    print(f"REPROCESAMIENTO INTELIGENTE - {tipo_categoria.upper()}")
    print(f"{'='*60}\n")
    print(f"Propuesta: '{categoria_vieja}' → '{categoria_nueva}'")
    print(f"Método: Re-análisis GPT-4V con confirmación\n")
    
    historial = load_historial()
    candidatos = []
    
    # Buscar videos con categoría vieja
    for video in historial["videos"]:
        analisis = video["analisis_gpt4v"]
        
        # Verificar si este video tenía la categoría vieja
        campo_revisar = None
        
        if tipo_categoria == "ubicacion" and analisis.get("ubicacion") == categoria_vieja:
            campo_revisar = "ubicacion"
        elif tipo_categoria == "accion" and analisis.get("accion") == categoria_vieja:
            campo_revisar = "accion"
        elif tipo_categoria == "emocion" and analisis.get("emocion") == categoria_vieja:
            campo_revisar = "emocion"
        
        if not campo_revisar:
            continue
        
        # Verificar frames disponibles
        frames_guardados = video.get("frames_analizados", [])
        frames_disponibles = [f for f in frames_guardados if os.path.exists(f)]
        
        if not frames_disponibles:
            print(f"⚠️ {video['original_name']}: Sin frames guardados (saltando)")
            continue
        
        candidatos.append({
            "video": video,
            "frames": frames_disponibles,
            "campo": campo_revisar
        })
    
    if not candidatos:
        print(f"\n✅ No hay videos con '{categoria_vieja}' que tengan frames guardados")
        print(f"   Nada que reprocesar\n")
        return
    
    print(f"\n📋 Videos candidatos para reprocesamiento: {len(candidatos)}\n")
    
    # Guardar reporte para OpenClaw
    reporte = {
        "tipo_categoria": tipo_categoria,
        "categoria_vieja": categoria_vieja,
        "categoria_nueva": categoria_nueva,
        "candidatos": [],
        "instrucciones": f"OpenClaw debe re-analizar frames con GPT-4V preguntando: '¿Esta {tipo_categoria} es {categoria_nueva}?' y confirmar antes de actualizar"
    }
    
    for i, candidato in enumerate(candidatos, 1):
        video = candidato["video"]
        
        print(f"{i}. {video['original_name']}")
        print(f"   Actual: {video['analisis_gpt4v'][candidato['campo']]}")
        print(f"   Propuesta: {categoria_nueva}")
        print(f"   Frames: {len(candidato['frames'])}")
        print()
        
        reporte["candidatos"].append({
            "video_id": video["file_id"],
            "original_name": video["original_name"],
            "final_name": video["final_name"],
            "frames": candidato["frames"],
            "categoria_actual": video['analisis_gpt4v'][candidato['campo']],
            "categoria_propuesta": categoria_nueva,
            "campo": candidato['campo']
        })
    
    # Guardar reporte
    with open(PENDIENTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"{'='*60}")
    print("SIGUIENTE PASO")
    print(f"{'='*60}\n")
    print(f"📄 Reporte guardado: {PENDIENTES_FILE}")
    print(f"🤖 OpenClaw debe ejecutar:")
    print(f"   python ejecutar_reanalisis_gpt4v.py")
    print(f"\n   Esto re-analizará {len(candidatos)} videos con GPT-4V")
    print(f"   y actualizará solo los que confirmen\n")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso:")
        print("  python reprocesar_con_confirmacion.py <tipo> <categoria_vieja> <categoria_nueva>")
        print()
        print("Ejemplo:")
        print("  python reprocesar_con_confirmacion.py ubicacion Otro Aeropuerto")
        sys.exit(1)
    
    tipo_categoria = sys.argv[1]
    categoria_vieja = sys.argv[2]
    categoria_nueva = sys.argv[3]
    
    generar_reporte_reanalisis(tipo_categoria, categoria_vieja, categoria_nueva)
