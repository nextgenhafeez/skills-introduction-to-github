import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useSectionObserver } from '../hooks/useSectionObserver'
import { MagneticButton } from './MagneticButton'

const navLinks = [
  { label: 'About', href: '#about' },
  { label: 'Work', href: '#projects' },
  { label: 'Experience', href: '#experience' },
  { label: 'Contact', href: '#contact' },
]

export function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const sectionIds = useMemo(() => ['hero', 'about', 'projects', 'experience', 'contact'], [])
  const { activeSection, scrollProgress } = useSectionObserver(sectionIds)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [mobileOpen])

  return (
    <>
      {/* Scroll progress bar */}
      <div className="scroll-progress" style={{ transform: `scaleX(${scrollProgress})` }} />

      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.8, delay: 1.8, ease: [0.22, 1, 0.36, 1] }}
        className={`fixed top-0 left-0 w-full z-50 transition-all duration-500 ${
          scrolled ? 'bg-[#050505]/80 backdrop-blur-xl border-b border-white/5' : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 md:px-12 py-5 flex justify-between items-center">
          <MagneticButton strength={0.2}>
            <a href="#hero" className="group flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center text-white font-display font-bold text-sm group-hover:shadow-[0_0_20px_rgba(168,85,247,0.4)] transition-shadow">
                AH
              </div>
              <span className="hidden md:block text-sm font-display font-medium text-white/60 group-hover:text-white transition-colors">
                Abdul Hafeez
              </span>
            </a>
          </MagneticButton>

          <div className="hidden md:flex items-center gap-10">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className={`text-xs font-medium uppercase tracking-[0.2em] transition-all animated-underline ${
                  activeSection === link.href.slice(1) ? 'text-white' : 'text-white/40 hover:text-white'
                }`}
              >
                {link.label}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-6">
            <MagneticButton strength={0.2}>
              <a
                href="#contact"
                className="hidden md:flex items-center gap-2 px-5 py-2.5 text-xs font-bold uppercase tracking-[0.15em] border border-purple-500/30 rounded-full hover:bg-purple-500/10 hover:border-purple-500/60 transition-all"
              >
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                Let's Talk
              </a>
            </MagneticButton>

            <button
              className="md:hidden flex flex-col gap-1.5 w-8 h-8 items-center justify-center"
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Toggle menu"
            >
              <motion.span className="w-6 h-[2px] bg-white block" animate={mobileOpen ? { rotate: 45, y: 5 } : { rotate: 0, y: 0 }} transition={{ duration: 0.3 }} />
              <motion.span className="w-6 h-[2px] bg-white block" animate={mobileOpen ? { opacity: 0 } : { opacity: 1 }} transition={{ duration: 0.2 }} />
              <motion.span className="w-6 h-[2px] bg-white block" animate={mobileOpen ? { rotate: -45, y: -5 } : { rotate: 0, y: 0 }} transition={{ duration: 0.3 }} />
            </button>
          </div>
        </div>
      </motion.nav>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-40 bg-[#050505]/95 backdrop-blur-2xl flex flex-col items-center justify-center"
          >
            <nav className="flex flex-col items-center gap-8">
              {navLinks.map((link, i) => (
                <motion.a
                  key={link.label}
                  href={link.href}
                  className="text-3xl font-display font-bold text-white hover:text-purple-400 transition-colors"
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  transition={{ delay: i * 0.08, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                  onClick={() => setMobileOpen(false)}
                >
                  {link.label}
                </motion.a>
              ))}
              <motion.a
                href="#contact"
                className="mt-4 px-8 py-3 text-sm font-bold uppercase tracking-[0.15em] border border-purple-500/50 rounded-full hover:bg-purple-500/10 transition-all"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ delay: 0.35, duration: 0.5 }}
                onClick={() => setMobileOpen(false)}
              >
                Let's Talk
              </motion.a>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
