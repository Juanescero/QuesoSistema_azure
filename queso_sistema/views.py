from django.shortcuts import render
from django.http import HttpResponseServerError

#Vista Index
def index(request):
    return render(request, 'core/index.html', {
    })
    
#Vista de los errores
def error_404_view(request, exception=None):
    return render(request, 'core/Error404.html', status=404)


def error_500_view(request, exception=None):
    return render(request, 'core/Error500.html', status=500)

#Vista de prueba del error 500
def test_error_500(request):
    raise Exception("This is a test error.")