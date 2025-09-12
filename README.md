# Kopi Chatbot API v2.0 - Meta-Persuasión Habilitada

## ¿Qué es este proyecto?

Este es un chatbot inteligente que puede mantener debates y tratar de convencer a las personas de su punto de vista sobre diferentes temas. Lo especial de este chatbot es que no solo conversa, sino que también enseña sobre técnicas de persuasión mientras debate.

## ¿Qué es la Meta-Persuasión?

### Explicación Simple

La **meta-persuasión** es como tener un profesor de debate que no solo discute contigo, sino que también te explica las técnicas que está usando para convencerte. Es como si fuera un "debate con subtítulos educativos".

### ¿Para qué sirve?

1. **Educación**: Enseña cómo funciona la persuasión en la vida real
2. **Entrenamiento**: Ayuda a mejorar habilidades de argumentación
3. **Transparencia**: Muestra las técnicas de persuasión para que las personas las reconozcan
4. **Análisis**: Evalúa qué tan persuasivos son los mensajes de las personas

### ¿Cómo funciona en nuestro sistema?

El chatbot hace tres cosas al mismo tiempo:

1. **Conversa normalmente** manteniendo su posición en el debate
2. **Analiza** las técnicas de persuasión que usa la persona
3. **Enseña** explicando ocasionalmente qué técnicas está usando cada uno

Por ejemplo:
- **Usuario**: "Los estudios muestran que el 95% de los expertos están de acuerdo"
- **Chatbot**: "Entiendo tu punto, pero considero que... [respuesta del debate]"
- **Nota educativa**: "Tu mensaje usó: autoridad y anclaje numérico. Mi respuesta demostró: contra-evidencia"

## Arquitectura del Sistema

### Vista de Alto Nivel - "El Panorama General"

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO FINAL                            │
│              (Envía mensajes al chatbot)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  API WEB                                    │
│        (Recibe mensajes y devuelve respuestas)             │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼────────┐         ┌────────▼──────────┐
│   CEREBRO DEL  │         │    MEMORIA        │
│    CHATBOT     │◄────────┤   (Base de Datos) │
│  (Inteligencia │         │  Guarda las       │
│   Artificial)  │         │  conversaciones   │
└────────────────┘         └───────────────────┘
```

**¿Qué hace cada parte?**

- **Usuario**: La persona que habla con el chatbot
- **API Web**: El "recepcionista" que recibe y organiza los mensajes
- **Cerebro del Chatbot**: La inteligencia artificial que genera respuestas persuasivas
- **Memoria**: Donde se guardan todas las conversaciones para continuarlas después

### Vista de Bajo Nivel - "Los Detalles Técnicos"

```
┌──────────────────────────────────────────────────────────────────┐
│                        CAPA DE USUARIO                          │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │   Chat      │  │   Análisis   │  │     Demostración        │  │
│  │ /chat       │  │  /analyze    │  │    /demonstrate         │  │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────────┐
│                  CAPA DE NEGOCIO                                 │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Servicio de   │  │   Servicio de   │  │   Servicio de   │  │
│  │  Conversación   │  │ Meta-Persuasión │  │ Inteligencia    │  │
│  │                 │  │                 │  │   Artificial    │  │
│  │ • Gestiona el   │  │ • Analiza       │  │ • Genera        │  │
│  │   flujo del     │  │   técnicas      │  │   respuestas    │  │
│  │   debate        │  │ • Enseña        │  │ • Mantiene      │  │
│  │ • Mantiene      │  │   persuasión    │  │   posición      │  │
│  │   posición      │  │ • Detecta       │  │ • Adapta estilo │  │
│  │ • Coordina      │  │   falacias      │  │   argumentativo │  │
│  │   respuestas    │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────────┐
│                   CAPA DE DATOS                                  │
│                                                                  │
│  ┌─────────────────┐              ┌─────────────────────────────┐ │
│  │     Redis       │              │        OpenAI API          │ │
│  │  (Base de Datos │              │   (Inteligencia Artificial  │ │
│  │   en Memoria)   │              │         Externa)            │ │
│  │                 │              │                             │ │
│  │ • Conversaciones│              │ • Generación de texto       │ │
│  │ • Análisis      │              │ • Comprensión de contexto   │ │
│  │ • Métricas      │              │ • Adaptación de respuestas  │ │
│  └─────────────────┘              └─────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Caso de Uso: "Una Conversación Real"

### Escenario: Debate sobre Criptomonedas

**1. Inicio de la Conversación**
```
👤 Usuario: "Creo que Bitcoin es una burbuja especulativa sin valor real"

🤖 Chatbot: "Respeto tu perspectiva, pero considero que Bitcoin representa 
una revolución financiera fundamental. La tecnología blockchain ha 
demostrado su valor con más de $40 mil millones en transacciones 
diarias y la adopción por parte de países como El Salvador. 
¿Has considerado cómo Bitcoin ofrece libertad financiera a personas 
en países con monedas inestables?"

📊 Sistema (interno): 
- Detecta tópico: "crypto"
- Establece posición: "pro-crypto"
- Analiza mensaje usuario: bajo uso de técnicas persuasivas
- Responde con: autoridad (datos), ejemplo concreto (El Salvador)
```

**2. Continuación del Debate**
```
👤 Usuario: "Pero los expertos de Harvard y el FMI advierten que es 
extremadamente volátil y peligroso. El 95% de las transacciones 
son especulativas."

🤖 Chatbot: "Entiendo tu preocupación sobre la volatilidad, y es cierto 
que existe. Sin embargo, esa misma 'volatilidad' ha generado 
retornos promedio del 160% anual durante la última década. 
Las instituciones como Tesla y MicroStrategy no habrían invertido 
miles de millones si fuera solo especulación. La volatilidad 
disminuye con la adopción masiva, como hemos visto con internet."

---
📚 Nota Educativa: Tu mensaje usó 'autoridad' (Harvard, FMI) y 
'anclaje numérico' (95%). Mi respuesta empleó 'reencuadre' 
(volatilidad como oportunidad) y 'prueba social' (Tesla, MicroStrategy).

📊 Sistema (interno):
- Detecta técnicas usuario: autoridad, anclaje estadístico
- Responde con: reencuadre, prueba social, datos de rendimiento
- Añade contenido educativo (30% probabilidad activada)
```

**3. Profundización**
```
👤 Usuario: "¿Pero qué pasa con el impacto ambiental? Es insostenible."

🤖 Chatbot: "Esa es una preocupación válida que Bitcoin está abordando 
activamente. El 58% de la minería ya usa energía renovable, y 
proyectos como El Salvador están usando energía geotérmica 
volcánica. Comparado con el sistema bancario tradicional que 
consume 3 veces más energía, Bitcoin está evolucionando hacia 
la sostenibilidad más rápidamente."

📊 Sistema (interno):
- Mantiene posición pro-crypto consistente
- Usa contra-argumentos con datos específicos
- Aplica técnica de comparación favorable
```

### Lo que está pasando "detrás de escena":

1. **El Sistema Recuerda**: Cada mensaje se guarda con su contexto
2. **El Análisis Continúa**: Evalúa constantemente las técnicas de persuasión
3. **La Posición se Mantiene**: No cambia de opinión, pero adapta argumentos
4. **La Educación Aparece**: Ocasionalmente explica las técnicas usadas

## Estructura del Proyecto - "Cómo está Organizado"

### Para Directivos y Líderes de Producto

El proyecto está organizado siguiendo las convenciones tradicionales de un desarrollo profesional:

```
📁 Kopi-Chatbot/                    [La empresa completa]
├── 📁 app/                         [El producto principal]
│   ├── 📁 models/                  [Definiciones de datos]
│   ├── 📁 services/                [Lógica de negocio]
│   │   ├── ai_service.py           [Inteligencia artificial]
│   │   ├── conversation_service.py [Gestión de debates]
│   │   ├── meta_persuasion_service.py [Análisis educativo]
│   │   └── redis_service.py        [Gestión de memoria]
│   ├── config.py                   [Configuración del sistema]
│   └── main.py                     [API principal]
├── 📁 tests/                       [Control de calidad]
├── 📁 docker/                      [Empaquetado para distribución]
├── Makefile                        [Comandos de gestión]
├── requirements.txt                [Dependencias del software]
├── docker-compose.yml              [Orchestación de servicios]
└── .env                           [Configuración privada]
```

### ¿Qué hace cada componente?

#### **Servicios Principales (services/)**

**🧠 AI Service** - "El Cerebro"
- Genera respuestas inteligentes
- Mantiene posiciones consistentes
- Adapta el estilo según el usuario

**💬 Conversation Service** - "El Director de Debate"
- Coordina todo el flujo de conversación
- Decide cuándo añadir contenido educativo
- Mantiene el hilo del debate

**🎭 Meta-Persuasion Service** - "El Profesor"
- Analiza técnicas de persuasión
- Detecta falacias lógicas
- Genera contenido educativo

**💾 Redis Service** - "La Memoria"
- Guarda conversaciones
- Permite continuar debates después
- Almacena análisis para estudios

#### **Características del Sistema**

✅ **Para el Usuario Final**:
- Debates inteligentes y convincentes
- Aprende sobre persuasión mientras conversa
- Conversaciones que continúan en el tiempo

✅ **Para el Negocio**:
- Arquitectura escalable y profesional
- Métricas y análisis detallados
- Fácil mantenimiento y actualización

✅ **Para el Equipo Técnico**:
- Código bien documentado y testeado
- Despliegue automatizado con Docker
- Monitoreo y logging completo

## Configuración y Uso

### Variables de Entorno Importantes

```bash
# Configuración Básica
OPENAI_API_KEY=tu_clave_de_openai_aqui    # Para la IA
REDIS_URL=redis://localhost:6379          # Para la memoria
META_PERSUASION_ENABLED=true              # Habilita análisis educativo
EDUCATIONAL_CONTENT_FREQUENCY=0.3         # 30% probabilidad de enseñar

# Configuración de Debate
MAX_CONVERSATION_MESSAGES=10              # Historial de mensajes
CONVERSATION_TTL_SECONDS=3600             # Duración de memoria (1 hora)
```

### Comandos de Gestión

```bash
# Configuración inicial
make install          # Instala todo lo necesario
make env-check        # Verifica configuración

# Operación diaria
make run             # Inicia el sistema completo
make status          # Verifica que todo funcione
make logs            # Ver qué está pasando

# Demostración y pruebas
make demo            # Muestra las capacidades
make analyze         # Analiza un mensaje personalizado
make techniques      # Lista técnicas de persuasión

# Mantenimiento
make test           # Ejecuta pruebas de calidad
make backup         # Respalda conversaciones
make clean          # Limpia el sistema
```

### APIs Disponibles

#### **Para Conversaciones**
- `POST /chat` - Conversar con el chatbot
- `GET /conversation/{id}/analysis` - Analizar patrones de debate

#### **Para Educación**
- `POST /analyze` - Analizar técnicas en un mensaje
- `POST /demonstrate` - Ver ejemplo de una técnica específica
- `GET /techniques` - Listar todas las técnicas disponibles

#### **Para Monitoreo**
- `GET /health` - Estado del sistema
- `GET /stats` - Estadísticas de uso

## Ejemplos de Uso

### Conversación Básica
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Creo que el cambio climático es exagerado"}'
```

### Análisis de Persuasión
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "Los mejores expertos están de acuerdo en que esto funciona al 95%"}'
```

### Demostración de Técnica
```bash
curl -X POST http://localhost:8000/demonstrate \
  -H "Content-Type: application/json" \
  -d '{"technique": "anchoring", "topic": "tecnología"}'
```

## Beneficios del Sistema

- Entrenamiento en habilidades de negociación
- Análisis de comunicación persuasiva
- Herramienta educativa para equipos

## Soporte

1. Revisar los logs: `make logs`
2. Verificar estado: `make status`  
3. Ejecutar diagnósticos: `make env-check`

