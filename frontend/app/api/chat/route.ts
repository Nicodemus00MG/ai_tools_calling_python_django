import { streamText } from 'ai'; // ← Cambia a streamText
import { google } from '@ai-sdk/google';

const DJANGO_API_URL = 'http://127.0.0.1:8000/api';

async function fetchFromDjango(endpoint: string) {
  try {
    const response = await fetch(`${DJANGO_API_URL}${endpoint}`, {
      cache: 'no-store'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    return null;
  }
}

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    const ultimoMensaje = messages[messages.length - 1]?.content || '';
    let datosReales = '';

    // CONSULTAR CLIENTES por nombre
    if (ultimoMensaje.includes('maría') || ultimoMensaje.includes('María') || ultimoMensaje.includes('garcía') || ultimoMensaje.includes('García')) {
      const clientesData = await fetchFromDjango('/clientes/');
      if (clientesData && clientesData.results) {
        const maria = clientesData.results.find((cliente: any) => 
          cliente.nombre.toLowerCase().includes('maría') || cliente.nombre.toLowerCase().includes('garcía')
        );
        
        if (maria) {
          datosReales = `CLIENTE: ${maria.nombre}, EMAIL: ${maria.email}, TELÉFONO: ${maria.telefono}, SALDO: ${maria.saldo_formateado}, ÚLTIMO PAGO: ${maria.ultimo_pago?.monto || 'N/A'} (${maria.ultimo_pago?.descripcion || 'Sin pagos'})`;
        } else {
          datosReales = 'Cliente María García no encontrado en el sistema';
        }
      } else {
        datosReales = 'Error al conectar con la base de datos de clientes';
      }
    }

    // CONSULTAR SALDO de cualquier cliente
    else if (ultimoMensaje.includes('saldo')) {
      const clientesData = await fetchFromDjango('/clientes/');
      if (clientesData && clientesData.results) {
        const clientesInfo = clientesData.results.map((cliente: any) => 
          `${cliente.nombre}: ${cliente.saldo_formateado}`
        ).join('; ');
        datosReales = `SALDOS ACTUALES: ${clientesInfo}`;
      } else {
        datosReales = 'No se pudieron obtener los saldos';
      }
    }

    // Si no hay datos específicos, usar mensaje genérico
    if (!datosReales) {
      datosReales = 'Sistema de gestión de clientes conectado. Puedo consultar saldos, tickets y pagos.';
    }

    const gemini = google('gemini-1.5-flash');

    // USAR streamText EN LUGAR DE generateText
    const result = streamText({
      model: gemini,
      system: `Eres un asistente de soporte técnico conectado al sistema Django.
               DATOS REALES DEL SISTEMA: ${datosReales}
               Responde de manera profesional y útil en español.`,
      messages,
    });

    return result.toDataStreamResponse();

  } catch (error) {
    console.error('Error en API chat:', error);
    return new Response(
      JSON.stringify({ error: 'Error interno del servidor' }), 
      { status: 500 }
    );
  }
}