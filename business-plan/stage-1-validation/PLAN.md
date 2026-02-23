# Stage 1: Validation & Proof of Concept

**Timeline:** 2-3 weeks
**Budget:** $0-50
**Goal:** Get 10-20 people to say "I want this, how do I pay?"

---

## Hypothesis to Test

**Primary Hypothesis (Lower Risk):**
"Professionals need better knowledge management and CV generation from conversational interviews, and will pay $15-40/month for it."

**Secondary Hypothesis (Higher Risk, Higher Value):**
"Technical users want to give ANY AI assistant (Claude, ChatGPT, Gemini, Cursor, etc.) long-term memory via MCP server."

**Strategy:** Test BOTH. See which converts better. Don't put all eggs in MCP basket.

## Proof of Success

- ✅ 20+ waitlist signups (email + Telegram username)
- ✅ 5+ direct messages asking "when can I pay?"
- ✅ 3+ people saying "I'd pay $X/month" (where X ≥ $15)

**If you get this proof, Stage 1 is successful. Move to Stage 2.**

---

## Phase 1.1: Create Demo Materials (Week 1, Days 1-3)

### Task 1.1.1: Record Demo Video (90 seconds)

**Goal:** Show the product working, make it tangible

**Script Version A: MCP Focus (Technical Audience)**
```
[0:00-0:15] The Problem
"AI assistants forget everything. You repeat yourself constantly."

[0:15-0:45] The Solution
"Interview Assistant + MCP gives ANY AI long-term memory."
- Show: Quick Telegram interview (10 seconds)
- Show: Claude/ChatGPT/Cursor querying your knowledge via MCP
- Show: AI writing cover letter using YOUR real experience

[0:45-1:15] The Benefits
"Works with Claude Desktop, ChatGPT, Cursor, any MCP-compatible AI."
"Privacy-first: crypto payments, self-hostable, your data."
"5-minute setup. Works today."

[1:15-1:30] Call to Action
"Early access opening Q2 2026. Join waitlist at [URL]"
```

**Script Version B: Non-Technical Focus (Broader Audience)**
```
[0:00-0:15] The Problem
"Updating your resume takes hours. You forget half your accomplishments."

[0:15-0:45] The Solution
"Interview Assistant: Talk to a bot, get a perfect CV."
- Show: Quick Telegram interview (natural conversation)
- Show: Auto-generated professional CV (PDF)
- Show: AI assistant can query your knowledge anytime

[0:45-1:15] The Benefits
"No typing. Just talk naturally about your experience."
"Professional CV generated automatically."
"Privacy-first: crypto payments, your data stays yours."

[1:15-1:30] Call to Action
"Free tier available. Early access at [URL]"
```

**Recommendation:** Record BOTH versions. Test which gets better response.

**How to Record:**
1. Use OBS Studio or Loom (free)
2. Screen recording: Claude Desktop + Telegram side by side
3. Voiceover: clear audio (use phone mic if needed)
4. Edit: Kapwing or DaVinci Resolve (free)
5. Export: 1080p, upload to YouTube (unlisted)

**Deliverable:** YouTube video link

---

### Task 1.1.2: Create Landing Page (Days 2-3)

**Option A: No-Code (Fastest)**
Use Carrd.co ($19/year) or free alternatives:
- One-page site
- Embed demo video
- Email capture form
- "Notify Me When Ready" button

**Option B: Custom HTML (Free, More Control)**
Deploy to Vercel (free tier):
- Single HTML page with Tailwind CSS
- Embed YouTube video
- ConvertKit or Mailchimp form embed
- Takes 3-4 hours if you know HTML

**Landing Page Structure:**
```
──────────────────────────────────
HERO SECTION
──────────────────────────────────
Headline: "Give Claude Perfect Memory"

Subheadline: "AI interview assistant that makes your
knowledge searchable by Claude Desktop"

[Demo Video Embed - 90 seconds]

[Notify Me] button (email capture)

──────────────────────────────────
PROBLEMS (3 Bullets)
──────────────────────────────────
❌ Claude forgets everything after chat ends
❌ You repeat yourself constantly
❌ Can't reference past conversations

──────────────────────────────────
SOLUTION (How It Works)
──────────────────────────────────
1️⃣ Quick Telegram interview (10 minutes)
2️⃣ AI extracts knowledge + creates vectors
3️⃣ Claude searches your data via MCP

──────────────────────────────────
BENEFITS (3 Columns)
──────────────────────────────────
🧠 Conversational Collection    🔒 Privacy-First         ⚡ Works Today
No boring forms                 Crypto payments          Claude Desktop
Just talk naturally             Self-hostable            Telegram bot ready

──────────────────────────────────
PRICING PREVIEW
──────────────────────────────────
Free: 1 interview + 1 CV (try it)
CV Pro: $12/mo or $79 lifetime
Knowledge Pro: $29/mo (MCP included)
Self-Hosted: $59/mo

💳 Credit card, Apple Pay, crypto accepted

──────────────────────────────────
CALL TO ACTION
──────────────────────────────────
[Join Waitlist - Launching Q2 2026]

Email: ________________
Telegram: @____________

[Notify Me] button
──────────────────────────────────
```

**Deliverable:** Live URL (yourdomain.com or vercel.app)

---

## Phase 1.2: Distribution & Proof Collection (Week 1-3)

### Task 1.2.1: Identify Target Communities (Day 4)

**Find 7-10 communities where your target customers already discuss pain points:**

**MCP / AI Power Users (Technical - Higher Risk):**
- r/ClaudeAI (Reddit) - 50K+ members
- r/LocalLLaMA (Reddit) - 100K+ members
- r/ChatGPT (Reddit) - 5M+ members
- Claude Discord, OpenAI Discord
- Cursor/Windsurf user communities
- MCP GitHub Discussions

**Career / Resume / Job Seekers (Non-Technical - Lower Risk, Bigger Market):**
- r/resumes (Reddit) - 500K+ members
- r/careerguidance (Reddit) - 800K+ members
- r/jobs (Reddit) - 2M+ members
- LinkedIn groups (job search, career coaching)
- Tech career Discord communities

**Privacy/Self-Hosted:**
- r/selfhosted (Reddit) - 500K+ members
- r/privacy (Reddit) - 1M+ members
- Privacy Guides Discord
- Hacker News (news.ycombinator.com)

**Developers/Productivity:**
- r/productivity (Reddit)
- r/PKMS (Personal Knowledge Management)
- IndieHackers.com
- Dev.to

**How to Evaluate:**
1. Search: "[problem keyword]" in each community
   - "Claude forgets everything"
   - "Claude memory"
   - "MCP server recommendations"
2. Count: How many posts in last 30 days?
3. Check rules: Are "Show HN" / self-promo posts allowed?
4. Join: Subscribe/join 5-7 most active communities

**Deliverable:** Spreadsheet with community names, rules, post ideas

---

### Task 1.2.2: Post in Communities (Week 2-3)

**Goal:** Get landing page in front of 1,000-5,000 people organically

**Posting Strategy:**

**Option 1A: MCP Technical Post**
```
Title: "I built an MCP server that gives AI assistants long-term memory"

Body:
"Frustrated with AI forgetting everything after each chat? Built a solution.

Interview Assistant:
- Conversational knowledge collection (Telegram/CLI)
- Extracts structured data + embeddings
- MCP server for ANY compatible AI (Claude, ChatGPT, Cursor, etc.)
- Your AI can now search past conversations

Example: Told it about my career once. Now Claude/ChatGPT write
cover letters using my real projects and skills.

5-minute setup. Works today.

Demo: [YouTube link]
Early access: [Landing page]

Feedback welcome!"
```

**Option 1B: Non-Technical CV Focus Post**
```
Title: "Built a bot that generates your CV from natural conversation"

Body:
"I hate updating resumes. Built something better.

Interview Assistant:
- Talk to Telegram bot about your experience (10-15 minutes)
- AI extracts accomplishments, skills, projects
- Auto-generates professional CV (PDF)
- Bonus: Any AI assistant can query your knowledge

No typing. No formatting. Just talk naturally.

Example CV: [screenshot]
Demo: [YouTube link]
Try it: [Landing page]

Looking for feedback - who needs this?"
```

**Option 2: "Ask for Advice" Post**
```
Title: "How do you give Claude context about yourself?"

Body:
"Curious how others handle this: every Claude conversation
starts from zero. I end up copying the same background info
repeatedly.

I've been experimenting with an MCP server that stores
interview responses and lets Claude search them. Works but
wondering if others have better solutions?

Demo: [link] if you want to see what I mean.

What's your workflow for giving Claude persistent context?"
```

**Option 3: "Helpful Comment" (Stealth Promo)**
When you see someone asking about Claude memory or MCP servers:
```
"I built something for this - MCP server that stores interview
data and lets Claude search it. Still testing but seems to work.

Demo: [link] if you want to check it out."
```

**Posting Schedule:**
- Day 1: Post to r/ClaudeAI
- Day 2: Post to r/LocalLLaMA
- Day 3: Post to Hacker News "Show HN"
- Day 4-5: Respond to comments, engage genuinely
- Day 7: Post to r/selfhosted
- Day 10: Post to r/privacy
- Day 14: Post to IndieHackers

**Rules:**
- ❌ Don't spam - one post per community, ever
- ❌ Don't be salesy - focus on solving problem
- ✅ Respond to every comment within 24 hours
- ✅ Ask questions back, be genuinely curious
- ✅ Mention it's early/experimental (people like helping)

**Deliverable:** 5-7 posts published, engagement tracked

---

### Task 1.2.3: Track Proof Signals (Ongoing)

**Create a Spreadsheet:**

| Date | Source | Contact | Signal | Notes |
|------|--------|---------|--------|-------|
| 2/24 | Reddit r/ClaudeAI | u/john_doe | Waitlist signup | Asked about pricing |
| 2/25 | HN comments | hn_user123 | DM: "When ready?" | Wants self-hosted |
| 2/26 | Email waitlist | alice@example.com | Email signup | Mentioned $40/mo ok |

**Signals to Track:**
1. **Waitlist signups** (email + Telegram username)
2. **Direct messages** asking "when can I pay?"
3. **Price validation** ("I'd pay $X")
4. **Feature requests** (tells you what they value)
5. **Competitor mentions** ("better than X because...")

**How to Capture:**
- Email signups: ConvertKit/Mailchimp export to spreadsheet
- Reddit DMs: Screenshot or copy to spreadsheet
- Comments: Tag as "interested" or "just curious"

**Deliverable:** Proof tracking spreadsheet (update daily)

---

## Phase 1.3: Engage & Learn (Week 2-3)

### Task 1.3.1: Respond to Every Inquiry

**Goal:** Learn what they care about, refine messaging

**When someone shows interest:**

1. **Thank them:**
   "Thanks for signing up! Really helpful to know there's demand."

2. **Ask a question:**
   "Quick question - what would you use this for most?
   (Cover letters, interview prep, knowledge search, something else?)"

3. **Offer early access:**
   "I'm doing early testing in March. Want to try it before launch?
   ($12/mo, free tier available, cancel anytime)"

**What You're Learning:**
- Which use case resonates most?
- What price point do they expect?
- What concerns do they have?
- Are they crypto-comfortable?

**Deliverable:** Notes from 10-20 conversations

---

### Task 1.3.2: Identify Patterns (End of Week 3)

**Review your proof tracking spreadsheet and answer:**

1. **Who wants this most?**
   - Developers? Consultants? Students? Privacy advocates?
   - Which segment has most signups?

2. **What problem are they solving?**
   - Claude memory? Knowledge management? CV generation?
   - Which pain point gets mentioned most?

3. **What's the willingness to pay?**
   - Did anyone mention a price?
   - Any pushback on pricing?

4. **What's the biggest objection?**
   - "Too expensive"? "Don't trust crypto"? "Need self-hosted"?

5. **Which community worked best?**
   - Where did you get most signups?
   - Where did you get best engagement?

**Deliverable:** 1-page summary answering these questions

---

## Stage 1 Success Criteria

**Check these boxes before moving to Stage 2:**

- [ ] **20+ waitlist signups** (emails collected)
- [ ] **5+ direct inquiries** about payment ("when can I pay?")
- [ ] **3+ price confirmations** (people saying $15-40 is reasonable)
- [ ] **Demo video** has 50+ views
- [ ] **Landing page** gets 100+ visitors
- [ ] **Clear winning segment** identified (who wants it most)

**If you hit these numbers: Stage 1 successful. Move to Stage 2.**

**If you don't hit these numbers after 3 weeks:**
- ❌ <10 signups → Messaging problem (try different angle)
- ❌ Views but no signups → Value prop unclear (fix landing page)
- ❌ No traffic → Distribution problem (find better communities)

---

## Budget Breakdown

| Item | Cost | Required? |
|------|------|-----------|
| Domain name (optional) | $10-15/yr | No (use Vercel subdomain) |
| Carrd.co (landing page) | $19/yr | No (use free tier or code own) |
| Video editing (Kapwing Pro) | $0-20 | No (free tier works) |
| ConvertKit (email) | $0 | No (free tier = 1,000 subscribers) |
| **Total** | **$0-50** | |

**Recommendation:** Start with $0 setup (Vercel + ConvertKit free), only pay if getting traction.

---

## Timeline

**Week 1:**
- Days 1-3: Create demo video + landing page
- Day 4: Identify communities
- Days 5-7: First 2-3 posts

**Week 2:**
- Days 1-3: More posts (3-4 communities)
- Days 4-7: Respond to comments, engage

**Week 3:**
- Days 1-3: Final posts
- Days 4-7: Review results, decide next stage

**Total: 2-3 weeks to validate demand**

---

## Next Steps

## Action Materials (In Order)

| # | File | What It Covers | When |
|---|------|---------------|------|
| 1 | [Week 1 Checklist](./01-week-1-checklist.md) | Day-by-day actions | Day 1 |
| 2 | [Payment Options](./02-payment-options.md) | Polar.sh + crypto setup | Day 1-2 |
| 3 | [Landing Page Copy](./03-landing-page-copy.md) | Website text (2 versions) | Day 4-5 |
| 4 | [Reddit Posts](./04-reddit-posts.md) | Community post templates | Day 5-6 |
| 5 | [Outreach Scripts](./05-outreach-scripts.md) | DM/email templates | Day 6+ |
| 6 | [Tracking Template](./06-tracking-template.md) | Customer tracking system | Day 2+ |
| 7 | [SEO Strategy](./07-seo-strategy.md) | Keywords, blog calendar, on-page SEO | Week 2+ |

---

If Stage 1 succeeds -> [Stage 2: First Paid Proofs](../stage-2-mvp/PLAN.md)

If Stage 1 fails -> Iterate:
1. Try different messaging (different problem angle)
2. Try different segment (maybe consultants instead of developers)
3. Try different channel (maybe Twitter instead of Reddit)
4. Consider: Is the product actually needed?
