
import os

def update_file(filepath, replacements):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for search, replace in replacements.items():
            # Avoid double replacement if already fixed
            if replace not in content: 
                content = content.replace(search, replace)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
        else:
            print(f"No changes: {filepath}")
    except Exception as e:
        print(f"Error updating {filepath}: {e}")

# Base directories
base_dir = r"c:\Users\hasee\OneDrive\Desktop\Bloodify_Professional_Final\frontend2"
admin_dir = os.path.join(base_dir, "admin", "pages")
user_dir = os.path.join(base_dir, "user", "pages")
auth_dir = os.path.join(base_dir, "auth")

# Replacements for Admin/User pages (2 levels deep)
deep_replacements = {
    'href="css/': 'href="../../css/',
    'src="js/': 'src="../../js/',
    'src="config/': 'src="../../config/',
    'href="assets/': 'href="../../assets/',
    'src="assets/': 'src="../../assets/',
    # Fix Sidebar Links if they point to root files (not needed if they are relative filenames)
    # But wait, sidebar links in dashboard.html were just "dashboard.html". Since they are siblings now, they are fine.
}

# Replacements for Auth pages (1 level deep)
shallow_replacements = {
    'href="css/': 'href="../css/',
    'src="js/': 'src="../js/',
    'src="config/': 'src="../config/',
    'href="assets/': 'href="../assets/',
    'src="assets/': 'src="../assets/',
}

# Process Admin Pages
if os.path.exists(admin_dir):
    for filename in os.listdir(admin_dir):
        if filename.endswith(".html"):
            update_file(os.path.join(admin_dir, filename), deep_replacements)

# Process User Pages
if os.path.exists(user_dir):
    for filename in os.listdir(user_dir):
        if filename.endswith(".html"):
            update_file(os.path.join(user_dir, filename), deep_replacements)

# Process Auth Pages
if os.path.exists(auth_dir):
    for filename in os.listdir(auth_dir):
        if filename.endswith(".html"):
            update_file(os.path.join(auth_dir, filename), shallow_replacements)
