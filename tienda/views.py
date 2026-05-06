from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from decouple import config
from .models import Producto, Categoria, Carrito, ItemCarrito
from google import genai
import json
import re
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistroForm
from django.contrib.auth import login
from django.db.models import Q
from django.contrib.auth.decorators import login_required



#-Configguracion ia
# ── Cliente Gemini ──────────────────────────────────────────
client = genai.Client(api_key=config('GEMINI_API_KEY'))
MODELO = 'models/gemini-2.5-flash-lite'


# ── Función de recomendaciones ──────────────────────────────
def recomendar_con_gemini(producto_actual, lista_productos):
    stock_texto = "\n".join(
        f"ID: {p.id} - Nombre: {p.nombre}" for p in lista_productos
    )

    prompt = f"""
    Eres un vendedor simpático de una tienda veterinaria.
    Un cliente está viendo: "{producto_actual.nombre}" para su {producto_actual.especie}.

    De esta lista de productos, elige los 3 que mejor complementen lo que está viendo:
    {stock_texto}

    Responde SOLO en este formato JSON. Las razones deben ser cortas (máximo 15 palabras),
    naturales y en segunda persona, como si le hablaras directamente al dueño de la mascota.
    Ejemplos de buen tono: "Perfecto para complementar su dieta diaria", "Tu perro va a adorarlo"

    [
        {{"id": 1, "razon": "razón corta y natural aquí"}}
    ]
    """

    cuerpo = ''
    try:
        response = client.models.generate_content(
            model=MODELO,
            contents=prompt
        )
        cuerpo = re.sub(r'^```json\s*|\s*```$', '', response.text.strip())
        resultado = json.loads(cuerpo)

        if not isinstance(resultado, list):
            return []
        resultado = [r for r in resultado if 'id' in r and 'razon' in r]
        return resultado[:3]

    except Exception as e:
        print(f"DEBUG Gemini: {e}")
        print(f"DEBUG cuerpo recibido: {cuerpo}")
        return []


# ── Vista detalle producto ──────────────────────────────────
def detalle_producto(request, producto_id):
    from django.db.models import Q

    producto = get_object_or_404(Producto, id=producto_id)
    cache_key = f"rec_gemini_{producto_id}"

    recomendaciones_ia = request.session.get(cache_key)

    if not recomendaciones_ia:
        # Filtra por misma especie primero
        productos_candidatos = Producto.objects.filter(
            especie=producto.especie
        ).exclude(id=producto_id)

        # Si hay menos de 5, agrega universales
        if productos_candidatos.count() < 5:
            productos_candidatos = Producto.objects.filter(
                Q(especie=producto.especie) | Q(especie='universal')
            ).exclude(id=producto_id)

        recomendaciones_ia = recomendar_con_gemini(producto, productos_candidatos)
        request.session[cache_key] = recomendaciones_ia

    ids_rec = [r['id'] for r in recomendaciones_ia if 'id' in r]
    productos_recomendados = Producto.objects.filter(id__in=ids_rec)

    return render(request, 'html/detalle.html', {
        'producto':        producto,
        'recomendaciones': productos_recomendados,
        'explicaciones':   recomendaciones_ia,
    })

##Index

def index(request):
    especie = request.GET.get('especie', '')  # ?especie=perro
    productos = Producto.objects.all()
    if especie:
        productos = productos.filter(especie=especie)
    return render(request, 'html/index.html', {
        'productos': productos[:9],
        'especie_activa': especie,
    })

#Login

def redirigir_tras_login(request):
    if request.user.is_staff:
        return redirect('/admin/')   
    return redirect('/') 


#Registro
def registro(request):
    if request.user.is_authenticated:
        return redirect('index')
 
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            login(request, cliente)   # login automático tras registro
            return redirect('index')
    else:
        form = RegistroForm()
 
    return render(request, 'html/registro.html', {'form': form})


#Catalogo

def catalogo(request):
    productos  = Producto.objects.all()
    categorias = Categoria.objects.all()
 
    # Búsqueda por texto
    query = request.GET.get('q', '').strip()
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )
 
    # Filtro por especie
    especie_activa = request.GET.get('especie', '')
    if especie_activa:
        productos = productos.filter(especie=especie_activa)
 
    # Filtro por categoría
    categoria_activa = request.GET.get('categoria', '')
    if categoria_activa:
        productos = productos.filter(categoria__id=categoria_activa)
 
    # Ordenamiento
    orden = request.GET.get('orden', '')
    orden_map = {
        'precio_asc':  'precio',
        'precio_desc': '-precio',
        'nombre':      'nombre',
    }
    if orden in orden_map:
        productos = productos.order_by(orden_map[orden])
 
    return render(request, 'html/catalogo.html', {
        'productos':        productos,
        'categorias':       categorias,
        'query':            query,
        'especie_activa':   especie_activa,
        'categoria_activa': categoria_activa,
        'orden':            orden,
        'total_productos':  Producto.objects.count(),
    })


#Carrito
@login_required
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        import json as json_module
        data     = json_module.loads(request.body) if request.body else {}
        cantidad = int(data.get('cantidad', 1))

        producto = get_object_or_404(Producto, id=producto_id)
        carrito, _ = Carrito.objects.get_or_create(cliente=request.user)
        item, creado = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto
        )

        # ── Validar stock ──────────────────────────────
        cantidad_actual = 0 if creado else item.cantidad
        cantidad_posible = producto.stock - cantidad_actual

        if cantidad_posible <= 0:
            return JsonResponse({
                'ok':    False,
                'error': 'sin_stock',
                'msg':   f'No hay más stock disponible de {producto.nombre}',
            })

        # Si pide más de lo disponible, ajusta al máximo posible
        if cantidad > cantidad_posible:
            cantidad = cantidad_posible
            ajustado = True
        else:
            ajustado = False

        item.cantidad = cantidad_actual + cantidad
        item.save()

        return JsonResponse({
            'ok':             True,
            'ajustado':       ajustado,
            'cantidad_total': carrito.cantidad_total(),
            'total':          carrito.total(),
            'item_id':        item.id,
            'item_nombre':    producto.nombre,
            'item_precio':    producto.precio,
            'item_cantidad':  item.cantidad,
            'item_subtotal':  item.subtotal(),
            'item_imagen':    producto.imagen.url if producto.imagen else None,
            'item_stock':     producto.stock,
        })
    return JsonResponse({'ok': False}, status=400)
 
@login_required
def actualizar_item_carrito(request, item_id):
    if request.method == 'POST':
        import json as json_module
        data     = json_module.loads(request.body)
        cantidad = int(data.get('cantidad', 1))
        item     = get_object_or_404(ItemCarrito, id=item_id, carrito__cliente=request.user)
        if cantidad < 1:
            item.delete()
        else:
            item.cantidad = cantidad
            item.save()
        carrito = item.carrito if cantidad >= 1 else Carrito.objects.get(cliente=request.user)
        return JsonResponse({
            'ok': True,
            'subtotal': item.subtotal() if cantidad >= 1 else 0,
            'total': carrito.total(),
            'cantidad_total': carrito.cantidad_total(),
        })
    return JsonResponse({'ok': False}, status=400)
 
 
@login_required
def eliminar_item_carrito(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__cliente=request.user)
        carrito = item.carrito
        item.delete()
        return JsonResponse({
            'ok': True,
            'total': carrito.total(),
            'cantidad_total': carrito.cantidad_total(),
        })
    return JsonResponse({'ok': False}, status=400)