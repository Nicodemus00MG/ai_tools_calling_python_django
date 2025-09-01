"""
Views para el API de soporte al cliente
Implementa endpoints específicos para AI tool calling
Cada endpoint está optimizado para ser llamado desde Vercel AI SDK
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
import logging

from .models import Cliente, Ticket, Pago, HistorialAccion
from .serializers import (
    ClienteSerializer, TicketSerializer, PagoSerializer,
    ToolResponseClienteSerializer, ToolResponseTicketSerializer,
    ToolResponsePagoSerializer
)

# Configurar logging para debugging AI tool calls
logger = logging.getLogger(__name__)

def registrar_accion(tipo, descripcion, cliente=None, usuario=None, ip=None, metadata=None):
    """
    Utility function para registrar acciones en el historial
    Útil para tracking de AI tool calls y debugging
    """
    try:
        HistorialAccion.objects.create(
            tipo=tipo,
            descripcion=descripcion,
            cliente=cliente,
            usuario=usuario,
            ip_address=ip,
            metadata=metadata or {}
        )
    except Exception as e:
        logger.error(f"Error registrando acción: {e}")

# ============= AI TOOL ENDPOINTS =============
# Estos endpoints están diseñados específicamente para ser llamados desde AI tools

@api_view(['GET'])
def buscar_cliente_tool(request):
    """
    🤖 AI Tool: Buscar cliente por nombre o email
    
    URL: GET /api/tools/buscar-cliente/?q=nombre_o_email
    
    Query params:
    - q: término de búsqueda (nombre o email)
    
    Returns:
    - Lista de clientes que coinciden
    - Información simplificada para AI processing
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({
            'success': False,
            'error': 'Parámetro "q" requerido',
            'message': 'Proporciona un nombre o email para buscar',
            'ejemplo': '?q=Juan Perez'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Búsqueda flexible por nombre o email (case insensitive)
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) | 
            Q(email__icontains=query),
            activo=True
        ).order_by('nombre')[:10]  # Limitar a 10 resultados
        
        if not clientes.exists():
            return Response({
                'success': True,
                'message': f'No se encontraron clientes con "{query}"',
                'clientes': [],
                'sugerencia': 'Verifica la ortografía o intenta con un término más general'
            })
        
        # Usar serializer simplificado para AI
        serializer = ToolResponseClienteSerializer(clientes, many=True)
        
        # Registrar acción para auditoría
        registrar_accion(
            tipo='consulta',
            descripcion=f'AI Tool: Búsqueda de cliente "{query}"',
            ip=request.META.get('REMOTE_ADDR'),
            metadata={'query': query, 'resultados': len(clientes)}
        )
        
        return Response({
            'success': True,
            'message': f'Se encontraron {len(clientes)} cliente(s) con "{query}"',
            'total': len(clientes),
            'clientes': serializer.data
        })
        
    except Exception as e:
        logger.error(f"Error en buscar_cliente_tool: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def consultar_saldo_tool(request, cliente_id):
    """
    🤖 AI Tool: Consultar saldo específico de un cliente
    
    URL: GET /api/tools/cliente/{cliente_id}/saldo/
    
    Path params:
    - cliente_id: ID del cliente
    
    Returns:
    - Información completa del saldo del cliente
    - Historial reciente de pagos para contexto
    """
    try:
        # Convertir cliente_id a int y validar
        try:
            cliente_id = int(cliente_id)
        except ValueError:
            return Response({
                'success': False,
                'error': 'ID de cliente inválido',
                'message': 'El ID debe ser un número entero'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar cliente
        cliente = get_object_or_404(Cliente, id=cliente_id, activo=True)
        
        # Obtener últimos 5 pagos para dar contexto al AI
        ultimos_pagos = cliente.pagos.all()[:5]
        
        # Registrar consulta para auditoría
        registrar_accion(
            tipo='consulta',
            descripcion=f'AI Tool: Consulta de saldo - {cliente.nombre}',
            cliente=cliente,
            ip=request.META.get('REMOTE_ADDR'),
            metadata={'cliente_id': cliente_id}
        )
        
        response_data = {
            'success': True,
            'cliente': {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'email': cliente.email,
                'saldo': float(cliente.saldo),
                'saldo_formateado': cliente.saldo_formateado,
                'fecha_registro': cliente.fecha_registro
            },
            'ultimos_pagos': [
                {
                    'monto': float(pago.monto),
                    'descripcion': pago.descripcion or 'Pago sin descripción',
                    'fecha': pago.fecha.strftime('%d/%m/%Y %H:%M'),
                    'metodo': pago.get_metodo_pago_display()
                }
                for pago in ultimos_pagos
            ],
            'resumen': {
                'total_tickets': cliente.tickets.count(),
                'total_pagos': cliente.pagos.count(),
                'ultimo_pago_fecha': ultimos_pagos.first().fecha.strftime('%d/%m/%Y') if ultimos_pagos else 'Sin pagos'
            }
        }
        
        return Response(response_data)
        
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cliente no encontrado',
            'message': f'No existe cliente activo con ID {cliente_id}'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Error en consultar_saldo_tool: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def crear_ticket_tool(request):
    """
    🤖 AI Tool: Crear ticket de soporte
    
    URL: POST /api/tools/crear-ticket/
    
    Body params (JSON):
    {
        "cliente": 1,                    # ID del cliente (requerido)
        "titulo": "Problema con factura", # Título del ticket (requerido)
        "descripcion": "Descripción detallada...", # Descripción (requerido)
        "prioridad": "media"             # baja/media/alta/critica (opcional)
    }
    
    Returns:
    - Información del ticket creado
    - Número de ticket para seguimiento
    """
    try:
        data = request.data.copy()
        
        # Validaciones básicas de campos requeridos
        required_fields = ['cliente', 'titulo', 'descripcion']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return Response({
                'success': False,
                'error': 'Campos requeridos faltantes',
                'campos_faltantes': missing_fields,
                'ejemplo': {
                    'cliente': 1,
                    'titulo': 'Problema con factura',
                    'descripcion': 'No puedo acceder a mi factura del mes pasado'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el cliente existe
        try:
            cliente = get_object_or_404(Cliente, id=data['cliente'], activo=True)
        except Cliente.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Cliente no encontrado',
                'message': f'No existe cliente activo con ID {data["cliente"]}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validar prioridad si se proporciona
        prioridades_validas = [choice[0] for choice in Ticket.PRIORIDAD_CHOICES]
        if 'prioridad' in data and data['prioridad'] not in prioridades_validas:
            data['prioridad'] = 'media'  # Default si es inválida
        
        # Crear el ticket
        serializer = TicketSerializer(data=data)
        
        if serializer.is_valid():
            ticket = serializer.save()
            
            # Registrar acción
            registrar_accion(
                tipo='creacion',
                descripcion=f'AI Tool: Ticket creado - {ticket.titulo}',
                cliente=cliente,
                ip=request.META.get('REMOTE_ADDR'),
                metadata={'ticket_id': ticket.id, 'titulo': ticket.titulo}
            )
            
            # Respuesta optimizada para AI
            response_data = {
                'success': True,
                'mensaje': '✅ Ticket creado exitosamente',
                'ticket': {
                    'id': ticket.id,
                    'numero': f"#{ticket.id:06d}",  # Formato: #000001
                    'cliente': cliente.nombre,
                    'titulo': ticket.titulo,
                    'descripcion': ticket.descripcion[:100] + '...' if len(ticket.descripcion) > 100 else ticket.descripcion,
                    'estado': ticket.get_estado_display(),
                    'prioridad': ticket.get_prioridad_display(),
                    'fecha_creacion': ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')
                },
                'instrucciones': f'Ticket #{ticket.id:06d} creado. El cliente {cliente.nombre} puede hacer seguimiento con este número.'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        else:
            return Response({
                'success': False,
                'error': 'Datos inválidos para crear el ticket',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error en crear_ticket_tool: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def registrar_pago_tool(request):
    """
    🤖 AI Tool: Registrar pago de cliente
    Actualiza automáticamente el saldo del cliente
    
    URL: POST /api/tools/registrar-pago/
    
    Body params (JSON):
    {
        "cliente": 1,                      # ID del cliente (requerido)
        "monto": 150.50,                   # Monto del pago (requerido, > 0)
        "descripcion": "Pago de factura",  # Concepto del pago (opcional)
        "metodo_pago": "transferencia"     # efectivo/tarjeta/transferencia/cheque (opcional)
    }
    
    Returns:
    - Información del pago registrado
    - Saldo anterior y nuevo del cliente
    """
    try:
        data = request.data.copy()
        
        # Validación de cliente requerido
        if not data.get('cliente'):
            return Response({
                'success': False,
                'error': 'ID del cliente es requerido',
                'ejemplo': {'cliente': 1, 'monto': 100.00}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validación de monto requerido
        if not data.get('monto'):
            return Response({
                'success': False,
                'error': 'Monto del pago es requerido',
                'ejemplo': {'cliente': 1, 'monto': 100.00}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar y convertir monto
        try:
            monto = float(data['monto'])
            if monto <= 0:
                return Response({
                    'success': False,
                    'error': 'El monto debe ser mayor a 0',
                    'monto_recibido': data['monto']
                }, status=status.HTTP_400_BAD_REQUEST)
            if monto > 999999.99:
                return Response({
                    'success': False,
                    'error': 'El monto es demasiado alto (máximo $999,999.99)',
                    'monto_recibido': monto
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Monto inválido, debe ser un número',
                'monto_recibido': data['monto']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el cliente existe
        try:
            cliente = get_object_or_404(Cliente, id=data['cliente'], activo=True)
            saldo_anterior = float(cliente.saldo)
        except Cliente.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Cliente no encontrado',
                'message': f'No existe cliente activo con ID {data["cliente"]}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validar método de pago
        metodos_validos = [choice[0] for choice in Pago.METODO_CHOICES]
        if 'metodo_pago' in data and data['metodo_pago'] not in metodos_validos:
            data['metodo_pago'] = 'transferencia'  # Default
        
        # Crear el pago
        serializer = PagoSerializer(data=data)
        
        if serializer.is_valid():
            pago = serializer.save()
            
            # El saldo se actualiza automáticamente en el modelo Pago.save()
            cliente.refresh_from_db()
            saldo_nuevo = float(cliente.saldo)
            
            # Registrar acción para auditoría
            registrar_accion(
                tipo='pago',
                descripcion=f'AI Tool: Pago registrado ${monto} - {cliente.nombre}',
                cliente=cliente,
                ip=request.META.get('REMOTE_ADDR'),
                metadata={
                    'pago_id': pago.id,
                    'monto': monto,
                    'saldo_anterior': saldo_anterior,
                    'saldo_nuevo': saldo_nuevo,
                    'metodo': data.get('metodo_pago', 'transferencia')
                }
            )
            
            response_data = {
                'success': True,
                'mensaje': '✅ Pago registrado exitosamente',
                'pago': {
                    'id': pago.id,
                    'cliente': cliente.nombre,
                    'monto': float(pago.monto),
                    'descripcion': pago.descripcion or 'Pago registrado por AI Assistant',
                    'metodo': pago.get_metodo_pago_display(),
                    'fecha': pago.fecha.strftime('%d/%m/%Y %H:%M')
                },
                'saldos': {
                    'anterior': saldo_anterior,
                    'actual': saldo_nuevo,
                    'incremento': saldo_nuevo - saldo_anterior
                },
                'confirmacion': f'💰 Saldo de {cliente.nombre} actualizado: ${saldo_anterior:,.2f} → ${saldo_nuevo:,.2f} (+${monto:,.2f})'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        else:
            return Response({
                'success': False,
                'error': 'Datos inválidos para registrar el pago',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error en registrar_pago_tool: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============= ENDPOINTS ADICIONALES =============

@api_view(['GET'])
def estadisticas_dashboard(request):
    """
    📊 Endpoint para dashboard con estadísticas generales
    Útil para el AI assistant para dar contexto general del sistema
    """
    try:
        stats = {
            'clientes': {
                'total': Cliente.objects.filter(activo=True).count(),
                'con_saldo_positivo': Cliente.objects.filter(activo=True, saldo__gt=0).count(),
                'registrados_hoy': Cliente.objects.filter(
                    activo=True, 
                    fecha_registro__date=timezone.now().date()
                ).count(),
            },
            'tickets': {
                'total': Ticket.objects.count(),
                'abiertos': Ticket.objects.filter(estado='abierto').count(),
                'en_proceso': Ticket.objects.filter(estado='en_proceso').count(),
                'resueltos_hoy': Ticket.objects.filter(
                    estado='resuelto',
                    fecha_resolucion__date=timezone.now().date()
                ).count(),
                'pendientes': Ticket.objects.filter(
                    estado__in=['abierto', 'en_proceso', 'pendiente']
                ).count(),
            },
            'pagos_hoy': {
                'total_transacciones': Pago.objects.filter(
                    fecha__date=timezone.now().date()
                ).count(),
                'monto_total': float(sum(
                    p.monto for p in Pago.objects.filter(fecha__date=timezone.now().date())
                )),
            },
            'sistema': {
                'fecha_actual': timezone.now().strftime('%d/%m/%Y %H:%M'),
                'timezone': 'America/Guayaquil (Ecuador)',
            }
        }
        
        return Response({
            'success': True,
            'estadisticas': stats,
            'mensaje': 'Estadísticas del sistema actualizadas'
        })
        
    except Exception as e:
        logger.error(f"Error en estadisticas_dashboard: {e}")
        return Response({
            'success': False,
            'error': 'Error obteniendo estadísticas',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def health_check(request):
    """
    ❤️ Health check endpoint para verificar que el API funciona
    Útil para monitoring y debugging
    """
    return Response({
        'status': 'OK',
        'message': '🤖 AI Assistant API funcionando correctamente',
        'timestamp': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        'version': '1.0.0',
        'endpoints_disponibles': [
            'GET /api/tools/buscar-cliente/?q=nombre',
            'GET /api/tools/cliente/{id}/saldo/',
            'POST /api/tools/crear-ticket/',
            'POST /api/tools/registrar-pago/',
            'GET /api/dashboard/estadisticas/',
            'GET /api/health/'
        ]
    })

# ============= VIEWSETS COMPLETOS (para administración) =============

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para CRUD de clientes
    Para uso administrativo del sistema
    """
    queryset = Cliente.objects.filter(activo=True)
    serializer_class = ClienteSerializer
    
    def get_queryset(self):
        queryset = Cliente.objects.filter(activo=True)
        nombre = self.request.query_params.get('nombre')
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        return queryset.order_by('nombre')

class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para CRUD de tickets
    Para uso administrativo del sistema
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        queryset = Ticket.objects.all()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset.order_by('-fecha_creacion')
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Acción personalizada para cambiar estado de ticket
        URL: POST /api/tickets/{id}/cambiar_estado/
        Body: {"estado": "resuelto"}
        """
        ticket = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        estados_validos = [choice[0] for choice in Ticket.ESTADO_CHOICES]
        if nuevo_estado in estados_validos:
            ticket.estado = nuevo_estado
            if nuevo_estado == 'resuelto' and not ticket.fecha_resolucion:
                ticket.fecha_resolucion = timezone.now()
            ticket.save()
            
            return Response({
                'success': True,
                'mensaje': f'Estado cambiado a {ticket.get_estado_display()}',
                'ticket': TicketSerializer(ticket).data
            })
        
        return Response({
            'success': False,
            'error': 'Estado inválido',
            'estados_validos': estados_validos
        }, status=status.HTTP_400_BAD_REQUEST)

class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para CRUD de pagos
    Para uso administrativo del sistema
    """
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
    def get_queryset(self):
        queryset = Pago.objects.all()
        cliente_id = self.request.query_params.get('cliente')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        return queryset.order_by('-fecha')