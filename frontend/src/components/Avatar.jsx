import React, { useRef, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

// Avatar Model Component - Simple mesh fallback (GLTF model file incomplete)
function AvatarModel({ currentSign }) {
  const groupRef = useRef();

  useFrame((state, delta) => {
    // Optional: Add rotation animation
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.005;
    }
  });

  return (
    <group ref={groupRef} position={[0, -0.5, 0]}>
      {/* Simple avatar placeholder - shows a blue figure */}
      <mesh position={[0, 0.8, 0]}>
        <sphereGeometry args={[0.3, 32, 32]} />
        <meshPhongMaterial color="#0066cc" />
      </mesh>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[0.6, 1.2, 0.3]} />
        <meshPhongMaterial color="#0066cc" />
      </mesh>
      {/* Left arm */}
      <mesh position={[-0.5, 0.4, 0]}>
        <boxGeometry args={[0.15, 0.8, 0.15]} />
        <meshPhongMaterial color="#004499" />
      </mesh>
      {/* Right arm */}
      <mesh position={[0.5, 0.4, 0]}>
        <boxGeometry args={[0.15, 0.8, 0.15]} />
        <meshPhongMaterial color="#004499" />
      </mesh>
      {/* Text label */}
      {currentSign && (
        <text position={[0, -1.2, 0]} fontSize={0.2} color="#00ff00">
          {currentSign.replace(/_/g, ' ')}
        </text>
      )}
    </group>
  );
}

// Main Avatar Component
const Avatar = ({ currentSign }) => {
  return (
    <div className="w-full h-full bg-gray-900 rounded-lg overflow-hidden">
      <Canvas
        camera={{
          position: [0, 0, 3],
          fov: 50
        }}
        style={{ background: '#111827' }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.6} />
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          castShadow
        />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />

        {/* Avatar Model */}
        <AvatarModel currentSign={currentSign} />

        {/* Camera Controls */}
        <OrbitControls
          enablePan={false}
          enableZoom={true}
          enableRotate={true}
          minDistance={2}
          maxDistance={5}
          maxPolarAngle={Math.PI / 2}
        />
      </Canvas>
    </div>
  );
};

export default Avatar;