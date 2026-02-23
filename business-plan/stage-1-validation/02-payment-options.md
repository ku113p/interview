# Payment Options Guide

**Context:** You want to accept payments but have no business entity, VAT number, or company registration.
**Old assumption:** "Traditional payment processors require business verification" -- THIS IS WRONG.
**Reality (verified Feb 2026):** Multiple platforms accept individuals. Crypto-only is unnecessary.

---

## TLDR: Recommended Payment Stack

| Method | Use For | Fee | Setup Time |
|--------|---------|-----|------------|
| **Polar.sh** (primary) | Credit cards, subscriptions, one-time purchases | 4% + $0.40 | 30 min |
| **USDC on Base** (privacy option) | Crypto-paying customers | ~$0.01 gas | 30 min |
| **NOWPayments** (automated crypto) | Scale crypto if demand exists | 0.5% | 15 min |

**Start with Polar.sh. Add crypto only if customers ask for it.**

---

## Option 1: Polar.sh (RECOMMENDED - Primary Payment)

### Overview
Open-source, developer-centric billing platform. Acts as **Merchant of Record** (MoR) -- handles global tax compliance, chargebacks, and payment processing on your behalf.

### Why This Is Best For You
- **No business entity required** - designed for indie developers
- **Handles tax compliance** globally (you don't worry about VAT/GST)
- **Credit cards, Apple Pay, Google Pay** - what 95% of customers prefer
- **Subscriptions + one-time purchases** - supports both monthly and lifetime tiers
- **Cheapest MoR option** at 4% + $0.40 per transaction
- **Developer-friendly** - good API, clean dashboard

### Pricing
- 4% + $0.40 per transaction
- No monthly fees
- No setup costs

### What You Can Sell
- Monthly subscriptions ($12/mo, $29/mo, $59/mo)
- Lifetime purchases ($79 one-time)
- Usage-based billing (if needed later)

### Setup Steps
1. Go to polar.sh and create account
2. Connect via Stripe Connect (Polar uses Stripe under the hood)
3. Create your products/tiers
4. Get payment links or embed checkout widget
5. Polar handles: payment processing, tax calculation, receipts, refunds

### How Payment Works
```
1. Customer clicks "Subscribe" on your landing page
2. Polar checkout opens (hosted page or embedded widget)
3. Customer pays with credit card / Apple Pay / Google Pay
4. Polar collects payment, handles tax, sends receipt
5. You receive webhook: "payment succeeded"
6. Your system creates API key automatically (or you do manually for MVP)
7. Money deposited to your bank account (minus 4% + $0.40)
```

**Website:** https://polar.sh

---

## Option 2: Lemon Squeezy (Alternative MoR)

### Overview
Acquired by Stripe in 2024. Full Merchant of Record. Transitioning to "Stripe Managed Payments."

### Why Consider
- **No business entity required**
- **35+ countries** supported for sellers
- **Well-known brand** among indie developers
- **Stripe ecosystem** integration

### Pricing
- 5% + $0.50 per transaction (slightly more expensive than Polar)
- No monthly fees

### When to Choose Over Polar
- If you prefer Stripe's ecosystem
- If Polar has issues in your country
- If you want the upcoming "Stripe Managed Payments" features

**Website:** https://lemonsqueezy.com

---

## Option 3: Stripe Direct (If You're in the US)

### Overview
Stripe accepts individuals as sole proprietors. You need a SSN (no EIN required) and a personal bank account.

### Pros
- Lowest fees (2.9% + $0.30)
- Full control over checkout experience
- Most payment methods (cards, wallets, bank transfers)
- Crypto payments via Stripe + Crypto.com integration (launched Jan 2026)

### Cons
- **No MoR** - you handle tax compliance yourself
- Need to build checkout integration (or use Stripe Payment Links for no-code)
- Must file taxes correctly for all jurisdictions

### When to Choose
- You're in the US and comfortable with tax filing
- You want lowest possible fees
- You want both crypto AND card payments in one platform

**Website:** https://stripe.com

---

## Option 4: USDC on Base (Privacy Option)

### Overview
For privacy-conscious customers who prefer crypto. Accept USDC stablecoin on Coinbase's Base L2 network.

### Why Base Network
- Gas fees: **$0.001 - $0.01** per transaction (essentially free)
- Fast: 2-second confirmations
- Widely supported: Coinbase Wallet, MetaMask, etc.
- Free USDC withdrawals from Coinbase exchange to Base

### Setup Steps
1. Install Coinbase Wallet or MetaMask
2. Write down 12-word recovery phrase (CRITICAL - store physically!)
3. Get your Base wallet address
4. Add to landing page as "Pay with crypto" option
5. Customer sends USDC, emails you tx hash
6. You verify on basescan.org, create API key manually

### Payment Instructions for Customers
```
Pay with Crypto (Privacy Option):

1. Send $12 USDC on Base network to: 0xYourAddressHere
2. Email transaction hash to: payment@yourdomain.com
3. Include your email and Telegram username
4. We'll activate your account within 24 hours

Important: Use Base network only. Wrong network = lost funds.
Need USDC? Buy on Coinbase, send to our address on Base (free transfer).
```

### When to Offer
- As secondary option alongside credit cards
- For privacy-focused marketing in r/privacy, r/selfhosted
- For international customers without credit card access

---

## Option 5: NOWPayments (Automated Crypto Gateway)

### Overview
If crypto demand is significant (10+ customers asking), automate with NOWPayments.

### Why
- **Individual accounts explicitly supported** - select "I'm an individual" at signup
- 350+ cryptocurrencies accepted
- 0.5% fee
- Payment links, invoices, API
- Forbes Advisor rated #1 Crypto Payment Gateway 2025

### Setup
1. Sign up at nowpayments.io (select individual)
2. No KYC required for basic tier
3. Create payment links or use API
4. Auto-withdrawal to your wallet

### When to Use
- When manual USDC verification becomes burdensome (20+ crypto customers)
- When you want professional checkout experience for crypto

**Website:** https://nowpayments.io

---

## Option 6: Ko-fi / Buy Me a Coffee (Tip Jar / Early Validation)

### Overview
Zero-friction way to accept tips and small payments during validation phase.

### Ko-fi
- **0% fee** on donations (free tier)
- 5% on memberships and shop sales
- PayPal, Cards, Apple Pay, Google Pay, Venmo, CashApp
- No business entity required

### Buy Me a Coffee
- 5% of every sale/donation/membership
- Backed by Y Combinator + Stripe
- Cards only (no PayPal)
- No business entity required

### When to Use
- During Stage 1 validation ("buy me a coffee if you find this useful")
- As a low-commitment way to gauge willingness to pay
- Before setting up proper subscriptions

---

## Pricing Tiers (Updated)

Based on market research (Feb 2026):

| Tier | Monthly | Lifetime | What's Included |
|------|---------|----------|----------------|
| **Free** | $0 | - | 1 interview + 1 CV generation (hook) |
| **CV Pro** | $12/mo | $79 | Unlimited interviews + CV generations, PDF export |
| **Knowledge** | $29/mo | - | CV Pro + MCP server access, semantic search |
| **Self-Hosted** | $59/mo | - | Everything + Docker deployment, priority support |

**Why these prices:**
- $12/mo is in the sweet spot ($5-30 range for resume tools)
- $79 lifetime captures job seekers (typically need it for 2-3 months during search)
- MCP access is subscription-only (recurring value justifies recurring payment)
- Free tier prevents "pay to download" backlash (common complaint about competitors)

---

## Comparison: All Payment Options

| Platform | Fee | Business Entity? | MoR? | Cards? | Crypto? | Best For |
|----------|-----|-----------------|------|--------|---------|----------|
| Polar.sh | 4% + $0.40 | No | Yes | Yes | No | Primary payments |
| Lemon Squeezy | 5% + $0.50 | No | Yes | Yes | No | Stripe ecosystem |
| Stripe Direct | 2.9% + $0.30 | No (US) | No | Yes | Yes (new) | Lowest fees, US sellers |
| USDC on Base | ~$0.01 gas | No | No | No | Yes | Privacy customers |
| NOWPayments | 0.5% | No | No | No | Yes | Automated crypto |
| Ko-fi | 0-5% | No | No | Yes | No | Tips/validation |

---

## Implementation Plan

### Stage 1 (Validation - Now)
1. **Ko-fi or Buy Me a Coffee** - add "support this project" link
2. **USDC wallet** - set up for crypto-first communities (r/privacy, r/selfhosted)
3. **Don't build payment integration yet** - validate demand first

### Stage 2 (First Customers)
1. **Polar.sh** - set up products and subscriptions
2. **USDC manual** - keep as privacy option
3. **Webhook integration** - auto-create API keys on Polar payment

### Stage 3 (Scaling)
1. **NOWPayments** - if crypto demand justifies automation
2. **Stripe Direct** - if you want lower fees and handle tax yourself
3. **Price optimization** - A/B test pricing based on conversion data

---

## Tax Considerations

### With Polar.sh/Lemon Squeezy (MoR)
- **They handle sales tax/VAT** for you globally
- You still need to report income on your personal taxes
- Keep records of all payouts received

### With Direct Payments (Stripe, USDC)
- **You are responsible** for tax compliance
- Track all income (date, amount, customer)
- Consult local tax advisor when revenue exceeds $5K total
- Consider forming entity when revenue exceeds $2K/month

### Crypto-Specific
- Track USD value at time of receipt (for tax purposes)
- Use CoinTracker or Koinly for automated crypto tax reporting
- Stablecoins (USDC) make accounting easier (1 USDC = $1 always)

---

## Security Best Practices

### For Crypto Wallet
- Use strong password (16+ characters)
- Enable 2FA (Google Authenticator, not SMS)
- Write down recovery phrase on paper (store physically, not digitally)
- Never share private key or seed phrase
- Test with small amount first ($1 transaction)
- Move to hardware wallet (Ledger/Trezor) if holding >$5K

### For Polar.sh/Stripe
- Enable 2FA on account
- Use strong unique password
- Monitor for unauthorized transactions
- Set up payout notifications

---

## Quick Decision Guide

**"I just want to validate demand"**
-> Use Ko-fi / Buy Me a Coffee (zero setup, free)

**"I have my first paying customers"**
-> Set up Polar.sh (30 min, credit cards + subscriptions)

**"Some customers want crypto"**
-> Add USDC on Base address to payment page (privacy option)

**"I have 20+ crypto customers"**
-> Add NOWPayments for automated crypto processing

**"I'm making $2K+/month"**
-> Consider Stripe Direct (lower fees) or forming business entity

---

**Version:** 2.0 (major rewrite - removed crypto-only constraint)
**Last Updated:** 2026-02-24
**Status:** Ready to implement
