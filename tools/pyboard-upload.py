import os
import glob
import shutil

print("Starting upload...")

paths = ['E:/', 'F:/', 'G:/', '/mnt/']

dest_root = False

for p in paths:
    if os.path.isfile(p + 'boot.py'):
        dest_root = p
        break

if not dest_root:
    print("Error, no Pyboard found")
    exit(99)

# Copy files
files = glob.glob("**/*py", recursive=True)
for file in files:

    # Complete source and destination
    src = os.path.realpath(file)
    dest = os.path.realpath(dest_root + file)

    # Create subdirectories
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    print("Writing", dest)
    shutil.copyfile(src, dest)

print("Done")
