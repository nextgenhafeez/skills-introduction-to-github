import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useLoading } from '../context/LoadingContext'

const name = 'ABDUL HAFEEZ'

export function Preloader() {
  const { isLoaded, setLoaded } = useLoading()
  const [progress, setProgress] = useState(0)
  const [phase, setPhase] = useState<'loading' | 'revealing' | 'done'>('loading')
  const hasStarted = useRef(false)

  useEffect(() => {
    if (hasStarted.current) return
    hasStarted.current = true

    // Preload critical assets
    const images = ['/pose-wave.png', '/pose-neutral.png', '/character-desk.png']
    const imagePromises = images.map(
      (src) =>
        new Promise<void>((resolve) => {
          const img = new Image()
          img.onload = () => resolve()
          img.onerror = () => resolve()
          img.src = src
        })
    )

    const fontPromise = document.fonts?.ready || Promise.resolve()

    // Animate progress counter
    let current = 0
    const interval = setInterval(() => {
      current += Math.random() * 12
      if (current >= 90) current = 90
      setProgress(Math.floor(current))
    }, 80)

    Promise.all([...imagePromises, fontPromise]).then(() => {
      clearInterval(interval)
      // Rapidly finish to 100
      let final = 90
      const finishInterval = setInterval(() => {
        final += 4
        if (final >= 100) {
          final = 100
          clearInterval(finishInterval)
          setProgress(100)
          setTimeout(() => setPhase('revealing'), 300)
          setTimeout(() => {
            setPhase('done')
            setLoaded()
          }, 1400)
        }
        setProgress(Math.floor(final))
      }, 30)
    })

    return () => clearInterval(interval)
  }, [setLoaded])

  return (
    <AnimatePresence>
      {phase !== 'done' && (
        <motion.div
          className="fixed inset-0 z-[100] bg-[#020202] flex flex-col items-center justify-center overflow-hidden"
          exit={{ clipPath: 'inset(0 0 100% 0)' }}
          transition={{ duration: 0.8, ease: [0.76, 0, 0.24, 1] }}
        >
          {/* Background grid */}
          <div className="absolute inset-0 opacity-[0.03]" style={{
            backgroundImage: 'linear-gradient(rgba(168,85,247,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(168,85,247,0.3) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }} />

          {/* Glow */}
          <div className="absolute w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-[120px]" />

          {/* Name letters */}
          <div className="relative flex gap-[2px] md:gap-1 mb-12 overflow-hidden">
            {name.split('').map((char, i) => (
              <motion.span
                key={i}
                className="text-4xl md:text-7xl font-display font-bold text-white/90"
                initial={{ y: 80, opacity: 0 }}
                animate={
                  phase === 'revealing'
                    ? { y: -120, opacity: 0, transition: { delay: i * 0.03, duration: 0.5, ease: [0.76, 0, 0.24, 1] } }
                    : { y: 0, opacity: 1, transition: { delay: 0.2 + i * 0.04, duration: 0.6, ease: [0.22, 1, 0.36, 1] } }
                }
              >
                {char === ' ' ? '\u00A0' : char}
              </motion.span>
            ))}
          </div>

          {/* Progress bar */}
          <div className="relative w-48 h-[1px] bg-white/10 overflow-hidden">
            <motion.div
              className="absolute left-0 top-0 h-full bg-purple-500"
              style={{ width: `${progress}%` }}
              transition={{ duration: 0.1 }}
            />
          </div>

          {/* Progress number */}
          <motion.p
            className="mt-6 text-xs font-mono tracking-[0.3em] text-white/30"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {progress}%
          </motion.p>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
