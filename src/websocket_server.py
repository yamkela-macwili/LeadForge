"""
WebSocket server for real-time dashboard updates.

Provides real-time communication between server and clients for:
- Live lead feed (new leads appear instantly)
- Real-time statistics updates
- Activity notifications
- Scraping progress updates
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from logger import logger
from datetime import datetime

# Initialize SocketIO
socketio = None

def init_socketio(app):
    """Initialize SocketIO with the Flask app."""
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",  # Allow all origins for development
        async_mode='threading',  # Use threading instead of eventlet for Python 3.13 compatibility
        logger=True,
        engineio_logger=False
    )
    
    # Register event handlers
    register_handlers()
    
    logger.info("WebSocket server initialized")
    return socketio


def register_handlers():
    """Register WebSocket event handlers."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {request.sid}")
        emit('connection_response', {
            'status': 'connected',
            'message': 'Successfully connected to LeadForge real-time server',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_dashboard')
    def handle_join_dashboard(data):
        """Client joins the dashboard room for updates."""
        room = 'dashboard'
        join_room(room)
        logger.info(f"Client {request.sid} joined {room}")
        emit('joined_room', {'room': room}, room=request.sid)
    
    @socketio.on('leave_dashboard')
    def handle_leave_dashboard(data):
        """Client leaves the dashboard room."""
        room = 'dashboard'
        leave_room(room)
        logger.info(f"Client {request.sid} left {room}")
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping from client (keep-alive)."""
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})


# Event emitters (called from other parts of the application)

def emit_new_lead(lead_data):
    """
    Emit event when a new lead is created.
    
    Args:
        lead_data: Dictionary containing lead information
    """
    if socketio:
        socketio.emit('new_lead', {
            'lead': lead_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='dashboard')
        logger.debug(f"Emitted new_lead event for lead {lead_data.get('id')}")


def emit_stats_update(stats_data):
    """
    Emit event when statistics are updated.
    
    Args:
        stats_data: Dictionary containing updated statistics
    """
    if socketio:
        socketio.emit('stats_update', {
            'stats': stats_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='dashboard')
        logger.debug("Emitted stats_update event")


def emit_scraping_progress(niche, progress_data):
    """
    Emit scraping progress updates.
    
    Args:
        niche: The niche being scraped
        progress_data: Dictionary with progress information
    """
    if socketio:
        socketio.emit('scraping_progress', {
            'niche': niche,
            'progress': progress_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='dashboard')
        logger.debug(f"Emitted scraping_progress for {niche}")


def emit_scraping_complete(niche, result_data):
    """
    Emit event when scraping completes.
    
    Args:
        niche: The niche that was scraped
        result_data: Dictionary with scraping results
    """
    if socketio:
        socketio.emit('scraping_complete', {
            'niche': niche,
            'result': result_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='dashboard')
        logger.info(f"Emitted scraping_complete for {niche}")


def emit_activity_notification(activity_type, message, data=None):
    """
    Emit general activity notification.
    
    Args:
        activity_type: Type of activity (info, success, warning, error)
        message: Human-readable message
        data: Optional additional data
    """
    if socketio:
        socketio.emit('activity_notification', {
            'type': activity_type,
            'message': message,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat()
        }, room='dashboard')
        logger.debug(f"Emitted activity_notification: {activity_type} - {message}")


def get_socketio():
    """Get the SocketIO instance."""
    return socketio
