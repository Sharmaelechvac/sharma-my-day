# My Day — revised size & layout spec (v2, research-based)

Written 2026-11-15 at Sanjay's direction ("Get the designs better"). Scope: SIZE, HIERARCHY and LAYOUT only. Mark's brand rules (palette, fonts, logo, gold line, no gradients/shadows/emoji) are unchanged and still govern. Nothing built or pushed until this spec lands with Sanjay; then screenshots go to Mark for sign-off, then Sanjay approves.

## What the research says

1. **Real field-service apps open on a timeline, not a stack of cards.** ServiceTitan's field app shows the day as a schedule with open gaps labelled by duration; RUX Service "opens on the technician's day, with a timeline of scheduled work, an Up Next card"; the Hawx technician-app redesign uses a route list with numbered stops, color-coded status and one-handed targets. Job rows are compact: time, customer, job, one action.
2. **Density is an audience decision.** A tool used all day, every day takes compact density — consumer spaciousness in a daily tool "forces constant scrolling." Reference row heights: compact 32–36px, comfortable 40–48px. Tufte's data-ink rule: pixels should carry data; card borders, boxes and whitespace are non-data ink.
3. **Platform numbers (Apple HIG).** Type ramp: Title 2 = 22, Title 3 = 20, Headline = 17 semibold, Body = 17, Callout = 16, Subheadline = 15, Footnote = 13, Caption = 12/11. Tap targets ≥ 44×44pt. Hierarchy comes from deliberate size jumps, not everything being big.
4. **Why template/AI design reads as AI** (Mowgli's "15 tells" analysis, design-press coverage): identical rounded cards with the same shadow and radius ("rules, not boxes" is the fix); an icon or number in a tinted square on every card; uniform type sizes with small steps (fix: one family, clear roles, big jumps between levels); template chrome — numbered markers, middle-dot metadata, arrows on buttons; uniform spacing everywhere so nothing is more important than anything else. Models produce the statistical average of all interfaces; the fix is product-specific decisions made before building.

## Why the current My Day build fails that test (honest map)

- Every stop is the same white card, same padding, same radius — the card-kit tell, even without shadows.
- A navy number chip in a square on every stop — the tinted-square tell.
- Everything is set at 16px with titles only slightly larger (23px condensed) — no real hierarchy; the day heading (31px) and app wordmark (27px) shout louder than any job.
- The Load the Truck panel is a full hero card equal in weight to the stops and ~40% of the scroll before the first job appears.
- Full-width Navigate slabs on every stop, identical — buttons as decoration, not actions.
- Uniform 14px gaps everywhere; materials lists (8 items × 3 TUG stops) fully expanded make one stop ~700px tall. Result: ~1.3 stops per phone screen. A route sheet should show the day.

## The revised layout — a route sheet, not a card stack

```
HEADER (white, gold 3px rule under)   logo 40px · "My Day" 20px
DAY LINE    Monday, November 16 — 26px Barlow SC 700, dark navy
            7 stops · 175 min driving · first stop 8:00 AM (14px, mono numbers)
LOAD THE TRUCK  ruled section, 2-column compact checklist (below)
TIMELINE    58px time rail | hairline | stop content, rules between stops
  8:00  ●   City Electric Supply — pickup ............ [Navigate]
  (75m) |   Altamonte Springs · pickup for the 3 TUGs
        |   Materials — 5 items ▸ (tap to expand)
  9:45  ●   178 Fisher Loop — electrical underground . [Navigate]
            ...
FOOTER      standards line + updated time (13px gray)
```

- **Timeline rail:** start times in the left column (IBM Plex Mono 13.5px, navy, right-aligned), a 1px vertical rule, stop dots as 8px navy squares. Drive legs live ON the rail as small mono labels — (75 min) — the way ServiceTitan labels gaps.
- **Stops are ruled rows, not boxes.** No card, no border box, no radius. Hairline rule between stops. This is the single biggest de-template move.
- **One primary block only:** the first stop (the day's Up Next) gets a 3px gold left edge and an 18px title. Every other stop is equal and quiet.
- **Materials collapse:** each stop shows "Materials — N items" as a tap-to-expand row (native details element, 44px tall). The full list is one tap away; the day fits on ~2 screens instead of ~6.
- **Load the Truck stays on top** (Sanjay loads before he leaves) but compresses: two-column checklist, 14.5px text, ~26px rows, counts in mono gray. Roughly half its current height.
- **Navigate:** compact button on the stop's title row — 44px tall, auto width (min 116px), navy, 4px radius. Not a full-width slab.

## Type & size table (now → revised)

| Element | Now | Revised |
|---|---|---|
| Logo height | 52px (44 mobile) | 40px |
| App wordmark | 27px Barlow SC | 20px Barlow SC |
| Day heading | 31px | 26px Barlow SC 700 |
| Section heading | 22px | 16px Barlow SC 700 + gold rule |
| Stop title | 23px Barlow SC 600 | 17px Inter 600 (18px on first stop) |
| Body / address | 16px / 1.45 | 16px / 1.35 |
| Secondary (who, note) | 16px gray | 14.5px gray |
| Times | 16.5px mono in card | 13.5px mono in rail |
| Drive labels | 13px centered divider | 12.5px mono on the rail |
| Materials rows | 16px, ~27px rows | 15px, ~24px rows, collapsed by default |
| Load list rows | 16px, ~29px rows, 1 col | 14.5px, ~26px rows, 2 cols |
| Navigate | 48px full-width slab | 44px, auto width ≥116px |
| Stop padding | 16–18px card | 12px top/bottom, ruled |
| Gap between stops | 14px + card borders | 0 — rules only |
| Radii | 5px on everything | 0 on sheet, 4px on buttons only |
| Number chips | navy square per stop | deleted — order comes from the rail |

Density target: 2.5–3 stops visible per phone viewport (materials collapsed), vs ~1.3 now. Whole Monday route ≈ 2 phone screens.

## What does not change

Palette, fonts, logo treatment, gold header line, no gradients/shadows/emoji/glass — all per DESIGN-RULES.md. Data contract (data.json) unchanged, so the morning rebuild keeps working; it will also emit the start address when present.

## Flow from here

Sanjay sees this spec → Jarvis rebuilds to it → phone + desktop screenshots to Mark (Design) for sign-off → Sanjay approves → push live and verify on a fresh load.
