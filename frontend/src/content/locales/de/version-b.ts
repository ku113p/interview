import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'KI Langzeitgedächtnis für Claude, ChatGPT & Cursor | Interview Assistant MCP',
    description:
      'Verleihen Sie jedem KI-Assistenten ein strukturiertes Langzeitgedächtnis. Aktive Interviews fördern tiefes Wissen zutage. Der MCP-Server funktioniert mit Claude Desktop, ChatGPT, Cursor und mehr.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline:
      'Verleihen Sie JEDEM KI-Assistenten strukturiertes Langzeitgedächtnis',
    subheadline:
      'Kein weiterer passiver Speicher. Aktive Interviews fördern tiefes, strukturiertes Wissen zutage. Ihre KI versteht tatsächlich Ihren Kontext.',
    cta: 'Frühen Zugang sichern',
    socialProof: 'Funktioniert mit Claude, ChatGPT, Cursor, Windsurf & mehr',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'KI-Gedächtnis darf nicht passiv sein',
    items: [
      {
        title: 'Oberflächliche Erfassung',
        description:
          'Tools wie Mem0 zeichnen Fragmente passiv auf. Sie erhalten „Nutzer bevorzugt Python“, nicht „leitete Migration von 500K LOC Java-Codebasis zu Python, reduzierte Deploy-Zeit um 60 %.“',
        icon: 'layers',
      },
      {
        title: 'Keine Struktur',
        description:
          'Wissensgraphen erfassen Entitäten und Beziehungen, aber nicht die Geschichte. Kontext ohne Erzählung ist nur Rauschen.',
        icon: 'grid',
      },
      {
        title: 'Sie wiederholen sich',
        description:
          'Jedes Claude-Gespräch beginnt bei Null. Kopieren und fügen Sie denselben Hintergrund ein. Jedes. Einzelne. Mal.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Aktive Interviews > Passive Erfassung',
    description:
      'Andere Speicher-Tools beobachten Ihr Verhalten und speichern Fragmente passiv.\n\nWir interviewen Sie. Systematisch. Wie ein Journalist, der ein Profil erstellt — mit Nachfragen, tiefergehenden Fragen, verfolgt, was bereits behandelt wurde und was nicht.\n\nDas Ergebnis: strukturiertes, umfassendes Wissen, das die KI wirklich NUTZEN kann, nicht nur abrufen.',
    before: {
      label: 'Mem0 speichert',
      text: 'Nutzer kennt Python',
    },
    after: {
      label: 'Wir speichern',
      text: 'Leitete Python-Migration bei Acme Corp (2023). Konvertierte 500K LOC Java-Monolith zu Python-Microservices. Team von 8. Reduzierte Deploy-Zeit um 60 %. Wählte FastAPI statt Django für asynchrone Workloads.',
    },
    closing: 'Das ist der Unterschied zwischen Gedächtnis und Verständnis.',
  },

  howItWorks: {
    heading: 'So funktioniert es',
    steps: [
      {
        number: 1,
        title: 'Strukturierte Interviews',
        description:
          'Kurze Telegram-Gespräche, die systematisch Ihr Wissen abdecken. Die KI verfolgt den Stand — sie weiß, was gefragt wurde und was nicht. Fortschreitende Vertiefung, keine zufälligen Fragmente.',
      },
      {
        number: 2,
        title: 'Wissensextraktion',
        description:
          'KI extrahiert strukturierte Zusammenfassungen mit semantischen Einbettungen. Organisiert nach Lebensbereichen, durchsuchbar nach Bedeutung, nicht nur Schlüsselwörtern.',
      },
      {
        number: 3,
        title: 'MCP-Integration',
        description:
          'Standard-MCP-Server, der mit Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code und jeder MCP-kompatiblen KI funktioniert. Bearer-Token-Authentifizierung. 5-Minuten-Setup.',
      },
    ],
    bonus: {
      title: 'Demnächst: MCP Apps',
      description:
        'Interaktives Wissens-Dashboard, direkt in Claude und ChatGPT über die neue MCP Apps-Erweiterung gerendert.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Für Entwickler',
        items: [
          'KI erinnert sich an Ihren Tech-Stack, Architekturentscheidungen und Programmiermuster',
          'Beziehen Sie sich in jedem Gespräch auf vergangene Projekte',
          'Generieren Sie Codebeispiele mit IHREN echten Mustern',
          'Erklären Sie Ihre Codebasis nie wieder neu',
        ],
      },
      {
        title: 'Für Berater',
        items: [
          'KI erinnert sich an Kundendetails, Methoden und frühere Einsätze',
          'Schreiben Sie Angebote mit Bezug auf echte Erfahrungen',
          'Wiederholen Sie Hintergrundinfos nie wieder',
          'Bauen Sie automatisch auf vorherigen Gesprächen auf',
        ],
      },
      {
        title: 'Für alle',
        items: [
          'Anschreiben basierend auf echten Erfolgen',
          'Interviewvorbereitung mit KI, die Ihre Geschichte kennt',
          'Professioneller Lebenslauf, automatisch aus Ihrem Wissen generiert',
          'Ihre Daten, jederzeit exportierbar',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Einfache Preise. Keine Überraschungen.',
    tiers: [
      {
        name: 'Kostenlos',
        price: null,
        priceLabel: 'Kostenlos',
        description: '1 Interview-Sitzung + Wissenssuche-Demo.',
        features: ['1 Interview-Sitzung', 'Wissenssuche-Demo'],
        cta: 'Kostenlos testen',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/Monat',
        description:
          'Voller Zugriff auf Interviews, MCP-Server und Lebenslauf-Generierung.',
        features: [
          'Unbegrenzte Interviews + Wissensextraktion',
          'Zugriff auf MCP-Server (Bearer-Token-Authentifizierung)',
          'Semantische Suche über Ihr gesamtes Wissen',
          'Lebenslauf-Generierung inklusive',
          'Funktioniert mit Claude, ChatGPT, Cursor, Windsurf',
        ],
        cta: 'Frühen Zugang sichern',
        highlighted: true,
        badge: 'Am beliebtesten',
      },
      {
        name: 'Self-Hosted',
        price: 59,
        priceLabel: '$59/Monat',
        description: 'Alles in Knowledge Pro, auf Ihrer eigenen Infrastruktur.',
        features: [
          'Alles in Knowledge Pro',
          'Docker-Deployment, voller Quellcode-Zugriff',
          'Volle Datenhoheit',
          'Priorisierter Support',
        ],
        cta: 'Frühen Zugang sichern',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Worin unterscheidet sich das von Mem0/OpenMemory?',
        answer:
          'Mem0 erfasst Fragmente aus Ihren KI-Gesprächen passiv. Wir interviewen Sie aktiv — systematisch, mit Coverage-Tracking — und extrahieren tiefes, strukturiertes Wissen. Das ist der Unterschied zwischen einer Überwachungskamera und einem Journalisteninterview.',
      },
      {
        question: 'Worin unterscheidet sich das von Zep?',
        answer:
          'Zep erstellt Wissensgraphen aus Dokumenten und Gesprächen. Wir führen aktive, strukturierte Interviews mit Nachfragen und fortschreitender Vertiefung. Unser Wissen ist reicher, weil es gezielt extrahiert wird, nicht nur passiv beobachtet.',
      },
      {
        question: 'Welche KIs werden unterstützt?',
        answer:
          'Jede MCP-kompatible KI. Bestätigt: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP ist jetzt ein Industriestandard (Linux Foundation).',
      },
      {
        question: 'Ist das MCP-Protokoll stabil?',
        answer:
          'MCP wird von der Agentic AI Foundation (Linux Foundation) mit Anthropic, OpenAI, Google, Microsoft und AWS als Mitglieder verwaltet. Wir gewährleisten Rückwärtskompatibilität.',
      },
      {
        question: 'Kann ich selbst hosten?',
        answer:
          'Ja. Der Self-Hosted-Tarif beinhaltet Docker Compose-Setup und vollständige Deployment-Dokumentation.',
      },
      {
        question: 'Kann ich meine Daten exportieren?',
        answer:
          'Jederzeit. Laden Sie Ihre Daten als JSON/PDF herunter. Sie gehören Ihnen.',
      },
      {
        question: 'Welche Zahlungsmethoden akzeptieren Sie?',
        answer:
          'Kreditkarte, Apple Pay, Google Pay über unseren Zahlungspartner. Wir akzeptieren auch USDC und BTC für datenschutzbewusste Kunden.',
      },
    ],
  },

  emailSignup: {
    heading: 'Frühen Zugang sichern',
    subheading:
      'Seien Sie der Erste, der strukturiertes KI-Gedächtnis ausprobiert.',
    placeholder: 'Geben Sie Ihre E-Mail ein',
    cta: 'Frühen Zugang sichern — Kostenlos',
    disclaimer:
      'Kein Spam. Keine Kreditkarte. Nur eine Benachrichtigung zum Start.',
    formAction: formspree.action,
  },
};
