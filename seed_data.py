# seed_data.py
import random
from app import app, db
from models import Categoria, Producto

# Lista de categorías
categorias_nombres = [
    "Pijamas",
    "Lencería",
    "Remerones",
    "Pant Pajamas"
]

# Lista de URLs de imágenes (puedes cambiar por las que quieras)
imagenes_urls = [
    "https://www.gmkits.es/images/gmkits-6-250618/camiseta-ac-milan-segunda-2025-2026_gmkits-6-250618-165.jpg",
    "https://www.gmkits.es/images/gmkits-6-250618/camiseta-ac-milan-primera-2025-2026_gmkits-6-250618-15.jpg",
    "https://www.gmkits.es/images/gmkits-6-250618/camiseta-ac-milan-edicion-especial-camuflaje-naranja-2025-2026_gmkits-6-250618-183.jpg",
    "https://www.gmkits.es/images/gmkits-6-250618/camiseta-as-roma-primera-2024-2025_gmkits-6-250618-229.jpg",
    "https://www.gmkits.es/images/gmkits-6-250618/camiseta-as-roma-tercera-2024-2025_gmkits-6-250618-232.jpg",
    "https://www.gmkits.es/images/gmkits-6-250618/camiseta-sampdoria-tercera-2024-2025_gmkits-6-250618-798.jpg"
]

with app.app_context():
    # Eliminar datos previos
    Producto.query.delete()
    Categoria.query.delete()
    db.session.commit()

    # Crear categorías
    categorias = []
    for nombre in categorias_nombres:
        cat = Categoria(nombre=nombre)
        db.session.add(cat)
        categorias.append(cat)

    db.session.commit()

    # Crear productos
    for i in range(50):
        categoria = random.choice(categorias)
        producto = Producto(
            nombre=f"Producto {i+1}",
            precio=round(random.uniform(1500, 5000), 2),
            stock=random.randint(1, 20),
            color=random.choice(["Rojo", "Azul", "Verde", "Negro", "Blanco"]),
            descripcion=f"Descripción del producto {i+1}",
            # Asignar una categoría aleatoria
            categoria_id=categoria.id,
            imagen_url=random.choice(imagenes_urls)  # URL en vez de archivo local
        )
        db.session.add(producto)

    db.session.commit()
    print("✅ Datos de ejemplo insertados correctamente.")
