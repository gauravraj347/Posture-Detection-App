# Posture Detection App

A full-stack web application that analyzes posture in real-time using computer vision and rule-based logic. The app can detect bad posture during squats and desk sitting, providing real-time feedback to users.

## Features

- **Real-time Posture Analysis**: Use webcam to get instant feedback on your posture
- **Video Upload**: Upload videos for detailed posture analysis
- **Two Posture Types**:
  - **Squat Analysis**: Detects knee over toe, back angle, and knee angle issues
  - **Desk Sitting Analysis**: Detects neck bending, shoulder levelness, and arm position
- **Visual Feedback**: Pose landmarks are drawn on the video with color-coded feedback
- **Statistics**: Track total frames, bad posture frames, and good posture percentage
- **Modern UI**: Beautiful, responsive design with real-time feedback

## Technology Stack

### Frontend

- React 18
- Axios for API communication
- Modern CSS with gradients and animations
- Canvas API for pose visualization

### Backend

- Flask (Python)
- MediaPipe for pose detection
- OpenCV for image processing
- NumPy for mathematical calculations

## Installation

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd posture-detection-app
   ```

2. **Install Frontend Dependencies**

   ```bash
   npm install
   ```

3. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Start the Backend Server

```bash
cd backend
python app.py
```

The Flask server will start on `http://localhost:5000`

### Start the Frontend Development Server

```bash
npm start
```

The React app will start on `http://localhost:3000`

## Usage

1. **Select Posture Type**: Choose between "Squat" or "Desk Sitting" from the dropdown
2. **Start Webcam**: Click "Start Webcam" to begin real-time analysis
3. **Upload Video**: Alternatively, click "Upload Video" to analyze a pre-recorded video
4. **View Feedback**: Real-time feedback will appear in the right panel
5. **Monitor Statistics**: Track your posture performance with the statistics cards

## Posture Analysis Rules

### Squat Analysis

- **Knee Over Toe**: Flags if knee goes beyond the ankle
- **Back Angle**: Warns if back angle is less than 150°
- **Knee Angle**: Checks if knee angle is between 80-110° for optimal squat depth

### Desk Sitting Analysis

- **Neck Angle**: Flags if neck bends more than 30°
- **Shoulder Levelness**: Checks if shoulders are level (indicates straight back)
- **Arm Position**: Ensures elbows are at proper desk level (70-110°)
- **Head Position**: Warns if head is too far forward

## API Endpoints

- `POST /api/analyze-posture`: Analyze a single frame
- `POST /api/analyze-video`: Analyze uploaded video
- `GET /api/health`: Health check endpoint

## Project Structure

```
posture-detection-app/
├── backend/
│   └── app.py              # Flask backend with posture analysis
├── public/
│   └── index.html          # Main HTML file
├── src/
│   ├── App.js             # Main React component
│   ├── App.css            # Component styles
│   ├── index.js           # React entry point
│   └── index.css          # Global styles
├── package.json           # Frontend dependencies
├── requirements.txt       # Backend dependencies
└── README.md             # This file
```

## Development

### Adding New Posture Types

1. Add new analysis method in `PostureAnalyzer` class
2. Update the `analyze_frame` method to handle the new type
3. Add the option to the frontend dropdown

### Customizing Analysis Rules

Modify the threshold values in the analysis methods:

- `analyze_squat()` for squat-related rules
- `analyze_desk_sitting()` for desk sitting rules

## Troubleshooting

### Common Issues

1. **Webcam not working**

   - Ensure camera permissions are granted
   - Check if another application is using the camera

2. **Backend connection error**

   - Verify Flask server is running on port 5000
   - Check if all Python dependencies are installed

3. **Pose detection not working**
   - Ensure good lighting conditions
   - Make sure the person is fully visible in the frame
   - Check if MediaPipe is properly installed

### Performance Tips

- For better performance, ensure good lighting
- Position yourself clearly in the camera frame
- For video uploads, shorter videos process faster
- The app analyzes every 5th frame for video uploads to improve speed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- MediaPipe for pose detection
- OpenCV for computer vision capabilities
- React team for the frontend framework
- Flask team for the backend framework
