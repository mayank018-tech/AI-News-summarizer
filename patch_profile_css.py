import re
import os

files_to_update = ['templates/dashboard.html', 'templates/history.html', 'templates/edit_profile.html']

for filepath in files_to_update:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Only add if not already present
        if '.profile-container {' not in content:
            content = content.replace(
                '.profile-btn {',
                '.profile-container {\n            position: relative;\n            display: inline-block;\n        }\n\n        .profile-btn {'
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filepath}")
        else:
            print(f"Already updated {filepath}")
    else:
        print(f"File {filepath} not found")

print("Done patching profile-container CSS!")
