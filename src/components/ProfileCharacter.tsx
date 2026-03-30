import { useRef, useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useLoading } from '../context/LoadingContext'

const base = import.meta.env.BASE_URL
const poses = [`${base}pose-wave.png`, `${base}pose-neutral.png`]

export function ProfileCharacter() {
  const containerRef = useRef<HTMLDivElement>(null)
  const [currentPose, setCurrentPose] = useState(0)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [smoothPos, setSmoothPos] = useState({ x: 0, y: 0 })
  const rafRef = useRef<number>()
  const { isLoaded } = useLoading()

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPose((prev) => (prev + 1) % poses.length)
    }, 1200)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth) * 2 - 1
      const y = (e.clientY / window.innerHeight) * 2 - 1
      setMousePos({ x, y })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  useEffect(() => {
    const lerp = (start: number, end: number, factor: number) => start + (end - start) * factor
    const animate = () => {
      setSmoothPos((prev) => ({
        x: lerp(prev.x, mousePos.x, 0.08),
        y: lerp(prev.y, mousePos.y, 0.08),
      }))
      rafRef.current = requestAnimationFrame(animate)
    }
    rafRef.current = requestAnimationFrame(animate)
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [mousePos])

  const rotateY = smoothPos.x * 20
  const rotateX = smoothPos.y * -8
  const translateX = smoothPos.x * 40
  const translateY = smoothPos.y * 15
  const glowTranslateX = smoothPos.x * 60
  const glowTranslateY = smoothPos.y * 40

  return (
    <motion.div
      ref={containerRef}
      className="relative h-full w-full flex items-center justify-center overflow-visible"
      style={{ perspective: '1000px' }}
      initial={{ scale: 0.8, opacity: 0 }}
      animate={isLoaded ? { scale: 1, opacity: 1 } : { scale: 0.8, opacity: 0 }}
      transition={{ duration: 1.2, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
    >
      {/* Floating particles */}
      {[...Array(14)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full pointer-events-none z-0"
          style={{
            width: 2 + Math.random() * 5,
            height: 2 + Math.random() * 5,
            background: ['#a855f7', '#6366f1', '#818cf8', '#c084fc', '#7c3aed', '#4f46e5'][i % 6],
            left: `${5 + Math.random() * 90}%`,
            top: `${5 + Math.random() * 90}%`,
          }}
          animate={{
            y: [0, -60 - Math.random() * 80, 0],
            x: [0, 30 - Math.random() * 60, 0],
            opacity: [0.0, 0.6, 0.0],
            scale: [0.2, 2, 0.2],
          }}
          transition={{
            duration: 4 + Math.random() * 5,
            repeat: Infinity,
            delay: Math.random() * 5,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Large ambient glow */}
      <div
        className="absolute pointer-events-none z-0"
        style={{
          width: 500, height: 500,
          background: 'radial-gradient(circle, rgba(139,92,246,0.25) 0%, rgba(99,102,241,0.08) 45%, transparent 70%)',
          transform: `translate(${glowTranslateX}px, ${glowTranslateY}px)`,
          filter: 'blur(80px)',
          transition: 'transform 0.1s ease-out',
        }}
      />

      {/* Orbiting ring */}
      <motion.div
        className="absolute w-[380px] h-[480px] md:w-[440px] md:h-[540px] border border-purple-500/[0.06] rounded-full pointer-events-none z-0"
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
      >
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-purple-500 rounded-full shadow-[0_0_14px_rgba(168,85,247,0.9)]" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-1.5 h-1.5 bg-indigo-400 rounded-full shadow-[0_0_10px_rgba(129,140,248,0.7)]" />
      </motion.div>

      {/* Counter-rotating ring */}
      <motion.div
        className="absolute w-[320px] h-[420px] md:w-[380px] md:h-[480px] border border-indigo-500/[0.04] rounded-full pointer-events-none z-0"
        animate={{ rotate: -360 }}
        transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
      >
        <div className="absolute right-0 top-1/2 translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-purple-300 rounded-full shadow-[0_0_8px_rgba(216,180,254,0.5)]" />
      </motion.div>

      {/* Character with mouse parallax */}
      <div
        className="relative z-10"
        style={{
          transform: `perspective(1000px) rotateY(${rotateY}deg) rotateX(${rotateX}deg) translate(${translateX}px, ${translateY}px)`,
          transition: 'transform 0.05s ease-out',
          transformStyle: 'preserve-3d',
        }}
      >
        <motion.div
          animate={{ y: [0, -12, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          className="relative"
        >
          <AnimatePresence mode="wait">
            <motion.img
              key={currentPose}
              src={poses[currentPose]}
              alt="Abdul Hafeez 3D Character"
              className="w-[220px] sm:w-[300px] md:w-[380px] lg:w-[440px] h-auto"
              style={{
                filter: 'drop-shadow(0 30px 60px rgba(139,92,246,0.2))',
                mixBlendMode: 'lighten' as const,
              }}
              initial={{ opacity: 0.5 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0.5 }}
              transition={{ duration: 0.15 }}
            />
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Ground glow */}
      <div
        className="absolute bottom-[6%] w-[220px] h-[24px] rounded-full pointer-events-none z-0"
        style={{
          background: 'radial-gradient(ellipse, rgba(139,92,246,0.12) 0%, transparent 70%)',
          filter: 'blur(12px)',
          transform: `translateX(${smoothPos.x * 20}px)`,
        }}
      />
    </motion.div>
  )
}
