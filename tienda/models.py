from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):

    ESPECIE_CHOICES = [
        ('perro',    '🐶 Perro'),
        ('gato',     '🐱 Gato'),
        ('ave',      '🐦 Ave'),
        ('pez',      '🐠 Pez'),
        ('roedor',   '🐹 Roedor'),
        ('universal','🐾 Universal'),
    ]

    nombre      = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200)
    precio      = models.IntegerField()
    stock       = models.IntegerField(default=0)
    categoria   = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen      = models.ImageField(upload_to='productos/', null=True, blank=True)
    especie     = models.CharField(          # ← nuevo campo
        max_length=20,
        choices=ESPECIE_CHOICES,
        default='universal'
    )

    def __str__(self):
        return self.nombre

class Cliente(AbstractUser):
    direccion = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.username

class Venta(models.Model):
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE
    )
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField()

    def __str__(self):
        return f"Venta {self.id} - {self.cliente.username}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.IntegerField() 

class Carrito(models.Model):
    cliente = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.cliente.username}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def cantidad_total(self):
        return sum(item.cantidad for item in self.items.all())


class ItemCarrito(models.Model):
    carrito  = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    def subtotal(self):
        return self.producto.precio * self.cantidad
