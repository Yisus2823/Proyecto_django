from django.contrib import admin
from .models import Categoria, Producto, Cliente, Venta, DetalleVenta

# Esto permite editar el DetalleVenta dentro de la misma vista de la Venta
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1 # Muestra una línea vacía para agregar un producto

class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total') # Columnas a mostrar en la lista
    inlines = [DetalleVentaInline] # Incluye el detalle dentro de la venta

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria') # Columnas a mostrar
    list_filter = ('categoria',) # Filtro por categoría a la derecha
    search_fields = ('nombre',) # Buscador por nombre

admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin) # Usamos ProductoAdmin para personalizar
admin.site.register(Cliente)
admin.site.register(Venta, VentaAdmin) # Usamos VentaAdmin para personalizar