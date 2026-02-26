// Shared constants — single source of truth for site-wide values.
// Update these when configuring for production.

export const site = {
  name: 'Interview Assistant',
  domain: 'interviewassistant.ai',
  url: 'https://interviewassistant.ai',
} as const;

const CONTACT_EMAIL =
  import.meta.env.PUBLIC_CONTACT_EMAIL || 'hello@interviewassistant.ai';
const CONTACT_TELEGRAM =
  import.meta.env.PUBLIC_CONTACT_TELEGRAM || 'interview_assistant';

export const contacts = {
  email: CONTACT_EMAIL,
  telegram: `https://t.me/${CONTACT_TELEGRAM}`,
  telegramLabel: `@${CONTACT_TELEGRAM}`,
} as const;

const FORMSPREE_ID = import.meta.env.PUBLIC_FORMSPREE_ID || 'demo'; // Load from env or use demo

export const formspree = {
  id: FORMSPREE_ID,
  action: `https://formspree.io/f/${FORMSPREE_ID}`,
} as const;
