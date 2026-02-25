import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'Memori Jangka Panjang AI untuk Claude, ChatGPT & Cursor | Interview Assistant MCP',
    description:
      'Berikan memori jangka panjang terstruktur untuk asisten AI apa pun. Wawancara aktif menggali pengetahuan mendalam. Server MCP bekerja dengan Claude Desktop, ChatGPT, Cursor, dan lainnya.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline:
      'Berikan Memori Jangka Panjang Terstruktur untuk ASISTEN AI Apa Pun',
    subheadline:
      'Bukan sekadar tumpukan memori pasif. Wawancara aktif menggali pengetahuan mendalam dan terstruktur. AI Anda benar-benar memahami konteks Anda.',
    cta: 'Gabung Akses Awal',
    socialProof: 'Bekerja dengan Claude, ChatGPT, Cursor, Windsurf & lainnya',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Memori AI Tidak Boleh Pasif',
    items: [
      {
        title: 'Penangkapan dangkal',
        description:
          'Alat seperti Mem0 merekam fragmen secara pasif. Anda dapat "pengguna suka Python" bukan "memimpin migrasi 500K LOC kode Java ke Python, mengurangi waktu deploy 60%."',
        icon: 'layers',
      },
      {
        title: 'Tanpa struktur',
        description:
          'Graf pengetahuan menangkap entitas dan hubungan tapi kehilangan narasi. Konteks tanpa cerita hanyalah kebisingan.',
        icon: 'grid',
      },
      {
        title: 'Anda mengulang diri sendiri',
        description:
          'Setiap percakapan dengan Claude dimulai dari nol. Salin-tempel latar belakang yang sama. Setiap. Saat.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Wawancara Aktif > Penangkapan Pasif',
    description:
      'Alat memori lain mengamati apa yang Anda lakukan dan menyimpan fragmen secara pasif.\n\nKami mewawancarai Anda. Sistematis. Seperti jurnalis yang membangun profil — bertanya lanjutan, menggali lebih dalam, melacak apa yang sudah dan belum dibahas.\n\nHasilnya: pengetahuan terstruktur dan komprehensif yang AI benar-benar BISA GUNAKAN, bukan hanya diambil kembali.',
    before: {
      label: 'Mem0 menyimpan',
      text: 'pengguna tahu Python',
    },
    after: {
      label: 'Kami menyimpan',
      text: 'Memimpin migrasi Python di Acme Corp (2023). Mengonversi monolitik Java 500K LOC ke microservices Python. Tim 8 orang. Mengurangi waktu deploy 60%. Memilih FastAPI daripada Django untuk beban kerja async.',
    },
    closing: 'Itulah perbedaan antara memori dan pemahaman.',
  },

  howItWorks: {
    heading: 'Cara Kerjanya',
    steps: [
      {
        number: 1,
        title: 'Wawancara Terstruktur',
        description:
          'Percakapan cepat di Telegram yang secara sistematis mencakup pengetahuan Anda. AI melacak cakupan — tahu apa yang sudah ditanyakan dan belum. Pendalaman progresif, bukan fragmen acak.',
      },
      {
        number: 2,
        title: 'Ekstraksi Pengetahuan',
        description:
          'AI mengekstrak ringkasan terstruktur dengan embedding semantik. Diatur berdasarkan area kehidupan, dapat dicari berdasarkan makna, bukan hanya kata kunci.',
      },
      {
        number: 3,
        title: 'Integrasi MCP',
        description:
          'Server MCP standar yang bekerja dengan Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code, dan AI kompatibel MCP lainnya. Autentikasi Bearer token. Setup 5 menit.',
      },
    ],
    bonus: {
      title: 'Segera Hadir: Aplikasi MCP',
      description:
        'Dashboard pengetahuan interaktif yang ditampilkan langsung di dalam Claude dan ChatGPT melalui ekstensi MCP Apps baru.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Untuk Pengembang',
        items: [
          'AI mengingat tumpukan teknologi, keputusan arsitektur, dan pola coding Anda',
          'Referensi proyek masa lalu dalam setiap percakapan',
          'Hasilkan contoh kode menggunakan pola ASLI ANDA',
          'Tidak perlu jelaskan ulang pengaturan kode Anda',
        ],
      },
      {
        title: 'Untuk Konsultan',
        items: [
          'AI mengingat detail klien, metodologi, keterlibatan sebelumnya',
          'Tulis proposal dengan referensi pengalaman nyata',
          'Tidak perlu ulangi info latar belakang lagi',
          'Bangun dari percakapan sebelumnya secara otomatis',
        ],
      },
      {
        title: 'Untuk Semua Orang',
        items: [
          'Surat lamaran dibuat dari pencapaian nyata',
          'Persiapan wawancara dengan AI yang tahu cerita Anda',
          'Resume profesional otomatis dari pengetahuan Anda',
          'Data Anda, selalu bisa diekspor',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Harga Sederhana. Tanpa Kejutan.',
    tiers: [
      {
        name: 'Gratis',
        price: null,
        priceLabel: 'Gratis',
        description: '1 sesi wawancara + demo pencarian pengetahuan.',
        features: ['1 sesi wawancara', 'Demo pencarian pengetahuan'],
        cta: 'Coba Gratis',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/bulan',
        description: 'Akses penuh ke wawancara, server MCP, dan pembuatan CV.',
        features: [
          'Wawancara tak terbatas + ekstraksi pengetahuan',
          'Akses server MCP (autentikasi Bearer token)',
          'Pencarian semantik di seluruh pengetahuan Anda',
          'Termasuk pembuatan CV',
          'Bekerja dengan Claude, ChatGPT, Cursor, Windsurf',
        ],
        cta: 'Gabung Akses Awal',
        highlighted: true,
        badge: 'Paling Populer',
      },
      {
        name: 'Self-Hosted',
        price: 59,
        priceLabel: '$59/bulan',
        description: 'Semua di Knowledge Pro, di infrastruktur Anda sendiri.',
        features: [
          'Semua di Knowledge Pro',
          'Deployment Docker, akses sumber lengkap',
          'Kepemilikan data penuh',
          'Dukungan prioritas',
        ],
        cta: 'Gabung Akses Awal',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Apa bedanya dengan Mem0/OpenMemory?',
        answer:
          'Mem0 menangkap fragmen secara pasif dari percakapan AI Anda. Kami mewawancarai Anda secara aktif — sistematis, dengan pelacakan cakupan — mengekstrak pengetahuan terstruktur yang mendalam. Ini seperti perbedaan antara kamera pengawas dan wawancara jurnalis.',
      },
      {
        question: 'Apa bedanya dengan Zep?',
        answer:
          'Zep membangun graf pengetahuan dari dokumen dan percakapan. Kami melakukan wawancara terstruktur aktif dengan pertanyaan lanjutan dan pendalaman progresif. Pengetahuan kami lebih kaya karena sengaja diekstrak, bukan hanya diamati pasif.',
      },
      {
        question: 'AI mana saja yang didukung?',
        answer:
          'AI kompatibel MCP apa pun. Terkonfirmasi: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP kini standar industri (Linux Foundation).',
      },
      {
        question: 'Apakah protokol MCP stabil?',
        answer:
          'MCP diatur oleh Agentic AI Foundation (Linux Foundation) dengan Anthropic, OpenAI, Google, Microsoft, dan AWS sebagai anggota. Kami menjaga kompatibilitas mundur.',
      },
      {
        question: 'Bisakah saya self-host?',
        answer:
          'Bisa. Tier Self-Hosted termasuk setup Docker Compose dan dokumentasi deployment lengkap.',
      },
      {
        question: 'Bisakah saya ekspor data saya?',
        answer:
          'Selalu. Unduh data Anda dalam format JSON/PDF kapan saja. Itu milik Anda.',
      },
      {
        question: 'Metode pembayaran apa yang diterima?',
        answer:
          'Kartu kredit, Apple Pay, Google Pay melalui mitra pembayaran kami. Kami juga menerima USDC dan BTC untuk pelanggan yang peduli privasi.',
      },
    ],
  },

  emailSignup: {
    heading: 'Dapatkan Akses Awal',
    subheading: 'Jadilah yang pertama mencoba memori AI terstruktur.',
    placeholder: 'Masukkan email Anda',
    cta: 'Gabung Akses Awal — Gratis',
    disclaimer:
      'Tanpa spam. Tanpa kartu kredit. Hanya pemberitahuan saat kami meluncur.',
    formAction: formspree.action,
  },
};
