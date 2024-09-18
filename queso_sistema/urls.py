from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.conf.urls import handler500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('user/', include('users.urls')),
    path('sales/', include('sales.urls')),
    path('inventory/', include('inventory.urls')),
    path('cart/', include('cart.urls')),
    path('blog/', include('blog.urls')),
    #Ruta para forzar error 500
    path('test-error/', views.test_error_500, name='test_error_500'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Llamado a las vistas del error 404 y 500
handler404 = views.error_404_view
handler500 = views.error_500_view



