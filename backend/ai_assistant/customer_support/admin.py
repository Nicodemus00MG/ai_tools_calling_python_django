"""
Configuración del Django Admin para AI Assistant
Interface web para administrar los datos del sistema
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count
from .models import Cliente, Ticket, Pago, HistorialAccion

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Administración de Clientes
    """
    list_display = [
        'nombre', 
        'email', 
        'saldo_badge', 
        'total_tickets_badge',
        'activo', 
        'fecha_registro'
    ]
    list_filter = ['activo', 'fecha_registro', 'saldo']
    search_fields = ['nombre', 'email', 'telefono']
    readonly_fields = ['fecha_registro', 'saldo_formateado', 'total_pagos', 'total_tickets']
    list_per_page = 20
    
    fieldsets = (
        ('📋 Información Personal', {
            'fields': ('nombre', 'email', 'telefono')
        }),
        ('💰 Información Financiera', {
            'fields': ('saldo', 'saldo_formateado', 'total_pagos')
        }),
        ('🎫 Información de Soporte', {
            'fields': ('total_tickets',)
        }),
        ('⚙️ Estado del Sistema', {
            'fields': ('activo', 'fecha_registro')
        }),
    )
    
    def saldo_badge(self, obj):
        """Badge colorizado para el saldo"""
        if obj.saldo > 1000:
            color = 'green'
            icon = '💰'
        elif obj.saldo > 0:
            color = 'orange'
            icon = '💵'
        else:
            color = 'red'
            icon = '❌'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.saldo_formateado
        )
    saldo_badge.short_description = "💰 Saldo"
    saldo_badge.admin_order_field = 'saldo'
    
    def total_tickets_badge(self, obj):
        """Badge con total de tickets"""
        total = obj.tickets.count()
        abiertos = obj.tickets.filter(estado__in=['abierto', 'en_proceso']).count()
        
        if abiertos > 0:
            color = 'red'
            icon = '🚨'
        else:
            color = 'green'
            icon = '✅'
            
        return format_html(
            '<span style="color: {};">{} {} total ({} abiertos)</span>',
            color, icon, total, abiertos
        )
    total_tickets_badge.short_description = "🎫 Tickets"
    
    def total_pagos(self, obj):
        """Total de pagos realizados"""
        total = obj.pagos.aggregate(
            count=Count('id'),
            sum=Sum('monto')
        )
        return f"{total['count']} pagos - ${total['sum'] or 0:,.2f}"
    total_pagos.short_description = "💳 Total Pagos"
    
    def total_tickets(self, obj):
        """Total de tickets del cliente"""
        return obj.tickets.count()
    total_tickets.short_description = "🎫 Total Tickets"
    
    actions = ['activar_clientes', 'desactivar_clientes']
    
    def activar_clientes(self, request, queryset):
        """Acción masiva para activar clientes"""
        updated = queryset.update(activo=True)
        self.message_user(request, f"{updated} clientes activados.")
    activar_clientes.short_description = "✅ Activar clientes seleccionados"
    
    def desactivar_clientes(self, request, queryset):
        """Acción masiva para desactivar clientes"""
        updated = queryset.update(activo=False)
        self.message_user(request, f"{updated} clientes desactivados.")
    desactivar_clientes.short_description = "❌ Desactivar clientes seleccionados"

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Administración de Tickets
    """
    list_display = [
        'id_formateado', 
        'cliente_link', 
        'titulo_corto', 
        'estado_badge', 
        'prioridad_badge',
        'asignado_a',
        'fecha_creacion'
    ]
    list_filter = [
        'estado', 
        'prioridad', 
        'fecha_creacion', 
        'asignado_a'
    ]
    search_fields = [
        'titulo', 
        'descripcion', 
        'cliente__nombre', 
        'cliente__email'
    ]
    readonly_fields = [
        'fecha_creacion', 
        'fecha_actualizacion', 
        'tiempo_resolucion_display'
    ]
    list_per_page = 25
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('🎫 Información del Ticket', {
            'fields': ('cliente', 'titulo', 'descripcion')
        }),
        ('⚙️ Estado y Prioridad', {
            'fields': ('estado', 'prioridad', 'asignado_a')
        }),
        ('📅 Fechas', {
            'fields': (
                'fecha_creacion', 
                'fecha_actualizacion', 
                'fecha_resolucion',
                'tiempo_resolucion_display'
            )
        }),
    )
    
    def id_formateado(self, obj):
        """ID con formato de ticket"""
        return f"#{obj.id:06d}"
    id_formateado.short_description = "ID"
    id_formateado.admin_order_field = 'id'
    
    def cliente_link(self, obj):
        """Link al cliente"""
        url = reverse('admin:customer_support_cliente_change', args=[obj.cliente.id])
        return format_html('<a href="{}">{}</a>', url, obj.cliente.nombre)
    cliente_link.short_description = "👤 Cliente"
    cliente_link.admin_order_field = 'cliente__nombre'
    
    def titulo_corto(self, obj):
        """Título truncado"""
        return obj.titulo[:50] + "..." if len(obj.titulo) > 50 else obj.titulo
    titulo_corto.short_description = "📝 Título"
    
    def estado_badge(self, obj):
        """Badge colorizado para estado"""
        colors_icons = {
            'abierto': ('red', '🔴'),
            'en_proceso': ('orange', '🟡'),
            'pendiente': ('blue', '🔵'),
            'resuelto': ('green', '✅'),
            'cerrado': ('gray', '⚫')
        }
        color, icon = colors_icons.get(obj.estado, ('black', '❓'))
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_estado_display()
        )
    estado_badge.short_description = "📊 Estado"
    estado_badge.admin_order_field = 'estado'
    
    def prioridad_badge(self, obj):
        """Badge para prioridad"""
        colors_icons = {
            'baja': ('green', '🟢'),
            'media': ('orange', '🟡'),
            'alta': ('red', '🔴'),
            'critica': ('darkred', '💥')
        }
        color, icon = colors_icons.get(obj.prioridad, ('black', '❓'))
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_prioridad_display()
        )
    prioridad_badge.short_description = "⚡ Prioridad"
    prioridad_badge.admin_order_field = 'prioridad'
    
    def tiempo_resolucion_display(self, obj):
        """Mostrar tiempo de resolución"""
        if obj.tiempo_resolucion:
            days = obj.tiempo_resolucion.days
            hours = obj.tiempo_resolucion.seconds // 3600
            return f"{days} días, {hours} horas"
        return "Sin resolver"
    tiempo_resolucion_display.short_description = "⏱️ Tiempo Resolución"
    
    actions = ['marcar_como_resuelto', 'marcar_como_en_proceso']
    
    def marcar_como_resuelto(self, request, queryset):
        """Acción masiva para marcar tickets como resueltos"""
        from django.utils import timezone
        updated = queryset.filter(estado__in=['abierto', 'en_proceso']).update(
            estado='resuelto',
            fecha_resolucion=timezone.now()
        )
        self.message_user(request, f"{updated} tickets marcados como resueltos.")
    marcar_como_resuelto.short_description = "✅ Marcar como resuelto"
    
    def marcar_como_en_proceso(self, request, queryset):
        """Acción masiva para marcar tickets en proceso"""
        updated = queryset.filter(estado='abierto').update(estado='en_proceso')
        self.message_user(request, f"{updated} tickets marcados en proceso.")
    marcar_como_en_proceso.short_description = "🟡 Marcar en proceso"

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """
    Administración de Pagos
    """
    list_display = [
        'id',
        'cliente_link',
        'monto_formateado',
        'metodo_badge',
        'descripcion_corta',
        'fecha',
        'procesado_por'
    ]
    list_filter = [
        'metodo_pago',
        'fecha',
        'procesado_por'
    ]
    search_fields = [
        'cliente__nombre',
        'cliente__email',
        'descripcion'
    ]
    readonly_fields = ['fecha']
    list_per_page = 25
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('💰 Información del Pago', {
            'fields': ('cliente', 'monto', 'descripcion')
        }),
        ('💳 Método y Procesamiento', {
            'fields': ('metodo_pago', 'procesado_por')
        }),
        ('📅 Fecha', {
            'fields': ('fecha',)
        }),
    )
    
    def cliente_link(self, obj):
        """Link al cliente"""
        url = reverse('admin:customer_support_cliente_change', args=[obj.cliente.id])
        return format_html('<a href="{}">{}</a>', url, obj.cliente.nombre)
    cliente_link.short_description = "👤 Cliente"
    cliente_link.admin_order_field = 'cliente__nombre'
    
    def monto_formateado(self, obj):
        """Monto con formato de moneda"""
        return format_html(
            '<span style="color: green; font-weight: bold;">${:,.2f}</span>',
            obj.monto
        )
    monto_formateado.short_description = "💰 Monto"
    monto_formateado.admin_order_field = 'monto'
    
    def metodo_badge(self, obj):
        """Badge para método de pago"""
        icons = {
            'efectivo': '💵',
            'tarjeta': '💳',
            'transferencia': '🏦',
            'cheque': '📄'
        }
        icon = icons.get(obj.metodo_pago, '❓')
        return format_html(
            '{} {}',
            icon, obj.get_metodo_pago_display()
        )
    metodo_badge.short_description = "💳 Método"
    metodo_badge.admin_order_field = 'metodo_pago'
    
    def descripcion_corta(self, obj):
        """Descripción truncada"""
        if not obj.descripcion:
            return "-"
        return obj.descripcion[:30] + "..." if len(obj.descripcion) > 30 else obj.descripcion
    descripcion_corta.short_description = "📝 Descripción"

@admin.register(HistorialAccion)
class HistorialAccionAdmin(admin.ModelAdmin):
    """
    Administración del Historial de Acciones (Auditoría)
    """
    list_display = [
        'fecha',
        'tipo_badge',
        'descripcion_corta',
        'cliente_link',
        'usuario',
        'ip_address'
    ]
    list_filter = [
        'tipo',
        'fecha',
        'usuario'
    ]
    search_fields = [
        'descripcion',
        'cliente__nombre',
        'usuario__username',
        'ip_address'
    ]
    readonly_fields = [
        'fecha',
        'metadata_display'
    ]
    list_per_page = 50
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('📋 Información de la Acción', {
            'fields': ('tipo', 'descripcion', 'cliente', 'usuario')
        }),
        ('🌐 Información Técnica', {
            'fields': ('ip_address', 'fecha', 'metadata_display')
        }),
    )
    
    def tipo_badge(self, obj):
        """Badge para tipo de acción"""
        colors_icons = {
            'consulta': ('blue', '🔍'),
            'creacion': ('green', '➕'),
            'actualizacion': ('orange', '✏️'),
            'pago': ('purple', '💰'),
            'ai_tool': ('red', '🤖')
        }
        color, icon = colors_icons.get(obj.tipo, ('black', '❓'))
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_tipo_display()
        )
    tipo_badge.short_description = "🏷️ Tipo"
    tipo_badge.admin_order_field = 'tipo'
    
    def descripcion_corta(self, obj):
        """Descripción truncada"""
        return obj.descripcion[:60] + "..." if len(obj.descripcion) > 60 else obj.descripcion
    descripcion_corta.short_description = "📝 Descripción"
    
    def cliente_link(self, obj):
        """Link al cliente si existe"""
        if obj.cliente:
            url = reverse('admin:customer_support_cliente_change', args=[obj.cliente.id])
            return format_html('<a href="{}">{}</a>', url, obj.cliente.nombre)
        return "-"
    cliente_link.short_description = "👤 Cliente"
    cliente_link.admin_order_field = 'cliente__nombre'
    
    def metadata_display(self, obj):
        """Mostrar metadata en formato legible"""
        if obj.metadata:
            import json
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.metadata, indent=2, ensure_ascii=False)
            )
        return "Sin datos adicionales"
    metadata_display.short_description = "📊 Metadata"
    
    def has_add_permission(self, request):
        """No permitir agregar historial manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir modificar historial"""
        return False

# Personalizar el admin site
admin.site.site_header = "🤖 AI Assistant - Panel de Control"
admin.site.site_title = "AI Assistant Admin"
admin.site.index_title = "Sistema de Soporte con Inteligencia Artificial"