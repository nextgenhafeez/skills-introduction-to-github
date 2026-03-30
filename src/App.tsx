import { Suspense, lazy } from 'react'
import { ProjectCard } from './components/ProjectCard'
import { SkillBadge } from './components/SkillBadge'
import { Navbar } from './components/Navbar'
import { WhatIDo } from './components/WhatIDo'
import { Footer } from './components/Footer'
import { CustomCursor } from './components/CustomCursor'
import { Preloader } from './components/Preloader'
import { TextReveal, LineReveal } from './components/TextReveal'
import { MagneticButton } from './components/MagneticButton'
import { useLoading } from './context/LoadingContext'
import { content } from './data/content'
import { motion } from 'framer-motion'

const TechStack = lazy(() => import('./components/TechStack').then(m => ({ default: m.TechStack })))

function App() {
  const { isLoaded } = useLoading()

  return (
    <div className="min-h-screen bg-[#020202] text-white font-sans overflow-x-hidden grain-overlay">
      <Preloader />
      <CustomCursor />
      <Navbar />

      {/* ═══════════════════════ HERO ═══════════════════════ */}
      <section id="hero" className="relative w-full h-screen flex items-center justify-center overflow-hidden">
        {/* Glow backgrounds */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/20 blur-[150px] rounded-full z-0 pointer-events-none" />
        <div className="absolute top-1/2 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-blue-600/10 blur-[120px] rounded-full z-0 pointer-events-none" />

        {/* Grid overlay */}
        <div className="absolute inset-0 z-0 opacity-[0.03]" style={{
          backgroundImage: 'linear-gradient(rgba(168,85,247,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(168,85,247,0.4) 1px, transparent 1px)',
          backgroundSize: '80px 80px',
        }} />

        <div className="container mx-auto px-6 md:px-12 z-10 grid grid-cols-1 md:grid-cols-2 h-full items-center gap-8">
          {/* Left: Text */}
          <div className="flex flex-col items-start gap-2 order-2 md:order-1 text-left">
            <motion.p
              className="text-sm md:text-lg font-bold uppercase tracking-[0.3em] opacity-40 mb-2"
              initial={{ opacity: 0, y: 20 }}
              animate={isLoaded ? { opacity: 0.4, y: 0 } : {}}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              Hello! I'm
            </motion.p>

            <h1 className="font-display font-black leading-[0.9] tracking-[-0.04em]">
              <motion.span
                className="block text-6xl sm:text-7xl md:text-8xl lg:text-9xl xl:text-[11rem]"
                initial={{ opacity: 0, y: 60 }}
                animate={isLoaded ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.4, duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
              >
                ABDUL
              </motion.span>
              <motion.span
                className="block text-6xl sm:text-7xl md:text-8xl lg:text-9xl xl:text-[11rem]"
                initial={{ opacity: 0, y: 60 }}
                animate={isLoaded ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.55, duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
              >
                HAFEEZ
              </motion.span>
            </h1>

            <motion.div
              className="mt-4 md:mt-6 flex flex-col gap-3"
              initial={{ opacity: 0, y: 30 }}
              animate={isLoaded ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.9, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            >
              <p className="text-sm md:text-lg font-bold uppercase tracking-[0.3em] text-purple-500 typing-cursor">
                A Software Engineer
              </p>
              <div className="flex items-center gap-4 mt-1">
                <div className="h-[1px] w-8 bg-white/20" />
                <p className="text-xs md:text-sm uppercase tracking-[0.2em] text-white/30 font-medium">
                  Product Delivery &middot; AI Services &middot; Full Stack
                </p>
              </div>
            </motion.div>
          </div>

          {/* Right: 3D Character */}
          <motion.div
            className="relative flex items-center justify-center order-1 md:order-2 h-[45vh] md:h-[85vh]"
            initial={{ opacity: 0, scale: 0.85 }}
            animate={isLoaded ? { opacity: 1, scale: 1 } : {}}
            transition={{ delay: 0.5, duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
          >
            {/* Glow behind character */}
            <div className="absolute w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none" />

            {/* Orbiting ring */}
            <motion.div
              className="absolute w-[320px] h-[430px] md:w-[420px] md:h-[560px] lg:w-[480px] lg:h-[640px] border border-purple-500/[0.08] rounded-full pointer-events-none z-0"
              animate={{ rotate: 360 }}
              transition={{ duration: 28, repeat: Infinity, ease: 'linear' }}
            >
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-purple-500 rounded-full shadow-[0_0_14px_rgba(168,85,247,0.9)]" />
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-1.5 h-1.5 bg-indigo-400 rounded-full shadow-[0_0_10px_rgba(129,140,248,0.7)]" />
            </motion.div>

            {/* Counter ring */}
            <motion.div
              className="absolute w-[280px] h-[380px] md:w-[360px] md:h-[490px] lg:w-[410px] lg:h-[560px] border border-indigo-500/[0.05] rounded-full pointer-events-none z-0"
              animate={{ rotate: -360 }}
              transition={{ duration: 38, repeat: Infinity, ease: 'linear' }}
            >
              <div className="absolute right-0 top-1/2 translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-purple-300 rounded-full shadow-[0_0_8px_rgba(216,180,254,0.5)]" />
            </motion.div>

            {/* Character with float */}
            <motion.div
              animate={{ y: [0, -14, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              className="relative z-10"
            >
              <img
                src="/character-3d-clean.png"
                alt="Abdul Hafeez 3D Avatar"
                className="w-[280px] sm:w-[340px] md:w-[420px] lg:w-[500px] xl:w-[560px] h-auto"
                style={{
                  filter: 'drop-shadow(0 30px 60px rgba(139,92,246,0.35))',
                }}
              />
            </motion.div>

            {/* Ground shadow */}
            <div className="absolute bottom-[8%] w-[240px] h-[24px] rounded-full pointer-events-none z-0" style={{
              background: 'radial-gradient(ellipse, rgba(139,92,246,0.18) 0%, transparent 70%)',
              filter: 'blur(12px)',
            }} />
          </motion.div>
        </div>

        {/* Bottom: Socials & Resume */}
        <motion.div
          className="absolute bottom-8 md:bottom-12 left-6 md:left-12 z-20 flex items-center gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={isLoaded ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 1.8, duration: 0.8 }}
        >
          <MagneticButton strength={0.3}>
            <a href={content.contact.github} target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center opacity-60 hover:opacity-100 hover:border-purple-500/50 transition-all">
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.372 0 0 5.373 0 12c0 5.302 3.438 9.8 8.08 11.348.6.111.78-.261.78-.578v-2.185c-3.338.726-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.605-2.664-.305-5.466-1.332-5.466-5.93 0-1.31.468-2.38 1.235-3.22-.123-.303-.535-1.523.117-3.175 0 0 1.008-.322 3.3 1.23a11.5 11.5 0 0 1 3-.405c1.02.005 2.047.138 3 .405 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.24 2.872.118 3.175.77.84 1.235 1.911 1.235 3.22 0 4.61-2.805 5.62-5.475 5.92.43.37.817 1.102.817 2.221v3.293c0 .32.17.694.787.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>
            </a>
          </MagneticButton>
          <MagneticButton strength={0.3}>
            <a href={content.contact.linkedin} target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center opacity-60 hover:opacity-100 hover:border-purple-500/50 transition-all">
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
            </a>
          </MagneticButton>
        </motion.div>

        <motion.div
          className="absolute bottom-8 md:bottom-12 right-6 md:right-12 z-20"
          initial={{ opacity: 0, y: 20 }}
          animate={isLoaded ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 1.9, duration: 0.8 }}
        >
          <MagneticButton strength={0.2}>
            <a href="/resume.html" download="Abdul_Hafeez_Resume.html" className="flex items-center gap-2 text-xs font-bold tracking-widest opacity-60 hover:opacity-100 transition-all">
              <span>RESUME</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            </a>
          </MagneticButton>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 md:bottom-12 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-2"
          initial={{ opacity: 0 }}
          animate={isLoaded ? { opacity: 0.4 } : {}}
          transition={{ delay: 2.2, duration: 1 }}
        >
          <span className="text-[9px] tracking-[0.3em] uppercase">Scroll</span>
          <motion.div
            className="w-[1px] h-8 bg-white/30"
            animate={{ scaleY: [0, 1, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            style={{ transformOrigin: 'top' }}
          />
        </motion.div>
      </section>

      {/* ═══════════════════════ WHAT I DO ═══════════════════════ */}
      <WhatIDo />

      {/* ═══════════════════════ ABOUT ═══════════════════════ */}
      <section id="about" className="max-w-7xl mx-auto px-6 md:px-12 py-24 md:py-32 border-t border-white/5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-20 items-center">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
            <p className="text-xs font-bold uppercase tracking-[0.3em] text-purple-500 mb-3">Who I Am</p>
            <h2 className="text-3xl md:text-4xl font-display font-black uppercase tracking-tighter mb-8">
              <TextReveal text="About Me" splitBy="word" stagger={0.1} />
            </h2>
            <p className="text-lg md:text-xl text-gray-400 leading-relaxed font-light">
              {content.summary}
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="p-8 md:p-12 bg-white/[0.03] rounded-[40px] border border-white/10 backdrop-blur-sm"
          >
            <h3 className="text-xl md:text-2xl font-display font-bold mb-6">Technical Tools</h3>
            <div className="flex flex-wrap gap-3">
              {content.skills.map((skill, i) => (
                <SkillBadge key={skill} skill={skill} index={i} />
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ═══════════════════════ PROJECTS ═══════════════════════ */}
      <section id="projects" className="max-w-7xl mx-auto px-6 md:px-12 py-24 md:py-32 border-t border-white/5">
        <div className="mb-12 md:mb-16">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-purple-500 mb-3">Portfolio</p>
          <h2 className="text-3xl md:text-4xl font-display font-black uppercase tracking-tighter">
            <TextReveal text="Selected Work" splitBy="word" stagger={0.1} />
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {content.projects.map((project, i) => (
            <ProjectCard key={project.id} project={project} index={i} />
          ))}
        </div>
      </section>

      {/* ═══════════════════════ EXPERIENCE ═══════════════════════ */}
      <section id="experience" className="max-w-7xl mx-auto px-6 md:px-12 py-24 md:py-32 border-t border-white/5">
        {/* Large background text with parallax feel */}
        <motion.h2
          className="text-5xl md:text-8xl font-display font-black uppercase tracking-tighter mb-16 md:mb-20 opacity-[0.04] select-none"
          initial={{ x: 0 }}
          whileInView={{ x: -40 }}
          viewport={{ once: true }}
          transition={{ duration: 2, ease: 'easeOut' }}
        >
          My Career &<br />Experience
        </motion.h2>

        <div className="flex flex-col gap-8 md:gap-12 relative">
          {/* Animated timeline line */}
          <motion.div
            className="absolute left-[15px] top-0 bottom-0 w-[2px] bg-gradient-to-b from-purple-500/30 via-purple-500/10 to-transparent origin-top"
            initial={{ scaleY: 0 }}
            whileInView={{ scaleY: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.5, ease: [0.22, 1, 0.36, 1] }}
          />

          {content.experience.map((exp: any, i: number) => (
            <motion.div
              key={i}
              className="flex gap-6 md:gap-12 items-start group"
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            >
              {/* Timeline dot */}
              <motion.div
                className="w-8 h-8 rounded-full bg-[#050505] border-2 border-purple-500/50 z-10 shrink-0 group-hover:border-purple-500 group-hover:shadow-[0_0_15px_rgba(168,85,247,0.4)] transition-all duration-500"
                whileInView={{ scale: [0.5, 1.2, 1] }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 + 0.3, duration: 0.5 }}
              />

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8 w-full p-6 md:p-8 border border-white/5 rounded-3xl bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/10 transition-all duration-500">
                <div className="flex flex-col gap-2">
                  <h3 className="text-xl md:text-2xl font-display font-bold">{exp.role}</h3>
                  <p className="text-purple-400 font-bold text-xs uppercase tracking-widest">{exp.company}</p>
                </div>
                <div className="text-2xl md:text-4xl font-display font-black opacity-20">{exp.period}</div>
                <p className="text-gray-400 text-sm leading-relaxed">{exp.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ═══════════════════════ TECH STACK ═══════════════════════ */}
      <Suspense fallback={<div className="h-screen" />}>
        <TechStack />
      </Suspense>

      {/* ═══════════════════════ CONTACT ═══════════════════════ */}
      <section id="contact" className="relative max-w-7xl mx-auto px-6 md:px-12 py-24 md:py-32 border-t border-white/5 text-center overflow-hidden">
        {/* Animated gradient orbs */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-1/3 left-1/3 w-[300px] h-[300px] bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />

        <div className="relative z-10">
          <motion.p
            className="text-xs font-bold uppercase tracking-[0.3em] text-purple-500 mb-4"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            Get In Touch
          </motion.p>

          <h2 className="text-4xl md:text-5xl lg:text-7xl font-display font-black tracking-tighter mb-8 uppercase">
            <TextReveal text="Let's build" splitBy="word" stagger={0.1} />
            <br />
            <span className="text-gradient">
              <TextReveal text="together" delay={0.3} />
            </span>
          </h2>

          <LineReveal delay={0.5}>
            <p className="text-gray-400 text-lg max-w-lg mx-auto mb-10">
              Open to software engineering, AI product, and full-stack roles where I can contribute fast and help ship meaningful work.
            </p>
          </LineReveal>

          <MagneticButton strength={0.15}>
            <a
              href={`mailto:${content.contact.email}`}
              className="inline-block text-xl md:text-2xl lg:text-3xl text-purple-400 font-light hover:text-white transition-all animated-underline pb-2"
            >
              {content.contact.email}
            </a>
          </MagneticButton>

          {/* Social row */}
          <motion.div
            className="flex justify-center gap-4 mt-12"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6 }}
          >
            <MagneticButton strength={0.3}>
              <a href={content.contact.github} target="_blank" rel="noreferrer" className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-purple-500/50 transition-all">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.372 0 0 5.373 0 12c0 5.302 3.438 9.8 8.08 11.348.6.111.78-.261.78-.578v-2.185c-3.338.726-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.605-2.664-.305-5.466-1.332-5.466-5.93 0-1.31.468-2.38 1.235-3.22-.123-.303-.535-1.523.117-3.175 0 0 1.008-.322 3.3 1.23a11.5 11.5 0 0 1 3-.405c1.02.005 2.047.138 3 .405 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.24 2.872.118 3.175.77.84 1.235 1.911 1.235 3.22 0 4.61-2.805 5.62-5.475 5.92.43.37.817 1.102.817 2.221v3.293c0 .32.17.694.787.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>
              </a>
            </MagneticButton>
            <MagneticButton strength={0.3}>
              <a href={content.contact.linkedin} target="_blank" rel="noreferrer" className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-purple-500/50 transition-all">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
              </a>
            </MagneticButton>
            <MagneticButton strength={0.3}>
              <a href={`mailto:${content.contact.email}`} className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-purple-500/50 transition-all">
                <svg className="w-5 h-5 fill-none stroke-current" viewBox="0 0 24 24" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" /></svg>
              </a>
            </MagneticButton>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export default App
