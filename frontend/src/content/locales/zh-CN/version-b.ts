import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      '为 Claude、ChatGPT 和 Cursor 提供 AI 长期记忆 | Interview Assistant MCP',
    description:
      '为任何 AI 助手赋予结构化的长期记忆。主动访谈深度提取知识。MCP 服务器兼容 Claude Desktop、ChatGPT、Cursor 等多种平台。',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline: '赋予任何 AI 助手结构化的长期记忆',
    subheadline:
      '不只是被动记忆堆积。主动访谈深度提取结构化知识，让你的 AI 真正理解你的上下文。',
    cta: '加入抢先体验',
    socialProof: '支持 Claude、ChatGPT、Cursor、Windsurf 等',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'AI 记忆不该是被动的',
    items: [
      {
        title: '浅层捕获',
        description:
          '像 Mem0 这样的工具只是被动记录片段。你得到的是“用户偏好 Python”，而不是“主导了 50 万行 Java 代码库向 Python 的迁移，部署时间减少 60%”。',
        icon: 'layers',
      },
      {
        title: '缺乏结构',
        description:
          '知识图谱捕捉实体和关系，却缺少叙事。没有故事的上下文只是噪音。',
        icon: 'grid',
      },
      {
        title: '你不断重复自己',
        description:
          '每次与 Claude 的对话都从零开始。你得一次次复制粘贴相同的背景信息。',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: '主动访谈 > 被动捕获',
    description:
      '其他记忆工具只是观察你的行为，被动存储片段。\n\n而我们主动访谈你。系统化地，就像记者做人物专访——追问细节，深入挖掘，跟踪已覆盖和未覆盖内容。\n\n结果是：结构化、全面的知识，AI 能真正利用，而不仅仅是检索。',
    before: {
      label: 'Mem0 存储',
      text: '用户懂 Python',
    },
    after: {
      label: '我们存储',
      text: '2023 年主导 Acme Corp 的 Python 迁移。将 50 万行 Java 单体应用拆分为 Python 微服务。团队 8 人。部署时间减少 60%。为异步任务选择 FastAPI 而非 Django。',
    },
    closing: '这就是记忆与理解的区别。',
  },

  howItWorks: {
    heading: '工作原理',
    steps: [
      {
        number: 1,
        title: '结构化访谈',
        description:
          '通过 Telegram 快速对话，系统性覆盖你的知识。AI 跟踪访谈进度——知道已问和未问内容。逐步深入，而非零散片段。',
      },
      {
        number: 2,
        title: '知识提取',
        description:
          'AI 利用语义嵌入提取结构化摘要。按生活领域组织，支持语义搜索，而非仅关键词。',
      },
      {
        number: 3,
        title: 'MCP 集成',
        description:
          '标准 MCP 服务器，兼容 Claude Desktop、ChatGPT、Cursor、Windsurf、VS Code 及所有 MCP 兼容 AI。Bearer token 认证，5 分钟快速部署。',
      },
    ],
    bonus: {
      title: '即将推出：MCP 应用',
      description:
        '通过全新 MCP Apps 扩展，直接在 Claude 和 ChatGPT 内呈现交互式知识仪表盘。',
    },
  },

  benefits: {
    columns: [
      {
        title: '为开发者',
        items: [
          'AI 记住你的技术栈、架构决策和编码模式',
          '在任何对话中引用过往项目',
          '生成符合你真实模式的代码示例',
          '无需重复解释代码库设置',
        ],
      },
      {
        title: '为顾问',
        items: [
          'AI 记住客户详情、方法论和过往合作',
          '撰写提案时引用真实经验',
          '再也不用重复背景信息',
          '自动基于之前对话继续构建',
        ],
      },
      {
        title: '为所有人',
        items: [
          '基于真实成就撰写求职信',
          'AI 助力的面试准备，了解你的故事',
          '专业简历自动生成',
          '你的数据，随时可导出',
        ],
      },
    ],
  },

  pricing: {
    heading: '简单定价，无隐藏费用',
    tiers: [
      {
        name: '免费',
        price: null,
        priceLabel: '免费',
        description: '1 次访谈 + 知识搜索演示。',
        features: ['1 次访谈', '知识搜索演示'],
        cta: '免费试用',
        highlighted: false,
      },
      {
        name: '知识专业版',
        price: 29,
        priceLabel: '$29/月',
        description: '全面访问访谈、MCP 服务器和简历生成。',
        features: [
          '无限访谈与知识提取',
          'MCP 服务器访问（Bearer token 认证）',
          '全知识语义搜索',
          '包含简历生成',
          '支持 Claude、ChatGPT、Cursor、Windsurf',
        ],
        cta: '加入抢先体验',
        highlighted: true,
        badge: '最受欢迎',
      },
      {
        name: '自托管版',
        price: 59,
        priceLabel: '$59/月',
        description: '知识专业版全部功能，部署在你自己的基础设施上。',
        features: [
          '包含知识专业版所有功能',
          'Docker 部署，完全源码访问',
          '数据完全归你所有',
          '优先支持',
        ],
        cta: '加入抢先体验',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: '这和 Mem0/OpenMemory 有什么区别？',
        answer:
          'Mem0 被动捕获你与 AI 的对话片段。我们主动访谈你——系统化、覆盖全面，提取深度结构化知识。这就像监控摄像头和记者采访的区别。',
      },
      {
        question: '这和 Zep 有什么不同？',
        answer:
          'Zep 从文档和对话构建知识图谱。我们进行主动结构化访谈，带有追问和逐步深入。我们的知识更丰富，因为是有意提取，而非被动观察。',
      },
      {
        question: '支持哪些 AI？',
        answer:
          '任何 MCP 兼容的 AI。已确认支持：Claude Desktop、ChatGPT、Cursor、Windsurf、VS Code Copilot、JetBrains、Goose、Raycast。MCP 现已成为行业标准（Linux Foundation）。',
      },
      {
        question: 'MCP 协议稳定吗？',
        answer:
          'MCP 由 Agentic AI Foundation（Linux Foundation）管理，成员包括 Anthropic、OpenAI、Google、Microsoft 和 AWS。我们保持向后兼容。',
      },
      {
        question: '可以自托管吗？',
        answer: '可以。自托管版包含 Docker Compose 配置和完整部署文档。',
      },
      {
        question: '可以导出我的数据吗？',
        answer: '随时可以。支持 JSON/PDF 格式下载。数据属于你自己。',
      },
      {
        question: '支持哪些支付方式？',
        answer:
          '通过我们的支付合作伙伴支持信用卡、Apple Pay、Google Pay。也接受 USDC 和 BTC，保障隐私的客户首选。',
      },
    ],
  },

  emailSignup: {
    heading: '抢先体验',
    subheading: '率先体验结构化 AI 记忆。',
    placeholder: '请输入你的邮箱',
    cta: '免费加入抢先体验',
    disclaimer: '无垃圾邮件，无需信用卡。上线时第一时间通知你。',
    formAction: formspree.action,
  },
};
