import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title: 'Claude, ChatGPT & Cursor용 AI 장기 기억 | Interview Assistant MCP',
    description:
      '모든 AI 어시스턴트에 구조화된 장기 기억을 제공합니다. 능동적인 인터뷰로 깊은 지식을 추출합니다. MCP 서버는 Claude Desktop, ChatGPT, Cursor 등과 연동됩니다.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline: '모든 AI 어시스턴트에 구조화된 장기 기억을 제공하세요',
    subheadline:
      '그저 수동적으로 기억을 쌓는 게 아닙니다. 능동적인 인터뷰로 깊고 구조화된 지식을 추출합니다. AI가 진짜로 당신의 맥락을 이해합니다.',
    cta: '얼리 액세스 참여하기',
    socialProof: 'Claude, ChatGPT, Cursor, Windsurf 등과 호환',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'AI 기억은 수동적이어선 안 됩니다',
    items: [
      {
        title: '피상적 기록',
        description:
          'Mem0 같은 도구들은 단편만 수동적으로 기록합니다. "사용자가 Python을 선호한다"는 알지만, "50만 LOC Java 코드베이스를 Python으로 이전해 배포 시간을 60% 단축했다"는 모릅니다.',
        icon: 'layers',
      },
      {
        title: '구조 부재',
        description:
          '지식 그래프는 엔티티와 관계를 포착하지만 이야기 흐름은 놓칩니다. 맥락에 이야기가 없으면 그저 잡음일 뿐입니다.',
        icon: 'grid',
      },
      {
        title: '반복되는 설명',
        description:
          'Claude와의 모든 대화는 처음부터 시작됩니다. 같은 배경 정보를 매번 복사해서 붙여넣어야 하죠. 매.번.매.번.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: '능동적 인터뷰 > 수동적 기록',
    description:
      '다른 기억 도구들은 당신의 행동을 관찰하며 단편을 수동적으로 저장합니다.\n\n우리는 당신을 인터뷰합니다. 체계적으로. 마치 기자가 프로필을 작성하듯 — 후속 질문을 하고, 깊이 파고들며, 다뤘던 내용과 다루지 않은 내용을 추적합니다.\n\n결과는 AI가 단순히 검색하는 게 아니라 실제로 활용할 수 있는 구조화되고 포괄적인 지식입니다.',
    before: {
      label: 'Mem0가 저장하는 내용',
      text: '사용자가 Python을 알고 있음',
    },
    after: {
      label: '우리가 저장하는 내용',
      text: '2023년 Acme Corp에서 Python 이전 주도. 50만 LOC Java 모놀리스를 Python 마이크로서비스로 전환. 8인 팀. 배포 시간 60% 단축. 비동기 작업에 FastAPI를 Django 대신 선택.',
    },
    closing: '이것이 기억과 이해의 차이입니다.',
  },

  howItWorks: {
    heading: '작동 방식',
    steps: [
      {
        number: 1,
        title: '구조화된 인터뷰',
        description:
          'Telegram을 통한 빠른 대화로 당신의 지식을 체계적으로 다룹니다. AI가 질문한 내용과 아직 다루지 않은 부분을 추적합니다. 무작위 단편이 아닌 점진적 심화.',
      },
      {
        number: 2,
        title: '지식 추출',
        description:
          'AI가 의미 임베딩을 활용해 구조화된 요약을 추출합니다. 삶의 영역별로 정리되고, 단순 키워드가 아닌 의미로 검색 가능합니다.',
      },
      {
        number: 3,
        title: 'MCP 통합',
        description:
          'Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code 등 MCP 호환 AI와 연동되는 표준 MCP 서버. Bearer 토큰 인증. 5분 설정.',
      },
    ],
    bonus: {
      title: '곧 출시: MCP 앱',
      description:
        '새로운 MCP 앱 확장 기능을 통해 Claude와 ChatGPT 내에서 바로 렌더링되는 인터랙티브 지식 대시보드.',
    },
  },

  benefits: {
    columns: [
      {
        title: '개발자를 위한',
        items: [
          'AI가 당신의 기술 스택, 아키텍처 결정, 코딩 패턴을 기억합니다',
          '과거 프로젝트를 모든 대화에서 참조 가능',
          '당신의 실제 패턴으로 코드 예제 생성',
          '코드베이스 설정을 다시 설명할 필요 없음',
        ],
      },
      {
        title: '컨설턴트를 위한',
        items: [
          'AI가 고객 정보, 방법론, 과거 프로젝트를 기억합니다',
          '실제 경험을 반영한 제안서 작성',
          '배경 정보를 다시 반복할 필요 없음',
          '이전 대화를 자동으로 이어감',
        ],
      },
      {
        title: '모두를 위한',
        items: [
          '실제 성과를 바탕으로 작성된 커버레터',
          '당신의 이야기를 아는 AI와 함께하는 인터뷰 준비',
          '지식 기반으로 자동 생성되는 전문 이력서',
          '데이터는 언제든지 내보낼 수 있음',
        ],
      },
    ],
  },

  pricing: {
    heading: '간단한 가격 정책. 숨겨진 비용 없음.',
    tiers: [
      {
        name: '무료',
        price: null,
        priceLabel: '무료',
        description: '인터뷰 세션 1회 + 지식 검색 데모 제공.',
        features: ['인터뷰 세션 1회', '지식 검색 데모'],
        cta: '무료로 사용해보기',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/월',
        description: '인터뷰, MCP 서버, 이력서 생성 기능 완전 제공.',
        features: [
          '무제한 인터뷰 및 지식 추출',
          'MCP 서버 접근 (Bearer 토큰 인증)',
          '전체 지식에 대한 의미 기반 검색',
          '이력서 생성 포함',
          'Claude, ChatGPT, Cursor, Windsurf와 호환',
        ],
        cta: '얼리 액세스 참여하기',
        highlighted: true,
        badge: '가장 인기 있음',
      },
      {
        name: '셀프 호스팅',
        price: 59,
        priceLabel: '$59/월',
        description: 'Knowledge Pro의 모든 기능을 자체 인프라에서 사용.',
        features: [
          'Knowledge Pro의 모든 기능 포함',
          'Docker 배포, 전체 소스 접근 가능',
          '완전한 데이터 소유권',
          '우선 지원',
        ],
        cta: '얼리 액세스 참여하기',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Mem0/OpenMemory와 어떻게 다른가요?',
        answer:
          'Mem0는 AI 대화에서 단편을 수동적으로 캡처합니다. 우리는 체계적으로 인터뷰하며, 다룬 내용과 다루지 않은 내용을 추적해 깊고 구조화된 지식을 추출합니다. 보안 카메라와 기자 인터뷰의 차이라고 생각하세요.',
      },
      {
        question: 'Zep과는 어떻게 다른가요?',
        answer:
          'Zep은 문서와 대화에서 지식 그래프를 만듭니다. 우리는 후속 질문과 점진적 심화를 포함한 능동적 구조화 인터뷰를 진행합니다. 우리의 지식은 의도적으로 추출되어 더 풍부합니다.',
      },
      {
        question: '어떤 AI를 지원하나요?',
        answer:
          '모든 MCP 호환 AI를 지원합니다. 확인된 지원 대상: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP는 현재 업계 표준입니다 (Linux Foundation).',
      },
      {
        question: 'MCP 프로토콜은 안정적인가요?',
        answer:
          'MCP는 Agentic AI Foundation (Linux Foundation)이 관리하며 Anthropic, OpenAI, Google, Microsoft, AWS가 회원사입니다. 하위 호환성을 유지합니다.',
      },
      {
        question: '셀프 호스팅이 가능한가요?',
        answer:
          '네. 셀프 호스팅 플랜에는 Docker Compose 설정과 완전한 배포 문서가 포함되어 있습니다.',
      },
      {
        question: '데이터를 내보낼 수 있나요?',
        answer:
          '언제든 가능합니다. JSON/PDF 형식으로 데이터를 다운로드하세요. 데이터는 항상 당신의 것입니다.',
      },
      {
        question: '어떤 결제 수단을 지원하나요?',
        answer:
          '신용카드, Apple Pay, Google Pay를 결제 파트너를 통해 지원합니다. 또한 프라이버시를 중시하는 고객을 위해 USDC와 BTC도 받습니다.',
      },
    ],
  },

  emailSignup: {
    heading: '얼리 액세스 받기',
    subheading: '구조화된 AI 기억을 가장 먼저 경험하세요.',
    placeholder: '이메일 입력',
    cta: '얼리 액세스 참여 — 무료',
    disclaimer: '스팸 없음. 신용카드 정보 필요 없음. 출시 알림만 드립니다.',
    formAction: formspree.action,
  },
};
