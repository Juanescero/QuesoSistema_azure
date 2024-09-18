from django.shortcuts import render
from inventory.models import Producto 

# Create your views here.
def nosotros(request):
    return render(request, 'blog/nosotros.html', {
    })
    
def catalogo(request):
    productos = Producto.objects.filter(descontinuado=False)  
    return render(request, 'blog/catalogo.html', {'productos': productos})

def nuestros_quesos(request):
    return render(request, 'blog/nuestros_quesos.html', {
    })

def nuestras_materias_prima(request):
    return render(request, 'blog/materias_prima.html', {
    })
    
    #BLOG VIEWS
def blog_informativo(request):
    return render(request, 'blog/blog_informativo.html', {
    })
    
def blog1(request):
    return render(request, 'blog/blog1.html', {
    })
    
def blog2(request):
    return render(request, 'blog/blog2.html', {
    })

def blog3(request):
    return render(request, 'blog/blog3.html', {
    })

def blog4(request):
    return render(request, 'blog/blog4.html', {
    })
    
