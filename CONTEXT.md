# Hackson Context

Hackson is a living two-Agent product where Idle, Companion, and Work experiences share raw history but use separate context rules. This glossary fixes product language so implementation documents do not drift.

## Language

**Context Runtime**:
The product layer that turns Hackson state into model-visible context for one model turn. It owns what the model sees, not how the model is called or how visible messages are stored.
_Avoid_: Context OS, prompt builder, memory system

**Auditable Context Package**:
A reproducible record of the materials used to build one model turn's context. It is the V1.0 release gate for Context Runtime.
_Avoid_: prompt log, debug blob, trace

**Full Prompt Logging**:
An optional user-controlled setting that stores the complete model-visible prompt text for future review and debugging. It defaults on in V1.0, retains full prompt text for 30 days, and is separate from Auditable Context Package metadata.
_Avoid_: invisible prompt capture, forced prompt storage

**Raw Message**:
The saved user, Agent, system, or tool line that remains the historical source of truth. Summaries, memories, and diary entries are derived from Raw Messages.
_Avoid_: chat row, transcript item

**Topic Direction**:
User-provided steering metadata for Idle generation. It is not a Raw Message and must not be rendered as if the user said it in the transcript.
_Avoid_: topic message, fake user message

**Idle Cadence**:
The rule that decides when Idle may create the next Agent turn. Browser Auto is a control surface; a server-owned cadence is a later runtime capability.
_Avoid_: Auto timer, background chat

**Idle Interruption**:
A user-authored line entered while an Idle model turn is already generating. It should remain visible as pending user intent and become the next prioritized Idle Say turn when the current generation settles.
_Avoid_: disabled input, cancelled thought, hidden draft

**Turn Intent**:
The single conversational move an Agent should make in the next visible reply. It keeps Idle from turning every turn into a full advice essay.
_Avoid_: response type, prompt vibe, style instruction

**Relationship Stance**:
The lightweight description of how one Agent tends to relate to the other Agent in the current scene. It supports continuity without rewriting core persona.
_Avoid_: mutable persona, relationship memory, mood

**Background Idle**:
A user-controlled setting that allows Idle Cadence to keep creating Agent turns after the browser is closed. It must be bounded by server-side budget, cooldown, and failure rules.
_Avoid_: infinite idle, always-on chat

**Companion 1**:
The mode where the user explicitly joins an existing Idle conversation. It uses the child conversation as direct history and the parent Idle conversation as background.
_Avoid_: joined chat, three-way chat

**Memory Control**:
The user-facing ability to inspect, disable, or delete governed memory. It is different from editing profile fields or prompt logs.
_Avoid_: memory editor, hidden memory admin

**Debug Surface**:
A user-visible but secondary area for audit and troubleshooting controls such as Full Prompt Logging and retained prompt logs. It should not be the primary product workflow.
_Avoid_: settings main content, default prompt dump

**Agent Profile Editor**:
The primary Me-page surface where the user edits Nora and Vale's names, voices, personalities, and stories. It is more central to daily product behavior than debug logs.
_Avoid_: hidden agent config, low-priority advanced setting

**Evaluator Runtime**:
The product layer that checks a completed or in-progress Work Mission against its goal, visible trace, Products, Artifacts, and retrieved evidence. It flags reliability risks; it does not prove truth.
_Avoid_: hallucination detector, universal agent safety platform

**Reliability Report**:
A user-visible assessment produced by Evaluator Runtime for one Work Mission. It contains a reliability score, status, issue list, supporting trace references, and suggested fixes.
_Avoid_: grade, benchmark score, model judgement

**Requirement Coverage**:
The mapping between atomic requirements inferred from a Mission goal and what the final Product or Artifact actually provides.
_Avoid_: task understanding, intent score

**Evidence Ledger**:
The bounded set of source snippets, URLs, tool observations, and research Artifacts that Evaluator Runtime is allowed to use when checking factual claims.
_Avoid_: web memory, source dump, hidden browsing history

**Reliability Issue**:
A concrete failure or risk detected by Evaluator Runtime, tied to a requirement, claim, source, tool event, Product, or Artifact. It must include severity and a suggested fix.
_Avoid_: feedback, comment, vague concern

**Research Mission**:
A Work Mission whose Product depends on external facts or sources. It is the first supported scope for Evaluator Runtime.
_Avoid_: any agent task, general work

**Artifact Navigator**:
The Product reader control that lets the user scan and select Artifacts belonging to one Product. It is navigation, not the deliverable itself.
_Avoid_: artifact card wall, debug lineage dump, title gallery

## Example Dialogue

Developer: "Should V1.0 implement memory?"

Domain expert: "No. V1.0 ships Auditable Context Package first. Memory can be wrong in many ways; without auditable context, we cannot diagnose whether a bad Agent reply came from the recipe, source selection, budget, or model policy."

Developer: "Can Topic Direction be saved as a message?"

Domain expert: "No. Topic Direction steers Idle, but the Raw Message transcript must show only visible events."

Developer: "Can we store the complete prompt?"

Domain expert: "Yes, but only through Full Prompt Logging. The user must be able to control whether complete prompt text is retained."

Developer: "Can users edit old full prompt logs?"

Domain expert: "They can view and delete retained prompt logs from Me, but historical prompt text should not be edited because it is an audit record."

Developer: "Should Prompt Logs appear before Agent editing in Me?"

Domain expert: "No. Prompt Logs belong to the Debug Surface. Agent Profile Editor is the primary Me workflow and should appear before debug artifacts."

Developer: "Should Idle continue after the browser closes?"

Domain expert: "Only if the user enables Background Idle, and only under server-side budget and cooldown rules."

Developer: "Can the user type while an Agent is generating?"

Domain expert: "Yes. That is an Idle Interruption. The UI keeps it visible as pending user intent, and the backend serializes it with the same transcript lock used by Idle Tick."

Developer: "Can Relationship Stance change an Agent's core persona?"

Domain expert: "No. Relationship Stance is scene context for how Agents relate to each other. Core persona remains user-owned source data."

Developer: "What memory can Companion 1 use?"

Domain expert: "Companion 1 can use idle relationship memory for the parent Idle background and companion user memory for the user's preferences. Work memory stays out."

Developer: "Does Evaluator Runtime certify that a research answer is true?"

Domain expert: "No. Evaluator Runtime flags reliability risks from the Mission trace, evidence ledger, and requirement coverage. It is a quality gate for human review, not a mathematical proof."

Developer: "Can Evaluator Runtime inspect hidden model reasoning?"

Domain expert: "No. It uses visible Mission events, Products, Artifacts, tool observations, and persisted context metadata. Raw chain-of-thought stays out."

Developer: "Should Product Artifacts render as a wrapping card grid?"

Domain expert: "No. Artifact Navigator should keep a fixed scan rhythm. The Product reader owns long-form content; generated titles should not reshape the layout."
