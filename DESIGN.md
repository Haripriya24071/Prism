# PRISM — Design System

> No AI slop. No template UI. Every decision is intentional.

---

## Design Philosophy

PRISM processes something complex and analytical — business intelligence. The UI shouldn't feel like a SaaS dashboard or a chatbot. It should feel like a **command center**. Dark, precise, alive with information. The kind of interface where serious decisions get made.

Three principles drive every decision:
1. **Information density without noise** — show everything that matters, hide everything that doesn't
2. **Motion with purpose** — every animation communicates system state, never decorates it
3. **Trust through transparency** — the UI doesn't hide how PRISM works; it shows the process in real time

---

## Colour Tokens

All colours are CSS custom properties. No hardcoded hex anywhere in component files.

```css
:root {
  /* Backgrounds */
  --color-void: #050A14;          /* Page background — near-black with blue undertone */
  --color-surface: #0C1524;       /* Card / panel background */
  --color-surface-raised: #112036; /* Elevated surfaces, dropdowns */
  --color-border: #1E3A5F;        /* Borders, dividers */
  --color-border-subtle: #142840; /* Subtle separators */

  /* Text */
  --color-text-primary: #E8F0FE;  /* Primary body text — cool white */
  --color-text-secondary: #7B9CC7; /* Secondary / supporting text */
  --color-text-muted: #3D5A80;    /* Disabled, placeholder — NOT for body text */

  /* Accent */
  --color-accent-signal: #4D9EFF;  /* Primary CTA, active states, links */
  --color-accent-glow: #1A6FD4;    /* Glow / shadow version of accent */

  /* Semantic */
  --color-success: #00D68F;
  --color-warning: #FFB020;
  --color-error: #FF4D4F;

  /* Agent Accent Colours — one per agent */
  --color-agent-vc: #7C3AED;          /* Violet — ambition */
  --color-agent-lean: #0EA5E9;        /* Blue — speed */
  --color-agent-cto: #10B981;         /* Green — stability */
  --color-agent-ux: #F59E0B;          /* Amber — warmth */
  --color-agent-regulator: #6366F1;   /* Indigo — authority */
  --color-agent-adversarial: #EF4444; /* Red — threat */

  /* Risk colours (heatmap) */
  --color-risk-high: #FF4D4F;
  --color-risk-medium: #FFB020;
  --color-risk-low: #00D68F;
}
```

**Verified contrast pairs (WCAG 2.1 AA):**
| Text | Background | Ratio |
|------|-----------|-------|
| `--color-text-primary` | `--color-void` | 16.8:1 ✓ |
| `--color-text-primary` | `--color-surface` | 14.2:1 ✓ |
| `--color-text-secondary` | `--color-void` | 5.1:1 ✓ |
| `--color-success` | `--color-surface` | 7.3:1 ✓ |
| `--color-error` | `--color-surface` | 5.8:1 ✓ |

**Forbidden:** `--color-text-muted` on any background as body text. Use only for non-text UI.

---

## Typography

```css
:root {
  --font-display:  'Montserrat', system-ui, sans-serif;  /* Logo, titles, section headers, agent names */
  --font-body:     'DM Sans', system-ui, sans-serif;      /* Body text, chat, BRD content, UI labels, buttons */
  --font-tertiary: 'Sora', system-ui, sans-serif;         /* Scores, timestamps, tags, lineage chips, status labels */

  /* Scale */
  --text-display: 3rem;     /* Hero headline — PRISM logo mark */
  --text-h1: 2rem;          /* Page titles */
  --text-h2: 1.5rem;        /* Section headers */
  --text-h3: 1.125rem;      /* Card titles */
  --text-body: 1rem;        /* Default body */
  --text-small: 0.875rem;   /* Supporting text, labels */
  --text-micro: 0.75rem;    /* Tags, timestamps, metadata */
  --text-mono: 0.9rem;      /* Score numbers, session IDs */
}
```

---

## Spacing & Layout

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 24px;

  --border-width: 1px;
  --border-width-accent: 2px;
}
```

**Breakpoints (three only — no exceptions):**
```css
/* Mobile base: 0–767px */
/* Tablet: */
@media (min-width: 768px) { }
/* Desktop: */
@media (min-width: 1024px) { }
```

---

## Page Layout — The Three Phases

PRISM has three distinct UI phases. Each is a full page transition, not a modal or panel swap.

### Phase 1: Intake
```
┌─────────────────────────────────────┐
│         PRISM                       │  ← Montserrat, --text-display
│  One idea. Six perspectives.        │  ← Tagline, --color-text-secondary
│  One ground truth.                  │
│                                     │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│  │   [Voice Button] [Attach]   │    │  ← ChatBox
│  │   ________________________  │    │
│  │  | Type your idea here...│  │    │
│  │  |________________________| │    │
│  │                    [Send →] │    │
│  └─────────────────────────────┘    │
│                                     │
│  AI reply appears here inline       │
│  (follow-up questions, dynamic)     │
└─────────────────────────────────────┘
```

### Phase 2: Generation (Live)
```
┌──────────────────────────────────────────┐
│  Analysing your idea...   [████░░░░] 45% │
│                                          │
│  CONTEXT HARVESTED          ✓ Done       │
│  NewsAPI · World Bank · Crunchbase       │
│                                          │
│  ┌────────┐ ┌────────┐ ┌────────┐       │
│  │  VC    │ │  Lean  │ │  CTO   │       │  ← AgentGrid 3×2
│  │ ●●●    │ │  Done  │ │Waiting │       │     Each card shows
│  └────────┘ └────────┘ └────────┘       │     agent accent colour
│  ┌────────┐ ┌────────┐ ┌────────┐       │     + live status
│  │   UX   │ │  Reg.  │ │ Adver. │       │
│  │ Done   │ │ ●●●    │ │Waiting │       │
│  └────────┘ └────────┘ └────────┘       │
└──────────────────────────────────────────┘
```

### Phase 3: Results
```
┌──────────────────────────────────────────────┐
│  INVESTOR READINESS    74/100                │  ← Score ring (GSAP)
│  ████████████████░░░░                        │
│                                              │
│  DIVERGENCE HEATMAP                          │
│  Problem Statement   ████████░░  HIGH RISK   │  ← Heatmap bars
│  Functional Reqs     ██████████  LOW RISK    │     (GSAP scaleX)
│  Technical Reqs      █████░░░░░  MED RISK    │
│  Risk Register       ███░░░░░░░  HIGH RISK   │
│  Timeline            ████████░░  LOW RISK    │
│                                              │
│  ─────────────────────────────────────────   │
│  BUSINESS REQUIREMENTS DOCUMENT             │
│                                              │
│  [Problem Statement]                         │  ← BRD Viewer
│  Source: Lean Founder · Confidence: 89%      │     with lineage
│  ↳ Based on: World Bank ease-of-business     │     tags
│    rank 63 for target region                 │
│                                              │
│  [Download PDF ↓]  [Investor View]           │
│  [Tech View]       [Regulatory View]         │
└──────────────────────────────────────────────┘
```

---

## Animation System

### Framer Motion — Component-Level Transitions

```jsx
// Page transitions between the 3 phases
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] } },
  exit: { opacity: 0, y: -10, transition: { duration: 0.2 } }
};

// Agent card state transitions
const agentCardVariants = {
  pending: { opacity: 0.4, scale: 0.98 },
  running: { opacity: 1, scale: 1.02, transition: { duration: 0.3 } },
  complete: { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 300 } },
  failed: { opacity: 0.6, scale: 0.98 }
};

// BRD section reveals — staggered
const brdSectionVariants = {
  hidden: { opacity: 0, x: -16 },
  visible: (i) => ({
    opacity: 1, x: 0,
    transition: { delay: i * 0.12, duration: 0.35, ease: 'easeOut' }
  })
};
```

### GSAP — Complex Orchestrated Animations

```javascript
// Investor readiness score ring — counts up on reveal
gsap.to(scoreObj, {
  value: targetScore,
  duration: 1.8,
  ease: 'power2.out',
  onUpdate: () => {
    scoreDisplay.textContent = Math.round(scoreObj.value);
    // Update SVG stroke-dashoffset
    const offset = circumference - (scoreObj.value / 100) * circumference;
    scoreCircle.style.strokeDashoffset = offset;
  }
});

// Heatmap bars — scaleX from left, staggered
gsap.fromTo('.heatmap-bar-fill',
  { scaleX: 0, transformOrigin: 'left center' },
  {
    scaleX: 1,
    duration: 0.8,
    ease: 'power2.out',
    stagger: 0.1
  }
);

// Particle background — canvas, requestAnimationFrame only
// See RULES.md ARCH-011 for required cleanup pattern
```

### Animation Rules (enforced)
- `transform` + `opacity` only — never animate `width`, `height`, `top`, `left`
- All canvas animations: `requestAnimationFrame` — never `setInterval`
- `prefers-reduced-motion`: all animations disabled or reduced to opacity fade
- Agent card canvas neural net: `aria-hidden="true"` (decorative) or `role="img"` with `aria-label`

---

## Component Inventory

### ChatBox
- Textarea with `sr-only` label
- Voice button: pulsing red ring when recording (Framer Motion)
- Attach button: file picker (PDF, images, Word)
- AI replies appear as chat bubbles above input
- Send button disabled until min 1 character

### AgentGrid
- CSS Grid: 3 columns desktop, 2 tablet, 1 mobile
- Each card: `data-agent` attribute drives accent colour via CSS
- Status chip: colour + text label (never colour alone — WCAG 1.4.1)
- Running state: subtle pulse on border via CSS animation
- Canvas neural net per card (optional — skip if IDX performance is slow)

### DivergenceHeatmap
- 5 rows, one per BRD section
- Bar fills via GSAP `scaleX` on reveal
- `data-risk` attribute on row drives colour (high / medium / low)
- Tooltip on hover: "4 of 6 agents disagreed here"

### BRDViewer
- Accordion — sections expand on click
- Each section header: source agent chip + confidence score
- Lineage block below content: citation + data source
- Assumption flags: collapsible yellow callout below section
- Dissenting agents: collapsed "2 agents disagreed" expandable

### ScoreCard
- GSAP count-up animation on score number
- SVG circle with `stroke-dashoffset` animation
- Colour: green > 70, amber 50–70, red < 50
- Gap flags: bulleted below score
- Pivot suggestions: appear if score < 60, with projected score per pivot

---

## What PRISM Does NOT Look Like

- No gradients on gradients on gradients (Web3 slop)
- No glowing neon borders on everything
- No spinning loading animations — use skeleton states
- No card carousels with pagination for content that fits on screen
- No hero sections with stock photos of "diverse teams brainstorming"
- No Lottie files of robots thinking

The reference aesthetic: Linear, Vercel dashboard, Raycast. Dark, precise, fast.
