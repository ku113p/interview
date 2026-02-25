import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'AI Long-Term Memory for Claude, ChatGPT & Cursor | Interview Assistant MCP',
    description:
      'Give any AI assistant structured long-term memory. Active interviews extract deep knowledge. MCP server works with Claude Desktop, ChatGPT, Cursor, and more.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline: 'Give ANY AI Assistant Structured Long-Term Memory',
    subheadline:
      'Not another passive memory dump. Active interviews extract deep, structured knowledge. Your AI actually understands your context.',
    cta: 'Join Early Access',
    socialProof: 'Works with Claude, ChatGPT, Cursor, Windsurf & more',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: "AI Memory Shouldn't Be Passive",
    items: [
      {
        title: 'Shallow capture',
        description:
          'Tools like Mem0 passively record fragments. You get "user prefers Python" not "led migration of 500K LOC Java codebase to Python, reducing deploy time 60%."',
        icon: 'layers',
      },
      {
        title: 'No structure',
        description:
          'Knowledge graphs capture entities and relationships but miss the narrative. Context without story is just noise.',
        icon: 'grid',
      },
      {
        title: 'You repeat yourself',
        description:
          'Every Claude conversation starts from zero. Copy-paste the same background. Every. Single. Time.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Active Interviews > Passive Capture',
    description:
      "Other memory tools watch what you do and passively store fragments.\n\nWe interview you. Systematically. Like a journalist building a profile — asking follow-ups, going deeper, tracking what's been covered and what hasn't.\n\nThe result: structured, comprehensive knowledge that AI can actually USE, not just retrieve.",
    before: {
      label: 'Mem0 stores',
      text: 'user knows Python',
    },
    after: {
      label: 'We store',
      text: 'Led Python migration at Acme Corp (2023). Converted 500K LOC Java monolith to Python microservices. Team of 8. Reduced deploy time 60%. Chose FastAPI over Django for async workloads.',
    },
    closing: "That's the difference between memory and understanding.",
  },

  howItWorks: {
    heading: 'How It Works',
    steps: [
      {
        number: 1,
        title: 'Structured Interviews',
        description:
          "Quick Telegram conversations that systematically cover your knowledge. The AI tracks coverage — it knows what it's asked and what it hasn't. Progressive deepening, not random fragments.",
      },
      {
        number: 2,
        title: 'Knowledge Extraction',
        description:
          'AI extracts structured summaries with semantic embeddings. Organized by life areas, searchable by meaning, not just keywords.',
      },
      {
        number: 3,
        title: 'MCP Integration',
        description:
          'Standard MCP server that works with Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code, and any MCP-compatible AI. Bearer token auth. 5-minute setup.',
      },
    ],
    bonus: {
      title: 'Coming Soon: MCP Apps',
      description:
        'Interactive knowledge dashboard rendered directly inside Claude and ChatGPT via the new MCP Apps extension.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'For Developers',
        items: [
          'AI remembers your tech stack, architectural decisions, and coding patterns',
          'Reference past projects in any conversation',
          'Generate code examples using YOUR real patterns',
          'Never re-explain your codebase setup',
        ],
      },
      {
        title: 'For Consultants',
        items: [
          'AI recalls client details, methodologies, past engagements',
          'Write proposals referencing real experience',
          'Never repeat background info again',
          'Build on previous conversations automatically',
        ],
      },
      {
        title: 'For Everyone',
        items: [
          'Cover letters written from real accomplishments',
          'Interview prep with AI that knows your story',
          'Professional resume auto-generated from your knowledge',
          'Your data, always exportable',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Simple Pricing. No Surprises.',
    tiers: [
      {
        name: 'Free',
        price: null,
        priceLabel: 'Free',
        description: '1 interview session + knowledge search demo.',
        features: ['1 interview session', 'Knowledge search demo'],
        cta: 'Try It Free',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/month',
        description:
          'Full access to interviews, MCP server, and CV generation.',
        features: [
          'Unlimited interviews + knowledge extraction',
          'MCP server access (Bearer token auth)',
          'Semantic search across all your knowledge',
          'CV generation included',
          'Works with Claude, ChatGPT, Cursor, Windsurf',
        ],
        cta: 'Join Early Access',
        highlighted: true,
        badge: 'Most Popular',
      },
      {
        name: 'Self-Hosted',
        price: 59,
        priceLabel: '$59/month',
        description: 'Everything in Knowledge Pro, on your own infrastructure.',
        features: [
          'Everything in Knowledge Pro',
          'Docker deployment, full source access',
          'Full data ownership',
          'Priority support',
        ],
        cta: 'Join Early Access',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'How is this different from Mem0/OpenMemory?',
        answer:
          "Mem0 passively captures fragments from your AI conversations. We actively interview you — systematically, with coverage tracking — extracting deep structured knowledge. It's the difference between a security camera and a journalist interview.",
      },
      {
        question: 'How is this different from Zep?',
        answer:
          "Zep builds knowledge graphs from documents and conversations. We do active structured interviews with follow-up questions and progressive deepening. Our knowledge is richer because it's intentionally extracted, not passively observed.",
      },
      {
        question: 'Which AIs are supported?',
        answer:
          'Any MCP-compatible AI. Confirmed: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP is now an industry standard (Linux Foundation).',
      },
      {
        question: 'Is the MCP protocol stable?',
        answer:
          'MCP is governed by the Agentic AI Foundation (Linux Foundation) with Anthropic, OpenAI, Google, Microsoft, and AWS as members. We maintain backward compatibility.',
      },
      {
        question: 'Can I self-host?',
        answer:
          'Yes. Self-Hosted tier includes Docker Compose setup and full deployment documentation.',
      },
      {
        question: 'Can I export my data?',
        answer: "Always. Download your data as JSON/PDF anytime. It's yours.",
      },
      {
        question: 'What payment methods do you accept?',
        answer:
          'Credit card, Apple Pay, Google Pay via our payment partner. We also accept USDC and BTC for privacy-conscious customers.',
      },
    ],
  },

  emailSignup: {
    heading: 'Get Early Access',
    subheading: 'Be first to try structured AI memory.',
    placeholder: 'Enter your email',
    cta: 'Join Early Access — Free',
    disclaimer: 'No spam. No credit card. Just a heads up when we launch.',
    formAction: formspree.action,
  },
};
