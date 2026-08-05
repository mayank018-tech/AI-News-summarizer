import os
import re

docs_dir = 'docs'

for file in os.listdir(docs_dir):
    if file.endswith('.html'):
        path = os.path.join(docs_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add api.js before the first <script> tag if not already there
        if '<script src="static/api.js"></script>' not in content and '<head>' in content:
            content = content.replace('</head>', '    <script src="static/api.js"></script>\n</head>')

        # Convert fetch('/ to apiFetch('/
        # This regex looks for fetch( followed by '/...
        content = re.sub(r'fetch\([\'\"](\/[^\'\"]+)[\'\"]', r"apiFetch('\1'", content)
        
        # Specific fixes for login/signup saving user_id
        if file in ['login.html', 'signup.html']:
            if "window.location.href = data.redirect" in content and "setItem" not in content:
                content = content.replace("window.location.href = data.redirect;", "localStorage.setItem('user_id', data.user_id); localStorage.setItem('username', data.username); window.location.href = data.redirect || 'index.html';")

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
print("Frontend JS updated to use API endpoint.")
