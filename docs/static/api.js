// Configuration for GitHub Pages Frontend
// Update this URL to match your Render backend URL once deployed
const API_BASE = 'http://127.0.0.1:5000'; // Change to Render URL for production

// Helper function for fetch with credentials
async function apiFetch(endpoint, options = {}) {
    if (!options.headers) {
        options.headers = {};
    }
    options.headers['Content-Type'] = 'application/json';
    
    // Pass user_id if logged in, since cross-domain cookies are blocked
    const userId = localStorage.getItem('user_id');
    if (userId) {
        if (!options.body && options.method !== 'GET') {
            options.body = JSON.stringify({ user_id: userId });
        } else if (options.body && typeof options.body === 'string') {
            try {
                let bodyObj = JSON.parse(options.body);
                bodyObj.user_id = userId;
                options.body = JSON.stringify(bodyObj);
            } catch(e){}
        }
    }
    
    options.credentials = 'include';
    
    return fetch(API_BASE + endpoint, options);
}
