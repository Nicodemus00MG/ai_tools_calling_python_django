"""
URLs principales del proyecto AI Assistant
Configuración de rutas para Django + AI Tools
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_health(request):
    """Redirigir root a health check"""
    return HttpResponseRedirect('/api/health/')

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API endpoints para AI Tools
    path('api/', include('customer_support.urls')),
    
    # Redirect root to health check
    path('', redirect_to_health),
]

# En desarrollo, servir archivos estáticos y media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Si tienes archivos de media en el futuro:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personalizar títulos del admin
admin.site.site_header = "🤖 AI Assistant Admin"
admin.site.site_title = "AI Assistant"
admin.site.index_title = "Panel de Administración"