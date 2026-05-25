# Hackson Frontend Design

Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## 1. Design Position

Hackson should not look like a normal chatbot with two assistant names. The product is a live two-Agent world: the user watches two AI individuals exist, joins them mid-conversation, or opens a focused companion chat.

The frontend should therefore feel like a quiet control room for a living timeline:

- Real-time enough to feel alive.
- Structured enough to make context, memory, and mode boundaries understandable.
- Minimal enough that the Agents, their messages, and their state remain the focus.

The style should be a restrained sci-fi workspace, not cute pet-game UI and not enterprise admin UI. It can have atmosphere, but the interface must stay operational.

## 2. Core Product Feeling

Target feeling:

- "I am entering a world already in motion."
- "These two Agents have identities and a relationship."
- "I can interrupt naturally without starting over."
- "I can see what the system is doing without reading debug logs."

Avoid:

- ChatGPT clone with a left chat list and one central message column as the whole product.
- Decorative cyberpunk UI with low readability.
- Cartoon desktop-pet UI as the main V1 web product.
- Dense developer dashboard as the first impression.
- Marketing landing page before the actual product.

## 3. Visual Style

Recommended style: calm observatory interface.

Use:

- Dark neutral base with warm off-white text.
- Thin borders, subtle surfaces, and clear spacing.
- Two stable Agent identity colors, one per Agent.
- Small state indicators for idle, joined, paused, thinking, and writing.
- Timeline and transcript layouts that show continuity.
- Compact controls with icons and short labels.

Avoid:

- Purple-blue gradient dominance.
- Beige/brown notebook themes.
- Heavy glassmorphism.
- Large rounded cards everywhere.
- Mascot-first layout.
- Long instructional text inside the app.

Color direction:

- Background: near-black charcoal, not pure black.
- Primary text: warm white.
- Secondary text: muted gray.
- Agent 1 accent: electric teal or cyan.
- Agent 2 accent: signal amber or coral.
- User accent: clean white or soft green.
- System events: muted violet or steel blue, used sparingly.
- Error/blocker: red with plain language.

Typography:

- Use a modern sans-serif for UI.
- Use monospace only for technical traces, context package ids, and tool logs.
- Keep type sizes compact. This product is a workspace, not a hero page.
- Letter spacing should stay normal.

Shape language:

- Cards: max 8px radius.
- Tool buttons: square or compact rounded rectangles.
- Status chips: small, high-contrast, not decorative.
- Panels: full-height or full-width regions, not floating nested cards.

## 4. Information Architecture

V1 should have four main surfaces.

### 4.1 `/@username`

Purpose: user and Agent setup.

Show:

- Current user identity.
- Idle on/off.
- Two fixed Agent slots.
- Agent name.
- Avatar.
- Core persona.
- Speaking style.
- Episode state.

Do not show:

- Model endpoint.
- Provider picker.
- API key.
- Local model path.
- Advanced runtime config.

Design:

- Treat the two Agents as paired identities.
- Put Agent 1 and Agent 2 side by side on desktop.
- Stack them on mobile.
- Persona editing should feel like editing an identity sheet, not writing a prompt file.
- Keep labels short: `Name`, `Avatar`, `Core`, `Voice`, `State`.

### 4.2 `/idle`

Purpose: watch the two Agents live.

This is the signature screen.

Layout:

- Left rail: two Agent identity blocks and world status.
- Center: living timeline transcript.
- Right rail: scene, recent topic, relationship, and context notes.
- Bottom: join input.

Core interaction:

- User watches idle messages arrive.
- User types into the bottom input.
- On submit, UI switches into joined state (`companion_1`) without visually breaking the thread.

The join moment should be visible as a small system event:

```text
You joined the conversation
```

Then Agent replies should continue under the same visual timeline. The user should not feel thrown into a separate chat app.

Message design:

- Agent messages use stable accent rails or small avatar marks.
- User message is visually distinct but not oversized.
- System events are compact timeline separators.
- Avoid speech bubbles that make the product feel like a mobile messenger.

### 4.3 `/companion`

Purpose: start a focused user-led chat.

This can be closer to a normal chat interface, but it should still carry Hackson identity.

Show:

- Selected Agent or both Agents.
- Current conversation transcript.
- Input composer.
- Small Agent persona snapshot.

Do not default to idle history. Only surface idle context when the user asks about it or when the backend returns it.

Design:

- Clean central transcript.
- Right-side compact persona/context panel on desktop.
- On mobile, persona/context becomes a drawer.

### 4.4 Future `/work`

Purpose: task collaboration and tool progress.

Do not build it as V1 primary navigation unless backend support exists. Reserve the design language.

Expected layout:

- Objective at top.
- Planner / Worker / Reviewer lanes.
- Task state timeline.
- Tool trace panel.
- Blockers and next action.

Work Mode must feel more operational than emotional. It should not reuse idle diary or relationship visuals.

## 5. Navigation

Recommended desktop shell:

- Narrow left app rail.
- Routes: `Idle`, `Companion`, `Agents`, later `Work`.
- User menu at bottom.
- Current world state visible near top.

Recommended mobile shell:

- Top bar with current mode.
- Bottom tab bar for primary routes.
- Agent/context panels open as drawers.

Navigation labels should be short:

- `Idle`
- `Chat`
- `Agents`
- `Work`

Avoid explanatory nav labels like `Watch AI Life Mode` or `Companion Mode 2`.

## 6. Mode Design

The UI must make mode boundaries visible without making the user learn backend terms.

Backend mode names and UI labels:

- `idle` -> `Idle`
- `companion_1` -> `Joined`
- `companion_2` -> `Chat`
- `work` -> `Work`

Mode indicators:

- Use a small status chip near the transcript header.
- Show `Idle` when Agents are talking to each other.
- Show `Joined` after user joins an idle thread.
- Show `Chat` in a fresh user-led conversation.
- Show `Work` only for task mode.

Do not expose raw mode names in primary UI unless in a developer/debug panel.

## 7. Agent Identity

Two Agents should feel like stable people with visible difference, not two copies of the same assistant.

Each Agent needs:

- Name.
- Avatar.
- Accent color.
- Short voice label.
- Current state.
- Optional mood/state phrase.

Avatar direction:

- V1 can use uploaded images, generated portraits, initials, or abstract identity marks.
- Avoid default robot icons for both Agents.
- Keep avatar size practical; identity should support the transcript, not dominate it.

Agent state examples:

- `thinking`
- `writing`
- `idle`
- `paused`
- `joined`

Keep user-facing state labels short:

- `Thinking`
- `Writing`
- `Idle`
- `Paused`

## 8. Context Visibility

Hackson's differentiator is context handling, but the main UI should not become a debug console.

Use progressive disclosure.

Normal user view:

- Recent topic.
- Scene summary.
- Relationship summary.
- Agent state.

Developer or advanced view:

- Context package id.
- Included recent messages count.
- Included summary ids.
- Token estimate.
- Prompt hash.

The right rail in `/idle` should show readable context, not raw prompt text.

Suggested sections:

- `Scene`
- `Topic`
- `Bond`
- `Memory`

Each section should be one to three short lines.

## 9. Timeline Model

The transcript should feel like a timeline, because the product is built around a living world.

Timeline item types:

- Agent message.
- User message.
- System event.
- Mode transition.
- Future tool event.
- Future diary event.

Design rules:

- Preserve chronological sequence.
- Use sequence order from backend when available.
- Support infinite scroll upward for history.
- Keep new messages anchored near the bottom.
- Do not collapse user join into an invisible API transition.

## 10. Input Design

Idle input:

- Placeholder: `Join`
- Button: send icon.
- Optional small mode hint chip: `Idle`

Companion input:

- Placeholder: `Message`
- Button: send icon.
- Optional Agent selector.

Do not use long placeholders such as "Type a message to join the Agents' ongoing idle conversation".

Composer controls:

- Send.
- Stop or pause idle.
- Attach image later.
- Agent target selector in companion mode.

## 11. Settings Design

Settings must stay product-facing.

Allowed V1 settings:

- Display name.
- Language preference.
- Idle on/off.
- Agent name.
- Agent avatar.
- Core persona.
- Speaking style.
- Episode state.

Forbidden V1 settings:

- Model endpoint.
- API key.
- Provider.
- Claude/OpenAI key.
- Local model path.
- Secret references.

If runtime configuration is needed for internal testing, hide it behind a separate developer-only route outside normal user settings.

## 12. Empty, Loading, and Error States

Empty idle:

- Show both Agent identity blocks.
- Show a quiet empty timeline.
- Primary action: start idle.

Loading:

- Use inline thinking states on Agent identity and transcript.
- Avoid full-screen spinners after the app has loaded.

Error:

- Put the error near the affected action.
- Use plain text.
- Offer retry.
- Do not expose raw stack traces in user UI.

Suggested short copy:

- `Could not send`
- `Retry`
- `Disconnected`
- `Reconnecting`
- `Paused`

## 13. Responsive Rules

Desktop:

- Three-region layout works best for `/idle`.
- Left identity rail: fixed width.
- Center timeline: flexible.
- Right context rail: fixed width.

Tablet:

- Left identity rail can compress into a top strip.
- Right context rail becomes a drawer.

Mobile:

- One column.
- Header shows mode and Agent pair.
- Timeline fills screen.
- Context and Agent details are drawers.
- Composer stays fixed at bottom.

Text must never overflow buttons, chips, or cards. Prefer shorter labels before smaller type.

## 14. Component Inventory

Core components:

- `AppShell`
- `ModeNav`
- `ModeChip`
- `AgentSlot`
- `AgentAvatar`
- `AgentState`
- `Timeline`
- `TimelineItem`
- `SystemEvent`
- `MessageComposer`
- `ContextRail`
- `PersonaEditor`
- `IdleToggle`
- `ConversationHeader`
- `HistoryPager`

Future components:

- `DiaryPanel`
- `MemoryCardList`
- `RelationshipMeter`
- `TaskLane`
- `ToolTrace`
- `ContextPackageInspector`

## 15. Copy Rules

The current frontend restriction says wording must be aggressively simplified. Follow it.

Use:

- `Idle`
- `Chat`
- `Agents`
- `Join`
- `Send`
- `Pause`
- `Resume`
- `Scene`
- `Topic`
- `Bond`
- `Memory`
- `Thinking`

Avoid:

- Long onboarding paragraphs.
- Explaining backend concepts in the UI.
- Repeating mode descriptions.
- Buttons with full sentences.

## 16. Accessibility

Minimum requirements:

- All controls keyboard reachable.
- Agent accent colors cannot be the only identity marker.
- Message author must be text-readable.
- Status changes need accessible labels.
- Contrast must remain readable on dark surfaces.
- Composer and timeline must work at mobile widths.

## 17. Implementation Priority

Recommended frontend order:

1. App shell and auth-aware user state.
2. Agent settings page.
3. Idle timeline with paged messages.
4. Idle composer and joined transition.
5. Companion chat.
6. Context rail.
7. Advanced context package inspector.
8. Diary, memory, relationship, and work views when backend supports them.

## 18. Product Design Principle

The frontend should make Hackson's technical architecture legible through product behavior:

- `Conversation` appears as timeline continuity.
- `Message` appears as stable ordered transcript.
- `Agent Persona` appears as identity and voice.
- `Transition Context` appears as a natural join moment.
- `Memory` appears as short, evidence-backed context.
- `Mode isolation` appears as different surfaces for Idle, Chat, and Work.

The result should be a focused interface for a living two-Agent system: quiet, precise, and alive.
