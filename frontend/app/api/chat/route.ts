import { openai } from '@ai-sdk/openai';
import { streamText, tool } from 'ai';
import { z } from 'zod';

const DJANGO_API_URL = process.env.NEXT_PUBLIC_DJANGO_API_URL;

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();

    const result = await streamText({
      model: openai('gpt-4o'),
      messages,
      tools: {
        buscarCliente: tool({
          description: 'Buscar cliente en el sistema por nombre o email',
          parameters: z.object({
            query: z.string().describe('Nombre o email del cliente a buscar'),
          }),
          execute: async ({ query }) => {
            try {
              const response = await fetch(
                `${DJANGO_API_URL}/tools/buscar-cliente/?q=${encodeURIComponent(query)}`
              );
              
              if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
              }
              
              const data = await response.json();
              return {
                success: true,
                message: data.message || 'Búsqueda completada',
                clientes: data.clientes || [],
                total: data.total || 0
              };
            } catch (error) {
              console.error('Error en buscarCliente:', error);
              return {
                success: false,
                error: 'No se pudo conectar con el sistema de clientes',
                message: error instanceof Error ? error.message : 'Error desconocido'
              };
            }
          },
        }),

        consultarSaldo: tool({
          description: 'Consultar el saldo actual de un cliente por su ID',
          parameters: z.object({
            clienteId: z.number().describe('ID numérico del cliente'),
          }),
          execute: async ({ clienteId }) => {
            try {
              const response = await fetch(
                `${DJANGO_API_URL}/tools/cliente/${clienteId}/saldo/`
              );
              
              if (!response.ok) {
                if (response.status === 404) {
                  return {
                    success: false,
                    error: 'Cliente no encontrado',
                    message: `No existe cliente con ID ${clienteId}`
                  };
                }
                throw new Error(`Error ${response.status}: ${response.statusText}`);
              }
              
              const data = await response.json();
              return {
                success: true,
                cliente: data.cliente,
                ultimos_pagos: data.ultimos_pagos || [],
                resumen: data.resumen || {}
              };
            } catch (error) {
              console.error('Error en consultarSaldo:', error);
              return {
                success: false,
                error: 'No se pudo consultar el saldo',
                message: error instanceof Error ? error.message : 'Error desconocido'
              };
            }
          },
        }),

        crearTicket: tool({
          description: 'Crear un nuevo ticket de soporte para un cliente',
          parameters: z.object({
            clienteId: z.number().describe('ID del cliente'),
            titulo: z.string().describe('Título del problema'),
            descripcion: z.string().describe('Descripción detallada del problema'),
            prioridad: z.enum(['baja', 'media', 'alta', 'critica']).optional().describe('Prioridad del ticket'),
          }),
          execute: async ({ clienteId, titulo, descripcion, prioridad = 'media' }) => {
            try {
              const response = await fetch(`${DJANGO_API_URL}/tools/crear-ticket/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  cliente: clienteId,
                  titulo,
                  descripcion,
                  prioridad,
                }),
              });
              
              if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                return {
                  success: false,
                  error: errorData?.error || 'Error al crear ticket',
                  message: errorData?.message || `Error ${response.status}`
                };
              }
              
              const data = await response.json();
              return {
                success: true,
                mensaje: data.mensaje,
                ticket: data.ticket,
                instrucciones: data.instrucciones
              };
            } catch (error) {
              console.error('Error en crearTicket:', error);
              return {
                success: false,
                error: 'No se pudo crear el ticket',
                message: error instanceof Error ? error.message : 'Error desconocido'
              };
            }
          },
        }),

        registrarPago: tool({
          description: 'Registrar un pago de cliente y actualizar su saldo',
          parameters: z.object({
            clienteId: z.number().describe('ID del cliente que realiza el pago'),
            monto: z.number().positive().describe('Monto del pago (debe ser positivo)'),
            descripcion: z.string().optional().describe('Descripción o concepto del pago'),
            metodoPago: z.enum(['efectivo', 'tarjeta', 'transferencia', 'cheque']).optional().describe('Método de pago'),
          }),
          execute: async ({ clienteId, monto, descripcion = 'Pago registrado', metodoPago = 'transferencia' }) => {
            try {
              const response = await fetch(`${DJANGO_API_URL}/tools/registrar-pago/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  cliente: clienteId,
                  monto,
                  descripcion,
                  metodo_pago: metodoPago,
                }),
              });
              
              if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                return {
                  success: false,
                  error: errorData?.error || 'Error al registrar pago',
                  message: errorData?.message || `Error ${response.status}`
                };
              }
              
              const data = await response.json();
              return {
                success: true,
                mensaje: data.mensaje,
                pago: data.pago,
                saldos: data.saldos,
                confirmacion: data.confirmacion
              };
            } catch (error) {
              console.error('Error en registrarPago:', error);
              return {
                success: false,
                error: 'No se pudo registrar el pago',
                message: error instanceof Error ? error.message : 'Error desconocido'
              };
            }
          },
        }),
      },
      maxTokens: 1000,
      temperature: 0.3,
    });

    // Usar toDataStreamResponse() en lugar de toAIStreamResponse()
    return result.toDataStreamResponse();
    
  } catch (error) {
    console.error('Error en POST /api/chat:', error);
    
    return new Response(
      JSON.stringify({
        error: 'Error interno del servidor',
        message: error instanceof Error ? error.message : 'Error desconocido'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
