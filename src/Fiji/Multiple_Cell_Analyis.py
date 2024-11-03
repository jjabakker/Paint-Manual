import os
import sys

from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import Model
from ij import IJ
from ij.gui import WaitForUserDialog
from ij.plugin.frame import RoiManager

path = os.getcwd()
path_comps = path.split(os.sep)
code = os.path.expanduser('~') + os.sep + "Trackmate Library"
sys.path.append(code)

from RunTrackmate import process_full_image
from RunTrackmate import process_selected_cells
from RunTrackmate import process_glass_surface
from RunTrackmate import create_directories
from RunTrackmate import get_tmd_root
from RunTrackmate import get_user_input


def multiple_cell_analysis():

    # -------------------------------
    # Determine where the Trackmate Data root is
    # It should be something like /User/Hans/Trackmate Data
    # -------------------------------

    tmd_root = get_tmd_root()

    if not os.path.isdir(tmd_root):
        print("Please ensure that a directory /User/*****/Trackmate Data exists (with xxxxx the user name)")
        model.getLogger().log(
            "Please ensure that a directory /User/Hans/Trackmate Data exists (with xxxxx the user name)")
        return -1

    imp = IJ.getImage()
    if imp is None:
        print("No image selected")
        model.getLogger().log("No image selected")
        return -1
    image_title = imp.getTitle().replace(".nd2", "")

    # Prepare the directory structure
    create_directories(tmd_root, image_title)

    # Ask for probe information and threshold
    probe, type_probe, threshold, concentration_probe = get_user_input(image_title)

    # Run the full image
    process_full_image(threshold, tmd_root, image_title, probe, type_probe, concentration_probe)

    print("\nCompleted processing full image\n\n")
    model.getLogger().log("\nCompleted processing full image\n\n")

    # Make sure there is an instance of the ROI Manager
    rm = RoiManager.getInstance()
    if not rm:
        rm = RoiManager()

    # Set some default options
    rm.runCommand("Show All")
    IJ.setTool("Elliptical")

    # There should be no ROIs in this stage, so remove any that may be there
    rm.runCommand("Reset")
    rm.runCommand("Sort")  # A trick to update the window

    # --------------------------------------------------
    # Ask user to define cells and run TrackMate on them
    # --------------------------------------------------

    my_wait = WaitForUserDialog("Cell definition",
                                "Select each cell and press 'T' to add to ROI Manager.\n\n\nPress OK when done")
    my_wait.show()
    nr_cells = process_selected_cells(threshold, tmd_root, image_title, probe, type_probe, concentration_probe)

    print("\nCompleted processing " + str(nr_cells) + " cells.\n\n")
    model.getLogger().log("\nCompleted processing " + str(nr_cells) + " cells.\n\n")

    # ----------------------------------------------------------
    # Then run Trackmate on everything except the selected cells
    # ----------------------------------------------------------

    my_wait = WaitForUserDialog("Glass definition",
                                "Select a set of ROI's that will exclude the glass areas. \n\n\nPress OK when done")
    my_wait.show()
    process_glass_surface(threshold, tmd_root, image_title, probe, type_probe, concentration_probe)

    return 0


if __name__ == "__main__":

    model = Model()
    model.setLogger(Logger.IJ_LOGGER)

    # -------------------------------
    # Determine where the Code is and add the directory to the path
    # Then the modules can be loaded
    # -------------------------------

    if multiple_cell_analysis() != 0:
        print("\n\nRoutine aborted with error")
        model.getLogger().log("\n\nRoutine aborted with error")
    else:
        print("\n\nRoutine completed successfully")
        model.getLogger().log("\n\nRoutine completed successfully")
