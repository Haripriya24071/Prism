import { motion } from 'framer-motion'

export default function CircularStamp({ onClick, text = "✦ 6 COMPETING MINDS ✦ STRESS TEST YOUR VENTURE " }) {
  // SVG circular text stamp with rotating animation
  return (
    <motion.button
      type="button"
      onClick={onClick}
      aria-label="Scroll to idea intake"
      className="relative w-28 h-28 sm:w-32 sm:h-32 rounded-full cursor-pointer bg-border text-void flex items-center justify-center shadow-lg transition-transform hover:scale-105 active:scale-95 group focus:outline-none"
      whileHover={{ rotate: 15 }}
      transition={{ type: 'spring', stiffness: 300, damping: 15 }}
    >
      {/* Rotating outer ring of text */}
      <motion.svg
        viewBox="0 0 100 100"
        className="absolute inset-0 w-full h-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 18, ease: 'linear', repeat: Infinity }}
      >
        <path
          id="circlePath"
          d="M 50, 50 m -37, 0 a 37,37 0 1,1 74,0 a 37,37 0 1,1 -74,0"
          fill="none"
        />
        <text className="text-[7.5px] font-tertiary tracking-[0.22em] fill-void font-bold uppercase">
          <textPath href="#circlePath" startOffset="0%">
            {text}
          </textPath>
        </text>
      </motion.svg>

      {/* Center symbol with interactive hover */}
      <div className="relative z-10 flex flex-col items-center justify-center text-center">
        <span className="text-xl sm:text-2xl group-hover:scale-125 transition-transform duration-200">✦</span>
        <span className="text-[9px] font-display font-bold uppercase tracking-wider mt-0.5">Pitch</span>
      </div>
    </motion.button>
  )
}
