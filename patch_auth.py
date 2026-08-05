import re

with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Add after_request handler if not exists
if '@app.after_request' not in app_code:
    cache_control_code = """
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

"""
    app_code = app_code.replace('app = Flask(__name__)\n', 'app = Flask(__name__)\n' + cache_control_code)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("Added cache-control headers to app.py")


# Fix edit_profile.html UI
with open('templates/edit_profile.html', 'r', encoding='utf-8') as f:
    edit_html = f.read()

edit_html = re.sub(
    r'\.edit-profile-container\s*\{[^\}]+\}',
    '.edit-profile-container {\n            width: 90%;\n            max-width: 440px;\n            background: rgba(20, 20, 22, 0.4);\n            border: 1px solid rgba(255, 255, 255, 0.08);\n            border-radius: 24px;\n            backdrop-filter: blur(40px);\n            -webkit-backdrop-filter: blur(40px);\n            padding: 2.5rem;\n            margin: 7rem auto 2rem auto;\n            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);\n            display: flex;\n            flex-direction: column;\n            align-items: stretch;\n            position: relative;\n            z-index: 10;\n        }',
    edit_html
)

with open('templates/edit_profile.html', 'w', encoding='utf-8') as f:
    f.write(edit_html)
print("Updated edit_profile.html styling")
