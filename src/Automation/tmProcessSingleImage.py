import os
import sys
from tkinter import Tk
from tkinter.filedialog import askdirectory

import pandas as pd

from src.tm.tmUtility import CompileDuration
from src.tm.tmUtility import CurveFitAndPlot
from src.tm.tmUtility import ReadTracksData
from src.tm.tmUtility import RestrictTracksLength


def process_single_image(image, roi_set):

    # Generate the file names
    plt_directory = image + os.sep + "plt"
    trackmate_cellfile = image + os.sep + roi_set + "-cell-results.csv"
    trackmate_fullfile = image + os.sep + roi_set + "-full-results.csv"
    glass_fullfile = image + os.sep + roi_set + "-glass-results.csv"
    results_file = image + os.sep + roi_set + "-results.xlsx"

    # If there are files in the plt directory delete them
    for f in os.listdir(plt_directory):
        os.remove(os.path.join(plt_directory, f))

    # Read the results data. The table will contain a record for each cell.
    try:
        df = pd.read_csv(trackmate_cellfile)
    except FileNotFoundError:
        print(f'Could not open {trackmate_cellfile}')
        sys.exit()

    # Create columns needed for the results table
    df["C Density"] = ""
    df["G Density"] = ""
    df["C/G Density Ratio"] = ""
    df["C Long / Total Ratio"] = ""
    df["C Tau"] = ""
    df["C Tau QC"] = ""
    df["C Density QC"] = ""

    # -------------------------------------------------------------------------------------------------
    # Now cycle through the cell results table, calculate the Tau for each cell and insert in the table
    # -------------------------------------------------------------------------------------------------

    for i in range(len(df)):
        filename = df["File Name"].iloc[i]
        image_title = df["Image Title"].iloc[i]
        #threshold = df["Threshold"].iloc[i]   # Not yet present in all files
        if "cell" not in filename:
            continue
        tracks = ReadTracksData(filename)
        minimum_track_length: int = 3
        maximum_track_length: int = -1

        tracks = RestrictTracksLength(tracks, minimum_track_length, maximum_track_length)
        duration_data = CompileDuration(tracks)
        nr_tracks = len(tracks.index)

        if minimum_track_length != -1 and maximum_track_length == -1:
            title = f'Duration histogram - only tracks longer than {minimum_track_length} spots'
        elif minimum_track_length != -1 and maximum_track_length != -1:
            title = f'Duration histogram - only tracks between {minimum_track_length} and {maximum_track_length} spots'
        elif minimum_track_length == -1 and maximum_track_length == -1:
            title = f'Duration histogram - all tracks are used'
        elif minimum_track_length == -1 and maximum_track_length != -1:
            title = f'Duration histogram - only tracks shorter than {maximum_track_length} spots'
        else:
            title = "Impossible Title"

        # For good visibility the time window over which the plot is viewed can be limited.
        # The parameter has no impact on the calculation, only on the visuals
        # This parameter is in seconds (not in number opf spots)

        filename = plt_directory + os.sep + image_title + "-cell-" + str(i + 1)

        tausec = CurveFitAndPlot(plot_data=duration_data, nr_tracks=nr_tracks, plot_max_x=5, plot_title=title,
                                 file=filename, plot_to_screen=False)
        df.at[i, "C Tau"] = round(tausec, 1)
        print(tausec)

    # -----------------------------------------------------------------------------
    # With the individual cells data processes, now add in the Full and Glass Data
    # -----------------------------------------------------------------------------

    # Read the data for the full image, just one record
    try:
        dff = pd.read_csv(trackmate_fullfile)
    except FileNotFoundError:
        print(f'Could not open {trackmate_fullfile}')
        sys.exit()

    f_spots = dff["F Spots"].iloc[0]
    f_ttracks = dff["F Total Tracks"].iloc[0]
    f_ltracks = dff["F Long Tracks"].iloc[0]
    #threshold = dff["Threshold"].iloc[0]   # Not yet present in all files

    # Read the data for the glass, just one record

    try:
        dfg = pd.read_csv(glass_fullfile)
    except FileNotFoundError:
        print(f'Could not open {glass_fullfile}')
        sys.exit()

    g_spots = dfg["G Spots"].iloc[0]
    g_ttracks = dfg["G Total Tracks"].iloc[0]
    g_ltracks = dfg["G Long Tracks"].iloc[0]
    g_area = dfg["G Area"].iloc[0]
    threshold = dfg["Threshold"].iloc[0]  # Present in all files
    df.insert(2, 'Threshold', threshold, True)

    # Use the cells table as the basis and add columns as needed.
    # The column values are invariable

    del df['File Name']
    df.insert(4, "E", '', True)
    df.insert(5, "F Spots", f_spots, True)
    df.insert(6, "F Total Tracks", f_ttracks, True)
    df.insert(7, "F Long Tracks", f_ltracks, True)
    df.insert(8, "F Area", 6738, True)
    df.insert(9, "E", '', True)
    df.insert(10, "G Spots", g_spots, True)
    df.insert(11, "G Total Tracks", g_ttracks, True)
    df.insert(12, "G Long Tracks", g_ltracks, True)
    df.insert(13, "G Area", g_area, True)
    df.insert(14, "E", '', True)
    del df['Image Title']

    # Then write the individual image results file
    try:
        df.to_excel(results_file)
        print("\n")
        print(f'\nResults file written: {results_file}\n')
    except:
        print("\n\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f'Results file not written: {results_file}')
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n")

    print("\nRoutine completed successfully.")


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    root_directory = askdirectory(title='Select Folder')  # shows dialog box and return the path
    path_comps = root_directory.split('/')
    roi_set = path_comps[-1]
    process_single_image(root_directory, roi_set)
