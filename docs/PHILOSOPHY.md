# Design Philosophy

## Core Principles

### 1. Opinionated Over Generic

These skills take strong positions on statistical practice. They don't present
all options equally — they recommend best practices and warn against common errors.

**Example**: The `experiment-designer` skill REFUSES to approve an experiment
with power < 80%. It doesn't just "suggest" adequate power — it enforces it.

### 2. Decision Trees Over Free-Form

Every skill includes explicit if/then routing. The agent doesn't have to figure
out which method to use — the decision tree specifies it based on the user's
answers to structured questions.

**Why**: LLMs are notoriously bad at method selection in statistics. They pick
methods based on keyword matching ("you mentioned groups, so use ANOVA") rather
than understanding the data structure and assumptions.

### 3. Guardrails Over Suggestions

Critical checks are mandatory, not optional. The agent will WARN or REFUSE when:
- Statistical assumptions are violated
- Power is inadequate
- Causal claims lack identification
- Multiple comparisons are uncorrected

**Escape hatch**: Experienced users can override guardrails with explicit acknowledgment.

### 4. Progressive Disclosure

Skills load only what's needed:
- Frontmatter for discovery (name + description)
- SKILL.md body for activation (core workflow)
- Reference docs for deep dives (method-specific guides)

This respects the agent's context window budget.

### 5. Reproducibility by Default

Every analysis guided by these skills produces:
- Documented assumptions and decisions
- Pre-specified analysis plans
- Structured outputs with all statistics reported
- Seed sensitivity checks (for ML analyses)

### 6. Cross-Platform by Design

Skills use vendor-neutral paths, standard Markdown, and no platform-specific features.
They work equally well in Claude Code, Gemini CLI, Cursor, and any SKILL.md-compatible agent.

## What These Skills Are NOT

- **Not a statistics textbook**: They guide workflow and enforce rigor, not teach from scratch
- **Not automated analysis**: They guide the AGENT to do the right thing, not replace the data scientist
- **Not infallible**: Statistical judgment requires human oversight. These skills improve the baseline.

## Intellectual Heritage

These skills are informed by:
- The causal inference revolution (Pearl, Rubin, Angrist, Imbens)
- Modern experimentation platforms (Spotify, Netflix, Airbnb, Booking.com)
- Reproducibility crisis literature (Ioannidis, Gelman, Wasserstein)
- Recent research on seed instability in deep learning evaluation
