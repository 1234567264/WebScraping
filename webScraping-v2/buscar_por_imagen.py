import sys
import os
import numpy as np
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "data", "embeddings_productos.npy")
MODEL_NAME = "openai/clip-vit-base-patch32"

def buscar_similares(image_path, top_k=5):
    if not os.path.exists(EMBEDDINGS_FILE):
        print(f"\n❌ Error: No se encontró el archivo de vectores: {EMBEDDINGS_FILE}")
        print("💡 Ejecuta primero: python generar_embeddings.py\n")
        return

    if not os.path.exists(image_path):
        print(f"\n❌ Error: La imagen especificada no existe: {image_path}\n")
        return

    # 1. Cargar el diccionario de embeddings guardado
    data = np.load(EMBEDDINGS_FILE, allow_pickle=True).item()
    
    # 2. Cargar modelo CLIP
    print("🤖 Cargando modelo CLIP para la consulta...")
    model = CLIPModel.from_pretrained(MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model.eval()

    # 3. Generar el embedding de la imagen de prueba
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        # Usamos get_image_features directamente para obtener el tensor correcto
        features = model.get_image_features(**inputs)
        
        # Si devuelve un objeto estructurado, extraemos el tensor de embeddings
        if hasattr(features, 'image_embeds'):
            features = features.image_embeds
        elif hasattr(features, 'pooler_output'):
            features = features.pooler_output

        # Normalizar vector de consulta
        query_vector = (features / features.norm(p=2, dim=-1, keepdim=True)).cpu().numpy().flatten()

    # 4. Calcular similitud coseno con todas las imágenes
    resultados = []
    for filename, embedding in data.items():
        # Normalizar el embedding guardado por seguridad
        emb_norm = embedding / np.linalg.norm(embedding)
        similarity = np.dot(query_vector, emb_norm)
        resultados.append((filename, similarity))

    # Ordenar de mayor a menor similitud
    resultados.sort(key=lambda x: x[1], reverse=True)

    # 5. Mostrar TOP K
    print(f"\n--- 🎯 TOP {top_k} RESULTADOS VISUALES ---")
    for rank, (filename, sim) in enumerate(resultados[:top_k], 1):
        porcentaje = max(0.0, sim) * 100
        # Extraer solo el nombre base del archivo para mayor claridad
        nombre_limpio = os.path.basename(filename)
        print(f"{rank}. {nombre_limpio} | Similitud: {porcentaje:.2f}%")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python buscar_por_imagen.py <ruta_de_la_imagen>")
    else:
        ruta_img = sys.argv[1]
        print(f"🔍 Buscando los 5 productos más parecidos a '{ruta_img}'...")
        buscar_similares(ruta_img, top_k=5)