from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect,get_object_or_404
from sales.models import Pedido, DetallePedido
from .resources import PedidoResource 
from io import BytesIO
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.pdfgen import canvas
from users.views import group_required
from django.core.mail import send_mail
from django.template.loader import render_to_string

@group_required('Empleados') 
def dashboardPedidos(request):
    # Obtener todos los pedidos
    pedidos = Pedido.objects.all() 

    # Contar pedidos por estado
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_proceso = Pedido.objects.filter(estado='en_proceso').count()
    pedidos_completados = Pedido.objects.filter(estado='completado').count()
    pedidos_cancelados = Pedido.objects.filter(estado='cancelado').count()

    # Crear el contexto para la plantilla
    context = {
        'pedidos': pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_proceso': pedidos_proceso,
        'pedidos_completados': pedidos_completados,
        'pedidos_cancelados': pedidos_cancelados,
    } 

    # Renderizar la plantilla con el contexto
    return render(request, 'sales/dashboardPedidos.html', context)

@group_required('Empleados') 
def export_pedidos(request):
    if request.method == 'POST':
        file_format = request.POST.get('file_format')
        resource = PedidoResource()
        dataset = resource.export()  # Exporta los datos en el formato tablib
        
        if file_format == 'xlsx':
            # Exportar como XLSX
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="pedidos_export.xlsx"'
            response.write(dataset.export('xlsx'))
            return response
        
        elif file_format == 'pdf':
            # Generar PDF utilizando ReportLab
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="pedidos_export.pdf"'
            
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            
            # Agrega contenido al PDF
            p.drawString(100, 750, "Reporte de Pedidos")
            
            # Iteración sobre el dataset y agregar filas al PDF
            y = 700
            for pedido in dataset.dict:
                cliente = pedido['cliente']  # Ajusta según los campos en dataset
                fecha_pedido = pedido['fecha_pedido']
                estado = pedido['estado']
                subtotal = pedido['subtotal']
                p.drawString(100, y, f"{cliente} - {fecha_pedido} - {estado} - {subtotal}")
                y -= 20  # Ajustar la altura según sea necesario
            
            p.showPage()
            p.save()
            
            # Escribir el contenido del buffer en el response
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)
            return response
        
        else:
            return HttpResponseBadRequest("Formato no soportado")
    else:
        return HttpResponseBadRequest("Método no permitido")

@group_required('Empleados')   
def pedidos_pendientes(request):
    pedidos = Pedido.objects.filter(estado='pendiente')
    pedidos_proceso = Pedido.objects.filter(estado='en_proceso').count()
    pedidos_completados = Pedido.objects.filter(estado='completado').count()
    pedidos_cancelados = Pedido.objects.filter(estado='cancelado').count()

    # Crear el contexto para la plantilla
    context = {
        'pedidos': pedidos,
        'pedidos_proceso': pedidos_proceso,
        'pedidos_completados': pedidos_completados,
        'pedidos_cancelados': pedidos_cancelados,
    } 
    return render(request, 'sales/DashPendientes.html', context)

@group_required('Empleados') 
def editar_pedido_pendiente(request, pedido_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        pedido = get_object_or_404(Pedido, id=pedido_id)

        # Cambiar el estado del pedido
        pedido.estado = nuevo_estado
        pedido.save()

        # Enviar correo al cliente notificando el cambio de estado
        enviar_correo_cambio_estado(pedido)

        return redirect('pedidos_pendientes')  # Redirigir a la página adecuada
    
@group_required('Empleados')   
def pedidos_proceso(request):
    pedidos = Pedido.objects.filter(estado='en_proceso')
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_completados = Pedido.objects.filter(estado='completado').count()
    pedidos_cancelados = Pedido.objects.filter(estado='cancelado').count()

    # Crear el contexto para la plantilla
    context = {
        'pedidos': pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_completados': pedidos_completados,
        'pedidos_cancelados': pedidos_cancelados,
    } 
    return render(request, 'sales/DashEnProceso.html', context)

@group_required('Empleados') 
def editar_pedido_proceso(request, pedido_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        pedido = get_object_or_404(Pedido, id=pedido_id)

        # Cambiar el estado del pedido
        pedido.estado = nuevo_estado
        pedido.save()

        # Enviar correo al cliente notificando el cambio de estado
        enviar_correo_cambio_estado(pedido)

        return redirect('pedidos_proceso')  # Redirigir a la página adecuada 

@group_required('Empleados')   
def pedidos_completados(request):
    pedidos = Pedido.objects.filter(estado='completado')
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_proceso = Pedido.objects.filter(estado='en_proceso').count()
    pedidos_cancelados = Pedido.objects.filter(estado='cancelado').count()

    # Crear el contexto para la plantilla
    context = {
        'pedidos': pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_proceso': pedidos_proceso,
        'pedidos_cancelados': pedidos_cancelados,
    } 
    return render(request, 'sales/DashCompletados.html', context)

@group_required('Empleados')
def editar_pedido_completado(request, pedido_id):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        pedido = get_object_or_404(Pedido, id=pedido_id)

        # Cambiar el estado del pedido
        pedido.estado = nuevo_estado
        pedido.save()

        enviar_correo_cambio_estado(pedido)
        
        return redirect('pedidos_proceso') 

@group_required('Empleados')   
def pedidos_cancelados(request):
    pedidos = Pedido.objects.filter(estado='cancelado')
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_proceso = Pedido.objects.filter(estado='en_proceso').count()
    pedidos_completados = Pedido.objects.filter(estado='completado').count()

    # Crear el contexto para la plantilla
    context = {
        'pedidos': pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_proceso': pedidos_proceso,
        'pedidos_completados': pedidos_completados,
    } 
    return render(request, 'sales/dashCancelados.html', context)

def consultar_pedido(request,id):
    pedido = get_object_or_404(Pedido, id=id)
    detalles_pedido = DetallePedido.objects.filter(pedido=pedido)
    
    return render(request, 'sales/consultas/consultar_pedido.html', {'pedido': pedido, 'detalles_pedido': detalles_pedido})

def enviar_correo_cambio_estado(pedido):
    subject = f"Tu pedido #{pedido.id} ha cambiado de estado"
    message = render_to_string('emails/pedido_estado_cambiado.html', {
        'pedido': pedido,
        'nuevo_estado': pedido.get_estado_display(),
    })
    send_mail(
        subject, 
        '',  # Si usas un mensaje HTML, este campo puede quedar vacío
        'soporte.quesosistema@gmail.com', 
        [pedido.cliente.email],
        html_message=message  # Se envía como HTML
    )      
