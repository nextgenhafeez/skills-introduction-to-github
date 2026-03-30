import { motion } from 'framer-motion'
import { MagneticButton } from './MagneticButton'

interface Project {
  id: string
  title: string
  description: string
  longDescription?: string
  tech: string[]
  featured?: boolean
  github?: string
  image?: string
  logo?: string
}

export function ProjectCard({ project, index }: { project: Project; index: number }) {
  const num = String(index + 1).padStart(2, '0')

  if (project.featured) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        className="col-span-1 md:col-span-2 lg:col-span-3 group relative p-5 sm:p-8 md:p-12 border border-white/10 rounded-[20px] sm:rounded-[32px] bg-white/[0.02] backdrop-blur-sm overflow-hidden hover:bg-white/[0.04] transition-all duration-500"
        data-cursor
      >
        {/* Hover glow */}
        <div className="absolute -inset-20 bg-gradient-to-tr from-purple-500/10 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 blur-3xl pointer-events-none" />

        <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <span className="text-5xl sm:text-[80px] md:text-[120px] font-display font-black leading-none text-white/[0.03] absolute -top-4 -left-2 select-none">
              {num}
            </span>
            <p className="text-xs font-bold uppercase tracking-[0.3em] text-purple-400 mb-3">Featured Project</p>
            <h3 className="text-2xl sm:text-3xl md:text-4xl font-display font-bold mb-3 sm:mb-4">{project.title}</h3>
            <p className="text-gray-400 text-base leading-relaxed mb-6">
              {project.longDescription || project.description}
            </p>
            <div className="flex flex-wrap gap-2 mb-8">
              {project.tech.map((t) => (
                <span key={t} className="px-3 py-1 text-xs font-medium text-purple-300 border border-purple-500/20 rounded-full bg-purple-500/5">
                  {t}
                </span>
              ))}
            </div>
            {project.github && (
              <MagneticButton strength={0.15}>
                <a
                  href={project.github}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 text-sm font-medium text-white/60 hover:text-white transition-colors group/link"
                >
                  View on GitHub
                  <svg className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </a>
              </MagneticButton>
            )}
          </div>
          <div className="flex items-center justify-center">
            {project.image ? (
              <div className="relative">
                {project.logo && (
                  <img
                    src={`${import.meta.env.BASE_URL}${project.logo}`}
                    alt={`${project.title} logo`}
                    className="absolute -top-6 -left-4 w-14 h-14 sm:w-16 sm:h-16 rounded-xl shadow-lg z-10 border border-white/10"
                  />
                )}
                <img
                  src={`${import.meta.env.BASE_URL}${project.image}`}
                  alt={`${project.title} preview`}
                  className="w-full max-w-[220px] sm:max-w-[240px] md:max-w-[260px] h-auto rounded-2xl border border-white/10 shadow-[0_20px_60px_rgba(0,0,0,0.5)]"
                />
              </div>
            ) : (
              <div className="w-full h-48 md:h-64 rounded-2xl bg-gradient-to-br from-purple-500/10 to-indigo-500/10 border border-white/5 flex items-center justify-center">
                <span className="text-6xl md:text-8xl font-display font-black text-white/[0.06]">{project.id.charAt(0).toUpperCase()}</span>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.7, delay: index * 0.1, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -8 }}
      className="group relative p-5 sm:p-8 border border-white/10 rounded-[20px] sm:rounded-[24px] bg-white/[0.02] backdrop-blur-sm overflow-hidden hover:bg-white/[0.04] hover:border-purple-500/20 transition-all duration-500"
      data-cursor
    >
      <div className="absolute -inset-20 bg-gradient-to-tr from-purple-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 blur-3xl pointer-events-none" />

      <div className="relative z-10">
        <span className="text-[60px] font-display font-black leading-none text-white/[0.03] absolute -top-2 -right-1 select-none">
          {num}
        </span>
        <h3 className="text-lg sm:text-xl font-display font-bold mb-3">{project.title}</h3>
        <p className="text-sm text-gray-400 leading-relaxed mb-6">{project.description}</p>
        <div className="flex flex-wrap gap-2 mb-6">
          {project.tech.map((t) => (
            <span key={t} className="px-2.5 py-1 text-xs font-medium text-purple-300 border border-purple-500/20 rounded-full bg-purple-500/5">
              {t}
            </span>
          ))}
        </div>
        {project.github && (
          <a
            href={project.github}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 text-xs font-medium text-white/40 hover:text-white transition-colors group/link"
          >
            View Project
            <svg className="w-3.5 h-3.5 group-hover/link:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        )}
      </div>
    </motion.div>
  )
}
