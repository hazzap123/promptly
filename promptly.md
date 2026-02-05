---
name: promptly
description: Distill messy exploration into reusable prompts, or match current prompt against library
argument-hint: "[distill|match]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Three modes:
1. **Distill** (default): Analyze current conversation, synthesize a refined reusable prompt, add to library
2. **Match**: Check a prompt against the library and surface similar entries
3. **Proactive** (auto-triggered): When detecting exploratory patterns mid-conversation, offer to capture

Purpose: Turn multi-step exploratory conversations into single-shot reusable prompts. Build up a personal prompt library over time.

Output: Either a new library entry (distill), matched suggestions (match), or proactive offer to help
</objective>

<context>
Mode: $ARGUMENTS (defaults to "distill" if not specified)

**Prompt library location:** @00-system/prompt-library.yaml

**User context sources** (read to inform prompt style):
- `@CLAUDE.md` — User profile, communication preferences, key frameworks
- `@00-system/user-profile.yaml` — Strategic pillars, thinking patterns, preferences
</context>

<user_context_integration>
When distilling prompts, incorporate the user's known preferences:

1. **Read user context first:**
   - Check CLAUDE.md for communication style (directness, formality)
   - Check user-profile.yaml for frameworks they use (portfolio framework, impact assessment, etc.)
   - Note their role context (CPO, product leader, strategic thinker)

2. **Adapt the distilled prompt to match:**
   - Use their preferred framing and vocabulary
   - Structure outputs using frameworks they know
   - Match their communication style (direct, no fluff, commercially-minded)
   - Include their standard evaluation criteria where relevant

3. **Example adaptation:**
   - Generic: "Analyze the market opportunity"
   - Harry-adapted: "Analyze market using TAM/SAM/SOM. Include capital allocation implications and where this fits in Explore/Scale/Optimize/Retire portfolio framework."
</user_context_integration>

<proactive_detection>
## When to Offer Help (Proactive Mode)

**Trigger signals** — offer to capture when you notice:
- 3+ clarification rounds on the same topic
- User iterating on output format ("try it as a table", "add X section")
- Explicit pivots ("actually, what I really want is...")
- Successful output after extended exploration
- User expressing satisfaction after iteration ("yes, that's it")

**How to interject:**
```
---
This looks like a prompt pattern worth capturing. Want me to distill it for reuse?

What I noticed:
- Initial ask: [what they started with]
- Key refinements: [what changed]
- Final form: [what worked]

[Yes, capture it] [No, just continue]
---
```

**When NOT to interject:**
- Executing a predefined plan (like this consolidation task)
- Simple Q&A exchanges
- Debugging or troubleshooting sessions
- When user is clearly in a hurry or frustrated
</proactive_detection>

<process>
## Mode: Distill (default)

### Phase 0: Load User Context

0. **Read user preferences:**
   - Read `CLAUDE.md` for communication style, role context, key frameworks
   - Read `00-system/user-profile.yaml` for strategic pillars and preferences
   - Note: direct communication, commercially-minded, uses Thor Mitchell framework, portfolio thinking
   - These inform how the distilled prompt should be written

### Phase 1: Analyze the Journey

1. **Review the conversation:**
   - What was the user trying to accomplish?
   - What was the initial (messy) prompt?
   - What clarifications, iterations, or pivots happened?
   - What made the final output successful?

2. **Extract the pattern:**
   - Core intent (what they were really asking for)
   - Key constraints or requirements that emerged
   - Output format that worked
   - Any domain-specific framing that helped
   - **Which user frameworks or vocabulary appeared?**

### Phase 2: Synthesize the Prompt

3. **Draft the refined prompt:**
   - Clear, single-shot prompt that achieves the same outcome
   - Include placeholders for variable parts: `[TOPIC]`, `[CONTEXT]`, etc.
   - Preserve the structure/format that worked
   - Remove the exploration noise
   - **Match user's communication style** (direct, no fluff)
   - **Incorporate their frameworks** where relevant (portfolio, impact assessment, etc.)

4. **Identify triggers:**
   - What phrases would indicate someone wants this prompt?
   - Common ways to ask for this type of analysis
   - Keywords that should match
   - **Include vocabulary the user actually uses**

### Phase 3: Add to Library

5. **Present the distilled prompt:**
   - Show the refined prompt
   - Show suggested triggers
   - Ask: "Does this capture the essence? Any adjustments?"

6. **Write to library:**
   - Read current `00-system/prompt-library.yaml`
   - Generate a short, descriptive ID (kebab-case)
   - Append the new entry
   - Confirm addition

## Mode: Match

1. **Load the library:**
   - Read `00-system/prompt-library.yaml`

2. **Compare against current input:**
   - Check trigger keywords against the user's message
   - Look for semantic similarity to stored prompts

3. **Surface matches:**
   - If match found: "This looks like your '[name]' prompt. Want to use the refined version?"
   - Show the stored prompt
   - Let user confirm or proceed with raw version

4. **No match:**
   - "No matching prompts in library. Proceed with your current prompt."

## Mode: Proactive (mid-conversation)

**When to trigger:** Claude should offer this when detecting exploratory patterns (see `<proactive_detection>` section above).

1. **Recognize the pattern:**
   - Multiple iterations on the same output
   - Format refinements
   - "Actually what I want is..." pivots
   - Satisfaction signals after iteration

2. **Offer to capture:**
   - Brief summary of the pattern observed
   - Ask if user wants to distill
   - Respect "no" — continue without further prompting

3. **If yes, proceed to Distill mode**

4. **If no, note it and don't re-offer** for this conversation thread
</process>

<library_format>
Entries in `00-system/prompt-library.yaml` follow this structure:

```yaml
prompts:
  - id: market-sizing          # kebab-case identifier
    name: "Market sizing analysis"
    description: "TAM/SAM/SOM breakdown for a market opportunity"
    prompt: |
      Analyze the market size for [TOPIC] using the TAM/SAM/SOM framework.

      For each level:
      - TAM: Total addressable market (global opportunity)
      - SAM: Serviceable addressable market (your realistic reach)
      - SOM: Serviceable obtainable market (near-term capture)

      Include:
      - Data sources and methodology
      - Key assumptions
      - Growth projections
    triggers:
      - "market size"
      - "TAM SAM SOM"
      - "how big is the market"
      - "market opportunity"
    created: 2026-02-05
```
</library_format>

<success_criteria>
**Distill mode:**
- Conversation journey understood
- Refined prompt captures the essence without the noise
- Triggers are relevant and will match future similar requests
- Entry added to library successfully

**Match mode:**
- Library loaded and searched
- Relevant matches surfaced with the stored prompt
- User can choose to use stored version or proceed raw
</success_criteria>

<examples>
## Example: Distill (with user context)

User has just finished a back-and-forth exploration about competitive analysis.

```
/promptly

Loading user context from CLAUDE.md...
- Communication style: Direct, no fluff, commercially-minded
- Key frameworks: Portfolio (Explore/Scale/Optimize/Retire), Impact Assessment
- Role context: CPO, product leader

Analyzing your conversation...

You explored competitive analysis for Haiven, iterating through:
- Initial ask: "who are the competitors"
- Refined to: feature comparison matrix
- Added: positioning analysis
- Final output: strategic recommendations

Here's your distilled prompt (adapted to your style):

---
**Competitive Analysis Framework**

Analyze the competitive landscape for [PRODUCT/COMPANY] in [MARKET].

Structure:
1. **Direct competitors** (same solution, same customer)
2. **Indirect competitors** (different solution, same problem)
3. **Feature comparison matrix** (key capabilities)
4. **Positioning map** (2x2 on key dimensions)
5. **Strategic implications:**
   - Where do we fit in the portfolio (Explore/Scale)?
   - What's our differentiated position?
   - Capital allocation implications

For each competitor: funding, revenue signals, architecture constraints, defensibility.

Be direct. No fluff. What does this mean for our strategy?
---

Triggers: "competitive analysis", "who are the competitors", "competitor landscape"

Add to library as 'competitive-analysis'? [Y/n]
```

## Example: Proactive Offer (mid-conversation)

User has been iterating on a meeting prep format for 3+ turns...

```
User: "Actually, can you add a section for open commitments I have to them?"

Claude: [Provides updated format]

User: "Yes, that's exactly what I need for meeting prep."

---
This looks like a prompt pattern worth capturing.

What I noticed:
- Initial ask: "prep me for meeting with X"
- Added: relationship history from Notion
- Added: open threads and last contact
- Added: commitments (both directions)
- Final form: structured prep doc

Want me to distill this as a reusable 'meeting-prep' prompt?

[Yes, capture it] [No, just continue]
---
```

## Example: Match (session start)

User starts a new session:

```
User: "I need to understand who the competitors are in eldercare tech"

[promptly match triggered]

This looks like your 'competitive-analysis' prompt. Use the refined version?

---
Analyze the competitive landscape for [PRODUCT/COMPANY] in [MARKET].
...
---

[Use refined] [Proceed raw]
```
</examples>

<edge_cases>
- **No clear pattern**: If conversation was too scattered, ask clarifying questions about what the user was trying to achieve
- **Library doesn't exist**: Create it with empty prompts array
- **Duplicate detected**: If similar prompt exists, ask whether to update existing or create new
- **Match ambiguity**: If multiple prompts match, present top 2-3 and let user choose
</edge_cases>
