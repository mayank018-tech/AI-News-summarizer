import re
import glob
import os

def patch_mousemove():
    html_files = glob.glob('templates/*.html')
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # The new optimized script
        optimized_script = """
        let isTicking = false;
        window.addEventListener('mousemove', (e) => {
            if (!isTicking) {
                window.requestAnimationFrame(() => {
                    const x = (e.clientX / window.innerWidth) * 100;
                    const y = (e.clientY / window.innerHeight) * 100;
                    
                    // Apply variables to overlay instead of documentElement to prevent layout thrashing
                    const ov = document.getElementById('bg-overlay');
                    if (ov) {
                        ov.style.setProperty('--mouse-x', `${x}%`);
                        ov.style.setProperty('--mouse-y', `${y}%`);
                    }

                    const moveX = (e.clientX - window.innerWidth / 2) * -0.015;
                    const moveY = (e.clientY - window.innerHeight / 2) * -0.015;
                    
                    const cont = document.getElementById('bg-container');
                    if (cont) {
                        cont.style.transform = `translate(${moveX}px, ${moveY}px) scale(1.03)`;
                    }
                    isTicking = false;
                });
                isTicking = true;
            }
        }, { passive: true });
"""
        
        # Replace window.addEventListener('mousemove', ...
        content = re.sub(
            r"window\.addEventListener\('mousemove',\s*\(e\)\s*=>\s*\{.*?(?:container\.style\.transform[^;]+;|container\.style\.transform.*?\`.*?\`\s*;|container\.style\.transform[^;]+;)\s*\}\);",
            optimized_script.strip(),
            content,
            flags=re.DOTALL
        )
        
        # Replace document.addEventListener('mousemove', ... in auth pages
        content = re.sub(
            r"document\.addEventListener\('mousemove',\s*\(e\)\s*=>\s*\{.*?(?:bgContainer\.style\.transform[^;]+;|bgContainer\.style\.transform.*?\`.*?\`\s*;|bgContainer\.style\.transform[^;]+;)\s*\}\);",
            optimized_script.strip(),
            content,
            flags=re.DOTALL
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
patch_mousemove()
print("Mousemove optimized!")
