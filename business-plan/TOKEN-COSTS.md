# Token Cost Analysis

**Last Updated:** 2026-02-25
**Data Source:** Production database analysis (user 53e58366-155e-5f8b-9fef-cffb977e8ec8)

## Executive Summary

**Cost per complete CV interview session: $0.19**

This analysis validates our pricing model assumptions and confirms that monthly subscriptions ($19-29/mo) are highly profitable (97%+ margins), while lifetime unlimited plans pose significant risk from high-volume users.

---

## Real User Data

### User Activity Profile
```
Total Messages:          202 (101 conversation turns)
Root Areas:              1
Sub-areas:               71 (hierarchical decomposition)
Leaf Areas:              57 (actual interview locations)
Interview Summaries:     58 (conversation turns in leaf interviews)
Skills Extracted:        155
Facts Extracted:         62
Total Knowledge Items:   217
```

**Interpretation:** This represents a thorough, multi-topic CV interview session. The user explored 57 different areas of expertise/experience with focused Q&A in each area.

---

## Cost Breakdown by Operation

| Operation | Count | Cost per Unit | Total Cost | % of Total |
|-----------|-------|---------------|------------|------------|
| **Interview Turns** (leaf areas) | 58 | $0.001225 | $0.071 | 37% |
| **Knowledge Extraction** | 58 | $0.000727 | $0.042 | 22% |
| **Area Creation & Management** | ~15 | $0.002 | $0.030 | 16% |
| **Intent Classification** | 101 | $0.000225 | $0.023 | 12% |
| **Area Navigation & Small Talk** | ~43 | $0.0006 | $0.026 | 13% |
| | | | | |
| **TOTAL** | | | **$0.192** | **100%** |

### Cost by Category

**Interview Flow (59%):** $0.113
- Core Q&A exchanges in leaf areas
- Dominant cost driver (60% of spend)
- Already optimized (reduced from $1.50+ in old architecture)

**Knowledge Extraction (22%):** $0.042
- Background processing of summaries
- Extracts skills/facts for AI memory
- Runs asynchronously (no user-facing latency)

**Infrastructure (19%):** $0.037
- Area creation/navigation
- Intent classification
- Small talk handling

---

## Model Pricing (via OpenRouter)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Usage |
|-------|----------------------|------------------------|-------|
| **gpt-5.1-codex-mini** | $0.25 | $2.00 | Interview, extraction, area management |
| **gpt-5.2** | $1.75 | $14.00 | Not used (7-8x more expensive) |
| **gemini-2.5-flash-lite** | $0.10 | $0.40 | Audio transcription (40x cheaper) |
| **text-embedding-3-small** | $0.02 | N/A | Vector embeddings (negligible cost) |

**Key optimization:** Using GPT-5.1-codex-mini instead of GPT-5.2 reduces costs by 87%.

---

## Cost Scenarios

| Scenario | Turns | Areas | Cost |
|----------|-------|-------|------|
| **Minimal CV** | 45 | 30 | $0.095 |
| **Typical CV** (actual) | 58 | 72 | $0.192 |
| **Maximum CV** | 300 | 150 | $0.598 |

**Typical range:** $0.18 - $0.25 per complete CV session

---

## Pricing Model Validation

### Margin Analysis

| Price Point | Token Cost | Gross Margin | Margin % | Break-even Volume |
|-------------|-----------|--------------|----------|-------------------|
| **Free (1 CV trial)** | $0.19 | -$0.19 | -100% | N/A (CAC) |
| **$12 per CV** | $0.19 | $11.81 | **98.4%** | 1 CV |
| **$19/mo (3 CVs)** | $0.57 | $18.43 | **97.0%** | 1 month |
| **$29/mo (5 CVs)** | $0.95 | $28.05 | **96.7%** | 1 month |
| **$79 lifetime (unlimited)** | $0.19 × N | ❌ | Degrades | **411 CVs** |

### Lifetime Unlimited Risk Analysis

**$79 lifetime unlimited = High risk**

| User Type | Usage Pattern | Break-even Point | Outcome |
|-----------|---------------|------------------|---------|
| Casual job seeker | 2-3 CVs over lifetime | Never breaks even | ✅ Profitable |
| Active job seeker | 10 CVs over 2 years | Never breaks even | ✅ Profitable |
| Career coach | 5 CVs/month | 16 months | ⚠️ Marginal |
| Recruiter | 10 CVs/week | **10 months** | ❌ Unprofitable |
| Consulting firm | 50 CVs/week | **2 months** | ❌ Major loss |

**Conclusion:** Lifetime unlimited works only if you can prevent high-volume users from signing up. Not realistic for B2B use cases.

---

## Cost Optimization Opportunities

| Optimization | Potential Savings | Implementation Complexity | Recommended |
|--------------|-------------------|---------------------------|-------------|
| Cache area structures | 5-10% | Low | ✅ Yes |
| Batch knowledge extraction | 10-15% | Medium | ✅ Yes |
| Cheaper model for intent classification | 5-8% | Low | ⚠️ Maybe |
| Reduce follow-up questions | 20-30% | High | ❌ No (hurts quality) |

**Realistic savings:** 15-20% → brings cost to **$0.16-0.17 per CV**

**Not recommended:** Reducing interview depth or question quality. The thoroughness is the product differentiator.

---

## Competitor Cost Comparison

| Competitor | Pricing | Estimated Token Cost | Margin |
|------------|---------|---------------------|--------|
| **Teal** | $29/mo unlimited | ~$0.05 per CV (template-based, minimal AI) | 99.8% |
| **Rezi** | $29/mo unlimited | ~$0.10 per CV (AI-assisted, not interview-based) | 99.7% |
| **ChatGPT Plus** | $20/mo unlimited | User pays directly | N/A |
| **Interview Assistant** | TBD | $0.19 per CV (deep interview) | 97-99% |

**Our positioning:** Higher cost per CV (deeper interviews) but still 97%+ margins at $19-29/mo with usage limits.

---

## Recommended Pricing Models

### ✅ Option 1: Monthly Subscription (Recommended)
```
Free: 1 CV trial ($0.19 CAC)
Pro: $19/mo - 3 CVs + AI memory ($0.57 cost, 97% margin)
Business: $49/mo - 15 CVs + team features ($2.85 cost, 94% margin)
Extra CVs: $8 each
```

**Pros:** Predictable revenue, aligns with job search patterns, limits exposure
**Cons:** Monthly churn, requires retention strategy

### ✅ Option 2: Pay-Per-CV
```
Free: 1 CV trial
$12 per CV (98.4% margin)
$30 for 3 CVs ($10 each, 98.3% margin)
$79 for 10 CVs ($7.90 each, 97.7% margin)
```

**Pros:** No subscription friction, scales with value
**Cons:** Higher friction per purchase, no recurring revenue

### ✅ Option 3: Capped Lifetime
```
$79 Lifetime Access:
- 12 CVs per year (resets annually)
- Additional CVs: $8 each
- AI memory features included

10-year cost: $21.60 in tokens
Margin: $57.40 (73% over 10 years)
```

**Pros:** "Lifetime" appeal, usage caps protect margins
**Cons:** Complex to explain, requires usage tracking

### ❌ Option 4: Unlimited Lifetime
```
$79 lifetime unlimited
Break-even: 411 CVs
Risk: High-volume users destroy economics
```

**Verdict:** Do not offer unless you can restrict B2B/high-volume use cases

---

## Validation Stage Pricing (Stage 1)

**For landing page / early adopters:**

```
🆓 Free Trial: 1 CV (no credit card)
   → Cost: $0.19 (acceptable CAC for validation)

🎯 Primary Offer: $19/mo CV Pro
   → 3 CVs per month + AI memory
   → Cost: $0.57/mo, Margin: $18.43 (97%)

🎁 Early Bird: $15/mo (first 50 customers)
   → Creates urgency
   → Cost: $0.57/mo, Margin: $14.43 (96%)

💎 One-Time: $12 per CV
   → No subscription commitment
   → Margin: $11.81 (98.4%)
```

**Why this works:**
- Lower risk than competitors (Teal/Rezi at $29/mo)
- Early bird drives FOMO for Stage 1 validation
- Free trial CAC ($0.19) is acceptable
- Can test both subscription and one-time models

---

## Action Items

1. ✅ **Validated:** Token costs match estimates ($0.18-0.20 per CV)
2. ⏳ **Update:** business-plan/stage-1-validation/02-payment-options.md with validated pricing
3. ⏳ **Update:** business-plan/stage-1-validation/03-landing-page-copy.md with new offers
4. ⏳ **Implement:** Usage tracking in backend (cv_count per user per month)
5. ⏳ **Set up:** Polar.sh with $19/mo subscription + $12 one-time option
6. ⏳ **Monitor:** Actual costs in production (log token usage per session)

---

## Sources

- OpenRouter pricing: https://openrouter.ai/pricing
- Production database: interview.db (274 users, analyzed user 53e58366-155e-5f8b-9fef-cffb977e8ec8)
- Code analysis: backend/src/processes/interview/, backend/src/config/settings.py
- LLM configuration: backend/LLM_MANIFEST.md

---

## Notes

**Why our costs are low:**
1. Smart model selection (GPT-5.1-codex-mini, not GPT-5.2) = 87% savings
2. Optimized architecture (1,700 tokens/turn vs 8,000+ old system) = 90% savings
3. Cheap embeddings (text-embedding-3-small) = negligible cost
4. Gemini for audio (40x cheaper than Whisper)

**Why lifetime unlimited is risky:**
- Consulting firms, recruiters, and career coaches are high-volume users
- 10-50 CVs/week would result in net losses within months
- Can't realistically restrict these users without alienating market
- Better to charge monthly with volume limits or per-CV pricing

**Why monthly subscriptions work:**
- Job seekers are active for 2-4 months typically
- 3 CVs/month covers: initial CV + 2 iterations
- $19/mo feels reasonable vs competitors ($29/mo for Teal/Rezi)
- Unused CVs expiring monthly limits exposure to token costs
