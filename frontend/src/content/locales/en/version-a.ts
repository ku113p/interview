import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'AI Career Coach - Professional Resume in 15 Minutes | Interview Assistant',
    description:
      'Talk naturally, get a professional ATS-optimized resume. AI interviews you like a career coach, extracts accomplishments, generates polished CV. Free tier.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: 'Your AI Career Coach.<br>Perfect Resume in 15 Minutes.',
    subheadline:
      'Talk naturally about your experience. AI interviews you like a career coach, extracts your accomplishments, and generates an ATS-optimized professional resume automatically.',
    cta: 'Try It Free',
    socialProof: 'Join 50+ professionals on the waitlist',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Sound Familiar?',
    items: [
      {
        title: 'You forget your best work',
        description:
          '"What did I accomplish at that job 3 years ago?" You did amazing things but can\'t articulate them under pressure.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT gives you generic fluff',
        description:
          'You paste your info, ChatGPT writes "results-oriented professional with proven track record." Recruiters see through it instantly.',
        icon: 'sparkles',
      },
      {
        title: 'Updating takes hours',
        description:
          "Every application means reformatting, rewriting, and hoping the ATS doesn't reject you. You have better things to do.",
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT Writes Resumes.<br>We Write YOUR Resume.',
    description:
      "ChatGPT can polish text you give it. But most people can't articulate their own accomplishments well.\n\nOur AI interviews you like a career coach — asking follow-ups, drawing out quantifiable impact, catching things you'd forget.",
    before: {
      label: 'Generic ChatGPT Output',
      text: 'Managed a development team',
    },
    after: {
      label: 'Interview-Extracted Output',
      text: 'Led a 12-person engineering team that delivered a $2M platform migration 3 weeks ahead of schedule',
    },
    closing:
      'You already know this stuff. You just need someone to ask the right questions.',
  },

  howItWorks: {
    heading: "15 Minutes. That's It.",
    steps: [
      {
        number: 1,
        title: 'Quick Conversation',
        description:
          'Chat with our Telegram bot for 10-15 minutes. Just talk naturally about your experience, projects, skills. It asks smart follow-up questions — like a career coach, not a form.',
      },
      {
        number: 2,
        title: 'AI Extraction',
        description:
          'Our AI extracts accomplishments, quantifies impact, identifies key skills, and organizes everything into structured career data. Nothing gets lost.',
      },
      {
        number: 3,
        title: 'Professional Resume',
        description:
          'Get a polished, ATS-optimized PDF resume. Proper formatting, keyword-rich, passes automated screening. Ready for any job application.',
      },
    ],
    bonus: {
      title: 'Bonus: AI Memory',
      description:
        'Your AI assistants (Claude, ChatGPT, Cursor) can now query your career history anytime. Write cover letters in seconds. Prep for interviews with your real experience.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Like a Career Coach',
        items: [
          'Guided interview draws out your best work',
          "Follow-up questions you wouldn't think to ask yourself",
          'Captures quantifiable achievements automatically',
          'Updates in 5-minute follow-up sessions',
        ],
      },
      {
        title: 'ATS-Optimized',
        items: [
          "Passes automated screening (75% of resumes don't)",
          'Keyword-rich content matched to your industry',
          'Clean formatting that ATS systems can parse',
          'Professional layout recruiters expect',
        ],
      },
      {
        title: 'Always Current',
        items: [
          'Add new experience anytime via quick chat',
          'Generate tailored versions for different roles',
          'Export to PDF instantly',
          'Your data, your control, exportable anytime',
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
        description: 'See if it works for you. No credit card required.',
        features: ['1 interview session', '1 resume generation'],
        cta: 'Try It Free',
        highlighted: false,
      },
      {
        name: 'CV Pro — Lifetime',
        price: 79,
        priceLabel: '$79 one-time',
        description: 'Pay once, use forever. Founding member price.',
        features: [
          'Unlimited interviews + resume generations',
          'ATS-optimized PDF export',
          'Multiple resume versions',
          'Telegram bot access',
        ],
        cta: 'Reserve Lifetime Access',
        highlighted: true,
        badge: 'Best Value',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'How is this different from ChatGPT?',
        answer:
          "ChatGPT polishes text you already have. We interview you — asking follow-up questions, drawing out specifics, catching accomplishments you'd forget. Think career coach, not text editor. The result is richer, more specific, and uniquely yours.",
      },
      {
        question: 'Is the resume ATS-friendly?',
        answer:
          'Yes. Clean formatting, proper heading hierarchy, keyword-rich content. Designed to pass automated screening systems that reject 75% of resumes.',
      },
      {
        question: 'Do I need technical skills?',
        answer:
          'No. If you can use Telegram, you can use this. Just chat naturally. The AI assistant features (Claude/ChatGPT memory) are a bonus for technical users.',
      },
      {
        question: 'How does the free tier work?',
        answer:
          'One full interview session and one resume generation, completely free. No credit card required. If you like it, upgrade to keep generating and updating.',
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
      {
        question: "What if I don't like it?",
        answer:
          'Cancel anytime. Monthly subscriptions, no lock-in. Lifetime purchases have a 30-day money-back guarantee.',
      },
    ],
  },

  emailSignup: {
    heading: 'Get Early Access',
    subheading: 'Free tier available at launch. Be first to try it.',
    placeholder: 'Enter your email',
    cta: 'Join Waitlist — Free',
    disclaimer: 'No spam. No credit card. Just a heads up when we launch.',
    formAction: formspree.action,
  },
};
