"""
URLs para la app de customer support
Organiza endpoints para AI tools y administración
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets (administración completa)
router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet, basename='cliente')
router.register(r'tickets', views.TicketViewSet, basename='ticket')
router.register(r'pagos', views.PagoViewSet, basename='pago')

app_name = 'customer_support'

urlpatterns = [
    # ============= 🤖 AI TOOL ENDPOINTS =============
    # Endpoints específicos para ser llamados desde Vercel AI SDK
    path('tools/buscar-cliente/', 
         views.buscar_cliente_tool, 
         name='buscar_cliente_tool'),
    
    path('tools/cliente/<int:cliente_id>/saldo/', 
         views.consultar_saldo_tool, 
         name='consultar_saldo_tool'),
    
    path('tools/crear-ticket/', 
         views.crear_ticket_tool, 
         name='crear_ticket_tool'),
    
    path('tools/registrar-pago/', 
         views.registrar_pago_tool, 
         name='registrar_pago_tool'),
    
    # ============= 📊 UTILITY ENDPOINTS =============
    path('dashboard/estadisticas/', 
         views.estadisticas_dashboard, 
         name='estadisticas_dashboard'),
    
    path('health/', 
         views.health_check, 
         name='health_check'),
    
    # ============= 🔧 CRUD COMPLETO =============
    # Include router URLs para administración completa
    path('', include(router.urls)),
]

"""
📋 RESUMEN DE ENDPOINTS DISPONIBLES:

🤖 AI TOOL ENDPOINTS (para Vercel AI SDK):
- GET  /api/tools/buscar-cliente/?q=nombre     - Buscar cliente
- GET  /api/tools/cliente/{id}/saldo/          - Consultar saldo
- POST /api/tools/crear-ticket/                - Crear ticket
- POST /api/tools/registrar-pago/              - Registrar pago

📊 UTILITY ENDPOINTS:
- GET /api/dashboard/estadisticas/             - Estadísticas del sistema
- GET /api/health/                             - Health check

🔧 CRUD COMPLETO (para administración):
- GET    /api/clientes/                        - Listar clientes
- POST   /api/clientes/                        - Crear cliente
- GET    /api/clientes/{id}/                   - Ver cliente específico
- PUT    /api/clientes/{id}/                   - Actualizar cliente completo
- PATCH  /api/clientes/{id}/                   - Actualizar cliente parcial
- DELETE /api/clientes/{id}/                   - Eliminar cliente

- GET    /api/tickets/                         - Listar tickets
- POST   /api/tickets/                         - Crear ticket
- GET    /api/tickets/{id}/                    - Ver ticket específico
- PUT    /api/tickets/{id}/                    - Actualizar ticket completo
- PATCH  /api/tickets/{id}/                    - Actualizar ticket parcial
- POST   /api/tickets/{id}/cambiar_estado/     - Cambiar estado del ticket
- DELETE /api/tickets/{id}/                    - Eliminar ticket

- GET    /api/pagos/                           - Listar pagos
- POST   /api/pagos/                           - Crear pago
- GET    /api/pagos/{id}/                      - Ver pago específico
- PUT    /api/pagos/{id}/                      - Actualizar pago completo
- PATCH  /api/pagos/{id}/                      - Actualizar pago parcial
- DELETE /api/pagos/{id}/                      - Eliminar pago

🎯 FILTROS DISPONIBLES:
- /api/clientes/?nombre=juan                   - Filtrar clientes por nombre
- /api/tickets/?estado=abierto                 - Filtrar tickets por estado
- /api/pagos/?cliente=1                        - Filtrar pagos por cliente
"""