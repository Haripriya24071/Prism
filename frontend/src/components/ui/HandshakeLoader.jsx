import { motion } from 'framer-motion'

/**
 * HandshakeLoader — Bespoke hand-drawn loading & alignment card.
 * Faithfully matches the editorial doodle style:
 * Step number badge, "SWIPE <<<" status pill, "SELL IT ON THE RIGHT PLATFORM" headline,
 * authentic two-tone hand-drawn handshake emerging from portals, and floating metric badges.
 */
export default function HandshakeLoader({
  stageMessage = 'Aligning founder vision with audience & market reality...',
  progressPct = 45,
  stepNumber = '5',
  tagText = 'SWIPE <<<',
}) {
  return (
    <div className="w-full max-w-md mx-auto my-2 p-4 sm:p-5 bg-surface rounded-2xl border-2 border-border shadow-[4px_4px_0px_var(--color-border)] relative overflow-hidden select-none font-body">
      {/* Background ambient warm wash */}
      <div className="absolute inset-0 bg-gradient-to-b from-accent-signal/5 via-transparent to-surface-raised/40 pointer-events-none" />

      {/* Top Header Row: Step Number & Swipe / Swarm Tag */}
      <div className="flex items-center justify-between relative z-10 mb-2">
        {/* Step Badge */}
        <div className="w-8 h-8 rounded-full border-2 border-border flex items-center justify-center font-display font-black text-sm text-content-primary bg-surface shadow-[1.5px_1.5px_0px_var(--color-border)]">
          {stepNumber}
        </div>

        {/* Action / Mode Pill */}
        <div className="px-2.5 py-0.5 rounded-full border-2 border-border font-tertiary text-[11px] font-bold tracking-wider text-content-primary bg-surface flex items-center gap-1.5 shadow-[1.5px_1.5px_0px_var(--color-border)]">
          <span className="w-1.5 h-1.5 rounded-full bg-accent-signal animate-ping" />
          <span>{tagText}</span>
        </div>
      </div>

      {/* Headline & Subhead */}
      <div className="text-center relative z-10 mb-1">
        <h2 className="font-display text-base sm:text-lg font-black tracking-tight text-content-primary uppercase">
          Sell It On The Right Platform
        </h2>
        <p className="font-body text-[10px] sm:text-[11px] text-content-secondary tracking-wide font-semibold uppercase">
          (USE PLATFORMS THAT MATCH YOUR PRODUCT AND AUDIENCE)
        </p>
      </div>

      {/* SVG Canvas Container */}
      <div className="relative w-full max-w-[380px] mx-auto flex items-center justify-center py-1">
        <svg
          viewBox="0 0 500 320"
          className="w-full h-auto max-h-[210px] overflow-visible drop-shadow-sm"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* ── Floating Badges with Sinusoidal Float ── */}

          {/* Badge 1: Revenue ($) — Upper Left */}
          <motion.g
            animate={{
              y: [-4, 4, -4],
              rotate: [-3, 2, -3],
            }}
            transition={{
              duration: 3.2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            <circle cx="105" cy="65" r="18" fill="#FFFFFF" stroke="#18181B" strokeWidth="2.8" />
            <text x="105" y="72" textAnchor="middle" fill="#18181B" className="font-display font-black text-lg">
              $
            </text>
            <circle cx="138" cy="68" r="3.5" fill="#18181B" />
          </motion.g>

          {/* Badge 2: Heart (Audience Love) — Mid Left */}
          <motion.g
            animate={{
              y: [4, -4, 4],
              rotate: [2, -3, 2],
            }}
            transition={{
              duration: 2.8,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.3,
            }}
          >
            <circle cx="172" cy="105" r="16" fill="#FFFFFF" stroke="#18181B" strokeWidth="2.8" />
            <path
              d="M 172 111 C 168 107, 163 103, 163 99 C 163 96, 166 94, 169 94 C 171 94, 172 96, 172 97 C 172 96, 173 94, 175 94 C 178 94, 181 96, 181 99 C 181 103, 176 107, 172 111 Z"
              fill="#18181B"
            />
            <circle cx="194" cy="88" r="2.5" fill="#78716C" />
          </motion.g>

          {/* Badge 3: Margin / Percentage (%) — Upper Right */}
          <motion.g
            animate={{
              y: [-4, 5, -4],
              rotate: [3, -2, 3],
            }}
            transition={{
              duration: 3.5,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.2,
            }}
          >
            <circle cx="375" cy="75" r="18" fill="#FFFFFF" stroke="#18181B" strokeWidth="2.8" />
            <text x="375" y="81" textAnchor="middle" fill="#18181B" className="font-display font-black text-sm">
              %
            </text>
            <circle cx="348" cy="82" r="3.5" fill="#18181B" />
          </motion.g>

          {/* Badge 4: Growth Trend Arrow — Lower Left */}
          <motion.g
            animate={{
              y: [5, -5, 5],
              rotate: [-2, 3, -2],
            }}
            transition={{
              duration: 3.0,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.5,
            }}
          >
            <circle cx="152" cy="265" r="17" fill="#FFFFFF" stroke="#18181B" strokeWidth="2.8" />
            <path
              d="M 143 270 L 148 264 L 152 267 L 160 258"
              fill="none"
              stroke="#18181B"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M 155 258 L 160 258 L 160 263"
              fill="none"
              stroke="#18181B"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="172" cy="240" r="3.5" fill="#78716C" />
          </motion.g>

          {/* Badge 5: Verified Checkmark — Lower Right */}
          <motion.g
            animate={{
              y: [-5, 4, -5],
              rotate: [2, -3, 2],
            }}
            transition={{
              duration: 3.1,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.6,
            }}
          >
            <circle cx="362" cy="255" r="18" fill="#FFFFFF" stroke="#18181B" strokeWidth="2.8" />
            <path
              d="M 353 255 L 359 261 L 372 248"
              fill="none"
              stroke="#18181B"
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="392" cy="268" r="3" fill="#78716C" />
          </motion.g>

          {/* Ambient Stipples */}
          <circle cx="305" cy="245" r="3.5" fill="#18181B" />
          <circle cx="370" cy="110" r="3" fill="#78716C" />
          <circle cx="200" cy="250" r="2.5" fill="#78716C" />

          {/* ── Portals ── */}

          {/* Left Portal Opening */}
          <g id="portal-left">
            <path d="M 72 75 C 24 115, 20 205, 68 250 C 82 210, 84 120, 72 75 Z" fill="#18181B" />
            <path d="M 72 75 C 20 115, 16 205, 68 250" fill="none" stroke="#18181B" strokeWidth="4.5" strokeLinecap="round" />
            <path d="M 72 75 C 92 115, 94 205, 68 250" fill="none" stroke="#18181B" strokeWidth="4.5" strokeLinecap="round" />
          </g>

          {/* Right Portal Opening */}
          <g id="portal-right">
            <path d="M 428 75 C 476 115, 480 205, 432 250 C 418 210, 416 120, 428 75 Z" fill="#18181B" />
            <path d="M 428 75 C 480 115, 484 205, 432 250" fill="none" stroke="#18181B" strokeWidth="4.5" strokeLinecap="round" />
            <path d="M 428 75 C 408 115, 406 205, 432 250" fill="none" stroke="#18181B" strokeWidth="4.5" strokeLinecap="round" />
          </g>

          {/* Left Sleeve (White with Cuff & Button) */}
          <g id="sleeve-left">
            <path
              d="M 70 120 C 105 124, 138 128, 172 134 C 180 166, 176 198, 164 232 C 126 228, 92 218, 62 202 Z"
              fill="#FFFFFF"
              stroke="#18181B"
              strokeWidth="4.2"
              strokeLinejoin="round"
            />
            {/* Cuff stitch line */}
            <path
              d="M 158 135 C 166 166, 162 196, 152 228"
              fill="none"
              stroke="#18181B"
              strokeWidth="2.8"
              strokeLinecap="round"
            />
            {/* Cuff Button */}
            <circle cx="138" cy="214" r="5" fill="#18181B" />
          </g>

          {/* Right Sleeve (White with Texture Dashes) */}
          <g id="sleeve-right">
            <path
              d="M 430 120 C 395 124, 362 128, 328 134 C 320 166, 324 198, 336 232 C 374 228, 408 218, 438 202 Z"
              fill="#FFFFFF"
              stroke="#18181B"
              strokeWidth="4.2"
              strokeLinejoin="round"
            />
            {/* Cuff stitch line */}
            <path
              d="M 342 135 C 334 166, 338 196, 348 228"
              fill="none"
              stroke="#18181B"
              strokeWidth="2.8"
              strokeLinecap="round"
            />
            {/* Hand-drawn sleeve pattern dashes */}
            <line x1="372" y1="145" x2="386" y2="147" stroke="#18181B" strokeWidth="3.8" strokeLinecap="round" />
            <line x1="364" y1="178" x2="378" y2="180" stroke="#18181B" strokeWidth="3.8" strokeLinecap="round" />
            <line x1="404" y1="162" x2="414" y2="166" stroke="#18181B" strokeWidth="3.8" strokeLinecap="round" />
            <line x1="386" y1="220" x2="398" y2="218" stroke="#78716C" strokeWidth="3.2" strokeLinecap="round" />
          </g>

          {/* ── Handshake Assembly with Rhythmic Motion Pulse ── */}
          <motion.g
            animate={{
              scale: [1, 1.025, 1],
            }}
            transition={{
              duration: 2.0,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            style={{ transformOrigin: '250px 180px' }}
          >
            {/* Left Hand (Grey Shaded Tone) */}
            <g id="hand-grey">
              <path
                d="M 172 146 C 190 148, 206 151, 222 147 C 234 144, 244 149, 252 156 C 262 165, 274 170, 274 179 C 272 188, 264 196, 254 204 C 238 210, 212 208, 188 208 C 176 208, 168 210, 164 218 L 172 146 Z"
                fill="#B0BEC5"
                stroke="#18181B"
                strokeWidth="4.2"
                strokeLinejoin="round"
                strokeLinecap="round"
              />
              {/* Knuckle creases */}
              <path d="M 268 174 C 272 182, 269 190, 261 196" fill="none" stroke="#18181B" strokeWidth="3" strokeLinecap="round" />
              <path d="M 258 182 C 261 189, 258 196, 250 201" fill="none" stroke="#18181B" strokeWidth="2.5" strokeLinecap="round" />
            </g>

            {/* Right Hand & Clasping Grip (White Tone) */}
            <g id="hand-white">
              {/* Wrist contours */}
              <path d="M 328 146 C 306 150, 290 153, 274 154" fill="none" stroke="#18181B" strokeWidth="4.2" strokeLinecap="round" />
              <path d="M 336 218 C 310 216, 286 212, 266 204" fill="none" stroke="#18181B" strokeWidth="4.2" strokeLinecap="round" />

              {/* Wrist Stipples */}
              <circle cx="302" cy="178" r="3.5" fill="#18181B" />
              <circle cx="312" cy="166" r="3.5" fill="#18181B" />
              <circle cx="316" cy="190" r="3" fill="#18181B" />
              <circle cx="296" cy="194" r="2.5" fill="#18181B" />

              {/* Clasping White Thumb (Distinct hook over top of grey hand) */}
              <path
                d="M 274 154 C 262 143, 238 140, 226 150 C 216 160, 220 172, 232 176 C 244 179, 256 170, 268 174"
                fill="#FFFFFF"
                stroke="#18181B"
                strokeWidth="4.2"
                strokeLinejoin="round"
                strokeLinecap="round"
              />

              {/* 3 Clasping White Fingers (Wrapped underneath grey hand) */}
              {/* Finger 1 */}
              <path
                d="M 204 204 C 201 222, 214 228, 220 215 C 221 207, 221 200, 221 198"
                fill="#FFFFFF"
                stroke="#18181B"
                strokeWidth="3.8"
                strokeLinejoin="round"
                strokeLinecap="round"
              />
              {/* Finger 2 */}
              <path
                d="M 220 215 C 223 230, 236 232, 240 217 C 241 208, 241 200, 241 198"
                fill="#FFFFFF"
                stroke="#18181B"
                strokeWidth="3.8"
                strokeLinejoin="round"
                strokeLinecap="round"
              />
              {/* Finger 3 */}
              <path
                d="M 240 217 C 244 231, 257 230, 261 216 C 262 208, 262 200, 262 198"
                fill="#FFFFFF"
                stroke="#18181B"
                strokeWidth="3.8"
                strokeLinejoin="round"
                strokeLinecap="round"
              />
            </g>

            {/* Action Spark Rays Above Clasp */}
            <line x1="220" y1="132" x2="210" y2="117" stroke="#18181B" strokeWidth="4" strokeLinecap="round" />
            <line x1="243" y1="124" x2="245" y2="108" stroke="#18181B" strokeWidth="4" strokeLinecap="round" />
            <line x1="265" y1="132" x2="276" y2="117" stroke="#18181B" strokeWidth="4" strokeLinecap="round" />
          </motion.g>
        </svg>
      </div>

      {/* Dynamic Subtitle & Live Status Message */}
      <div className="relative z-10 text-center mt-1 pt-2.5 border-t border-border-subtle">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-surface-raised border border-border text-xs font-tertiary text-content-primary shadow-[1.5px_1.5px_0px_var(--color-border-subtle)]">
          <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
          <span className="font-semibold text-accent-signal">{stageMessage}</span>
        </div>

        {/* Subtle Progress Bar */}
        <div className="w-full max-w-[220px] mx-auto mt-2 h-1.5 bg-void rounded-full overflow-hidden border border-border-subtle">
          <motion.div
            className="h-full bg-gradient-to-r from-accent-signal to-success"
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(100, Math.max(10, progressPct))}%` }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          />
        </div>
      </div>
    </div>
  )
}
