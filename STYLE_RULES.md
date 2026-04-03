# STYLE_RULES

## Purpose

- This file defines the visual rules for public-facing and shared UI styling.
- Use it alongside [PROJECT_RULES.md](C:/Users/gethe/Desktop/qr_reader/PROJECT_RULES.md) before making meaningful frontend changes.

## Brand Direction

- The product should feel calm, credible, operational, and professional.
- Prefer "software buyers trust this" over "startup landing page with many accents."
- Use visual restraint. Strong hierarchy is better than loud decoration.

## Color System

- Default palette: neutral slate surfaces plus one primary blue accent family.
- Acceptable accent use:
  - primary actions
  - active states
  - key brand marks/icons
  - subtle highlights
- Avoid mixing unrelated bright accent families in the same section.
- Do not use pink, green, purple, orange, and blue together unless the colors are semantic status signals.
- Reserve strong non-blue colors for semantic meaning:
  - green: success/status only
  - yellow/orange: warning/highlight only
  - red: destructive/danger only

## Gradients, Shadows, and Depth

- Use gradients sparingly, mainly for brand marks or very soft page backgrounds.
- Avoid gradient-filled feature cards, multi-color CTA buttons, and rainbow icon systems.
- Shadows should be soft and low-contrast.
- Prefer subtle depth from border + soft shadow instead of heavy glow.

## Surfaces and Layout

- Prefer clean light surfaces with restrained borders and generous spacing.
- Cards should look consistent across a page:
  - similar radius family
  - similar shadow intensity
  - similar border treatment
- Do not make every card look like a different component system.
- Sections should have clear spacing rhythm and enough white space to lower cognitive load.
- Data-heavy internal views should use neutral or softly tinted headers instead of bold gradient header bars.

## Typography and Content Density

- Headlines should be confident and concise.
- Body copy should be easy to scan and not over-styled.
- Avoid oversized decorative icons competing with text hierarchy.
- Prefer fewer strong emphasis points per section.

## Buttons and CTAs

- Each area should have one obvious primary CTA.
- Secondary actions should usually be outlined or neutral, not another loud filled color.
- Do not place multiple equally loud CTA colors next to each other unless the intent is explicitly semantic.
- Button styling should match the page palette and not introduce a new color family.

## Navbar Rules

- The navbar must feel like part of the same page, not a separate theme.
- Use the same neutral surfaces and primary accent family as the page beneath it.
- Public auth actions should follow:
  - one primary filled button
  - one secondary neutral or outlined button
- Theme toggle, language switcher, and menu buttons should use quiet utility styling, not attention-grabbing colors.

## Marketing Page Rules

- Hero sections should be visually clean:
  - one clear headline
  - one supporting message
  - one compact set of proof/highlight items
- Feature grids should prioritize readability over novelty.
- If many features are listed, keep icon treatment consistent and subdued.
- Interactive expansion controls should feel lightweight and unobtrusive.

## Mobile-First Expectations

- Public marketing pages must remain polished on phones first.
- On mobile:
  - stacks are preferred over squeezed multi-column layouts
  - touch targets must stay large
  - cards should not feel cramped
  - nav controls must remain simple and obvious
- Desktop enhancements should not come at the cost of mobile clarity.

## Dark Mode

- Dark mode should preserve the same hierarchy and restraint as light mode.
- Do not make dark mode more saturated than light mode.
- Keep contrast high, but accents controlled.

## Localization and Copy Safety

- Any new user-visible text must follow the project i18n system documented in [PROJECT_RULES.md](C:/Users/gethe/Desktop/qr_reader/PROJECT_RULES.md).
- Styling changes must not depend on hardcoded language assumptions.
- Allow for longer translated labels in buttons, nav items, and cards.

## Reuse Guidance

- Reuse existing spacing, card, and utility patterns before inventing new ones.
- If a page already has a calmer established system, extend it instead of introducing a parallel aesthetic.
- Before adding new colors or visual effects, justify them against this file.
- For badges in dashboards and tables, prefer subdued tinted semantic badges over fully saturated fills unless the state is destructive or urgently important.
