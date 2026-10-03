export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'Idea Intake & Scoping',
      desc: 'Pitch your startup thesis in plain language, voice dictation, or upload a pitch deck. PRISM extracts industry, stage, budget, and success criteria.',
      icon: '💡',
    },
    {
      num: '02',
      title: 'Context Harvesting & Swarm Gauntlet',
      desc: 'Macroeconomic data, Crunchbase comps, and regulatory registries are harvested. All 6 autonomous agents evaluate your venture in parallel.',
      icon: '🐝',
    },
    {
      num: '03',
      title: 'Consolidated BRD & Divergence Matrix',
      desc: 'PRISM scores cross-agent divergence, highlights unaddressed kill-shots, and delivers an exhaustive, role-tailored Business Requirements Document.',
      icon: '📊',
    },
  ]

  return (
    <section id="how-it-works" className="my-16 scroll-mt-24" aria-labelledby="how-it-works-heading">
      <div className="text-center max-w-2xl mx-auto mb-10">
        <div className="inline-block px-3 py-1 rounded-full border border-border bg-surface-raised font-tertiary text-micro font-semibold uppercase tracking-widest text-content-secondary mb-3 shadow-[2px_2px_0px_var(--color-border)]">
          The 3-Step Engine
        </div>
        <h2 id="how-it-works-heading" className="font-display text-h1 sm:text-display font-extrabold text-content-primary">
          How PRISM Works
        </h2>
        <p className="font-body text-content-secondary text-body mt-2">
          From a raw 2-sentence concept to an enterprise-grade, stress-tested product requirements blueprint.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {steps.map((step) => (
          <div
            key={step.num}
            className="sketch-card p-6 bg-surface border-2 border-border shadow-[4px_4px_0px_var(--color-border)] relative flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl">{step.icon}</span>
                <span className="font-tertiary text-h2 font-black text-content-muted">
                  {step.num}
                </span>
              </div>
              <h3 className="font-display text-h3 font-bold text-content-primary mb-2">
                {step.title}
              </h3>
              <p className="font-body text-small text-content-secondary leading-relaxed">
                {step.desc}
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-border-subtle flex items-center gap-1.5 text-micro font-tertiary font-bold text-accent-signal uppercase tracking-wider">
              <span>Verified Step</span>
              <span>✓</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
