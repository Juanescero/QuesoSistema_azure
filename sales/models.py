import uuid
from django.db import models
from inventory.models import Producto
from django.conf import settings
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='pedidos',
        limit_choices_to={'groups__name': 'Clientes'}, 
        verbose_name='Cliente'
    )
    notificaciones_activas = models.BooleanField(default=False, verbose_name='Notificaciones Activas')
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name='Fecha del pedido')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado del pedido')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal', default=0.00, editable=False)

    def __str__(self):
        return f"Pedido {self.id} - Estado: {self.get_estado_display()} - Subtotal: {self.subtotal}"

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        db_table = 'pedido'
        ordering = ['-fecha_pedido']


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Establece el precio basado en el precio del producto
        self.precio = self.producto.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Producto #{self.producto.id}"

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'
        db_table = 'detalle_pedido'
        ordering = ['pedido', 'producto']
