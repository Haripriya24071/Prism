import { prefersReducedMotion } from '../utils/motion.js'

const INSTANT = { duration: 0 }

export function getPageVariants() {
  if (!prefersReducedMotion()) {
    return {
      initial: { opacity: 0, y: 20 },
      animate: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] },
      },
      exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
    }
  }
  return {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: INSTANT },
    exit: { opacity: 0, transition: INSTANT },
  }
}

export function getAgentCardVariants() {
  if (!prefersReducedMotion()) {
    return {
      pending: { opacity: 0.4, scale: 0.98 },
      running: { opacity: 1, scale: 1.02 },
      complete: { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 300 } },
      failed: { opacity: 0.6, scale: 0.98 },
    }
  }
  return {
    pending: { opacity: 0.4, transition: INSTANT },
    running: { opacity: 1, transition: INSTANT },
    complete: { opacity: 1, transition: INSTANT },
    failed: { opacity: 0.6, transition: INSTANT },
  }
}

export function getBrdSectionVariants() {
  if (!prefersReducedMotion()) {
    return {
      hidden: { opacity: 0, x: -16 },
      visible: (index) => ({
        opacity: 1,
        x: 0,
        transition: { delay: index * 0.12, duration: 0.35 },
      }),
    }
  }
  return {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: INSTANT },
  }
}
