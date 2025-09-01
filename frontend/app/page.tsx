'use client';

import { useChat } from 'ai/react';
import { useState } from 'react';

export default function AIAssistantPage() {
  const [isConnected, setIsConnected] = useState(true);
  
  const { 
    messages, 
    input, 
    handleInputChange, 
    handleSubmit, 
    isLoading, 
    error 
  } = useChat({
    api: '/api/chat',
    onError: (error) => {
      console.error('Error en chat:', error);
      setIsConnected(false);
    },
    onResponse: () => {
      setIsConnected(true);
    }
  });

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              AI Assistant - Soporte al Cliente
            </h1>
            <div className="flex items-center space-x-2 mt-1">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600">
                {isConnected ? 'Conectado' : 'Desconectado'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">í´–</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Bienvenido al AI Assistant
            </h3>
            <p className="text-gray-500 max-w-md mx-auto mb-6">
              Puedo ayudarte con tareas de soporte al cliente como buscar clientes, 
              consultar saldos, crear tickets y registrar pagos.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
              {[
                "Â¿CuÃ¡l es el saldo de MarÃ­a GarcÃ­a?",
                "Busca al cliente juan.perez@empresa.com",
                "Crea un ticket para el cliente ID 1",
                "Registra un pago de $500 para el cliente 2"
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleInputChange({ target: { value: example } } as any)}
                  className="text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-3xl p-4 rounded-lg ${
              message.role === 'user'
                ? 'bg-blue-500 text-white ml-12'
                : 'bg-white border border-gray-200 mr-12'
            }`}>
              <div className="font-medium mb-1">
                {message.role === 'user' ? 'í±¤ Usuario:' : 'í´– AI Assistant:'}
              </div>
              <div className="whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-3xl p-4 bg-gray-100 rounded-lg mr-12">
              <div className="font-medium mb-1">í´– AI Assistant:</div>
              <div>Procesando consulta...</div>
            </div>
          </div>
        )}

        {error && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-red-800">
                <strong>Error:</strong> {error.message}
              </div>
              <div className="text-red-600 text-sm mt-1">
                Verifica que el backend Django estÃ© corriendo en http://127.0.0.1:8000
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="bg-white border-t px-6 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex space-x-4">
            <input
              value={input}
              onChange={handleInputChange}
              placeholder="Escribe tu consulta aquÃ­... Ejemplo: 'Â¿CuÃ¡l es el saldo de MarÃ­a GarcÃ­a?'"
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Enviando...' : 'Enviar'}
            </button>
          </div>
          
          <div className="mt-2 text-xs text-gray-500">
            Ejemplos: "Busca MarÃ­a GarcÃ­a", "Â¿Saldo del cliente 1?", "Crea ticket para cliente 2"
          </div>
        </form>
      </div>
    </div>
  );
}
