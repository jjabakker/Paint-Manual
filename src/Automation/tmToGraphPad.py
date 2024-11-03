import pandas as pd
import sys
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def prepare_graphpad(trackmate_resultsfile):

    # -----------------------------------------------------------
    # Read the results file and only keep the columns of interest
    # -----------------------------------------------------------

    try:
        df = pd.read_excel(trackmate_resultsfile)
    except FileNotFoundError:
        print(f'Could not open {trackmate_resultsfile}')
        sys.exit()

    # Limit to the columns of interest and get rid of empty columns and all the rows where there is
    # not a valid QC'ed value for density and Tau
    # Then sort the table on the combination "Type Probe", "Probe"
    # Determine which probes there are

    df = df[['Image', 'Cell', 'Type Probe', 'Probe', 'C Tau QC', 'C Density QC']]
    df = df.dropna()
    df = df.sort_values(by=["Type Probe", "Probe"])
    probes = df['Probe'].unique()

    # ---------------------------------------------------------------------------
    # Create the Tau and Density GraphPad tables and add a first empty row in each
    # ---------------------------------------------------------------------------

    t_graphpad = pd.DataFrame(
        columns=['Image', 'Cell', 'Probe', 'Type Probe', 'Key', '1 Mono', '1 Bi', '1 Tri', '2 Mono', '2 Bi', '2 Tri', '6 Mono', '6 Bi', '6 Tri'])
    t_graphpad.loc[len(df.index)] = ['', '', '', '','', '', '', '', '', '', '', '', '', '']
    d_graphpad = pd.DataFrame(
        columns=['Image', 'Cell', 'Probe', 'Type Probe', 'Key', '1 Mono', '1 Bi', '1 Tri', '2 Mono', '2 Bi', '2 Tri', '6 Mono', '6 Bi', '6 Tri'])
    d_graphpad.loc[len(df.index)] = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']

    for probe in probes:

        # For each probe select the applicable records
        selection = (df['Probe'] == probe)
        unique_probe = df[selection]

        # Add a 'Key' column to the tqble
        # unique_probe['Key'] = ""
        unique_probe.insert(0, "Key", "")

        # Generate a key for each image
        for index, row in unique_probe.iterrows():
            key = row['Image'] + '-' + 'Cell-' + str(row['Cell'] ) + ' (' + row['Probe'] + ')'
            unique_probe.at[index, 'Key'] = key

        # Simplify the table to the few columns needed
        #unique_probe = unique_probe.drop(columns=['Image', 'Cell', 'Probe', 'Type Probe'])

        for index, row in unique_probe.iterrows():
            if probe == '1 Mono':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], row['C Tau QC'], '', '', '', '', '', '', '', '']
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], row['C Density QC'], '', '', '', '', '', '', '', '']
            elif probe == '1 Bi':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', row['C Tau QC'], '', '', '', '', '', '', '']
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', row['C Density QC'], '', '', '', '', '', '', '']
            elif probe == '1 Tri':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', row['C Tau QC'], '', '', '', '', '', '']
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', row['C Density QC'], '', '', '', '', '', '']
            elif probe == '2 Mono':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', row['C Tau QC'], '', '', '', '', '']
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', row['C Density QC'], '', '', '', '', '']
            elif probe == '2 Bi':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', row['C Tau QC'], '', '', '', '']
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', row['C Density QC'], '', '', '', '']
            elif probe == '2 Tri':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', '', row['C Tau QC'], '', '', '']
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', '', row['C Density QC'], '', '', '']
            elif probe == '6 Mono':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', '', '', row['C Tau QC'], '', '']
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', '', '', row['C Density QC'], '', '']
            elif probe == '6 Bi':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', '', '', '', row['C Tau QC'], '']
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', '', '', '', row['C Density QC'], '']
            elif probe == '6 Tri':
                t_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', '', '', '', '', row['C Tau QC']]
                d_record = [row['Image'], row['Cell'], row['Type Probe'], row['Probe'], row['Key'], '', '', '', '', '', '', '', '', row['C Density QC']]
            else:
                sys.exit(0)

            # Add the records to the graphpad tables
            t_graphpad.loc[len(t_graphpad.index)] = t_record
            d_graphpad.loc[len(d_graphpad.index)] = d_record

    t_graphpad = t_graphpad.sort_values(by=["Key"])
    d_graphpad = d_graphpad.sort_values(by=["Key"])

    print(t_graphpad)
    print(d_graphpad)

    writer = pd.ExcelWriter("/Users/Hans/Trackmate Data/Trackmate Graphpad Tau.xlsx", engine="xlsxwriter")
    workbook = writer.book
    worksheet = workbook.add_worksheet()
    t_graphpad.to_excel(writer)
    worksheet.autofit()
    workbook.close()

    writer = pd.ExcelWriter("/Users/Hans/Trackmate Data/Trackmate Graphpad Density.xlsx", engine="xlsxwriter")
    workbook = writer.book
    worksheet = workbook.add_worksheet()
    d_graphpad.to_excel(writer)
    worksheet.autofit()
    workbook.close()


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    filename = askopenfilename(filetypes=[("Excel File", "*.xlsx")])

    #root_directory = os.path.expanduser('~') + os.sep + "Trackmate Data"
    prepare_graphpad(filename)
