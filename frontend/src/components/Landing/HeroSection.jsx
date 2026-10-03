import { motion } from 'framer-motion'
import lineupImg from '../../assets/landing/prism_swarm_lineup.jpg'
import CircularStamp from './CircularStamp.jsx'

export default function HeroSection({ onStartClick }) {
  return (
    <section className="relative pt-6 pb-12" aria-label="Hero">
      {/* Top Paper Binder Clip / Tape Accent */}
      <div className="flex justify-center mb-6">
        <div className="w-16 h-3 bg-border rounded-sm shadow-sm flex items-center justify-center">
          <div className="w-8 h-1 bg-surface-raised rounded-full opacity-60"></div>
        </div>
      </div>

      {/* Main Hero Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Column: Editorial Headline & Subtitle */}
        <div className="lg:col-span-6 flex flex-col justify-center">
          {/* Swarm Badge */}
          <div className="inline-flex items-center gap-2 self-start px-3 py-1 rounded-full border border-border bg-surface font-tertiary text-micro font-semibold uppercase tracking-wider text-content-primary mb-4 shadow-[2px_2px_0px_var(--color-border)]">
            <span className="w-2 h-2 rounded-full bg-accent-signal animate-pulse"></span>
            Six-Agent Swarm Intelligence
          </div>

          {/* Main Headline */}
          <h1 className="font-display text-[2.5rem] sm:text-[3.25rem] lg:text-[3.5rem] font-black text-content-primary leading-[1.08] tracking-tight">
            Will your startup survive the 6-agent gauntlet?
          </h1>

          {/* Subtitle */}
          <p className="font-body text-content-secondary text-body sm:text-h3 mt-5 leading-relaxed">
            PRISM pits your startup idea against six adversarial AI personas with diametrically opposed incentives.
            We uncover unscalable architectures, fatal regulatory liabilities, and competitor kill-shots before you write a single line of code.
          </p>

          {/* Action Row with Circular Rotating Stamp */}
          <div className="mt-8 flex items-center gap-6">
            <CircularStamp onClick={onStartClick} />
            <div className="flex flex-col">
              <span className="font-display font-bold text-content-primary text-h3">
                No cheerleaders.
              </span>
              <span className="font-body text-small text-content-secondary">
                Brutal, objective venture validation in 90 seconds.
              </span>
              <button
                type="button"
                onClick={onStartClick}
                className="mt-2 text-left font-tertiary text-micro font-bold text-accent-signal hover:underline flex items-center gap-1"
              >
                Jump to Idea Intake <span>→</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Hero Lineup Illustration */}
        <div className="lg:col-span-6 flex flex-col items-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="w-full relative sketch-card p-3 sm:p-4 bg-surface border-2 border-border shadow-[6px_6px_0px_var(--color-border)]"
          >
            {/* Corner Stamp */}
            <div className="absolute -top-3 -right-3 px-3 py-1 bg-accent-signal text-surface border border-border rounded-md font-tertiary text-micro font-bold uppercase tracking-wider shadow-[2px_2px_0px_var(--color-border)] rotate-2 z-10">
              6 Personas
            </div>

            {/* Lineup Artwork */}
            <div className="rounded-md overflow-hidden border border-border-subtle bg-[#FAF7F2]">
              <img
                src={lineupImg}
                alt="PRISM 6-agent swarm lineup: VC, Bootstrapper, Enterprise CTO, UX Researcher, Policy Expert, and Adversarial Rival"
                className="w-full h-auto object-contain hover:scale-[1.02] transition-transform duration-300"
                loading="eager"
              />
            </div>

            {/* Inked Caption */}
            <div className="mt-3 pt-2 border-t border-border-subtle flex flex-wrap items-center justify-between gap-2 text-micro font-body text-content-secondary">
              <span className="italic">
                From left: Seed VC • Bootstrapper • CTO • UX Researcher • Regulator • Rival
              </span>
              <span className="font-tertiary font-semibold text-content-primary">
                ✦ Swarm Grounded
              </span>
            </div>
          </motion.div>
        </div>
      </div>

      {/* 3 Quick Value Badges */}
      <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t border-border-subtle">
        <div className="p-3 rounded-lg bg-surface border border-border-subtle flex items-start gap-3">
          <span className="text-xl">📊</span>
          <div>
            <div className="font-display font-bold text-small text-content-primary">Real Data Grounding</div>
            <div className="font-body text-micro text-content-secondary mt-0.5">Live market comps, World Bank macroeconomic data & regulatory feeds.</div>
          </div>
        </div>
        <div className="p-3 rounded-lg bg-surface border border-border-subtle flex items-start gap-3">
          <span className="text-xl">⚡</span>
          <div>
            <div className="font-display font-bold text-small text-content-primary">Adversarial Divergence</div>
            <div className="font-body text-micro text-content-secondary mt-0.5">Agents challenge each other&apos;s assumptions to expose fatal blindspots.</div>
          </div>
        </div>
        <div className="p-3 rounded-lg bg-surface border border-border-subtle flex items-start gap-3">
          <span className="text-xl">📑</span>
          <div>
            <div className="font-display font-bold text-small text-content-primary">Actionable BRD Output</div>
            <div className="font-body text-micro text-content-secondary mt-0.5">Synthesized Business Requirements Document with exportable PDF views.</div>
          </div>
        </div>
      </div>
    </section>
  )
}
