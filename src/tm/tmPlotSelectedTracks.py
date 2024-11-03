from tmUtility import ReadSpotsData, ReadTracksData, PlotTracks
from tmUtility import RestrictTracksSquare, RestrictTracksTime, FindSpotsForTracks, RestrictTracksLength

root_directory = '/Users/hans/'
root_directory = '/Users/jjaba/'

spotfilename = root_directory + 'spots.csv'
trackfilename = root_directory + 'tracks.csv'

spots = ReadSpotsData(spotfilename)
tracks = ReadTracksData(trackfilename)
PlotTracks(spots, xlim=81, ylim=81, title='Plot 1: All tracks - Full image')

# Determine the maximum x and y values and plot the unprocessed spots
xmax = spots['POSITION_X'].max()
ymax = spots['POSITION_Y'].max()

xmax = 81
ymax = 81

# Be careful, the RestrictTracksSquare takes a 'spots' file, not a 'tracks' file
spots1 = RestrictTracksSquare(spots, x_min=15, y_min=0, x_max=70, y_max=75)

# Plot in original context
PlotTracks(spots1, line_width=0.1, xlim=xmax, ylim=ymax, title='Plot 2: Restricted square - Full Image')

# Plot in maximum detail
PlotTracks(spots1, line_width=0.1, title='Plot 3: Restricted square - maximum detail')


spots2 = RestrictTracksSquare(spots, x_min=20, y_min=7, x_max=25, y_max=12)
PlotTracks(spots2, line_width=0.1, title='More Restricted square')

# Plot tracks with a specified TRACK_ID (in this case 0, 1 and 2)
mask = spots['TRACK_ID'] == 0
mask = mask + spots['TRACK_ID'] == 1
mask = mask + spots['TRACK_ID'] == 2

spots3 = spots[mask]
PlotTracks(spots3, line_width=0.1, title='Only a few specific tracks')
PlotTracks(spots3, line_width=0.1, xlim=xmax, ylim=ymax, title='Only a few specific tracks')

# Now plot the tracks where the time is limited

begin_time = 50
reduced_tracks = RestrictTracksTime(tracks, begin_time=begin_time, end_time=-1)
spots4 = FindSpotsForTracks(reduced_tracks, spots)
PlotTracks(spots, line_width=0.1, title='xxx Original Tracks')
PlotTracks(spots4, line_width=0.1, title=f'yyy Tracks after {begin_time} sec')


# Determine the maximum x and y values and plot the unprocessed spots in the smallest bounding rectangle
xmax = spots['POSITION_X'].max()
ymax = spots['POSITION_Y'].max()
PlotTracks(spots, line_width=1, xlim=xmax, ylim=ymax)

min_track_len = 10
max_track_len = 10
# Determine the track names of tracks longer than the minimum
tracks1 = RestrictTracksLength(tracks, minimum_track_length=min_track_len, maximum_track_length=max_track_len)
reduced_spots = FindSpotsForTracks(tracks1, spots)

# Plot the reduced spots with the earlier established xmax and ymax
plot_title = f"Only tracks >= {min_track_len} and <= {max_track_len}"
PlotTracks(reduced_spots, line_width=0.5, xlim=xmax, ylim=ymax,title=plot_title)


# Determine the track names of tracks longer than the minimum
tracks2 = RestrictTracksLength(tracks, maximum_track_length=max_track_len)
reduced_spots = FindSpotsForTracks(tracks2, spots)

# Plot the reduced spots with the earlier established xmax and ymax
plot_title = f"Only tracks <= {max_track_len}"
PlotTracks(reduced_spots, line_width=0.5, xlim=81, ylim=81,title=plot_title)
