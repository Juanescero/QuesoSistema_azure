from django.urls import path
from . import views

urlpatterns = [
    path('productos', views.productos, name='productos'),
    path('descontinuar_producto/<int:producto_id>/', views.descontinuar_producto, name='descontinuar_producto'),
    path('descontinuar_materia/<int:materia_id>/', views.descontinuar_materia, name='descontinuar_materia'), 
    path('materia_prima/', views.materiaPrima, name='materia_prima'),
    path('alertas/', views.mostrar_alertas, name='alertas'),
]

