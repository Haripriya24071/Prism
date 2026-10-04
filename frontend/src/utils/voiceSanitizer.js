/**
 * voiceSanitizer.js — Smart voice AI transcript cleaner & autocorrect engine.
 * Strips vocal fillers (uh, um, ah, you know), eliminates stutter repetitions,
 * corrects tech/venture terminology, and formats proper sentence capitalization.
 */

// Regex patterns for verbal filler sounds
const FILLER_SOUNDS_REGEX = /\b(uh|um|umm|uhh|ah|ahh|er|err|hm|hmm|mhm)\b/gi

// Filler phrases when used as verbal crutches
const FILLER_PHRASES_REGEX = /\b(you know|like i mean|sort of|kind of|i mean like|basically like)\b/gi

// Business & Startup phonetic autocorrect dictionary
const DOMAIN_TERMS = [
  { pattern: /\b(health\s*care)\b/gi, replacement: 'Healthcare' },
  { pattern: /\b(fin\s*tech)\b/gi, replacement: 'FinTech' },
  { pattern: /\b(ed\s*tech)\b/gi, replacement: 'EdTech' },
  { pattern: /\b(b\s*to\s*b|b2\s*b)\b/gi, replacement: 'B2B' },
  { pattern: /\b(b\s*to\s*c|b2\s*c)\b/gi, replacement: 'B2C' },
  { pattern: /\b(s\s*a\s*a\s*s|sass|saas)\b/gi, replacement: 'SaaS' },
  { pattern: /\b(a\s*i)\b/gi, replacement: 'AI' },
  { pattern: /\b(a\s*p\s*i)\b/gi, replacement: 'API' },
  { pattern: /\b(m\s*v\s*p)\b/gi, replacement: 'MVP' },
  { pattern: /\b(a\s*r\s*r)\b/gi, replacement: 'ARR' },
  { pattern: /\b(m\s*r\s*r)\b/gi, replacement: 'MRR' },
  { pattern: /\b(i\s*o\s*t)\b/gi, replacement: 'IoT' },
  { pattern: /\b(l\s*l\s*m)\b/gi, replacement: 'LLM' },
  { pattern: /\b(united\s+states|u\s*s\s*a)\b/gi, replacement: 'US' },
  { pattern: /\b(united\s+kingdom|u\s*k)\b/gi, replacement: 'UK' },
  { pattern: /\b(u\s*a\s*e|emirates)\b/gi, replacement: 'UAE' },
]

/**
 * Removes vocal filler sounds and eliminates repeated stutter words.
 */
export function removeFillers(rawText) {
  if (!rawText) return ''

  let text = rawText
    // Remove filler sounds (uh, um, er, etc.)
    .replace(FILLER_SOUNDS_REGEX, '')
    // Remove common verbal crutches (you know, like I mean, etc.)
    .replace(FILLER_PHRASES_REGEX, '')
    .trim()

  // Remove sentence-starter filler crutches ("so basically", "basically", etc.)
  text = text.replace(/(^|[.?!]\s+)(so\s+)?(basically|literally)\s+/gi, '$1')

  // Remove stutter repetitions (e.g., "so so" -> "so", "we we" -> "we")
  text = text.replace(/\b(\w+)\s+\1\b/gi, '$1')

  return text
}

/**
 * Applies venture & tech autocorrect dictionary.
 */
export function applyDomainCorrections(text) {
  if (!text) return ''
  let result = text
  for (const { pattern, replacement } of DOMAIN_TERMS) {
    result = result.replace(pattern, replacement)
  }
  return result
}

/**
 * Auto-capitalizes sentences and fixes punctuation spacing.
 */
export function formatCapitalizationAndPunctuation(text) {
  if (!text) return ''

  // Collapse multiple spaces into one
  let cleaned = text.replace(/\s{2,}/g, ' ').trim()

  // Fix spacing before punctuation (e.g. "word ," -> "word,")
  cleaned = cleaned.replace(/\s+([.,!?;:])/g, '$1')

  // Capitalize the first letter of each sentence
  cleaned = cleaned.replace(/(^|[.!?]\s+)([a-z])/g, (_, boundary, char) => {
    return boundary + char.toUpperCase()
  })

  // Ensure first character overall is capitalized
  if (cleaned.length > 0) {
    cleaned = cleaned.charAt(0).toUpperCase() + cleaned.slice(1)
  }

  return cleaned
}

/**
 * Primary Voice AI Sanitizer — runs on spoken transcripts in real-time.
 */
export function sanitizeVoiceInput(rawText) {
  if (!rawText || typeof rawText !== 'string') return ''

  // 1. Remove vocal fillers and stutters
  const withoutFillers = removeFillers(rawText)

  // 2. Correct venture terms and acronyms
  const withCorrections = applyDomainCorrections(withoutFillers)

  // 3. Format capitalization, spacing, and punctuation
  return formatCapitalizationAndPunctuation(withCorrections)
}
