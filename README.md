# 🤖 AI Assistant - Sistema de Soporte al Cliente

Un asistente de inteligencia artificial integrado con Django que permite gestionar clientes, tickets de soporte y pagos mediante herramientas (tool calling) en lenguaje natural.

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema completo de soporte al cliente que combina:

- **Backend Django**: API REST con endpoints optimizados para AI tool calling
- **Frontend Next.js**: Interfaz de chat con streaming en tiempo real
- **AI Integration**: OpenAI GPT-4 con capacidades de tool calling
- **Base de datos**: SQLite con modelos relacionales para clientes, tickets y pagos

### Funcionalidades Principales

- **Buscar clientes** por nombre o email
- **Consultar saldos** de clientes específicos
- **Crear tickets** de soporte con diferentes prioridades
- **Registrar pagos** y actualizar saldos automáticamente
- **Obtener estadísticas** del sistema
- **Interfaz conversacional** en lenguaje natural
- **Streaming de respuestas** en tiempo real
- **Panel administrativo** completo (Django Admin)

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                  USUARIO FINAL                          │
└─────────────────────┬───────────────────────────────────┘
                      │ (Lenguaje natural)
                      ▼
┌─────────────────────────────────────────────────────────┐
│               FRONTEND (Next.js)                        │
│  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │   Chat UI       │  │     Vercel AI SDK           │   │
│  │   Component     │  │     (useChat hook)          │   │
│  └─────────────────┘  └─────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │ (HTTP/JSON + Tool Calls)
                      ▼
┌─────────────────────────────────────────────────────────┐
│            AI MODEL (OpenAI GPT-4o)                     │
│  ┌─────────────────────────────────────────────────────┐│
│  │  🤖 AI Tool Calling Engine                         ││
│  │  • Analiza intención del usuario                    ││
│  │  • Decide qué herramientas usar                     ││
│  │  • Extrae parámetros automáticamente                ││
│  │  • Orquesta múltiples llamadas si es necesario      ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────┬───────────────────────────────────┘
                      │ (Function calls)
                      ▼
┌─────────────────────────────────────────────────────────┐
│              BACKEND API (Django)                       │
│                                                         │
│  🛠️ AI TOOL ENDPOINTS                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │buscarCliente│ │consultarSaldo│ │  crearTicket    │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │registrarPago│ │ estadísticas│ │  health_check   │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
│                                                         │
│  📊 BUSINESS LOGIC                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │    Views    │ │ Serializers │ │    Validators   │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
│                                                         │
│  🗃️ DATA MODELS                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │   Cliente   │ │   Ticket    │ │      Pago       │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │ (SQL)
                      ▼
┌─────────────────────────────────────────────────────────┐
│               DATABASE (SQLite)                         │
│  Tablas: Cliente, Ticket, Pago, HistorialAccion        │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.5**: Framework web principal
- **Django REST Framework 3.16.1**: API REST
- **django-cors-headers 4.7.0**: Configuración CORS
- **python-decouple 3.8**: Variables de entorno
- **SQLite**: Base de datos (desarrollo)

### Frontend
- **Next.js 15.5.2**: Framework React
- **TypeScript**: Tipado estático
- **Tailwind CSS 4**: Estilos
- **Vercel AI SDK 5.0.29**: Integración con IA
- **@ai-sdk/openai 2.0.23**: Cliente OpenAI
- **Zod 3.25.76**: Validación de esquemas
- **Lucide React 0.542.0**: Iconos

### AI Integration
- **OpenAI GPT-4o**: Modelo de lenguaje
- **Tool Calling**: Capacidad de usar herramientas
- **Streaming**: Respuestas en tiempo real

## 📋 Requisitos del Sistema

### Software Base
- **Python 3.10+**: Para Django backend
- **Node.js 18+**: Para Next.js frontend
- **npm**: Gestor de paquetes
- **Git**: Control de versiones

### Servicios Externos
- **OpenAI API Key**: Cuenta activa en OpenAI
- **Conexión a Internet**: Para llamadas a OpenAI API

### Sistema Operativo
- Windows 10/11, macOS, Linux
- Terminal/PowerShell/Bash

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd ai-assistant-project
```

### 2. Configurar Backend (Django)

```bash
# Ir al directorio backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python manage.py makemigrations customer_support
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Crear datos de prueba
python manage.py crear_datos_prueba --limpiar

# Ejecutar servidor
python manage.py runserver
```

### 3. Configurar Frontend (Next.js)

```bash
# En nueva terminal, ir al directorio frontend
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tu OpenAI API key
```

#### Configuración de Variables de Entorno (.env.local):

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-tu_api_key_aqui
OPENAI_MODEL=gpt-4o

# Backend URL
NEXT_PUBLIC_DJANGO_API_URL=http://127.0.0.1:8000/api

# App Configuration
NEXT_PUBLIC_APP_NAME=AI Assistant
NEXT_PUBLIC_APP_VERSION=1.0.0
```

```bash
# Ejecutar servidor de desarrollo
npm run dev
```

### 4. Obtener OpenAI API Key

1. Crear cuenta en [OpenAI Platform](https://platform.openai.com)
2. Ir a [API Keys](https://platform.openai.com/api-keys)
3. Crear nueva API key
4. Copiar la key a `.env.local`

## 🎯 Uso del Sistema

### Acceso a las Aplicaciones

- **Frontend (Chat)**: http://localhost:3000
- **Django Admin**: http://127.0.0.1:8000/admin/
- **API Health Check**: http://127.0.0.1:8000/api/health/

### Ejemplos de Consultas

#### Buscar Clientes
```
"Busca a María García"
"¿Puedes encontrar al cliente juan.perez@empresa.com?"
"Encuentra información de Ana Rodríguez"
```

#### Consultar Saldos
```
"¿Cuál es el saldo de María García López?"
"Consulta el saldo del cliente ID 1"
"Muéstrame el balance del cliente 2"
"Busca a María García y dime su saldo"
```

#### Crear Tickets
```
"Crea un ticket para el cliente ID 1 sobre problema de facturación"
"El cliente 2 tiene problemas con su cuenta, crea un ticket urgente"
"Crear ticket para María García: no puede acceder a su cuenta"
```

#### Registrar Pagos
```
"Registra un pago de $500 para el cliente 2"
"El cliente ID 1 pagó $300 por transferencia bancaria"
"María García hizo un pago de $150 en efectivo"
```

#### Estadísticas del Sistema
```
"Muéstrame las estadísticas del sistema"
"¿Cuántos clientes hay en total?"
"¿Cuántos tickets están abiertos?"
```

## 📁 Estructura del Proyecto

```
ai-assistant-project/
├── backend/                        # Django Backend
│   ├── ai_assistant/               # Configuración del proyecto
│   │   ├── __init__.py
│   │   ├── settings.py            # Configuración principal
│   │   ├── urls.py                # URLs principales
│   │   ├── wsgi.py                # WSGI config
│   │   └── asgi.py                # ASGI config
│   │
│   ├── customer_support/           # App principal
│   │   ├── __init__.py
│   │   ├── models.py              # Modelos de datos
│   │   ├── views.py               # Endpoints API
│   │   ├── serializers.py         # Serialización JSON
│   │   ├── urls.py                # URLs de la app
│   │   ├── admin.py               # Django Admin config
│   │   ├── apps.py                # Configuración de la app
│   │   ├── migrations/            # Migraciones DB
│   │   └── management/            # Comandos personalizados
│   │       └── commands/
│   │           └── crear_datos_prueba.py
│   │
│   ├── manage.py                  # Script Django principal
│   ├── requirements.txt           # Dependencias Python
│   └── db.sqlite3                 # Base de datos
│
├── frontend/                      # Next.js Frontend
│   ├── app/                       # App Router (Next.js 13+)
│   │   ├── api/chat/              # API Routes
│   │   │   └── route.ts           # AI Tool Calling endpoint
│   │   ├── globals.css            # Estilos globales
│   │   ├── layout.tsx             # Layout principal
│   │   └── page.tsx               # Página principal (Chat)
│   │
│   ├── types/                     # Tipos TypeScript
│   │   └── index.ts
│   │
│   ├── .env.local                 # Variables de entorno
│   ├── package.json               # Dependencias Node.js
│   ├── tailwind.config.js         # Configuración Tailwind
│   ├── tsconfig.json              # Configuración TypeScript
│   └── next.config.js             # Configuración Next.js
│
└── README.md                      # Este archivo
```

## 🔌 API Endpoints

### AI Tool Endpoints (Optimizados para IA)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/tools/buscar-cliente/` | GET | Buscar cliente por nombre o email |
| `/api/tools/cliente/{id}/saldo/` | GET | Consultar saldo de cliente específico |
| `/api/tools/crear-ticket/` | POST | Crear ticket de soporte |
| `/api/tools/registrar-pago/` | POST | Registrar pago y actualizar saldo |
| `/api/dashboard/estadisticas/` | GET | Obtener estadísticas del sistema |
| `/api/health/` | GET | Health check del API |

### CRUD Completo (Administración)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/clientes/` | GET/POST | Listar/crear clientes |
| `/api/clientes/{id}/` | GET/PUT/DELETE | CRUD cliente específico |
| `/api/tickets/` | GET/POST | Listar/crear tickets |
| `/api/tickets/{id}/` | GET/PUT/DELETE | CRUD ticket específico |
| `/api/pagos/` | GET/POST | Listar/crear pagos |
| `/api/pagos/{id}/` | GET/PUT/DELETE | CRUD pago específico |

### Ejemplos de Uso de API

#### Buscar Cliente
```bash
curl "http://127.0.0.1:8000/api/tools/buscar-cliente/?q=Maria"
```

#### Consultar Saldo
```bash
curl "http://127.0.0.1:8000/api/tools/cliente/1/saldo/"
```

#### Crear Ticket
```bash
curl -X POST http://127.0.0.1:8000/api/tools/crear-ticket/ \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": 1,
    "titulo": "Problema con factura",
    "descripcion": "No puedo acceder a mi factura"
  }'
```

#### Registrar Pago
```bash
curl -X POST http://127.0.0.1:8000/api/tools/registrar-pago/ \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": 1,
    "monto": 250.50,
    "descripcion": "Pago de factura mensual"
  }'
```

## 🔍 Modelos de Datos

### Cliente
- `nombre`: Nombre completo del cliente
- `email`: Email único del cliente
- `telefono`: Teléfono de contacto (opcional)
- `saldo`: Saldo actual del cliente
- `fecha_registro`: Fecha de registro en el sistema
- `activo`: Estado del cliente (activo/inactivo)

### Ticket
- `cliente`: Relación con Cliente
- `titulo`: Título del problema
- `descripcion`: Descripción detallada
- `estado`: abierto, en_proceso, pendiente, resuelto, cerrado
- `prioridad`: baja, media, alta, critica
- `asignado_a`: Usuario asignado (opcional)
- `fecha_creacion`: Fecha de creación
- `fecha_resolucion`: Fecha de resolución (opcional)

### Pago
- `cliente`: Relación con Cliente
- `monto`: Cantidad del pago
- `descripcion`: Concepto del pago
- `metodo_pago`: efectivo, tarjeta, transferencia, cheque
- `fecha`: Fecha del pago
- `procesado_por`: Usuario que procesó (opcional)

### HistorialAccion (Auditoría)
- `tipo`: Tipo de acción (consulta, creacion, pago, ai_tool)
- `descripcion`: Descripción de la acción
- `cliente`: Cliente relacionado (opcional)
- `usuario`: Usuario que realizó la acción
- `ip_address`: IP desde donde se realizó
- `metadata`: Datos adicionales en JSON
- `fecha`: Timestamp de la acción

## 🧪 Testing y Desarrollo

### Ejecutar Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests (si están configurados)
cd frontend
npm test
```

### Datos de Prueba
El sistema incluye un comando para crear datos de prueba:

```bash
cd backend
python manage.py crear_datos_prueba --limpiar
```

Esto crea:
- 6 clientes con diferentes saldos
- 4 tickets en varios estados
- 17 pagos distribuidos entre clientes
- 3 acciones de historial para auditoría

### Modo de Desarrollo
- Backend en modo DEBUG (configurado en settings.py)
- Frontend con recarga en caliente (Next.js dev mode)
- CORS configurado para desarrollo local

## ❗ Troubleshooting

### Problemas Comunes

#### Error: "No module named 'customer_support'"
```bash
# Verificar que existe __init__.py
touch backend/customer_support/__init__.py
```

#### Error: "OPENAI_API_KEY not found"
```bash
# Verificar archivo .env.local en frontend/
cat frontend/.env.local
# Reiniciar servidor Next.js
```

#### Error: "Connection refused" al backend
```bash
# Verificar que Django está corriendo
curl http://127.0.0.1:8000/api/health/
```

#### Error: "toAIStreamResponse is not a function"
- Ya resuelto en la versión actual usando `toDataStreamResponse()`

#### Base de datos corrupta
```bash
# Recrear base de datos
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py crear_datos_prueba --limpiar
```

### Logs y Debugging

#### Backend (Django)
- Logs en consola donde ejecutas `python manage.py runserver`
- Archivo `debug.log` en directorio backend/
- Django Admin para inspeccionar datos

#### Frontend (Next.js)
- Consola del navegador (F12 > Console)
- Terminal donde ejecutas `npm run dev`
- Network tab para inspeccionar requests

## 🚀 Despliegue en Producción

### Backend (Django)
1. Configurar variables de entorno de producción
2. Usar PostgreSQL en lugar de SQLite
3. Configurar servidor web (Nginx + Gunicorn)
4. SSL/HTTPS obligatorio

### Frontend (Next.js)
1. Build de producción: `npm run build`
2. Desplegar en Vercel, Netlify, o servidor propio
3. Configurar variables de entorno de producción

### Consideraciones de Seguridad
- API Keys en variables de entorno
- CORS restrictivo en producción
- Rate limiting para API
- Autenticación/autorización según necesidades

## 🤝 Contribución

### Desarrollo Local
1. Fork del repositorio
2. Crear rama para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit changes: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código
- Python: PEP 8
- TypeScript: ESLint config
- Commits: Conventional Commits format

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

Desarrollado como prueba técnica para demostrar integración de:
- Django REST Framework
- Next.js + TypeScript
- OpenAI GPT-4 Tool Calling
- Arquitectura de microservicios

## 📞 Soporte

Para reportar bugs o solicitar features:
1. Crear issue en GitHub
2. Incluir logs relevantes
3. Describir pasos para reproducir el problema

---

## 🎉 ¡Listo para usar!

Con esta configuración tienes un sistema completo de AI Assistant que puede:
- Procesar consultas en lenguaje natural
- Ejecutar acciones reales en base de datos
- Proporcionar respuestas contextuales
- Mantener historial de auditoría
- Escalar para casos de uso reales

**URLs principales:**
- **Chat AI**: http://localhost:3000
- **Django Admin**: http://127.0.0.1:8000/admin/