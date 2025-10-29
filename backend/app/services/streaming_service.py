import socketio
from typing import Dict, Set
import logging

logger = logging.getLogger(__name__)

class StreamingManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins='*',
            logger=True,
            engineio_logger=True
        )
        
        self.test_rooms: Dict[str, Set[str]] = {}
        self.student_info: Dict[str, Dict] = {}
        self.teacher_rooms: Dict[str, str] = {}
    
    def get_asgi_app(self):
        return socketio.ASGIApp(self.sio)
    
    async def setup_handlers(self):
        @self.sio.event
        async def connect(sid, environ):
            logger.info(f"Client connected: {sid}")
            await self.sio.emit('connected', {'sid': sid}, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            logger.info(f"Client disconnected: {sid}")
            
            if sid in self.student_info:
                student_data = self.student_info[sid]
                test_code = student_data.get('test_code')
                
                if test_code and test_code in self.test_rooms:
                    self.test_rooms[test_code].discard(sid)
                    
                    teacher_sid = self.teacher_rooms.get(test_code)
                    if teacher_sid:
                        await self.sio.emit('student_left', {
                            'student_id': student_data.get('user_id'),
                            'student_name': student_data.get('name')
                        }, room=teacher_sid)
                
                del self.student_info[sid]
            
            if sid in self.teacher_rooms.values():
                test_code = [k for k, v in self.teacher_rooms.items() if v == sid][0]
                del self.teacher_rooms[test_code]
        
        @self.sio.event
        async def join_test_as_student(sid, data):
            test_code = data.get('test_code')
            user_id = data.get('user_id')
            name = data.get('name')
            attempt_id = data.get('attempt_id')
            
            if not test_code:
                await self.sio.emit('error', {'message': 'Test code required'}, room=sid)
                return
            
            if test_code not in self.test_rooms:
                self.test_rooms[test_code] = set()
            
            self.test_rooms[test_code].add(sid)
            self.student_info[sid] = {
                'user_id': user_id,
                'name': name,
                'test_code': test_code,
                'attempt_id': attempt_id,
                'violations': []
            }
            
            await self.sio.enter_room(sid, f"test_{test_code}")
            
            teacher_sid = self.teacher_rooms.get(test_code)
            if teacher_sid:
                await self.sio.emit('student_joined', {
                    'sid': sid,
                    'student_id': user_id,
                    'student_name': name,
                    'attempt_id': attempt_id
                }, room=teacher_sid)
            
            await self.sio.emit('joined_test', {'test_code': test_code}, room=sid)
            logger.info(f"Student {name} joined test {test_code}")
        
        @self.sio.event
        async def join_test_as_teacher(sid, data):
            test_code = data.get('test_code')
            
            if not test_code:
                await self.sio.emit('error', {'message': 'Test code required'}, room=sid)
                return
            
            self.teacher_rooms[test_code] = sid
            await self.sio.enter_room(sid, f"test_{test_code}_teacher")
            
            students = []
            if test_code in self.test_rooms:
                for student_sid in self.test_rooms[test_code]:
                    if student_sid in self.student_info:
                        student = self.student_info[student_sid]
                        students.append({
                            'sid': student_sid,
                            'student_id': student['user_id'],
                            'student_name': student['name'],
                            'attempt_id': student['attempt_id']
                        })
            
            await self.sio.emit('monitoring_started', {
                'test_code': test_code,
                'students': students
            }, room=sid)
            
            logger.info(f"Teacher joined monitoring for test {test_code}")
        
        @self.sio.event
        async def video_frame(sid, data):
            if sid not in self.student_info:
                return
            
            student_data = self.student_info[sid]
            test_code = student_data.get('test_code')
            
            teacher_sid = self.teacher_rooms.get(test_code)
            if teacher_sid:
                await self.sio.emit('student_video_frame', {
                    'sid': sid,
                    'student_id': student_data['user_id'],
                    'student_name': student_data['name'],
                    'frame': data.get('frame'),
                    'timestamp': data.get('timestamp')
                }, room=teacher_sid)
        
        @self.sio.event
        async def violation_detected(sid, data):
            if sid not in self.student_info:
                return
            
            student_data = self.student_info[sid]
            test_code = student_data.get('test_code')
            
            violation = {
                'type': data.get('type'),
                'severity': data.get('severity'),
                'timestamp': data.get('timestamp'),
                'details': data.get('details')
            }
            
            student_data['violations'].append(violation)
            
            teacher_sid = self.teacher_rooms.get(test_code)
            if teacher_sid:
                await self.sio.emit('student_violation', {
                    'sid': sid,
                    'student_id': student_data['user_id'],
                    'student_name': student_data['name'],
                    'violation': violation
                }, room=teacher_sid)
            
            logger.warning(f"Violation detected for student {student_data['name']}: {violation['type']}")
        
        @self.sio.event
        async def student_in_waiting_room(sid, data):
            """Handle student entering waiting room"""
            logger.info(f"Student {data.get('name')} entered waiting room")
            
            # Store waiting room info
            self.student_info[sid] = {
                'user_id': data.get('user_id'),
                'name': data.get('name'),
                'test_id': data.get('test_id'),
                'attempt_id': data.get('attempt_id'),
                'status': 'waiting',
                'sid': sid
            }
            
            # Notify teacher monitoring this test
            test_code = data.get('test_code')
            if test_code:
                teacher_sid = self.teacher_rooms.get(test_code)
                if teacher_sid:
                    await self.sio.emit('student_in_waiting_room', {
                        'sid': sid,
                        'name': data.get('name'),
                        'user_id': data.get('user_id'),
                        'test_id': data.get('test_id'),
                        'attempt_id': data.get('attempt_id')
                    }, room=teacher_sid)
        
        @self.sio.event
        async def teacher_pause_student(sid, data):
            """Teacher manually pauses a student"""
            logger.info(f"Teacher pausing student {data.get('student_id')}")
            
            student_sid = data.get('sid')
            if student_sid:
                # Tell student to go to waiting room
                await self.sio.emit('go_to_waiting_room', {
                    'test_id': data.get('test_id'),
                    'reason': data.get('reason', 'Paused by teacher')
                }, room=student_sid)
        
        @self.sio.event
        async def approve_student(sid, data):
            """Teacher approves student to continue test"""
            logger.info(f"Teacher approved student {data.get('student_id')}")
            
            student_sid = data.get('sid')
            if student_sid:
                # Tell student they can continue
                await self.sio.emit('approved_to_continue', {
                    'test_id': data.get('test_id')
                }, room=student_sid)
                
                # Update status
                if student_sid in self.student_info:
                    self.student_info[student_sid]['status'] = 'active'
        
        @self.sio.event
        async def teacher_terminate_student(sid, data):
            """Teacher terminates student's test"""
            logger.info(f"Teacher terminated student {data.get('student_id')}")
            
            student_sid = data.get('sid')
            if student_sid:
                # Tell student test is terminated
                await self.sio.emit('test_terminated', {
                    'reason': 'Test terminated by teacher'
                }, room=student_sid)
                
                # Clean up
                if student_sid in self.student_info:
                    del self.student_info[student_sid]
        
        @self.sio.event
        async def terminate_from_waiting(sid, data):
            """Terminate student from waiting room"""
            logger.info(f"Terminating student {data.get('student_id')} from waiting room")
            
            student_sid = data.get('sid')
            if student_sid:
                await self.sio.emit('test_terminated', {
                    'reason': 'Test terminated by teacher'
                }, room=student_sid)
                
                if student_sid in self.student_info:
                    del self.student_info[student_sid]
        
        @self.sio.event
        async def student_flagged(sid, data):
            """Student flagged by ML system"""
            logger.warning(f"Student flagged by ML: {data}")
            
            if sid not in self.student_info:
                return
            
            student_data = self.student_info[sid]
            test_code = student_data.get('test_code')
            
            # Notify teacher
            teacher_sid = self.teacher_rooms.get(test_code)
            if teacher_sid:
                await self.sio.emit('student_flagged', {
                    'sid': sid,
                    'student_name': student_data['name'],
                    'type': data.get('type'),
                    'severity': data.get('severity'),
                    'details': data.get('details'),
                    'reasons': data.get('reasons', [])
                }, room=teacher_sid)
        
        # WebRTC Signaling handlers
        @self.sio.event
        async def webrtc_offer(sid, data):
            """Forward WebRTC offer from student to teacher"""
            logger.info(f"Received WebRTC offer from {sid}")
            
            if sid not in self.student_info:
                return
            
            student_data = self.student_info[sid]
            test_code = student_data.get('test_code')
            teacher_sid = self.teacher_rooms.get(test_code)
            
            if teacher_sid:
                await self.sio.emit('webrtc_offer', {
                    'sid': sid,
                    'student_id': student_data['user_id'],
                    'student_name': student_data['name'],
                    'offer': data.get('offer'),
                    'stream_type': data.get('stream_type')  # 'camera' or 'screen'
                }, room=teacher_sid)
        
        @self.sio.event
        async def webrtc_answer(sid, data):
            """Forward WebRTC answer from teacher to student"""
            logger.info(f"Received WebRTC answer from teacher to {data.get('student_sid')}")
            
            student_sid = data.get('student_sid')
            if student_sid:
                await self.sio.emit('webrtc_answer', {
                    'answer': data.get('answer'),
                    'stream_type': data.get('stream_type')
                }, room=student_sid)
        
        @self.sio.event
        async def webrtc_ice_candidate(sid, data):
            """Forward ICE candidate between peers"""
            logger.info(f"Received ICE candidate from {sid}")
            
            # Check if sender is student or teacher
            if sid in self.student_info:
                # Student -> Teacher
                student_data = self.student_info[sid]
                test_code = student_data.get('test_code')
                teacher_sid = self.teacher_rooms.get(test_code)
                
                if teacher_sid:
                    await self.sio.emit('webrtc_ice_candidate', {
                        'sid': sid,
                        'candidate': data.get('candidate'),
                        'stream_type': data.get('stream_type')
                    }, room=teacher_sid)
            else:
                # Teacher -> Student
                student_sid = data.get('student_sid')
                if student_sid:
                    await self.sio.emit('webrtc_ice_candidate', {
                        'candidate': data.get('candidate'),
                        'stream_type': data.get('stream_type')
                    }, room=student_sid)

streaming_manager = StreamingManager()
