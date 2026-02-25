export interface VersionContent {
  meta: {
    readonly title: string;
    readonly description: string;
    readonly ogImage: string;
    readonly canonicalPath: string;
  };
  hero: {
    readonly headline: string;
    readonly subheadline: string;
    readonly cta: string;
    readonly socialProof: string;
    readonly heroImage?: string;
    readonly videoId: string;
  };
  problem: {
    readonly heading: string;
    readonly items: readonly {
      readonly title: string;
      readonly description: string;
      readonly icon: string;
    }[];
  };
  whyNotChatGPT: {
    readonly heading: string;
    readonly description: string;
    readonly before: { readonly label: string; readonly text: string };
    readonly after: { readonly label: string; readonly text: string };
    readonly closing: string;
  };
  howItWorks: {
    readonly heading: string;
    readonly steps: readonly {
      readonly number: number;
      readonly title: string;
      readonly description: string;
    }[];
    readonly bonus: {
      readonly title: string;
      readonly description: string;
    };
  };
  benefits: {
    readonly columns: readonly {
      readonly title: string;
      readonly items: readonly string[];
    }[];
  };
  pricing: {
    readonly heading: string;
    readonly tiers: readonly {
      readonly name: string;
      readonly price: number | null;
      readonly priceLabel: string;
      readonly description: string;
      readonly features: readonly string[];
      readonly cta: string;
      readonly highlighted: boolean;
      readonly badge?: string;
    }[];
  };
  faq: {
    readonly items: readonly {
      readonly question: string;
      readonly answer: string;
    }[];
  };
  emailSignup: {
    readonly heading: string;
    readonly subheading: string;
    readonly placeholder: string;
    readonly cta: string;
    readonly disclaimer: string;
    readonly formAction: string;
  };
}

export interface UiStrings {
  header: {
    logo: string;
    cta: string;
    menuToggle: string;
  };
  footer: {
    rights: string;
  };
  faq: {
    heading: string;
  };
  pricing: {
    paymentNote: string;
  };
  nav: {
    forDevelopers: string;
    forJobSeekers: string;
  };
  thanks: {
    title: string;
    heading: string;
    message: string;
    sharePrompt: string;
    copyLink: string;
    shareOnX: string;
    copied: string;
    tweetText: string;
  };
}
