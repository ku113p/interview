import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title: 'AI 职业教练 - 15 分钟打造专业简历 | Interview Assistant',
    description:
      '自然对话，获得专业 ATS 优化简历。AI 像职业教练一样面试你，提炼成就，生成精致简历。免费套餐可用。',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: '你的 AI 职业教练。<br>15 分钟完成完美简历。',
    subheadline:
      '自然谈论你的经历。AI 像职业教练一样面试你，提炼你的成就，自动生成 ATS 优化的专业简历。',
    cta: '免费试用',
    socialProof: '已有 50+ 专业人士加入候补名单',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: '听起来熟悉吗？',
    items: [
      {
        title: '你忘记了自己的最佳表现',
        description:
          '“三年前那份工作我都做了些什么？”你做了很多了不起的事，但压力下难以表达。',
        icon: 'brain',
      },
      {
        title: 'ChatGPT 给你千篇一律的内容',
        description:
          '你粘贴信息，ChatGPT 写出“结果导向、业绩卓越的专业人士”。招聘官一眼就看穿。',
        icon: 'sparkles',
      },
      {
        title: '更新简历耗时长',
        description:
          '每次申请都要重新排版、重写，还得祈祷 ATS 不拒绝你。你有更重要的事要做。',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT 写简历。<br>我们写你的简历。',
    description:
      'ChatGPT 可以润色你提供的文本。但大多数人难以清晰表达自己的成就。\n\n我们的 AI 像职业教练一样面试你——提出追问，挖掘量化影响，捕捉你可能忘记的细节。',
    before: {
      label: '普通 ChatGPT 输出',
      text: '管理一个开发团队',
    },
    after: {
      label: '面试提炼输出',
      text: '领导一个 12 人工程团队，提前 3 周交付了价值 200 万美元的平台迁移项目',
    },
    closing: '你已经知道这些内容，只是需要有人问对问题。',
  },

  howItWorks: {
    heading: '15 分钟。就这么简单。',
    steps: [
      {
        number: 1,
        title: '快速对话',
        description:
          '通过 Telegram 机器人聊天 10-15 分钟。自然谈论你的经历、项目和技能。它会像职业教练一样提出智能追问，而不是简单表格。',
      },
      {
        number: 2,
        title: 'AI 提炼',
        description:
          '我们的 AI 提炼成就，量化影响，识别关键技能，并将所有内容组织成结构化职业数据。绝不遗漏。',
      },
      {
        number: 3,
        title: '专业简历',
        description:
          '获得一份精致、ATS 优化的 PDF 简历。格式规范、关键词丰富，能通过自动筛选。随时准备好申请任何职位。',
      },
    ],
    bonus: {
      title: '额外福利：AI 记忆',
      description:
        '你的 AI 助手（Claude、ChatGPT、Cursor）随时可查询你的职业历史。几秒钟内写好求职信。用真实经历准备面试。',
    },
  },

  benefits: {
    columns: [
      {
        title: '如同职业教练',
        items: [
          '引导式面试挖掘你的最佳表现',
          '提出你自己想不到的追问',
          '自动捕捉可量化的成就',
          '5 分钟快速跟进更新',
        ],
      },
      {
        title: 'ATS 优化',
        items: [
          '通过自动筛选（75% 简历无法通过）',
          '关键词丰富，匹配你的行业',
          '清晰格式，ATS 系统易解析',
          '招聘官期待的专业排版',
        ],
      },
      {
        title: '始终最新',
        items: [
          '随时通过快速聊天添加新经历',
          '为不同职位生成定制版本',
          '即时导出 PDF',
          '你的数据，你掌控，随时导出',
        ],
      },
    ],
  },

  pricing: {
    heading: '简单定价，无隐藏费用。',
    tiers: [
      {
        name: '免费',
        price: null,
        priceLabel: '免费',
        description: '试试看是否适合你。无需信用卡。',
        features: ['1 次面试', '1 次简历生成'],
        cta: '免费试用',
        highlighted: false,
      },
      {
        name: 'CV Pro — 终身版',
        price: 79,
        priceLabel: '$79 一次性付费',
        description: '一次付费，永久使用。创始会员价。',
        features: [
          '无限面试和简历生成',
          'ATS 优化 PDF 导出',
          '多版本简历',
          'Telegram 机器人访问',
        ],
        cta: '预订终身访问',
        highlighted: true,
        badge: '最佳价值',
      },
    ],
  },

  faq: {
    items: [
      {
        question: '这和 ChatGPT 有什么不同？',
        answer:
          'ChatGPT 只润色你已有的文本。我们面试你——提出追问，挖掘细节，捕捉你可能忘记的成就。更像职业教练，而非文本编辑器。结果更丰富、更具体，独一无二。',
      },
      {
        question: '简历适合 ATS 吗？',
        answer:
          '是的。格式清晰，标题层级合理，关键词丰富。专为通过拒绝 75% 简历的自动筛选系统设计。',
      },
      {
        question: '需要技术技能吗？',
        answer:
          '不需要。如果你会用 Telegram，就能用这个。只需自然聊天。AI 助手功能（Claude/ChatGPT 记忆）是技术用户的额外福利。',
      },
      {
        question: '免费套餐如何使用？',
        answer:
          '包含一次完整面试和一次简历生成，完全免费。无需信用卡。喜欢的话，可以升级继续生成和更新。',
      },
      {
        question: '我可以导出数据吗？',
        answer: '随时可以。以 JSON/PDF 格式下载你的数据。数据归你所有。',
      },
      {
        question: '支持哪些支付方式？',
        answer:
          '通过支付合作伙伴支持信用卡、Apple Pay、Google Pay。也接受 USDC 和 BTC，满足注重隐私的用户。',
      },
      {
        question: '如果我不满意怎么办？',
        answer: '随时取消。月度订阅无绑定。终身购买享 30 天退款保证。',
      },
    ],
  },

  emailSignup: {
    heading: '抢先体验',
    subheading: '上线即有免费套餐，率先试用。',
    placeholder: '输入你的邮箱',
    cta: '加入候补名单 — 免费',
    disclaimer: '无垃圾邮件，无需信用卡。上线时第一时间通知你。',
    formAction: formspree.action,
  },
};
