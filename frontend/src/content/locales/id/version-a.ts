import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'Pelatih Karir AI - Resume Profesional dalam 15 Menit | Interview Assistant',
    description:
      'Berbicara secara alami, dapatkan resume profesional yang dioptimalkan untuk ATS. AI mewawancarai Anda seperti pelatih karir, mengekstrak pencapaian, menghasilkan CV yang rapi. Tier gratis.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: 'Pelatih Karir AI Anda.<br>Resume Sempurna dalam 15 Menit.',
    subheadline:
      'Bicarakan pengalaman Anda secara alami. AI mewawancarai Anda seperti pelatih karir, mengekstrak pencapaian Anda, dan secara otomatis menghasilkan resume profesional yang dioptimalkan untuk ATS.',
    cta: 'Coba Gratis',
    socialProof: 'Bergabung dengan 50+ profesional dalam daftar tunggu',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Kedengarannya Familiar?',
    items: [
      {
        title: 'Anda lupa pekerjaan terbaik Anda',
        description:
          '"Apa yang saya capai di pekerjaan itu 3 tahun lalu?" Anda melakukan hal luar biasa tapi sulit mengungkapkannya saat tekanan.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT memberikan hasil yang umum',
        description:
          'Anda menempelkan info Anda, ChatGPT menulis "profesional berorientasi hasil dengan rekam jejak terbukti." Perekrut langsung bisa melihatnya.',
        icon: 'sparkles',
      },
      {
        title: 'Memperbarui butuh waktu berjam-jam',
        description:
          'Setiap lamaran berarti mengubah format, menulis ulang, dan berharap ATS tidak menolak Anda. Anda punya hal lebih penting untuk dilakukan.',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT Menulis Resume.<br>Kami Menulis Resume ANDA.',
    description:
      'ChatGPT bisa memperbaiki teks yang Anda berikan. Tapi kebanyakan orang sulit mengungkapkan pencapaian mereka dengan baik.\n\nAI kami mewawancarai Anda seperti pelatih karir — mengajukan pertanyaan lanjutan, menggali dampak yang terukur, menangkap hal-hal yang mungkin terlupakan.',
    before: {
      label: 'Output Umum ChatGPT',
      text: 'Memimpin tim pengembangan',
    },
    after: {
      label: 'Output dari Wawancara AI',
      text: 'Memimpin tim engineering 12 orang yang menyelesaikan migrasi platform senilai $2M 3 minggu lebih cepat dari jadwal',
    },
    closing:
      'Anda sudah tahu hal-hal ini. Anda hanya butuh seseorang yang mengajukan pertanyaan tepat.',
  },

  howItWorks: {
    heading: '15 Menit. Itu Saja.',
    steps: [
      {
        number: 1,
        title: 'Percakapan Singkat',
        description:
          'Ngobrol dengan bot Telegram kami selama 10-15 menit. Cukup bicarakan pengalaman, proyek, dan keterampilan Anda secara alami. Bot mengajukan pertanyaan lanjutan cerdas — seperti pelatih karir, bukan formulir.',
      },
      {
        number: 2,
        title: 'Ekstraksi AI',
        description:
          'AI kami mengekstrak pencapaian, mengukur dampak, mengidentifikasi keterampilan utama, dan mengorganisir semuanya menjadi data karir terstruktur. Tidak ada yang terlewat.',
      },
      {
        number: 3,
        title: 'Resume Profesional',
        description:
          'Dapatkan resume PDF yang rapi dan dioptimalkan untuk ATS. Format tepat, kaya kata kunci, lolos penyaringan otomatis. Siap untuk lamaran pekerjaan apa pun.',
      },
    ],
    bonus: {
      title: 'Bonus: Memori AI',
      description:
        'Asisten AI Anda (Claude, ChatGPT, Cursor) kini bisa mengakses riwayat karir Anda kapan saja. Tulis surat lamaran dalam hitungan detik. Persiapkan wawancara dengan pengalaman nyata Anda.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Seperti Pelatih Karir',
        items: [
          'Wawancara terarah menggali karya terbaik Anda',
          'Pertanyaan lanjutan yang tidak terpikirkan sendiri',
          'Menangkap pencapaian terukur secara otomatis',
          'Pembaruan dalam sesi lanjutan 5 menit',
        ],
      },
      {
        title: 'Dioptimalkan untuk ATS',
        items: [
          'Lolos penyaringan otomatis (75% resume tidak lolos)',
          'Konten kaya kata kunci sesuai industri Anda',
          'Format bersih yang dapat dibaca sistem ATS',
          'Tata letak profesional yang diharapkan perekrut',
        ],
      },
      {
        title: 'Selalu Terbaru',
        items: [
          'Tambahkan pengalaman baru kapan saja lewat chat cepat',
          'Buat versi resume yang disesuaikan untuk berbagai peran',
          'Ekspor ke PDF secara instan',
          'Data Anda, kendali Anda, bisa diekspor kapan saja',
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
        description:
          'Coba dan lihat apakah cocok untuk Anda. Tanpa kartu kredit.',
        features: ['1 sesi wawancara', '1 kali pembuatan resume'],
        cta: 'Coba Gratis',
        highlighted: false,
      },
      {
        name: 'CV Pro — Seumur Hidup',
        price: 79,
        priceLabel: '$79 sekali bayar',
        description: 'Bayar sekali, gunakan selamanya. Harga anggota pendiri.',
        features: [
          'Wawancara dan pembuatan resume tanpa batas',
          'Ekspor PDF dioptimalkan untuk ATS',
          'Beberapa versi resume',
          'Akses bot Telegram',
        ],
        cta: 'Pesan Akses Seumur Hidup',
        highlighted: true,
        badge: 'Nilai Terbaik',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Apa bedanya dengan ChatGPT?',
        answer:
          'ChatGPT memperbaiki teks yang sudah Anda punya. Kami mewawancarai Anda — mengajukan pertanyaan lanjutan, menggali detail, menangkap pencapaian yang mungkin terlupakan. Bayangkan seperti pelatih karir, bukan editor teks. Hasilnya lebih kaya, spesifik, dan unik untuk Anda.',
      },
      {
        question: 'Apakah resume ini ramah ATS?',
        answer:
          'Ya. Format bersih, hirarki judul yang tepat, konten kaya kata kunci. Dirancang untuk lolos sistem penyaringan otomatis yang menolak 75% resume.',
      },
      {
        question: 'Apakah saya perlu keterampilan teknis?',
        answer:
          'Tidak. Jika Anda bisa menggunakan Telegram, Anda bisa menggunakan ini. Cukup ngobrol secara alami. Fitur memori asisten AI (Claude/ChatGPT) adalah bonus untuk pengguna teknis.',
      },
      {
        question: 'Bagaimana cara kerja tier gratis?',
        answer:
          'Satu sesi wawancara penuh dan satu pembuatan resume, sepenuhnya gratis. Tanpa kartu kredit. Jika suka, upgrade untuk terus membuat dan memperbarui.',
      },
      {
        question: 'Bisakah saya mengekspor data saya?',
        answer:
          'Selalu bisa. Unduh data Anda dalam format JSON/PDF kapan saja. Itu milik Anda.',
      },
      {
        question: 'Metode pembayaran apa yang diterima?',
        answer:
          'Kartu kredit, Apple Pay, Google Pay melalui mitra pembayaran kami. Kami juga menerima USDC dan BTC untuk pelanggan yang mengutamakan privasi.',
      },
      {
        question: 'Bagaimana jika saya tidak suka?',
        answer:
          'Bisa batalkan kapan saja. Langganan bulanan tanpa ikatan. Pembelian seumur hidup dilengkapi garansi uang kembali 30 hari.',
      },
    ],
  },

  emailSignup: {
    heading: 'Dapatkan Akses Awal',
    subheading:
      'Tier gratis tersedia saat peluncuran. Jadilah yang pertama mencoba.',
    placeholder: 'Masukkan email Anda',
    cta: 'Gabung Daftar Tunggu — Gratis',
    disclaimer:
      'Tanpa spam. Tanpa kartu kredit. Hanya pemberitahuan saat peluncuran.',
    formAction: formspree.action,
  },
};
