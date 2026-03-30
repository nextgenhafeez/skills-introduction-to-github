import { useGLTF, useAnimations, Float, Clone } from '@react-three/drei'
import { useEffect, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface AvatarProps {
  pose?: 'standing' | 'sitting'
}

export function Avatar({ pose = 'standing' }: AvatarProps) {
  const modelUrl = '/models/character.glb'
  const { scene, animations } = useGLTF(modelUrl)
  
  const group = useRef<THREE.Group>(null!)
  const { actions } = useAnimations(animations, group)

  // We will store a target vector that smooths out mouse movements
  const smoothTarget = useRef(new THREE.Vector3(0, 0, 5))

  useFrame((state, delta) => {
    if (scene) {
      // The exact bones for this model are spine.006 (Head) and spine.005 (Neck)
      const head = scene.getObjectByName('spine.006') || scene.getObjectByName('Head')
      const neck = scene.getObjectByName('spine.005') || scene.getObjectByName('Neck')
      
      const targetX = state.pointer.x * 5
      const targetY = state.pointer.y * 3 + 1
      
      // Smoothly interpolate the target coordinates
      smoothTarget.current.x = THREE.MathUtils.lerp(smoothTarget.current.x, targetX, 5 * delta)
      smoothTarget.current.y = THREE.MathUtils.lerp(smoothTarget.current.y, targetY, 5 * delta)

      if (head) head.lookAt(smoothTarget.current)
      if (neck) neck.lookAt(smoothTarget.current)
    }
  })

  useEffect(() => {
    if (actions) {
      // Play idle/intro animations, ensure typing is off for the Hero section
      if (actions['typing']) actions['typing'].stop()
      if (actions['introAnimation']) actions['introAnimation'].play()
      if (actions['Blink']) actions['Blink'].play()
    }
  }, [actions])

  return (
    <group ref={group} scale={11} position={[0, -11, 0]} rotation={[0, 0, 0]}>
      <Float speed={2} rotationIntensity={0.2} floatIntensity={0.2}>
        <Clone object={scene} />
      </Float>
    </group>
  )
}

useGLTF.preload('/models/character.glb')
