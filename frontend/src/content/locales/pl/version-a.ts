import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'AI Career Coach - Profesjonalne CV w 15 minut | Interview Assistant',
    description:
      'Rozmawiaj naturalnie, otrzymaj profesjonalne CV zoptymalizowane pod ATS. AI przeprowadza z Tobą rozmowę jak coach kariery, wydobywa osiągnięcia, generuje dopracowane CV. Darmowy plan.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: 'Twój AI Coach Kariery.<br>Idealne CV w 15 minut.',
    subheadline:
      'Opowiedz naturalnie o swoim doświadczeniu. AI przeprowadza z Tobą rozmowę jak coach kariery, wydobywa Twoje osiągnięcia i automatycznie generuje profesjonalne CV zoptymalizowane pod ATS.',
    cta: 'Wypróbuj za darmo',
    socialProof: 'Dołącz do 50+ profesjonalistów na liście oczekujących',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Brzmi znajomo?',
    items: [
      {
        title: 'Zapominasz o swoich najlepszych osiągnięciach',
        description:
          '"Co osiągnąłem na tym stanowisku 3 lata temu?" Robiłeś świetne rzeczy, ale pod presją trudno Ci je jasno przedstawić.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT daje Ci ogólnikowe frazesy',
        description:
          'Wklejasz swoje dane, a ChatGPT pisze „profesjonalista zorientowany na wyniki i udokumentowanymi sukcesami”. Rekruterzy od razu to wyczują.',
        icon: 'sparkles',
      },
      {
        title: 'Aktualizacja zajmuje godziny',
        description:
          'Każda aplikacja to formatowanie, przepisywanie i modlenie się, by ATS Cię nie odrzucił. Masz ważniejsze rzeczy do zrobienia.',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT pisze CV.<br>My piszemy TWOJE CV.',
    description:
      'ChatGPT potrafi wygładzić tekst, który mu dasz. Ale większość ludzi nie potrafi dobrze opisać własnych osiągnięć.\n\nNasze AI przeprowadza z Tobą rozmowę jak coach kariery — zadaje pytania uzupełniające, wydobywa wymierne efekty, wyłapuje rzeczy, które byś zapomniał.',
    before: {
      label: 'Ogólny tekst z ChatGPT',
      text: 'Zarządzał zespołem deweloperskim',
    },
    after: {
      label: 'Tekst wydobyty w rozmowie',
      text: 'Kierował 12-osobowym zespołem inżynierów, który zrealizował migrację platformy za 2 mln $ na 3 tygodnie przed terminem',
    },
    closing:
      'Ty już to wszystko wiesz. Potrzebujesz tylko kogoś, kto zada właściwe pytania.',
  },

  howItWorks: {
    heading: '15 minut. Tyle wystarczy.',
    steps: [
      {
        number: 1,
        title: 'Szybka rozmowa',
        description:
          'Porozmawiaj z naszym botem na Telegramie przez 10-15 minut. Po prostu opowiedz naturalnie o swoim doświadczeniu, projektach, umiejętnościach. Bot zadaje inteligentne pytania uzupełniające — jak coach kariery, nie formularz.',
      },
      {
        number: 2,
        title: 'Wydobywanie przez AI',
        description:
          'Nasze AI wydobywa osiągnięcia, kwantyfikuje efekty, identyfikuje kluczowe umiejętności i organizuje wszystko w uporządkowane dane kariery. Nic nie ginie.',
      },
      {
        number: 3,
        title: 'Profesjonalne CV',
        description:
          'Otrzymaj dopracowane, zoptymalizowane pod ATS CV w formacie PDF. Poprawne formatowanie, bogate w słowa kluczowe, przechodzi automatyczne selekcje. Gotowe na każdą aplikację.',
      },
    ],
    bonus: {
      title: 'Bonus: Pamięć AI',
      description:
        'Twoi asystenci AI (Claude, ChatGPT, Cursor) mogą teraz w każdej chwili odwołać się do Twojej historii kariery. Pisanie listów motywacyjnych w sekundę. Przygotowanie do rozmów na podstawie Twojego prawdziwego doświadczenia.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Jak coach kariery',
        items: [
          'Prowadzona rozmowa wydobywa Twoje najlepsze osiągnięcia',
          'Pytania uzupełniające, o których sam byś nie pomyślał',
          'Automatyczne wychwytywanie wymiernych sukcesów',
          'Aktualizacje w 5-minutowych sesjach uzupełniających',
        ],
      },
      {
        title: 'Zoptymalizowane pod ATS',
        items: [
          'Przechodzi automatyczne selekcje (75% CV nie przechodzi)',
          'Treść bogata w słowa kluczowe dopasowane do branży',
          'Czyste formatowanie czytelne dla systemów ATS',
          'Profesjonalny układ, którego oczekują rekruterzy',
        ],
      },
      {
        title: 'Zawsze aktualne',
        items: [
          'Dodawaj nowe doświadczenia w każdej chwili przez szybką rozmowę',
          'Generuj wersje CV dopasowane do różnych ról',
          'Eksportuj do PDF natychmiast',
          'Twoje dane, Twoja kontrola, eksportowalne w każdej chwili',
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
        description: 'Sprawdź, czy Ci odpowiada. Bez karty kredytowej.',
        features: ['1 sesja rozmowy', '1 generowanie CV'],
        cta: 'Wypróbuj za darmo',
        highlighted: false,
      },
      {
        name: 'CV Pro — na zawsze',
        price: 79,
        priceLabel: '$79 jednorazowo',
        description:
          'Płać raz, korzystaj na zawsze. Cena dla członków założycieli.',
        features: [
          'Nielimitowane rozmowy i generowanie CV',
          'Eksport PDF zoptymalizowany pod ATS',
          'Wiele wersji CV',
          'Dostęp do bota na Telegramie',
        ],
        cta: 'Zarezerwuj dostęp na zawsze',
        highlighted: true,
        badge: 'Najlepsza oferta',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Czym to się różni od ChatGPT?',
        answer:
          'ChatGPT wygładza tekst, który już masz. My przeprowadzamy z Tobą rozmowę — zadajemy pytania uzupełniające, wydobywamy szczegóły, wyłapujemy osiągnięcia, które byś zapomniał. To jak coach kariery, nie edytor tekstu. Efekt jest bogatszy, bardziej konkretny i unikalnie Twój.',
      },
      {
        question: 'Czy CV jest przyjazne dla ATS?',
        answer:
          'Tak. Czyste formatowanie, właściwa hierarchia nagłówków, treść bogata w słowa kluczowe. Zaprojektowane, by przejść automatyczne systemy selekcji, które odrzucają 75% CV.',
      },
      {
        question: 'Czy potrzebuję umiejętności technicznych?',
        answer:
          'Nie. Jeśli potrafisz korzystać z Telegrama, możesz korzystać z tego narzędzia. Po prostu rozmawiaj naturalnie. Funkcje asystenta AI (pamięć Claude/ChatGPT) to bonus dla użytkowników technicznych.',
      },
      {
        question: 'Jak działa darmowy plan?',
        answer:
          'Jedna pełna sesja rozmowy i jedno generowanie CV całkowicie za darmo. Bez karty kredytowej. Jeśli Ci się spodoba, możesz przejść na płatny plan, by dalej generować i aktualizować CV.',
      },
      {
        question: 'Czy mogę eksportować swoje dane?',
        answer:
          'Zawsze. Pobierz swoje dane w formacie JSON/PDF w dowolnym momencie. To Twoje dane.',
      },
      {
        question: 'Jakie metody płatności akceptujecie?',
        answer:
          'Karta kredytowa, Apple Pay, Google Pay przez naszego partnera płatności. Akceptujemy też USDC i BTC dla klientów ceniących prywatność.',
      },
      {
        question: 'Co jeśli mi się nie spodoba?',
        answer:
          'Anuluj w dowolnym momencie. Subskrypcje miesięczne bez zobowiązań. Zakupy na zawsze mają 30-dniową gwarancję zwrotu pieniędzy.',
      },
    ],
  },

  emailSignup: {
    heading: 'Zyskaj wczesny dostęp',
    subheading:
      'Darmowy plan dostępny od startu. Bądź pierwszy, który wypróbuje.',
    placeholder: 'Wpisz swój email',
    cta: 'Dołącz do listy oczekujących — za darmo',
    disclaimer:
      'Zero spamu. Bez karty kredytowej. Tylko powiadomienie o starcie.',
    formAction: formspree.action,
  },
};
