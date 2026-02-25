import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'Claude, ChatGPT & Cursor için Yapay Zeka Uzun Süreli Hafıza | Interview Assistant MCP',
    description:
      'Herhangi bir yapay zeka asistanına yapılandırılmış uzun süreli hafıza kazandırın. Aktif görüşmeler derin bilgi çıkarır. MCP sunucusu Claude Desktop, ChatGPT, Cursor ve daha fazlasıyla çalışır.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline:
      'HERHANGİ BİR Yapay Zeka Asistanına Yapılandırılmış Uzun Süreli Hafıza Verin',
    subheadline:
      'Bir başka pasif hafıza yığını değil. Aktif görüşmeler derin, yapılandırılmış bilgi çıkarır. Yapay zekanız gerçekten bağlamınızı anlar.',
    cta: 'Erken Erişime Katıl',
    socialProof: 'Claude, ChatGPT, Cursor, Windsurf ve daha fazlasıyla çalışır',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Yapay Zeka Hafızası Pasif Olmamalı',
    items: [
      {
        title: 'Yüzeysel kayıt',
        description:
          'Mem0 gibi araçlar parçaları pasif şekilde kaydeder. "Kullanıcı Python tercih ediyor" alırsınız, "500K LOC Java kod tabanını Python\'a taşıdı, dağıtım süresini %60 azalttı" değil.',
        icon: 'layers',
      },
      {
        title: 'Yapısız bilgi',
        description:
          'Bilgi grafikleri varlıkları ve ilişkileri yakalar ama anlatıyı kaçırır. Hikayesiz bağlam sadece gürültüdür.',
        icon: 'grid',
      },
      {
        title: 'Kendinizi tekrar ediyorsunuz',
        description:
          'Her Claude sohbeti sıfırdan başlar. Aynı arka planı kopyala-yapıştır yaparsınız. Her. Tek. Seferde.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Aktif Görüşmeler > Pasif Kayıt',
    description:
      'Diğer hafıza araçları yaptıklarınızı izler ve parçaları pasif şekilde depolar.\n\nBiz sizi sistematik olarak röportaj yaparız. Bir profil oluşturan gazeteci gibi — takip soruları sorar, derinleşir, nelerin kapsandığını ve nelerin kapsanmadığını takip eder.\n\nSonuç: Yapay zekanın sadece erişmekle kalmayıp GERÇEKTEN KULLANABİLECEĞİ yapılandırılmış, kapsamlı bilgi.',
    before: {
      label: 'Mem0 depolar',
      text: 'kullanıcı Python biliyor',
    },
    after: {
      label: 'Biz depoluyoruz',
      text: "Acme Corp'ta Python geçişini yönetti (2023). 500K LOC Java monoliti Python mikroservislerine dönüştürdü. 8 kişilik ekip. Dağıtım süresini %60 azalttı. Asenkron işler için Django yerine FastAPI seçildi.",
    },
    closing: 'İşte hafıza ile anlama arasındaki fark bu.',
  },

  howItWorks: {
    heading: 'Nasıl Çalışır',
    steps: [
      {
        number: 1,
        title: 'Yapılandırılmış Görüşmeler',
        description:
          'Bilginizi sistematik şekilde kapsayan hızlı Telegram sohbetleri. Yapay zeka kapsama alanını takip eder — ne sorulduğunu ve ne sorulmadığını bilir. Rastgele parçalar değil, aşamalı derinleşme.',
      },
      {
        number: 2,
        title: 'Bilgi Çıkarımı',
        description:
          'Yapay zeka anlamsal gömme yöntemleriyle yapılandırılmış özetler çıkarır. Hayat alanlarına göre organize edilir, sadece anahtar kelimelerle değil anlamıyla aranabilir.',
      },
      {
        number: 3,
        title: 'MCP Entegrasyonu',
        description:
          'Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code ve MCP uyumlu tüm yapay zekalarla çalışan standart MCP sunucusu. Bearer token kimlik doğrulama. 5 dakikalık kurulum.',
      },
    ],
    bonus: {
      title: 'Yakında: MCP Uygulamaları',
      description:
        'Yeni MCP Uygulamaları eklentisiyle Claude ve ChatGPT içinde doğrudan görüntülenen etkileşimli bilgi panosu.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Geliştiriciler İçin',
        items: [
          'Yapay zeka teknoloji yığını, mimari kararlar ve kodlama kalıplarınızı hatırlar',
          'Geçmiş projelere herhangi bir sohbette referans verin',
          'Kendi gerçek kalıplarınızla kod örnekleri oluşturun',
          'Kod tabanınızın kurulumunu asla tekrar açıklamak zorunda kalmayın',
        ],
      },
      {
        title: 'Danışmanlar İçin',
        items: [
          'Yapay zeka müşteri detaylarını, metodolojileri, önceki projeleri hatırlar',
          'Gerçek deneyime dayalı teklifler yazın',
          'Arka plan bilgilerini bir daha asla tekrar etmeyin',
          'Önceki sohbetlerin üzerine otomatik olarak inşa edin',
        ],
      },
      {
        title: 'Herkes İçin',
        items: [
          'Gerçek başarılarınızdan yazılmış ön yazılar',
          'Hikayenizi bilen yapay zeka ile mülakat hazırlığı',
          'Bilginizden otomatik oluşturulan profesyonel özgeçmiş',
          'Verileriniz her zaman dışa aktarılabilir',
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
        description: '1 görüşme oturumu + bilgi arama demosu.',
        features: ['1 görüşme oturumu', 'Bilgi arama demosu'],
        cta: 'Ücretsiz Deneyin',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/ay',
        description:
          'Görüşmelere, MCP sunucusuna ve CV oluşturma özelliğine tam erişim.',
        features: [
          'Sınırsız görüşme + bilgi çıkarımı',
          'MCP sunucu erişimi (Bearer token kimlik doğrulama)',
          'Tüm bilginizde anlamsal arama',
          'CV oluşturma dahil',
          'Claude, ChatGPT, Cursor, Windsurf ile çalışır',
        ],
        cta: 'Erken Erişime Katıl',
        highlighted: true,
        badge: 'En Popüler',
      },
      {
        name: 'Kendi Sunucunuzda',
        price: 59,
        priceLabel: '$59/ay',
        description: "Knowledge Pro'daki her şey, kendi altyapınızda.",
        features: [
          "Knowledge Pro'daki her şey",
          'Docker dağıtımı, tam kaynak erişimi',
          'Tam veri sahipliği',
          'Öncelikli destek',
        ],
        cta: 'Erken Erişime Katıl',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: "Bu Mem0/OpenMemory'den nasıl farklı?",
        answer:
          'Mem0 yapay zeka sohbetlerinizden parçaları pasif şekilde yakalar. Biz sizi aktif şekilde röportaj yaparız — sistematik, kapsama takibi ile — derin yapılandırılmış bilgi çıkarırız. Bu, güvenlik kamerası ile gazeteci röportajı arasındaki fark gibi.',
      },
      {
        question: "Bu Zep'ten nasıl farklı?",
        answer:
          'Zep belgeler ve sohbetlerden bilgi grafikleri oluşturur. Biz takip soruları ve aşamalı derinleşmeyle aktif yapılandırılmış görüşmeler yaparız. Bilgimiz daha zengindir çünkü kasıtlı olarak çıkarılır, pasif şekilde gözlemlenmez.',
      },
      {
        question: 'Hangi yapay zekalar destekleniyor?',
        answer:
          'Her MCP uyumlu yapay zeka. Onaylananlar: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP artık sektör standardı (Linux Foundation).',
      },
      {
        question: 'MCP protokolü stabil mi?',
        answer:
          'MCP, Anthropic, OpenAI, Google, Microsoft ve AWS üyeliğinde Agentic AI Foundation (Linux Foundation) tarafından yönetilir. Geriye dönük uyumluluğu koruyoruz.',
      },
      {
        question: 'Kendi sunucumda barındırabilir miyim?',
        answer:
          'Evet. Kendi Sunucunuzda paketi Docker Compose kurulumu ve tam dağıtım dokümantasyonu içerir.',
      },
      {
        question: 'Verilerimi dışa aktarabilir miyim?',
        answer:
          'Her zaman. Verilerinizi JSON/PDF olarak istediğiniz zaman indirin. Size ait.',
      },
      {
        question: 'Hangi ödeme yöntemlerini kabul ediyorsunuz?',
        answer:
          'Ödeme ortağımız aracılığıyla kredi kartı, Apple Pay, Google Pay. Gizliliğe önem veren müşteriler için USDC ve BTC de kabul ediyoruz.',
      },
    ],
  },

  emailSignup: {
    heading: 'Erken Erişim Alın',
    subheading: 'Yapılandırılmış yapay zeka hafızasını ilk deneyen siz olun.',
    placeholder: 'E-posta adresinizi girin',
    cta: 'Erken Erişime Katıl — Ücretsiz',
    disclaimer: 'Spam yok. Kredi kartı yok. Sadece lansman haberleri.',
    formAction: formspree.action,
  },
};
