# SignBridge Frontend

React application with 3D avatar for real-time sign language translation.

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Backend API running on localhost:8000

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The app will run on http://localhost:3000

## 3D Avatar Setup

### Download Mixamo Character

1. Go to [mixamo.com](https://www.mixamo.com/)
2. Search for "Ybot" character
3. Download in GLTF format (.glb)
4. Save as `frontend/public/avatar/ybot.glb`

### Avatar Features

- **3D Character**: Mixamo Ybot model with animations
- **Wave Animation**: Plays welcome animation on load
- **Camera Controls**: Orbit around character
- **Waist-up View**: Character shown from waist up
- **Dark Background**: Professional appearance

## Components

### Avatar.jsx
- Three.js canvas with React Three Fiber
- GLTF model loading with useGLTF
- Animation mixer for playing animations
- OrbitControls for camera interaction

### VideoUpload.jsx
- Drag and drop file upload
- Progress bar with percentage
- File validation (MP4, AVI, MOV, MKV, WebM)
- Size limit (100MB max)
- Axios integration with backend API

### Dashboard.jsx
- Main application layout
- Two-column design (upload | avatar)
- SignBridge branding
- Dark professional theme

## API Integration

- **Video Upload**: POST /api/video/upload
- **Authentication**: JWT-based user sessions
- **Subscription**: Stripe checkout integration

## Technologies

- **React 18**: Modern React with hooks
- **Three.js**: 3D graphics and animations
- **React Three Fiber**: React renderer for Three.js
- **React Three Drei**: Useful helpers for Three.js
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **React Router**: Client-side routing