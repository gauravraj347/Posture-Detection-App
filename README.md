# Full-Stack Rule-Based Bad Posture Detection App

## Objective

Build a web application where users can upload a video or use their webcam while performing a squat or sitting at a desk. The app analyzes posture using rule-based logic and flags instances of bad posture (e.g., slouching, knee over toe, hunched back, etc.).

---

## Features

- **Video Upload & Webcam Support:** Users can upload a video or use their webcam for posture analysis.
- **Real-Time & Frame-by-Frame Feedback:** Get instant or per-frame feedback on posture.
- **Visual Feedback:** See messages or highlights when bad posture is detected.
- **Statistics:** Track total frames, good/bad posture counts, and percentages.

---

## Tech Stack

- **Frontend:** React, Axios
- **Backend:** Flask (Python), MediaPipe, OpenCV, NumPy
- **Deployment:** (e.g., Render for backend, Vercel/Netlify for frontend)

---

## Folder Structure

```
project-root/
├── frontend/   # React app
├── backend/    # Flask app
└── README.md   # This file
```

---

## Setup Instructions

### Prerequisites

- Node.js (v14+)
- Python 3.8+
- pip

### 1. Backend Setup

```sh
cd backend
pip install -r requirements.txt
python app.py
```

The backend will run on `http://localhost:5000` by default.

### 2. Frontend Setup

```sh
cd ../frontend
npm install
# Create a .env file with your backend URL:
echo REACT_APP_API_URL=http://localhost:5000 > .env
npm start
```

The frontend will run on `http://localhost:3000` by default.

---

## Deployment

- **Frontend:** Deployed on [Vercel](https://vercel.com/) or [Netlify](https://netlify.com/)

**Public URLs:**

- Frontend: [https://posture-detection-app-five.vercel.app](https://posture-detection-app-five.vercel.app/)

---

## Demo Video

- [Watch the demo video](https://drive.google.com/file/d/1hg5b3lL6RUjVxoW9pBOOOc-qBeSR5_yv/view?usp=sharing)

---

## Usage

1. **Select Posture Type:** Choose "Squat" or "Desk Sitting".
2. **Start Webcam or Upload Video:**
   - Click "Start Webcam" for real-time analysis.
   - Or click "Upload Video" to analyze a pre-recorded video.
3. **View Feedback:**
   - Real-time or frame-by-frame feedback will appear.
   - Bad posture messages are shown when detected.
4. **Check Statistics:**
   - See total frames, good/bad posture counts, and good posture percentage.

---

## Rule-Based Logic

- **Squat:**
  - Flag if knee goes beyond toe.
  - Flag if back angle < 150°.
- **Desk Sitting:**
  - Flag if neck bends > 30°.
  - Flag if back isn’t straight.

---

## API Endpoints

- `POST /api/analyze-posture`: Analyze a single frame (for real-time feedback)
- `POST /api/analyze-video`: Analyze an uploaded video
- `GET /api/health`: Health check

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

---

## License

MIT License

---

## Acknowledgments

- MediaPipe
- OpenCV
- React
- Flask
