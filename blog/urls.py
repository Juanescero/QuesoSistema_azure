from django.urls import path
from . import views

urlpatterns = [
    path('nosotros/', views.nosotros, name='nosotros'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('nuestros_quesos/', views.nuestros_quesos, name='nuestros_quesos'),
    path('nuestras_materias_prima/', views.nuestras_materias_prima, name='nuestras_materias_prima'),
    path('blog_informativo/', views.blog_informativo, name='blog_informativo'),
    path('blog1/', views.blog1, name='blog1'),
    path('blog2/', views.blog2, name='blog2'),
    path('blog3/', views.blog3, name='blog3'),
    path('blog4/', views.blog4, name='blog4'),
] 