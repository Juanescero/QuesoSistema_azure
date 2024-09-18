from django.shortcuts import render, redirect, get_object_or_404
from users.views import group_required
from django.contrib import messages
from cart.Carrito import Carrito
from inventory.models import Producto
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from sales.models import Pedido, DetallePedido
from django.contrib import messages
from .forms import ClienteProfileForm

@group_required('Clientes')
def carrito(request):
    carrito = request.session.get('carrito', {})
    total_carrito = sum(item['acumulado'] for item in carrito.values())
    pedido_id = request.GET.get('pedido_id')  # Obtén el pedido_id desde la URL si está presente
    return render(request, 'cart/carrito.html', {'total_carrito': total_carrito, 'pedido_id': pedido_id})

@group_required('Clientes')
def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.eliminar(producto)
    return redirect("carrito")

@group_required('Clientes')
def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.restar(producto)
    return redirect("carrito")

@group_required('Clientes')
def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("carrito")

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme  # Cambiar la importación


@group_required('Clientes')
def agregar_al_carrito(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    carrito = request.session.get('carrito', {})

    id = str(producto_id)
    precio = float(producto.precio)  # Convertir el precio de Decimal a float

    if id not in carrito:
        carrito[id] = {
            'nombre': producto.nombre,
            'cantidad': 1,
            'acumulado': precio,
            'producto_id': producto_id
        }
    else:
        carrito[id]['cantidad'] += 1
        carrito[id]['acumulado'] += precio  # Usar el precio convertido a float

    request.session['carrito'] = carrito

    messages.success(request, f'{producto.nombre} ha sido agregado al carrito.')

    # Obtener la URL referer para determinar desde qué página proviene la solicitud
    referer = request.META.get('HTTP_REFERER', '')
    
    # Verificar si la URL referer es segura
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
        # Si estás en el template de catálogo, la URL referer será probablemente la del catálogo
        if 'catalogo' in referer:
            return HttpResponseRedirect(referer)  # Mantenerse en el catálogo

        # Si estás en el template de carrito, la URL referer será probablemente la del carrito
        if 'carrito' in referer:
            return redirect('carrito')  # Redirigir al carrito

    # Redirigir al catálogo si no hay referer
    return redirect('catalogo')

def enviar_correo_pedido_cliente(pedido, detalles):
    try:
        asunto = f'Tu pedido #{pedido.id} ha sido creado'
        mensaje_html = render_to_string('emails/pedido_creado_cliente.html', {'pedido': pedido, 'detalles': detalles})
        mensaje_texto = f"Hola {pedido.cliente.primer_nombre}, tu pedido #{pedido.id} ha sido registrado con éxito. Pronto recibirás más actualizaciones."

        send_mail(
            asunto,
            mensaje_texto,
            settings.DEFAULT_FROM_EMAIL,
            [pedido.cliente.email],
            html_message=mensaje_html
        )
    except Exception as e:
        print(f'Error al enviar correo al cliente: {e}')

@group_required('Clientes')
def procesar_pedido(request):
    carrito = request.session.get('carrito', {})

    if not carrito:
        messages.warning(request, 'No hay productos en el carrito')
        return redirect('carrito')

    try:
        with transaction.atomic():
            # Crear el pedido
            pedido = Pedido.objects.create(
                cliente=request.user,
                subtotal=sum(item['acumulado'] for item in carrito.values())
            )

            # Crear los detalles del pedido
            detalles = []
            for key, item in carrito.items():
                producto = Producto.objects.get(id=item['producto_id'])
                detalle = DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item['cantidad'],
                    precio=producto.precio
                )
                detalles.append(detalle)

            # Limpiar el carrito después de crear el pedido
            request.session['carrito'] = {}

            # Guardar el ID del pedido en la sesión (convertido a string)
            request.session['last_order_id'] = str(pedido.id)

            # Restablecer las banderas de notificación
            if 'notificacion_enviada' in request.session:
                del request.session['notificacion_enviada']
            if 'notificaciones_activadas' in request.session:
                del request.session['notificaciones_activadas']

        # Intentar enviar el correo
        try:
            enviar_correo_pedido_admin(pedido, detalles)
            messages.success(request, '¡Pedido creado con éxito!')
            return redirect('carrito')
        except Exception as email_error:
            messages.warning(request, f'Pedido creado, pero hubo un problema al enviar el correo: {email_error}')
            return redirect('carrito')

    except Exception as e:
        messages.error(request, f'Hubo un problema al procesar tu pedido: {e}')
        return redirect('carrito')


@group_required('Clientes')
def activar_notificaciones_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    detalles = DetallePedido.objects.filter(pedido=pedido)  # Obtener los detalles del pedido
    pedido.notificaciones_activas = True  # Activar notificaciones
    pedido.save()

    # Enviar el correo para este pedido si no se ha hecho ya
    if 'notificacion_enviada' not in request.session:
        enviar_correo_pedido_cliente(pedido, detalles)
        # Marcar la notificación como enviada solo para este pedido
        request.session['notificacion_enviada'] = True
        
    request.session['notificaciones_activadas'] = True
    messages.success(request, 'Has activado las notificaciones para tu pedido.')
    return redirect('carrito')

def enviar_correo_pedido_admin(pedido, detalles):
    """
    Función para enviar un correo al administrador con los detalles del pedido.
    """
    subject = f'Nuevo Pedido #{pedido.id} - Cliente: {pedido.cliente.email}'
    message = f"Detalles del Pedido #{pedido.id}\n\n"
    
    for detalle in detalles:
        message += f"Producto: {detalle.producto.nombre}\n"
        message += f"Cantidad: {detalle.cantidad}\n"
        message += f"Precio Unitario: ${detalle.precio}\n"
        message += "----------------------\n"

    message += f"Subtotal: ${pedido.subtotal}\n"
    message += f"Cliente: {pedido.cliente.primer_nombre} ({pedido.cliente.email})\n"
    message += f"Fecha del pedido: {pedido.fecha_pedido}\n"

    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['soporte.quesosistema@gmail.com']  # Cambia a la dirección del administrador

    # Enviar el correo
    send_mail(subject, message, email_from, recipient_list)
   
@group_required('Clientes')
def limpiar_notificacion_flag(request):
    if 'notificacion_enviada' in request.session:
        del request.session['notificacion_enviada']  # Eliminar la bandera de sesión
    if 'notificaciones_activadas' in request.session:
        del request.session['notificaciones_activadas']  # Eliminar la bandera de activación de notificaciones
    messages.info(request, 'Preferencias de notificación actualizadas.')
    return redirect('carrito')  # Redirigir al carrito

@group_required('Clientes')
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    return render(request, 'cart/pedidosCliente.html', {'pedidos': pedidos})

@group_required('Clientes')
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if pedido.estado == 'pendiente':  
        pedido.estado = 'cancelado'
        pedido.save()
        messages.error(request, f'El pedido #{pedido.id} ha sido cancelado.')

    return redirect('mis_pedidos')  

@group_required('Clientes')
def perfil_cliente(request):
    if request.method == 'POST':
        form = ClienteProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado con éxito.')
            return redirect('perfil_cliente')
        else:
            print(form.errors)  # Esto imprimirá los errores del formulario en la consola
            messages.error(request, 'Por favor corrige los errores a continuación.')

    else:
        form = ClienteProfileForm(instance=request.user)

    return render(request, 'users/perfilCliente.html', {
        'form': form,
        'user': request.user,
    })