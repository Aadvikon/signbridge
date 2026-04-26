# SignBridge

**Make every business video accessible to 70 million deaf people worldwide using AI.**

SignBridge is a B2B SaaS platform that adds real-time sign language translation to any business video. We use advanced AI/ML to automatically detect speech, extract hand gestures, and render a photorealistic sign language avatar.

## Product Overview

### Target Customers
- **E-learning platforms** — Make educational content accessible to deaf students
- **Media broadcasters** — Broadcast accessible news and entertainment
- **Corporate enterprises** — Ensure compliance with accessibility standards

### Pricing Tiers
- **Starter** — $299/mo (up to 10 videos/month)
- **Business** — $899/mo (unlimited videos)
- **Enterprise** — Custom pricing (dedicated support)

## Tech Stack

### Backend
- **Language**: Python 3.12
- **Framework**: FastAPI + Uvicorn
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + JWT
- **Storage**: Cloudflare R2

### AI/ML
- **Video Processing**: OpenCV + FFmpeg
- **Hand Detection**: MediaPipe
- **Deep Learning**: TensorFlow + LSTM
- **Sign Language Dataset**: WLASL
- **Speech-to-Text**: OpenAI Whisper (local, free)

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **3D Avatar**: Three.js + react-three-fiber
- **Character Models**: Mixamo

### Payments & Hosting
- **Payments**: Stripe
- **Backend Hosting**: Railway
- **Frontend Hosting**: Vercel
- **Testing**: Pytest (backend) + Jest (frontend)

## Project Structure

```
signbridgedir/
├── backend/                    # FastAPI backend server
│   ├── main.py                # Entry point
│   ├── models/                # AI model files and loaders
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic (video processing, etc.)
│   └── utils/                 # Helper functions
├── frontend/                  # React frontend app
│   └── src/
│       ├── components/        # Reusable React components
│       ├── pages/            # Page views
│       ├── hooks/            # Custom React hooks
│       └── utils/            # Helper utilities
├── models/                    # Trained ML models
│   ├── trained/              # Final .h5 model files
│   └── checkpoints/          # Training checkpoints
├── data/                      # Training and processing data
│   ├── raw/                  # Original WLASL videos
│   ├── landmarks/            # Extracted MediaPipe JSON files
│   └── processed/            # Ready-to-train numpy arrays
├── notebooks/                 # Jupyter notebooks for experiments
│   └── exploration/          # Data exploration and prototyping
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (dev)
├── .env.example              # Example env template
├── README.md                 # This file
└── PROGRESS.md              # Task tracking
```

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+ (for frontend)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/signbridge/signbridge.git
   cd signbridgedir
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

5. **Run the API server**
   ```bash
   python backend/main.py
   ```
   
   The API will be available at `http://localhost:8000`
   - Health check: `http://localhost:8000/health`
   - API docs: `http://localhost:8000/docs`

## API Endpoints

### Health Check
```
GET /
GET /health
```

Returns the status of the API server.

## Development Workflow

### Adding a New Dependency
1. Install it: `pip install package-name`
2. Add to requirements.txt: `pip freeze > requirements.txt`
3. Commit and push

### Code Style
- **Python**: Follow PEP8, use type hints on all functions
- **React**: Functional components only, no class components
- **Variable names**: Clear and descriptive
- **Functions**: Do one thing only, keep under 30 lines
- Every file must have a docstring explaining its purpose

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
npm test
```

## Architecture

### Video Processing Pipeline
1. **Video Upload** → User uploads video via frontend
2. **Speech Extraction** → Whisper extracts speech and timestamps
3. **Hand Detection** → MediaPipe extracts hand landmarks from video
4. **Sign Recognition** → LSTM model maps hand landmarks to sign language
5. **Avatar Rendering** → Three.js renders Mixamo avatar performing signs
6. **Video Merge** → FFmpeg combines original video with sign language overlay
7. **Output Delivery** → Video stored in R2, delivered to user

### Database Schema
- Users (authentication)
- Videos (upload history)
- Processing Jobs (track pipeline progress)
- Subscriptions (billing and pricing tier)

## Deployment

### Backend (Railway)
- Docker container with FastAPI app
- Automatic deployments on git push
- Environment variables configured in Railway dashboard

### Frontend (Vercel)
- Static React build
- Automatic deployments on git push
- Connected to backend API

## Troubleshooting

### Common Issues

**Port 8000 already in use?**
```bash
python backend/main.py --port 8001
```

**Module not found error?**
Make sure you activated the virtual environment and installed requirements:
```bash
pip install -r requirements.txt
```

**Supabase connection error?**
Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes following code style
3. Write tests for new functionality
4. Submit a pull request

## License

Proprietary - SignBridge © 2026

## Contact

For questions or partnerships, contact the SignBridge team.
