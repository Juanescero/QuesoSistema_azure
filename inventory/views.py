from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from users.views import group_required
from django.contrib import messages
from .models import Producto, LoteProducto, MateriaPrimaLote, MateriaPrima, EntradaMateriaPrima
from .forms import MateriaPrimaForm, EntradaMateriaPrimaForm, LoteProductoForm, ProductoForm

""" Productos """

@group_required('Empleados')
def productos(request):
    productos = Producto.objects.all()
    lotes_producto = LoteProducto.objects.all()
    producto_form = ProductoForm()  # Para el modal de agregar
    lote_form = LoteProductoForm()

    # Crear un diccionario con formularios prellenados para cada producto
    producto_forms = {producto.id: ProductoForm(instance=producto) for producto in productos}

    if request.method == "POST":
        form_type = request.POST.get('form_type')

        if form_type == 'producto':
            producto_form = ProductoForm(request.POST, request.FILES)
            if producto_form.is_valid():
                producto_form.save()
                messages.success(request, "Producto agregado exitosamente.")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': producto_form.errors})

        elif form_type == 'lote_producto':
            lote_form = LoteProductoForm(request.POST)
            if lote_form.is_valid():
                lote = lote_form.save()
                producto = lote.producto
                producto.stock += lote.cantidad_producto
                producto.save()

                messages.success(request, "Lote de producto registrado exitosamente.")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': lote_form.errors})

        elif form_type == 'editar_producto':
            producto_id = request.POST.get('producto_id')
            producto = Producto.objects.get(id=producto_id)
            producto_form = ProductoForm(request.POST, request.FILES, instance=producto)
            if producto_form.is_valid():
                producto_form.save()
                messages.success(request, "Producto editado exitosamente.")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': producto_form.errors})

    return render(request, 'inventory/productos.html', {
        'productos': productos,
        'lotes_producto': lotes_producto,
        'producto_form': producto_form,  # Para el modal de agregar
        'producto_forms': producto_forms,  # Diccionario de formularios de edición
        'lote_form': lote_form,
    })

@group_required('Empleados')
def descontinuar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.descontinuado = True
    producto.save()
    messages.success(request, f"El producto {producto.nombre} ha sido descontinuado.")
    return redirect('productos')

""" Materias Primas """

@group_required('Empleados')
def materiaPrima(request):
    materias_primas = MateriaPrima.objects.all()
    entrada_materia_prima = EntradaMateriaPrima.objects.all()
    materia_form = MateriaPrimaForm()
    entrada_form = EntradaMateriaPrimaForm()

    if request.method == "POST":
        form_type = request.POST.get('form_type')

        if form_type == 'materia_prima':
            materia_form = MateriaPrimaForm(request.POST)
            if materia_form.is_valid():
                materia_form.save()
                messages.success(request, "Materia prima agregada exitosamente.")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': materia_form.errors})

        elif form_type == 'entrada_materia_prima':
            entrada_form = EntradaMateriaPrimaForm(request.POST)
            if entrada_form.is_valid():
                entrada = entrada_form.save()
                    
                # Actualizar la cantidad disponible de la materia prima
                materia_prima = entrada.materia_prima
                materia_prima.stock += entrada.cantidad
                materia_prima.save()

                messages.success(request, "Entrada de materia prima registrada exitosamente.")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': entrada_form.errors})

    return render(request, 'inventory/materiaPrima.html', {
        'materias_primas': materias_primas,
        'entrada_materia_prima': entrada_materia_prima,
        'materia_form': materia_form,
        'entrada_form': entrada_form,
    })

@group_required('Empleados')
def descontinuar_materia(request, materia_id):
    materia = get_object_or_404(MateriaPrima, id=materia_id)
    materia.descontinuado = True
    materia.save()
    messages.success(request, f"El materia {materia.nombre} ha sido descontinuado.")
    return redirect('materia_prima')

""" Alertas """

@group_required('Empleados')
def mostrar_alertas(request):
    productos_bajo_stock = Producto.objects.filter(stock__lt=100, descontinuado=False)
    materias_primas_bajo_stock = MateriaPrima.objects.filter(stock__lt=100, descontinuado=False)
    context = {
        'productos': productos_bajo_stock,
        'materias_primas': materias_primas_bajo_stock,
    }
    return render(request, 'inventory/alertas.html', context)

