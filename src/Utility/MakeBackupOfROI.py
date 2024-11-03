import os
from shutil import copyfile

# Specify the Omero directory on the Windows PC
omero_dir = 'd:/Omero/'
omero_dir = '/Users/hans/Downloads/Omero'
dest_dir  = '/Users/hans/Downloads/roi'
# Specify the directory where the Fileset are stored


# Check if destination directory exists
if not os.path.isdir(dest_dir):
    os.makedirs(dest_dir)

# Make sure it is empty, otherwise stop
if len(os.listdir(dest_dir)) != 0:
    print("Directory is not empty.")
#    exit()

# Loop through all directories

all_dirs = os.listdir(omero_dir)

for d in all_dirs:

    if d.startswith('.'):
        continue
    dir = omero_dir + '/' + d
    # Find all files with extension ROI)
    all_files = os.listdir(dir)

    for f in all_files:
        if f.startswith('.'):
            continue
        if f.endswith('.roi'):
            print(f)
            destfile = dest_dir + '/'+ f
            sourcefile = omero_dir + '/'+ d + '/' + f
            copyfile(sourcefile, destfile)