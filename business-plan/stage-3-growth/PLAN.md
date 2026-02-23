# Stage 3: Working Service & Growth

**Timeline:** 4-6 weeks
**Budget:** $200-500
**Goal:** Scale to 25-50 paying customers with testimonials and referrals

**Prerequisite:** Stage 2 completed successfully (5+ customers, positive feedback)

---

## Hypothesis to Test

"With working product + testimonials + better materials, we can grow to 50 users organically or with small paid campaigns."

## Proof of Success

- 25-50 paying customers
- <20% monthly churn (customers renew)
- 5+ testimonials/case studies
- 2-3 referrals (customers telling friends)
- $500-1,500 Monthly Recurring Revenue

**If you get this proof, business is validated. Continue scaling.**

---

## Phase 3.1: Automate & Optimize Payment (Week 1-2)

### Task 3.1.1: Full Polar.sh Webhook Automation

**Why automate now:**
- Semi-manual works for 5-10 customers
- Semi-manual breaks at 20+ customers (too much time)
- Full automation unlocks scaling

**Implementation:**
1. Polar.sh webhook handler fully automated
2. Auto-create API keys on subscription.created
3. Auto-extend on subscription.renewed
4. Auto-send welcome email on creation
5. Graceful handling of subscription.canceled (expire at end of period)

**Files to update:**
- `src/processes/payment/polar_webhook.py` - full automation
- Add automated welcome email via SendGrid/Postmark

**Testing:**
- Use Polar.sh test mode
- Test full flow: checkout -> webhook -> key created -> email sent
- Test renewal and cancellation flows

**Deliverable:** Zero-touch payment automation

---

### Task 3.1.2: Crypto Payment Automation (If Volume Justifies)

**If 10+ customers pay with crypto, automate with NOWPayments:**

**Setup:**
1. NOWPayments account (individual, 0.5% fee)
2. Create invoices via API
3. Webhook on payment confirmed -> create API key
4. Auto-send welcome email

**Only build this if crypto customers > 10. Otherwise, keep manual.**

**Deliverable:** Automated crypto payment processing

---

### Task 3.1.3: Subscription Renewal System

**Goal:** Automatic monthly renewals

**Polar.sh handles this automatically:**
- Recurring billing on card
- Webhook extends API key on each charge
- Customer gets receipt email from Polar
- Failed payment -> Polar retries + notifies customer

**Crypto renewals (manual for now):**
- 5 days before expiry: send renewal reminder email
- Customer sends new payment
- You manually extend key

**Deliverable:** Renewal system working

---

## Phase 3.2: Content Marketing (Week 1-6, Ongoing)

### Task 3.2.1: Write SEO Blog Posts

**Goal:** Get organic traffic from Google

**Topics (write 1 per week):**
1. "How to Give Claude Desktop Long-Term Memory (MCP Tutorial)"
2. "Build vs Buy: MCP Server for Personal Knowledge"
3. "Privacy-Preserving AI: Why I Built My Own Knowledge Assistant"
4. "Best Practices for AI-Assisted Cover Letters"
5. "MCP Servers Explained: A Developer's Guide"
6. "How to Organize Your Career Knowledge for AI Assistants"

**Format:**
- 1,500-2,000 words
- Include screenshots/code examples
- Link to your product naturally (not salesy)
- Publish on your blog (or Medium/Dev.to)

**SEO Basics:**
- Title includes keyword (e.g., "Claude Desktop Memory")
- H2 headings with related keywords
- Alt text on images
- Internal links to other posts
- Link to documentation

**Deliverable:** 1 blog post per week x 6 = 6 posts

---

### Task 3.2.2: Create Video Tutorials

**Goal:** Show product in action, capture YouTube search traffic

**Videos to make:**
1. "Claude Desktop + MCP Tutorial (5 minutes)" - setup walkthrough
2. "Give Claude Perfect Memory (Demo)" - end-to-end demo
3. "AI-Generated Cover Letter from Interview Data" - use case
4. "Privacy-First Knowledge Management" - positioning

**Distribution:**
- Upload to YouTube
- Embed in blog posts
- Share in Reddit comments (when relevant)
- Link from documentation

**Deliverable:** 4 tutorial videos published

---

### Task 3.2.3: Build Case Studies from Real Users

**Goal:** Detailed success stories with specific outcomes

**Format:**
```
Title: "How [Name] Saved 10 Hours Per Week on Job Applications"

Interview format:
- Background: Who is this person?
- Problem: What were they struggling with?
- Solution: How did they use your product?
- Results: What changed? (time saved, $ earned, etc.)
- Quote: Testimonial in their words

[Screenshots of their usage]
```

**How to get case studies:**
1. Email your happiest customers (ask nicely)
2. Offer incentive: free month or upgrade
3. Interview them (15-20 minutes)
4. Write it up, get their approval
5. Publish on your site + share socially

**Deliverable:** 3 case studies published

---

## Phase 3.3: Community Building (Week 2-6)

### Task 3.3.1: Start Email Newsletter

**Goal:** Stay in touch with users, share tips

**Frequency:** Bi-weekly (every 2 weeks)

**Content ideas:**
- New feature announcements
- Usage tips ("Did you know you can...?")
- Customer spotlights
- Industry news (Claude updates, MCP ecosystem)

**Tools:**
- ConvertKit (free up to 1,000 subscribers)
- Substack (free, built-in audience)

**Deliverable:** First 3 newsletters sent

---

### Task 3.3.2: Create Discord or Telegram Community

**Goal:** Let users help each other, reduce support burden

**Why community:**
- Users answer each other's questions
- Feature requests discussed openly
- You learn what people care about
- Creates loyalty/stickiness

**Setup:**
- Discord server or Telegram group
- Channels: #introductions, #support, #feature-requests, #showcase
- Invite all paying customers
- Be active first month (respond to everything)

**Deliverable:** Community launched with 10+ members

---

### Task 3.3.3: Launch Referral Program

**Goal:** Get customers to refer friends

**Simple referral incentive:**
```
"Refer a friend, you both get 1 month free."

How it works:
1. Share your referral link
2. Friend signs up and pays
3. You both get 1 month free added to accounts
```

**Implementation:**
- Add `referred_by` field to user records
- Track referrals in database
- Manually extend both accounts when referral pays
- (Later: automate this)

**Deliverable:** Referral program live

---

## Phase 3.4: Improve Product Based on Feedback (Week 3-5)

### Task 3.4.1: Analyze Customer Usage Data

**Goal:** Understand what features actually get used

**Questions to answer:**
1. Which features are used most?
   - MCP search queries? CV generation? Specific interview topics?
2. Where do users drop off?
   - Do they complete onboarding? Finish interviews?
3. What do they ask support about?
   - Common pain points or confusion?

**Data sources:**
- Database queries (summaries per user, API calls)
- Support emails (common questions)
- Community discussions (feature requests)

**Deliverable:** Usage report identifying top priorities

---

### Task 3.4.2: Build Top-Requested Features

**Only build what 10+ customers request.**

**Likely requests (based on market research):**
1. **ATS Scoring** - Match resume keywords against job descriptions (table stakes for resume market)
2. **CV Templates** - Multiple resume styles (professional, creative, minimalist)
3. **MCP Apps Integration** - Interactive interview UI rendered inside Claude/ChatGPT (SEP-1865)
4. **Export Data** - Download all your data as JSON/CSV
5. **Job-Tailored Resumes** - Generate different versions for different job postings
6. **Multi-Language** - Interview in Spanish, French, etc.
7. **Self-Hosted Option** - Docker Compose setup

**MCP Apps Opportunity (high strategic value):**
The MCP Apps extension (SEP-1865, Jan 2026) lets servers render interactive HTML UIs inside Claude and ChatGPT. This could enable:
- Running interviews directly inside Claude Desktop (no Telegram needed)
- Interactive knowledge dashboard in the AI chat
- CV preview and editing within the conversation
- Progress visualization for interview coverage
Already shipping in ChatGPT, Claude, Goose, VS Code.

**Prioritization:**
- Must have: 20+ requests OR strategic differentiator
- Should have: 10-20 requests
- Nice to have: 5-10 requests
- Ignore: <5 requests

**Deliverable:** Top 2-3 features built

---

### Task 3.4.3: Improve Onboarding Experience

**Goal:** Get users to "aha moment" faster

**Current onboarding flow:**
1. Pay → Get API key via email
2. Set up MCP manually
3. Start interview
4. Test search in Claude

**Improvements:**
- **Video walkthrough:** Personalized for their tier
- **Checklist:** Progress tracker (✅ MCP setup, ✅ First interview)
- **Sample queries:** "Try asking Claude: 'What's my Python experience?'"
- **Faster feedback:** See results after 1st interview (not 5th)

**Deliverable:** Improved onboarding flow live

---

## Phase 3.5: Scale Marketing (Week 4-6)

### Task 3.5.1: Double Down on What Works

**Review Stage 2 results:**
- Which community had best conversion?
- Which content got most engagement?
- Did paid ads work?

**Strategy:**
- ✅ If Reddit posts worked → Post more (different subreddits)
- ✅ If HN worked → Post follow-up / "Show HN: Update"
- ✅ If blog posts worked → Write 2x per week
- ✅ If ads worked → Double budget on best-performing

**Deliverable:** 2x effort on best channel

---

### Task 3.5.2: Try New Channels

**If you've maxed out current channels, experiment:**

**Option 1: Twitter/X**
- Share tips, demos, use cases
- Engage with Claude/AI community
- Post daily for 30 days (test commitment)

**Option 2: YouTube Ads**
- Target Claude Desktop tutorial viewers
- Budget: $200-300
- Track cost per customer

**Option 3: Podcast Sponsorships**
- Find privacy/productivity/AI podcasts
- Sponsor 1-2 episodes ($200-500 each)
- Include promo code to track conversions

**Option 4: Affiliate Partnerships**
- Find creators in your niche
- Offer 20-30% commission
- They promote, you fulfill

**Pick ONE new channel, test for 2-4 weeks.**

**Deliverable:** New channel test results

---

## Phase 3.6: Business Formalization (If Revenue Justifies)

### Task 3.6.1: Form Business Entity (Optional)

**Trigger:** When hitting $2K+ MRR consistently

**Options:**
1. **Estonia e-Residency** (crypto-friendly, remote incorporation)
2. **US LLC via Stripe Atlas** (if using Stripe)
3. **Local entity** (your country's requirements)

**Why formalize:**
- Legal protection (separate personal/business liability)
- Easier to accept non-crypto payments
- Professional image
- Tax optimization

**Deliverable:** Business entity formed (if needed)

---

### Task 3.6.2: Set Up Proper Accounting

**Track income and expenses:**
- Use Wave (free) or QuickBooks
- Record all crypto payments (convert to USD value at time of receipt)
- Track expenses (hosting, tools, ads)
- Consult accountant for tax filing

**Deliverable:** Accounting system in place

---

## Stage 3 Success Criteria

**Check these boxes:**

- [ ] **25-50 paying customers**
- [ ] **$500-1,500 Monthly Recurring Revenue**
- [ ] **<20% monthly churn** (customers renewing)
- [ ] **5+ testimonials/case studies** published
- [ ] **2-3 organic referrals** (customers told friends)
- [ ] **Automated payment system** (if using Stripe)
- [ ] **Support <5 hours per week** (self-service docs working)
- [ ] **Clear growth channel** identified (know where customers come from)

**If you hit these: Business is validated. Continue scaling.**

---

## Budget Breakdown

| Item | Cost | Notes |
|------|------|-------|
| Stripe fees (if used) | ~3% of revenue | Auto-deducted |
| Hosting (VPS for BTCPay) | $10-20/mo | If self-hosting payments |
| Email (ConvertKit) | $0-29/mo | Free up to 1K subs |
| Video tools (Loom Pro) | $0-12/mo | Optional |
| Paid ads (test) | $200-300 | If previous ads worked |
| Podcast sponsor (optional) | $200-500 | Test 1-2 episodes |
| **Total** | **$200-500** | |

---

## Timeline

**Week 1-2: Automation**
- Stripe integration (or BTCPay)
- Subscription renewal system
- Automated onboarding emails

**Week 3-4: Content**
- 2 blog posts
- 2 videos
- 2 case studies
- Start newsletter

**Week 5-6: Growth**
- Scale best channel from Stage 2
- Test 1 new channel
- Launch referral program
- Community building

**Total: 4-6 weeks to scale to 25-50 customers**

---

## What Happens After Stage 3?

**If successful, you have a real business:**
- $1K-2K MRR
- Proven acquisition channels
- Happy customers renewing
- Testimonials and referrals

**Next steps (Stage 4, not detailed here):**
1. **Scale to $10K MRR** (300-400 customers)
   - Hire part-time support
   - Build more advanced features
   - Enterprise tier (team accounts, SSO)

2. **Product Expansion**
   - Self-hosted version (one-time license)
   - White-label licensing
   - API access for developers

3. **Business Growth**
   - Form entity (if not yet)
   - Raise prices (grandfathered early users)
   - Explore partnerships

**You're now a sustainable business!**

---

## Next Steps

Continue growing organically, or consider:
- [Hiring help](https://www.upwork.com) (support, marketing)
- [Joining communities](https://indiehackers.com) (advice from other founders)
- [Tracking metrics](https://www.baremetrics.com) (proper SaaS analytics)
