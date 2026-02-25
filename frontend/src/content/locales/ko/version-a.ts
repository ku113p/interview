import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'AI 커리어 코치 - 15분 만에 완성하는 전문 이력서 | Interview Assistant',
    description:
      '자연스럽게 대화하고, 전문 ATS 최적화 이력서를 받으세요. AI가 커리어 코치처럼 인터뷰하며 성과를 추출하고 다듬어진 이력서를 생성합니다. 무료 플랜 제공.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: '당신의 AI 커리어 코치.<br>15분 만에 완벽한 이력서.',
    subheadline:
      '경험에 대해 자연스럽게 이야기하세요. AI가 커리어 코치처럼 인터뷰하며 성과를 추출하고 ATS 최적화된 전문 이력서를 자동으로 만들어 드립니다.',
    cta: '무료로 체험하기',
    socialProof: '50명 이상의 전문가가 대기 중',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: '이런 경험 있으신가요?',
    items: [
      {
        title: '가장 뛰어난 성과를 잊어버리세요',
        description:
          '"3년 전 그 직장에서 뭘 이뤘더라?" 멋진 성과가 있지만 압박감 속에 제대로 표현하지 못합니다.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT는 흔한 문구만 줘요',
        description:
          '정보를 붙여넣으면 ChatGPT가 "성과 중심의 검증된 전문가" 같은 평범한 문장을 만듭니다. 채용 담당자는 금방 알아챕니다.',
        icon: 'sparkles',
      },
      {
        title: '업데이트에 몇 시간이 걸려요',
        description:
          '지원할 때마다 포맷을 다시 맞추고, 다시 써야 하며 ATS가 거부하지 않길 바랄 뿐입니다. 더 중요한 일이 많지 않나요?',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT는 이력서를 씁니다.<br>우리는 당신만의 이력서를 만듭니다.',
    description:
      'ChatGPT는 주어진 문장을 다듬을 수 있습니다. 하지만 대부분 사람들은 자신의 성과를 잘 표현하지 못하죠.\n\n우리 AI는 커리어 코치처럼 인터뷰하며 후속 질문을 던지고, 수치화된 성과를 끌어내며, 당신이 잊을 만한 부분까지 잡아냅니다.',
    before: {
      label: '일반적인 ChatGPT 출력',
      text: '개발 팀을 관리함',
    },
    after: {
      label: '인터뷰로 추출한 출력',
      text: '12명 엔지니어 팀을 이끌어 3주 앞당겨 200만 달러 규모 플랫폼 마이그레이션 완료',
    },
    closing:
      '당신은 이미 이 내용을 알고 있습니다. 단지 올바른 질문을 받을 필요가 있을 뿐입니다.',
  },

  howItWorks: {
    heading: '15분이면 충분합니다.',
    steps: [
      {
        number: 1,
        title: '간단한 대화',
        description:
          'Telegram 봇과 10~15분간 대화하세요. 경험, 프로젝트, 기술에 대해 자연스럽게 이야기하면 커리어 코치처럼 똑똑한 후속 질문을 던집니다.',
      },
      {
        number: 2,
        title: 'AI 추출',
        description:
          'AI가 성과를 추출하고, 영향력을 수치화하며, 핵심 기술을 파악해 체계적인 경력 데이터로 정리합니다. 놓치는 게 없습니다.',
      },
      {
        number: 3,
        title: '전문 이력서',
        description:
          '다듬어진 ATS 최적화 PDF 이력서를 받으세요. 올바른 포맷, 키워드 풍부, 자동 심사 통과 가능. 모든 지원에 준비 완료.',
      },
    ],
    bonus: {
      title: '보너스: AI 메모리',
      description:
        'Claude, ChatGPT, Cursor 같은 AI 어시스턴트가 언제든 경력 기록을 조회할 수 있습니다. 몇 초 만에 자기소개서 작성, 실제 경험으로 면접 준비 가능.',
    },
  },

  benefits: {
    columns: [
      {
        title: '커리어 코치처럼',
        items: [
          '가이드 인터뷰로 최고의 성과를 끌어냄',
          '스스로 생각하지 못한 후속 질문 제공',
          '수치화된 성과를 자동으로 포착',
          '5분 후속 세션으로 업데이트 가능',
        ],
      },
      {
        title: 'ATS 최적화',
        items: [
          '자동 심사 통과(75% 이력서가 탈락하는 곳)',
          '산업별 키워드가 풍부한 내용',
          'ATS가 인식하는 깔끔한 포맷',
          '채용 담당자가 기대하는 전문 레이아웃',
        ],
      },
      {
        title: '항상 최신 상태',
        items: [
          '빠른 채팅으로 언제든 새 경험 추가',
          '다양한 역할에 맞춘 맞춤 버전 생성',
          '즉시 PDF로 내보내기',
          '내 데이터, 내 통제, 언제든 내보내기 가능',
        ],
      },
    ],
  },

  pricing: {
    heading: '간단한 가격, 숨겨진 비용 없음.',
    tiers: [
      {
        name: '무료',
        price: null,
        priceLabel: '무료',
        description: '내게 맞는지 확인해 보세요. 신용카드 불필요.',
        features: ['1회 인터뷰 세션', '1회 이력서 생성'],
        cta: '무료로 체험하기',
        highlighted: false,
      },
      {
        name: 'CV Pro — 평생 이용',
        price: 79,
        priceLabel: '$79 일회성 결제',
        description: '한 번 결제하면 평생 사용 가능. 창립 멤버 가격.',
        features: [
          '무제한 인터뷰 및 이력서 생성',
          'ATS 최적화 PDF 내보내기',
          '여러 이력서 버전',
          'Telegram 봇 접근',
        ],
        cta: '평생 이용권 예약하기',
        highlighted: true,
        badge: '최고 가치',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'ChatGPT와 어떻게 다른가요?',
        answer:
          'ChatGPT는 이미 가진 문장을 다듬습니다. 우리는 인터뷰를 통해 후속 질문을 던지고 구체적인 내용을 끌어내며, 잊기 쉬운 성과까지 잡아냅니다. 커리어 코치처럼, 단순한 텍스트 편집기가 아닙니다. 결과는 더 풍부하고 구체적이며 당신만의 것입니다.',
      },
      {
        question: '이력서가 ATS 친화적인가요?',
        answer:
          '네. 깔끔한 포맷, 올바른 제목 계층, 키워드가 풍부한 내용으로 75%가 탈락하는 자동 심사 시스템을 통과하도록 설계되었습니다.',
      },
      {
        question: '기술적 스킬이 필요하나요?',
        answer:
          '아니요. Telegram만 사용할 수 있으면 됩니다. 자연스럽게 대화하세요. AI 어시스턴트 기능(Claude/ChatGPT 메모리)은 기술 사용자에게 추가 혜택입니다.',
      },
      {
        question: '무료 플랜은 어떻게 작동하나요?',
        answer:
          '인터뷰 1회 세션과 이력서 1회 생성이 완전 무료입니다. 신용카드 불필요. 마음에 들면 계속 생성 및 업데이트를 위해 업그레이드하세요.',
      },
      {
        question: '내 데이터를 내보낼 수 있나요?',
        answer:
          '언제든 가능합니다. JSON/PDF 형식으로 데이터를 다운로드하세요. 데이터는 당신의 것입니다.',
      },
      {
        question: '결제 수단은 무엇을 받나요?',
        answer:
          '결제 파트너를 통해 신용카드, Apple Pay, Google Pay를 받습니다. 개인정보 보호를 원하는 고객을 위해 USDC와 BTC도 지원합니다.',
      },
      {
        question: '마음에 들지 않으면 어떻게 하나요?',
        answer:
          '언제든 취소 가능합니다. 월 구독은 약정 없으며, 평생 이용권은 30일 환불 보장됩니다.',
      },
    ],
  },

  emailSignup: {
    heading: '얼리 액세스 받기',
    subheading: '출시 시 무료 플랜 제공. 가장 먼저 체험하세요.',
    placeholder: '이메일 입력',
    cta: '대기자 명단 가입 — 무료',
    disclaimer: '스팸 없음. 신용카드 불필요. 출시 알림만 받습니다.',
    formAction: formspree.action,
  },
};
