# Reddit Post Templates

**Usage:** Copy, customize with your details, post to target communities
**Tracking:** Note which version/community performs best

---

## Template 1A: Show & Tell (MCP Focus)

**Ideal for:** r/ClaudeAI, r/LocalLLaMA, r/ChatGPT

**Title:**
```
I built an MCP server that actively interviews you (not just passive memory like Mem0)
```

**Body:**
```
Hey everyone,

Tried Mem0 and similar memory tools but found them too shallow --
they passively capture fragments like "user prefers Python."

Wanted something deeper. Built an MCP server that actually
interviews you, like a journalist building a profile.

**How it's different from Mem0/Zep/etc:**
- ACTIVE interviews (Telegram bot asks follow-up questions)
- Tracks coverage (knows what it's asked about and what it hasn't)
- Extracts structured knowledge, not fragments
- Progressive deepening (first pass = overview, later = specifics)

**Result:**
Instead of: "user knows Python"
You get: "Led Python migration at Acme Corp (2023). Converted 500K LOC
Java monolith to Python microservices. Team of 8. Reduced deploy time 60%."

Claude/ChatGPT/Cursor can now write cover letters, prep for interviews,
and reference your actual projects -- with real specifics.

Also auto-generates ATS-optimized resumes from your knowledge.

Demo: [LINK]
More info: [LINK]

**Questions:**
1. Anyone else found passive memory tools too shallow?
2. Would active interviews be worth paying for ($12-29/mo)?
3. What knowledge would you want your AI to remember most?

Thanks!
```

**Engagement Strategy:**
- Respond to EVERY comment within 6 hours
- If someone mentions Mem0, explain the difference (active vs passive) without being negative
- Ask follow-up questions
- Don't be defensive about criticism
- Share architecture details if asked

**Prepared answers for likely comments:**

"How is this different from Mem0?"
-> "Mem0 passively captures fragments from your conversations. This actively interviews you -- systematically, with follow-ups. Think security camera vs journalist interview. The knowledge extracted is much deeper and more structured."

"Why not just use Claude Projects / custom instructions?"
-> "Character limits. And they don't extract knowledge -- you have to write it yourself. This interviews you and extracts it automatically. Like a career coach who documents everything."

---

## Template 1B: Show & Tell (CV Focus)

**Ideal for:** r/resumes, r/careerguidance, r/jobs

**Title:**
```
Built an AI that interviews you like a career coach and writes your resume
```

**Body:**
```
I know what you're thinking: "just use ChatGPT." Hear me out.

**The problem with ChatGPT for resumes:**
You paste your info, it spits out "results-oriented professional
with proven track record." Generic. Recruiter sees through it.
The real issue: most people can't articulate their own accomplishments
well enough for ChatGPT to work with.

**What I built instead:**
An AI that interviews you like a career coach. It asks follow-up
questions, draws out specifics, catches things you'd forget.

The difference:
  Before: "Managed a development team"
  After:  "Led 12-person engineering team that delivered $2M
           platform migration 3 weeks ahead of schedule"

You already know this stuff. You just need something to ask
the right questions.

**How it works:**
- Chat with Telegram bot for 10-15 minutes
- AI asks smart follow-ups (like a real career coach would)
- Extracts accomplishments, quantifies impact
- Generates ATS-optimized PDF resume automatically
- Update anytime with a quick 5-minute follow-up chat

**Free tier** available -- one interview + one resume generation.
No credit card. See if it works for you.

Demo: [LINK]

**Honest question:**
$12/month or $79 lifetime seem fair? Or would you only use a
free tier? Trying to figure out pricing.
```

**Engagement Strategy:**
- Offer to generate sample resume for 2-3 commenters (free beta access)
- Ask what they currently use (Word? Canva? Teal? Rezi?)
- Note objections (too expensive, prefer manual, ChatGPT is enough)
- Address "just use ChatGPT" with the career coach comparison

**Prepared answers for likely comments:**

"Just use ChatGPT"
-> "ChatGPT polishes text you give it. But most people undersell themselves. This interviews you -- asking 'what was the impact?' 'how big was the team?' 'what happened after?' It captures things you'd forget to mention. Like having a career coach for $12/mo instead of $400."

"Is it ATS-friendly?"
-> "Yes! Clean formatting, proper heading hierarchy, keyword-rich content. Designed to pass the automated screening that rejects 75% of resumes."

"Why not free?"
-> "There IS a free tier -- one interview + one resume. If that works for you, great! Paid is for unlimited updates and AI memory features."

---

## Template 2: Soft Launch (Ask for Advice)

**Ideal for:** r/SideProject, IndieHackers, Hacker News

**Title:**
```
Show HN: Interview assistant + MCP server for AI memory
```

**Body:**
```
Hi HN,

Built an interview assistant that gives AI long-term memory.

**Background:**
Using Claude for work, constantly repeating context. Thought: what if
Claude could search past conversations?

**How it works:**
1. Quick Telegram interview (conversational, not a form)
2. AI extracts knowledge → summaries + embeddings
3. MCP server exposes search to Claude/ChatGPT/Cursor
4. AI assistants can now reference your knowledge

**Use cases so far:**
- Cover letter writing (AI knows your real projects)
- Interview prep (recall accomplishments on demand)
- Knowledge management (search past conversations)
- CV generation (auto-generated from your data)

**Tech stack:**
- Python/LangGraph for interview workflow
- OpenAI/Gemini for extraction
- SQLite + vector search
- MCP protocol for AI integration
- Telegram bot for UX

**Status:**
Working but rough. Considering launching as service. Questions:

1. Privacy-first (self-hostable, crypto option) vs mainstream appeal?
2. $12-29/mo with free tier seem fair?
3. Focus on developers or broader (job seekers, consultants)?

Demo: [LINK]
Docs: [LINK]

Feedback welcome. Roast it if you need to—want to know if this is
worth building further.
```

**Engagement Strategy:**
- Expect technical questions—answer thoroughly
- If someone requests feature, add to backlog publicly
- Share architecture details if asked
- Don't hide challenges (shows authenticity)

---

## Template 3: Problem-First (Community Engagement)

**Ideal for:** Any community where you see relevant discussions

**Title:**
```
How do you give Claude/ChatGPT persistent context about yourself?
```

**Body:**
```
Curious how others handle this:

Every Claude conversation starts from zero. I end up copying the same
background info repeatedly:
- "I'm a [role] working on [projects]"
- "I prefer [coding style/framework/approach]"
- "My experience includes [list of things]"

Feels inefficient. Currently experimenting with an MCP server that
stores interview responses and lets Claude search them. But wondering
if there's a better approach?

**What I've tried:**
- Custom instructions (too short, not searchable)
- Pasting from Notion (manual, gets outdated)
- Projects feature (doesn't work for personal context)

**What works for you?**

(Demo of my MCP approach: [LINK] if you want to see what I mean)
```

**Engagement Strategy:**
- Genuinely engage with other solutions people suggest
- Compare your approach to theirs (pros/cons)
- Don't push your product hard—let curiosity drive clicks
- If someone says "this is useful", follow up in DMs

---

## Template 4: Stealth Mention (Comment on Relevant Thread)

**When someone asks:** "How do I make Claude remember things?" or "Best MCP servers?"

**Comment:**
```
I built something for exactly this—MCP server that stores conversational
interviews and lets Claude search your knowledge.

Quick Telegram chat → structured storage → Claude can query it later.

Working well for me (cover letters, interview prep, etc.). Still early
but might solve your problem.

Demo: [LINK]

Happy to answer questions if you try it.
```

**When to Use:**
- Someone explicitly asks for recommendations
- You can genuinely help (not just spamming link)
- Add value first, mention product second

---

## Template 5: Success Story (After Stage 2)

**Use when:** You have 5-10 paying customers and testimonials

**Title:**
```
Update: 10 people are now paying for the AI memory tool I posted last month
```

**Body:**
```
Last month I posted about an MCP server for AI memory.
Got mixed feedback—some loved it, some skeptical.

Decided to launch early access anyway. Results:

**What happened:**
- 50+ waitlist signups from that thread
- Reached out to 15 people offering early access ($12/mo)
- 10 said yes and paid (60%+ conversion!)
- Been using it for 2-3 weeks, mostly positive feedback

**What people actually use it for:**
1. Cover letter generation (most popular)
2. Interview prep (recall projects/accomplishments)
3. Consulting calls (AI remembers client context)
4. Knowledge search (find that thing I said 3 weeks ago)

**Biggest learning:**
The CV generation feature is way more popular than I expected.
Most users don't care about the technical MCP stuff—they just want
their resume updated easily.

**What's next:**
- Self-hosted option (requested by 4/10 users)
- Better CV templates
- Team features (companies want this?)

Original post: [LINK]
Product: [LINK]

If you tried it from last thread, curious how it went!
```

**Why This Works:**
- Social proof (real customers)
- Transparency (share numbers)
- Lessons learned (not just bragging)
- Invites continued discussion

---

## Posting Schedule & Strategy

### Week 1
- **Day 1:** r/ClaudeAI (Template 1A - MCP focus)
- **Day 2:** r/resumes (Template 1B - CV focus)
- **Day 3:** Hacker News Show HN (Template 2)
- **Day 4-7:** Engage with comments, answer questions

### Week 2
- **Day 8:** r/LocalLLaMA (Template 1A with edits based on feedback)
- **Day 10:** r/selfhosted (mention self-hostable feature)
- **Day 12:** IndieHackers (Template 2)
- **Day 14:** Review which community responded best

### Week 3
- **Day 15-17:** Stealth comments (Template 4) on relevant threads
- **Day 18-21:** Respond to anyone who reached out via DM

---

## Posting Best Practices

**Before Posting:**
- ✅ Read community rules (some ban self-promo)
- ✅ Check for "Self-Promotion Saturday" or similar allowed days
- ✅ Have demo video ready (people will ask)
- ✅ Clear your schedule for 2-3 hours after posting (engage immediately)

**After Posting:**
- ✅ Respond to first 5 comments within 30 minutes (boosts visibility)
- ✅ Answer every question (even critical ones)
- ✅ Don't argue or get defensive
- ✅ Upvote thoughtful comments (even if negative)
- ✅ Thank people for feedback

**What to Avoid:**
- ❌ Don't spam multiple communities same day (looks desperate)
- ❌ Don't use exact same post twice (customize per community)
- ❌ Don't ignore negative feedback (engage constructively)
- ❌ Don't delete post if it goes poorly (learn from it)
- ❌ Don't buy upvotes (ban risk, looks fake)

---

## Measuring Success

**Engagement Metrics:**
- Upvotes (50+ = good, 200+ = great)
- Comments (20+ = good discussion)
- Landing page clicks (check analytics)
- Waitlist signups (5+ from one post = success)
- Direct messages (2+ asking about pricing = very good)

**What to Track:**

| Post | Community | Upvotes | Comments | Clicks | Signups | Notes |
|------|-----------|---------|----------|--------|---------|-------|
| MCP v1 | r/ClaudeAI | 45 | 12 | 150 | 8 | Asked about self-hosted |
| CV v1 | r/resumes | 23 | 6 | 80 | 3 | Price concerns |

**Iterate Based on Data:**
- High upvotes, low signups → landing page problem (fix CTA)
- Low upvotes, high signups → post didn't go viral but right audience
- Lots of questions about X → X is confusing (clarify in next post)

---

## DM Response Templates

**When someone asks "How much does it cost?"**
```
Hey! Thanks for asking.

Still in early testing, but planning $12/mo for CV access,
$29/mo for full platform (MCP server, AI memory, etc.).

Credit card, Apple Pay, crypto all accepted.

I'm doing early access starting [DATE]. Want to try it?
Would give you first month free for feedback.
```

**When someone asks "When will it be ready?"**
```
Aiming for Q2 2026 launch, but doing small early access group
starting next month.

Want to be in the first batch? Just need email + Telegram handle
and I'll reach out when ready.
```

**When someone asks technical question:**
```
Good question! [Answer thoroughly with specifics]

If you want to try it, happy to set up a test account.
Still rough around edges but core features work.
```

---

## Red Flags (When to Pivot Messaging)

**If you see these patterns, change approach:**

1. **"Too expensive"** in 5+ comments
   → Lower price OR better communicate value

2. **"Why not just use X?"** (competitor mentions)
   → Clarify differentiation, mention in future posts

3. **"How do I pay?"**
   → Credit card, Apple Pay, Google Pay. Crypto (USDC/BTC) also available.

4. **"Seems complicated to set up"**
   → Create better onboarding materials, emphasize simplicity

5. **Zero engagement on multiple posts**
   → Wrong communities OR wrong messaging (try different angle)

---

**Version:** 1.0
**Last Updated:** 2026-02-24
**Status:** Ready to use
