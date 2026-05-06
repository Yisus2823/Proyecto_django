from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('redirigir/', views.redirigir_tras_login, name='redirigir_tras_login'),
    path('registro/', views.registro, name='registro'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'), # El <int:producto_id> captura el número de la URL y lo pasa a la vista,
    path('carrito/agregar/<int:producto_id>/',      views.agregar_al_carrito,      name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/',       views.actualizar_item_carrito, name='actualizar_item_carrito'),
    path('carrito/eliminar/<int:item_id>/',         views.eliminar_item_carrito,   name='eliminar_item_carrito'),
]