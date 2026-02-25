import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'Coach de Carrera con IA - Currículum Profesional en 15 Minutos | Interview Assistant',
    description:
      'Habla de forma natural, obtén un currículum profesional optimizado para ATS. La IA te entrevista como un coach de carrera, extrae logros y genera un CV impecable. Plan gratuito disponible.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline:
      'Tu Coach de Carrera con IA.<br>Currículum Perfecto en 15 Minutos.',
    subheadline:
      'Habla naturalmente sobre tu experiencia. La IA te entrevista como un coach de carrera, extrae tus logros y genera automáticamente un currículum profesional optimizado para ATS.',
    cta: 'Pruébalo Gratis',
    socialProof: 'Únete a más de 50 profesionales en la lista de espera',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: '¿Te Suena Familiar?',
    items: [
      {
        title: 'Olvidas tu mejor trabajo',
        description:
          '"¿Qué logré en ese trabajo hace 3 años?" Hiciste cosas increíbles pero no sabes cómo expresarlas bajo presión.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT te da respuestas genéricas',
        description:
          'Pegas tu información y ChatGPT escribe "profesional orientado a resultados con historial comprobado." Los reclutadores lo detectan al instante.',
        icon: 'sparkles',
      },
      {
        title: 'Actualizar toma horas',
        description:
          'Cada aplicación significa reformatear, reescribir y esperar que el ATS no te rechace. Tienes cosas mejores que hacer.',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading:
      'ChatGPT Escribe Currículums.<br>Nosotros Escribimos TU Currículum.',
    description:
      'ChatGPT puede pulir el texto que le das. Pero la mayoría no sabe expresar bien sus propios logros.\n\nNuestra IA te entrevista como un coach de carrera — hace preguntas de seguimiento, saca impacto cuantificable, detecta cosas que olvidarías.',
    before: {
      label: 'Salida Genérica de ChatGPT',
      text: 'Gestionó un equipo de desarrollo',
    },
    after: {
      label: 'Salida Extraída en la Entrevista',
      text: 'Lideró un equipo de ingeniería de 12 personas que entregó una migración de plataforma de $2M con 3 semanas de anticipación',
    },
    closing:
      'Ya sabes esto. Solo necesitas que alguien haga las preguntas correctas.',
  },

  howItWorks: {
    heading: '15 Minutos. Eso es Todo.',
    steps: [
      {
        number: 1,
        title: 'Conversación Rápida',
        description:
          'Chatea con nuestro bot de Telegram durante 10-15 minutos. Habla naturalmente sobre tu experiencia, proyectos y habilidades. Hace preguntas inteligentes de seguimiento — como un coach de carrera, no un formulario.',
      },
      {
        number: 2,
        title: 'Extracción con IA',
        description:
          'Nuestra IA extrae logros, cuantifica impacto, identifica habilidades clave y organiza todo en datos estructurados de carrera. Nada se pierde.',
      },
      {
        number: 3,
        title: 'Currículum Profesional',
        description:
          'Obtén un currículum PDF pulido y optimizado para ATS. Formato adecuado, rico en palabras clave, pasa filtros automáticos. Listo para cualquier aplicación laboral.',
      },
    ],
    bonus: {
      title: 'Bonus: Memoria IA',
      description:
        'Tus asistentes IA (Claude, ChatGPT, Cursor) pueden consultar tu historial profesional en cualquier momento. Escribe cartas de presentación en segundos. Prepárate para entrevistas con tu experiencia real.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Como un Coach de Carrera',
        items: [
          'La entrevista guiada saca lo mejor de ti',
          'Preguntas de seguimiento que no te harías solo',
          'Captura logros cuantificables automáticamente',
          'Actualizaciones en sesiones rápidas de 5 minutos',
        ],
      },
      {
        title: 'Optimizado para ATS',
        items: [
          'Pasa filtros automáticos (75% de currículums no lo hacen)',
          'Contenido rico en palabras clave ajustado a tu industria',
          'Formato limpio que los sistemas ATS pueden leer',
          'Diseño profesional que esperan los reclutadores',
        ],
      },
      {
        title: 'Siempre Actualizado',
        items: [
          'Agrega nueva experiencia en cualquier momento vía chat rápido',
          'Genera versiones personalizadas para distintos roles',
          'Exporta a PDF al instante',
          'Tus datos, bajo tu control, exportables cuando quieras',
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
          'Prueba si funciona para ti. No se requiere tarjeta de crédito.',
        features: ['1 sesión de entrevista', '1 generación de currículum'],
        cta: 'Pruébalo Gratis',
        highlighted: false,
      },
      {
        name: 'CV Pro — Acceso de por Vida',
        price: 79,
        priceLabel: '$79 pago único',
        description:
          'Paga una vez, úsalo para siempre. Precio para miembros fundadores.',
        features: [
          'Entrevistas y generaciones de currículum ilimitadas',
          'Exportación PDF optimizada para ATS',
          'Múltiples versiones de currículum',
          'Acceso al bot de Telegram',
        ],
        cta: 'Reserva Acceso de por Vida',
        highlighted: true,
        badge: 'Mejor Valor',
      },
    ],
  },

  faq: {
    items: [
      {
        question: '¿En qué se diferencia esto de ChatGPT?',
        answer:
          'ChatGPT pule texto que ya tienes. Nosotros te entrevistamos — hacemos preguntas de seguimiento, sacamos detalles específicos, capturamos logros que olvidarías. Piensa en un coach de carrera, no en un editor de texto. El resultado es más rico, específico y único para ti.',
      },
      {
        question: '¿El currículum es compatible con ATS?',
        answer:
          'Sí. Formato limpio, jerarquía adecuada de encabezados, contenido rico en palabras clave. Diseñado para pasar sistemas de filtrado automático que rechazan el 75% de currículums.',
      },
      {
        question: '¿Necesito habilidades técnicas?',
        answer:
          'No. Si sabes usar Telegram, puedes usar esto. Solo chatea naturalmente. Las funciones de asistente IA (memoria Claude/ChatGPT) son un plus para usuarios técnicos.',
      },
      {
        question: '¿Cómo funciona el plan gratuito?',
        answer:
          'Una sesión completa de entrevista y una generación de currículum, totalmente gratis. No se requiere tarjeta. Si te gusta, actualiza para seguir generando y actualizando.',
      },
      {
        question: '¿Puedo exportar mis datos?',
        answer:
          'Siempre. Descarga tus datos en JSON/PDF cuando quieras. Son tuyos.',
      },
      {
        question: '¿Qué métodos de pago aceptan?',
        answer:
          'Tarjeta de crédito, Apple Pay, Google Pay a través de nuestro socio de pagos. También aceptamos USDC y BTC para clientes que valoran la privacidad.',
      },
      {
        question: '¿Y si no me gusta?',
        answer:
          'Cancela cuando quieras. Suscripciones mensuales sin compromiso. Las compras de por vida tienen garantía de devolución de 30 días.',
      },
    ],
  },

  emailSignup: {
    heading: 'Obtén Acceso Anticipado',
    subheading:
      'Plan gratuito disponible al lanzamiento. Sé el primero en probarlo.',
    placeholder: 'Introduce tu correo electrónico',
    cta: 'Únete a la Lista de Espera — Gratis',
    disclaimer:
      'Sin spam. Sin tarjeta de crédito. Solo un aviso cuando lancemos.',
    formAction: formspree.action,
  },
};
