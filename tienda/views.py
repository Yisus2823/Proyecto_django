from django.shortcuts import render, get_object_or_404
from .models import Producto
from ia.gemmini_recomender import recomendar_con_gemini

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Creamos una "llave" única para este producto en el caché
    cache_key = f"rec_gemini_{producto_id}"
    
    # Intentamos obtener las recomendaciones de la sesión (caché)
    recomendaciones_ia = request.session.get(cache_key)

    if not recomendaciones_ia:
        # Si no están en caché, llamamos a Gemini
        productos_categoria = Producto.objects.filter(
            categoria=producto.categoria
        ).exclude(id=producto_id)
        
        recomendaciones_ia = recomendar_con_gemini(producto, productos_categoria)
        
        # Guardamos en la sesión para la próxima vez (expira al cerrar navegador o según settings)
        request.session[cache_key] = recomendaciones_ia
    
    # Obtenemos los objetos reales de la DB usando los IDs del JSON
    ids_rec = [r['id'] for r in recomendaciones_ia]
    productos_recomendados = Producto.objects.filter(id__in=ids_rec)

    return render(request, 'html/detalle.html', {
        'producto': producto,
        'recomendaciones': productos_recomendados,
        'explicaciones': recomendaciones_ia 
    })