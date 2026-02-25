import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'Memória de Longo Prazo com IA para Claude, ChatGPT & Cursor | Interview Assistant MCP',
    description:
      'Dê a qualquer assistente de IA uma memória estruturada de longo prazo. Entrevistas ativas extraem conhecimento profundo. Servidor MCP funciona com Claude Desktop, ChatGPT, Cursor e mais.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline:
      'Dê a QUALQUER Assistente de IA Memória Estruturada de Longo Prazo',
    subheadline:
      'Não é mais um despejo passivo de memória. Entrevistas ativas extraem conhecimento profundo e estruturado. Sua IA realmente entende seu contexto.',
    cta: 'Participe do Acesso Antecipado',
    socialProof: 'Funciona com Claude, ChatGPT, Cursor, Windsurf e mais',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'A Memória da IA Não Deve Ser Passiva',
    items: [
      {
        title: 'Captura superficial',
        description:
          'Ferramentas como Mem0 registram fragmentos passivamente. Você recebe "usuário prefere Python", não "liderou migração de 500K LOC de código Java para Python, reduzindo o tempo de deploy em 60%."',
        icon: 'layers',
      },
      {
        title: 'Sem estrutura',
        description:
          'Grafos de conhecimento capturam entidades e relações, mas perdem a narrativa. Contexto sem história é só ruído.',
        icon: 'grid',
      },
      {
        title: 'Você se repete',
        description:
          'Toda conversa no Claude começa do zero. Copie e cole o mesmo contexto. Toda. Maldita. Vez.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Entrevistas Ativas > Captura Passiva',
    description:
      'Outras ferramentas de memória observam o que você faz e armazenam fragmentos passivamente.\n\nNós entrevistamos você. Sistematicamente. Como um jornalista construindo um perfil — fazendo perguntas de acompanhamento, aprofundando, acompanhando o que foi coberto e o que não foi.\n\nO resultado: conhecimento estruturado e abrangente que a IA pode realmente USAR, não apenas recuperar.',
    before: {
      label: 'Mem0 armazena',
      text: 'usuário sabe Python',
    },
    after: {
      label: 'Nós armazenamos',
      text: 'Liderou migração Python na Acme Corp (2023). Converteu monólito Java de 500K LOC para microserviços Python. Equipe de 8. Reduziu tempo de deploy em 60%. Escolheu FastAPI em vez de Django para cargas assíncronas.',
    },
    closing: 'Essa é a diferença entre memória e entendimento.',
  },

  howItWorks: {
    heading: 'Como Funciona',
    steps: [
      {
        number: 1,
        title: 'Entrevistas Estruturadas',
        description:
          'Conversas rápidas no Telegram que cobrem sistematicamente seu conhecimento. A IA acompanha o que foi perguntado — sabe o que já foi abordado e o que falta. Aprofundamento progressivo, não fragmentos aleatórios.',
      },
      {
        number: 2,
        title: 'Extração de Conhecimento',
        description:
          'IA extrai resumos estruturados com embeddings semânticos. Organizados por áreas da vida, pesquisáveis por significado, não apenas por palavras-chave.',
      },
      {
        number: 3,
        title: 'Integração MCP',
        description:
          'Servidor MCP padrão que funciona com Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code e qualquer IA compatível com MCP. Autenticação por Bearer token. Configuração em 5 minutos.',
      },
    ],
    bonus: {
      title: 'Em Breve: Aplicativos MCP',
      description:
        'Painel interativo de conhecimento renderizado diretamente dentro do Claude e ChatGPT via a nova extensão MCP Apps.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Para Desenvolvedores',
        items: [
          'IA lembra sua stack tecnológica, decisões arquiteturais e padrões de código',
          'Referencie projetos passados em qualquer conversa',
          'Gere exemplos de código usando SEUS padrões reais',
          'Nunca mais explique sua base de código do zero',
        ],
      },
      {
        title: 'Para Consultores',
        items: [
          'IA recorda detalhes de clientes, metodologias e projetos anteriores',
          'Escreva propostas com base em experiência real',
          'Nunca repita informações de contexto novamente',
          'Construa sobre conversas anteriores automaticamente',
        ],
      },
      {
        title: 'Para Todos',
        items: [
          'Cartas de apresentação baseadas em conquistas reais',
          'Preparação para entrevistas com IA que conhece sua história',
          'Currículo profissional gerado automaticamente a partir do seu conhecimento',
          'Seus dados, sempre exportáveis',
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
        priceLabel: 'Grátis',
        description: '1 sessão de entrevista + demo de busca de conhecimento.',
        features: ['1 sessão de entrevista', 'Demo de busca de conhecimento'],
        cta: 'Experimente Grátis',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/mês',
        description:
          'Acesso completo a entrevistas, servidor MCP e geração de CV.',
        features: [
          'Entrevistas ilimitadas + extração de conhecimento',
          'Acesso ao servidor MCP (autenticação Bearer token)',
          'Busca semântica em todo seu conhecimento',
          'Geração de CV incluída',
          'Funciona com Claude, ChatGPT, Cursor, Windsurf',
        ],
        cta: 'Participe do Acesso Antecipado',
        highlighted: true,
        badge: 'Mais Popular',
      },
      {
        name: 'Self-Hosted',
        price: 59,
        priceLabel: '$59/mês',
        description: 'Tudo do Knowledge Pro, na sua própria infraestrutura.',
        features: [
          'Tudo do Knowledge Pro',
          'Deploy via Docker, acesso total ao código-fonte',
          'Propriedade total dos dados',
          'Suporte prioritário',
        ],
        cta: 'Participe do Acesso Antecipado',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Como isso é diferente do Mem0/OpenMemory?',
        answer:
          'Mem0 captura fragmentos passivamente das suas conversas com IA. Nós entrevistamos você ativamente — sistematicamente, com acompanhamento de cobertura — extraindo conhecimento profundo e estruturado. É a diferença entre uma câmera de segurança e uma entrevista jornalística.',
      },
      {
        question: 'Como isso é diferente do Zep?',
        answer:
          'Zep constrói grafos de conhecimento a partir de documentos e conversas. Nós fazemos entrevistas estruturadas ativas com perguntas de acompanhamento e aprofundamento progressivo. Nosso conhecimento é mais rico porque é extraído intencionalmente, não apenas observado passivamente.',
      },
      {
        question: 'Quais IAs são suportadas?',
        answer:
          'Qualquer IA compatível com MCP. Confirmadas: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP é agora um padrão da indústria (Linux Foundation).',
      },
      {
        question: 'O protocolo MCP é estável?',
        answer:
          'MCP é governado pela Agentic AI Foundation (Linux Foundation) com Anthropic, OpenAI, Google, Microsoft e AWS como membros. Mantemos compatibilidade retroativa.',
      },
      {
        question: 'Posso hospedar por conta própria?',
        answer:
          'Sim. O plano Self-Hosted inclui configuração Docker Compose e documentação completa de deploy.',
      },
      {
        question: 'Posso exportar meus dados?',
        answer:
          'Sempre. Baixe seus dados em JSON/PDF a qualquer momento. Eles são seus.',
      },
      {
        question: 'Quais métodos de pagamento vocês aceitam?',
        answer:
          'Cartão de crédito, Apple Pay, Google Pay via nosso parceiro de pagamento. Também aceitamos USDC e BTC para clientes que prezam pela privacidade.',
      },
    ],
  },

  emailSignup: {
    heading: 'Garanta Acesso Antecipado',
    subheading: 'Seja o primeiro a testar a memória estruturada para IA.',
    placeholder: 'Digite seu e-mail',
    cta: 'Participe do Acesso Antecipado — Grátis',
    disclaimer:
      'Sem spam. Sem cartão de crédito. Apenas um aviso quando lançarmos.',
    formAction: formspree.action,
  },
};
