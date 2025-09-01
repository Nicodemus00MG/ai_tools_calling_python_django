"""
Serializers para convertir modelos Django a JSON y viceversa
Incluye validaciones personalizadas y campos calculados para AI Tools
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Cliente, Ticket, Pago, HistorialAccion

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para Cliente - Información completa
    Incluye campos calculados y validaciones
    """
    saldo_formateado = serializers.ReadOnlyField()
    total_tickets = serializers.SerializerMethodField()
    ultimo_pago = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre', 'email', 'telefono', 'saldo', 
            'saldo_formateado', 'fecha_registro', 'activo',
            'total_tickets', 'ultimo_pago'
        ]
        read_only_fields = ['id', 'fecha_registro']
    
    def get_total_tickets(self, obj):
        """Cuenta total de tickets del cliente"""
        return obj.tickets.count()
    
    def get_ultimo_pago(self, obj):
        """Información del último pago"""
        ultimo = obj.pagos.first()
        if ultimo:
            return {
                'monto': ultimo.monto,
                'fecha': ultimo.fecha,
                'descripcion': ultimo.descripcion
            }
        return None
    
    def validate_email(self, value):
        """Validación personalizada para email único"""
        if self.instance and self.instance.email == value:
            return value
        
        if Cliente.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un cliente con este email")
        return value

class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer para Ticket - Información completa
    Incluye información del cliente y validaciones de estado
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_email = serializers.CharField(source='cliente.email', read_only=True)
    tiempo_resolucion_str = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'cliente', 'cliente_nombre', 'cliente_email',
            'titulo', 'descripcion', 'estado', 'prioridad',
            'asignado_a', 'fecha_creacion', 'fecha_actualizacion',
            'fecha_resolucion', 'tiempo_resolucion_str'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_tiempo_resolucion_str(self, obj):
        """Tiempo de resolución en formato legible"""
        tiempo = obj.tiempo_resolucion
        if tiempo:
            days = tiempo.days
            hours = tiempo.seconds // 3600
            return f"{days} días, {hours} horas"
        return None
    
    def validate(self, data):
        """Validaciones del modelo completo"""
        # Si se marca como resuelto, agregar fecha de resolución
        if data.get('estado') == 'resuelto' and not data.get('fecha_resolucion'):
            data['fecha_resolucion'] = timezone.now()
        
        return data

class PagoSerializer(serializers.ModelSerializer):
    """
    Serializer para Pago - Información completa
    Incluye validaciones de monto y actualización automática de saldo
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_email = serializers.CharField(source='cliente.email', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id', 'cliente', 'cliente_nombre', 'cliente_email',
            'monto', 'descripcion', 'metodo_pago', 'fecha',
            'procesado_por'
        ]
        read_only_fields = ['id', 'fecha']
    
    def validate_monto(self, value):
        """Validación de monto positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        if value > 999999.99:
            raise serializers.ValidationError("El monto es demasiado alto")
        return value

class HistorialAccionSerializer(serializers.ModelSerializer):
    """
    Serializer para HistorialAccion - Para auditoría
    Para auditoría y seguimiento de AI tool calls
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = HistorialAccion
        fields = [
            'id', 'tipo', 'descripcion', 'cliente', 'cliente_nombre',
            'usuario', 'usuario_username', 'ip_address', 'metadata', 'fecha'
        ]
        read_only_fields = ['id', 'fecha']

# ============= SERIALIZERS ESPECÍFICOS PARA AI TOOLS =============

class ToolResponseClienteSerializer(serializers.ModelSerializer):
    """
    Serializer SIMPLIFICADO para respuestas de AI tools
    Incluye solo información esencial para el AI
    """
    saldo_formateado = serializers.ReadOnlyField()
    
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'email', 'saldo', 'saldo_formateado']

class ToolResponseTicketSerializer(serializers.ModelSerializer):
    """
    Serializer SIMPLIFICADO para tickets en respuestas AI
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'cliente_nombre', 'titulo', 'estado', 'fecha_creacion']

class ToolResponsePagoSerializer(serializers.ModelSerializer):
    """
    Serializer SIMPLIFICADO para pagos en respuestas AI
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    nuevo_saldo = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = ['id', 'cliente_nombre', 'monto', 'descripcion', 'fecha', 'nuevo_saldo']
    
    def get_nuevo_saldo(self, obj):
        """Saldo actualizado del cliente después del pago"""
        return obj.cliente.saldo