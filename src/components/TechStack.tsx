import { Canvas, useFrame } from '@react-three/fiber'
import { Stars } from '@react-three/drei'
import { motion } from 'framer-motion'
import { Suspense, useRef } from 'react'
import * as THREE from 'three'
import { content } from '../data/content'
import { TextReveal } from './TextReveal'

function ParticleBackground() {
  const ref = useRef<THREE.Points>(null!)
  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 10
      ref.current.rotation.y -= delta / 15
    }
  })
  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Stars ref={ref} radius={50} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
    </group>
  )
}

export function TechStack() {
  return (
    <section id="tech" className="relative w-full min-h-screen py-24 md:py-32 bg-[#020202] border-t border-white/5 overflow-hidden">
      {/* 3D Background */}
      <div className="absolute inset-0 z-0 opacity-40">
        <Canvas>
          <Suspense fallback={null}>
            <ParticleBackground />
          </Suspense>
        </Canvas>
      </div>

      <div className="container relative z-10 mx-auto px-6 md:px-12">
        <div className="mb-16 md:mb-20">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-purple-500 mb-3">My Arsenal</p>
          <h3 className="text-4xl md:text-5xl lg:text-7xl font-display font-black uppercase tracking-tighter">
            <TextReveal text="Technology Stack" splitBy="word" stagger={0.08} />
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
          {content.techStack.map((category, idx) => (
            <motion.div
              key={category.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1, duration: 0.8 }}
              viewport={{ once: true }}
              className="p-6 md:p-8 border border-white/10 rounded-[32px] bg-white/[0.02] backdrop-blur-md hover:bg-white/[0.04] transition-colors group relative overflow-hidden"
            >
              <div className="absolute -inset-20 bg-gradient-to-tr from-purple-500/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 blur-3xl pointer-events-none" />

              <h4 className="text-xl md:text-2xl font-display font-bold mb-6 text-white">{category.title}</h4>
              <div className="flex flex-wrap gap-3 relative z-10">
                {category.skills.map((skill, i) => (
                  <motion.span
                    key={skill}
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: idx * 0.1 + i * 0.05 }}
                    className="px-4 py-2 text-sm font-medium text-gray-300 border border-white/10 rounded-full bg-black/50 hover:border-purple-500/50 hover:text-purple-300 backdrop-blur-sm transition-all cursor-default"
                  >
                    {skill}
                  </motion.span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
