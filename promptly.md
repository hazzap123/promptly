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

**Prompt library location:** Defined in your `CLAUDE.md`, or auto-discovered as `prompt-library.yaml` in the project root or a `00-system/` subdirectory.

**User context sources** (read to inform prompt style):
- `CLAUDE.md` — User profile, communication preferences, key frameworks
- `user-profile.yaml` (if present in project) — Strategic pillars, thinking patterns, preferences
</context>

<user_context_integration>
When distilling prompts, incorporate the user's known preferences:

1. **Read user context first:**
   - Check CLAUDE.md for communication style (directness, formality)
   - Check user-profile.yaml for frameworks they use (if present)
   - Note their role context and domain from whatever context files exist

2. **Adapt the distilled prompt to match:**
   - Use their preferred framing and vocabulary
   - Structure outputs using frameworks they know
   - Match their communication style
   - Include their standard evaluation criteria where relevant

3. **Example adaptation:**
   - Generic: "Analyze the market opportunity"
   - User-adapted: "Analyze market using TAM/SAM/SOM. Include capital allocation implications."
</user_context_integration>

<proactive_detection>
## When to Offer Help (Proactive Mode)

> **Important:** Proactive mode works best when your `CLAUDE.md` includes instructions for Claude
> to watch for iteration patterns during normal conversation. Without this, proactive mode only
> triggers when `/promptly` is explicitly invoked.

**Trigger signals** — offer to capture when you notice:

*Iteration patterns (high confidence):*
- 2+ rounds refining the same output ("try it as a table", "add X section", "make it shorter")
- Explicit pivots that reveal the real intent ("actually, what I really want is...")
- User asking to restructure or reformat something they just got
- Adding/removing sections to an output iteratively

*Satisfaction signals (trigger after iteration):*
- Explicit satisfaction after refinement ("yes, that's it", "perfect", "exactly what I need")
- User copying or saving the output after multiple rounds
- User saying they'll reuse this format ("I'll use this template", "this is my go-to")

*Exploration patterns (moderate confidence — wait for satisfaction signal):*
- 3+ clarification rounds on the same topic
- Successful output after extended back-and-forth
- User building up a complex prompt through multiple messages

**How to interject:**

Use AskUserQuestion to present the offer clearly:

```
---
I noticed you iterated on this a few times to get it right — this might be worth saving as a reusable prompt.

What I observed:
- Started with: [initial ask]
- Refined: [what changed across iterations]
- Landed on: [the format/structure that worked]

Want me to distill this into a reusable prompt for your library?

[Yes, capture it] [No thanks]
---
```

**When NOT to interject:**
- Executing a predefined plan or checklist
- Simple Q&A exchanges (single question, single answer)
- Debugging or troubleshooting sessions (fixing bugs, reading errors)
- When user is clearly in a hurry or frustrated
- First iteration on something — wait for the refinement loop
- User already declined a proactive offer in this conversation
</proactive_detection>

<process>
## Mode: Distill (default)

### Phase 0: Load User Context

0. **Read user preferences:**
   - Read `CLAUDE.md` for communication style, role context, key frameworks
   - Read `user-profile.yaml` (if present) for strategic pillars and preferences
   - These inform how the distilled prompt should be written — do not assume what you'll find; read it fresh

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
   - Locate the prompt library (check CLAUDE.md for path, or search for `prompt-library.yaml` in project root / `00-system/`)
   - Read the current file, generate a short, descriptive ID (kebab-case)
   - Append the new entry
   - Confirm addition

7. **Confirm addition:**
   - Report: "Added '[name]' to your prompt library."

## Mode: Match

1. **Load the library:**
   - Locate and read `prompt-library.yaml` (check CLAUDE.md for path, or search project root / `00-system/`)

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

**When to trigger:** Claude detects exploratory patterns during normal conversation. Requires the proactive snippet in `CLAUDE.md` (see `proactive-snippet.md`).

1. **Track the conversation shape:**
   - Count refinement rounds on the same topic
   - Note format changes, section additions/removals, structural pivots
   - Watch for the "aha" moment — when the user's real intent becomes clear

2. **Evaluate confidence before interjecting:**
   - **High confidence** (interject immediately): 2+ format iterations + satisfaction signal
   - **Moderate confidence** (wait for satisfaction): extended exploration without clear satisfaction
   - **Low confidence** (don't interject): single iteration, debugging, Q&A

3. **Offer to capture:**
   - Summarize what you observed (initial ask → refinements → final form)
   - Use AskUserQuestion to ask clearly
   - Keep it brief — don't interrupt the user's flow with a wall of text

4. **If yes:** Proceed to Distill mode (Phase 0 onward)

5. **If no:** Acknowledge and continue. Do not re-offer in this conversation thread.

**Silent tracking (always-on):**
When the user expresses satisfaction after multiple iterations — even if /promptly is declined — note
the pattern mentally. If the same shape recurs, proactively offer to capture it next time.
</process>

<library_format>
Entries in `prompt-library.yaml` follow this structure:

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
    created: YYYY-MM-DD
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
- Communication style: [read from CLAUDE.md]
- Key frameworks: [read from CLAUDE.md / user-profile.yaml]
- Role context: [read from CLAUDE.md]

Analyzing your conversation...

You explored competitive analysis for [YOUR_PRODUCT], iterating through:
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
   - What's our differentiated position?
   - Capital allocation implications

For each competitor: funding, revenue signals, architecture constraints, defensibility.
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
- Added: relationship history
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
