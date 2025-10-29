import cv2
import numpy as np
from typing import Dict, Any, List
import base64
from datetime import datetime

class ProctoringService:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        self.MULTIPLE_FACES_THRESHOLD = 1
        self.NO_FACE_DURATION_THRESHOLD = 3
    
    def decode_image(self, base64_image: str) -> np.ndarray:
        try:
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            
            img_data = base64.b64decode(base64_image)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"Error decoding image: {e}")
            return None
    
    async def analyze_frame(self, frame_base64: str) -> Dict[str, Any]:
        violations = []
        frame = self.decode_image(frame_base64)
        
        if frame is None:
            return {
                "violations": [{
                    "type": "invalid_frame",
                    "severity": "high",
                    "description": "Unable to process video frame"
                }],
                "face_count": 0,
                "head_pose": None,
                "gaze_direction": None
            }
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        face_count = len(faces)
        
        if face_count == 0:
            violations.append({
                "type": "no_face_detected",
                "severity": "high",
                "description": "No face detected in frame"
            })
        elif face_count > self.MULTIPLE_FACES_THRESHOLD:
            violations.append({
                "type": "multiple_faces",
                "severity": "critical",
                "description": f"{face_count} faces detected. Only one person allowed."
            })
        
        head_pose = None
        gaze_direction = None
        
        if face_count == 1:
            x, y, w, h = faces[0]
            face_roi_gray = gray[y:y+h, x:x+w]
            
            eyes = self.eye_cascade.detectMultiScale(
                face_roi_gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(20, 20)
            )
            
            if len(eyes) < 2:
                violations.append({
                    "type": "eyes_not_visible",
                    "severity": "medium",
                    "description": "Eyes not clearly visible or looking away"
                })
                gaze_direction = "away"
            else:
                gaze_direction = "forward"
            
            frame_center_x = frame.shape[1] // 2
            frame_center_y = frame.shape[0] // 2
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            horizontal_offset = abs(face_center_x - frame_center_x)
            vertical_offset = abs(face_center_y - frame_center_y)
            
            if horizontal_offset > frame.shape[1] * 0.25:
                head_pose = "turned_horizontal"
                violations.append({
                    "type": "head_turned",
                    "severity": "medium",
                    "description": "Head is turned significantly to the side"
                })
            elif vertical_offset > frame.shape[0] * 0.2:
                head_pose = "tilted"
                violations.append({
                    "type": "head_tilted",
                    "severity": "low",
                    "description": "Head is tilted or looking up/down"
                })
            else:
                head_pose = "centered"
        
        return {
            "violations": violations,
            "face_count": face_count,
            "head_pose": head_pose,
            "gaze_direction": gaze_direction,
            "timestamp": datetime.utcnow().isoformat()
        }

proctoring_service = ProctoringService()
