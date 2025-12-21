# WebRTC Signaling Server for Telemedicine
# Handles WebRTC offer/answer/ICE candidate exchange via Socket.IO

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from datetime import datetime
import json

# Will be initialized in app.py
socketio = None

def init_socketio(app):
    """Initialize Socket.IO with Flask app"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    register_events()
    return socketio

def register_events():
    """Register all Socket.IO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        print(f"[SocketIO] Client connected: {socketio.request.sid}")
        emit('connection_success', {'status': 'connected', 'sid': socketio.request.sid})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"[SocketIO] Client disconnected: {socketio.request.sid}")
    
    @socketio.on('join-room')
    def handle_join_room(data):
        """
        Join a telemedicine session room
        data: { session_id, token, user_type }
        """
        try:
            session_id = data.get('session_id')
            token = data.get('token')
            user_type = data.get('user_type', 'patient')  # patient or doctor
            
            if not session_id:
                emit('error', {'message': 'session_id is required'})
                return
            
            # Verify JWT token
            if token:
                try:
                    decoded = decode_token(token)
                    user_info = json.loads(decoded['sub']) if isinstance(decoded['sub'], str) else decoded['sub']
                    user_name = user_info.get('name', 'User')
                except Exception as e:
                    print(f"[SocketIO] Token validation error: {e}")
                    user_name = 'Unknown'
            else:
                user_name = 'Guest'
            
            # Join the session room
            join_room(session_id)
            print(f"[SocketIO] {user_type} '{user_name}' joined room: {session_id}")
            
            # Notify others in the room
            emit('user-joined', {
                'user_type': user_type,
                'user_name': user_name,
                'sid': socketio.request.sid
            }, room=session_id, include_self=False)
            
            # Confirm join to the user
            emit('room-joined', {
                'session_id': session_id,
                'message': f'Joined room successfully'
            })
            
        except Exception as e:
            print(f"[SocketIO] Error joining room: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('leave-room')
    def handle_leave_room(data):
        """Leave a telemedicine session room"""
        session_id = data.get('session_id')
        if session_id:
            leave_room(session_id)
            emit('user-left', {'sid': socketio.request.sid}, room=session_id)
            print(f"[SocketIO] Client left room: {session_id}")
    
    @socketio.on('offer')
    def handle_offer(data):
        """
        Relay WebRTC offer to the other peer
        data: { session_id, offer (SDP) }
        """
        session_id = data.get('session_id')
        offer = data.get('offer')
        
        if session_id and offer:
            print(f"[SocketIO] Relaying offer in room: {session_id}")
            emit('offer', {
                'offer': offer,
                'from_sid': socketio.request.sid
            }, room=session_id, include_self=False)
    
    @socketio.on('answer')
    def handle_answer(data):
        """
        Relay WebRTC answer to the other peer
        data: { session_id, answer (SDP) }
        """
        session_id = data.get('session_id')
        answer = data.get('answer')
        
        if session_id and answer:
            print(f"[SocketIO] Relaying answer in room: {session_id}")
            emit('answer', {
                'answer': answer,
                'from_sid': socketio.request.sid
            }, room=session_id, include_self=False)
    
    @socketio.on('ice-candidate')
    def handle_ice_candidate(data):
        """
        Relay ICE candidate to the other peer
        data: { session_id, candidate }
        """
        session_id = data.get('session_id')
        candidate = data.get('candidate')
        
        if session_id and candidate:
            emit('ice-candidate', {
                'candidate': candidate,
                'from_sid': socketio.request.sid
            }, room=session_id, include_self=False)
    
    @socketio.on('call-ended')
    def handle_call_ended(data):
        """
        Notify all participants that the call has ended
        data: { session_id, ended_by }
        """
        session_id = data.get('session_id')
        ended_by = data.get('ended_by', 'unknown')
        
        if session_id:
            print(f"[SocketIO] Call ended in room: {session_id} by {ended_by}")
            emit('call-ended', {
                'ended_by': ended_by,
                'timestamp': datetime.utcnow().isoformat()
            }, room=session_id)
    
    @socketio.on('toggle-audio')
    def handle_toggle_audio(data):
        """Notify peer about audio mute/unmute"""
        session_id = data.get('session_id')
        is_muted = data.get('is_muted', False)
        
        if session_id:
            emit('peer-audio-toggle', {
                'is_muted': is_muted,
                'from_sid': socketio.request.sid
            }, room=session_id, include_self=False)
    
    @socketio.on('toggle-video')
    def handle_toggle_video(data):
        """Notify peer about video enable/disable"""
        session_id = data.get('session_id')
        is_disabled = data.get('is_disabled', False)
        
        if session_id:
            emit('peer-video-toggle', {
                'is_disabled': is_disabled,
                'from_sid': socketio.request.sid
            }, room=session_id, include_self=False)

    print("[SocketIO] Event handlers registered")
