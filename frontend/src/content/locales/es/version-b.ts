import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'Memoria a Largo Plazo con IA para Claude, ChatGPT y Cursor | Interview Assistant MCP',
    description:
      'Dale a cualquier asistente de IA una memoria estructurada a largo plazo. Las entrevistas activas extraen conocimiento profundo. El servidor MCP funciona con Claude Desktop, ChatGPT, Cursor y más.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline:
      'Dale a CUALQUIER Asistente de IA Memoria Estructurada a Largo Plazo',
    subheadline:
      'No es otro volcado pasivo de memoria. Las entrevistas activas extraen conocimiento profundo y estructurado. Tu IA realmente entiende tu contexto.',
    cta: 'Únete al Acceso Anticipado',
    socialProof: 'Funciona con Claude, ChatGPT, Cursor, Windsurf y más',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'La Memoria de la IA No Debe Ser Pasiva',
    items: [
      {
        title: 'Captura superficial',
        description:
          'Herramientas como Mem0 registran fragmentos de forma pasiva. Obtienes "el usuario prefiere Python" y no "lideró la migración de 500K LOC de código Java a Python, reduciendo el tiempo de despliegue un 60%."',
        icon: 'layers',
      },
      {
        title: 'Sin estructura',
        description:
          'Los grafos de conocimiento capturan entidades y relaciones pero pierden la narrativa. Contexto sin historia es solo ruido.',
        icon: 'grid',
      },
      {
        title: 'Te repites',
        description:
          'Cada conversación con Claude empieza desde cero. Copia y pega el mismo contexto. Cada. Maldita. Vez.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Entrevistas Activas > Captura Pasiva',
    description:
      'Otras herramientas de memoria observan lo que haces y almacenan fragmentos pasivamente.\n\nNosotros te entrevistamos. Sistemáticamente. Como un periodista construyendo un perfil — haciendo preguntas de seguimiento, profundizando, rastreando lo que se ha cubierto y lo que no.\n\nEl resultado: conocimiento estructurado y completo que la IA puede realmente USAR, no solo recuperar.',
    before: {
      label: 'Mem0 almacena',
      text: 'el usuario sabe Python',
    },
    after: {
      label: 'Nosotros almacenamos',
      text: 'Lideró la migración a Python en Acme Corp (2023). Convertimos un monolito Java de 500K LOC a microservicios Python. Equipo de 8. Reducción del tiempo de despliegue en 60%. Eligió FastAPI sobre Django para cargas asíncronas.',
    },
    closing: 'Esa es la diferencia entre memoria y comprensión.',
  },

  howItWorks: {
    heading: 'Cómo Funciona',
    steps: [
      {
        number: 1,
        title: 'Entrevistas Estructuradas',
        description:
          'Conversaciones rápidas por Telegram que cubren sistemáticamente tu conocimiento. La IA rastrea la cobertura — sabe qué ha preguntado y qué no. Profundización progresiva, no fragmentos aleatorios.',
      },
      {
        number: 2,
        title: 'Extracción de Conocimiento',
        description:
          'La IA extrae resúmenes estructurados con embeddings semánticos. Organizados por áreas de la vida, buscables por significado, no solo por palabras clave.',
      },
      {
        number: 3,
        title: 'Integración MCP',
        description:
          'Servidor MCP estándar que funciona con Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code y cualquier IA compatible con MCP. Autenticación con Bearer token. Configuración en 5 minutos.',
      },
    ],
    bonus: {
      title: 'Próximamente: Apps MCP',
      description:
        'Panel interactivo de conocimiento renderizado directamente dentro de Claude y ChatGPT vía la nueva extensión MCP Apps.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Para Desarrolladores',
        items: [
          'La IA recuerda tu stack tecnológico, decisiones arquitectónicas y patrones de código',
          'Referencia proyectos pasados en cualquier conversación',
          'Genera ejemplos de código usando TUS patrones reales',
          'Nunca vuelvas a explicar la configuración de tu código',
        ],
      },
      {
        title: 'Para Consultores',
        items: [
          'La IA recuerda detalles de clientes, metodologías y proyectos anteriores',
          'Escribe propuestas basadas en experiencia real',
          'Nunca repitas información de contexto otra vez',
          'Construye sobre conversaciones previas automáticamente',
        ],
      },
      {
        title: 'Para Todos',
        items: [
          'Cartas de presentación basadas en logros reales',
          'Preparación para entrevistas con IA que conoce tu historia',
          'Currículum profesional generado automáticamente desde tu conocimiento',
          'Tus datos, siempre exportables',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Precios Simples. Sin Sorpresas.',
    tiers: [
      {
        name: 'Gratis',
        price: null,
        priceLabel: 'Gratis',
        description:
          '1 sesión de entrevista + demo de búsqueda de conocimiento.',
        features: [
          '1 sesión de entrevista',
          'Demo de búsqueda de conocimiento',
        ],
        cta: 'Pruébalo Gratis',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/mes',
        description:
          'Acceso completo a entrevistas, servidor MCP y generación de CV.',
        features: [
          'Entrevistas ilimitadas + extracción de conocimiento',
          'Acceso al servidor MCP (autenticación Bearer token)',
          'Búsqueda semántica en todo tu conocimiento',
          'Generación de CV incluida',
          'Funciona con Claude, ChatGPT, Cursor, Windsurf',
        ],
        cta: 'Únete al Acceso Anticipado',
        highlighted: true,
        badge: 'Más Popular',
      },
      {
        name: 'Autoalojado',
        price: 59,
        priceLabel: '$59/mes',
        description: 'Todo lo de Knowledge Pro, en tu propia infraestructura.',
        features: [
          'Todo lo de Knowledge Pro',
          'Despliegue con Docker, acceso completo al código fuente',
          'Propiedad total de los datos',
          'Soporte prioritario',
        ],
        cta: 'Únete al Acceso Anticipado',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: '¿En qué se diferencia esto de Mem0/OpenMemory?',
        answer:
          'Mem0 captura fragmentos pasivamente de tus conversaciones con IA. Nosotros te entrevistamos activamente — sistemáticamente, con seguimiento de cobertura — extrayendo conocimiento profundo y estructurado. Es la diferencia entre una cámara de seguridad y una entrevista periodística.',
      },
      {
        question: '¿En qué se diferencia esto de Zep?',
        answer:
          'Zep construye grafos de conocimiento a partir de documentos y conversaciones. Nosotros hacemos entrevistas estructuradas activas con preguntas de seguimiento y profundización progresiva. Nuestro conocimiento es más rico porque se extrae intencionalmente, no se observa pasivamente.',
      },
      {
        question: '¿Qué IAs son compatibles?',
        answer:
          'Cualquier IA compatible con MCP. Confirmadas: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP es ahora un estándar industrial (Linux Foundation).',
      },
      {
        question: '¿El protocolo MCP es estable?',
        answer:
          'MCP está gobernado por la Agentic AI Foundation (Linux Foundation) con Anthropic, OpenAI, Google, Microsoft y AWS como miembros. Mantenemos compatibilidad hacia atrás.',
      },
      {
        question: '¿Puedo autoalojar?',
        answer:
          'Sí. El plan Autoalojado incluye configuración con Docker Compose y documentación completa de despliegue.',
      },
      {
        question: '¿Puedo exportar mis datos?',
        answer:
          'Siempre. Descarga tus datos en JSON/PDF en cualquier momento. Son tuyos.',
      },
      {
        question: '¿Qué métodos de pago aceptan?',
        answer:
          'Tarjeta de crédito, Apple Pay, Google Pay a través de nuestro socio de pagos. También aceptamos USDC y BTC para clientes que valoran la privacidad.',
      },
    ],
  },

  emailSignup: {
    heading: 'Obtén Acceso Anticipado',
    subheading: 'Sé el primero en probar la memoria estructurada de IA.',
    placeholder: 'Ingresa tu correo electrónico',
    cta: 'Únete al Acceso Anticipado — Gratis',
    disclaimer:
      'Sin spam. Sin tarjeta de crédito. Solo un aviso cuando lancemos.',
    formAction: formspree.action,
  },
};
