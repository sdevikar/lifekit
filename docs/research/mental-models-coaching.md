# Mental Models Coaching (Concept Pool Entry)

**Source:** Inspired by Peter Hollins's framework of cognitive decision-making tools.
**Phase:** Phase 0+ (Feature extension to current teaching methods)
**Type:** Teaching Method / Strategy Layer Extension

## The Core Idea
Current task generation asks the LLM to produce exercises shaped by standard learning strategies (Socratic, Feynman analogical, spaced). This feature introduces **cognitive lenses**: every exercise is framed through a specific Mental Model from Hollins's catalog, forcing the user not just to *consume* knowledge but to *decide* better using it.

## The Mental Models Catalog
1. **First Principles Thinking:** Strip away assumptions and rebuild logic from fundamental truths. Use when: feeling overwhelmed or stuck in "busy work."
   *Prompt Hook:* *"Deconstruct your goal into its most basic truths..."*
2. **Second-Order Thinking (Cause → Effect Chains):** Map cascading consequences of current actions 1 step, 2 steps, & N steps ahead. Use when: evaluating risky decisions or multi-step plans.
   *Prompt Hook:* *"What happens after you take action X? What about the step after that?"*
3. **Opportunity Cost Filtering:** Evaluate what is actively being sacrificed by investing time here. Use when: prioritizing, avoiding "productive procrastination."
   *Prompt Hook:* *"For every hour spent on Task A, what's the highest-value alternative you're declining?"*
4. **Circle of Competence Mapping:** Distinguish actual skill from false confidence. Expand boundaries only where necessary. Use when: scope clarity, avoiding misdirection.
   *Prompt Hook:* *"Is this challenge inside your Circle? If not, what's the smallest step to expand it before committing time?"*
5. **Inversion (Anti-Goals):** Map exactly how you would guarantee failure, then build anti-tactics against those outcomes. Use when: risk mitigation, uncovering blind spots.
   *Prompt Hook:* *"How would you guarantee failure? Now build defenses against those outcomes."*
6. **Hanlon's Razor / Contextual Detachment:** Separate incompetence/circumstance from malice or personal failure. Use when: emotional regulation during setbacks/plateaus.
   *Prompt Hook:* *"Could this obstacle be explained by circumstance rather than intent?"*

## Interview Tier 1 Integration
During onboarding, ask: 
*"Are your decisions guided by clear cognitive frameworks, or do you tend to react intuitively under stress?"*
- If "Frameworks" selected → default to `first_principles` + `inversion`.
- If "Intuitive/Stress" selected → default to `hanlons_razor` + `second_order_thinking` to build deliberate decision-making habits.

## Implementation Path
1. Add mental models to `/lifekit/plan_forge/forge_plan.py` as a parallel teaching strategy map.
2. Adjust prompt template construction to inject model-specific definitions + book excerpts.
3. Output schema accepts `exercise_type: "first_principles"` (etc.) as valid types.

## Risks / Caveats
- Hollins's framework targets *decision-making*, whereas current MVP focuses on *subject matter comprehension*. This pivots LifeKit slightly toward "coaching better judgments" vs "completing reading tasks."
- Prompt space usage: each model definition + book chapter excerpt increases token count. Requires context-window management in future phases.

---
*Drafted by Agent @ 2026-07-11T...*
