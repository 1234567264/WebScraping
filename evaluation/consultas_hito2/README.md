# Prueba integrada común del Hito 2 (50 consultas)

Este directorio y `evaluation/consultas_hito2.csv` son la PRUEBA
INTEGRADA del Hito 2 (TRABAJO.md: 'Pruebas obligatorias para TODAS
las salas'). Cada consulta tiene previamente identificado el diseño
correcto (`id_correcto`).

## Estado generado por scripts/generar_consultas_prueba.py

| Categoría | Cantidad | Quién aporta | Estado |
|---|---|---|---|
| exacta | 10 | derivada del banco (images_final) | listo |
| sin_marco | 10 | derivada de Sala 1 (images_normalized) | listo |
| recoloreada | 10 | Sala 4 (conjunto de prueba) | pendiente |
| recortada | 10 | Sala 4 (conjunto de prueba) | pendiente |
| mockup_persona | 10 | Sala 2 (fotos reales) | pendiente |

## Cómo agregar las consultas pendientes

Añadir filas al CSV `evaluation/consultas_hito2.csv` con el mismo
formato (o reemplazar el archivo completo):

```
consulta,categoria,ruta_imagen,id_correcto
rec_01.png,recoloreada,evaluation/consultas_hito2/recoloreadas/rec_01.png,AIM-P001-001
```

Las imágenes pueden vivir en `evaluation/consultas_hito2/` (subcarpetas `recoloreadas/`, `recortadas/`, `mockups/`).
scripts/compare_hito1_hito2.py toma automáticamente todas las filas
cuyo archivo exista y omite las demás.
