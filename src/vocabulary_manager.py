#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de Vocabulario Controlado
Maneja aprobación/rechazo de nuevas categorías
"""

import sys
import io
import json
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CANDIDATOS_FILE = "vocabulario_candidatos.json"
VOCABULARIO_OFICIAL = {
    "ubicaciones": [
        "Casa", "Oficina", "Gym", "Parque", "Playa", 
        "Calle_Santiago", "Restaurante", "Ciclismo"
    ],
    "acciones": [
        "Caminar", "Correr", "Comer", "Trabajar", "Entrenar",
        "Cocinar", "Hablar", "Conducir", "Nadar"
    ],
    "emociones": [
        "Calma", "Energia", "Esfuerzo", "Logro", 
        "Concentracion", "Alegria", "Sorpresa"
    ]
}

def load_candidatos():
    """Carga candidatos"""
    if os.path.exists(CANDIDATOS_FILE):
        with open(CANDIDATOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"ubicaciones": {}, "acciones": {}, "emociones": {}}

def save_candidatos(candidatos):
    """Guarda candidatos"""
    with open(CANDIDATOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(candidatos, f, indent=2, ensure_ascii=False)

def normalizar_categoria(categoria_propuesta, tipo):
    """
    Normaliza categoría propuesta al vocabulario oficial
    Si no existe → registra como candidato
    Retorna categoría normalizada
    """
    # Verificar si está en vocabulario oficial
    if categoria_propuesta in VOCABULARIO_OFICIAL[tipo]:
        return categoria_propuesta
    
    # Verificar si es sinónimo conocido
    sinonimos = {
        "ubicaciones": {
            "Hogar": "Casa",
            "Exterior": "Parque",
            "Calle": "Calle_Santiago",
            "Ciudad": "Calle_Santiago",
            "Mar": "Playa",
            "Costa": "Playa",
            "Trabajo": "Oficina",
            "Gimnasio": "Gym",
            "Comida": "Restaurante",
            "Bicicleta": "Ciclismo",
            "Ruta": "Ciclismo"
        },
        "acciones": {
            "Trotar": "Correr",
            "Ejercitar": "Entrenar",
            "Conversar": "Hablar",
            "Dialogar": "Hablar",
            "Preparar_Comida": "Cocinar",
            "Manejar": "Conducir",
            "Caminata": "Caminar"
        },
        "emociones": {
            "Tranquilo": "Calma",
            "Relajado": "Calma",
            "Feliz": "Alegria",
            "Contento": "Alegria",
            "Enfocado": "Concentracion",
            "Intenso": "Esfuerzo",
            "Desafio": "Esfuerzo",
            "Activo": "Energia",
            "Animado": "Energia"
        }
    }
    
    if categoria_propuesta in sinonimos.get(tipo, {}):
        return sinonimos[tipo][categoria_propuesta]
    
    # No está en vocabulario → registrar como candidato
    registrar_candidato(categoria_propuesta, tipo, "video_actual.mp4")
    
    # Por ahora, mapear a "Otro" o categoría genérica
    return "Otro"

def registrar_candidato(categoria, tipo, video_name):
    """Registra nueva categoría candidata"""
    candidatos = load_candidatos()
    
    if categoria not in candidatos[tipo]:
        candidatos[tipo][categoria] = {
            "apariciones": 1,
            "videos": [video_name],
            "fecha_primera_aparicion": datetime.now().isoformat(),
            "propuesto_por": "gpt4v"
        }
        print(f"  🆕 Nueva categoría candidata: {tipo}/{categoria}")
    else:
        if video_name not in candidatos[tipo][categoria]["videos"]:
            candidatos[tipo][categoria]["videos"].append(video_name)
            candidatos[tipo][categoria]["apariciones"] += 1
            print(f"  ⬆️  Candidato actualizado: {tipo}/{categoria} (apariciones: {candidatos[tipo][categoria]['apariciones']})")
    
    save_candidatos(candidatos)

def revisar_candidatos_pendientes():
    """
    Revisa candidatos que tienen 3+ apariciones
    Retorna lista de candidatos listos para aprobación
    """
    candidatos = load_candidatos()
    pendientes = []
    
    for tipo in ["ubicaciones", "acciones", "emociones"]:
        for categoria, data in candidatos[tipo].items():
            if data["apariciones"] >= 3:
                pendientes.append({
                    "tipo": tipo,
                    "categoria": categoria,
                    "apariciones": data["apariciones"],
                    "videos": data["videos"]
                })
    
    return pendientes

def aprobar_candidato(tipo, categoria):
    """Aprueba candidato y lo mueve a vocabulario oficial"""
    candidatos = load_candidatos()
    
    if categoria in candidatos[tipo]:
        print(f"✅ Categoría '{categoria}' aprobada en {tipo}")
        print(f"   Agregar manualmente a VOCABULARIO_CONTROLADO.md")
        
        # Marcar como aprobado (para no volver a notificar)
        candidatos[tipo][categoria]["aprobado"] = True
        save_candidatos(candidatos)
        return True
    
    return False

def rechazar_candidato(tipo, categoria, consolidar_con=None):
    """Rechaza candidato y opcionalmente lo consolida con otra categoría"""
    candidatos = load_candidatos()
    
    if categoria in candidatos[tipo]:
        if consolidar_con:
            print(f"❌ Categoría '{categoria}' rechazada. Consolidar con: {consolidar_con}")
            # Agregar a sinonimos (esto debería ir en el código principal)
        else:
            print(f"❌ Categoría '{categoria}' rechazada permanentemente")
        
        del candidatos[tipo][categoria]
        save_candidatos(candidatos)
        return True
    
    return False

def listar_candidatos():
    """Lista todos los candidatos actuales"""
    candidatos = load_candidatos()
    
    print(f"\n{'='*60}")
    print("CANDIDATOS DE VOCABULARIO")
    print(f"{'='*60}\n")
    
    for tipo in ["ubicaciones", "acciones", "emociones"]:
        if candidatos[tipo]:
            print(f"\n📋 {tipo.upper()}:")
            for categoria, data in candidatos[tipo].items():
                aprobado = " [APROBADO]" if data.get("aprobado") else ""
                print(f"  • {categoria}{aprobado}")
                print(f"    Apariciones: {data['apariciones']} ({len(data['videos'])} videos)")
                if data['apariciones'] >= 3 and not data.get("aprobado"):
                    print(f"    🔔 LISTO PARA REVISIÓN")
        else:
            print(f"\n📋 {tipo.upper()}: (ninguno)")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  Listar candidatos:")
        print("    python vocabulario_manager.py list")
        print()
        print("  Aprobar candidato:")
        print("    python vocabulario_manager.py approve <tipo> <categoria>")
        print()
        print("  Rechazar candidato:")
        print("    python vocabulario_manager.py reject <tipo> <categoria> [consolidar_con]")
        print()
        print("Ejemplo:")
        print("    python vocabulario_manager.py list")
        print("    python vocabulario_manager.py approve ubicaciones Aeropuerto")
        print("    python vocabulario_manager.py reject acciones Saltar Entrenar")
        sys.exit(1)
    
    accion = sys.argv[1]
    
    if accion == "list":
        listar_candidatos()
    elif accion == "approve" and len(sys.argv) >= 4:
        tipo = sys.argv[2]
        categoria = sys.argv[3]
        aprobar_candidato(tipo, categoria)
    elif accion == "reject" and len(sys.argv) >= 4:
        tipo = sys.argv[2]
        categoria = sys.argv[3]
        consolidar_con = sys.argv[4] if len(sys.argv) > 4 else None
        rechazar_candidato(tipo, categoria, consolidar_con)
    else:
        print("❌ Argumentos inválidos")
        sys.exit(1)
