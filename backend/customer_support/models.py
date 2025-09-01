"""
Modelos de datos para el sistema de soporte al cliente con AI Tools
- Cliente: Información básica y saldo
- Ticket: Casos de soporte 
- Pago: Registro de pagos realizados
- Historial: Log de todas las acciones para auditoría
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Cliente(models.Model):
    """
    Modelo para almacenar información de clientes
    Incluye saldo para simulación de sistema financiero
    """
    nombre = models.CharField(
        max_length=100, 
        help_text="Nombre completo del cliente"
    )
    email = models.EmailField(
        unique=True,
        help_text="Email único del cliente"
    )
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Teléfono de contacto"
    )
    saldo = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        help_text="Saldo actual del cliente"
    )
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha de registro del cliente"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Cliente activo en el sistema"
    )
    
    class Meta:
        ordering = ['nombre']
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    def __str__(self):
        return f"{self.nombre} ({self.email})"
    
    @property
    def saldo_formateado(self):
        """Retorna el saldo formateado en moneda"""
        return f"${self.saldo:,.2f}"

class Ticket(models.Model):
    """
    Modelo para tickets de soporte
    Sistema de estados para seguimiento de casos
    """
    
    # Estados del ticket
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Proceso'),
        ('pendiente', 'Pendiente Cliente'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]
    
    # Prioridades
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE,
        related_name='tickets',
        help_text="Cliente que reporta el ticket"
    )
    titulo = models.CharField(
        max_length=200,
        help_text="Título descriptivo del problema"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del problema"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='abierto',
        help_text="Estado actual del ticket"
    )
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        help_text="Prioridad del ticket"
    )
    asignado_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_asignados',
        help_text="Agente asignado al ticket"
    )
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha de creación del ticket"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización"
    )
    fecha_resolucion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de resolución del ticket"
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
    
    def __str__(self):
        return f"#{self.id} - {self.titulo[:50]}"
    
    @property
    def tiempo_resolucion(self):
        """Calcula tiempo de resolución si está resuelto"""
        if self.fecha_resolucion:
            return self.fecha_resolucion - self.fecha_creacion
        return None

class Pago(models.Model):
    """
    Modelo para registro de pagos de clientes
    Actualiza automáticamente el saldo del cliente
    """
    
    METODO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('cheque', 'Cheque'),
    ]
    
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE,
        related_name='pagos',
        help_text="Cliente que realiza el pago"
    )
    monto = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Monto del pago"
    )
    descripcion = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Descripción/concepto del pago"
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        default='transferencia',
        help_text="Método de pago utilizado"
    )
    fecha = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha del pago"
    )
    procesado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que procesó el pago"
    )
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
    
    def __str__(self):
        return f"{self.cliente.nombre} - ${self.monto}"
    
    def save(self, *args, **kwargs):
        """
        Override save para actualizar el saldo del cliente
        automáticamente cuando se registra un pago
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:  # Solo si es un pago nuevo
            self.cliente.saldo += self.monto
            self.cliente.save()

class HistorialAccion(models.Model):
    """
    Modelo para auditoría - registra todas las acciones del sistema
    Útil para tracking de AI tool calls y debugging
    """
    
    TIPO_CHOICES = [
        ('consulta', 'Consulta'),
        ('creacion', 'Creación'),
        ('actualizacion', 'Actualización'),
        ('pago', 'Pago'),
        ('ai_tool', 'AI Tool Call'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        help_text="Tipo de acción realizada"
    )
    descripcion = models.TextField(
        help_text="Descripción de la acción"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='historial',
        help_text="Cliente relacionado (si aplica)"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que realizó la acción"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP desde donde se realizó la acción"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos adicionales en formato JSON"
    )
    fecha = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de la acción"
    )
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = "Historial de Acción"
        verbose_name_plural = "Historial de Acciones"
    
    def __str__(self):
        return f"{self.tipo} - {self.descripcion[:50]} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"