import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'Mémoire Long Terme IA pour Claude, ChatGPT & Cursor | Interview Assistant MCP',
    description:
      'Offrez à n’importe quel assistant IA une mémoire structurée à long terme. Les interviews actives extraient un savoir approfondi. Le serveur MCP fonctionne avec Claude Desktop, ChatGPT, Cursor, et plus encore.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline: 'Offrez à TOUT Assistant IA une Mémoire Structurée à Long Terme',
    subheadline:
      'Pas un simple dépôt passif de mémoire. Les interviews actives extraient un savoir profond et structuré. Votre IA comprend réellement votre contexte.',
    cta: 'Rejoignez l’Accès Anticipé',
    socialProof: 'Compatible avec Claude, ChatGPT, Cursor, Windsurf & plus',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'La Mémoire IA Ne Doit Pas Être Passive',
    items: [
      {
        title: 'Capture superficielle',
        description:
          'Des outils comme Mem0 enregistrent passivement des fragments. Vous obtenez "l’utilisateur préfère Python" au lieu de "a dirigé la migration d’une base de code Java de 500K LOC vers Python, réduisant le temps de déploiement de 60 %."',
        icon: 'layers',
      },
      {
        title: 'Pas de structure',
        description:
          'Les graphes de connaissances capturent entités et relations mais manquent la narration. Un contexte sans histoire n’est que du bruit.',
        icon: 'grid',
      },
      {
        title: 'Vous vous répétez',
        description:
          'Chaque conversation avec Claude repart de zéro. Copiez-collez toujours le même contexte. À chaque. Fois.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Interviews Actives > Captures Passives',
    description:
      'Les autres outils de mémoire observent ce que vous faites et stockent passivement des fragments.\n\nNous vous interviewons. Systématiquement. Comme un journaliste construisant un profil — posant des questions de suivi, approfondissant, suivant ce qui a été couvert et ce qui ne l’a pas été.\n\nLe résultat : un savoir structuré et complet que l’IA peut réellement UTILISER, pas seulement retrouver.',
    before: {
      label: 'Mem0 stocke',
      text: 'l’utilisateur sait Python',
    },
    after: {
      label: 'Nous stockons',
      text: 'A dirigé la migration Python chez Acme Corp (2023). Conversion d’un monolithe Java de 500K LOC en microservices Python. Équipe de 8. Réduction du temps de déploiement de 60 %. Choix de FastAPI plutôt que Django pour les charges asynchrones.',
    },
    closing: 'C’est la différence entre mémoire et compréhension.',
  },

  howItWorks: {
    heading: 'Comment Ça Marche',
    steps: [
      {
        number: 1,
        title: 'Interviews Structurées',
        description:
          'Conversations rapides sur Telegram qui couvrent systématiquement votre savoir. L’IA suit la couverture — elle sait ce qu’elle a demandé et ce qu’elle n’a pas encore demandé. Approfondissement progressif, pas de fragments aléatoires.',
      },
      {
        number: 2,
        title: 'Extraction de Connaissances',
        description:
          "L'IA extrait des résumés structurés avec des embeddings sémantiques. Organisés par domaines de vie, consultables par sens, pas seulement par mots-clés.",
      },
      {
        number: 3,
        title: 'Intégration MCP',
        description:
          'Serveur MCP standard compatible avec Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code, et toute IA compatible MCP. Authentification par Bearer token. Installation en 5 minutes.',
      },
    ],
    bonus: {
      title: 'Bientôt : Applications MCP',
      description:
        'Tableau de bord interactif de connaissances rendu directement dans Claude et ChatGPT via la nouvelle extension MCP Apps.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Pour les Développeurs',
        items: [
          'L’IA se souvient de votre stack tech, décisions architecturales, et patterns de code',
          'Référez-vous à vos projets passés dans n’importe quelle conversation',
          'Générez des exemples de code avec VOS vrais patterns',
          'Ne réexpliquez jamais la configuration de votre codebase',
        ],
      },
      {
        title: 'Pour les Consultants',
        items: [
          'L’IA rappelle les détails clients, méthodologies, missions passées',
          'Rédigez des propositions en vous appuyant sur une expérience réelle',
          'Ne répétez plus jamais les informations de contexte',
          'Bâtissez automatiquement sur les conversations précédentes',
        ],
      },
      {
        title: 'Pour Tous',
        items: [
          'Lettres de motivation rédigées à partir de réalisations concrètes',
          'Préparation aux entretiens avec une IA qui connaît votre histoire',
          'CV professionnel généré automatiquement à partir de votre savoir',
          'Vos données, toujours exportables',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Tarification Simple. Sans Surprise.',
    tiers: [
      {
        name: 'Gratuit',
        price: null,
        priceLabel: 'Gratuit',
        description:
          '1 session d’entretien + démo de recherche de connaissances.',
        features: [
          '1 session d’entretien',
          'Démo de recherche de connaissances',
        ],
        cta: 'Essayez Gratuitement',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/mois',
        description:
          'Accès complet aux interviews, serveur MCP, et génération de CV.',
        features: [
          'Interviews illimitées + extraction de connaissances',
          'Accès serveur MCP (authentification Bearer token)',
          'Recherche sémantique sur l’ensemble de vos connaissances',
          'Génération de CV incluse',
          'Compatible avec Claude, ChatGPT, Cursor, Windsurf',
        ],
        cta: 'Rejoignez l’Accès Anticipé',
        highlighted: true,
        badge: 'Le Plus Populaire',
      },
      {
        name: 'Auto-hébergé',
        price: 59,
        priceLabel: '$59/mois',
        description:
          'Tout ce qui est dans Knowledge Pro, sur votre propre infrastructure.',
        features: [
          'Tout ce qui est dans Knowledge Pro',
          'Déploiement Docker, accès complet au code source',
          'Propriété totale des données',
          'Support prioritaire',
        ],
        cta: 'Rejoignez l’Accès Anticipé',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'En quoi est-ce différent de Mem0/OpenMemory ?',
        answer:
          'Mem0 capture passivement des fragments de vos conversations IA. Nous vous interviewons activement — de façon systématique, avec suivi de la couverture — pour extraire un savoir structuré et profond. C’est la différence entre une caméra de surveillance et une interview journalistique.',
      },
      {
        question: 'En quoi est-ce différent de Zep ?',
        answer:
          'Zep construit des graphes de connaissances à partir de documents et conversations. Nous réalisons des interviews actives et structurées avec questions de suivi et approfondissement progressif. Notre savoir est plus riche car il est intentionnellement extrait, pas simplement observé passivement.',
      },
      {
        question: 'Quelles IA sont supportées ?',
        answer:
          'Toute IA compatible MCP. Confirmé : Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP est désormais une norme industrielle (Linux Foundation).',
      },
      {
        question: 'Le protocole MCP est-il stable ?',
        answer:
          "MCP est gouverné par l'Agentic AI Foundation (Linux Foundation) avec Anthropic, OpenAI, Google, Microsoft, et AWS comme membres. Nous assurons la compatibilité ascendante.",
      },
      {
        question: 'Puis-je auto-héberger ?',
        answer:
          'Oui. Le forfait Auto-hébergé inclut la configuration Docker Compose et une documentation complète de déploiement.',
      },
      {
        question: 'Puis-je exporter mes données ?',
        answer:
          'Toujours. Téléchargez vos données en JSON/PDF à tout moment. Elles vous appartiennent.',
      },
      {
        question: 'Quels moyens de paiement acceptez-vous ?',
        answer:
          'Carte bancaire, Apple Pay, Google Pay via notre partenaire de paiement. Nous acceptons aussi USDC et BTC pour les clients soucieux de leur confidentialité.',
      },
    ],
  },

  emailSignup: {
    heading: 'Obtenez un Accès Anticipé',
    subheading: 'Soyez les premiers à tester la mémoire IA structurée.',
    placeholder: 'Entrez votre email',
    cta: 'Rejoignez l’Accès Anticipé — Gratuit',
    disclaimer:
      'Pas de spam. Pas de carte bancaire. Juste un avis lors du lancement.',
    formAction: formspree.action,
  },
};
