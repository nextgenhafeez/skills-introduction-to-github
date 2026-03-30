import { useEffect, useRef, useCallback } from 'react'

export function CustomCursor() {
  const dotRef = useRef<HTMLDivElement>(null)
  const outlineRef = useRef<HTMLDivElement>(null)
  const posRef = useRef({ x: 0, y: 0 })
  const dotPos = useRef({ x: 0, y: 0 })
  const outlinePos = useRef({ x: 0, y: 0 })
  const rafRef = useRef<number>()
  const isTouch = useRef(false)

  useEffect(() => {
    isTouch.current = !window.matchMedia('(hover: hover)').matches
    if (isTouch.current) return

    const handleMouseMove = (e: MouseEvent) => {
      posRef.current = { x: e.clientX, y: e.clientY }
    }

    const handleMouseDown = () => {
      outlineRef.current?.classList.add('clicking')
    }

    const handleMouseUp = () => {
      outlineRef.current?.classList.remove('clicking')
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mousedown', handleMouseDown)
    window.addEventListener('mouseup', handleMouseUp)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mousedown', handleMouseDown)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [])

  // Hover detection via event delegation
  useEffect(() => {
    if (isTouch.current) return

    const handleOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      const interactive = target.closest('a, button, [data-cursor], input, textarea, [role="button"]')
      if (interactive) {
        dotRef.current?.classList.add('hovering')
        outlineRef.current?.classList.add('hovering')
      }
    }

    const handleOut = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      const interactive = target.closest('a, button, [data-cursor], input, textarea, [role="button"]')
      if (interactive) {
        dotRef.current?.classList.remove('hovering')
        outlineRef.current?.classList.remove('hovering')
      }
    }

    document.addEventListener('mouseover', handleOver)
    document.addEventListener('mouseout', handleOut)
    return () => {
      document.removeEventListener('mouseover', handleOver)
      document.removeEventListener('mouseout', handleOut)
    }
  }, [])

  // Animation loop
  useEffect(() => {
    if (isTouch.current) return

    const lerp = (a: number, b: number, f: number) => a + (b - a) * f

    const animate = () => {
      dotPos.current.x = lerp(dotPos.current.x, posRef.current.x, 0.2)
      dotPos.current.y = lerp(dotPos.current.y, posRef.current.y, 0.2)
      outlinePos.current.x = lerp(outlinePos.current.x, posRef.current.x, 0.08)
      outlinePos.current.y = lerp(outlinePos.current.y, posRef.current.y, 0.08)

      if (dotRef.current) {
        dotRef.current.style.transform = `translate(${dotPos.current.x - 4}px, ${dotPos.current.y - 4}px)`
      }
      if (outlineRef.current) {
        outlineRef.current.style.transform = `translate(${outlinePos.current.x - 20}px, ${outlinePos.current.y - 20}px)`
      }

      rafRef.current = requestAnimationFrame(animate)
    }
    rafRef.current = requestAnimationFrame(animate)
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [])

  if (typeof window !== 'undefined' && !window.matchMedia('(hover: hover)').matches) {
    return null
  }

  return (
    <>
      <div ref={dotRef} className="cursor-dot" />
      <div ref={outlineRef} className="cursor-outline" />
    </>
  )
}
