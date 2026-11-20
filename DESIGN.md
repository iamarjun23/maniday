# Manidhay: design notes

> **Update, 19 Nov 2026:** `index.html` now follows a "modern living" reference layout:
> - a warm white palette with a burnt-orange accent and Plus Jakarta Sans type
> - a pill-shaped nav and glass cards
> - a Three.js cutaway house in the hero
>
> The Hoysala temple-wall version described below is kept as `index-hoysala.html`. The content plan in BRIEF.md applies to both.
>
> The site is now **six pages**: `index`, `services`, `projects`, `academy`, `about` and `contact`. They share:
> - `css/styles.css`: tokens, light and dark themes, components and page sections
> - `js/main.js`: the icon sprite, theme toggle, menu, reveals, filter, form prefill
>
> The header and footer are copied into each page on purpose, so the site works without a build step. When you change one, change all six.
>
> **Eye comfort rules:**
> - no pure black or white
> - soft layered shadows instead of hard borders
> - 17 px body text at 1.7 line height, with lines capped near 62 characters
> - slow easing on motion
> - a system-aware dark theme with a manual toggle
> - soft cross-fades between pages
> - everything still respects reduced motion
>
> **Scroll storytelling (Home):** a pinned 3D stage builds the home as you scroll through six steps:
> 1. site
> 2. blueprint wireframe
> 3. approval (the wireframe turns green)
> 4. ground floor
> 5. upper floor and furniture
> 6. lights on for the griha pravesha
>
> On phones, the stage is a pinned window and the cards slide up underneath it.
>
> **Animation markup, used on every page:**
> - `data-r="left|right|scale|clip"` sets how an element reveals.
> - `data-stagger` makes children reveal one after another.
> - `data-count` makes a number count up.
> - `data-scrub` with `data-at` ties steps to scroll position.
> - Headings rise word by word automatically.
>
> Parallax photos, the timeline line, the hero exit and the progress bar use CSS scroll timelines where the browser supports them. In other browsers they stay still.

Method: the `awwwards` skill from juliobsz/skills (brief, three concepts, art direction, genericness test). The stack is the existing single static `index.html`.

## Brief
- **Subject:** Manidhay Business Services, a civil engineering firm in Karnataka. Seven services (engineering design, architecture, approvals, loans, construction, readymade concrete walls, education and training).
- **Audience:**
  - Families building a home.
  - Plot owners.
  - Engineering students and practising engineers, for the courses.
- **The client:** older and traditional. He wants the site to feel Indian, not like a modern tech site.
- **The site's job:** get call-back requests and sell Academy courses.

## Concepts considered
| | Idea | Anchor | O / F / Fe / P |
|---|---|---|---|
| **A. Place (chosen)** | The site is built like a Hoysala temple wall: each section is a carved band, and the whole page stands on a *gajapatti*, the row of elephants carved at the base of the wall | Hoysala temples (Belur, Halebidu) are in the region where Manidhay works, and the firm has a temple project in Chikmagalur | 4 / 5 / 4 / 2 |
| B. Culture / process | Building as a life event: from bhoomi puja to griha pravesha | how Indian families actually experience a build | 4 / 5 / 5 / 3 |
| C. Material | Every section as an Indian stamp-paper document with guilloche borders and seals | approvals paperwork | 3 / 3 / 4 / 3 |

A was picked. From B, I took the process section: six steps from bhoomi puja to griha pravesha, laid out as kalyani (stepwell) steps.

## Concept card
- **Idea:** a Hoysala temple wall. The elephant band (gajapatti) carries the building, and Manidhay carries the build.
- **Metaphor:** carved soapstone friezes, lime-plaster walls, temple niches and the border of a Mysore silk saree.
- **Signature:** a procession of decorated elephants walks slowly along the plinth under the hero. It comes back as the foundation of the footer.
- **Emotion:** grounded, trusted, rooted in Karnataka.
- **Motion verb:** *carve and settle.* Ornament lines draw in like a chisel, and blocks settle down into place.
- **Screenshot:** the hero headline over the stone plinth, with the elephants mid-stride.

## System
- **Palette:**
  - ground: lime plaster `#F5EEDF`
  - ink: `#231E17`
  - muted: `#6B5E4B`
  - stone: soapstone `#1F2925`
  - accent: kumkum `#8E1B12`
  - ornament: haldi `#E2A72E`
- **Type, all from Indian foundries:**
  - Rozha One (Indian Type Foundry) for display.
  - Mukta (Ek Type) for text, at 18 px body for older readers.
  - Tiro Kannada for Kannada greetings and the step numerals.
- **Shape:**
  - A 4 px radius on controls.
  - Arches only on niches and frames.
- **Layout:**
  - Symmetry, as in temple architecture.
  - A different layout family per section: split hero, niche grid, ledger, stepwell, split product, field-colour academy with a table, arched frames, form.
- **Genericness test:** a generic "Indian website" would use tricolour saffron and green, mandalas, paisley and diyas. All of those are avoided. Every motif here comes from Karnataka's building tradition.

## Still placeholder
- WhatsApp number and Bangalore branch address. Phone, email and head office now come from the live site.
- Course names, durations and fees.
- Project photographs (line drawings are used for now).
- Podcast, blog, YouTube and Facebook links.
- The form backend.
