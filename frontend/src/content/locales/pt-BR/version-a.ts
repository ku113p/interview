import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'Coach de Carreira com IA - Currículo Profissional em 15 Minutos | Interview Assistant',
    description:
      'Converse naturalmente, obtenha um currículo profissional otimizado para ATS. IA entrevista você como um coach de carreira, extrai conquistas e gera um CV refinado. Plano gratuito.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline:
      'Seu Coach de Carreira com IA.<br>Currículo Perfeito em 15 Minutos.',
    subheadline:
      'Converse naturalmente sobre sua experiência. A IA entrevista você como um coach de carreira, extrai suas conquistas e gera automaticamente um currículo profissional otimizado para ATS.',
    cta: 'Teste Gratuitamente',
    socialProof: 'Junte-se a mais de 50 profissionais na lista de espera',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Parece Familiar?',
    items: [
      {
        title: 'Você esquece seu melhor trabalho',
        description:
          '"O que eu conquistei naquele emprego há 3 anos?" Você fez coisas incríveis, mas não consegue expressá-las sob pressão.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT gera respostas genéricas',
        description:
          'Você cola suas informações, o ChatGPT escreve "profissional orientado a resultados com histórico comprovado." Os recrutadores percebem isso na hora.',
        icon: 'sparkles',
      },
      {
        title: 'Atualizar leva horas',
        description:
          'Cada candidatura significa reformatação, reescrita e torcer para o ATS não rejeitar. Você tem coisas melhores para fazer.',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT Escreve Currículos.<br>Nós Escrevemos SEU Currículo.',
    description:
      'O ChatGPT pode aprimorar o texto que você fornece. Mas a maioria das pessoas não consegue articular bem suas próprias conquistas.\n\nNossa IA entrevista você como um coach de carreira — fazendo perguntas de acompanhamento, destacando impactos quantificáveis, capturando detalhes que você esqueceria.',
    before: {
      label: 'Resultado Genérico do ChatGPT',
      text: 'Gerenciou uma equipe de desenvolvimento',
    },
    after: {
      label: 'Resultado Extraído na Entrevista',
      text: 'Liderou uma equipe de engenharia de 12 pessoas que entregou uma migração de plataforma de $2M com 3 semanas de antecedência',
    },
    closing:
      'Você já sabe dessas coisas. Só precisa de alguém que faça as perguntas certas.',
  },

  howItWorks: {
    heading: '15 Minutos. Só Isso.',
    steps: [
      {
        number: 1,
        title: 'Conversa Rápida',
        description:
          'Converse com nosso bot no Telegram por 10-15 minutos. Fale naturalmente sobre sua experiência, projetos, habilidades. Ele faz perguntas inteligentes de acompanhamento — como um coach, não um formulário.',
      },
      {
        number: 2,
        title: 'Extração por IA',
        description:
          'Nossa IA extrai conquistas, quantifica impactos, identifica habilidades-chave e organiza tudo em dados estruturados de carreira. Nada se perde.',
      },
      {
        number: 3,
        title: 'Currículo Profissional',
        description:
          'Receba um currículo PDF polido, otimizado para ATS. Formatação adequada, rico em palavras-chave, aprovado em triagens automáticas. Pronto para qualquer vaga.',
      },
    ],
    bonus: {
      title: 'Bônus: Memória da IA',
      description:
        'Seus assistentes de IA (Claude, ChatGPT, Cursor) podem consultar seu histórico de carreira a qualquer momento. Escreva cartas de apresentação em segundos. Prepare-se para entrevistas com sua experiência real.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Como um Coach de Carreira',
        items: [
          'Entrevista guiada que destaca seu melhor trabalho',
          'Perguntas de acompanhamento que você não pensaria em fazer',
          'Captura conquistas quantificáveis automaticamente',
          'Atualizações em sessões rápidas de 5 minutos',
        ],
      },
      {
        title: 'Otimizado para ATS',
        items: [
          'Passa na triagem automática (75% dos currículos não passam)',
          'Conteúdo rico em palavras-chave alinhado ao seu setor',
          'Formatação limpa que sistemas ATS conseguem ler',
          'Layout profissional que recrutadores esperam',
        ],
      },
      {
        title: 'Sempre Atualizado',
        items: [
          'Adicione novas experiências a qualquer momento via chat rápido',
          'Gere versões personalizadas para diferentes cargos',
          'Exporte para PDF instantaneamente',
          'Seus dados, sob seu controle, exportáveis quando quiser',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Preço Simples. Sem Surpresas.',
    tiers: [
      {
        name: 'Grátis',
        price: null,
        priceLabel: 'Gratuito',
        description: 'Veja se funciona para você. Sem cartão de crédito.',
        features: ['1 sessão de entrevista', '1 geração de currículo'],
        cta: 'Teste Gratuitamente',
        highlighted: false,
      },
      {
        name: 'CV Pro — Vitalício',
        price: 79,
        priceLabel: '$79 pagamento único',
        description:
          'Pague uma vez, use para sempre. Preço para membros fundadores.',
        features: [
          'Entrevistas e gerações de currículo ilimitadas',
          'Exportação de PDF otimizada para ATS',
          'Múltiplas versões de currículo',
          'Acesso via bot do Telegram',
        ],
        cta: 'Reserve Acesso Vitalício',
        highlighted: true,
        badge: 'Melhor Custo-Benefício',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Como isso é diferente do ChatGPT?',
        answer:
          'O ChatGPT aprimora textos que você já tem. Nós entrevistamos você — fazendo perguntas de acompanhamento, extraindo detalhes específicos, capturando conquistas que você esqueceria. Pense em um coach de carreira, não em um editor de texto. O resultado é mais rico, específico e único.',
      },
      {
        question: 'O currículo é compatível com ATS?',
        answer:
          'Sim. Formatação limpa, hierarquia correta de títulos, conteúdo rico em palavras-chave. Projetado para passar por sistemas automáticos que rejeitam 75% dos currículos.',
      },
      {
        question: 'Preciso de habilidades técnicas?',
        answer:
          'Não. Se você sabe usar Telegram, pode usar isso. Basta conversar naturalmente. Os recursos de assistente de IA (memória Claude/ChatGPT) são um bônus para usuários técnicos.',
      },
      {
        question: 'Como funciona o plano gratuito?',
        answer:
          'Uma sessão completa de entrevista e uma geração de currículo, totalmente grátis. Sem cartão de crédito. Se gostar, faça upgrade para continuar gerando e atualizando.',
      },
      {
        question: 'Posso exportar meus dados?',
        answer:
          'Sempre. Baixe seus dados em JSON/PDF a qualquer momento. Eles são seus.',
      },
      {
        question: 'Quais métodos de pagamento aceitam?',
        answer:
          'Cartão de crédito, Apple Pay, Google Pay via nosso parceiro de pagamento. Também aceitamos USDC e BTC para clientes que prezam pela privacidade.',
      },
      {
        question: 'E se eu não gostar?',
        answer:
          'Cancele a qualquer momento. Assinaturas mensais, sem fidelidade. Compras vitalícias têm garantia de reembolso de 30 dias.',
      },
    ],
  },

  emailSignup: {
    heading: 'Garanta Acesso Antecipado',
    subheading:
      'Plano gratuito disponível no lançamento. Seja o primeiro a testar.',
    placeholder: 'Digite seu e-mail',
    cta: 'Entrar na Lista de Espera — Grátis',
    disclaimer:
      'Sem spam. Sem cartão de crédito. Só avisamos quando lançarmos.',
    formAction: formspree.action,
  },
};
