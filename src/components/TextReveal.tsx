import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

interface TextRevealProps {
  text: string
  className?: string
  delay?: number
  stagger?: number
  direction?: 'up' | 'down'
  once?: boolean
  splitBy?: 'char' | 'word'
}

export function TextReveal({
  text,
  className = '',
  delay = 0,
  stagger = 0.03,
  direction = 'up',
  once = true,
  splitBy = 'char',
}: TextRevealProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once, margin: '-10% 0px' })

  const items = splitBy === 'char'
    ? text.split('').map((char) => (char === ' ' ? '\u00A0' : char))
    : text.split(' ')

  const y = direction === 'up' ? 60 : -60

  return (
    <span ref={ref} className={`inline-flex flex-wrap ${className}`} aria-label={text}>
      {items.map((item, i) => (
        <span key={i} className="overflow-hidden inline-block">
          <motion.span
            className={`inline-block ${splitBy === 'word' ? 'mr-[0.3em]' : ''}`}
            initial={{ y, opacity: 0 }}
            animate={isInView ? { y: 0, opacity: 1 } : { y, opacity: 0 }}
            transition={{
              duration: 0.6,
              delay: delay + i * stagger,
              ease: [0.22, 1, 0.36, 1],
            }}
          >
            {item}
          </motion.span>
        </span>
      ))}
    </span>
  )
}

interface LineRevealProps {
  children: React.ReactNode
  className?: string
  delay?: number
  once?: boolean
}

export function LineReveal({ children, className = '', delay = 0, once = true }: LineRevealProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once, margin: '-5% 0px' })

  return (
    <div ref={ref} className={`overflow-hidden ${className}`}>
      <motion.div
        initial={{ y: '100%', opacity: 0 }}
        animate={isInView ? { y: '0%', opacity: 1 } : { y: '100%', opacity: 0 }}
        transition={{ duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </motion.div>
    </div>
  )
}
