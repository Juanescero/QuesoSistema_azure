from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Pedido
from django.contrib.auth.models import User, Group  # Asegúrate de importar el modelo de User y Group

class PedidoResource(resources.ModelResource):
    # Campo personalizado para el cliente que pertenece al grupo 'Clientes'
    cliente = fields.Field(
        column_name='cliente',
        attribute='cliente',
        widget=ForeignKeyWidget(User, 'email')  # Se asume que 'email' es el identificador del usuario
    )
    
    class Meta:
        model = Pedido
        fields = ('id', 'cliente', 'fecha_pedido', 'estado', 'subtotal')
        export_order = ('id', 'cliente', 'fecha_pedido', 'estado', 'subtotal')

    def dehydrate_cliente(self, pedido):
        """
        Personaliza la forma en que se muestra el cliente en la exportación.
        Asegúrate de que el cliente pertenece al grupo 'Clientes'.
        """
        cliente = pedido.cliente
        if cliente.groups.filter(name='Clientes').exists():
            return cliente.email  # Se muestra el email del cliente en la exportación
        return "Cliente no asignado"  # O cualquier otro texto en caso de error



