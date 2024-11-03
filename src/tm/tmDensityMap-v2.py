from tmUtility import ReadTracksData
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


# Magnification is the factor at which you can try to make the grid smaller
# Magnification = 1 means you look at a grid of 81x81, with avery square 1x1 micrometer
# Magnification = 2 means you look at a grid of (2x81) x (2x81), with every square 0.5 x 0.5 micrometer
# Magnification = 10 means you look at a grid of (10x81) x (10x81), with every square 0.1 x 0.1 micrometer
#
# Cutoff means that you limit the highest value that can be displayed
# It is useful in a scenario when you might have 40,1,2,1,2,1,2,1,2,1,2,1,1,2,1,3,2,1,2,1
# You don't see the small values because the one high value stretches the display
# if you supply a low cutoff value, say 0.1, the max value displayed is 4 and the small values are visible


magnification = 5
cutoff = 0.2


root_directory = '/Users/hans/'
root_directory = '/Users/jjaba/'

def print_bindings(z):
    xdim = z.shape[0]
    ydim = z.shape[1]

    total = 0

    for x in range(0, xdim):
        for y in range(0, ydim):
            print(f"{z[x, y]:3d}", end="")
            total += z[x, y]
        print("\n")

    print(f"Total bindings is {total}, x dimension is {xdim}, y dimension is {ydim}")


tracksfilename = root_directory + 'tracks.csv'

# Read the tracks data and eliminate the ones that are too short or are too long
tracks = ReadTracksData(tracksfilename,
                        min_spots=3,
                        max_spots=-1,
                        min_time=1,
                        max_time=99)

# Determine the earliest and latest start times
time_first = tracks['TRACK_START'].min()
time_last = tracks['TRACK_START'].max()

# Determine the min and max x and y coordinates of tracks (in micrometers)
xmin = tracks['TRACK_X_LOCATION'].min()
xmax = tracks['TRACK_X_LOCATION'].max()
ymin = tracks['TRACK_Y_LOCATION'].min()
ymax = tracks['TRACK_Y_LOCATION'].max()

# Calculate area assuming you have a rectangle
area = (xmax - xmin) * (ymax - ymin)

print(f"xMin is {xmin:0.2f}")
print(f"xMax is {xmax:0.2f}")
print(f"yMin is {ymin:0.2f}")
print(f"yMax is {ymax:0.2f}")

print(f"Area is {area:0.2f}")

# Make them integer values
xmin = math.floor(xmin)
ymin = math.floor(ymin)
xmax = math.floor(xmax)
ymax = math.floor(ymax)



xmin = 0
ymin = 0
xmax = 81 * magnification
ymax = 81 * magnification

# Create the 2 dimensional array to hold the track count
count_array = np.zeros((xmax-xmin+1, ymax-ymin+1), dtype=int)

# Loop through the tracks
track_names = list(tracks["TRACK_ID"].unique())
for track_name in track_names:

    # Retrieve the x and y coordinates
    track = tracks[tracks['TRACK_ID'] == track_name]
    x1 = track['TRACK_X_LOCATION'].loc[track.index[0]]
    y1 = track['TRACK_Y_LOCATION'].loc[track.index[0]]

    # Insert them in the array
    x2 = math.floor(x1*magnification - xmin)
    y2 = math.floor(y1*magnification - ymin)

    count_array[x2][y2] = count_array[x2][y2] + 1

    # For debugging
    # print(f"{track_name:5d} {int(x1):3d} {int(y1):3d}")


# Count how many times a certain value occurs
max_value = count_array.max()
occurrence = np.zeros(max_value + 1, dtype=int)
for i in range(1, max_value + 1):
    occurrence[i] = np.count_nonzero(count_array == i)

# Now calculate how many values are cut off when a cutoff factor other than 1 is use
if cutoff != 1:
    new_max = int(max_value * cutoff)
    nr_cutoff = np.count_nonzero(count_array > new_max)
    print(f"\n\nA cutoff value of {int(cutoff * 100):d}% is set.")
    print(f"The maximum binding count is {max_value}, but only the true value up to {new_max} is displayed,")
    if nr_cutoff > 1:
        print(f"There are {nr_cutoff} locations where the actual peak value is higher than displayed\n")
    else:
        print(f"There is {nr_cutoff} location where the actual peak value is higher than displayed\n")

for i in range(1, new_max):
    if occurrence[i] != 0:
        if occurrence[i] > 1:
            print(f"Included: {occurrence[i]:3d} instances of {i}")
        else:
            print(f"Included: {occurrence[i]:3d} instance  of {i}")

print("\n")

for i in range(new_max+1, max_value+1):
    if occurrence[i] != 0:
        if occurrence[i] > 1:
            print(f"Cut off: {occurrence[i]:3d} instances of {i}")
        else:
            print(f"Cut off: {occurrence[i]:3d} instance  of {i}")
print("\n\n")

# Create the meshgrid
x = np.arange(xmin, xmax + 1, 1)
y = np.arange(ymax, ymin - 1, -1)

#x = np.linspace(0, 81, 81*n+1)
#y = np.linspace(0, 81, 81*n+1)


X, Y = np.meshgrid(x, y)
Z = np.transpose(count_array)

# For debugging
#print_bindings(Z)

# Quick summary
nr_tracks = Z.sum()
density = nr_tracks/((xmax-xmin+1)*(ymax-ymin+1))
duration = time_last-time_first
print(f"A total of {int(nr_tracks):d} binding events were found in a square of {xmax-xmin+1} by {ymax-ymin+1} square micrometer,")
print(f"giving a density of {density:.1f} bindings per square micrometer")
print(f"The period in which the binding events occurred was {duration:.1f} seconds.")
print(f"The average number of events per square micrometer per second is: {density/duration:.3f}")


# Now do the plotting

xlim = ylim = 81

fig, ax = plt.subplots()
ax.set_aspect('equal')
colors = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]
cmap = LinearSegmentedColormap.from_list("colormap", colors, N=50)
cm = ax.pcolormesh(X, Y, Z, vmin=np.amin(Z), vmax=np.amax(Z) * cutoff, cmap=cmap)
plt.colorbar(cm)
plt.show()

'''
fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.invert_yaxis()
csf = ax.contour(Z)
plt.colorbar(csf)
plt.show()

fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.invert_yaxis()
csf = ax.contour(Z, 10)
plt.colorbar(csf)
plt.show()

fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.invert_yaxis()
csf = ax.contourf(Z)
plt.colorbar(csf)
plt.show()
'''