# Manidhay redesign: section-by-section brief

This brief maps every piece of content on the live WordPress site (www.manidhay.com, audited 19 Nov 2026) onto the one-page redesign in `index.html`. The visual system (the Hoysala temple wall, palette, type and motion) lives in [DESIGN.md](DESIGN.md); this file covers **what goes in each section and what is still missing**.

**Old site → new page**

| Old page | Goes to |
|---|---|
| Home hero + "What we do" | §1 Hero, §2 Services |
| About (story) | §3 One team, §7 Who we are *(new)* |
| About (team, Visvesvaraya quote) | §7 Who we are *(new)* |
| Services (7 lists) | §2 Services (summary), §5 Walls, §6 Academy |
| Projects + categories + detail pages | §8 Projects |
| Blog, Podcast | §9 Podcast, blog and videos |
| Contact | §10 Contact, §11 Footer |
| Theme demo blocks (lorem ipsum), AdSense, OneSignal | **Dropped** |

**Status key:** ✅ done in `index.html` · 🟡 built, but with placeholder or unverified content · ⛔ not built

---

## 0. Header and mobile drawer ✅
- **Job:** let a visitor jump to any section, with the call-back button always one tap away.
- **Content:** logo (a kumkum square with an "M" mark) · Services · How we work · Compound walls · Academy · Projects · Contact · **Request a call back** button.
- **Layout:** a sticky bar that gets a background once the page scrolls (the `#sentinel` element triggers it). Below about 900 px the links collapse into a full-height drawer.
- **Done:** the "Who we are" link is added. The desktop nav now collapses to the menu below 1200 px, because 7 links don't fit at narrower widths.
- **To do:**
  - Decide whether to use the real round logo from the live site (`Manidhay-Logo-100x100.png`) or keep the new mark. The client has to approve this.

## 1. Hero 🟡
- **Job:** in 5 seconds, say what Manidhay is, where it works and what to do next.
- **Content:**
  - A Kannada greeting, "ನಮಸ್ಕಾರ".
  - The H1 "Your complete building partner, from plot to keys." It replaces the old "One Stop Solution for all Civil Engineering Services".
  - A one-line summary of the services.
  - Buttons: **Request a call back** (primary) and **View our courses**.
  - 3 proof chips: 7 services · one point of contact · courses for engineers.
  - A framed picture of the Mahalakshmi Temple, Chikmagalur.
- **Layout and motif:** split hero. The gajapatti (elephant procession) walks along the plinth under the hero.
- **To do:**
  - Replace the line drawing with a **real photo** of the Mahalakshmi Temple. The live site has 4 in `wp-content/uploads/2018/06/mahalakshmi-temple-chikmagalur-*.jpg`.
  - Add one trust line from the old About page: *"Est. 2018 · Chikmagalur & Bangalore · a family in construction for 3 decades"*.

## 2. Services: "Seven services under one roof" 🟡
- **Job:** show that every service exists and route each one to an enquiry.
- **Content:** 7 niche cards, each with a title, one sentence and a link. Walls and Academy link to their own sections; the rest prefill the contact form.
- **Layout and motif:** a niche grid, with arch-topped cards like temple niches.
- **Fix the copy to match what the firm actually lists.** The live Services page has the sub-items below. Show 3–4 of them per card as a small list under the sentence, or as a "What's included" disclosure.

  | Card | Sub-services from the live site |
  |---|---|
  | Engineering design | RCC and steel structural design · RCC and steel detailing · MEP layouts · fire fighting · HVAC · soil testing |
  | Architecture | Building planning · interior design · 3D visualisation · landscape · residential layout planning |
  | Government approvals | Blueprint online approval · PWD SR estimation · local body plan approvals |
  | Loans & finance | Bank loans for construction and mortgage · estimation and valuation reports |
  | Construction | RCC/steel buildings (residential, commercial, institutional, industrial) · layout development (roads, drains, water, power) · low-cost housing · renovation and retrofitting · estimation/BOQ · quality and site coordination · PMC |
  | Readymade concrete wall | Design and installation |
  | Education & training | See §6 |

- **Verify with the client:** the Approvals card currently promises *land conversion* and *completion certificates*, which the live site doesn't list. Keep them only if the firm really does this work.

## 3. Why one team: "Six people to manage, or one team you can trust" ✅
- **Job:** the core argument, taken from the old "What we do" paragraph: clients usually chase an architect, a structural designer, a licensing agent and so on themselves.
- **Content:** 6 specialists numbered in Kannada numerals (೧–೬), all merging into "Manidhay: one team, one phone number".
- **Layout and motif:** a ledger on a dark soapstone field.
- **To do:** nothing. This section is the old site's best idea, done properly.

## 4. Process: "From bhoomi puja to griha pravesha" ✅
- **Job:** make the process feel familiar and low-risk for families.
- **Content:** 6 steps: Bhoomi (site selection) → Nakshe (design) → Anumati (approvals) → Saala (finance) → Nirmana (construction) → Griha pravesha (handover).
- **Layout and motif:** stepwell (kalyani) steps that go down as you scroll.
- **To do:** none. Optionally add a typical duration to each step once the client provides it.

## 5. Readymade compound walls 🟡
- **Job:** sell the firm's original product (the business started with it in 2018) on its own terms.
- **Content:**
  - A diagram of one panel bay.
  - The headline "Installed in days", with a how-it-works line.
  - 4 benefits: made off-site · quick install · no plastering or curing · any boundary.
  - A **Get a wall quote** button.
- **Layout and motif:** a split product layout, with panels settling into the slots ("carve and settle").
- **To do:** add a **proof strip** of 3–4 real wall jobs from the live portfolio, each with a photo and a place name:
  - Sai Angels School, Chikmagalur
  - St Mary's School, Chikmagalur
  - VCNR Group, Nelamangala
  - P K Ganapathy godown, Somwarpet
  - Hosur project

## 6. Manidhay Academy 🟡 ⚠️
- **Job:** the site's second goal, selling courses.
- **Content now:**
  - A flagship programme, "The Site-Ready Engineer" (12 weeks, ₹24,999).
  - A table of 6 courses with audience, duration and fee.
  - 3 audience cards: students, engineers, homeowners.
- **Layout and motif:** a field-colour band with a table.
- **⚠️ All course names, durations and fees are invented placeholders.** The live site only lists these topics:
  - Civil engineering software
  - Estimation, BOQ and valuation to bank standards
  - Site engineer training, basic and advanced
  - Subject tutoring for Diploma, BE and M.Tech
  - Material testing (soil and others)
- **To do:**
  - Get the real course list from the client.
  - The table should cover the 5 live topics at minimum. Tutoring and software are missing from it right now.
  - Do not publish prices until the client confirms them.

## 7. Who we are ✅ *(new section, `#who`)*
- **Job:** trust. An older, traditional client and older homebuyers want to see **real people and a real history**. The redesign currently has no About or team content at all.
- **Content from the live About page:**
  - **Story (3 lines):** founded in 2018 in Chikmagalur, where coffee was first grown in India. The family has been in construction for 3 decades. The firm started with aerated concrete wall panels and became a full civil engineering service in 2019. Head office in Chikmagalur, branch in Bangalore.
  - **Team (8):**
    - Prajna Ganapathy P (Administrator)
    - Sri Rama Rao T A (Technical Head)
    - Raghavendra J (Financial & Real Estate Advisor)
    - Usha H J (Manager, Electrical)
    - Shruthi L C (Manager, Plumbing)
    - Sridevi S Bhat (Architect & Interior Designer)
    - Madhan N R (Site Engineer)
    - Sagar Naik B S (Site Engineer)
  - **Quote:** Sir M. Visvesvaraya. It fits the Karnataka-rooted concept perfectly, since he is the region's own engineering icon. Paraphrase or shorten it.
- **Layout and motif:** a new layout family, the **inscription frieze**, on a dark soapstone background:
  - A 3-figure band: 2018 · 30 years · 2 offices.
  - 8 carved plaques with Kannada numerals ೧–೮, in a 4-column grid that drops to 2 columns on tablet and mobile.
  - The Visvesvaraya quote inside a large arched temple niche.
- **Placement:** after Notes (§9), straight before Contact, so the trust content sits right above the form.
- **Still open:** team photos (optional) and the client's OK to show names (see question 4).

## 8. Projects 🟡
- **Job:** show real, local work.
- **Content now:** only 2 arched frames (Mahalakshmi Temple and Vistara County Resort), drawn as line art.
- **Content on the live site:** 8 completed projects and 3 ongoing ones, each with photo galleries.

  | Project | Type | Note |
  |---|---|---|
  | Mahalakshmi Temple, Chikmagalur | Building | — |
  | Vistara County Resort, Chikmagalur | Building | — |
  | Aura Homestay, Chikmagalur | Building | about 3,500 sq ft, 5 guest rooms |
  | Sai Angels School, Chikmagalur | Concrete wall | — |
  | St Mary's School, Chikmagalur | Concrete wall | — |
  | VCNR Group, Nelamangala | Concrete wall | — |
  | P K Ganapathy godown and labour shed, Somwarpet | Concrete wall | — |
  | Hosur project | Concrete wall | — |
  | MRF Showroom, I G Road, Chikmagalur | **Ongoing** | — |
  | Residence at Mudigere | **Ongoing** | — |
  | Commercial building, T C Palya, Bangalore | **Ongoing** | — |

- **Layout and motif:** arched frames.
- **To do:**
  - Show 6 arches: 3 buildings and 3 walls. Put the ongoing projects in an "Under construction now" strip.
  - Use the client's real photos from `wp-content/uploads/2018/06` and `2020/07`, saved locally, in WebP, with `loading="lazy"`.
  - Skip filter tabs. With 11 projects a plain grid is enough.

## 9. Podcast, blog and videos 🟡
- **Job:** show that the firm teaches, which feeds the Academy.
- **Content:** 3 note cards (Podcast, Blog, YouTube). All of them link to `#` right now.
- **Real content that exists:**
  - **Podcast:** "Civil Engineering Made Simple" by Sri Rama Rao. *No episodes yet.* Label the card "Coming soon" or drop it.
  - **Blog:** 2 posts from July 2020, "How to hire a structural designer for a project" and a personal post. Link the first one only.
  - **YouTube:** the channel URL is needed from the client.
- **To do:** use real URLs, or remove any card that has nothing behind it. A dead "Podcast" link costs more trust than leaving the card out.

## 10. Contact: "Let us build it together" 🟡
- **Job:** collect call-back requests. This is goal #1.
- **Content:** a contact list (phone, WhatsApp, email, office) and social icons, next to a form: name, phone, "I need help with" (8 options), message.
- **Layout and motif:** form.
- **Done:** filled in from the live site:
  - Phone: +91 99864 70846
  - Email: info@manidhay.com
  - Head office: Basavanahalli, Chikmagalur 577101, linked to Google Maps
  - Branch: Bangalore
  - Facebook
  - JSON-LD: address, phone, email and founding date
- **Still placeholder:**
  - WhatsApp number (ask whether it's the same as the phone).
  - Bangalore street address.
  - YouTube link.
- **Social:** the JSON-LD `sameAs` points to personal Twitter and LinkedIn accounts. Confirm with the client whether the firm wants those, or company pages instead.
- **To do:**
  - **Form backend.** The lightest option is Formspree, Web3Forms or Netlify Forms, posting to info@manidhay.com.
  - Phone is already the only required contact field. That's correct for this audience; keep it.

## 11. Footer ✅
- **Content:**
  - The elephant procession, back as the foundation.
  - "ಧನ್ಯವಾದಗಳು".
  - Link columns: Services, Academy, Contact.
  - © line and Back to top.
- **Done:** head office address, phone, email, Facebook and a "Who we are" link.
- **To do:**
  - Point the "Podcast" and "Blog" links to the same real URLs as §9.

---

## Site-wide requirements
- **Redirects.** The old site ranks for its existing URLs. Send each one to the matching anchor with a 301 redirect so search ranking isn't lost:
  - `/about/` → `/#who`
  - `/services/` → `/#services`
  - `/projects/` and `/projects/*` → `/#projects`
  - `/contact/` → `/#contact`
  - `/podcasts/` and `/blog/` → `/#notes` (or the posts kept on a blog host)
- **Old blog post.** Keep "How to hire a structural designer" live at its old URL if possible. It's the site's only real article.
- **Drop:**
  - AdSense, OneSignal, the duplicate Universal Analytics tags, jQuery and the WordPress plugins.
  - Keep one GA4 tag only if the client reads it.
- **Accessibility:**
  - Allow pinch-zoom. The old site blocked it; the new viewport tag is already correct.
  - Keep body text at 18 px.
  - Respect `prefers-reduced-motion`. This is done (the elephants stop).
  - Every Kannada word sits next to its English meaning.
- **Fixes the old site needs if it stays up meanwhile:**
  - 404s at `/about-us/` and `/contact-us/`.
  - Lorem-ipsum blocks on the Services page.
  - The raw `[manidhay …]` shortcode on the Contact page.

## Open questions for the client
1. Real Academy courses, durations and fees. Can prices be shown?
2. Does the firm do land conversion and completion certificates (the Approvals card)?
3. WhatsApp number, Bangalore branch address and YouTube/Instagram URLs.
4. May team names (and photos) appear on the site?
5. Which logo: the existing round badge or the new mark?
6. Is the podcast still planned? If not, drop it.
