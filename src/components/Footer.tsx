import { content } from '../data/content'
import { MagneticButton } from './MagneticButton'

export function Footer() {
  return (
    <footer className="border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-12 py-10 sm:py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-8">
          {/* Brand */}
          <div>
            <a href="https://www.blacklayers.ca" target="_blank" rel="noreferrer" className="flex items-center gap-3 mb-4 group">
              <img src={`${import.meta.env.BASE_URL}blacklayers-logo.png`} alt="Black Layers" className="w-8 h-8 object-contain" />
              <span className="font-display font-medium text-sm group-hover:text-purple-400 transition-colors">{content.name}</span>
            </a>
            <p className="text-xs text-gray-500 leading-relaxed max-w-xs">
              Software Engineer crafting digital experiences with AI-powered workflows and modern tech stacks.
            </p>
          </div>

          {/* Quick links */}
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-gray-500 mb-4">Navigation</p>
            <div className="flex flex-col gap-2">
              {['About', 'Projects', 'Experience', 'Contact'].map((link) => (
                <a
                  key={link}
                  href={`#${link.toLowerCase()}`}
                  className="text-sm text-gray-400 hover:text-white transition-colors animated-underline w-fit"
                >
                  {link}
                </a>
              ))}
            </div>
          </div>

          {/* Socials */}
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-gray-500 mb-4">Connect</p>
            <div className="flex gap-4">
              <MagneticButton strength={0.3}>
                <a href={content.contact.github} target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-purple-500/50 transition-all" aria-label="GitHub">
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.372 0 0 5.373 0 12c0 5.302 3.438 9.8 8.08 11.348.6.111.78-.261.78-.578v-2.185c-3.338.726-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.605-2.664-.305-5.466-1.332-5.466-5.93 0-1.31.468-2.38 1.235-3.22-.123-.303-.535-1.523.117-3.175 0 0 1.008-.322 3.3 1.23a11.5 11.5 0 0 1 3-.405c1.02.005 2.047.138 3 .405 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.24 2.872.118 3.175.77.84 1.235 1.911 1.235 3.22 0 4.61-2.805 5.62-5.475 5.92.43.37.817 1.102.817 2.221v3.293c0 .32.17.694.787.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>
                </a>
              </MagneticButton>
              <MagneticButton strength={0.3}>
                <a href={content.contact.linkedin} target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-purple-500/50 transition-all" aria-label="LinkedIn">
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                </a>
              </MagneticButton>
              <MagneticButton strength={0.3}>
                <a href={`mailto:${content.contact.email}`} className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-purple-500/50 transition-all" aria-label="Email">
                  <svg className="w-4 h-4 fill-none stroke-current" viewBox="0 0 24 24" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" /></svg>
                </a>
              </MagneticButton>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 sm:mt-16 pt-6 sm:pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-[10px] tracking-[0.3em] uppercase text-gray-600">
            &copy; {new Date().getFullYear()} {content.name}
          </p>
          <MagneticButton strength={0.2}>
            <a
              href="#hero"
              className="text-[10px] tracking-[0.2em] uppercase text-gray-500 hover:text-white transition-colors flex items-center gap-2"
            >
              Back to top
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" /></svg>
            </a>
          </MagneticButton>
        </div>
      </div>
    </footer>
  )
}
