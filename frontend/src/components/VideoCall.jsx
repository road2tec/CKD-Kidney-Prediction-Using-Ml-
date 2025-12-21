import React, { useState, useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';
import { FaVideo, FaVideoSlash, FaMicrophone, FaMicrophoneSlash, FaPhoneSlash, FaUser, FaHeartbeat, FaExclamationTriangle } from 'react-icons/fa';
import './VideoCall.css';

const SOCKET_URL = 'http://localhost:5000';

// ICE servers for NAT traversal (using public STUN servers)
const ICE_SERVERS = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:stun2.l.google.com:19302' }
    ]
};

const VideoCall = ({ sessionId, token, userType, patientInfo, ckdReport, onCallEnd }) => {
    // State
    const [connectionStatus, setConnectionStatus] = useState('connecting');
    const [isAudioMuted, setIsAudioMuted] = useState(false);
    const [isVideoDisabled, setIsVideoDisabled] = useState(false);
    const [remoteUserJoined, setRemoteUserJoined] = useState(false);
    const [toast, setToast] = useState(null);

    // Refs
    const socketRef = useRef(null);
    const peerConnectionRef = useRef(null);
    const localStreamRef = useRef(null);
    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);

    // Show toast notification
    const showToast = useCallback((message) => {
        setToast(message);
        setTimeout(() => setToast(null), 3000);
    }, []);

    // Initialize local media stream
    const initLocalStream = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });
            localStreamRef.current = stream;
            if (localVideoRef.current) {
                localVideoRef.current.srcObject = stream;
            }
            return stream;
        } catch (error) {
            console.error('Error accessing media devices:', error);
            showToast('Failed to access camera/microphone. Please allow permissions.');
            throw error;
        }
    }, [showToast]);

    // Create peer connection
    const createPeerConnection = useCallback(() => {
        const pc = new RTCPeerConnection(ICE_SERVERS);

        // Add local tracks to peer connection
        if (localStreamRef.current) {
            localStreamRef.current.getTracks().forEach(track => {
                pc.addTrack(track, localStreamRef.current);
            });
        }

        // Handle incoming remote tracks
        pc.ontrack = (event) => {
            console.log('Received remote track:', event.streams[0]);
            if (remoteVideoRef.current && event.streams[0]) {
                remoteVideoRef.current.srcObject = event.streams[0];
            }
        };

        // Handle ICE candidates
        pc.onicecandidate = (event) => {
            if (event.candidate && socketRef.current) {
                socketRef.current.emit('ice-candidate', {
                    session_id: sessionId,
                    candidate: event.candidate
                });
            }
        };

        // Handle connection state changes
        pc.onconnectionstatechange = () => {
            console.log('Connection state:', pc.connectionState);
            if (pc.connectionState === 'connected') {
                setConnectionStatus('connected');
                showToast('Call connected!');
            } else if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
                setConnectionStatus('disconnected');
                showToast('Connection lost');
            }
        };

        peerConnectionRef.current = pc;
        return pc;
    }, [sessionId, showToast]);

    // Handle creating and sending offer
    const createOffer = useCallback(async () => {
        const pc = peerConnectionRef.current;
        if (!pc) return;

        try {
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);

            socketRef.current?.emit('offer', {
                session_id: sessionId,
                offer: offer
            });
            console.log('Offer sent');
        } catch (error) {
            console.error('Error creating offer:', error);
        }
    }, [sessionId]);

    // Handle receiving offer and sending answer
    const handleOffer = useCallback(async (data) => {
        console.log('Received offer');
        const pc = peerConnectionRef.current;
        if (!pc) return;

        try {
            await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);

            socketRef.current?.emit('answer', {
                session_id: sessionId,
                answer: answer
            });
            console.log('Answer sent');
        } catch (error) {
            console.error('Error handling offer:', error);
        }
    }, [sessionId]);

    // Handle receiving answer
    const handleAnswer = useCallback(async (data) => {
        console.log('Received answer');
        const pc = peerConnectionRef.current;
        if (!pc) return;

        try {
            await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
        } catch (error) {
            console.error('Error handling answer:', error);
        }
    }, []);

    // Handle receiving ICE candidate
    const handleIceCandidate = useCallback(async (data) => {
        const pc = peerConnectionRef.current;
        if (!pc || !data.candidate) return;

        try {
            await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
        } catch (error) {
            console.error('Error adding ICE candidate:', error);
        }
    }, []);

    // Initialize Socket.IO and WebRTC
    useEffect(() => {
        let isMounted = true;

        const init = async () => {
            try {
                // 1. Initialize local media
                await initLocalStream();

                // 2. Connect to signaling server
                const socket = io(SOCKET_URL, {
                    transports: ['websocket', 'polling']
                });
                socketRef.current = socket;

                socket.on('connect', () => {
                    console.log('Socket connected:', socket.id);

                    // Join the session room
                    socket.emit('join-room', {
                        session_id: sessionId,
                        token: token,
                        user_type: userType
                    });
                });

                socket.on('room-joined', (data) => {
                    console.log('Joined room:', data);
                    setConnectionStatus('waiting');

                    // Create peer connection after joining room
                    createPeerConnection();
                });

                socket.on('user-joined', (data) => {
                    console.log('Remote user joined:', data);
                    setRemoteUserJoined(true);
                    showToast(`${data.user_type === 'doctor' ? 'Doctor' : 'Patient'} joined the call`);

                    // If we're the patient (caller), create offer when doctor joins
                    if (userType === 'patient') {
                        setTimeout(() => createOffer(), 500);
                    }
                });

                socket.on('offer', handleOffer);
                socket.on('answer', handleAnswer);
                socket.on('ice-candidate', handleIceCandidate);

                socket.on('call-ended', (data) => {
                    showToast('Call ended');
                    if (isMounted) {
                        setTimeout(() => onCallEnd?.(), 2000);
                    }
                });

                socket.on('peer-audio-toggle', (data) => {
                    showToast(data.is_muted ? 'Remote user muted' : 'Remote user unmuted');
                });

                socket.on('peer-video-toggle', (data) => {
                    showToast(data.is_disabled ? 'Remote user disabled camera' : 'Remote user enabled camera');
                });

                socket.on('disconnect', () => {
                    console.log('Socket disconnected');
                    setConnectionStatus('disconnected');
                });

                socket.on('error', (error) => {
                    console.error('Socket error:', error);
                    showToast(error.message || 'Connection error');
                });

            } catch (error) {
                console.error('Initialization error:', error);
                setConnectionStatus('disconnected');
            }
        };

        init();

        // Cleanup
        return () => {
            isMounted = false;

            // Stop local tracks
            localStreamRef.current?.getTracks().forEach(track => track.stop());

            // Close peer connection
            peerConnectionRef.current?.close();

            // Leave room and disconnect socket
            if (socketRef.current) {
                socketRef.current.emit('leave-room', { session_id: sessionId });
                socketRef.current.disconnect();
            }
        };
    }, [sessionId, token, userType, initLocalStream, createPeerConnection, createOffer, handleOffer, handleAnswer, handleIceCandidate, showToast, onCallEnd]);

    // Toggle audio
    const toggleAudio = () => {
        if (localStreamRef.current) {
            const audioTrack = localStreamRef.current.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = !audioTrack.enabled;
                setIsAudioMuted(!audioTrack.enabled);

                socketRef.current?.emit('toggle-audio', {
                    session_id: sessionId,
                    is_muted: !audioTrack.enabled
                });
            }
        }
    };

    // Toggle video
    const toggleVideo = () => {
        if (localStreamRef.current) {
            const videoTrack = localStreamRef.current.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                setIsVideoDisabled(!videoTrack.enabled);

                socketRef.current?.emit('toggle-video', {
                    session_id: sessionId,
                    is_disabled: !videoTrack.enabled
                });
            }
        }
    };

    // End call
    const endCall = () => {
        socketRef.current?.emit('call-ended', {
            session_id: sessionId,
            ended_by: userType
        });

        setTimeout(() => onCallEnd?.(), 500);
    };

    return (
        <div className="video-call-container">
            {/* Header */}
            <div className="video-call-header">
                <h2>
                    <FaVideo /> Telemedicine Consultation
                </h2>
                <div className="call-status">
                    <span className={`status-dot ${connectionStatus}`}></span>
                    <span>
                        {connectionStatus === 'connecting' && 'Connecting...'}
                        {connectionStatus === 'waiting' && 'Waiting for other participant...'}
                        {connectionStatus === 'connected' && 'Connected'}
                        {connectionStatus === 'disconnected' && 'Disconnected'}
                    </span>
                </div>
            </div>

            {/* Main content */}
            <div className="video-call-main">
                {/* Videos */}
                <div className="videos-container">
                    <div className="remote-video-container">
                        {!remoteUserJoined ? (
                            <div className="remote-video-placeholder">
                                <FaUser />
                                <p>Waiting for {userType === 'patient' ? 'doctor' : 'patient'} to join...</p>
                            </div>
                        ) : (
                            <video
                                ref={remoteVideoRef}
                                className="remote-video"
                                autoPlay
                                playsInline
                            />
                        )}

                        {/* Local video overlay */}
                        <div className="local-video-container">
                            <video
                                ref={localVideoRef}
                                className="local-video"
                                autoPlay
                                playsInline
                                muted
                            />
                        </div>
                    </div>
                </div>

                {/* Info Panel (shown for doctors) */}
                {userType === 'doctor' && (
                    <div className="call-info-panel">
                        <div className="patient-info-card">
                            <h3><FaUser /> Patient Information</h3>
                            <div className="info-row">
                                <span className="info-label">Name</span>
                                <span className="info-value">{patientInfo?.name || 'Unknown'}</span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">Age</span>
                                <span className="info-value">{patientInfo?.age || 'N/A'}</span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">Blood Group</span>
                                <span className="info-value">{patientInfo?.blood_group || 'N/A'}</span>
                            </div>
                        </div>

                        {ckdReport && (
                            <div className="ckd-summary-card">
                                <h3><FaHeartbeat /> CKD Assessment</h3>
                                <div className="info-row">
                                    <span className="info-label">Risk Level</span>
                                    <span className={`risk-badge ${ckdReport.risk_level?.toLowerCase()}`}>
                                        {ckdReport.risk_level || 'N/A'}
                                    </span>
                                </div>
                                <div className="info-row">
                                    <span className="info-label">Confidence</span>
                                    <span className="info-value">{ckdReport.confidence ? `${(ckdReport.confidence * 100).toFixed(1)}%` : 'N/A'}</span>
                                </div>
                                {ckdReport.prediction === 'ckd' && (
                                    <div className="info-row" style={{ color: '#fca5a5' }}>
                                        <FaExclamationTriangle /> CKD Detected
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Controls */}
            <div className="call-controls">
                <button
                    className={`control-btn ${isAudioMuted ? 'muted' : 'active'}`}
                    onClick={toggleAudio}
                    title={isAudioMuted ? 'Unmute' : 'Mute'}
                >
                    {isAudioMuted ? <FaMicrophoneSlash /> : <FaMicrophone />}
                </button>

                <button
                    className={`control-btn ${isVideoDisabled ? 'muted' : 'active'}`}
                    onClick={toggleVideo}
                    title={isVideoDisabled ? 'Enable Camera' : 'Disable Camera'}
                >
                    {isVideoDisabled ? <FaVideoSlash /> : <FaVideo />}
                </button>

                <button
                    className="control-btn end-call"
                    onClick={endCall}
                    title="End Call"
                >
                    <FaPhoneSlash />
                </button>
            </div>

            {/* Toast */}
            {toast && <div className="call-toast">{toast}</div>}
        </div>
    );
};

export default VideoCall;
