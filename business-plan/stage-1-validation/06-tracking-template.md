# Customer Tracking Spreadsheet Template

**Purpose:** Track all leads, signups, and customer interactions during validation
**How to use:** Copy to Google Sheets or Excel, update daily
**Goal:** Identify patterns, measure traction, spot winning segment

---

## Sheet 1: Waitlist Signups

| Date | Source | Email | Telegram | Segment | Signal | Price Mentioned | Notes | Status |
|------|--------|-------|----------|---------|--------|----------------|-------|--------|
| 2/24 | r/ClaudeAI | john@example.com | @johndoe | MCP Power User | Waitlist signup | - | Asked about self-hosted | Active |
| 2/25 | HN comments | alice@example.com | @alice_dev | Developer | DM: "When ready?" | $20-30 ok | Uses Claude daily | Hot Lead |
| 2/26 | r/resumes | bob@mail.com | @bobby | Job Seeker | Email signup | - | Needs CV by March | Active |

**Columns Explained:**
- **Date:** When they signed up or reached out
- **Source:** Where they found you (Reddit post, HN, referral, etc.)
- **Email:** For waitlist notifications
- **Telegram:** Username for early access (optional but preferred)
- **Segment:** MCP Power User / Job Seeker / Consultant / Developer / Privacy Advocate / Other
- **Signal:** What action they took (Waitlist signup / DM / Comment / Pre-commit / Other)
- **Price Mentioned:** If they said a price, note it ("$25 seems fair", "too expensive", etc.)
- **Notes:** Any important context (use case, concerns, requests)
- **Status:** Active / Hot Lead / Converted / Churned / Unresponsive

---

## Sheet 2: Community Performance

| Community | Date Posted | Post Type | Upvotes | Comments | Clicks | Signups | Conversion % | Notes |
|-----------|-------------|-----------|---------|----------|--------|---------|--------------|-------|
| r/ClaudeAI | 2/24 | Show & Tell (MCP) | 45 | 12 | 150 | 8 | 5.3% | Lots of self-hosted questions |
| r/resumes | 2/25 | Show & Tell (CV) | 23 | 6 | 80 | 3 | 3.75% | Price concerns ($19 too high?) |
| Hacker News | 2/26 | Show HN | 89 | 34 | 320 | 15 | 4.7% | Technical audience, good fit |

**Columns Explained:**
- **Community:** Subreddit, forum, or platform name
- **Date Posted:** When you posted
- **Post Type:** Which template you used (Show & Tell, Ask for Advice, etc.)
- **Upvotes:** Reddit karma or similar engagement metric
- **Comments:** Number of replies
- **Clicks:** Landing page visits from this source (check analytics)
- **Signups:** Waitlist signups attributed to this post
- **Conversion %:** (Signups / Clicks) × 100
- **Notes:** Key takeaways, patterns, feedback themes

**Success Indicators:**
- 🟢 Conversion >5% = great fit, double down
- 🟡 Conversion 2-5% = okay, test different messaging
- 🔴 Conversion <2% = wrong audience or poor messaging

---

## Sheet 3: Customer Conversations

| Date | Contact | Channel | Topic | Key Insights | Action Items | Follow-Up Date |
|------|---------|---------|-------|--------------|--------------|----------------|
| 2/27 | john@example.com | Email | Pricing concerns | Thinks $39 too high, would pay $25 | Consider $25 tier | 3/6 |
| 2/28 | @alice_dev | Telegram DM | Self-hosted setup | Wants Docker deploy, data privacy critical | Add to roadmap | 3/7 |
| 3/1 | bob@mail.com | Reddit DM | Use case | Needs CV for job fair March 15 | Offer early beta access | 3/8 |

**Columns Explained:**
- **Date:** When conversation happened
- **Contact:** Email or username
- **Channel:** Email, Reddit DM, Telegram, etc.
- **Topic:** What they asked about
- **Key Insights:** What you learned (pain points, willingness to pay, objections)
- **Action Items:** What you need to do (build feature, send info, follow up)
- **Follow-Up Date:** When to reach back out

**Why This Matters:**
- Spot patterns (if 5 people ask about self-hosted, it's a real need)
- Track commitments (who said they'd pay? Follow up!)
- Improve messaging (what questions come up repeatedly? Address in FAQ)

---

## Sheet 4: Proof Signals

| Signal Type | Count | Goal | Status | Evidence |
|-------------|-------|------|--------|----------|
| Waitlist Signups | 12 | 20 | 🟡 In Progress | Email list |
| Direct Payment Inquiries | 3 | 5 | 🟡 In Progress | 2 DMs, 1 email |
| Price Confirmations ($15+) | 2 | 3 | 🟡 In Progress | alice: "$25 ok", john: "$20 fair" |
| Demo Video Views | 85 | 50 | ✅ Complete | YouTube analytics |
| Landing Page Visitors | 220 | 100 | ✅ Complete | Plausible analytics |

**Signal Types Explained:**

**1. Waitlist Signups**
- Someone gives you email/Telegram to be notified
- Goal: 20+ signups = people are interested
- Evidence: ConvertKit/Mailchimp export

**2. Direct Payment Inquiries**
- Unprompted questions: "How do I pay?" or "When can I start?"
- Goal: 5+ inquiries = strong demand signal
- Evidence: Screenshots of DMs/emails

**3. Price Confirmations**
- Someone explicitly says "$X/month is reasonable"
- Goal: 3+ confirmations at $15+ = pricing validated
- Evidence: Quote them directly in notes

**4. Demo Video Views**
- People watching your demo
- Goal: 50+ views = distribution working
- Evidence: YouTube/Vimeo analytics

**5. Landing Page Visitors**
- Unique visitors to your site
- Goal: 100+ visitors = getting attention
- Evidence: Plausible/Simple Analytics

**Decision Rule:**
✅ Hit 4/5 proof signals → Move to Stage 2 (build payment MVP)
🟡 Hit 2-3 signals → Keep validating, iterate messaging
🔴 Hit 0-1 signals → Pivot: different segment or different problem

---

## Sheet 5: Feature Requests

| Feature | Requested By (Count) | Segment | Priority | Feasibility | Notes |
|---------|---------------------|---------|----------|-------------|-------|
| Self-hosted deployment | 4 people | Privacy advocates | High | Medium | Docker Compose + docs needed |
| Multiple CV templates | 2 people | Job seekers | Medium | Easy | Add 3-5 templates to generator |
| Team sharing | 1 person | Consultant | Low | Hard | Wait for more demand |
| Slack integration | 1 person | Developer | Low | Medium | After Telegram works well |

**Columns Explained:**
- **Feature:** What they're asking for
- **Requested By:** Number of different people requesting
- **Segment:** Which customer type wants this
- **Priority:** High (5+ requests) / Medium (2-4) / Low (1)
- **Feasibility:** Easy (days) / Medium (weeks) / Hard (months)
- **Notes:** Technical notes or context

**Prioritization Rule:**
- Build: High priority + Easy/Medium feasibility
- Plan: High priority + Hard feasibility (needs planning)
- Backlog: Low priority (wait for more demand)

---

## Sheet 6: Competitive Intel

| Competitor | What They Do | Price | Target Market | Weakness (Our Advantage) | Notes |
|------------|--------------|-------|---------------|-------------------------|-------|
| HireVue | Video interview practice | $30-50/mo | Job seekers | No CV generation, corporate feel | We're more casual/accessible |
| Notion | Knowledge management | Free-$10/mo | Everyone | Not AI-native, manual organization | Ours is conversational |
| Other MCP servers | Various tools | Free/OSS | Developers | No knowledge extraction workflow | We have interview flow |

**Columns Explained:**
- **Competitor:** Product name
- **What They Do:** Core value proposition
- **Price:** Pricing model
- **Target Market:** Who uses it
- **Weakness:** What we do better (your differentiator)
- **Notes:** Observations, ideas

**Why Track Competitors:**
- Identify gaps in market (features no one offers)
- Validate pricing (are you too high/low?)
- Refine positioning (what makes you different?)

---

## How to Use This Template

### Daily Tasks (5-10 minutes)
1. **Add new signups** to Sheet 1 (check email, Reddit DMs, Telegram)
2. **Log conversations** in Sheet 3 (what did people say today?)
3. **Update proof signals** in Sheet 4 (check analytics, count inquiries)

### Weekly Reviews (30 minutes)
1. **Analyze Sheet 2** (which communities work best? Where to post next?)
2. **Review Sheet 5** (are patterns emerging? 3+ people want same feature?)
3. **Update priorities** (what should you build/test next week?)

### Decision Points
- **After 1 week:** Which segment (CV vs MCP) is responding better? Double down on winner.
- **After 2 weeks:** Have you hit 10+ signups? If yes, keep going. If no, pivot messaging.
- **After 3 weeks:** Check Sheet 4 proof signals. Hit 4/5? Move to Stage 2. Miss badly? Re-evaluate.

---

## Example: Spotting Patterns

**Scenario 1: Self-Hosted Demand**
If Sheet 5 shows "Self-hosted deployment" requested by 5+ people:
- ✅ Real demand exists
- Action: Add self-hosted tier ($79/mo) to pricing
- Action: Create Docker Compose setup in Stage 2

**Scenario 2: Price Too High**
If Sheet 3 shows 5+ conversations mention "$39 is too expensive":
- ✅ Pricing issue identified
- Action: Test $25/mo tier
- Action: Better communicate value (emphasize time savings)

**Scenario 3: Wrong Audience**
If Sheet 2 shows r/resumes has 1% conversion but r/ClaudeAI has 8%:
- ✅ MCP technical users are better fit
- Action: Focus on developer/AI communities
- Action: Drop job seeker messaging, emphasize AI memory

---

## Google Sheets Setup (Optional)

**Create This in Google Sheets:**

1. Go to sheets.google.com
2. Create new spreadsheet: "Interview Assistant - Customer Tracking"
3. Create 6 sheets (tabs) with names above
4. Copy column headers from this template
5. Set up conditional formatting:
   - Sheet 4: Green if goal met, yellow if in progress, red if far behind
   - Sheet 1: Highlight "Hot Lead" status in orange
6. Share with yourself only (private data!)

**Tips:**
- Use data validation for dropdowns (Segment, Status, Priority)
- Add charts: signups over time, conversion rate by community
- Export weekly as backup (File → Download → CSV)

---

## Privacy Note

**This spreadsheet contains personal data (emails, usernames).**

- ✅ Keep it private (don't share publicly)
- ✅ Delete data if someone requests it
- ✅ Export/delete after Stage 1 if you don't proceed
- ❌ Don't upload to public repos
- ❌ Don't sell/share with third parties

---

**Version:** 1.0
**Last Updated:** 2026-02-24
**Status:** Ready to use

**Next:** Copy this to Google Sheets or Excel and start tracking!
