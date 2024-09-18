from django import forms
from django.utils import timezone
from .models import MateriaPrima, EntradaMateriaPrima, Producto, LoteProducto

""" Formularios y validaciones Materia Prima """
class MateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = MateriaPrima
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Agregue un nombre'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Agregue la descripción'}),
        }

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        max_length = 100
        if len(descripcion) > max_length:
            raise forms.ValidationError(f"La descripción no puede exceder los {max_length} caracteres.")
        return descripcion
class EntradaMateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = EntradaMateriaPrima
        fields = ['proveedor', 'materia_prima', 'cantidad', 'fecha_vencimiento', 'costo_total']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'materia_prima': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la cantidad', 'min': '0', 'max': '1000', 'step': '1'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'costo_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el costo total', 'min': '0', 'max': '10000000', 'step': '1000'}),
        }

    def __init__(self, *args, **kwargs):
        super(EntradaMateriaPrimaForm, self).__init__(*args, **kwargs)
        self.fields['materia_prima'].queryset = MateriaPrima.objects.filter(descontinuado=False)

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return cantidad

    def clean_costo_total(self):
        costo_total = self.cleaned_data.get('costo_total')
        if costo_total is not None and costo_total <= 0.0:
            raise forms.ValidationError("El costo total debe ser mayor que cero.")
        return costo_total

    def clean_fecha_vencimiento(self):
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        fecha_actual = timezone.localtime(timezone.now()).date()  
        if fecha_vencimiento:
            if isinstance(fecha_vencimiento, timezone.datetime):
                fecha_vencimiento = fecha_vencimiento.date()

            if fecha_vencimiento <= fecha_actual:
                raise forms.ValidationError("La fecha de vencimiento debe ser mayor a la fecha actual.")
        
        return fecha_vencimiento

""" Formularios y validaciones Productos"""
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Agregue el nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Agregue la descripción', 'rows': 2}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el precio', 'min': '0', 'max': '100000', 'step': '1000'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que cero.")
        return precio
class LoteProductoForm(forms.ModelForm):
    class Meta:
        model = LoteProducto
        fields = ['producto', 'cantidad_producto', 'fecha_produccion', 'fecha_vencimiento']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_producto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la cantidad', 'min': '0', 'max': '1000', 'step': '1'}),
            'fecha_produccion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(LoteProductoForm, self).__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(descontinuado=False)

    def clean_cantidad_producto(self):
        cantidad_producto = self.cleaned_data.get('cantidad_producto')
        if cantidad_producto is not None and cantidad_producto <= 0:
            raise forms.ValidationError("La cantidad del lote debe ser mayor que cero.")
        return cantidad_producto

    def clean_fecha_produccion(self):
        fecha_produccion = self.cleaned_data.get('fecha_produccion')
        fecha_actual = timezone.localtime(timezone.now()).date()

        if fecha_produccion:
            if fecha_produccion < fecha_actual:
                raise forms.ValidationError("La fecha de producción no puede ser anterior a la fecha actual.")
        
        return fecha_produccion

    def clean_fecha_vencimiento(self):
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        fecha_produccion = self.cleaned_data.get('fecha_produccion')

        if fecha_vencimiento:
            if fecha_produccion and fecha_vencimiento <= fecha_produccion:
                raise forms.ValidationError("La fecha de vencimiento debe ser posterior a la fecha de producción.")
        
        return fecha_vencimiento

