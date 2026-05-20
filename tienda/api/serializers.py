from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from tienda.models import Venta, DetalleVenta, Producto, Cliente

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Producto
        fields = ['id', 'nombre', 'precio', 'stock', 'especie', 'imagen']

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model  = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(source='detalleventa_set', many=True)
    cliente  = serializers.StringRelatedField()

    class Meta:
        model  = Venta
        fields = [
            'id', 'cliente', 'fecha', 'total',
            'estado', 'detalles',
            'fecha_despacho', 'fecha_entrega',
        ]

def get_rol(user):
    if hasattr(user, 'vendedor'):        return 'vendedor'
    elif hasattr(user, 'transportador'): return 'transportador'
    return 'cliente'

class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['rol']      = get_rol(self.user)
        data['username'] = self.user.username
        return data