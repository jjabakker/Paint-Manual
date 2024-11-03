import os

# Specify the Omero directory on the Windows PC
omero_dir = 'd:/Omero/'
omero_dir = '/Users/hans/Downloads/'

# Specify the directory where the Fileset are stored
source_dir = 'Omero'

# Loop through all Fileset directories
dest_dir = omero_dir+source_dir
all_dirs = os.listdir(dest_dir)

for d in all_dirs:

    # There should really be only directories named 'Fileset*****')
    # If there is something else (for example an image file already copied) ignore it
    if d[0] != 'F':
        continue
    src_path = dest_dir + '/' + d

    # Now list all the files in a 'Fileset****' directory
    # There should be only one image file

    all_files = os.listdir(src_path)
    if len(all_files) == 0:
        print(f"Directory {d} does not contain a file.")
        continue
    elif len(all_files) != 1:
        print(f"Directory {d} does contain multiple files. Cannot be right, we stop.")
        exit()

    for f in all_files:
        file_to_move = src_path + '/' + f
        dest_file = dest_dir + '/' + f
        print(f"The file to move is {file_to_move} to {dest_file}")
        os.rename(file_to_move, dest_file)

    # Then delete the 'Fileset****' directory
    del_dir = dest_dir + '/' + d
    print(f"The directory to delete is {del_dir}")
    os.rmdir(del_dir)
