from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DetallePedido, Pedido

@receiver(post_save, sender=DetallePedido)
def actualizar_subtotal_pedido(sender, instance, **kwargs):
    pedido = instance.pedido
    pedido.subtotal = sum(item.precio * item.cantidad for item in pedido.detalles.all())
    pedido.save()
