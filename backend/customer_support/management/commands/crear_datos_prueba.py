"""
Management command para crear datos de prueba
Útil para testing y demo del sistema AI Assistant

Uso: python manage.py crear_datos_prueba
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from customer_support.models import Cliente, Ticket, Pago, HistorialAccion
from decimal import Decimal
import random
from datetime import timedelta

class Command(BaseCommand):
    help = '🤖 Crear datos de prueba para AI Assistant'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Limpiar datos existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando creación de datos de prueba...')
        )

        if options['limpiar']:
            self.limpiar_datos()

        # Crear datos en orden
        clientes = self.crear_clientes()
        tickets = self.crear_tickets(clientes)
        pagos = self.crear_pagos(clientes)
        self.crear_historial()

        self.mostrar_resumen(clientes, tickets, pagos)

    def limpiar_datos(self):
        """Limpiar todos los datos existentes"""
        self.stdout.write('🧹 Limpiando datos existentes...')
        
        HistorialAccion.objects.all().delete()
        Pago.objects.all().delete()
        Ticket.objects.all().delete()
        Cliente.objects.all().delete()
        
        self.stdout.write(
            self.style.WARNING('   ✅ Datos limpiados')
        )

    def crear_clientes(self):
        """Crear clientes de prueba"""
        self.stdout.write('👥 Creando clientes...')
        
        clientes_data = [
            {
                'nombre': 'María García López',
                'email': 'maria.garcia@email.com',
                'telefono': '+593-98-765-4321',
                'saldo': Decimal('1250.00'),
            },
            {
                'nombre': 'Juan Carlos Pérez',
                'email': 'juan.perez@empresa.com',
                'telefono': '+593-99-123-4567',
                'saldo': Decimal('850.50'),
            },
            {
                'nombre': 'Ana Sofía Rodríguez',
                'email': 'ana.rodriguez@gmail.com',
                'telefono': '+593-96-789-0123',
                'saldo': Decimal('0.00'),
            },
            {
                'nombre': 'Carlos Alberto Mendoza',
                'email': 'carlos.mendoza@yahoo.com',
                'telefono': '+593-97-456-7890',
                'saldo': Decimal('2100.75'),
            },
            {
                'nombre': 'Lucía Fernández Silva',
                'email': 'lucia.fernandez@hotmail.com',
                'telefono': '+593-95-234-5678',
                'saldo': Decimal('450.25'),
            },
            {
                'nombre': 'Roberto González Vega',
                'email': 'roberto.gonzalez@empresa.ec',
                'telefono': '+593-98-345-6789',
                'saldo': Decimal('3200.00'),
            },
        ]

        clientes_creados = []
        for data in clientes_data:
            # Fecha de registro aleatoria en los últimos 6 meses
            fecha_registro = timezone.now() - timedelta(
                days=random.randint(1, 180)
            )
            
            cliente = Cliente.objects.create(
                nombre=data['nombre'],
                email=data['email'],
                telefono=data['telefono'],
                saldo=data['saldo'],
                fecha_registro=fecha_registro,
                activo=True
            )
            clientes_creados.append(cliente)
            
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ {len(clientes_creados)} clientes creados')
        )
        return clientes_creados

    def crear_tickets(self, clientes):
        """Crear tickets de prueba"""
        self.stdout.write('🎫 Creando tickets...')
        
        tickets_data = [
            {
                'titulo': 'Problema con factura del mes anterior',
                'descripcion': 'No puedo acceder a mi factura de noviembre. El sistema me dice que no tengo permisos.',
                'estado': 'abierto',
                'prioridad': 'media',
            },
            {
                'titulo': 'Error en el cálculo del saldo',
                'descripcion': 'Mi saldo muestra un valor incorrecto después del último pago realizado.',
                'estado': 'en_proceso',
                'prioridad': 'alta',
            },
            {
                'titulo': 'Solicitud de cambio de datos personales',
                'descripcion': 'Necesito actualizar mi número de teléfono y dirección de correo electrónico.',
                'estado': 'resuelto',
                'prioridad': 'baja',
            },
            {
                'titulo': 'No puedo realizar pagos en línea',
                'descripcion': 'La plataforma de pagos no acepta mi tarjeta de crédito. He intentado varias veces.',
                'estado': 'abierto',
                'prioridad': 'alta',
            },
        ]

        tickets_creados = []
        for i, data in enumerate(tickets_data):
            # Asignar cliente aleatorio
            cliente = random.choice(clientes)
            
            # Fecha de creación aleatoria en los últimos 30 días
            fecha_creacion = timezone.now() - timedelta(
                days=random.randint(1, 30)
            )
            
            # Si está resuelto, agregar fecha de resolución
            fecha_resolucion = None
            if data['estado'] == 'resuelto':
                fecha_resolucion = fecha_creacion + timedelta(
                    hours=random.randint(2, 72)
                )
            
            ticket = Ticket.objects.create(
                cliente=cliente,
                titulo=data['titulo'],
                descripcion=data['descripcion'],
                estado=data['estado'],
                prioridad=data['prioridad'],
                fecha_creacion=fecha_creacion,
                fecha_resolucion=fecha_resolucion
            )
            tickets_creados.append(ticket)
            
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ {len(tickets_creados)} tickets creados')
        )
        return tickets_creados

    def crear_pagos(self, clientes):
        """Crear pagos de prueba"""
        self.stdout.write('💰 Creando pagos...')
        
        pagos_creados = []
        
        # Crear varios pagos por cliente
        for cliente in clientes:
            num_pagos = random.randint(1, 5)  # 1-5 pagos por cliente
            
            for _ in range(num_pagos):
                # Monto aleatorio
                monto = Decimal(str(round(random.uniform(50, 1000), 2)))
                
                # Método de pago aleatorio
                metodo = random.choice(['efectivo', 'tarjeta', 'transferencia', 'cheque'])
                
                # Descripción aleatoria
                descripciones = [
                    'Pago de factura mensual',
                    'Abono a cuenta corriente',
                    'Pago de servicios',
                    'Cancelación de deuda pendiente',
                ]
                descripcion = random.choice(descripciones)
                
                # Fecha aleatoria en los últimos 60 días
                fecha = timezone.now() - timedelta(
                    days=random.randint(1, 60)
                )
                
                # Crear el pago SIN actualizar el saldo automáticamente
                pago = Pago(
                    cliente=cliente,
                    monto=monto,
                    descripcion=descripcion,
                    metodo_pago=metodo,
                    fecha=fecha
                )
                
                # Guardar SIN triggear el save automático
                super(Pago, pago).save()
                pagos_creados.append(pago)
        
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ {len(pagos_creados)} pagos creados')
        )
        return pagos_creados

    def crear_historial(self):
        """Crear algunas acciones de historial"""
        self.stdout.write('📋 Creando historial de acciones...')
        
        acciones_data = [
            {
                'tipo': 'ai_tool',
                'descripcion': 'AI Tool: Búsqueda de cliente "Maria"',
                'metadata': {'query': 'Maria', 'resultados': 1}
            },
            {
                'tipo': 'ai_tool',
                'descripcion': 'AI Tool: Consulta de saldo - María García López',
                'metadata': {'cliente_id': 1}
            },
            {
                'tipo': 'ai_tool',
                'descripcion': 'AI Tool: Ticket creado - Problema con factura',
                'metadata': {'ticket_id': 1}
            },
        ]
        
        historial_creado = []
        for data in acciones_data:
            fecha = timezone.now() - timedelta(
                days=random.randint(1, 7)
            )
            
            accion = HistorialAccion.objects.create(
                tipo=data['tipo'],
                descripcion=data['descripcion'],
                fecha=fecha,
                ip_address='127.0.0.1',
                metadata=data['metadata']
            )
            historial_creado.append(accion)
        
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ {len(historial_creado)} acciones de historial creadas')
        )

    def mostrar_resumen(self, clientes, tickets, pagos):
        """Mostrar resumen de datos creados"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('🎉 DATOS DE PRUEBA CREADOS EXITOSAMENTE')
        )
        self.stdout.write('='*50)
        
        self.stdout.write(f'👥 Clientes: {len(clientes)}')
        self.stdout.write(f'🎫 Tickets: {len(tickets)}')
        self.stdout.write(f'💰 Pagos: {len(pagos)}')
        
        self.stdout.write('\n📊 ESTADÍSTICAS:')
        
        # Clientes con saldo
        clientes_con_saldo = [c for c in clientes if c.saldo > 0]
        self.stdout.write(f'   💰 Clientes con saldo positivo: {len(clientes_con_saldo)}')
        
        # Total en saldos
        total_saldos = sum(c.saldo for c in clientes)
        self.stdout.write(f'   💵 Total en saldos: ${total_saldos:,.2f}')
        
        # Tickets por estado
        tickets_abiertos = len([t for t in tickets if t.estado in ['abierto', 'en_proceso']])
        self.stdout.write(f'   🎫 Tickets abiertos/en proceso: {tickets_abiertos}')
        
        # Total pagos
        total_pagos = sum(p.monto for p in pagos)
        self.stdout.write(f'   💳 Total en pagos: ${total_pagos:,.2f}')
        
        self.stdout.write('\n🚀 EJEMPLOS DE TESTING:')
        self.stdout.write('   • Buscar: "Maria" o "juan.perez@empresa.com"')
        self.stdout.write('   • Consultar saldo del cliente ID 1, 2, 3...')
        self.stdout.write('   • Crear ticket para cliente ID 1')
        self.stdout.write('   • Registrar pago para cliente ID 2')
        
        self.stdout.write('\n🌐 URLS PARA PROBAR:')
        self.stdout.write('   • http://127.0.0.1:8000/api/health/')
        self.stdout.write('   • http://127.0.0.1:8000/api/tools/buscar-cliente/?q=Maria')
        self.stdout.write('   • http://127.0.0.1:8000/api/tools/cliente/1/saldo/')
        self.stdout.write('   • http://127.0.0.1:8000/admin/ (crear superuser primero)')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('✅ ¡Listo para probar el AI Assistant!')
        )