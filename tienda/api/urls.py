from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('login/',         TokenObtainPairView.as_view(),  name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(),     name='api_refresh'),
    path('perfil/',        views.perfil,                   name='api_perfil'),

    # Ventas
    path('ventas/',                        views.ventas_por_rol, name='api_ventas'),
    path('ventas/<int:venta_id>/aprobar/', views.aprobar_venta,  name='api_aprobar'),
    path('ventas/<int:venta_id>/tomar/',   views.tomar_venta,    name='api_tomar'),
    path('ventas/<int:venta_id>/entregar/',views.entregar_venta, name='api_entregar'),
]