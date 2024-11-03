import os
import sys
from ij import IJ
from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Logger
from ij.IJ import getNumber
from ij.gui import WaitForUserDialog
from ij.plugin.frame import RoiManager

path = os.getcwd()
path_comps = path.split(os.sep)
code = os.path.expanduser('~') + os.sep + "Trackmate Library"
sys.path.append(code)

from RunTrackmate import process_glass_surface
from RunTrackmate import get_tmd_root
from RunTrackmate import get_user_input


def MultipleCellGlass():

    model.getLogger().log("\n\nReprocessing Glass")

    # -------------------------------
    # Determine where the root is
    # It should be something like /User/Hans/Trackmate Data
    # -------------------------------

    tmd_root = get_tmd_root()
    
    imp = IJ.getImage()
    if imp is None:
        print("No image selected")
        model.getLogger().log("No image selected")
        return -1

    image_title = imp.getTitle().replace(".nd2", "")

    # Ask for threshold, and probe info
    probe, type_probe, threshold, concentration_probe = get_user_input(image_title)

    # Make sure there is an instance of the ROI Manager

    rm = RoiManager.getInstance()
    if not rm:
        rm = RoiManager()

    # If there is a roi called 'glass' delete it

    ind = rm.getIndex("Glass")
    if ind != -1:
        rm.select(ind)
        rm.runCommand("Delete")

    # Set some default options

    rm.runCommand("Show All")
    IJ.setTool("Elliptical")

    # -------------------------------
    # Ask for the definitions and go
    # -------------------------------

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

    if MultipleCellGlass() != 0:
        print("\n\nRoutine aborted with error")
        model.getLogger().log("\n\nRoutine aborted with error")
    else:
        print("\n\nRoutine completed successfully")
        model.getLogger().log("\n\nRoutine completed successfully")
