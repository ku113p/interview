# Week 1 Action Checklist

**Goal:** Validate demand, test messaging, get first 5-10 waitlist signups
**Time commitment:** 10-15 hours total (2-3 hours per day)
**Budget:** $0-20 (optional domain/hosting)

---

## Day 1: Payment & Market Research (2-3 hours)

### Morning: Set Up Payment Infrastructure
- [ ] Read [02-payment-options.md](./02-payment-options.md) fully
- [ ] **Sign up for Polar.sh** (primary payment - credit cards, subscriptions, handles tax)
- [ ] Create your product tiers: Free, CV Pro ($12/mo + $79 lifetime), Knowledge Pro ($29/mo)
- [ ] Get payment links (you'll embed these on landing page)

### Afternoon: Set Up Crypto Option (Optional)
- [ ] Install Coinbase Wallet or MetaMask (for crypto-paying customers)
- [ ] **CRITICAL:** Write down 12-word recovery phrase on paper (store safely!)
- [ ] Note your Base wallet address (for USDC payments)
- [ ] This is secondary -- most customers will use credit cards

### Evening: Study Competitors
- [ ] Try Mem0/OpenMemory (understand the MCP memory competition)
- [ ] Try Teal or Rezi free tier (understand the CV competition)
- [ ] Note: What do they do well? Where do they fall short?
- [ ] Read [REVIEW-2026-02-24.md](../REVIEW-2026-02-24.md) for full competitive analysis

**End of Day 1:** Polar.sh account + payment links ready. Know your competitors.

**Deliverable:** Working payment infrastructure (credit cards!) + competitor notes

---

## Day 2: Market Research & Community Joining (2-3 hours)

### Morning: Read Market Analysis
- [ ] Read `MARKET-SEGMENTS.md` in business-plan folder
- [ ] Decide which segment to test first: CV focus OR MCP focus (or both)
- [ ] Note which messaging resonates with you

### Afternoon: Join Target Communities
**If testing MCP/technical segment:**
- [ ] Join r/ClaudeAI (50K members)
- [ ] Join r/LocalLLaMA (100K members)
- [ ] Join Claude Discord (official - search for invite link)
- [ ] Follow #mcp tag on Twitter/X

**If testing CV/career segment:**
- [ ] Join r/resumes (500K members)
- [ ] Join r/careerguidance (800K members)
- [ ] Join r/jobs (2M members)

**Both segments:**
- [ ] Join r/selfhosted (privacy advocates)
- [ ] Create account on IndieHackers.com

### Evening: Observe Discussions
- [ ] Spend 1 hour reading posts in each community
- [ ] Note: What problems do people mention? What language do they use?
- [ ] Create tracking spreadsheet (use [06-tracking-template.md](./06-tracking-template.md))
- [ ] Log 5-10 pain points you observe in Sheet 1

**Deliverable:** Joined 5-7 communities + tracking spreadsheet with initial observations

---

## Day 3: Demo Video Recording (3-4 hours)

### Morning: Prepare Demo Environment
- [ ] Clean up desktop (close unnecessary apps)
- [ ] Open Telegram + PDF viewer side by side
- [ ] Test your microphone (record 10 seconds, listen back)
- [ ] Download OBS Studio or Loom (free)
- [ ] Read demo scripts in [PLAN.md](./PLAN.md) (lines 35-75)

### Afternoon: Record Demo Video(s)
**Priority: Record CV demo first (larger market). MCP demo second if time allows.**

**MUST HAVE: CV Focus Demo (90 seconds)**
- [ ] Show: Natural Telegram conversation about career (the bot asking follow-ups)
- [ ] Show: Side-by-side: generic ChatGPT resume vs YOUR generated resume (specific, detailed)
- [ ] Show: Generated PDF resume (professional, ATS-friendly)
- [ ] Voiceover: "ChatGPT writes generic resumes. This interviews you like a career coach."
- [ ] Key moment: Show the bot asking a smart follow-up question (this is your differentiator)

**NICE TO HAVE: MCP Technical Demo (90 seconds)**
- [ ] Show: Quick Telegram interview (10-15 seconds)
- [ ] Show: Claude Desktop querying your knowledge via MCP
- [ ] Show: AI writing cover letter using your real data
- [ ] Voiceover: "Unlike Mem0, this actively interviews you. Deep knowledge, not fragments."

### Evening: Edit & Upload
- [ ] Trim to 90 seconds (cut fluff, keep it tight)
- [ ] Add simple title card: "Interview Assistant - AI Memory/CV Generation"
- [ ] Export video (1080p)
- [ ] Upload to YouTube (unlisted until you're ready)
- [ ] Test: Does video play smoothly? Is audio clear?

**Deliverable:** 1-2 demo videos uploaded to YouTube (unlisted)

---

## Day 4: Landing Page Creation (3-4 hours)

### Morning: Choose Landing Page Approach
**Option A: No-Code (Carrd) - 2 hours total**
- [ ] Sign up for Carrd.co ($19/year or free trial)
- [ ] Choose simple one-page template
- [ ] Follow [03-landing-page-copy.md](./03-landing-page-copy.md) structure
- [ ] Embed YouTube video
- [ ] Add email capture form

**Option B: Custom HTML (Vercel) - 3-4 hours if you code**
- [ ] Create simple HTML page with Tailwind CSS
- [ ] Follow [03-landing-page-copy.md](./03-landing-page-copy.md) structure
- [ ] Embed YouTube video (iframe)
- [ ] Add ConvertKit form embed for email capture
- [ ] Deploy to Vercel (free hosting)

### Afternoon: Write Landing Page Copy
- [ ] Open [03-landing-page-copy.md](./03-landing-page-copy.md)
- [ ] **Use Version A (CV focus) as the main landing page** (bigger market)
- [ ] Version B (MCP focus) can be a separate /developers page later
- [ ] Customize copy with your details
- [ ] Replace placeholders (Polar.sh payment link, YouTube link, etc.)
- [ ] Make sure "Why not ChatGPT?" section is prominent
- [ ] Make sure ATS-friendly is mentioned
- [ ] Proofread (typos kill conversions!)

### Evening: Deploy & Test
- [ ] Deploy landing page (Carrd publish or Vercel deploy)
- [ ] Test on mobile + desktop (does it look good?)
- [ ] Test video embed (does it play?)
- [ ] Test email form (sign up yourself - does it work?)
- [ ] Fix any broken links or formatting issues

**Optional: Set Up Analytics**
- [ ] Add Plausible or Simple Analytics (privacy-friendly, free tier)
- [ ] Track: page views, video plays, form submissions

**Deliverable:** Live landing page with demo video and email capture

---

## Day 5: First Community Posts (2-3 hours)

### Morning: Prepare Posts
- [ ] Open [04-reddit-posts.md](./04-reddit-posts.md)
- [ ] Choose template based on your segment:
  - MCP focus → Template 1A
  - CV focus → Template 1B
  - Broad audience → Template 2 (Show HN style)
- [ ] Customize with your landing page link
- [ ] Proofread (read out loud to catch awkward phrasing)

### Afternoon: Post to 2 Communities
**Post #1: CV segment (primary market)**
- [ ] Post to r/resumes using Template 1B from [04-reddit-posts.md](./04-reddit-posts.md)
- [ ] Include link to landing page + demo video
- [ ] Frame as "looking for feedback" not "selling"
- [ ] Be ready to answer "just use ChatGPT" (see prepared answers in template)

**Post #2: Technical segment**
- [ ] Post to r/ClaudeAI using Template 1A
- [ ] Differentiate from Mem0/Zep (active interviews vs passive capture)
- [ ] OR post to Hacker News "Show HN" (Template 2)

### Evening: Engage with Comments
- [ ] Set aside 2 hours to respond to comments
- [ ] Respond within 30 minutes to first 5 comments (boosts visibility)
- [ ] Answer every question thoroughly
- [ ] Thank people for feedback (even critical)
- [ ] Use [05-outreach-scripts.md](./05-outreach-scripts.md) for DM templates if needed

**Deliverable:** 2 posts live + engaged with all comments

---

## Day 6: Engagement & Outreach (2 hours)

### Morning: Check Results
- [ ] How many upvotes? (50+ = good)
- [ ] How many comments? (10+ = engaged discussion)
- [ ] How many landing page visits? (check analytics)
- [ ] How many email signups? (check ConvertKit/Mailchimp)

### Afternoon: Follow Up
**If post did well (50+ upvotes, 5+ signups):**
- [ ] DM people who commented positively (use Script 2 from [05-outreach-scripts.md](./05-outreach-scripts.md))
- [ ] Offer early access to anyone who seemed very interested
- [ ] Log all interactions in tracking spreadsheet

**If post didn't do well (<20 upvotes, 0 signups):**
- [ ] Read negative comments carefully (what objections?)
- [ ] Note: Was messaging unclear? Wrong audience? Price too high?
- [ ] Plan to try different angle tomorrow

### Evening: Stealth Outreach
- [ ] Find 3-5 recent posts in communities about relevant problems
- [ ] Example: "How do I make Claude remember things?"
- [ ] Reply with helpful comment + subtle mention (Template 4)
- [ ] Don't spam - add value first, mention product second

**Deliverable:** 5+ meaningful interactions (comments, DMs, replies)

---

## Day 7: Review & Plan Next Week (1-2 hours)

### Morning: Analyze Week 1 Results
- [ ] Open tracking spreadsheet
- [ ] Count total waitlist signups (Goal: 5-10)
- [ ] Review landing page analytics (Goal: 100+ visitors)
- [ ] Review demo video views (Goal: 30+ views)
- [ ] Note which community/post performed best

### Afternoon: Identify Patterns
**Answer these questions:**
- [ ] Which segment showed more interest? (MCP technical vs CV career)
- [ ] What objections came up repeatedly? (price, crypto, complexity?)
- [ ] What features did people ask about? (self-hosted, team features, etc.)
- [ ] Did anyone mention price? (too high, too low, just right?)
- [ ] Which messaging resonated? (AI memory vs CV generation)

### Evening: Plan Week 2
**Based on Week 1 learnings:**

**If CV segment won (more signups from r/resumes, r/careerguidance):**
- [ ] Focus Week 2 posts on job seeker communities
- [ ] Update landing page to emphasize CV generation
- [ ] Record better CV demo if needed

**If MCP segment won (more signups from r/ClaudeAI, r/LocalLLaMA):**
- [ ] Focus Week 2 posts on AI/developer communities
- [ ] Update landing page to emphasize AI memory
- [ ] Create technical setup guide

**If both worked equally:**
- [ ] Keep dual messaging (tabs on landing page for each segment)
- [ ] Post to both types of communities
- [ ] See which converts to paying customers better

**Deliverable:** Week 1 summary document (1 page) + Week 2 plan

---

## Success Metrics: Did Week 1 Work?

### 🟢 Great Success (Move to Week 2 with confidence)
- ✅ 10+ waitlist signups
- ✅ 2+ people asked "when can I pay?"
- ✅ 150+ landing page visitors
- ✅ 50+ demo video views
- ✅ Clear segment preference identified

### 🟡 Moderate Success (Week 2 needed but promising)
- ✅ 5-9 waitlist signups
- ✅ 1 person asked about payment
- ✅ 80-150 landing page visitors
- ✅ 30-50 demo video views
- ✅ Some positive feedback but mixed

### 🔴 Needs Pivot (Re-evaluate messaging/segment)
- ❌ <5 waitlist signups
- ❌ 0 payment inquiries
- ❌ <50 landing page visitors
- ❌ Mostly negative/confused feedback

**If red flags, consider:**
- Different segment (try career focus if you tried technical, or vice versa)
- Different messaging (clearer value prop)
- Different communities (maybe wrong audience)
- Talk to 3-5 people directly before posting more

---

## Common Week 1 Blockers & Solutions

**Blocker: "I don't know how to make videos"**
→ Solution: Use Loom (easiest - records screen + voice automatically)
→ Alternative: Just screen recording + slides with text (no voiceover needed)

**Blocker: "I'm afraid of negative feedback"**
→ Solution: Frame as "experiment" not "product launch" - lowers stakes
→ Reminder: Any feedback (even critical) teaches you something

**Blocker: "No one is signing up"**
→ Solution: Check landing page (is CTA clear? Is value prop obvious?)
→ Solution: Ask 2 friends to review - what's confusing?

**Blocker: "Posts aren't getting traction"**
→ Solution: Post timing matters - try mornings (9-11am) in community's timezone
→ Solution: Better title - more specific problem statement

**Blocker: "I'm spending too much time on this"**
→ Solution: Set timer for each task - avoid perfectionism
→ Reminder: Week 1 is sprint, not marathon - short burst okay

---

## Week 1 Time Breakdown

| Day | Tasks | Estimated Time | Critical? |
|-----|-------|----------------|-----------|
| 1 | Payment setup + research | 2-3 hours | ✅ Yes |
| 2 | Market research + community joining | 2-3 hours | ✅ Yes |
| 3 | Demo video recording | 3-4 hours | ✅ Yes |
| 4 | Landing page creation | 3-4 hours | ✅ Yes |
| 5 | First community posts | 2-3 hours | ✅ Yes |
| 6 | Engagement + outreach | 2 hours | 🟡 Important |
| 7 | Review + plan Week 2 | 1-2 hours | 🟡 Important |
| **Total** | **15-21 hours** | **~2-3 hours/day** | |

**Flexibility:** Can compress to 5 days (3-4 hours/day) if needed

---

## After Week 1: Next Steps

**If Week 1 went well (5+ signups):**
→ Continue to Week 2-3 following [PLAN.md](./PLAN.md)
→ Post in 3-4 more communities
→ Start reaching out to signups directly
→ Prepare for early access launch (Stage 2)

**If Week 1 didn't work (<5 signups):**
→ Don't give up yet! Iterate:
→ Try different messaging (use language from customer conversations)
→ Try different segment (CV vs MCP)
→ Post in different communities (maybe tech Twitter, LinkedIn, etc.)
→ Talk to 5 people 1-on-1 before posting more

**If Week 1 was AMAZING (20+ signups, payment inquiries):**
→ Consider starting Stage 2 earlier (build payment infrastructure)
→ Reach out to hottest leads with early access offer
→ Document what worked (you found product-market fit signals!)

---

## Checklist Summary

**By end of Week 1, you should have:**
- [ ] Working crypto wallet + payment method decided
- [ ] Joined 5-7 target communities
- [ ] 1-2 demo videos recorded and uploaded
- [ ] Live landing page with email capture
- [ ] 2+ posts in communities
- [ ] Customer tracking spreadsheet with data
- [ ] 5-10 waitlist signups (stretch goal)
- [ ] Clear sense of which segment responds better

**What you're learning:**
- Who wants this product?
- What messaging resonates?
- What price point seems fair?
- What objections come up?
- Which communities are best fit?

**What you're NOT doing:**
- Building payment infrastructure (save for Stage 2)
- Coding new features (product is done for now)
- Paid ads (too early, organic first)
- Business entity formation (premature)

---

## Resources Quick Reference

**Documents (in action order):**
- [01-week-1-checklist.md](./01-week-1-checklist.md) - This file (day-by-day plan)
- [02-payment-options.md](./02-payment-options.md) - Crypto wallet setup
- [03-landing-page-copy.md](./03-landing-page-copy.md) - Landing page text (2 versions)
- [04-reddit-posts.md](./04-reddit-posts.md) - Reddit post templates
- [05-outreach-scripts.md](./05-outreach-scripts.md) - DM and email templates
- [06-tracking-template.md](./06-tracking-template.md) - Customer tracking spreadsheet

**External Tools:**
- Wallet: Coinbase Wallet or MetaMask
- Video: Loom (loom.com) or OBS Studio (free)
- Landing Page: Carrd (carrd.co) or Vercel (vercel.com)
- Email: ConvertKit (free for 1,000 subs)
- Analytics: Plausible (plausible.io) or Simple Analytics

**Communities to Post:**
- r/ClaudeAI, r/LocalLLaMA (MCP focus)
- r/resumes, r/careerguidance (CV focus)
- Hacker News (Show HN)
- IndieHackers.com

---

**Version:** 1.0
**Last Updated:** 2026-02-24
**Status:** Ready to execute

**Start now:** Day 1, Task 1 - Set up crypto wallet. You got this! 🚀
