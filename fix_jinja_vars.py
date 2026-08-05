import os
import re

dashboard_path = 'docs/dashboard.html'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    content = f.read()
    
# Replace Jinja variables with spans
content = re.sub(r'\{\{\s*stats\.(\w+)\s*\}\}', r'<span id="stat-\1"></span>', content)

js_dashboard = """
<script>
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await apiFetch('/api/dashboard');
        const data = await response.json();
        
        for (const [key, value] of Object.entries(data)) {
            const el = document.getElementById('stat-' + key);
            if (el) {
                el.textContent = value;
            }
        }
    } catch(e) {
        console.error("Dashboard fetch error:", e);
    }
});
</script>
"""
if '</body>' in content:
    content = content.replace('</body>', js_dashboard + '\n</body>')

with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(content)


history_path = 'docs/history.html'
with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()
    
js_history = """
<script>
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await apiFetch('/api/history');
        const data = await response.json();
        
        const container = document.getElementById('history-grid-container');
        if (!container) return;
        
        container.innerHTML = ''; // clear existing dummy items
        
        if (data.history && data.history.length > 0) {
            data.history.forEach(item => {
                const card = document.createElement('div');
                card.className = 'history-card';
                card.innerHTML = `
                    <div class="card-header">
                        <h3>${item.headline}</h3>
                        <span class="date">${item.created_at}</span>
                    </div>
                    <div class="card-body">
                        <p>${item.summary_text.substring(0, 150)}...</p>
                    </div>
                    <div class="card-footer">
                        <span class="badge category">${item.primary_category || 'Uncategorized'}</span>
                        <span class="badge sentiment ${item.sentiment_label ? item.sentiment_label.toLowerCase() : ''}">${item.sentiment_label || 'Neutral'}</span>
                    </div>
                `;
                container.appendChild(card);
            });
        } else {
            container.innerHTML = '<p class="empty-state">No analysis history found.</p>';
        }
    } catch(e) {
        console.error("History fetch error:", e);
    }
});
</script>
"""
if '</body>' in content:
    content = content.replace('</body>', js_history + '\n</body>')

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)
    
print("Dashboard and history files updated to fetch data via JS.")
