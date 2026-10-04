# PRISM — Design System & UI Specification

> No AI slop. No generic templates. Executive command-center precision.

---

## 1. Design Philosophy

PRISM transforms unstructured founder chaos into institutional-grade requirements. The interface is engineered as an **Executive Command Center** — sleek, dark, focused, and alive with information.

<p align="center">
  <img src="./docs/images/prism_swarm_lineup.jpg" alt="PRISM Swarm Lineup" width="100%" style="border-radius: 12px; border: 1px solid #1E3A5F;" />
</p>

### Core Principles
1. **Information Density without Clutter:** Surface critical intelligence immediately (lineage, citations, divergence, scores) while keeping navigation intuitive.
2. **Motion with Intent:** Animations exist to communicate system state and progress, never as superficial decoration.
3. **Radical Transparency:** The interface never hides the debate; it displays the tension between competing agent perspectives.

---

## 2. Color Palette & Design Tokens

All colors are defined as CSS custom properties in `tokens.css` / `src/index.css`. Hardcoded hex codes are strictly prohibited in component markup (UI-001).

```css
:root {
  /* Backgrounds */
  --color-void: #050A14;          /* Deepest page background */
  --color-surface: #0C1524;       /* Primary card and panel surface */
  --color-surface-raised: #112036; /* Elevated modals, dropdowns, popovers */
  --color-border: #1E3A5F;        /* Standard element border */
  --color-border-subtle: #142840; /* Subtle section dividers */

  /* Text & Typography */
  --color-text-primary: #E8F0FE;  /* High-contrast readable white */
  --color-text-secondary: #7B9CC7; /* Metadata, timestamps, descriptions */
  --color-text-muted: #3D5A80;    /* Disabled states, subtle placeholders */

  /* Accents & Signals */
  --color-accent-signal: #4D9EFF;  /* Primary interactive actions & links */
  --color-accent-glow: #1A6FD4;    /* Glowing focus rings & highlights */

  /* Semantic Alerts */
  --color-success: #00D68F;       /* High confidence, approved tests */
  --color-warning: #FFB020;       /* Medium risk, caution flags */
  --color-error: #FF4D4F;         /* Severe regulatory/technical risk */

  /* 6 Agent Persona Accents */
  --color-agent-vc: #7C3AED;          /* Violet — capital efficiency & scale */
  --color-agent-lean: #0EA5E9;        /* Sky Blue — speed & MVP simplicity */
  --color-agent-cto: #10B981;         /* Emerald — architectural resilience */
  --color-agent-ux: #F59E0B;          /* Amber — human-centered adoption */
  --color-agent-regulator: #6366F1;   /* Indigo — compliance & legal rigor */
  --color-agent-adversarial: #EF4444; /* Crimson — competitor destruction */

  /* Divergence Heatmap Risk */
  --color-risk-high: #FF4D4F;
  --color-risk-medium: #FFB020;
  --color-risk-low: #00D68F;
}
```

---

## 3. Loading Screens & Micro-Animations

### The "Market Alignment / Handshake Deal" Loader (`HandshakeLoader.jsx`)
During the swarm deliberation phase (when 6 agents are debating and market intelligence is being harvested), PRISM displays an iconic, stylized **Market Handshake Animation**.

<p align="center">
  <img src="./docs/images/handshake_loader.png" alt="PRISM Handshake Deal Loader" width="480" style="border-radius: 12px; border: 1px solid #1E3A5F;" />
</p>

#### Visual & Motion Behavior:
1. **The Portal Sleeves:** Two clean hand-drawn arms emerge from rounded spatial portals representing the Founder and the Market/Audience reaching an agreement.
2. **The Handshake Pulse:** A subtle, rhythmic micro-compression (`scale: [1, 1.03, 1]`) every 1.6s simulating a living partnership.
3. **Floating Financial & Trust Badges:** Five floating tokens orbit gently around the handshake using independent sinusoidal keyframe floats:
   - **`$` (Revenue / Monetization)**: Floats upper-left with slight tilt.
   - **`%` (Market Share / Margin)**: Floats upper-right.
   - **`♥` (User Retention / Passion)**: Hovers near the center-left.
   - **`✔` (Regulatory Compliance / Quality)**: Floats lower-right.
   - **`📈` (Growth Velocity)**: Bobbing bottom-center.
4. **Caption Typography:** Bold headline *"SELL IT ON THE RIGHT PLATFORM"* with sub-caption *"Aligning founder vision with audience reality"*.
5. **Accessibility / Reduced Motion:** When `prefers-reduced-motion` is active, animations settle into a crisp, static illustration with zero bobbing (UI-003).

---

## 4. Key Interactive Components

### 4.1 ChatBox (`src/components/ChatBox/`)
- Streamlined zero-friction conversational intake.
- Auto-growing textarea with `Shift+Enter` multi-line support.
- Visual microphone pulse indicator during Web Speech API voice capture.
- Drag-and-drop file upload zone with file-type chip badges (PDF, PNG, DOCX).

### 4.2 AgentGrid & Deliberation Cards (`src/components/AgentGrid/`)
<p align="center">
  <img src="./docs/images/generation_page_view.png" alt="PRISM Live Agent Deliberation Grid" width="100%" style="border-radius: 12px; border: 1px solid #1E3A5F;" />
</p>

- 6-card responsive CSS grid (3 cols desktop, 2 cols tablet, 1 col mobile).
- Each card features:
  - Archetype portrait thumbnail and persona mandate title.
  - Live status chip (`queued` &rarr; `running` &rarr; `complete` / `failed`) with pulsing activity ring.
  - Glowing border keyed to `--color-agent-{persona}`.
  - **Live Deliberation Thought Bubbles:** Displays in real time what the persona is actively arguing or critiquing.

### 4.3 Divergence Heatmap (`src/components/DivergenceHeatmap/`)
- 6 rows representing the BRD sections (Executive Summary, Market Analysis, Functional Requirements, Technical Requirements, Risk Register, Go-To-Market).
- Displays color-coded divergence bars from green (consensus, low risk) to red (sharp disagreement, high risk).
- Interactive tooltip explaining why the agents disagreed.

### 4.4 ScoreCard & ScoreRing (`src/components/ScoreCard/`)
- Animated SVG circle ring running a smooth GSAP count-up from 0 to final composite score (0-100).
- Dynamically shifts color token based on readiness band:
  - **Score ≥ 75:** High Confidence (Emerald Green)
  - **Score 55–74:** Conditional / Needs Polish (Amber Yellow)
  - **Score < 55:** Critical Risk / Pivot Triggered (Crimson Red)

### 4.5 BRDViewer (`src/components/BRDViewer/`)
- Accordion interface for exploring each section of the merged document.
- **Lineage Badge:** Clearly identifies which persona authored each section (`[LineageTag]`).
- **Source Citation Chips:** Clickable source citations (`[SOURCE: worldbank]`, `[SOURCE: newsapi]`) validating real-world data grounding.
- **Dissent Expander:** Toggle button to view conflicting points raised by other personas.
