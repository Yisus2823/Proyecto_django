from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decouple import config
from .models import Producto, Categoria, Carrito, ItemCarrito, Venta, DetalleVenta
from google import genai
from .forms import RegistroForm
import paypalrestsdk
import json
import re
import requests as http_requests


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

# ── Configuración PayPal (se ejecuta una vez al cargar el módulo) ──
paypalrestsdk.configure({
    'mode':       config('PAYPAL_MODE', default='sandbox'),
    'client_id':  config('PAYPAL_CLIENT_ID'),
    'client_secret': config('PAYPAL_CLIENT_SECRET'),
})
 
 
# ════════════════════════════════════
#   CHECKOUT — Página principal
# ════════════════════════════════════
@login_required
def checkout(request):
    """
    Muestra la página de checkout con el resumen del carrito
    y los métodos de pago disponibles.
    Redirige al catálogo si el carrito está vacío.
    """
    try:
        carrito = request.user.carrito
        items   = carrito.items.select_related('producto').all()
    except Carrito.DoesNotExist:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('catalogo')
 
    if not items.exists():
        messages.warning(request, 'Agrega productos antes de continuar.')
        return redirect('catalogo')
 
    return render(request, 'html/checkout.html', {
        'carrito':       carrito,
        'carrito_items': items,
    })
 

##Aqui esta la conversion de clps a usd 
def _clp_a_usd(monto_clp):
    try:
        api_key = config('EXCHANGERATE_API_KEY')
        response = http_requests.get(
            f'https://v6.exchangerate-api.com/v6/{api_key}/pair/CLP/USD',
            timeout=5,
        )
        response.raise_for_status()
        tasa = response.json()['conversion_rate']
        return round(monto_clp * tasa, 2)

    except Exception as e:
        print(">>> ERROR CONVERSIÓN:", e)
        # Tasa de fallback para desarrollo
        TASA_FALLBACK = 0.00105
        return round(monto_clp * TASA_FALLBACK, 2)
 
 
# ════════════════════════════════════
#   PAGO CON PAYPAL — Iniciar (con conversión CLP → USD)
# ════════════════════════════════════
@login_required
def pago_paypal(request):
    """
    Convierte el total de CLP a USD y crea el pago en PayPal.
    El usuario ve los precios en CLP en todo el sitio;
    PayPal recibe y cobra en USD internamente.
    """

    if request.method != 'POST':
        return redirect('checkout')
 
    try:
        carrito = request.user.carrito
        items   = carrito.items.select_related('producto').all()
    except Carrito.DoesNotExist:
        return redirect('checkout')
 
    if not items.exists():
        return redirect('checkout')
 
    # Convertir total CLP → USD
    try:
        total_usd = _clp_a_usd(carrito.total())
    except ValueError as e:
        print(">>> ERROR CONVERSIÓN:", e)
        messages.error(request, str(e))
        return redirect('checkout')
    
 
    # Construir ítems para PayPal
    # Nota: PayPal requiere que la suma de (precio * qty) sea igual al total.
    # Como la conversión puede generar decimales imprecisos por ítem,
    # enviamos un solo ítem con el total consolidado — práctica estándar.
    item_list = [{
        'name':     f'Compra VetShop ({items.count()} producto/s)',
        'sku':      'pedido-vetshop',
        'price':    f'{total_usd:.2f}',
        'currency': 'USD',
        'quantity': 1,
    }]
 
    payment = paypalrestsdk.Payment({
        'intent': 'sale',
        'payer': {
            'payment_method': 'paypal',
        },
        'redirect_urls': {
            'return_url': request.build_absolute_uri('/pago/paypal/exitoso/'),
            'cancel_url': request.build_absolute_uri('/pago/paypal/cancelado/'),
        },
        'transactions': [{
            'item_list': {'items': item_list},
            'amount': {
                'total':    f'{total_usd:.2f}',
                'currency': 'USD',
            },
            'description': (
                f'VetShop — pedido de {request.user.username} '
                f'(${carrito.total():,} CLP)'   # referencia en CLP en la descripción
            ),
        }],
    })
 
    if payment.create():
        request.session['paypal_payment_id'] = payment.id

        for link in payment.links:
            if link.rel == 'approval_url':
                # En vez de redirect directo, devolvemos la URL al JS
                return JsonResponse({'redirect_url': str(link.href)})
    else:
        print("ERROR PAYPAL:", payment.error)
        return JsonResponse({'error': str(payment.error)}, status=400)
 
 
# ════════════════════════════════════
#   PAGO CON PAYPAL — Retorno exitoso
# ════════════════════════════════════
@login_required
def pago_paypal_exitoso(request):
    """
    PayPal redirige aquí tras la aprobación del usuario.
    Ejecuta el pago, crea la Venta y vacía el carrito.
    """
    payment_id = request.GET.get('paymentId') or request.session.get('paypal_payment_id')
    payer_id   = request.GET.get('PayerID')
 
    if not payment_id or not payer_id:
        messages.error(request, 'No se pudo verificar el pago. Contacta soporte.')
        return redirect('checkout')
 
    payment = paypalrestsdk.Payment.find(payment_id)
 
    if payment.execute({'payer_id': payer_id}):
        # Pago aprobado — registrar en BD de forma atómica
        try:
            with transaction.atomic():
                venta = _crear_venta(request.user, estado='pagado')
 
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('checkout')
 
        # Limpiar sesión
        request.session.pop('paypal_payment_id', None)
 
        messages.success(request, '¡Pago realizado con éxito! 🎉')
        return render(request, 'html/pago_exitoso.html', {'venta': venta})
    else:
        messages.error(request, 'El pago no pudo completarse. Intenta de nuevo.')
        return redirect('checkout')
 
 
# ════════════════════════════════════
#   PAGO CON PAYPAL — Cancelado
# ════════════════════════════════════
@login_required
def pago_paypal_cancelado(request):
    """
    PayPal redirige aquí si el usuario cancela el pago.
    El carrito se mantiene intacto.
    """
    request.session.pop('paypal_payment_id', None)
    messages.warning(request, 'Cancelaste el pago. Tu carrito sigue guardado.')
    return redirect('checkout')
 
 
# ════════════════════════════════════
#   PAGO POR TRANSFERENCIA
# ════════════════════════════════════
@login_required
def pago_transferencia(request):
    """
    Registra el pedido con estado 'pendiente'.
    El carrito se vacía y se espera confirmación manual del pago.
    """
    if request.method != 'POST':
        return redirect('checkout')
 
    try:
        with transaction.atomic():
            venta = _crear_venta(request.user, estado='pendiente')
 
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('checkout')
 
    messages.success(
        request,
        'Pedido registrado. En cuanto confirmemos tu transferencia, lo procesamos. 🐾'
    )
    return render(request, 'html/pago_exitoso.html', {'venta': venta})
 
 
# ════════════════════════════════════
#   HELPER — Crear Venta (uso interno)
# ════════════════════════════════════
def _crear_venta(user, estado):
    """
    Función interna compartida entre PayPal y Transferencia.
    - Valida stock en el momento del pago
    - Crea Venta + DetalleVenta
    - Descuenta stock de cada Producto
    - Vacía el carrito del usuario
    Lanza ValueError si hay problema de stock.
    """
    carrito = user.carrito
    items   = carrito.items.select_related('producto').all()
 
    if not items.exists():
        raise ValueError('El carrito está vacío.')
 
    # Validar stock antes de procesar
    for item in items:
        producto = Producto.objects.select_for_update().get(pk=item.producto.pk)
        if producto.stock < item.cantidad:
            raise ValueError(
                f'Stock insuficiente para "{producto.nombre}". '
                f'Solo quedan {producto.stock} unidades.'
            )
 
    # Crear la venta
    venta = Venta.objects.create(
        cliente = user,
        total   = carrito.total(),
        estado  = estado,
    )
 
    # Crear detalles y descontar stock
    for item in items:
        producto = Producto.objects.select_for_update().get(pk=item.producto.pk)
 
        DetalleVenta.objects.create(
            venta           = venta,
            producto        = producto,
            cantidad        = item.cantidad,
            precio_unitario = producto.precio,
        )
 
        producto.stock -= item.cantidad
        producto.save()
 
    # Vaciar el carrito
    items.delete()
 
    return venta