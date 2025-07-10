from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import base64
import io
from PIL import Image
import os
import tempfile
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class PostureAnalyzer:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def analyze_squat(self, landmarks):
        """Analyze squat posture"""
        issues = []
        angles = {}
        
        # Get key landmarks
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        
        # Check knee over toe (knee should not go beyond ankle)
        if left_knee.visibility > 0.5 and left_ankle.visibility > 0.5:
            if left_knee.x > left_ankle.x:
                issues.append("Left knee is going beyond toes")
        
        if right_knee.visibility > 0.5 and right_ankle.visibility > 0.5:
            if right_knee.x > right_ankle.x:
                issues.append("Right knee is going beyond toes")
        
        # Check back angle (should be relatively straight)
        if (left_shoulder.visibility > 0.5 and left_hip.visibility > 0.5 and 
            left_knee.visibility > 0.5):
            back_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
            angles['left_back_angle'] = back_angle
            if back_angle < 150:
                issues.append(f"Back angle too acute ({back_angle:.1f}°)")
        
        if (right_shoulder.visibility > 0.5 and right_hip.visibility > 0.5 and 
            right_knee.visibility > 0.5):
            back_angle = self.calculate_angle(right_shoulder, right_hip, right_knee)
            angles['right_back_angle'] = back_angle
            if back_angle < 150:
                issues.append(f"Back angle too acute ({back_angle:.1f}°)")
        
        # Check knee angle (should be around 90 degrees for proper squat depth)
        if (left_hip.visibility > 0.5 and left_knee.visibility > 0.5 and 
            left_ankle.visibility > 0.5):
            knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            angles['left_knee_angle'] = knee_angle
            if knee_angle < 80 or knee_angle > 110:
                issues.append(f"Left knee angle not optimal ({knee_angle:.1f}°)")
        
        if (right_hip.visibility > 0.5 and right_knee.visibility > 0.5 and 
            right_ankle.visibility > 0.5):
            knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            angles['right_knee_angle'] = knee_angle
            if knee_angle < 80 or knee_angle > 110:
                issues.append(f"Right knee angle not optimal ({knee_angle:.1f}°)")
        
        return issues, angles
    
    def analyze_desk_sitting(self, landmarks):
        """Analyze desk sitting posture"""
        issues = []
        angles = {}
        
        # Get key landmarks
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
        right_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        
        # Check neck angle (head should be relatively straight)
        neck_angles = []
        if (nose.visibility > 0.5 and left_shoulder.visibility > 0.5 and 
            left_ear.visibility > 0.5):
            neck_angle = self.calculate_angle(left_ear, nose, left_shoulder)
            angles['left_neck_angle'] = neck_angle
            if neck_angle > 30:
                neck_angles.append(f"Left: {neck_angle:.1f}°")
        
        if (nose.visibility > 0.5 and right_shoulder.visibility > 0.5 and 
            right_ear.visibility > 0.5):
            neck_angle = self.calculate_angle(right_ear, nose, right_shoulder)
            angles['right_neck_angle'] = neck_angle
            if neck_angle > 30:
                neck_angles.append(f"Right: {neck_angle:.1f}°")
        
        if neck_angles:
            issues.append(f"Neck bent too much ({', '.join(neck_angles)})")
        
        # Check if back is straight (shoulders should be level)
        if (left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5):
            shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
            angles['shoulder_diff'] = shoulder_diff
            if shoulder_diff > 0.1:  # Threshold for shoulder levelness
                issues.append("Shoulders not level - back may not be straight")
        
        # Check arm position (elbows should be at desk level)
        if (left_elbow.visibility > 0.5 and left_shoulder.visibility > 0.5):
            arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            angles['left_arm_angle'] = arm_angle
            if arm_angle < 70 or arm_angle > 110:
                issues.append(f"Left arm position not optimal ({arm_angle:.1f}°)")
        
        if (right_elbow.visibility > 0.5 and right_shoulder.visibility > 0.5):
            arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
            angles['right_arm_angle'] = arm_angle
            if arm_angle < 70 or arm_angle > 110:
                issues.append(f"Right arm position not optimal ({arm_angle:.1f}°)")
        
        # Check if person is too close to screen (head forward)
        if (nose.visibility > 0.5 and left_shoulder.visibility > 0.5):
            head_forward = nose.x - left_shoulder.x
            angles['head_forward'] = head_forward
            if head_forward > 0.1:  # Threshold for forward head posture
                issues.append("Head too far forward - maintain proper distance from screen")
        
        return issues, angles
    
    def analyze_frame(self, frame, posture_type):
        """Analyze a single frame for posture issues"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return {
                'hasBadPosture': False,
                'message': 'No pose detected',
                'landmarks': None,
                'angles': None
            }
        
        # Convert landmarks to list for easier processing
        landmarks = results.pose_landmarks.landmark
        
        # Analyze based on posture type
        if posture_type == 'squat':
            issues, angles = self.analyze_squat(landmarks)
        elif posture_type == 'desk':
            issues, angles = self.analyze_desk_sitting(landmarks)
        else:
            issues, angles = [], {}
        
        # Convert landmarks to serializable format
        landmarks_data = []
        for landmark in landmarks:
            landmarks_data.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        
        if issues:
            return {
                'hasBadPosture': True,
                'message': '; '.join(issues),
                'landmarks': landmarks_data,
                'issues': issues,
                'angles': angles
            }
        else:
            return {
                'hasBadPosture': False,
                'message': 'Good posture detected',
                'landmarks': landmarks_data,
                'angles': angles
            }

# Initialize analyzer
analyzer = PostureAnalyzer()

@app.route('/api/analyze-posture', methods=['POST'])
def analyze_posture():
    try:
        data = request.get_json()
        frame_data = data.get('frame')
        posture_type = data.get('postureType', 'squat')
        
        if not frame_data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        # Remove data URL prefix
        if frame_data.startswith('data:image/jpeg;base64,'):
            frame_data = frame_data.split(',')[1]
        
        # Decode base64 image
        image_data = base64.b64decode(frame_data)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to OpenCV format
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Analyze posture
        result = analyzer.analyze_frame(frame, posture_type)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    video_path = None
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        posture_type = request.form.get('postureType', 'squat')
        
        # Check if file is empty
        if video_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
        file_extension = video_file.filename.rsplit('.', 1)[1].lower() if '.' in video_file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': f'Unsupported file format. Allowed formats: {", ".join(allowed_extensions)}'}), 400
        
        # Save video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            video_file.save(tmp_file.name)
            video_path = tmp_file.name
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return jsonify({'error': 'Could not open video file'}), 400
        
        feedback = []
        stats = {
            'totalFrames': 0,
            'badPostureFrames': 0,
            'goodPostureFrames': 0
        }
        
        frame_count = 0
        max_frames = 300  # Limit processing to prevent timeout
        
        while cap.isOpened() and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            stats['totalFrames'] += 1
            
            # Analyze every frame for real-time feedback
            try:
                result = analyzer.analyze_frame(frame, posture_type)
                
                if result['hasBadPosture']:
                    stats['badPostureFrames'] += 1
                    feedback.append({
                        'frame': frame_count,
                        'message': result['message'],
                        'type': 'error',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    stats['goodPostureFrames'] += 1
                    
            except Exception as frame_error:
                print(f"Error analyzing frame {frame_count}: {frame_error}")
                continue
        
        cap.release()
        
        if stats['totalFrames'] == 0:
            return jsonify({'error': 'No frames could be processed from the video'}), 400
        
        return jsonify({
            'feedback': feedback,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Error in analyze_video: {str(e)}")
        return jsonify({'error': f'Error analyzing video: {str(e)}'}), 500
    finally:
        # Clean up temporary file
        if video_path and os.path.exists(video_path):
            try:
                os.unlink(video_path)
            except Exception as cleanup_error:
                print(f"Error cleaning up temporary file: {cleanup_error}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Posture detection API is running'})

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'Backend is working correctly!'})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 