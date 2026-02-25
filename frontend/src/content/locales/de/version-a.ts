import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'KI-Karrierecoach – Professioneller Lebenslauf in 15 Minuten | Interview Assistant',
    description:
      'Sprich natürlich, erhalte einen professionellen, ATS-optimierten Lebenslauf. Die KI interviewt dich wie ein Karrierecoach, extrahiert Erfolge und erstellt einen überzeugenden Lebenslauf. Kostenloser Tarif.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: 'Dein KI-Karrierecoach.<br>Perfekter Lebenslauf in 15 Minuten.',
    subheadline:
      'Sprich ganz natürlich über deine Erfahrungen. Die KI interviewt dich wie ein Karrierecoach, extrahiert deine Erfolge und erstellt automatisch einen ATS-optimierten, professionellen Lebenslauf.',
    cta: 'Kostenlos testen',
    socialProof: 'Über 50 Profis auf der Warteliste',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Kommt dir das bekannt vor?',
    items: [
      {
        title: 'Du vergisst deine besten Leistungen',
        description:
          '"Was habe ich vor 3 Jahren in diesem Job erreicht?" Du hast Großartiges geleistet, kannst es aber unter Druck nicht klar ausdrücken.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT liefert generische Floskeln',
        description:
          'Du gibst deine Infos ein, ChatGPT schreibt „ergebnisorientierter Profi mit nachweislicher Erfolgsbilanz“. Recruiter durchschauen das sofort.',
        icon: 'sparkles',
      },
      {
        title: 'Aktualisieren kostet Stunden',
        description:
          'Jede Bewerbung bedeutet Neuformatierung, Umschreiben und die Hoffnung, dass das ATS dich nicht aussortiert. Du hast Besseres zu tun.',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading:
      'ChatGPT schreibt Lebensläufe.<br>Wir schreiben DEINEN Lebenslauf.',
    description:
      'ChatGPT kann Text aufpolieren, den du vorgibst. Aber die meisten können ihre eigenen Erfolge nicht gut formulieren.\n\nUnsere KI interviewt dich wie ein Karrierecoach – stellt Nachfragen, holt messbare Erfolge heraus und erwischt Dinge, die du vergessen würdest.',
    before: {
      label: 'Generische ChatGPT-Ausgabe',
      text: 'Leitete ein Entwicklungsteam',
    },
    after: {
      label: 'Interview-basierte Ausgabe',
      text: 'Führte ein 12-köpfiges Engineering-Team, das eine $2M Plattformmigration 3 Wochen vor Plan lieferte',
    },
    closing:
      'Du kennst das alles schon. Du brauchst nur jemanden, der die richtigen Fragen stellt.',
  },

  howItWorks: {
    heading: '15 Minuten. Mehr nicht.',
    steps: [
      {
        number: 1,
        title: 'Kurzes Gespräch',
        description:
          'Chatte 10-15 Minuten mit unserem Telegram-Bot. Sprich ganz natürlich über deine Erfahrungen, Projekte und Fähigkeiten. Er stellt clevere Nachfragen – wie ein Karrierecoach, kein Formular.',
      },
      {
        number: 2,
        title: 'KI-Extraktion',
        description:
          'Unsere KI zieht deine Erfolge heraus, quantifiziert den Impact, identifiziert Schlüsselkompetenzen und organisiert alles in strukturierte Karrieredaten. Nichts geht verloren.',
      },
      {
        number: 3,
        title: 'Professioneller Lebenslauf',
        description:
          'Erhalte einen polierten, ATS-optimierten PDF-Lebenslauf. Sauberes Format, keyword-stark, besteht automatisierte Prüfungen. Bereit für jede Bewerbung.',
      },
    ],
    bonus: {
      title: 'Bonus: KI-Gedächtnis',
      description:
        'Deine KI-Assistenten (Claude, ChatGPT, Cursor) können jederzeit auf deine Karrierehistorie zugreifen. Schreibe Anschreiben in Sekunden. Bereite dich mit deinen echten Erfahrungen auf Interviews vor.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Wie ein Karrierecoach',
        items: [
          'Geführtes Interview bringt deine besten Leistungen hervor',
          'Nachfragen, die du dir selbst nicht stellen würdest',
          'Erfasst automatisch messbare Erfolge',
          'Updates in 5-minütigen Folgegesprächen',
        ],
      },
      {
        title: 'ATS-optimiert',
        items: [
          'Besteht automatisierte Prüfungen (75 % der Lebensläufe nicht)',
          'Keyword-starker Inhalt, abgestimmt auf deine Branche',
          'Sauberes Format, das ATS-Systeme lesen können',
          'Professionelles Layout, das Recruiter erwarten',
        ],
      },
      {
        title: 'Immer aktuell',
        items: [
          'Füge jederzeit neue Erfahrungen per schnellem Chat hinzu',
          'Erstelle maßgeschneiderte Versionen für verschiedene Rollen',
          'Exportiere sofort als PDF',
          'Deine Daten, deine Kontrolle, jederzeit exportierbar',
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
        description: 'Teste, ob es für dich passt. Keine Kreditkarte nötig.',
        features: ['1 Interview-Sitzung', '1 Lebenslauf-Erstellung'],
        cta: 'Kostenlos testen',
        highlighted: false,
      },
      {
        name: 'CV Pro – Lifetime',
        price: 79,
        priceLabel: '$79 einmalig',
        description: 'Einmal zahlen, für immer nutzen. Gründerpreis.',
        features: [
          'Unbegrenzte Interviews + Lebenslauf-Erstellungen',
          'ATS-optimierter PDF-Export',
          'Mehrere Lebenslauf-Versionen',
          'Zugang zum Telegram-Bot',
        ],
        cta: 'Lifetime-Zugang sichern',
        highlighted: true,
        badge: 'Bestes Angebot',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Worin unterscheidet sich das von ChatGPT?',
        answer:
          'ChatGPT poliert vorhandenen Text. Wir interviewen dich – stellen Nachfragen, holen Details heraus, erfassen Erfolge, die du vergessen würdest. Denk an einen Karrierecoach, nicht an einen Texteditor. Das Ergebnis ist reichhaltiger, spezifischer und einzigartig dein.',
      },
      {
        question: 'Ist der Lebenslauf ATS-freundlich?',
        answer:
          'Ja. Sauberes Format, korrekte Überschriftenhierarchie, keyword-starker Inhalt. Entwickelt, um automatisierte Screening-Systeme zu bestehen, die 75 % der Lebensläufe ablehnen.',
      },
      {
        question: 'Brauche ich technische Kenntnisse?',
        answer:
          'Nein. Wenn du Telegram nutzen kannst, kannst du das hier nutzen. Einfach natürlich chatten. Die KI-Assistenten-Funktionen (Claude/ChatGPT-Gedächtnis) sind ein Bonus für technisch versierte Nutzer.',
      },
      {
        question: 'Wie funktioniert der kostenlose Tarif?',
        answer:
          'Eine komplette Interview-Sitzung und eine Lebenslauf-Erstellung, komplett kostenlos. Keine Kreditkarte nötig. Wenn es dir gefällt, kannst du upgraden, um weiter zu generieren und zu aktualisieren.',
      },
      {
        question: 'Kann ich meine Daten exportieren?',
        answer:
          'Jederzeit. Lade deine Daten jederzeit als JSON/PDF herunter. Sie gehören dir.',
      },
      {
        question: 'Welche Zahlungsmethoden akzeptiert ihr?',
        answer:
          'Kreditkarte, Apple Pay, Google Pay über unseren Zahlungspartner. Wir akzeptieren auch USDC und BTC für datenschutzbewusste Kunden.',
      },
      {
        question: 'Was, wenn es mir nicht gefällt?',
        answer:
          'Jederzeit kündbar. Monatliche Abos ohne Bindung. Lifetime-Käufe mit 30-Tage-Geld-zurück-Garantie.',
      },
    ],
  },

  emailSignup: {
    heading: 'Frühen Zugang sichern',
    subheading:
      'Kostenloser Tarif zum Start. Sei der Erste, der es ausprobiert.',
    placeholder: 'Deine E-Mail eingeben',
    cta: 'Warteliste beitreten – Kostenlos',
    disclaimer:
      'Kein Spam. Keine Kreditkarte. Nur eine Info, wenn wir starten.',
    formAction: formspree.action,
  },
};
