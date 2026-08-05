import re

# Update history.html
with open('templates/history.html', 'r', encoding='utf-8') as f:
    history = f.read()

history = re.sub(
    r'\.history-card\s*\{[^\}]+\}',
    '.history-card {\n            background: rgba(20, 20, 22, 0.4);\n            border: 1px solid rgba(255, 255, 255, 0.08);\n            border-radius: 24px;\n            padding: 1.5rem;\n            backdrop-filter: blur(40px);\n            -webkit-backdrop-filter: blur(40px);\n            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);\n            transition: var(--transition);\n            display: flex;\n            flex-direction: column;\n            gap: 1rem;\n        }',
    history
)

history = re.sub(
    r'\.history-card:hover\s*\{[^\}]+\}',
    '.history-card:hover {\n            transform: translateY(-4px);\n            border-color: rgba(255, 255, 255, 0.15);\n            background: rgba(30, 30, 32, 0.5);\n            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);\n        }',
    history
)

with open('templates/history.html', 'w', encoding='utf-8') as f:
    f.write(history)

# Update dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

dash = re.sub(
    r'\.stat-card\s*\{[^\}]+\}',
    '.stat-card {\n            background: rgba(20, 20, 22, 0.4);\n            backdrop-filter: blur(40px);\n            -webkit-backdrop-filter: blur(40px);\n            border: 1px solid rgba(255, 255, 255, 0.08);\n            border-radius: 24px;\n            padding: 1.5rem;\n            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);\n            text-align: left;\n            transition: var(--transition);\n        }',
    dash
)

dash = re.sub(
    r'\.stat-card:hover\s*\{[^\}]+\}',
    '.stat-card:hover {\n            transform: translateY(-2px);\n            border-color: rgba(255, 255, 255, 0.15);\n            background: rgba(30, 30, 32, 0.5);\n            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);\n        }',
    dash
)

dash = re.sub(
    r'\.breakdown-card\s*\{[^\}]+\}',
    '.breakdown-card {\n            background: rgba(20, 20, 22, 0.4);\n            backdrop-filter: blur(40px);\n            -webkit-backdrop-filter: blur(40px);\n            border: 1px solid rgba(255, 255, 255, 0.08);\n            border-radius: 24px;\n            padding: 2rem;\n            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);\n            text-align: left;\n        }',
    dash
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash)

print("Updated CSS successfully!")
