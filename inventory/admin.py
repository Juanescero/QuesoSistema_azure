from django.contrib import admin
from .models import MateriaPrima, Producto, LoteProducto, MateriaPrimaLote

admin.site.register(MateriaPrima)
admin.site.register(Producto)
admin.site.register(LoteProducto)
admin.site.register(MateriaPrimaLote)

