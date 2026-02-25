import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'AI Długoterminowa Pamięć dla Claude, ChatGPT & Cursor | Interview Assistant MCP',
    description:
      'Dodaj każdemu asystentowi AI uporządkowaną długoterminową pamięć. Aktywne wywiady wydobywają głęboką wiedzę. Serwer MCP współpracuje z Claude Desktop, ChatGPT, Cursor i innymi.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline:
      'Dodaj KAŻDEMU Asystentowi AI Uporządkowaną Długoterminową Pamięć',
    subheadline:
      'To nie kolejny pasywny zrzut pamięci. Aktywne wywiady wydobywają głęboką, uporządkowaną wiedzę. Twój AI naprawdę rozumie Twój kontekst.',
    cta: 'Dołącz do Wczesnego Dostępu',
    socialProof: 'Działa z Claude, ChatGPT, Cursor, Windsurf i innymi',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Pamięć AI nie powinna być pasywna',
    items: [
      {
        title: 'Płytkie przechwytywanie',
        description:
          'Narzędzia takie jak Mem0 pasywnie rejestrują fragmenty. Dostajesz "użytkownik woli Pythona", a nie "prowadził migrację 500K LOC kodu Java do Pythona, skracając czas wdrożenia o 60%."',
        icon: 'layers',
      },
      {
        title: 'Brak struktury',
        description:
          'Grafy wiedzy rejestrują byty i relacje, ale pomijają narrację. Kontekst bez historii to tylko szum.',
        icon: 'grid',
      },
      {
        title: 'Powtarzasz się',
        description:
          'Każda rozmowa z Claude zaczyna się od zera. Kopiuj-wklej te same informacje w tle. Za każdym. Jednym. Razem.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Aktywne Wywiady > Pasywne Przechwytywanie',
    description:
      'Inne narzędzia pamięci obserwują Twoje działania i pasywnie przechowują fragmenty.\n\nMy przeprowadzamy z Tobą wywiady. Systematycznie. Jak dziennikarz budujący profil — zadając pytania uzupełniające, zagłębiając się, śledząc, co zostało omówione, a co nie.\n\nEfekt: uporządkowana, kompleksowa wiedza, którą AI naprawdę POTRAFI WYKORZYSTAĆ, nie tylko odtworzyć.',
    before: {
      label: 'Mem0 przechowuje',
      text: 'użytkownik zna Pythona',
    },
    after: {
      label: 'My przechowujemy',
      text: 'Prowadził migrację na Pythona w Acme Corp (2023). Przekształcił 500K LOC monolitu Java w mikroserwisy Python. Zespół 8 osób. Skrócił czas wdrożenia o 60%. Wybrał FastAPI zamiast Django dla asynchronicznych zadań.',
    },
    closing: 'To różnica między pamięcią a zrozumieniem.',
  },

  howItWorks: {
    heading: 'Jak to działa',
    steps: [
      {
        number: 1,
        title: 'Strukturalne wywiady',
        description:
          'Szybkie rozmowy na Telegramie, które systematycznie obejmują Twoją wiedzę. AI śledzi zakres — wie, o co pytało i czego jeszcze nie. Stopniowe pogłębianie, nie losowe fragmenty.',
      },
      {
        number: 2,
        title: 'Ekstrakcja wiedzy',
        description:
          'AI wydobywa uporządkowane podsumowania z osadzeniami semantycznymi. Organizowane według obszarów życia, wyszukiwane po znaczeniu, nie tylko słowach kluczowych.',
      },
      {
        number: 3,
        title: 'Integracja MCP',
        description:
          'Standardowy serwer MCP współpracujący z Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code i dowolnym AI kompatybilnym z MCP. Autoryzacja Bearer token. Konfiguracja w 5 minut.',
      },
    ],
    bonus: {
      title: 'Wkrótce: Aplikacje MCP',
      description:
        'Interaktywny pulpit wiedzy renderowany bezpośrednio w Claude i ChatGPT dzięki nowemu rozszerzeniu MCP Apps.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Dla programistów',
        items: [
          'AI pamięta Twój stos technologiczny, decyzje architektoniczne i wzorce kodowania',
          'Odniesienia do poprzednich projektów w każdej rozmowie',
          'Generuj przykłady kodu używając TWOICH rzeczywistych wzorców',
          'Nigdy więcej nie tłumacz konfiguracji swojego kodu',
        ],
      },
      {
        title: 'Dla konsultantów',
        items: [
          'AI przypomina szczegóły klientów, metodologie, wcześniejsze projekty',
          'Pisanie ofert z odniesieniem do realnego doświadczenia',
          'Nigdy więcej nie powtarzaj informacji w tle',
          'Automatycznie buduj na bazie wcześniejszych rozmów',
        ],
      },
      {
        title: 'Dla wszystkich',
        items: [
          'Listy motywacyjne pisane na podstawie rzeczywistych osiągnięć',
          'Przygotowanie do rozmów z AI, które zna Twoją historię',
          'Profesjonalne CV generowane automatycznie z Twojej wiedzy',
          'Twoje dane, zawsze możliwe do eksportu',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Proste ceny. Bez niespodzianek.',
    tiers: [
      {
        name: 'Darmowy',
        price: null,
        priceLabel: 'Darmowy',
        description: '1 sesja wywiadu + demo wyszukiwania wiedzy.',
        features: ['1 sesja wywiadu', 'Demo wyszukiwania wiedzy'],
        cta: 'Wypróbuj za darmo',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/miesiąc',
        description: 'Pełny dostęp do wywiadów, serwera MCP i generowania CV.',
        features: [
          'Nielimitowane wywiady + ekstrakcja wiedzy',
          'Dostęp do serwera MCP (autoryzacja Bearer token)',
          'Wyszukiwanie semantyczne w całej Twojej wiedzy',
          'Generowanie CV w pakiecie',
          'Działa z Claude, ChatGPT, Cursor, Windsurf',
        ],
        cta: 'Dołącz do Wczesnego Dostępu',
        highlighted: true,
        badge: 'Najpopularniejszy',
      },
      {
        name: 'Self-Hosted',
        price: 59,
        priceLabel: '$59/miesiąc',
        description: 'Wszystko z Knowledge Pro, na Twojej infrastrukturze.',
        features: [
          'Wszystko z Knowledge Pro',
          'Wdrożenie Docker, pełny dostęp do źródeł',
          'Pełna własność danych',
          'Priorytetowe wsparcie',
        ],
        cta: 'Dołącz do Wczesnego Dostępu',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Czym to się różni od Mem0/OpenMemory?',
        answer:
          'Mem0 pasywnie przechwytuje fragmenty z Twoich rozmów z AI. My aktywnie przeprowadzamy wywiady — systematycznie, ze śledzeniem zakresu — wydobywając głęboką, uporządkowaną wiedzę. To różnica między kamerą bezpieczeństwa a wywiadem dziennikarskim.',
      },
      {
        question: 'Czym to się różni od Zep?',
        answer:
          'Zep buduje grafy wiedzy z dokumentów i rozmów. My prowadzimy aktywne, strukturalne wywiady z pytaniami uzupełniającymi i stopniowym pogłębianiem. Nasza wiedza jest bogatsza, bo jest celowo wydobywana, a nie pasywnie obserwowana.',
      },
      {
        question: 'Jakie AI są wspierane?',
        answer:
          'Każde AI kompatybilne z MCP. Potwierdzone: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP to teraz standard branżowy (Linux Foundation).',
      },
      {
        question: 'Czy protokół MCP jest stabilny?',
        answer:
          'MCP jest zarządzany przez Agentic AI Foundation (Linux Foundation) z Anthropic, OpenAI, Google, Microsoft i AWS jako członkami. Utrzymujemy kompatybilność wsteczną.',
      },
      {
        question: 'Czy mogę hostować samodzielnie?',
        answer:
          'Tak. Pakiet Self-Hosted zawiera konfigurację Docker Compose i pełną dokumentację wdrożenia.',
      },
      {
        question: 'Czy mogę eksportować moje dane?',
        answer:
          'Zawsze. Pobieraj swoje dane w formacie JSON/PDF w dowolnym momencie. To Twoje dane.',
      },
      {
        question: 'Jakie metody płatności akceptujecie?',
        answer:
          'Karta kredytowa, Apple Pay, Google Pay przez naszego partnera płatniczego. Akceptujemy też USDC i BTC dla klientów ceniących prywatność.',
      },
    ],
  },

  emailSignup: {
    heading: 'Uzyskaj Wczesny Dostęp',
    subheading: 'Bądź pierwszy, który wypróbuje uporządkowaną pamięć AI.',
    placeholder: 'Wpisz swój email',
    cta: 'Dołącz do Wczesnego Dostępu — Za darmo',
    disclaimer:
      'Zero spamu. Bez karty kredytowej. Tylko powiadomienie o starcie.',
    formAction: formspree.action,
  },
};
