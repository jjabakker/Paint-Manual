"""

This routine assumes the presence of a set of TrackMate runs stored in the '/User/Name/Trackmate Data' directory.

For each set of cells:
    The roi's have been defined and stored in the roi directory.
    The track files have been stored in the tracks directory.
    The image files have been stored in the img directory.

This routine determines in one sweep the Tau values for each cell in each experiment.

Per experiment:
    A quality file is generated.
    The plot figures are saves

Then finally, an overall quality file is written that can be pasted into a quality spreadsheet

"""

import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

import pandas as pd

from src.Automation.tmProcessImage import process_image
from src.Automation.tmToGraphPad import prepare_graphpad
from src.Automation.tmWriteFormattedExcel import write_formatted_excel


def get_probe(file):
    df = pd.read_excel(file)
    return df["Probe"].iloc[0]



def process_all_images(root_directory):
    try:
        quality_criteria_file = "/Users/hans/Trackmate Data/Quality criteria.xlsx"
        qdf = pd.read_excel(quality_criteria_file, sheet_name="Sheet1")
    except:
        print("No Quality criteria")
        return

    # ------------------------------------------------------
    # Loop through all the images in the selecte directory
    # ------------------------------------------------------

    all_dirs = os.listdir(root_directory)
    for d in all_dirs:

        # There may already be files in the directory. Ignore anything but directories
        if os.path.isfile(root_directory + os.sep + d):
            continue

        # Create the individual results files containing the data for the selected cells
        image = root_directory + os.sep + d
        print('/nProcessing directory/n', image)
        process_image(image, d)

    #all_dirs = os.listdir(root_directory)

    start = True
    for d in all_dirs:
        if os.path.isfile(root_directory + os.sep + d):
            continue

        qfile = root_directory + os.sep + d + os.sep + d + '-results.xlsx'

        # Get the appropriate quality criteria for the specific probe
        probe = get_probe(qfile)
        minimum_tracks = qdf[probe].iloc[0]
        minimum_length_ratio = qdf[probe].iloc[1]
        minimum_density_ratio = qdf[probe].iloc[2]
        minimum_cell_area = qdf[probe].iloc[3]

        # Read the individual image results file, add two columns, and delete one called 'Unnamed'
        df = pd.read_excel(qfile)
        df.insert(0, "Image", d, True)
        df.insert(1, "Cell", d, True)
        df = df.drop(df.columns[2], axis='columns')

        # Label the cells
        for i in range(len(df)):
            cellstr = "Cell-" + str(i + 1)
            df.iloc[i, 1] = cellstr

        # ---------------------------------------------------
        # Calculate the cell and glass density and its ratio
        # Determine which Tau and Density values are valid
        # ---------------------------------------------------

        for i in range(len(df)):
            cl_tracks = float(df["C Long Tracks"].iloc[i])
            ct_tracks = float(df["C Total Tracks"].iloc[i])
            c_area = float(df["C Area"].iloc[i])
            g_tracks = float(df["G Long Tracks"].iloc[i])
            g_area = float(df["G Area"].iloc[i])
            concentration = float(df["Concentration"].iloc[i])

            # The density is the long tracks on the cell divided by the cell area divided by the duration (100 s)
            c_density = ((cl_tracks / c_area) / 100) * 1000
            # Then the density is normalised on concentration
            c_density /= concentration
            c_density = round(c_density, 1)
            df.at[i, "C Density"] = c_density

            # The density is the long tracks on the cell divided by the cell area divided by the duration (100 s)
            g_density = ((g_tracks / g_area) / 100) * 1000
            # Then the density is normalised on concentration
            g_density /= concentration
            g_density = round(g_density, 1)
            df.at[i, "G Density"] = g_density

            # Calculate the ratio of cell/glas density
            density_ratio = round(c_density / g_density, 1)
            df.at[i, "C/G Density Ratio"] = density_ratio

            # Calculate the ratio of cell long/total racks
            length_ratio = round(cl_tracks / ct_tracks, 3)
            df.at[i, "C Long / Total Ratio"] = length_ratio

            if (cl_tracks >= minimum_tracks and length_ratio >= minimum_length_ratio and
                    density_ratio >= minimum_density_ratio and
                    c_area >= minimum_cell_area):
                df.at[i, "C Tau QC"] = df["C Tau"].iloc[i]
                df.at[i, "C Density QC"] = c_density

        # ----------------------------------------------------------
        # Now add the individual results table to the compound table
        # ----------------------------------------------------------

        if start:
            df_merged = df.copy()
            start = False
        else:
            df_merged = pd.concat([df_merged, df])

    # -------------------------------------------
    # Then write to Excel
    # -------------------------------------------

    df_merged = df_merged.sort_values(by=['Probe', 'Image', 'Cell'])
    write_formatted_excel(root_directory, df_merged, qdf)


def PostProcessing():
    root = Tk()
    root.withdraw()
    root_directory = askdirectory(title='Select Folder')  # shows dialog box and return the path

    process_all_images(root_directory)
    prepare_graphpad(root_directory)


if __name__ == "__main__":
    PostProcessing()
