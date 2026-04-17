---
name: good-marketing-skill
description: A comprehensive digital marketing analytics skill that guides proper attribution modeling, customer analytics, and campaign measurement with privacy compliance.
version: "1.0.0"
domain: digital-marketing
author: Test Author
triggers:
  - "marketing attribution"
  - "campaign measurement"
  - "customer lifetime value"
  - "marketing ROI"
use_for:
  - "Setting up marketing attribution models"
  - "Calculating customer lifetime value"
  - "Measuring campaign effectiveness"
  - "SEO and SEM strategy"
do_not_use_for:
  - "General A/B testing methodology (use experiment-design)"
  - "Statistical hypothesis testing (use statistics)"
compatibility:
  - claude-code
  - gemini-cli
  - cursor
---

# Digital Marketing Analytics Guide

## Overview

This skill guides the agent through proper digital marketing measurement,
attribution modeling, customer analytics, and campaign optimization. It covers
the full customer journey from awareness through retention, ensuring
methodologically sound measurement and privacy-compliant data practices.

## When to Use

Use this skill when the user wants to:
- Set up or evaluate marketing attribution models
- Calculate and predict customer lifetime value (CLV/LTV)
- Measure campaign ROI/ROAS with incrementality testing
- Optimize SEO/SEM strategy with proper keyword research
- Design email marketing campaigns with deliverability best practices

## Decision Tree

```
IF measuring marketing channel effectiveness:
  IF the goal is real-time campaign optimization:
    → Use multi-touch attribution (MTA) with model awareness
    → WARN: No single attribution model is "correct" — always report
      multiple models (last-click, linear, time-decay, data-driven)
    → Acknowledge model bias: last-click overvalues bottom-funnel,
      first-click overvalues top-funnel
  ELIF the goal is strategic budget allocation:
    → Use Marketing Mix Modeling (MMM) with adstock/carryover effects
    → Model diminishing returns via Hill functions or log transforms
    → Account for cross-channel synergy and interaction effects
  ELIF the goal is causal impact measurement:
    → Use incrementality testing (geo experiments, holdout groups)
    → This is the gold standard for establishing causal lift

IF calculating customer value:
  IF contractual business (subscription, SaaS):
    → Use survival models with discount rate and time horizon
    → Define churn operationally (cancellation, non-renewal)
  ELIF non-contractual business (e-commerce, retail):
    → Use probabilistic models (BG/NBD for frequency, Gamma-Gamma
      for monetary value)
    → Define inactivity window threshold with justification
    → Account for recency, frequency, and monetary value (RFM)

IF optimizing search:
  IF organic search (SEO):
    → Ensure technical SEO fundamentals (crawlability, indexation,
      Core Web Vitals — LCP, CLS, INP)
    → Address E-E-A-T (Experience, Expertise, Authoritativeness,
      Trustworthiness) and topical authority
    → Keyword research: balance search volume with user intent
      (informational, transactional, navigational) and difficulty
  ELIF paid search (SEM/PPC):
    → Evaluate bidding strategies: manual CPC vs. tCPA vs. tROAS
    → Consider quality score optimization alongside bid management
    → Track cost per click (CPC) and ROAS as primary efficiency metrics
```

## Guardrails

- **REFUSE** to recommend last-click attribution as the correct or only model.
  Always present model assumptions and limitations.
- **REFUSE** to calculate CLV as simply "average revenue × average lifespan"
  without specifying a probabilistic or contractual model framework.
- **WARN** if marketing KPIs are vanity metrics (followers, likes, impressions)
  not tied to business outcomes (revenue, profit, LTV). Marketing measurement
  should ladder up to north star metrics with clear alignment to business OKRs.
- **WARN** if tracking is discussed without addressing privacy compliance
  (GDPR, CCPA, iOS ATT, cookieless measurement). First-party data strategy
  and consent management are non-negotiable.
- **MUST NOT** recommend purchasing email lists. Always require opt-in consent
  and proper list hygiene (bounce removal, suppression lists, re-engagement
  campaigns for inactive subscribers).
- **MUST NOT** ignore deliverability — SPF, DKIM, and DMARC authentication
  are table stakes for email marketing.

## Attribution Model Comparison

| Model | Bias | Best For |
|-------|------|----------|
| Last-click | Overvalues bottom-funnel (branded search) | Quick directional signal |
| First-click | Overvalues top-funnel (display, social) | Awareness campaign eval |
| Linear | Dilutes across all touchpoints | Even-handed but naive |
| Time-decay | Overweights recent touches | Conversion-focused |
| Data-driven | Requires significant data volume | Best available observational model |
| Incrementality | Gold standard — causal | Strategic decisions |

## Privacy & Compliance

All digital marketing measurement must account for:
- **GDPR** (EU) and **CCPA/CPRA** (California) consent requirements
- **iOS 14+ ATT** framework limiting IDFA availability
- The shift from third-party cookies to first-party data strategies
- Server-side tracking (Conversion API / CAPI) as complement to pixel-based
- Cookie consent banners and their impact on data completeness
- Privacy Sandbox proposals (Topics API, Attribution Reporting API)

## Tracking Infrastructure

- Use **UTM parameters** consistently for campaign attribution
- Implement **tag management** (Google Tag Manager) for governance
- Consider **server-side tracking** for reliability and privacy compliance
- Set up proper **conversion tracking** with defined conversion windows
- Use **event-based measurement** (GA4 paradigm) over pageview-based

## Ad Tech & Programmatic

When working with programmatic advertising:
- Understand auction mechanics: first-price auctions require bid shading
- Set **frequency caps** to prevent ad fatigue and wasted spend
- Monitor **viewability** (MRC standard: 50% pixels, 1+ second) and
  **invalid traffic** (IVT) to ensure ad verification
- Evaluate **brand safety** controls alongside performance metrics

## Email Marketing Best Practices

- Prioritize **deliverability**: authenticate with SPF, DKIM, DMARC
- Practice **list hygiene**: remove hard bounces, re-engage or sunset
  inactive subscribers, honor unsubscribes promptly
- **Personalization** should use behavioral signals (purchase history,
  browsing behavior, engagement patterns, lifecycle stage) — not just
  dynamic name insertion
- Segment by engagement level, lifecycle stage, and purchase behavior

## Content & SEO Strategy

- Build **topical authority** through pillar-cluster content architecture
- Focus on **E-E-A-T** signals: demonstrate real experience, expertise,
  authoritativeness, and trustworthiness
- Prioritize **user experience** and helpful content over keyword density
- Address **Core Web Vitals**: LCP, CLS, INP for page experience

## Customer Analytics

- **Segmentation**: Use data-driven methods (RFM scoring, k-means clustering
  with silhouette validation) rather than arbitrary thresholds
- **Cohort analysis**: Normalize by initial cohort size and control for
  seasonality effects across time periods
- **Churn modeling**: Define churn criteria operationally; use recency-based
  thresholds for non-contractual settings

## Edge Cases

- **Small advertisers**: May not have enough conversion volume for
  data-driven attribution — fall back to rules-based with caveats
- **Cross-device journeys**: Acknowledge deterministic matching gaps;
  probabilistic identity graphs are incomplete
- **Offline conversions**: Store visits, phone calls require modeling
  or direct integration (store visit conversions, call tracking)
- **View-through attribution**: High inflation risk in cookieless
  environments — require incrementality validation

## Escape Hatch

Experienced marketers can override guardrails by explicitly stating:
"I acknowledge [specific guardrail] and am proceeding because [justification]."

## References

For detailed methodology guides, see the `references/` directory.
