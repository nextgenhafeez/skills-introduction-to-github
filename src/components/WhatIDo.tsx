import { content } from '../data/content'
import { motion } from 'framer-motion'
import { TextReveal } from './TextReveal'

export function WhatIDo() {
  return (
    <section id="what-i-do" className="relative w-full min-h-screen border-t border-white/5 bg-[#050505] flex items-center overflow-hidden">
      <div className="container mx-auto px-6 md:px-12 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center h-full py-24 md:py-32">

        {/* Left: Vertical Text */}
        <div className="lg:col-span-1 relative h-[200px] lg:h-[600px] flex items-center">
          <h1 className="text-6xl md:text-8xl lg:text-[12rem] font-display font-black tracking-tighter uppercase leading-none opacity-[0.03] select-none lg:-rotate-90 whitespace-nowrap lg:absolute lg:left-[-10rem] lg:top-1/2 lg:-translate-y-1/2">
            WHAT I DO
          </h1>
        </div>

        {/* Center: Character at Desk */}
        <div className="lg:col-span-6 h-[400px] md:h-[700px] relative flex items-center justify-center">
          <div className="absolute w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-[100px] pointer-events-none" />

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
            className="relative z-10"
          >
            <motion.div
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            >
              <img
                src="/character-desk.png"
                alt="Abdul Hafeez coding at desk"
                className="w-[300px] md:w-[500px] lg:w-[550px] h-auto"
                style={{
                  filter: 'drop-shadow(0 30px 60px rgba(139,92,246,0.15))',
                  mixBlendMode: 'lighten' as const,
                }}
              />
            </motion.div>

            <motion.p
              className="text-center mt-4 text-xs font-bold uppercase tracking-[0.3em] text-purple-500/60"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
            >
              This is what I do every day
            </motion.p>
          </motion.div>
        </div>

        {/* Right: Skill Cards */}
        <div className="lg:col-span-5 flex flex-col gap-8">
          <SkillCard
            title="FRONTEND"
            subtitle="BUILDING INTERACTIVE UIS"
            description={content.whatIDo.frontend.description}
            skills={content.whatIDo.frontend.skills}
            color="purple"
            delay={0}
          />
          <SkillCard
            title="BACKEND"
            subtitle="SCALABLE SERVER ARCHITECTURE"
            description={content.whatIDo.backend.description}
            skills={content.whatIDo.backend.skills}
            color="blue"
            delay={0.15}
          />
        </div>
      </div>
    </section>
  )
}

function SkillCard({ title, subtitle, description, skills, color, delay }: { title: string; subtitle: string; description: string; skills: string[]; color: string; delay: number }) {
  const accentColor = color === 'purple' ? 'text-purple-400' : 'text-blue-400'
  const borderColor = color === 'purple' ? 'border-purple-500/20' : 'border-blue-500/20'

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.8, delay }}
      className={`relative p-8 border ${borderColor} rounded-[24px] bg-white/[0.02] backdrop-blur-sm overflow-hidden group hover:bg-white/[0.04] transition-colors`}
    >
      {/* Corner brackets */}
      <div className="absolute top-3 left-3 w-4 h-4 border-t border-l border-white/10" />
      <div className="absolute top-3 right-3 w-4 h-4 border-t border-r border-white/10" />
      <div className="absolute bottom-3 left-3 w-4 h-4 border-b border-l border-white/10" />
      <div className="absolute bottom-3 right-3 w-4 h-4 border-b border-r border-white/10" />

      <h3 className="text-3xl font-display font-black tracking-tight mb-1">{title}</h3>
      <p className={`text-xs font-bold uppercase tracking-[0.2em] ${accentColor} mb-4`}>{subtitle}</p>
      <p className="text-sm text-gray-400 italic leading-relaxed mb-6">{description}</p>

      <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500 mb-3">Skillset & Tools</p>
      <div className="flex flex-wrap gap-2">
        {skills.map((skill, i) => (
          <motion.span
            key={skill}
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: delay + 0.3 + i * 0.04 }}
            className="px-3 py-1 text-xs font-medium text-gray-300 border border-white/10 rounded-full bg-black/30 hover:border-purple-500/40 transition-colors"
          >
            {skill}
          </motion.span>
        ))}
      </div>
    </motion.div>
  )
}
