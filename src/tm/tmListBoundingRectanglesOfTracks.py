from tmUtility import ReadTracksData, ReadSpotsData
from tmUtility import RestrictTracksLength, RestrictTracksTime

'''
A simple routine to get information on the rectangle tracks that just contains the tracks
You read in a tracks and a spots file
You specify the minimum and maximum length of the tracks you want to consider 

The output then is for each track the bounding rectangle and the delta x and delta y values 
'''

root_directory = "/Users/hans/"
root_directory = "/Users/jjaba/"


def DetermineBoundingRectangle(tracks, spots, minimum_size, maximum_size):
    tracks = tracks.loc[tracks['NUMBER_SPOTS'] >= minimum_size]
    tracks = tracks.loc[tracks['NUMBER_SPOTS'] <= maximum_size]

    # Find the area of each track
    nr_tracks = tracks.shape[0]

    for i in range(0, nr_tracks):
        track = tracks.iloc[i]
        track_name = track['LABEL']
        track_index = track['TRACK_INDEX']
        nr_spots = track['NUMBER_SPOTS']

        # Select the spots

        spots_in_track = spots.loc[spots['TRACK_ID'] == track_index]
        max_values = spots_in_track.max()
        min_values = spots_in_track.min()

        min_x = min_values['POSITION_X']
        max_x = max_values['POSITION_X']
        min_y = min_values['POSITION_Y']
        max_y = max_values['POSITION_Y']

        print(
            f'Track {track_name:12s} with {nr_spots:5d} spots:\
                xmin = {min_x:5.2f}   xmax = {max_x:5.2f}   deltax = {max_x - min_x:5.2f}\
                ymin = {min_y:5.2f}   ymax = {max_y:5.2f}   deltay = {max_y - min_y:5.2f}')


tracksfilename = root_directory + 'tracks.csv'
spotsfilename = root_directory + 'spots.csv'

tracks = ReadTracksData(tracksfilename)
spots = ReadSpotsData(spotsfilename)

while True:
    min_number = input('Specify a value for the minimum track length (or any letter to stop: ')
    if min_number.isdecimal() == False:
        print ('\n\nProgram exited')
        break
    max_number = input('Specify a value for the maximum track length (or any letter to stop: ')
    if max_number.isdecimal() == False:
        print ('\n\nProgram exited')
        break
    else:
        print(f'Analysing for a track length of larger {int(min_number)} and smaller than {int(max_number)}\n\n')
        DetermineBoundingRectangle(tracks, spots, int(min_number), int(max_number))
        print('\n\n')

