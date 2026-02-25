import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'Yapay Zeka Kariyer Koçu - 15 Dakikada Profesyonel Özgeçmiş | Interview Assistant',
    description:
      'Doğal konuşun, profesyonel ATS uyumlu özgeçmişinizi alın. Yapay zeka, kariyer koçu gibi sizi mülakat yapar, başarılarınızı çıkarır, kusursuz CV oluşturur. Ücretsiz katman.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: 'Yapay Zeka Kariyer Koçunuz.<br>15 Dakikada Mükemmel Özgeçmiş.',
    subheadline:
      'Deneyiminiz hakkında doğal şekilde konuşun. Yapay zeka, kariyer koçu gibi sizi mülakat yapar, başarılarınızı çıkarır ve ATS uyumlu profesyonel özgeçmişi otomatik oluşturur.',
    cta: 'Ücretsiz Deneyin',
    socialProof: '50+ profesyonel bekleme listesine katıldı',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Tanıdık Geliyor Mu?',
    items: [
      {
        title: 'En iyi işlerinizi unutuyorsunuz',
        description:
          '"3 yıl önceki işimde ne başarmıştım?" Harika işler yaptınız ama baskı altında ifade edemiyorsunuz.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT size genel ifadeler verir',
        description:
          'Bilgilerinizi yapıştırırsınız, ChatGPT "sonuç odaklı, kanıtlanmış başarıya sahip profesyonel" yazar. İşe alımcılar bunu hemen anlar.',
        icon: 'sparkles',
      },
      {
        title: 'Güncellemek saatler sürer',
        description:
          "Her başvuru yeniden formatlama, yeniden yazma ve ATS'nin reddetmemesini ummak demek. Siz daha önemli işlerle uğraşmalısınız.",
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT Özgeçmiş Yazar.<br>BİZ SİZİN Özgeçmişinizi Yazarız.',
    description:
      'ChatGPT verdiğiniz metni parlatabilir. Ama çoğu kişi kendi başarılarını iyi ifade edemez.\n\nYapay zekamız sizi kariyer koçu gibi mülakat yapar — takip soruları sorar, ölçülebilir etkileri ortaya çıkarır, unutacağınız şeyleri yakalar.',
    before: {
      label: 'Genel ChatGPT Çıktısı',
      text: 'Bir geliştirme ekibini yönetti',
    },
    after: {
      label: 'Mülakattan Çıkarılan Çıktı',
      text: '12 kişilik mühendislik ekibini yönetti, 3 hafta erken teslim edilen 2M$ değerinde platform geçişi sağladı',
    },
    closing:
      'Bunları zaten biliyorsunuz. Sadece doğru soruları soracak birine ihtiyacınız var.',
  },

  howItWorks: {
    heading: '15 Dakika. Hepsi Bu.',
    steps: [
      {
        number: 1,
        title: 'Hızlı Sohbet',
        description:
          'Telegram botumuzla 10-15 dakika sohbet edin. Deneyiminiz, projeleriniz, becerileriniz hakkında doğal konuşun. Form değil, kariyer koçu gibi akıllı takip soruları sorar.',
      },
      {
        number: 2,
        title: 'Yapay Zeka Çıkartımı',
        description:
          'Yapay zekamız başarıları çıkarır, etkileri ölçer, anahtar becerileri belirler ve her şeyi yapılandırılmış kariyer verisine dönüştürür. Hiçbir şey kaybolmaz.',
      },
      {
        number: 3,
        title: 'Profesyonel Özgeçmiş',
        description:
          'Parlak, ATS uyumlu PDF özgeçmiş alın. Doğru formatlama, anahtar kelime zenginliği, otomatik taramadan geçer. Her iş başvurusu için hazır.',
      },
    ],
    bonus: {
      title: 'Bonus: Yapay Zeka Hafızası',
      description:
        'Yapay zeka asistanlarınız (Claude, ChatGPT, Cursor) artık kariyer geçmişinizi istediğiniz zaman sorgulayabilir. Kapak mektuplarını saniyeler içinde yazın. Gerçek deneyiminizle mülakatlara hazırlanın.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Kariyer Koçu Gibi',
        items: [
          'Yönlendirilmiş mülakat en iyi işlerinizi ortaya çıkarır',
          'Kendinize sormayacağınız takip soruları',
          'Ölçülebilir başarıları otomatik yakalar',
          '5 dakikalık takip seanslarında güncellemeler',
        ],
      },
      {
        title: 'ATS Uyumlu',
        items: [
          'Otomatik taramadan geçer (özgeçmişlerin %75’i geçemez)',
          'Sektörünüze uygun anahtar kelime zenginliği',
          'ATS sistemlerinin okuyabileceği temiz formatlama',
          'İşe alımcıların beklediği profesyonel tasarım',
        ],
      },
      {
        title: 'Her Zaman Güncel',
        items: [
          'Hızlı sohbetle istediğiniz zaman yeni deneyim ekleyin',
          'Farklı roller için özel versiyonlar oluşturun',
          'PDF olarak anında dışa aktarın',
          'Verileriniz sizin kontrolünüzde, istediğiniz zaman dışa aktarılabilir',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Basit Fiyatlandırma. Sürpriz Yok.',
    tiers: [
      {
        name: 'Ücretsiz',
        price: null,
        priceLabel: 'Ücretsiz',
        description: 'Size uygun olup olmadığını görün. Kredi kartı gerekmez.',
        features: ['1 mülakat seansı', '1 özgeçmiş oluşturma'],
        cta: 'Ücretsiz Deneyin',
        highlighted: false,
      },
      {
        name: 'CV Pro — Ömür Boyu',
        price: 79,
        priceLabel: '$79 tek seferlik',
        description: 'Bir kere öde, sonsuza kadar kullan. Kurucu üye fiyatı.',
        features: [
          'Sınırsız mülakat + özgeçmiş oluşturma',
          'ATS uyumlu PDF dışa aktarımı',
          'Birden fazla özgeçmiş versiyonu',
          'Telegram bot erişimi',
        ],
        cta: 'Ömür Boyu Erişimi Rezerve Et',
        highlighted: true,
        badge: 'En İyi Değer',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Bu ChatGPT’den nasıl farklı?',
        answer:
          'ChatGPT zaten sahip olduğunuz metni parlatır. Biz sizi mülakat yaparız — takip soruları sorar, detayları ortaya çıkarır, unutacağınız başarıları yakalar. Kariyer koçu gibi, metin düzenleyici değil. Sonuç daha zengin, daha spesifik ve tamamen size özel.',
      },
      {
        question: 'Özgeçmiş ATS dostu mu?',
        answer:
          'Evet. Temiz formatlama, doğru başlık hiyerarşisi, anahtar kelime zenginliği. Özgeçmişlerin %75’ini reddeden otomatik tarama sistemlerinden geçecek şekilde tasarlandı.',
      },
      {
        question: 'Teknik beceriye ihtiyacım var mı?',
        answer:
          'Hayır. Telegram kullanabiliyorsanız, bunu da kullanabilirsiniz. Sadece doğal sohbet edin. Yapay zeka asistan özellikleri (Claude/ChatGPT hafızası) teknik kullanıcılar için ekstra bir avantajdır.',
      },
      {
        question: 'Ücretsiz katman nasıl çalışıyor?',
        answer:
          'Bir tam mülakat seansı ve bir özgeçmiş oluşturma tamamen ücretsiz. Kredi kartı gerekmez. Beğenirseniz, devam etmek için yükseltebilirsiniz.',
      },
      {
        question: 'Verilerimi dışa aktarabilir miyim?',
        answer:
          'Her zaman. Verilerinizi JSON/PDF olarak istediğiniz zaman indirebilirsiniz. Size ait.',
      },
      {
        question: 'Hangi ödeme yöntemlerini kabul ediyorsunuz?',
        answer:
          'Ödeme ortağımız aracılığıyla kredi kartı, Apple Pay, Google Pay. Gizliliğe önem veren müşteriler için USDC ve BTC de kabul ediyoruz.',
      },
      {
        question: 'Beğenmezsem ne olur?',
        answer:
          'İstediğiniz zaman iptal edin. Aylık aboneliklerde taahhüt yok. Ömür boyu satın almalarda 30 günlük para iade garantisi var.',
      },
    ],
  },

  emailSignup: {
    heading: 'Erken Erişim Alın',
    subheading: 'Lansmanda ücretsiz katman mevcut. İlk deneyen siz olun.',
    placeholder: 'E-posta adresinizi girin',
    cta: 'Bekleme Listesine Katıl — Ücretsiz',
    disclaimer: 'Spam yok. Kredi kartı yok. Sadece lansman bildirimleri.',
    formAction: formspree.action,
  },
};
