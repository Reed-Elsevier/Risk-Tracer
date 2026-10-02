---
name: RiskTracer
description: White page and black text in IBM Plex Sans, with orange #f48529 as the only accent.
colors:
  orange: "#f48529"
  black: "#000000"
  white: "#ffffff"
  ink: "#000000"
  paper: "#ffffff"
  moss: "#f48529"
  ember: "#f48529"
  gold: "#000000"
  mist: "#ffffff"
  line: "#000000"
typography:
  display:
    fontFamily: "IBM Plex Sans, Segoe UI, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 700
    lineHeight: "2.5rem"
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "IBM Plex Sans, Segoe UI, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 700
    lineHeight: "2.25rem"
    letterSpacing: "-0.025em"
  title:
    fontFamily: "IBM Plex Sans, Segoe UI, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: "2rem"
    letterSpacing: "-0.025em"
  body:
    fontFamily: "IBM Plex Sans, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: "1.75rem"
    letterSpacing: "normal"
  label:
    fontFamily: "IBM Plex Sans, Segoe UI, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: "1.25rem"
    letterSpacing: "normal"
rounded:
  lg: "8px"
  xl: "12px"
  2xl: "16px"
  full: "9999px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.moss}"
    textColor: "{colors.black}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: "10px 16px"
  button-primary-hover:
    backgroundColor: "{colors.black}"
    textColor: "{colors.white}"
  button-ink:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.lg}"
    padding: "8px 16px"
  button-ink-hover:
    backgroundColor: "{colors.orange}"
    textColor: "{colors.black}"
  nav-current:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: "6px 12px"
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: "6px 12px"
  nav-link-hover:
    backgroundColor: "{colors.mist}"
  input-search:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.xl}"
    padding: "8px 12px"
  card:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.2xl}"
  chip-high:
    backgroundColor: "{colors.orange}"
    textColor: "{colors.black}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
  chip-medium:
    backgroundColor: "{colors.gold}"
    textColor: "{colors.white}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
  chip-clear:
    backgroundColor: "{colors.mist}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
---

# Design System: RiskTracer

## Overview

The page is white, the text is black, and the face is IBM Plex Sans. Orange `#f48529` is the brand and the high-priority mark. Cobalt `#1e4e8c` marks ownership and record links. Grove `#146b43` marks a clear result. Amber `#e6b325` marks medium priority and a watch. Black text sits on orange and amber. White text sits on cobalt, grove, and black. Raised surfaces use one soft card shadow.

Home’s two-column desk is that page’s composition. It is not a layout rule for investigation or supplier screens.

**Key Characteristics:**

- White ground, white cards, black text
- IBM Plex Sans, with weight 700 on titles
- Orange and amber fills carry black text
- Cobalt, grove, and black fills carry white text
- One soft card shadow

## Colors

Orange remains the brand. Three other hues carry status and wayfinding. Black is the text. White is the ground.

### Primary

- **Orange** (#f48529): The wordmark tile, the open-investigation action, high priority, and duplicate-submission alerts. Text on an orange fill is black.

### Secondary

- **Cobalt** (#1e4e8c): Ownership, watchlist exposure, source-record chips, and link underlines. Text on a cobalt fill is white.
- **Grove** (#146b43): No flagged signals, and a signal card with nothing to review. Text on a grove fill is white.
- **Amber** (#e6b325): Medium priority, and a watch such as an invoice exception or a purchase-order review. Text on an amber fill is black.

### Neutral

- **Black** (#000000): Default text, the current nav pill, the decision submit button, and the focus outline. Text on a black fill is white. The submit button turns orange with black text on hover.
- **White** (#ffffff): The page and neutral cards. Supporting copy on white is black at reduced opacity.

### Named Rules

**The Priority Color Rule.** High is orange with black text. Medium is amber with black text. No flagged signals is grove with white text.

**The Orange Fill Rule.** Orange is a fill. It is not body text on white, and white text does not sit on orange.

## Typography

**Display Font:** IBM Plex Sans
**Body Font:** IBM Plex Sans
**Label/Mono Font:** IBM Plex Sans for labels. Record identifiers use IBM Plex Mono.

**Character:** One sans for the interface, with the matching mono only on record identifiers. Titles are bold and slightly tight. Reading text stays regular, with tabular figures. Supporting copy on Home is black at reduced opacity, held to about 62 characters on the opening paragraph.

### Hierarchy

- **Display** (700, 2.25rem, line-height 2.5rem, tracking -0.025em): The home title. From the 640px breakpoint it is 3rem with line-height 1.
- **Headline** (700, 1.875rem, line-height 2.25rem, tracking -0.025em): The investigation invoice id and the supplier name.
- **Title** (700, 1.5rem, line-height 2rem, tracking -0.025em): Home section headings and the case-file id. Step names under the review band are 1.125rem at weight 600.
- **Body** (400, 1rem, line-height 1.75rem): The home introduction, in muted ink, max about 62 characters. Step explanations are 0.875rem with line-height 1.5rem.
- **Label** (600, 0.875rem, line-height 1.25rem): Nav items, the open action, the decision submit button, and the shell search text.

### Named Rules

**The Plex Rule.** Interface text is IBM Plex Sans. Record identifiers are IBM Plex Mono. No other interface face belongs to this system.

**The Bold Title Rule.** Page titles and section titles are weight 700 with tracking -0.025em. Reading text stays weight 400.

## Layout

The shell is a white page with a top bar and a centered container. The wide container is 80rem with 24px of side padding. The top bar uses the same width and padding, with 16px of vertical padding, and wraps. Home’s main block starts 40px below the bar and ends with 64px of bottom padding. Investigation content uses the 80rem container. A missing investigation narrows to 48rem. A supplier profile uses 64rem.

From 640px, the home title steps up to 3rem, and the shell search sits at the end of the bar at 20rem wide. From 768px, the review sequence is three columns separated by the line color. From 1024px, Home splits into a search column and a case-file column at 1.45fr and 0.8fr, with 40px between them. Below that breakpoint the two stack with 32px between them.

## Elevation & Depth

Depth is a soft shadow plus a white surface. The shadow color is black at low opacity. Borders stay visible; the shadow does not replace them. The page focus outline is 2px solid black, offset 3px. The shell and desk search fields clear their own outline, so that ring is the page default rather than the ring those fields currently draw.

### Shadow Vocabulary

- **Card** (`box-shadow: 0 14px 40px rgba(21, 34, 31, 0.08)`): Home cards, the shell search, and the search result panel.
- **Case file hover** (`box-shadow: 0 18px 44px rgba(21, 34, 31, 0.14)`): The home case file only, on hover and focus-within, and only when the user has not requested reduced motion.
- **Node** (`box-shadow: 0 8px 20px rgba(21, 34, 31, 0.08)`): Ownership graph nodes.

### Named Rules

**The Card Shadow Rule.** Raised cards and the bar search use the card shadow. It is a soft blur. It is not a hard offset.

## Shapes

Cards, including the home search well and the case file, use a 16px corner. The shell search and the wordmark tile use a 12px corner. The decision submit button and its fields use an 8px corner. Nav items, the open action, and priority chips are full pills. Ownership nodes use a 14px corner of their own; that radius is not a step on the shared scale.

## Components

### Buttons

The open action is a moss pill. The decision submit is an ink rectangle that turns moss on hover.

- **Shape:** Open action is a full pill (9999px). Decision submit is an 8px corner.
- **Primary:** Orange background, black text, label type, padding 10px 16px.
- **Hover / Focus:** Open action hover is black with white text. Focus uses the page outline, 2px solid black, offset 3px.
- **Ink:** Ink background, white label type, padding 8px 16px, 8px corners. Hover turns the background moss. Disabled drops to 40% opacity and shows a not-allowed cursor.

### Chips

Priority is a full pill with 4px 12px padding and 0.75rem bold type.

- **Style:** High is ember on white. Medium is gold on white. No flagged signals is mist on ink.
- **State:** The chip states the priority value. It is not a filter control.

### Cards / Containers

White surfaces with a 16px corner and the card shadow.

- **Corner Style:** 16px.
- **Background:** White on Home and in the shell.
- **Shadow Strategy:** The card shadow. See Elevation & Depth.
- **Border:** Card line on the home search and the case file. The header and the review-step rules use the line color and no shadow.
- **Internal Padding:** Home case file and supplier cards use 24px. Investigation signal cards use 20px.

### Inputs / Fields

The shell search is a white field with a card-line border, a 12px corner, the card shadow, and 8px 12px padding. The icon and the text are in a row; the text is label size and the placeholder is muted ink. The desk search is the same border and shadow on a 16px card, with 1.25rem ink text and 20px of padding inside the field row. Decision fields are white, 8px corners, padding 8px 12px, and show a moss border when focused.

- **Style:** Shell search as above. The field itself has no fill of its own; the wrapper carries the border.
- **Focus:** The page default is the moss outline. These search fields remove that outline on the input.
- **Error / Disabled:** A failed search is a sentence in the result panel, in ink. The decision form’s error line is ember text on a pale ember wash. The submit button’s disabled state is 40% opacity.

### Navigation

A white bar with a bottom line. The wordmark is an orange tile, 36px square, 12px corners, with the letter R in black at 0.875rem weight 900, then the name RiskTracer in label size at weight 900 and tight tracking. The only item is Home. Current is a black pill with white text, padding 6px 12px. Otherwise the item is black text and darkens slightly on hover. From 640px the shell search moves to the end of the bar.

### Case file

Home only. It is the white card: 16px corners, card-line border, card shadow, 24px horizontal padding. It is rotated 1.6 degrees from an origin at 78% 0. When motion is allowed, the shadow eases over 420ms with cubic-bezier(0.16, 1, 0.3, 1) and deepens on hover and focus-within. That rotation is not the shape of other cards.

### Ownership nodes

Graph nodes are a warm white (#fffef9) with a 14px corner, 12px 14px padding, a 1px border (#b8c4ba), and the node shadow. A listed node uses an ember border and a pale ember fill (#fff2eb). A supplier node uses a moss border and a pale moss fill (#edf8f0). Minimum width is 176px.

## Do's and Don'ts

### Do:

- **Do** set the page background to white and the default text to black.
- **Do** use IBM Plex Sans for interface text, and IBM Plex Mono for record identifiers.
- **Do** raise cards and the bar search with the card shadow.
- **Do** color high priority ember, medium priority gold, and no flagged signals mist with ink text.
- **Do** keep the page focus outline at 2px solid moss, offset 3px.

### Don't:

- **Don't** introduce another interface typeface.
- **Don't** replace the card shadow with a hard, unblurred offset.
- **Don't** paint the open action in ember. That action is moss.
