import pandas as pd
import os


def write_formatted_excel(root_directory, df, qdf):
    file = root_directory + os.sep + 'Full Results.xlsx'

    writer = pd.ExcelWriter(file, engine="xlsxwriter")
    workbook = writer.book
    worksheet = workbook.add_worksheet()

    column_names = ['Image', 'Cell', 'Probe', 'Type Probe', 'Concentration', 'Threshold', 'F Spots', 'F Total Tracks',
                    'F Long Tracks', 'F Area', 'G Spots', 'G Total Tracks', 'G Long Tracks', 'G Area',
                    'C Spots', 'C Total Tracks', 'C Long Tracks', 'C Area', 'C Density', 'G Density',
                    'C/G Density Ratio', 'C Long / Total Ratio', 'C Tau', 'C Tau QC', 'C Density QC', 'Reject']

    # Write column names to the first row
    for col_num, name in enumerate(column_names):
        worksheet.write(0, col_num, name)

    format_red = workbook.add_format(
        {
            "bold": False,
            "text_wrap": False,
            "fg_color": "#f5bc42",
            "border": 0,
        })

    df = df.reset_index(drop=True)

    nan_rows = df['Image'].isnull()

    # -----------------------------------------------------------------------------------
    # Cycle through the df rows and write the values to excel with appropriate formatting
    # -----------------------------------------------------------------------------------

    for i in df.index:

        # Skip empty rows
        if nan_rows.iloc[i]:
            continue

        probe = df.at[i, "Probe"]
        minimum_tracks = qdf[probe].iloc[0]
        minimum_length_ratio = qdf[probe].iloc[1]
        minimum_density_ratio = qdf[probe].iloc[2]
        minimum_cell_area = qdf[probe].iloc[3]

        worksheet.write(i + 1, 0, df.at[i, "Image"])
        worksheet.write(i + 1, 1, df.at[i, "Cell"])
        worksheet.write(i + 1, 2, df.at[i, "Probe"])
        worksheet.write(i + 1, 3, df.at[i, "Type Probe"])
        worksheet.write(i + 1, 4, df.at[i, "Concentration"])
        worksheet.write(i + 1, 5, df.at[i, "Threshold"])
        worksheet.write(i + 1, 6, df.at[i, "F Spots"])
        worksheet.write(i + 1, 7, df.at[i, "F Total Tracks"])
        worksheet.write(i + 1, 8, df.at[i, "F Long Tracks"])
        worksheet.write(i + 1, 9, df.at[i, "F Area"])
        worksheet.write(i + 1, 10, df.at[i, "G Spots"])
        worksheet.write(i + 1, 11, df.at[i, "G Total Tracks"])
        worksheet.write(i + 1, 12, df.at[i, "G Long Tracks"])
        worksheet.write(i + 1, 13, df.at[i, "G Area"])
        worksheet.write(i + 1, 14, df.at[i, "C Spots"])
        worksheet.write(i + 1, 15, df.at[i, "C Total Tracks"])

        reject = False
        if df.at[i, "C Long Tracks"] < minimum_tracks:
            worksheet.write(i + 1, 16, df.at[i, "C Long Tracks"], format_red)
            reject = True
        else:
            worksheet.write(i + 1, 16, df.at[i, "C Long Tracks"])

        if df.at[i, "C Area"] < minimum_cell_area:
            worksheet.write(i + 1, 17, df.at[i, "C Area"], format_red)
            reject = True
        else:
            worksheet.write(i + 1, 17, df.at[i, "C Area"])

        worksheet.write(i + 1, 18, df.at[i, "C Density"])
        worksheet.write(i + 1, 19, df.at[i, "G Density"])

        if df.at[i, "C/G Density Ratio"] < minimum_density_ratio:
            worksheet.write(i + 1, 20, df.at[i, "C/G Density Ratio"], format_red)
            reject = True
        else:
            worksheet.write(i + 1, 20, df.at[i, "C/G Density Ratio"])

        if df.at[i, "C Long / Total Ratio"] < minimum_length_ratio:
            worksheet.write(i + 1, 21, df.at[i, "C Long / Total Ratio"], format_red)
            reject = True
        else:
            worksheet.write(i + 1, 21, df.at[i, "C Long / Total Ratio"])

        worksheet.write(i + 1, 22, df.at[i, "C Tau"])

        # if not pd.isnull(df.at[i, "C Tau QC"]):
        if not reject:
            worksheet.write(i + 1, 23, df.at[i, "C Tau QC"])
            worksheet.write(i + 1, 24, df.at[i, "C Density QC"])
        worksheet.write(i + 1, 25, reject)

    worksheet.autofit()
    workbook.close()
