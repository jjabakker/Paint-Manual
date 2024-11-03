
from tmUtility import ReadTracksData
from tmUtility import RestrictTracksLength
from tmUtility import CompileDuration
from tmUtility import CurveFitAndPlot_Exp
from tmUtility import PlotDuration
from tmUtility import CurveFitAndPlot

root_directory = "/Users/hans/"
#root_directory = "/Users/jjaba/"

filename = 'export.csv'

tracksfilename = root_directory + filename

# Read the tracks data and eliminate the ones that are too short or are too long
# Default settings: only tracks of 3 points or more are considered for curve fitting
# The very high value for maximum_track_length means that there is no restriction on maximum length

tracks = ReadTracksData(tracksfilename)
minimum_track_length: int = 3
maximum_track_length: int = -1

tracks = RestrictTracksLength(tracks, minimum_track_length, maximum_track_length)
duration_data = CompileDuration(tracks)
nr_tracks = len(tracks.index)

if minimum_track_length != -1 and maximum_track_length == -1:
    title = f'Duration histogram - only tracks longer than {minimum_track_length} spots'
if minimum_track_length != -1 and maximum_track_length != -1:
    title = f'Duration histogram - only tracks between {minimum_track_length} and {maximum_track_length} spots'
if minimum_track_length == -1 and maximum_track_length == -1:
    title = f'Duration histogram - all tracks are used'
if minimum_track_length == -1 and maximum_track_length != -1:
    title = f'Duration histogram - only tracks shorter than {maximum_track_length} spots'


# For good visibility the time window over which the plot is viewed can be limited.
# The parameter has no impact on the calculation, only on the visuals
# This paremeter is in seconds (not in number opf spots)

PlotDuration(plot_data=duration_data, plot_max_x=5, plot_title=title)
CurveFitAndPlot(plot_data=duration_data, nr_tracks=nr_tracks, plot_max_x=5, plot_title=title)
#CurveFitAndPlot_Exp(duration_data, title)
