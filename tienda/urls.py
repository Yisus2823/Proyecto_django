from django.urls import path
from . import views

urlpatterns = [
    # El <int:producto_id> captura el número de la URL y lo pasa a la vista
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
]