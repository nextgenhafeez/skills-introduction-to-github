import { motion } from 'framer-motion'

export function SkillBadge({ skill, index = 0 }: { skill: string; index?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.05, duration: 0.4 }}
      whileHover={{ scale: 1.08, rotate: 1 }}
      whileTap={{ scale: 0.95 }}
      className="px-4 py-2 sm:px-6 sm:py-3 text-sm sm:text-base font-medium transition-all border border-white/10 rounded-full bg-white/[0.03] backdrop-blur-md hover:border-purple-500/50 hover:shadow-[0_0_20px_rgba(168,85,247,0.15)] cursor-default relative overflow-hidden group"
    >
      {/* Shimmer on hover */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-500/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
      <span className="relative z-10">{skill}</span>
    </motion.div>
  )
}
