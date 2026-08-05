import re
import glob

for filepath in glob.glob('templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_js = """            profileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                profileDropdown.classList.toggle('show');
            });
            document.addEventListener('click', (e) => {
                if (!profileDropdown.contains(e.target) && !profileBtn.contains(e.target)) {
                    profileDropdown.classList.remove('show');
                }
            });"""
            
    content = re.sub(
        r"profileBtn\.addEventListener\('click', \(e\) => \{[\s\S]*?profileDropdown\.classList\.remove\('show'\);\s*\}\s*\);\s*\}\s*\);",
        new_js,
        content
    )
    
    content = re.sub(
        r"profileBtn\.addEventListener\('click', \(e\) => \{[\s\S]*?profileDropdown\.classList\.remove\('show'\);\s*\}\s*\);\s*\n\s*\}\s*\);",
        new_js,
        content
    )
    
    # Just a simpler string replace since they are exactly the same
    old_js = """            profileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                profileDropdown.classList.toggle('show');
            });
            document.addEventListener('click', (e) => {
                if (!profileDropdown.contains(e.target) && e.target !== profileBtn) {
                    profileDropdown.classList.remove('show');
                }
            });"""
    content = content.replace(old_js, new_js)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
print("Updated JS successfully!")
