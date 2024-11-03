from tmUtility import ReadTracksData, ReadSpotsData
import pandas as pd
import matplotlib.pyplot as plt


#root_directory = "/Users/hans/"
root_directory = "/Users/jjaba/"

tracksfilename = root_directory + 'export.csv'

pixel_dimension = 0.1603251
precision = 0
minimum_events_to_display = 12     # Only spots where there are more than this number of events are sees are reported

# Set up the number of graphs to plot. If you make the numbers too large the plots will become too small

nr_rows = 3
nr_cols = 2


# Read the tracks data, excluding the very short tracks and only include tracks
# that are fall in the 1-99% range
tracks = ReadTracksData(tracksfilename,
                        min_spots=3,
                        max_spots=-1,
                        min_time=1,
                        max_time=99)

# Add the mean x and y coordinates of the track as new columns and make integer
tracks['INT_X'] = round(tracks['TRACK_X_LOCATION'] / pixel_dimension,precision)
tracks['INT_X'] = tracks['INT_X'].apply(lambda x: int(x))
tracks['INT_Y'] = round(tracks['TRACK_Y_LOCATION'] / pixel_dimension,precision)
tracks['INT_Y'] = tracks['INT_Y'].apply(lambda x: int(x))

# Create a dataframe grouped on x and y and count
test = tracks.groupby(['INT_X','INT_Y'])['INT_X']
grouped_data = tracks.groupby(['INT_X','INT_Y'])['INT_X'].count()
grouped_data = pd.DataFrame(grouped_data)
grouped_data.columns = ['Count']

# Strange trick to get the row names into the dataframe itself (from the internet)
grouped_data.index.name = 'newhead'
grouped_data.reset_index(inplace=True)

grouped_data = grouped_data.sort_values('Count', ascending=False)
max_events = grouped_data['Count'].max()

# Set up the picture for the max 6 events series, sharex and sharey need to be set so that the context
# for the bar charts is consistent

fig, axs = plt.subplots(nrows=nr_rows, ncols=nr_cols, sharex=True, sharey=True)


for i in range (0, len(grouped_data)):
    nr_events = grouped_data['Count'].iloc[i]
    if nr_events >= minimum_events_to_display:
        print(f"Number of events: {nr_events}")
        x = grouped_data['INT_X'].iloc[i]
        y = grouped_data['INT_Y'].iloc[i]
        mask = (tracks['INT_X'] == x) & (tracks['INT_Y'] == y)
        selection = tracks.loc[mask]
        sorted_selection = selection.sort_values(by=['TRACK_START'])
        for j in range (0, nr_events):
           print(f"({sorted_selection['TRACK_START'].iloc[j]:3.1f}, {sorted_selection['TRACK_DURATION'].iloc[j]:3.1f}) ")
    else:
        break

for i in range (0, int(nr_rows * nr_cols)):

    # Get the x and y coordinates of the pixels with the highest number of events
    x = grouped_data['INT_X'].iloc[i]
    y = grouped_data['INT_Y'].iloc[i]

    # Get the data for those coordinates
    mask = (tracks['INT_X'] == x) & (tracks['INT_Y'] == y)
    selection = tracks.loc[mask]
    sorted_selection = selection.sort_values(by=['TRACK_START'])

    # Prepare the info for the bar chart
    height = sorted_selection['TRACK_DURATION']
    x_pos = sorted_selection['TRACK_START']
    nr_events = sorted_selection['TRACK_DURATION'].count()

    axs[int(i/2), int(i%2)].bar(x_pos, height)

    x_middle = 70
    y_middle = 3
    axs[int(i/2), int(i%2)].text(x_middle, y_middle, f"{x} {y}")
    axs[int(i/2), int(i%2)].text(x_middle, 0.7*y_middle, f"{nr_events}")
    axs[int(i/2), int(i%2)].set_xlabel('Time')
    axs[int(i/2), int(i%2)].set_ylabel('Duration of binding')

plt.show()

i = 1





