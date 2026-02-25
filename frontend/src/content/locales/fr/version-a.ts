import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'Coach de Carrière IA - CV Professionnel en 15 Minutes | Interview Assistant',
    description:
      'Parlez naturellement, obtenez un CV professionnel optimisé ATS. L’IA vous interviewe comme un coach de carrière, extrait vos réussites, génère un CV soigné. Offre gratuite disponible.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: 'Votre Coach de Carrière IA.<br>CV Parfait en 15 Minutes.',
    subheadline:
      'Parlez naturellement de votre expérience. L’IA vous interviewe comme un coach de carrière, extrait vos réussites et génère automatiquement un CV professionnel optimisé ATS.',
    cta: 'Essayez Gratuitement',
    socialProof: 'Rejoignez plus de 50 professionnels sur la liste d’attente',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Ça vous parle ?',
    items: [
      {
        title: 'Vous oubliez vos meilleures réalisations',
        description:
          '"Qu’ai-je accompli dans ce job il y a 3 ans ?" Vous avez fait des choses incroyables mais avez du mal à les exprimer sous pression.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT vous donne du contenu générique',
        description:
          'Vous copiez vos infos, ChatGPT écrit "professionnel orienté résultats avec un parcours éprouvé." Les recruteurs détectent ça immédiatement.',
        icon: 'sparkles',
      },
      {
        title: 'La mise à jour prend des heures',
        description:
          'Chaque candidature signifie reformater, réécrire, et espérer que l’ATS ne vous rejette pas. Vous avez mieux à faire.',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT écrit des CV.<br>Nous écrivons VOTRE CV.',
    description:
      'ChatGPT peut peaufiner un texte que vous lui donnez. Mais la plupart des gens ne savent pas bien exprimer leurs propres réussites.\n\nNotre IA vous interviewe comme un coach de carrière — posant des questions de suivi, faisant ressortir l’impact quantifiable, captant ce que vous oublieriez.',
    before: {
      label: 'Texte Générique ChatGPT',
      text: 'Gestion d’une équipe de développement',
    },
    after: {
      label: 'Texte Extrait par Interview',
      text: 'Direction d’une équipe de 12 ingénieurs ayant livré une migration de plateforme à 2M$ avec 3 semaines d’avance',
    },
    closing:
      'Vous connaissez déjà tout ça. Il vous faut juste quelqu’un pour poser les bonnes questions.',
  },

  howItWorks: {
    heading: '15 Minutes. C’est tout.',
    steps: [
      {
        number: 1,
        title: 'Conversation Rapide',
        description:
          'Discutez avec notre bot Telegram pendant 10-15 minutes. Parlez naturellement de votre expérience, projets, compétences. Il pose des questions intelligentes — comme un coach, pas un formulaire.',
      },
      {
        number: 2,
        title: 'Extraction par IA',
        description:
          'Notre IA extrait vos réussites, quantifie l’impact, identifie les compétences clés, et organise tout en données de carrière structurées. Rien ne se perd.',
      },
      {
        number: 3,
        title: 'CV Professionnel',
        description:
          'Recevez un CV PDF soigné, optimisé ATS. Formatage parfait, mots-clés pertinents, passe le filtrage automatique. Prêt pour toute candidature.',
      },
    ],
    bonus: {
      title: 'Bonus : Mémoire IA',
      description:
        'Vos assistants IA (Claude, ChatGPT, Cursor) peuvent désormais interroger votre parcours à tout moment. Rédigez des lettres de motivation en secondes. Préparez vos entretiens avec votre vraie expérience.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Comme un Coach de Carrière',
        items: [
          'L’interview guidée fait ressortir vos meilleures réalisations',
          'Questions de suivi auxquelles vous ne penseriez pas vous-même',
          'Capture automatiquement les réussites quantifiables',
          'Mises à jour en sessions de 5 minutes',
        ],
      },
      {
        title: 'Optimisé ATS',
        items: [
          'Passe le filtrage automatique (75% des CV ne le font pas)',
          'Contenu riche en mots-clés adapté à votre secteur',
          'Formatage propre que les ATS peuvent lire',
          'Présentation professionnelle attendue par les recruteurs',
        ],
      },
      {
        title: 'Toujours à Jour',
        items: [
          'Ajoutez de l’expérience à tout moment via un chat rapide',
          'Générez des versions personnalisées pour différents postes',
          'Export instantané en PDF',
          'Vos données, votre contrôle, exportables à tout moment',
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
        description: 'Testez sans engagement. Pas de carte bancaire requise.',
        features: ['1 session d’entretien', '1 génération de CV'],
        cta: 'Essayez Gratuitement',
        highlighted: false,
      },
      {
        name: 'CV Pro — À Vie',
        price: 79,
        priceLabel: '$79 paiement unique',
        description: 'Payez une fois, utilisez à vie. Prix membre fondateur.',
        features: [
          'Entretiens et générations de CV illimités',
          'Export PDF optimisé ATS',
          'Versions multiples de CV',
          'Accès via bot Telegram',
        ],
        cta: 'Réservez l’Accès à Vie',
        highlighted: true,
        badge: 'Meilleur Rapport Qualité-Prix',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'En quoi est-ce différent de ChatGPT ?',
        answer:
          'ChatGPT peaufine un texte que vous avez déjà. Nous vous interviewons — posant des questions de suivi, faisant ressortir les détails, captant les réussites que vous oublieriez. Pensez coach de carrière, pas éditeur de texte. Le résultat est plus riche, plus précis, et unique.',
      },
      {
        question: 'Le CV est-il compatible ATS ?',
        answer:
          'Oui. Formatage propre, hiérarchie des titres correcte, contenu riche en mots-clés. Conçu pour passer les systèmes de filtrage automatique qui rejettent 75% des CV.',
      },
      {
        question: 'Faut-il des compétences techniques ?',
        answer:
          'Non. Si vous savez utiliser Telegram, vous pouvez utiliser ce service. Parlez simplement naturellement. Les fonctions assistants IA (mémoire Claude/ChatGPT) sont un bonus pour les utilisateurs techniques.',
      },
      {
        question: 'Comment fonctionne l’offre gratuite ?',
        answer:
          'Une session complète d’entretien et une génération de CV, entièrement gratuites. Pas de carte bancaire requise. Si vous aimez, passez à la version payante pour continuer à générer et mettre à jour.',
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
      {
        question: 'Et si je ne suis pas satisfait ?',
        answer:
          'Annulez à tout moment. Abonnements mensuels sans engagement. Les achats à vie bénéficient d’une garantie de remboursement de 30 jours.',
      },
    ],
  },

  emailSignup: {
    heading: 'Accès Anticipé',
    subheading:
      'Offre gratuite disponible au lancement. Soyez les premiers à essayer.',
    placeholder: 'Entrez votre email',
    cta: 'Rejoindre la Liste d’Attente — Gratuit',
    disclaimer:
      'Pas de spam. Pas de carte bancaire. Juste un rappel au lancement.',
    formAction: formspree.action,
  },
};
