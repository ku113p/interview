# Stage 1 Validation - Execution Guide

**Goal:** Get 30-50 email signups in 7 days to validate demand for CV generation feature.

**Timeline:** 7 days (Mon-Sun) with deployment later

---

## Step 1: Set Up Email Capture (TODAY - 10 minutes)

### A. Create Formspree Form

1. Go to https://formspree.io/
2. Sign up with any email
3. Click "New Form"
4. Enter email: `digitalscyther@gmail.com`
5. Create the form
6. Copy your **Form ID** from the URL or dashboard
   - Example: If the action URL is `https://formspree.io/f/abc123de`, your ID is `abc123de`

### B. Add to Frontend

1. Create `frontend/.env.local`:
   ```bash
   PUBLIC_FORMSPREE_ID=your_form_id_here
   ```

2. Replace `your_form_id_here` with the ID from Formspree

3. Test locally:
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

4. Visit http://localhost:4321
5. Fill out the email form and submit
6. Check your email (digitalscyther@gmail.com) to confirm it works

---

## Step 2: Prepare Screenshots (TODAY - 15 minutes)

### What to Capture

You need 3 screenshots for the landing page:

1. **Interview Conversation** (Telegram or CLI demo)
   - Show 3-4 exchanges between AI and user
   - Show a real career question being answered
   - File: `frontend/public/screenshots/interview-demo.png`

2. **Knowledge Extraction**
   - Show the extracted skills, achievements, impact
   - File: `frontend/public/screenshots/extraction-demo.png`

3. **CV Output**
   - Show a generated resume/CV (PDF or screenshot)
   - File: `frontend/public/screenshots/cv-output-demo.png`

### Tools
- OS screenshot tool (built-in)
- For PDF: Use existing CV, or mock one in Google Docs
- Save to `frontend/public/screenshots/` or external URL

### Current Images Needed
Add these to `frontend/src/components/HowItWorks.astro` in the steps section:
```astro
<img src="/screenshots/interview-demo.png" alt="Interview conversation" />
<img src="/screenshots/extraction-demo.png" alt="AI extraction" />
<img src="/screenshots/cv-output-demo.png" alt="Generated CV" />
```

---

## Step 3: Deploy When Ready

### Option A: Free Vercel Deployment (Recommended)

```bash
cd frontend
pnpm install
pnpm build

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

This creates a live link like: `https://interview-assistant-[hash].vercel.app`

### Option B: Netlify Deployment

```bash
cd frontend
pnpm build

# Drop dist/ folder to netlify.com
```

### Option C: GitHub Pages (if you prefer)

Push to GitHub, enable Pages in repo settings.

---

## Step 4: Prepare Reddit Posts (DAY 1-2)

Copy these templates and schedule posts for **Tuesday-Thursday, 9-11am US Eastern**:

### Post 1: r/resumes

**Title:** I built a tool that interviews you about your career and writes your resume from the conversation

**Body:**
I've reviewed a lot of resumes (including my own, repeatedly) and the problem is always the same: you sit down to write, stare at the screen, and end up with generic bullet points that don't capture what you actually do.

So I built something different. Instead of filling in a template, an AI interviews you — asks about your roles, your projects, what you're proud of, what impact you made. Then it generates a structured CV from your answers.

The idea is that you're the expert on your career. You just need someone (or something) to ask the right questions.

It's free to try — one CV, no cost. If anyone wants to test it and give me feedback, I'd genuinely appreciate it.

**First comment (post immediately after):**
Link is here: `[YOUR_SITE_URL]?utm_source=reddit&utm_medium=post&utm_campaign=resumes`

Completely free for one CV. Would really love honest feedback — especially if you think the questions it asks are useful or if it misses important stuff.

---

### Post 2: r/careerguidance

**Title:** I spent years in my career and couldn't fit it on two pages. So I built an AI that interviews you and writes the resume for you.

**Body:**
Career changers especially — you know the pain. You've done a dozen different things, worn a hundred hats, but when it comes time to write a resume, you end up with something that looks like everyone else's.

I kept running into the same problem: templates force you into boxes. They don't capture *why* you made certain moves, or the depth of what you actually built.

So I made a tool where AI asks you questions — like a real conversation — about your experience. Then it generates a CV from your answers. It pulls out skills and achievements you wouldn't think to include because you're too close to your own story.

Sharing it here in case it helps anyone who's in the middle of a career transition or just dreading the "update my resume" task.

Happy to share the link if anyone's interested — just wanted to gauge if this is useful before I spam anything.

**First comment (post immediately after):**
Here's the link for anyone who wants to try it: `[YOUR_SITE_URL]?utm_source=reddit&utm_medium=post&utm_campaign=careerguidance`

Free for one CV. I built this because I was going through a career change myself and every template I tried made my experience look thinner than it actually was.

---

### Post 3: r/jobs

**Title:** Free tool: AI asks you about your career and generates your CV from the conversation (no template filling)

**Body:**
Quick share for anyone actively job hunting. I built a tool that takes a different approach to resume writing.

Instead of filling in a template, you have a conversation with an AI about your work experience. It asks follow-up questions, digs into your actual contributions, and then generates a structured CV.

Think of it like having a professional resume writer interview you, except it's free and you can do it at 2am in your pajamas.

One free CV, no account needed beyond an email. Would love feedback from anyone who tries it.

**First comment (post immediately after):**
Link: `[YOUR_SITE_URL]?utm_source=reddit&utm_medium=post&utm_campaign=jobs`

No catch — one free CV. I'm a solo dev building this and looking for early users to tell me what works and what doesn't.

---

## Step 5: Monitor & Track (Days 2-7)

### Create Google Sheet with these columns:
- Date
- Visitors (from Plausible Analytics)
- Free Signups (from Formspree)
- Top Source

### Daily Check (2 min):
1. Visit Plausible Analytics dashboard
2. Log visitor count and signups
3. Check Reddit comment replies (reply within 2 hours!)
4. Update spreadsheet

### Analytics Dashboard:
Plausible is already integrated. View at: `[your-site]/plausible`
(Or set up at https://plausible.io)

---

## Day 7: Decision Framework

| Metric | Green (Build) | Yellow (Iterate) | Red (Pivot) |
|--------|---------------|------------------|------------|
| **Visitors** | 200+ | 50-199 | <50 |
| **Email Signups** | 30+ | 10-29 | <10 |
| **High-Intent** | 5+ | 2-4 | 0-1 |

### Green = Ship It
- Start building CV generation feature
- Set up Polar.sh payments
- Onboard waitlist

### Yellow = Refine
- Rewrite landing page copy
- Try different Reddit communities
- Test again for 1 week

### Red = Pivot
- Either the market doesn't want this
- Or messaging is very wrong
- Consider MCP/AI memory value prop instead

---

## Checklist

### Before Day 1 Posts
- [ ] Formspree form created and ID added to `.env.local`
- [ ] Email form tested locally
- [ ] Screenshots prepared (or URLs ready)
- [ ] Landing page deployed (or test URL ready)
- [ ] UTM parameters verified in email form

### Days 1-2: Posting
- [ ] Post to r/resumes (Tue-Thu 9-11am ET)
- [ ] Reply to all comments within 2 hours
- [ ] Post to r/careerguidance (Tue-Thu 9-11am ET)
- [ ] Reply to all comments
- [ ] Post to r/jobs (Tue-Thu 9-11am ET)
- [ ] Reply to all comments

### Days 2-7: Monitoring
- [ ] Check analytics daily (2 min)
- [ ] Log signups in spreadsheet
- [ ] Reply to Reddit comments ASAP
- [ ] Track referral sources

### Day 7: Review
- [ ] Count total visitors
- [ ] Count total signups
- [ ] Calculate conversion rate
- [ ] Review comments for feedback
- [ ] Make decision (Green/Yellow/Red)
- [ ] Document learnings

---

## Quick Reference: Your Site URL

Replace `[YOUR_SITE_URL]` in Reddit posts with your deployed landing page URL.

**Examples:**
- Vercel: `https://interview-assistant-abc123.vercel.app`
- Netlify: `https://interview-assistant.netlify.app`
- Custom: `https://interviewassistant.ai`

**With UTM tags:**
```
https://your-site.com?utm_source=reddit&utm_medium=post&utm_campaign=resumes
```

---

## Notes

- Keep it real: You're a solo dev validating an idea
- Reply to every comment — this is crucial for learning
- Don't oversell — be honest about the free tier limitations
- After Day 7, review learnings and decide next move
- Save all feedback comments — they're gold for iteration

Good luck! 🚀
