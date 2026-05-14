from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from tienda.models import Venta, Producto
from .serializers import VentaSerializer


def get_rol(user):
    if hasattr(user, 'vendedor'):
        return 'vendedor'
    elif hasattr(user, 'transportador'):
        return 'transportador'
    return 'cliente'


# ── Login info + rol ──────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil(request):
    return Response({
        'id':       request.user.id,
        'username': request.user.username,
        'email':    request.user.email,
        'rol':      get_rol(request.user),
    })


# ── Ventas según rol ──────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ventas_por_rol(request):
    user = request.user
    rol  = get_rol(user)

    if rol == 'vendedor':
        # Vendedor ve pendientes y todas las demás excepto fallido/cancelado
        ventas = Venta.objects.filter(
            estado__in=['pendiente', 'aprobado', 'pagado', 'en_despacho', 'entregado']
        ).select_related('cliente').prefetch_related('detalleventa_set__producto')

    elif rol == 'transportador':
        # Transportador solo ve aprobado y pagado
        ventas = Venta.objects.filter(
            estado__in=['aprobado', 'pagado']
        ).select_related('cliente').prefetch_related('detalleventa_set__producto')

    else:
        # Cliente solo ve sus propias ventas
        ventas = Venta.objects.filter(
            cliente=user
        ).select_related('cliente').prefetch_related('detalleventa_set__producto')

    serializer = VentaSerializer(ventas, many=True)
    return Response(serializer.data)


# ── Vendedor aprueba una venta (pendiente → aprobado) ──
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aprobar_venta(request, venta_id):
    if not hasattr(request.user, 'vendedor'):
        return Response({'error': 'Sin permiso'}, status=status.HTTP_403_FORBIDDEN)

    try:
        venta = Venta.objects.get(id=venta_id, estado='pendiente')
    except Venta.DoesNotExist:
        return Response({'error': 'Venta no encontrada o no está pendiente'}, status=404)

    # Descontar stock al aprobar
    from django.db import transaction
    with transaction.atomic():
        for detalle in venta.detalleventa_set.select_related('producto').all():
            producto = detalle.producto
            if producto.stock < detalle.cantidad:
                return Response(
                    {'error': f'Stock insuficiente para {producto.nombre}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            producto.stock -= detalle.cantidad
            producto.save()

        venta.estado   = 'aprobado'
        venta.vendedor = request.user.vendedor
        venta.save()

    return Response(VentaSerializer(venta).data)


# ── Transportador toma una venta (aprobado/pagado → en_despacho) ──
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tomar_venta(request, venta_id):
    if not hasattr(request.user, 'transportador'):
        return Response({'error': 'Sin permiso'}, status=status.HTTP_403_FORBIDDEN)

    try:
        venta = Venta.objects.get(id=venta_id, estado__in=['aprobado', 'pagado'])
    except Venta.DoesNotExist:
        return Response({'error': 'Venta no disponible'}, status=404)

    venta.estado         = 'en_despacho'
    venta.transportador  = request.user.transportador
    venta.fecha_despacho = timezone.now()
    venta.save()

    return Response(VentaSerializer(venta).data)


# ── Transportador marca entregado ──
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def entregar_venta(request, venta_id):
    if not hasattr(request.user, 'transportador'):
        return Response({'error': 'Sin permiso'}, status=status.HTTP_403_FORBIDDEN)

    try:
        venta = Venta.objects.get(
            id=venta_id,
            estado='en_despacho',
            transportador=request.user.transportador
        )
    except Venta.DoesNotExist:
        return Response({'error': 'Venta no encontrada'}, status=404)

    venta.estado        = 'entregado'
    venta.fecha_entrega = timezone.now()
    venta.save()

    return Response(VentaSerializer(venta).data)