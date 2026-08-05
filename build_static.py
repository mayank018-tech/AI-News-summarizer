import os
import re
import shutil

src_dir = 'templates'
static_src = 'static'
dest_dir = 'docs'

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Copy static files
dest_static = os.path.join(dest_dir, 'static')
if os.path.exists(dest_static):
    shutil.rmtree(dest_static)
shutil.copytree(static_src, dest_static)

# Basic Jinja replacements
replacements = {
    r"\{\{\s*url_for\('static',\s*filename=['\"]([^'\"]+)['\"]\)\s*\}\}": r"static/\1",
    r"\{\{\s*url_for\('index'\)\s*\}\}": r"index.html",
    r"\{\{\s*url_for\('dashboard'\)\s*\}\}": r"dashboard.html",
    r"\{\{\s*url_for\('history'\)\s*\}\}": r"history.html",
    r"\{\{\s*url_for\('login'\)\s*\}\}": r"login.html",
    r"\{\{\s*url_for\('signup'\)\s*\}\}": r"signup.html",
    r"\{\{\s*url_for\('logout'\)\s*\}\}": r"login.html",
    r"\{\{\s*url_for\('edit_profile'\)\s*\}\}": r"edit_profile.html",
}

js_auth_logic = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    const userId = localStorage.getItem('user_id');
    const guestState = localStorage.getItem('guest_mode');
    
    // Auth elements to toggle
    const loginLink = document.querySelector('a[href="login.html"]');
    const signupLink = document.querySelector('a[href="signup.html"]');
    const logoutLink = document.querySelector('a[href="login.html"]'); 
    
    // We assume the logout link was replaced with login.html by the regex but we can identify it by text content
    const navLinks = document.querySelectorAll('.nav-links a');
    let realLogoutLink = null;
    navLinks.forEach(link => {
        if(link.textContent.includes('Logout')) {
            realLogoutLink = link;
        }
    });

    const dashLink = document.querySelector('a[href="dashboard.html"]');
    const histLink = document.querySelector('a[href="history.html"]');
    
    if (realLogoutLink) {
        realLogoutLink.href = "#";
        realLogoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            localStorage.removeItem('guest_mode');
            window.location.href = 'login.html';
        });
    }

    if (userId) {
        if(loginLink) loginLink.style.display = 'none';
        if(signupLink) signupLink.style.display = 'none';
    } else if (guestState === 'true') {
        if(loginLink) loginLink.style.display = 'none';
        if(signupLink) signupLink.style.display = 'none';
        if(realLogoutLink) realLogoutLink.textContent = "Exit Guest Mode";
    } else {
        if(realLogoutLink) realLogoutLink.style.display = 'none';
        if(dashLink) dashLink.style.display = 'none';
        if(histLink) histLink.style.display = 'none';
    }
});
</script>
"""

for file in os.listdir(src_dir):
    if file.endswith('.html'):
        with open(os.path.join(src_dir, file), 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Strip Jinja if statements for now and let JS handle auth toggle
        content = re.sub(r'\{%\s*if session\.get\([^\)]+\)\s*%\}', '', content)
        content = re.sub(r'\{%\s*else\s*%\}', '', content)
        content = re.sub(r'\{%\s*endif\s*%\}', '', content)
        
        # Strip specific summary loops in history.html
        if file == 'history.html':
            content = re.sub(r'\{%\s*for summary in summaries\s*%\}', '', content)
            content = re.sub(r'\{\{\s*summary\.headline\s*\}\}', '<span class="hist-headline"></span>', content)
            content = re.sub(r'\{\{\s*summary\.created_at\.strftime\([^)]+\)\s*\}\}', '<span class="hist-date"></span>', content)
            content = re.sub(r'\{\{\s*summary\.primary_category\s*\}\}', '<span class="hist-cat"></span>', content)
            content = re.sub(r'\{\{\s*summary\.sentiment_label\s*\}\}', '<span class="hist-sent"></span>', content)
            content = re.sub(r'\{\{\s*summary\.id\s*\}\}', '1', content)
            # Add JS loader placeholder
            content = content.replace('<div class="history-grid">', '<div class="history-grid" id="history-grid-container">')

        # Replace loops
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
            
        # Inject JS Auth Logic before </body>
        if '</body>' in content:
            content = content.replace('</body>', js_auth_logic + '\n</body>')
            
        with open(os.path.join(dest_dir, file), 'w', encoding='utf-8') as f:
            f.write(content)
            
print("Static site built in docs/ folder.")
