import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

// Configure axios to use the Flask backend from environment variable
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
import './App.css';

function App() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [postureType, setPostureType] = useState('squat');
  const [feedback, setFeedback] = useState([]);
  const [stats, setStats] = useState({
    totalFrames: 0,
    badPostureFrames: 0,
    goodPostureFrames: 0
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const animationFrameRef = useRef(null);

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 640, 
          height: 480,
          facingMode: 'user'
        } 
      });
      
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      setIsStreaming(true);
      
    } catch (error) {
      console.error('Error accessing webcam:', error);
      alert('Error accessing webcam. Please make sure you have granted camera permissions.');
    }
  };

  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    setIsStreaming(false);
    setFeedback([]);
    setStats({
      totalFrames: 0,
      badPostureFrames: 0,
      goodPostureFrames: 0
    });
  };

  const processFrames = async () => {
    if (!isRecording || !videoRef.current) return;

    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get frame data
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    try {
      // Send frame to backend for analysis
      const response = await axios.post('/api/analyze-posture', {
        frame: imageData,
        postureType: postureType
      });

      const result = response.data;
      
      // Update stats
      setStats(prev => ({
        totalFrames: prev.totalFrames + 1,
        badPostureFrames: prev.badPostureFrames + (result.hasBadPosture ? 1 : 0),
        goodPostureFrames: prev.goodPostureFrames + (result.hasBadPosture ? 0 : 1)
      }));

      // Add real-time feedback
      if (result.message !== 'No pose detected') {
        const newFeedback = {
          id: Date.now(),
          message: result.message,
          type: result.hasBadPosture ? 'error' : 'success',
          timestamp: new Date().toLocaleTimeString()
        };
        
        setFeedback(prev => [newFeedback, ...prev.slice(0, 9)]); // Keep last 10 feedback items
      }

    } catch (error) {
      console.error('Error analyzing posture:', error);
    }

    // Continue processing frames (10 FPS)
    setTimeout(() => {
      animationFrameRef.current = requestAnimationFrame(processFrames);
    }, 100);
  };

  const startRecording = () => {
    if (!streamRef.current) return;
    recordedChunksRef.current = [];
    const mediaRecorder = new window.MediaRecorder(streamRef.current, { mimeType: 'video/webm' });
    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunksRef.current.push(e.data);
    };
    mediaRecorder.start();
    setIsRecording(true);
    
    // Start real-time frame processing
    processFrames();
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      
      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        
        // Final analysis of the recorded video
        setIsAnalyzing(true);
        const formData = new FormData();
        formData.append('video', blob, 'webcam_recording.webm');
        formData.append('postureType', postureType);

        try {
          const response = await axios.post('/api/analyze-video', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            timeout: 60000
          });

          const result = response.data;
          
          // Update with final results
          setFeedback(result.feedback.map((item, index) => ({
            id: Date.now() + index,
            message: item.message,
            type: item.type,
            timestamp: new Date().toLocaleTimeString()
          })));
          
          setStats({
            totalFrames: result.stats.totalFrames,
            badPostureFrames: result.stats.badPostureFrames,
            goodPostureFrames: result.stats.goodPostureFrames
          });

        } catch (error) {
          console.error('Error analyzing video:', error);
          alert('Error analyzing video. Please try again.');
        } finally {
          setIsAnalyzing(false);
        }
      };
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsAnalyzing(true);
    setFeedback([]);
    setStats({
      totalFrames: 0,
      badPostureFrames: 0,
      goodPostureFrames: 0
    });

    const formData = new FormData();
    formData.append('video', file);
    formData.append('postureType', postureType);

    try {
      const response = await axios.post('/api/analyze-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000
      });

      const result = response.data;
      
      setFeedback(result.feedback.map((item, index) => ({
        id: Date.now() + index,
        message: item.message,
        type: item.type,
        timestamp: new Date().toLocaleTimeString()
      })));
      
      setStats({
        totalFrames: result.stats.totalFrames,
        badPostureFrames: result.stats.badPostureFrames,
        goodPostureFrames: result.stats.goodPostureFrames
      });

    } catch (error) {
      console.error('Error analyzing video:', error);
      alert('Error analyzing video. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    return () => {
      stopWebcam();
    };
  }, []);

  const getPosturePercentage = () => {
    if (stats.totalFrames === 0) return 0;
    return Math.round((stats.goodPostureFrames / stats.totalFrames) * 100);
  };

  return (
    <div className="container">
      <div className="app-header">
        <h1>Posture Detection App</h1>
        <p>Analyze your posture in real-time or upload a video</p>
      </div>

      <div className="main-content">
        <div className="video-section">
          <div className="posture-type-selector">
            <label htmlFor="posture-type">Select Posture Type:</label>
            <select 
              id="posture-type"
              value={postureType}
              onChange={(e) => setPostureType(e.target.value)}
            >
              <option value="squat">Squat</option>
              <option value="desk">Desk Sitting</option>
            </select>
          </div>

          <div className="video-container">
            <video
              ref={videoRef}
              className="video-element"
              autoPlay
              playsInline
              muted
            />
          </div>

          <div className="controls">
            {!isStreaming ? (
              <button 
                className="btn btn-primary" 
                onClick={startWebcam}
              >
                Start Webcam
              </button>
            ) : (
              <button className="btn btn-danger" onClick={stopWebcam}>
                Stop Webcam
              </button>
            )}
            
            {isStreaming && (
              <button 
                className={`btn ${isRecording ? 'btn-danger' : 'btn-primary'}`}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isAnalyzing}
              >
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </button>
            )}
            
            <label className={`btn ${isAnalyzing ? 'btn-secondary disabled' : 'btn-secondary'}`}>
              {isAnalyzing ? 'Analyzing...' : 'Upload Video'}
              <input
                type="file"
                accept="video/*"
                onChange={handleFileUpload}
                disabled={isAnalyzing}
                style={{ display: 'none' }}
              />
            </label>
          </div>

          <div className="stats-section">
            <div className="stat-card">
              <div className="stat-value">{stats.totalFrames}</div>
              <div className="stat-label">Total Frames</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.badPostureFrames}</div>
              <div className="stat-label">Bad Posture</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{getPosturePercentage()}%</div>
              <div className="stat-label">Good Posture</div>
            </div>
          </div>
        </div>

        <div className="feedback-section">
          <div className="feedback-header">
            <h3>Posture Analysis Feedback</h3>
            {isRecording && (
              <div style={{ color: '#ff6b6b', fontSize: '14px', marginTop: '5px' }}>
                🔴 Recording 
              </div>
            )}
          </div>
          
          {isAnalyzing && (
            <div className="analysis-progress">
              <p className="progress-text">Analyzing video...</p>
            </div>
          )}
          
          {feedback.length === 0 && !isAnalyzing && !isRecording ? (
            <p style={{ textAlign: 'center', color: '#6c757d', fontStyle: 'italic' }}>
              Upload video or record with webcam to see posture analysis feedback
            </p>
          ) : (
            feedback.map(item => (
              <div key={item.id} className={`feedback-item ${item.type}`}>
                <div className="feedback-time">{item.timestamp}</div>
                <div className="feedback-message">{item.message}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default App; 