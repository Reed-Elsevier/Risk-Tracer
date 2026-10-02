---
version: 1
slug: "frontend-app-page-tsx"
primary_target: "frontend/app/page.tsx"
related_targets: ["frontend/components/AppShell.tsx","frontend/app/layout.tsx"]
---

# Home

## Scope

The home route (`frontend/app/page.tsx`) and the shared shell used by investigations and supplier profiles. Visitor mode: Operate.

## Audience and task

A reviewer with an invoice id, and someone opening the verified demo. Success is finding an invoice or opening `INV0021439` within seconds, and understanding that a review is signals, an ownership path, and a human decision.

## Constraints

Review priority stays rule-based. The narrative only explains. Glossary wording. No investigation queue. Existing investigation and supplier behavior stays; the shell adds a way back to Home.

## Direction contract

THESIS: Home is a desk. Search is the work surface, the verified case is a file clipped beside it, and the review sequence sits under both. It refuses a document-first brief and a demo row that buries search.

OWN-WORLD: Paper `#f7f5ef`, ink `#15221f`, moss `#1f6a50` for the open action, ember `#c35636` only on high priority. Arial. Existing card shadow with offset and soft blur. No new palette.

STORY: The visitor sees two ways in, then the order of a review. They type an invoice, number, or supplier, or they open the verified case.

FIRST VIEWPORT: A top bar with the RiskTracer mark and Home. The left two-thirds is one large search, focused, labeled Find an invoice. The right third is the `INV0021439` case file: invoice id, supplier, amount, priority, and Open investigation. Under both, one band in reading order: signals from source records, the ownership path, then the human review decision. Search is the primary action. Open is the demo action, same vertical band, not buried.

FORM: Desk blotter, fourth on the ordered list. Seed key f68db22e.

SIGNATURE: The case file sits a few degrees off the desk, like a sheet clipped to the blotter. Opening it is the only motion that leaves the page. Search results unfold in place under the field.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
