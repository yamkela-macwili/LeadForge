/**
 * Recommendations Client
 * Fetches and displays trending niches and personalized recommendations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Only run on dashboard
    if (!document.getElementById('trending-niches')) return;

    fetchTrendingNiches();
    fetchRecommendations();
});

/**
 * Fetch trending niches from API
 */
async function fetchTrendingNiches() {
    const container = document.getElementById('trending-niches');

    try {
        const response = await fetch('/api/recommendations/trending?days=7&limit=5');

        if (!response.ok) throw new Error('Failed to fetch trends');

        const data = await response.json();
        renderTrendingNiches(data.trending, container);

    } catch (error) {
        console.error('Error fetching trends:', error);
        container.innerHTML = '<div class="loading-placeholder">Could not load trends</div>';
    }
}

/**
 * Render trending niches list
 */
function renderTrendingNiches(trends, container) {
    if (!trends || trends.length === 0) {
        container.innerHTML = '<div class="loading-placeholder">No trending niches yet</div>';
        return;
    }

    container.innerHTML = trends.map(trend => `
        <div class="trending-item">
            <div class="trend-info">
                <i class="fas fa-chart-line trend-up"></i>
                <span>${trend.niche}</span>
            </div>
            <div class="trend-count">${trend.count} leads</div>
        </div>
    `).join('');
}

/**
 * Fetch personalized recommendations
 */
async function fetchRecommendations() {
    const container = document.getElementById('recommended-leads');

    try {
        const response = await fetch('/api/recommendations/for-you?limit=5');

        if (!response.ok) throw new Error('Failed to fetch recommendations');

        const data = await response.json();
        renderRecommendations(data.recommendations, container);

    } catch (error) {
        console.error('Error fetching recommendations:', error);
        container.innerHTML = '<div class="loading-placeholder">Could not load recommendations</div>';
    }
}

/**
 * Render recommendations list
 */
function renderRecommendations(leads, container) {
    if (!leads || leads.length === 0) {
        container.innerHTML = '<div class="loading-placeholder">No recommendations yet</div>';
        return;
    }

    container.innerHTML = leads.map(lead => `
        <div class="recommended-item">
            <div class="rec-header">
                <span class="rec-name">${lead.first_name} ${lead.last_name}</span>
                <span class="rec-score">${lead.lead_score ? lead.lead_score.toFixed(0) : 'N/A'}</span>
            </div>
            <div class="rec-details">
                <span><i class="fas fa-building"></i> ${lead.company || 'N/A'}</span>
                <span><i class="fas fa-tag"></i> ${lead.niche}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Helper to get JWT token (assuming it's stored in cookie or localStorage)
 * For this MVP, we'll assume the browser handles cookies automatically for same-origin requests
 * or we might need to extract it if using Bearer auth header explicitly.
 * 
 * Since the backend uses @jwt_required(), we need to send the token.
 * In the current app, the token is likely stored in a cookie 'access_token_cookie' 
 * if using set_access_cookies, or we need to get it from somewhere.
 * 
 * Checking auth.py/login route: it uses set_access_cookies.
 * So the browser will send the cookie automatically.
 * 
 * However, if the API expects Authorization header, we need to extract it.
 * Flask-JWT-Extended by default looks in headers. If configured for cookies, it looks in cookies.
 * Let's assume cookies are working since it's a browser app.
 * 
 * BUT, the fetch calls above use 'Authorization': Bearer ...
 * We need to remove that if we rely on cookies, or get the token.
 * 
 * Let's check config.py to see JWT_TOKEN_LOCATION.
 */
function getAuthToken() {
    // Placeholder - if we need to manually send token
    return localStorage.getItem('access_token') || '';
}
