import os
import glob
import numpy as np
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "data", "images_final")
OUTPUT_NPY = os.path.join(BASE_DIR, "data", "embeddings_productos.npy")

MODEL_NAME = "openai/clip-vit-base-patch32"


def main():
    print(f"🤖 Cargando modelo CLIP: '{MODEL_NAME}'...")
    model = CLIPModel.from_pretrained(MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model.eval()

    # Buscar imágenes en data/images_final
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.gif")
    image_paths = []
    for ext in extensions:
        image_paths.extend(glob.glob(os.path.join(IMAGES_DIR, ext)))

    image_paths.sort()
    total = len(image_paths)
    print(f"📸 Procesando {total} imágenes desde '{IMAGES_DIR}'...\n")

    embeddings_dict = {}
    procesadas_con_exito = 0

    for idx, img_path in enumerate(image_paths, 1):
        filename = os.path.basename(img_path)
        try:
            # Cargar imagen y convertir a RGB
            image = Image.open(img_path).convert("RGB")
            inputs = processor(images=image, return_tensors="pt")

            with torch.no_grad():
                # Extraer características visuales
                features = model.get_image_features(**inputs)

                # CORRECCIÓN AQUÍ: Asegurar que extraemos el Tensor si viene encapsulado
                if hasattr(features, "image_embeds"):
                    features = features.image_embeds
                elif hasattr(features, "pooler_output"):
                    features = features.pooler_output

                # Normalización L2 para similitud de coseno
                features = features / features.norm(p=2, dim=-1, keepdim=True)

                # Convertir Tensor a Numpy array unidimensional
                embedding = features.cpu().numpy().flatten()

            embeddings_dict[filename] = embedding
            procesadas_con_exito += 1
            print(f"[{idx}/{total}] ✅ {filename} procesado correctamente")

        except Exception as e:
            print(f"[{idx}/{total}] ⚠️ Error procesando {filename}: {e}")

    # Crear carpeta data/ si no existe y guardar resultado
    os.makedirs(os.path.dirname(OUTPUT_NPY), exist_ok=True)
    np.save(OUTPUT_NPY, embeddings_dict)

    print("\n" + "=" * 50)
    print("🎉 ¡TRABAJO DE LA SALA 4 COMPLETADO!")
    print(f"📦 Archivo generado: {OUTPUT_NPY}")
    print(f"📊 Total vectores procesados: {procesadas_con_exito}")
    print("=" * 50)


if __name__ == "__main__":
    main()