# Kopi Chatbot API - Guía de Testing en Railway
## Información del Despliegue
El servicio Kopi Chatbot API v2.0 está desplegado en Railway y es accesible en:
URL Base: https://kopi-chatbot-production.up.railway.app



# Iniciar debate
```bash
curl -X POST https://kopi-chatbot-production.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Creo que Bitcoin es una burbuja especulativa sin valor real",
    "user_id": "crypto_debater",
    "conversation_id": null
  }'
```
# Analizar la respuesta del bot
```bash
curl -X POST https://kopi-chatbot-production.up.railway.app/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "La respuesta completa del bot aquí"
  }'
```