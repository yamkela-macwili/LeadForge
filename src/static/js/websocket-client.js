/**
 * WebSocket Client for Real-Time Dashboard Updates
 * 
 * Handles real-time communication with the server for:
 * - Live lead feed
 * - Real-time statistics updates
 * - Activity notifications
 * - Scraping progress
 */

class LeadForgeWebSocket {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
    }

    /**
     * Initialize WebSocket connection
     */
    connect() {
        try {
            // Connect to WebSocket server
            this.socket = io({
                transports: ['websocket', 'polling'],
                reconnection: true,
                reconnectionDelay: this.reconnectDelay,
                reconnectionAttempts: this.maxReconnectAttempts
            });

            this.registerEventHandlers();
            console.log('WebSocket connection initiated');
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }

    /**
     * Register all event handlers
     */
    registerEventHandlers() {
        // Connection events
        this.socket.on('connect', () => this.onConnect());
        this.socket.on('disconnect', () => this.onDisconnect());
        this.socket.on('connection_response', (data) => this.onConnectionResponse(data));

        // Dashboard events
        this.socket.on('new_lead', (data) => this.onNewLead(data));
        this.socket.on('stats_update', (data) => this.onStatsUpdate(data));
        this.socket.on('scraping_progress', (data) => this.onScrapingProgress(data));
        this.socket.on('scraping_complete', (data) => this.onScrapingComplete(data));
        this.socket.on('activity_notification', (data) => this.onActivityNotification(data));

        // Keep-alive
        this.socket.on('pong', (data) => this.onPong(data));
    }

    /**
     * Handle successful connection
     */
    onConnect() {
        this.connected = true;
        this.reconnectAttempts = 0;
        console.log('✅ Connected to LeadForge real-time server');

        // Join dashboard room
        this.socket.emit('join_dashboard', {});

        // Show connection indicator
        this.updateConnectionStatus(true);
    }

    /**
     * Handle disconnection
     */
    onDisconnect() {
        this.connected = false;
        console.log('❌ Disconnected from server');
        this.updateConnectionStatus(false);
    }

    /**
     * Handle connection response
     */
    onConnectionResponse(data) {
        console.log('Connection response:', data.message);
    }

    /**
     * Handle new lead event
     */
    onNewLead(data) {
        console.log('📥 New lead received:', data.lead);

        // Add lead to live feed
        this.addLeadToFeed(data.lead);

        // Update lead count
        this.updateLeadCount();

        // Show notification
        this.showNotification('New Lead', `${data.lead.first_name} ${data.lead.last_name}`, 'success');

        // Play sound (optional)
        this.playNotificationSound();
    }

    /**
     * Handle stats update event
     */
    onStatsUpdate(data) {
        console.log('📊 Stats updated:', data.stats);
        this.updateDashboardStats(data.stats);
    }

    /**
     * Handle scraping progress event
     */
    onScrapingProgress(data) {
        console.log('⏳ Scraping progress:', data);
        this.updateScrapingProgress(data.niche, data.progress);
    }

    /**
     * Handle scraping complete event
     */
    onScrapingComplete(data) {
        console.log('✅ Scraping complete:', data);
        this.showNotification(
            'Scraping Complete',
            `${data.niche}: ${data.result.count} leads collected`,
            'success'
        );
        this.updateLeadCount();
    }

    /**
     * Handle activity notification event
     */
    onActivityNotification(data) {
        console.log('🔔 Activity:', data);
        this.showNotification('Activity', data.message, data.type);
    }

    /**
     * Handle pong (keep-alive response)
     */
    onPong(data) {
        console.log('🏓 Pong received');
    }

    /**
     * Add lead to live feed UI
     */
    addLeadToFeed(lead) {
        const feedContainer = document.getElementById('live-feed');
        if (!feedContainer) return;

        const leadItem = document.createElement('div');
        leadItem.className = 'live-feed-item fade-in';
        leadItem.innerHTML = `
            <div class="feed-icon">
                <i class="fas fa-user-plus"></i>
            </div>
            <div class="feed-content">
                <div class="feed-title">${lead.first_name} ${lead.last_name}</div>
                <div class="feed-meta">
                    <span class="feed-niche">${lead.niche}</span>
                    ${lead.lead_score ? `<span class="feed-score score-${this.getScoreClass(lead.lead_score)}">${lead.lead_score.toFixed(1)}</span>` : ''}
                </div>
            </div>
            <div class="feed-time">Just now</div>
        `;

        feedContainer.insertBefore(leadItem, feedContainer.firstChild);

        // Remove old items (keep max 10)
        const items = feedContainer.querySelectorAll('.live-feed-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        if (!indicator) return;

        if (connected) {
            indicator.className = 'connection-status connected';
            indicator.innerHTML = '<i class="fas fa-circle"></i> Live';
        } else {
            indicator.className = 'connection-status disconnected';
            indicator.innerHTML = '<i class="fas fa-circle"></i> Offline';
        }
    }

    /**
     * Update lead count
     */
    updateLeadCount() {
        // Refresh the page stats (simple approach)
        // In production, you'd update specific elements
        setTimeout(() => {
            const statCards = document.querySelectorAll('.stat-card h3');
            statCards.forEach(card => {
                const currentCount = parseInt(card.textContent);
                card.textContent = currentCount + 1;
            });
        }, 100);
    }

    /**
     * Update dashboard statistics
     */
    updateDashboardStats(stats) {
        // Update stat cards with new data
        Object.keys(stats).forEach(niche => {
            const statCard = document.querySelector(`[data-niche="${niche}"] h3`);
            if (statCard) {
                statCard.textContent = stats[niche];
            }
        });
    }

    /**
     * Update scraping progress
     */
    updateScrapingProgress(niche, progress) {
        const progressBar = document.querySelector(`[data-niche="${niche}"] .progress-bar`);
        if (progressBar) {
            progressBar.style.width = `${progress.percentage}%`;
            progressBar.textContent = `${progress.current}/${progress.total}`;
        }
    }

    /**
     * Show notification
     */
    showNotification(title, message, type = 'info') {
        // Use browser notifications if permitted
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png',
                badge: '/static/images/badge.png'
            });
        }

        // Also show in-app toast
        this.showToast(message, type);
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} show`;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Play notification sound
     */
    playNotificationSound() {
        try {
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => console.log('Could not play sound:', e));
        } catch (e) {
            // Sound not available
        }
    }

    /**
     * Get score class for styling
     */
    getScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    }

    /**
     * Send ping to keep connection alive
     */
    ping() {
        if (this.connected) {
            this.socket.emit('ping');
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.socket) {
            this.socket.emit('leave_dashboard', {});
            this.socket.disconnect();
        }
    }
}

// Initialize WebSocket when DOM is ready
let wsClient = null;

document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on dashboard pages
    if (document.body.classList.contains('dashboard-page') ||
        document.getElementById('live-feed')) {
        wsClient = new LeadForgeWebSocket();
        wsClient.connect();

        // Keep-alive ping every 30 seconds
        setInterval(() => {
            if (wsClient) wsClient.ping();
        }, 30000);

        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (wsClient) {
        wsClient.disconnect();
    }
});
