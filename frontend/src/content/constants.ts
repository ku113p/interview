// Shared constants — single source of truth for site-wide values.
// Update these when configuring for production.

export const site = {
  name: 'Interview Assistant',
  domain: 'interviewassistant.ai',
  url: 'https://interviewassistant.ai',
} as const;

export const contacts = {
  email: 'hello@interviewassistant.ai',
  telegram: 'https://t.me/interview_assistant', // TODO: replace with actual handle
  telegramLabel: '@interview_assistant',
} as const;

const FORMSPREE_ID = 'YOUR_FORM_ID'; // TODO: replace with actual Formspree form ID

export const formspree = {
  id: FORMSPREE_ID,
  action: `https://formspree.io/f/${FORMSPREE_ID}`,
} as const;
