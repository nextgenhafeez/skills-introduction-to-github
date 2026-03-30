import { useEffect, useRef, useState } from 'react'

interface MousePosition {
  x: number
  y: number
  normalizedX: number
  normalizedY: number
}

export function useMousePosition(lerpFactor = 0.08) {
  const [smoothPos, setSmoothPos] = useState<MousePosition>({ x: 0, y: 0, normalizedX: 0, normalizedY: 0 })
  const rawPos = useRef({ x: 0, y: 0 })
  const rafRef = useRef<number>()

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      rawPos.current = { x: e.clientX, y: e.clientY }
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  useEffect(() => {
    const lerp = (start: number, end: number, factor: number) => start + (end - start) * factor
    let currentX = 0
    let currentY = 0

    const animate = () => {
      currentX = lerp(currentX, rawPos.current.x, lerpFactor)
      currentY = lerp(currentY, rawPos.current.y, lerpFactor)
      setSmoothPos({
        x: currentX,
        y: currentY,
        normalizedX: (currentX / window.innerWidth) * 2 - 1,
        normalizedY: (currentY / window.innerHeight) * 2 - 1,
      })
      rafRef.current = requestAnimationFrame(animate)
    }
    rafRef.current = requestAnimationFrame(animate)
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [lerpFactor])

  return smoothPos
}
