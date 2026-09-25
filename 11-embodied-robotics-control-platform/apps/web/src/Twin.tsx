import { Canvas } from '@react-three/fiber'
import type { LinkPose, RobotState } from './state'

const parts: Record<string, { scale: [number, number, number]; color: string }> = {
  torso: { scale: [0.48, 0.28, 0.7], color: '#168ba0' },
  head: { scale: [0.3, 0.3, 0.3], color: '#d7ded6' },
  left_arm: { scale: [0.12, 0.52, 0.12], color: '#e8aa55' },
}

function RobotPart({ link }: { link: LinkPose }) {
  const part = parts[link.link_name]
  if (!part) return null
  const p = link.position_m
  const q = link.orientation
  return (
    <mesh position={[p.x, p.y, p.z]} quaternion={[q.x, q.y, q.z, q.w]}>
      {link.link_name === 'head' ? <sphereGeometry args={[0.15, 16, 16]} /> : <boxGeometry args={part.scale} />}
      <meshStandardMaterial color={part.color} roughness={0.42} metalness={0.25} />
    </mesh>
  )
}

export default function Twin({ state }: { state: RobotState | null }) {
  return (
    <Canvas camera={{ position: [2.4, -3.3, 2.3], fov: 42 }} gl={{ antialias: true }}>
      <color attach="background" args={['#081522']} />
      <ambientLight intensity={1.35} />
      <directionalLight position={[2, -1, 4]} intensity={2.2} />
      <gridHelper args={[4, 16, '#294a5c', '#173043']} rotation={[Math.PI / 2, 0, 0]} />
      {state?.links.map(link => <RobotPart key={link.link_name} link={link} />)}
    </Canvas>
  )
}
