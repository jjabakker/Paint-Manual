'''
This routine counts the tracks in the specified area.
The shape of the RoI does not matter because Trackmate reports the shape's area
Be careful though with selecting multiple shapes: make sure that you have OR'ed the area
and report that measurement,

'''

from tmUtility import ReadTracksData, RestrictTracksLength
import numpy as np
import math

root_directory = '/Users/hans/'
root_directory = "/Users/jjaba/"
trackfilename = root_directory + 'tracks.csv'


def CalcDensity(area, min_track_length):
    # Read the tracks data and eliminate the ones that are too short
    tracks = ReadTracksData(trackfilename,
                            min_spots=min_track_length,
                            max_spots=-1)

    # Determine the earliest start end the latest start time
    tmin = tracks['TRACK_START'].min()
    tmax = tracks['TRACK_START'].max()
    tint = tmax - tmin

    # Get the number of tracks
    ntracks = len(tracks.index)

    # Report
    density = ntracks / (area * tint)

    print()
    print(
        f"In time interval {tmin:0.3f} to {tmax:0.3f} there were {ntracks} tracks longer than {min_track_length} spots on an area of {area} square micrometer")
    print(f"Density is {density:0.3f} tracks per square micrometer per second")
    print("\n\n")


try:
    area = input('Specify a value for the area reported by Trackmate: ')
    area = float(area)
    min_track_length = 6
    CalcDensity(area, min_track_length)
except:
    print("NaN interpreted as exit.")
    exit()
