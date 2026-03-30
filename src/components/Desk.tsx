import { Float } from '@react-three/drei'

export function Desk() {
  return (
    <group position={[0, -3.5, 0]}>
      {/* Table Top - Premium wood/carbon look */}
      <mesh position={[0, 1.8, -0.5]} receiveShadow>
        <boxGeometry args={[6, 0.15, 3]} />
        <meshStandardMaterial color="#0a0a0a" roughness={0} metalness={0.9} />
      </mesh>
      
      {/* Desk Mat */}
      <mesh position={[0, 1.88, 0.4]} receiveShadow>
        <boxGeometry args={[4.5, 0.01, 1.5]} />
        <meshStandardMaterial color="#050505" roughness={0.8} />
      </mesh>
      
      {/* Table Legs - Minimalist black steel */}
      <mesh position={[-2.8, 0.9, -1.5]}>
        <boxGeometry args={[0.1, 1.8, 0.1]} />
        <meshStandardMaterial color="#000" metalness={1} />
      </mesh>
      <mesh position={[2.8, 0.9, -1.5]}>
        <boxGeometry args={[0.1, 1.8, 0.1]} />
        <meshStandardMaterial color="#000" metalness={1} />
      </mesh>
      <mesh position={[-2.8, 0.9, 0.8]}>
        <boxGeometry args={[0.1, 1.8, 0.1]} />
        <meshStandardMaterial color="#000" metalness={1} />
      </mesh>
      <mesh position={[2.8, 0.9, 0.8]}>
        <boxGeometry args={[0.1, 1.8, 0.1]} />
        <meshStandardMaterial color="#000" metalness={1} />
      </mesh>

      {/* Chair - Simple ergonomic shape */}
      <group position={[0, 0, 1.8]}>
        <mesh position={[0, 0.6, 0]}>
          <boxGeometry args={[1.6, 0.2, 1.6]} />
          <meshStandardMaterial color="#222" />
        </mesh>
        <mesh position={[0, 1.6, 0.7]} rotation={[0.2, 0, 0]}>
          <boxGeometry args={[1.5, 1.8, 0.2]} />
          <meshStandardMaterial color="#222" />
        </mesh>
        <mesh position={[0, 0.3, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 0.6]} />
          <meshStandardMaterial color="#000" />
        </mesh>
      </group>

      {/* Monitor with Glow */}
      <Float speed={2} rotationIntensity={0.1} floatIntensity={0.2}>
        <group position={[0, 3.2, -1.2]}>
          <mesh castShadow>
            <boxGeometry args={[3.2, 1.8, 0.15]} />
            <meshStandardMaterial color="#000" />
          </mesh>
          <mesh position={[0, 0, 0.08]}>
            <planeGeometry args={[3.1, 1.7]} />
            <meshBasicMaterial color="#4c1d95" />
          </mesh>
          {/* Monitor Glow on face */}
          <pointLight position={[0, 0, 1]} intensity={2} color="#8b5cf6" distance={5} />
        </group>
      </Float>
    </group>
  )
}
