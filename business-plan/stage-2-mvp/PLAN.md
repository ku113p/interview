# Stage 2: First Paid Proofs

**Timeline:** 3-4 weeks
**Budget:** $50-200
**Goal:** Get 5-10 people to actually pay (automated via Polar.sh)

**Prerequisite:** Stage 1 completed successfully (20+ signups, 5+ inquiries)

---

## Hypothesis to Test

"People from Stage 1 waitlist will convert to paying customers when offered early access at $12-29/month."

## Proof of Success

- 5+ people pay (credit card or crypto)
- 3+ people actively use the product after paying
- 2+ people send positive feedback or testimonial
- 0 payment refunds/complaints

**If you get this proof, Stage 2 is successful. Move to Stage 3.**

---

## Phase 2.1: Activate Payment System (Week 1, Days 1-3)

### Task 2.1.1: Configure Polar.sh Products (Day 1)

**Goal:** Payment links ready for customers to click and pay

**Setup Steps:**
1. Log into Polar.sh (set up in Stage 1)
2. Create products:

| Product | Type | Price | Description |
|---------|------|-------|-------------|
| CV Pro Monthly | Subscription | $12/mo | Unlimited interviews + CV generations |
| CV Pro Lifetime | One-time | $79 | Same features, pay once |
| Knowledge Pro | Subscription | $29/mo | CV Pro + MCP server access |
| Self-Hosted | Subscription | $59/mo | Everything + Docker deployment |

3. Get payment links for each product
4. Test checkout flow yourself ($1 test payment)
5. Set up webhook URL for payment notifications

**Deliverable:** Working payment links + tested checkout flow

---

### Task 2.1.2: Set Up Crypto Option (Day 2)

**For privacy-conscious customers (secondary option):**

1. Confirm wallet is set up (from Stage 1)
2. Create payment instructions page:

```
Pay with Crypto (Privacy Option):

Send USDC on Base to: 0xYourAddress
- CV Pro: $12 USDC (monthly) or $79 USDC (lifetime)
- Knowledge Pro: $29 USDC (monthly)

After sending:
1. Email transaction hash to payment@yourdomain.com
2. Include your email + Telegram username
3. We'll activate within 24 hours

Need help? Email support@yourdomain.com
```

**Deliverable:** Crypto payment instructions page

---

### Task 2.1.3: Create Email Templates (Day 3)

**Template 1: Early Access Invitation** (send to waitlist)
```
Subject: Early access is open - your AI career coach is ready

Hi [name],

You signed up for Interview Assistant waitlist. Early access
is now open!

What you get:
- AI career coach interviews (Telegram bot)
- ATS-optimized resume generation
- AI assistant memory (Claude, ChatGPT, Cursor can query your knowledge)
- 30-day money-back guarantee

Try it free: 1 interview + 1 resume at no cost.
Upgrade: $12/month or $79 lifetime for unlimited access.

[Get Early Access] -> link to landing page with payment options

Limited spots: 20 users this round.

Questions? Reply to this email.

Best,
[Your name]
```

**Template 2: Payment Received Confirmation**
```
Subject: You're in! Here's your Interview Assistant access

Hi [name],

Payment confirmed! Welcome to Interview Assistant.

YOUR ACCESS:
- API Key: sk_live_[key]
- Tier: [CV Pro / Knowledge Pro / Self-Hosted]
- Expires: [date] (auto-renews via your card)

GET STARTED (5 minutes):

1. Start Your First Interview
   Open Telegram, find @yourbot, send /start
   Chat naturally about your experience (10-15 min)

2. Generate Your Resume
   After interview, send /generate_cv in Telegram
   Download your ATS-optimized PDF

3. [Knowledge Pro+] Set Up MCP Server
   Add to Claude Desktop config:
   {
     "mcpServers": {
       "interview": {
         "type": "http",
         "url": "https://yourdomain.com/mcp",
         "headers": {"Authorization": "Bearer YOUR_KEY"}
       }
     }
   }
   Test: Ask Claude "What do you know about me?"

NEED HELP?
- Setup guide: [link]
- Video tutorial: [link]
- Reply to this email

Thanks for being an early user!
[Your name]
```

**Template 3: Welcome Email (24 hours after access)**
```
Subject: Getting the most out of Interview Assistant

Hi [name],

Hope you've tried your first interview! Quick tips:

1. Interview in chunks (15-20 min sessions work best)
2. Answer naturally - the AI asks smart follow-ups
3. Be specific about numbers - "team of 8" beats "worked with team"
4. Generate CV after 2-3 sessions for best results
5. [Knowledge Pro] Test in Claude: "What are my Python projects?"

GOT FEEDBACK?
Reply with what's working (or not). You're shaping the product.

Best,
[Your name]
```

**Deliverable:** 3 email templates ready to send

---

## Phase 2.2: Convert Waitlist (Week 1-2)

### Task 2.2.1: Send Early Access Invitations (Day 4-5)

**Goal:** Convert waitlist to paying customers

**Steps:**
1. Email all waitlist signups (from Stage 1)
2. Send in batches: 10 emails per day
3. Track opens/clicks (ConvertKit shows this)
4. Follow up non-openers after 3 days with different subject line

**What to Expect:**
- 30-50% open rate (waitlist is warm)
- 10-20% click-through (payment page)
- 5-15% conversion (actual payment, higher with free tier)

**Example (20 waitlist signups):**
- 10 opens -> 3 click payment -> 5 try free tier -> 1-2 convert to paid

**Deliverable:** Emails sent, responses tracked

---

### Task 2.2.2: Process Payments (Ongoing)

**For Polar.sh payments (automatic):**
1. Polar sends webhook when payment succeeds
2. For MVP: email notification -> you manually create API key
3. Send welcome email (Template 2) with API key
4. Add to customer spreadsheet

**For crypto payments (manual):**
1. Verify transaction on basescan.org
2. Create API key via admin CLI
3. Send welcome email with API key

```bash
# Create new paid key
uv run python -m src.cli.admin create_key \
  --email "user@example.com" \
  --telegram "@username" \
  --tier "cv_pro" \
  --days 30
```

**Total time per customer:** 5 minutes (Polar) or 10 minutes (crypto)

**Deliverable:** Payment processing workflow documented

---

### Task 2.2.3: Support First Customers (Week 2-4)

**Goal:** Keep early customers happy, learn pain points

**Support Channels:**
- Email (primary): respond within 12 hours
- Telegram: for quick questions

**Common Questions (prepare answers):**
1. "How do I set up MCP in Claude Desktop?"
   -> Link to setup guide with screenshots

2. "Telegram bot not responding"
   -> Check /start command, verify bot username

3. "Claude can't see my data"
   -> Need to complete at least 1 interview session

4. "How do I generate CV?"
   -> Use /generate_cv command in Telegram

5. "Can I get refund?"
   -> Yes! Process via Polar.sh dashboard (credit card) or send USDC back (crypto)

6. "Is the resume ATS-friendly?"
   -> Yes, clean formatting, keyword-rich, proper hierarchy

**Deliverable:** Support log + FAQ document (add as you go)

---

## Phase 2.3: Build Minimal Features (Week 2-3)

### Task 2.3.1: Add Payment Tracking to Database

**Goal:** Track who paid, when expires, what tier

**Database Changes:**
```sql
-- Add to api_keys table
ALTER TABLE api_keys ADD COLUMN expiry_date REAL;
ALTER TABLE api_keys ADD COLUMN tier TEXT; -- 'free', 'cv_pro', 'knowledge', 'self_hosted'
ALTER TABLE api_keys ADD COLUMN payment_source TEXT; -- 'polar', 'crypto', 'free'
ALTER TABLE api_keys ADD COLUMN polar_customer_id TEXT;
```

**Files to modify:**
- `src/infrastructure/db/schema.py` - add migration
- `src/infrastructure/db/models.py` - update ApiKey model

**Deliverable:** Database updated to track payments

---

### Task 2.3.2: Create Admin CLI Commands

**Goal:** Make customer management faster

**Commands to build:**
```bash
# Create new paid key
uv run python -m src.cli.admin create_key \
  --email "user@example.com" \
  --telegram "@username" \
  --tier "cv_pro" \
  --days 30

# Extend existing key
uv run python -m src.cli.admin extend_key \
  --key-id "abc123" \
  --days 30

# List expiring keys (remind customers)
uv run python -m src.cli.admin list_expiring \
  --days 7

# Show customer details
uv run python -m src.cli.admin show_customer \
  --email "user@example.com"
```

**Files to create:**
- `src/cli/admin_commands.py` - CLI commands
- `src/infrastructure/db/admin_queries.py` - admin database functions

**Deliverable:** Working admin commands

---

### Task 2.3.3: Add Expiry Check to MCP Server

**Goal:** Block expired keys from using MCP

**Modify auth middleware:**
```python
# In src/processes/mcp_server/auth.py

async def _resolve_user_id(context: MiddlewareContext) -> uuid.UUID:
    # ... existing code ...

    api_key = await ApiKeysManager.get_by_key(key)
    if api_key is None:
        raise PermissionError("Invalid API key")

    # NEW: Check expiry
    if api_key.expiry_date and api_key.expiry_date < time.time():
        raise PermissionError("API key expired - please renew subscription")

    # NEW: Check tier access
    if context.requires_mcp and api_key.tier == "cv_pro":
        raise PermissionError("MCP access requires Knowledge Pro or higher")

    return api_key.user_id
```

**Deliverable:** Expired and under-tiered keys blocked appropriately

---

### Task 2.3.4: Add Polar.sh Webhook Handler (Optional but Recommended)

**Goal:** Auto-provision API keys when Polar payment succeeds

```python
# New file: src/processes/payment/polar_webhook.py

async def handle_polar_webhook(request):
    event = verify_polar_signature(request)

    if event["type"] == "subscription.created":
        user_email = event["data"]["customer"]["email"]
        tier = map_polar_product_to_tier(event["data"]["product_id"])
        api_key = await create_api_key(user_email, tier, days=30)
        await send_welcome_email(user_email, api_key)

    elif event["type"] == "subscription.renewed":
        await extend_api_key(event["data"]["customer"]["email"], days=30)

    elif event["type"] == "subscription.canceled":
        # Don't revoke immediately - let it expire naturally
        pass
```

**Deliverable:** Automated key provisioning on payment

---

### Task 2.3.5: Create Setup Documentation

**Goal:** Make onboarding self-service

**Documentation pages:**

1. **Quick Start Guide**
   - Generate your first resume (3 steps, 10 minutes)
   - Claude Desktop MCP setup (5 steps with screenshots)
   - Test with first query

2. **Telegram Bot Guide**
   - How to start interview
   - Best practices (answer naturally, be specific about numbers)
   - How to check progress

3. **CV Generation Guide**
   - When CV is available (after 1-2 interview sessions)
   - How to generate (/generate_cv command)
   - How to download PDF

4. **Troubleshooting**
   - MCP not responding -> check config
   - Bot not responding -> check username
   - Data not appearing -> complete interview
   - Resume not ATS-friendly -> report issue

**Host on:**
- GitHub Pages (free)
- GitBook (free tier)
- Notion (free, easy to update)

**Deliverable:** Documentation site live

---

## Phase 2.4: Improve Materials (Week 3-4)

### Task 2.4.1: Create Use Case Examples

**Goal:** Show specific outcomes, not just features

**Use Case 1: Resume Generation (PRIMARY)**
```
Before: "I spent 3 hours updating my resume for each application.
        Kept forgetting projects and accomplishments."

After:  "Chatted with the bot for 12 minutes. Got a resume that's
         more detailed than anything I've written manually.
         ATS-friendly, ready to submit."

The difference:
  Manual: "Managed a development team"
  Interview Assistant: "Led 12-person engineering team that delivered
  $2M platform migration 3 weeks ahead of schedule, reducing
  infrastructure costs by 40%"
```

**Use Case 2: Cover Letters**
```
Before: "I spent 2 hours writing a cover letter,
        copying my resume, rephrasing everything."

After:  "Claude wrote my cover letter in 30 seconds
         using my real projects from Interview Assistant."
```

**Use Case 3: Interview Prep**
```
Before: "I forgot half my accomplishments in interviews."

After:  "Asked Claude 'What are my best achievements relevant to
         a senior engineering role?' Got 5 specific STAR-format
         examples I'd forgotten about."
```

**Deliverable:** 3-5 use case examples with screenshots

---

### Task 2.4.2: Get First Testimonials

**Ask early customers (after 2+ weeks of usage):**
```
Hi [name],

Quick request: Would you write 1-2 sentences about your
experience with Interview Assistant?

What helped most? What outcome did you get?

Example: "Generated a resume in 12 minutes that was better
than what I spent 5 hours writing manually. The follow-up
questions caught accomplishments I'd completely forgotten."

Can I share on the website? (First name + last initial only)

Thanks!
```

**Deliverable:** 3+ testimonials collected

---

### Task 2.4.3: Optional: Small Paid Ads Test

**If organic is working, test scaling:**

**Budget:** $50-100
**Channels:** Reddit ads targeting r/resumes, r/careerguidance (CV segment) + r/ClaudeAI (MCP segment)

**Ad Copy (CV focus):**
```
Headline: "AI Career Coach - Resume in 15 Minutes"

Body: "Talk naturally, get an ATS-optimized resume. AI interviews
you like a career coach. Free tier available."

[Demo Video thumbnail]

CTA: "Try It Free"
```

**Ad Copy (MCP focus):**
```
Headline: "Give Claude Structured Long-Term Memory"

Body: "Active interviews, not passive capture. Deeper knowledge
than Mem0. Works with Claude, ChatGPT, Cursor."

[Demo Video thumbnail]

CTA: "Try Early Access"
```

**Success Metric:**
- Cost per signup: <$5
- Cost per paying customer: <$50

**Deliverable:** Ad test results documented

---

## Stage 2 Success Criteria

**Check these boxes before moving to Stage 3:**

- [ ] **5+ paying customers** (credit card or crypto)
- [ ] **3+ active users** (using product after paying)
- [ ] **2+ testimonials** collected
- [ ] **Zero refunds** (or refund for legit reason, not quality)
- [ ] **Payment flow working** (Polar.sh automated or manual <2 hrs/week)
- [ ] **Support volume manageable** (<5 questions per week)
- [ ] **Clear which segment converts better** (CV vs MCP, from data)

**If you hit these: Stage 2 successful. Move to Stage 3.**

---

## Budget Breakdown

| Item | Cost | Required? |
|------|------|-----------|
| Domain name | $10-15/yr | Optional |
| Polar.sh fees | 4% + $0.40/tx | Yes (per sale) |
| Email service (ConvertKit) | $0 | Free tier |
| Documentation hosting | $0 | GitHub Pages free |
| Video recording (Loom) | $0 | Free tier |
| Reddit ads (optional) | $50-100 | No (test only) |
| **Total** | **$50-200** | |

---

## Timeline

**Week 1:**
- Days 1-3: Configure Polar.sh products + email templates
- Days 4-5: Send early access invitations
- Days 6-7: First payments arrive + onboard

**Week 2:**
- Days 1-3: Process payments, support first customers
- Days 4-7: Build admin commands + expiry logic + webhook handler

**Week 3:**
- Days 1-4: Create documentation
- Days 5-7: Improve materials (use cases, testimonials)

**Week 4:**
- Days 1-3: Optional ads test
- Days 4-7: Review results, decide Stage 3

**Total: 3-4 weeks to get first paying customers**

---

## Next Steps

If Stage 2 succeeds -> [Stage 3: Working Service](../stage-3-growth/PLAN.md)

If Stage 2 fails:
- **<3 paying customers:** Waitlist wasn't qualified (revisit Stage 1 messaging)
- **Payments but refunds:** Product not delivering value (fix core experience)
- **Free tier converts but paid doesn't:** Pricing issue (try lower price or different tier structure)
- **CV converts but MCP doesn't:** Double down on CV segment, deprioritize MCP marketing
