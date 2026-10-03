import { motion } from 'framer-motion'
import { getBrdSectionVariants } from '../../animations/variants.js'
import { AssumptionFlag } from './AssumptionFlag.jsx'
import { BRDSection } from './BRDSection.jsx'
import './BRDViewer.css'

export default function BRDViewer({ sections, assumptions = [] }) {
  const variants = getBrdSectionVariants()

  return (
    <div className="brd-viewer" aria-live="polite">
      {sections.map((section, index) => (
        <motion.div
          key={section.title}
          variants={variants}
          custom={index}
          initial="hidden"
          animate="visible"
        >
          <BRDSection
            title={section.title}
            content={section.content}
            lineage={section.lineage}
            dissentingAgents={section.dissentingAgents}
          />
        </motion.div>
      ))}

      {assumptions.length > 0 && (
        <section className="brd-viewer__assumptions" aria-label="Hidden assumptions">
          <h2 className="brd-viewer__assumptions-title">Hidden assumptions</h2>
          {assumptions.map((item) => (
            <AssumptionFlag
              key={item.text}
              text={item.text}
              confidenceLevel={item.confidenceLevel}
              evidence={item.evidence}
              recommendedAction={item.recommendedAction}
            />
          ))}
        </section>
      )}
    </div>
  )
}
