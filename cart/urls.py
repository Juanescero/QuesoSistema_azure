
from django.urls import path

from cart.views import carrito, eliminar_producto, restar_producto, limpiar_carrito, agregar_al_carrito, procesar_pedido, mis_pedidos, cancelar_pedido, perfil_cliente, enviar_correo_pedido_admin, activar_notificaciones_pedido, enviar_correo_pedido_cliente, limpiar_notificacion_flag

urlpatterns = [
    path('cart/carrito/', carrito, name='carrito'),
    path('agregar/<int:producto_id>/', agregar_al_carrito, name='Add'),  # Mantén esta o la de abajo
    path('eliminar/<int:producto_id>/', eliminar_producto, name="Del"),
    path('restar/<int:producto_id>/', restar_producto, name="Sub"),
    path('limpiar/', limpiar_carrito, name="CLS"),
    path('procesar_pedido/', procesar_pedido, name='procesar_pedido'),
    path('activar_notificaciones/<uuid:pedido_id>/', activar_notificaciones_pedido, name='activar_notificaciones_pedido'),
    path('enviar_correo_pedido_cliente/', enviar_correo_pedido_cliente, name='enviar_correo_pedido_cliente'),
    path('enviar_correo_pedido_admin/', enviar_correo_pedido_admin, name='enviar_correo_pedido_admin'),
    path('limpiar_notificacion_flag/', limpiar_notificacion_flag, name='limpiar_notificacion_flag'),
    path('mis_pedidos/', mis_pedidos, name='mis_pedidos'),
    path('cancelar-pedido/<uuid:pedido_id>/', cancelar_pedido, name='cancelar_pedido'),
    path('perfil_cliente/', perfil_cliente, name='perfil_cliente'),
    ]


