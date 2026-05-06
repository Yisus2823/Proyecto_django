
from .models import Carrito
 
def carrito_context(request):
    if request.user.is_authenticated:
        carrito, _ = Carrito.objects.get_or_create(cliente=request.user)
        return {
            'carrito': carrito,
            'carrito_cantidad': carrito.cantidad_total(),
            'carrito_items': carrito.items.select_related('producto').all(),
        }
    return {
        'carrito': None,
        'carrito_cantidad': 0,
        'carrito_items': [],
    }
 
