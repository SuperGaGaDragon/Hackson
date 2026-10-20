## header
Created at: 2026-10-20
Created by: Codex
Last Modified at: 2026-10-20
Last Modified by: Codex

# Parallax Light Product Theme

## brief intro
- goal for this file.
  - Define the product-grade light visual system used after visitors enter Parallax Work, Idle, Chat, Me, Auth, and Desktop Companion surfaces.
- 架构思路
  - Preserve the public home composition and extend its calm, editorial visual language into the complete Hackson product.
  - Use semantic colors and restrained surface hierarchy instead of component-specific decorative colors.
  - Keep backend behavior, routes, data, Product/Artifact lineage, and runtime state unchanged.

## product feeling
The authenticated product should feel calm, precise, and trustworthy: a working document and supervision surface rather than a dark developer console.

The interface serves four user needs:

- Predictability: stable navigation, consistent controls, explicit state colors.
- Understanding: clear separation between canvas, working surfaces, selected state, and diagnostics.
- Achievement: strong but restrained completion and progress feedback.
- Control: visible focus, immediate press feedback, reduced-motion support, and readable error states.

## semantic palette
| Token | Value | Use |
| --- | --- | --- |
| Canvas | `#F1F2EE` | Page background and product workspace. |
| Structural rail | `#E9EBE5` | Navigation and fixed chrome. |
| Paper | `#FBFCF8` | Main panels and document surfaces. |
| Paper strong | `#FDFEFA` | Inputs, selected content, and primary reading surfaces. |
| Ink | `#191A17` | Primary text and high-emphasis controls. |
| Ink soft | `#3F423C` | Long-form and secondary body text. |
| Muted | `#6F736A` | Metadata and low-emphasis labels. |
| Rule | `#D7D9D1` | Standard borders and dividers. |
| Rule strong | `#BFC3B8` | Input borders and stronger separation. |
| Accent | `#3154D8` | Focus, selection, navigation, and active work. |
| Accent soft | `#E8ECFB` | Selected rows and focused contextual surfaces. |
| Success | `#247151` | Completed and healthy state. |
| Success soft | `#E5F2EA` | Completed-state background. |
| Warning | `#8F5D15` | Waiting, paused, or review-needed state; AA contrast on warning-soft. |
| Warning soft | `#F7EDD9` | Warning-state background. |
| Danger | `#B34235` | Failed and destructive state. |
| Danger soft | `#F8E8E5` | Failure-state background. |

Color rules:

- Accent blue communicates interaction, not decoration.
- Success, warning, and danger colors never substitute for labels or icons.
- Text contrast must remain readable on every semantic background.
- Avoid gradients, neon glows, and saturated panel fills inside the product workspace.

## surface hierarchy
1. Canvas: quiet warm gray.
2. Structural navigation: slightly darker warm gray.
3. Product panels: paper white with one-pixel rules.
4. Reader and input surfaces: strongest paper tone.
5. Modal surfaces: paper with a bounded shadow and a translucent neutral scrim.

Rules:

- Major surfaces are siblings, not stacks of nested cards.
- Borders define ordinary grouping; shadows are reserved for modal separation.
- Selected rows use accent-soft background and an accent border.
- Diagnostics remain visually quieter than Product, Activity, and current state.

## typography
- Product body uses Instrument Sans with platform sans-serif fallback.
- Technical metadata uses IBM Plex Mono with platform monospace fallback.
- Display and page titles use tighter tracking; body text uses comfortable leading.
- Long-form Product content must remain the most readable text surface.
- User text scaling must not cause horizontal overflow.

## interaction and motion
- Buttons provide immediate `:active` feedback with a one-pixel translation.
- Hover changes color and border only; it must not cause layout movement.
- Focus uses a visible two-pixel accent outline.
- Product interactions must remain available during non-blocking visual transitions.
- `prefers-reduced-motion` removes motion transforms and uses static or opacity feedback.
- `prefers-reduced-transparency` replaces translucent chrome with solid paper.
- `prefers-contrast: more` strengthens rules and text contrast.

## responsive behavior
- Desktop keeps a readable structural sidebar and three-column Work console where space permits.
- Tablet collapses secondary context before compressing the reader.
- Mobile uses a horizontal navigation bar and single-column content.
- No route may create horizontal document overflow at 390 CSS pixels.
- Product reader, Progress, Work Windows, Me forms, and modals must remain usable without tiny text.

## non-goals
- No backend behavior changes.
- No deletion of Hackson or Parallax routes.
- No dark/light theme toggle in this release.
- No decorative animation system.
- No change to the preserved Parallax public home structure.

## release gate
- Backend full test suite and deterministic Work/Context smokes pass.
- Frontend and Desktop builds pass with zero dependency vulnerabilities.
- Browser smoke covers Auth, Idle, Chat, Work, Me, Product, Quality, modal, and mobile layouts.
- Screenshot review confirms palette consistency and readable state contrast.
- Pages edge proxy, health, SSE, deep-link, and download behavior remain unchanged.
- Production Pages deployment passes real Quick Try and Hackson API checks without modifying `hackson.catachess.com`.

## 代办
- Revisit the palette only when a new product state cannot be expressed through the existing semantic tokens.
