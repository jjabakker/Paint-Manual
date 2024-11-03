# -*- coding: utf-8 -*-

import csv
import os

import java.lang
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import Model
from ij import IJ
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager
from fiji.util.gui import GenericDialogPlus
from TrackMate import paint_trackmate


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

# Determine where the root is. We are looking for something like /Users/Hans/
def get_tmd_root():
    return os.path.expanduser('~') + os.sep + "Trackmate Data"


# Determine the file open attribute, depending on whether you run from macOS or Windows
def get_file_open_attribute():
    ver = java.lang.System.getProperty("os.name").lower()
    if ver.startswith("windows"):
        open_attribute = "wb"
    else:
        open_attribute = "w"
    return open_attribute


# Get the threshold and probe information
def get_user_input(image_title):
    threshold = 5.0
    probe = "Not Specified"
    type_probe = "Not Specified"
    concentration_probe = 1
    selection = False

    root = get_tmd_root()
    trackmate_file = root + os.sep + image_title + os.sep + image_title + "-glass-results.csv"

    # See if there is a glass results file. If there is, take the values from there (apparently this function was
    # invoked when redrawing the glass surface). Otherwise, ask the user for the info

    try:
        f = open(trackmate_file, 'rt')
        reader = csv.reader(f)
        print("success")
        print(reader)
        i = 0
        for row in reader:
            if i == 1:
                probe = row[1]
                type_probe = row[2]
                concentration_probe = row[3]
                threshold = float(row[4])
            i += 1
    except:

        gui = GenericDialogPlus("PAINT input")
        gui.addNumericField("Quality Threshold", threshold, 1)
        gui.addNumericField("Concentration Probe", concentration_probe, 1)
        gui.addRadioButtonGroup("Probe", ["1 Mono", "2 Mono", "6 Mono",
                                          "1 Bi", "2 Bi", "6 Bi",
                                          "1 Tri", "2 Tri", "6 Tri"],
                                3, 3, "1 Mono")
        gui.addRadioButtonGroup("Type of Probe", ["Simple", "Peptide"], 1, 2, "Simple")

        gui.showDialog()

        if gui.wasOKed():
            threshold = gui.getNextNumber()
            concentration_probe = gui.getNextNumber()
            probe = gui.getNextRadioButton()
            type_probe = gui.getNextRadioButton()

            if probe == "null" or type_probe == "null":
                print "Need a selection for probes"
            else:
                selection = True

    return probe, type_probe, threshold, concentration_probe


# Delete all files in the directories that might be there from previous runs

def delete_files_in_directory(directory_path):
    try:
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except OSError:
        print("Error occurred while deleting files.")


# Create the directories
def create_directories(root, image_title):
    root = root + os.sep + image_title + os.sep
    if not os.path.isdir(root):
        os.makedirs(root)
    else:
        delete_files_in_directory(root)

    roi_root = root + os.sep + "roi" + os.sep  # Where all cells roi files will be stored
    if not os.path.isdir(roi_root):  # Create the roi directory if it does not exist
        os.makedirs(roi_root)
    else:
        delete_files_in_directory(roi_root)

    tracks_root = root + os.sep + "tracks" + os.sep  # Where all cells track files will be stored
    if not os.path.isdir(tracks_root):  # Create the tracks directory if it does not exist
        os.makedirs(tracks_root)
    else:
        delete_files_in_directory(tracks_root)

    plt_root = root + os.sep + "plt" + os.sep  # Where all cells plt files will be stored
    if not os.path.isdir(plt_root):  # Create the plt directory if it does not exist (needed for Python)
        os.makedirs(plt_root)
    else:
        delete_files_in_directory(plt_root)

    img_root = root + os.sep + "img" + os.sep  # Where all cells img files will be stored
    if not os.path.isdir(img_root):  # Create the img directory if it does not exist
        os.makedirs(img_root)
    else:
        delete_files_in_directory(img_root)

    return root, roi_root, tracks_root, plt_root, img_root


# -----------------------------------------------------------------------------
# The main functions function
# -----------------------------------------------------------------------------

def process_full_image(threshold, tmd_root, image_title, probe, type_probe, concentration_probe):
    trackmate_file = tmd_root + os.sep + image_title + os.sep + image_title + "-full-results.csv"

    new_root = tmd_root + os.sep + image_title + os.sep
    image_root = new_root + "img" + os.sep
    tracks_filename = new_root + "tracks" + os.sep + image_title + "-full-tracks.csv"

    tiff_filename = image_root + image_title + ".tiff"
    nr_spots, total_tracks, long_tracks = paint_trackmate(threshold, tracks_filename, tiff_filename)

    # ----------------------
    # Write the tracks file
    # ----------------------

    open_attribute = get_file_open_attribute()
    export_file = open(trackmate_file, open_attribute)
    export_writer = csv.writer(export_file)

    fields = ["Image Title", "Probe", "Type Probe",  "Concentration", "Threshold", "F Spots", "F Total Tracks", "F Long Tracks",
              "F Area"]
    export_writer.writerow(fields)

    area = 82.0864 * 82.0864

    fields = [image_title, probe, type_probe, concentration_probe, threshold, nr_spots, total_tracks, long_tracks, area]
    export_writer.writerow(fields)

    export_file.close()


def process_glass_surface(threshold, tmd_root, image_title, probe, type_probe, concentration_probe):
    model = Model()
    model.setLogger(Logger.IJ_LOGGER)

    rm = RoiManager.getInstance()
    if not rm:
        rm = RoiManager()

    # If there is a roi called glass delete it
    ind = rm.getIndex("Glass")
    if ind != -1:
        rm.select(ind)
        rm.runCommand("Delete")

    rm.runCommand("Show None")  # Show
    rm.deselect()  # By deselecting all, the next OR will work on everything
    rm.runCommand('Or')  # The OR defines the OR of all ROIs
    rm.runCommand('Add')  # Save it

    IJ.makeRectangle(0, 0, 512, 512)  # Create the rectangle
    rm.runCommand('Add')  # Save it

    count = rm.getCount()
    rm.setSelectedIndexes([count - 1, count - 2])  # Select the Rectangle and the Or
    rm.runCommand('XOr')  # Do the XOR so that you select everything outside the OR
    rm.runCommand('Add')  # Save it
    rm.runCommand("Delete")  # Delete the
    rm.runCommand("Show None")
    rm.rename(rm.getCount() - 1, "Glass")
    rm.runCommand("Sort")

    rm.select(rm.getCount() - 1)
    ResultsTable.getResultsTable().reset()  # Empty the results table
    rm.runCommand("Measure")
    area = round(ResultsTable.getResultsTable().getValueAsDouble(0, 0),
                 0)  # There is only row, AREA is the first columns

    # Define filee names
    roi_filename       = tmd_root + os.sep + image_title + os.sep + "roi" + os.sep + image_title + "-glass.roi"
    trackmate_filename = tmd_root + os.sep + image_title + os.sep + image_title + "-glass-results.csv"
    tracks_filename    = tmd_root + os.sep + image_title + os.sep + "tracks" + os.sep + image_title + "-glass-tracks.csv"
    tiff_filename      = tmd_root + os.sep + image_title + os.sep + "img" + os.sep + image_title + "-glass-tracks.tiff"

    # Save the ROI file
    rm.save(roi_filename)

    # Run trackmate
    nr_spots, total_tracks, long_tracks = paint_trackmate(threshold, tracks_filename, tiff_filename)

    # Write the trackmate results file
    open_attribute = get_file_open_attribute()
    export_file = open(trackmate_filename, open_attribute)
    export_writer = csv.writer(export_file)

    header = ["Image Title", "Probe", "Type Probe", "Concentration", "Threshold", "G Spots", "G Total Tracks",
              "G Long Tracks", "G Area"]
    export_writer.writerow(header)

    fields = [image_title, probe, type_probe, concentration_probe, threshold, nr_spots, total_tracks, long_tracks, area]
    export_writer.writerow(fields)

    export_file.close()


def process_selected_cells(threshold, tmd_root, image_title, probe, type_probe, concentration_probe):

    model = Model()
    model.setLogger(Logger.IJ_LOGGER)

    track_filename_stub  = tmd_root + os.sep + image_title + os.sep + "tracks" + os.sep + image_title
    roi_filename_stub    = tmd_root + os.sep + image_title + os.sep + "roi" + os.sep + image_title
    tiff_root            = tmd_root + os.sep + image_title + os.sep + "img"  #
    trackmate_filename   = tmd_root + os.sep + image_title + os.sep + image_title + "-cell-results"  # The file where trackmate results are stored


    # Open the ROI Manager
    rm = RoiManager.getInstance()
    if not rm:
        rm = RoiManager()

    # Determine how many ROIs there are
    rm.runCommand('Deselect')
    roi_indexes = rm.getIndexes()
    nr_roi = len(roi_indexes)
    if nr_roi == 0:
        return

    # Name the cells
    for i in range(nr_roi):
        cell_name = "Cell-" + str(i + 1)
        rm.rename(i, cell_name)
    rm.runCommand("Sort")

    # Close the "Results" window if it is open
    if IJ.isResultsWindow():
        IJ.selectWindow("Results")
        IJ.run("Close")

    # Measure the area of the ROIs
    rm.runCommand('Deselect')
    ResultsTable.getResultsTable().reset()  # Empty the results table
    rm.runCommand("Measure")

    # Save the ROI's as a zip file
    rm.runCommand('Deselect')
    roi_filename = tmd_root + os.sep + image_title + os.sep + "roi" + os.sep + image_title + "-roi.zip"
    rm.save(roi_filename)

    # Check the OS version. On windows csv files need to be opened with 'wb'
    open_attribute = get_file_open_attribute()
    export_file = open(trackmate_filename + '.csv', open_attribute)
    export_writer = csv.writer(export_file)

    fields = ["Image Title", "File Name", "Probe", "Type Probe", "Concentration", "Threshold", "C Spots", "C Total Tracks",
              "C Long Tracks", "C Area"]
    export_writer.writerow(fields)

    # Cycle through the ROIs, run Trackmate and save the results
    for i in range(nr_roi):
        rm.select(i)
        tracks_filename = track_filename_stub + "-cell-tracks-" + str(i + 1) + ".csv"
        tiff_filename = tiff_root + os.sep + image_title + "-cell-" + str(i + 1) + ".tiff"

        nr_spots, all_tracks, filtered_tracks = paint_trackmate(threshold, tracks_filename, tiff_filename)

        # Create the record to save and append the record to the file
        area = round(ResultsTable.getResultsTable().getValueAsDouble(0, i), 0)
        fields = [image_title, tracks_filename, probe, type_probe, concentration_probe, threshold, nr_spots, all_tracks,
                  filtered_tracks, area]
        export_writer.writerow(fields)

        # Save the individual ROI
        roi_filename = roi_filename_stub + "-cell-" + str(i + 1) + ".roi"
        rm.save(roi_filename)

    export_file.close()

    process_combined_cells(threshold, tmd_root, image_title, probe, type_probe, concentration_probe)

    return nr_roi


def process_combined_cells(threshold, tmd_root, image_title, probe, type_probe, concentration_probe):

    rm = RoiManager.getInstance()
    if not rm:
        rm = RoiManager()
    rm.runCommand("Show None")  # Show
    rm.deselect()  # By deselecting all, the next OR will work on everything
    rm.runCommand('Or')  # The OR defines the OR of all ROIs
    rm.runCommand('Add')  # Save it
    rm.select(rm.getCount() - 1)

    ResultsTable.getResultsTable().reset()  # Empty the results table
    rm.runCommand("Measure")
    area = round(ResultsTable.getResultsTable().getValueAsDouble(0, 0), 0)  # There is only row, AREA is the first column

    track_filename      = tmd_root + os.sep + image_title + os.sep + "tracks" + os.sep + image_title + "-combined-.csv"
    roi_filename        = tmd_root + os.sep + image_title + os.sep + "roi" + os.sep + image_title + "-combined.roi"
    tiff_filename       = tmd_root + os.sep + image_title + os.sep + "img" + os.sep + image_title + "-combined.tiff"
    trackmate_filename  = tmd_root + os.sep + image_title + os.sep + image_title + "-combined-results.csv"  # The file where trackmate results are stored

    # Save the combined ROI
    rm.select(rm.getCount() - 1)
    rm.rename(rm.getCount() - 1, "Combined")
    rm.save(roi_filename)

    nr_spots, all_tracks, long_tracks = paint_trackmate(threshold, track_filename, tiff_filename)

    # ----------------------
    # Write the tracks file
    # ----------------------

    open_attribute = get_file_open_attribute()
    export_file = open(trackmate_filename, open_attribute)
    export_writer = csv.writer(export_file)

    header = ["Image Title", "Probe", "Type Probe", "Concentration", "Threshold", "Com Spots", "Com Total Tracks",
              "Com Long Tracks", "Com Area"]
    export_writer.writerow(header)

    fields = [image_title, probe, type_probe, concentration_probe, threshold, nr_spots, all_tracks, long_tracks, area]
    export_writer.writerow(fields)

    export_file.close()