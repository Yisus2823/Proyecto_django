from rest_framework import serializers
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