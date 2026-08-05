document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await apiFetch('/api/dashboard');
        const stats = await response.json();
        
        // Populate DOM elements (assuming they have specific classes or structure)
        // Let's add simple mapping logic. We will find elements containing the old jinja labels if any,
        // or we need to rely on the fact that I didn't replace the jinja tags in dashboard.html.
        // Wait, did I replace them in build_static? No, I only replaced url_for and if statements.
        // So dashboard.html still has {{ stats.total }} as plain text in the HTML!
        
        // I should re-write the HTML generation step to give these spans IDs.
    } catch(e) {
        console.error(e);
    }
});
