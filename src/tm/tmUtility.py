
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
from scipy.optimize import OptimizeWarning


######################################################################################
# First a set of functions to manipulate tracks and spots data imported from Trackmate
######################################################################################


def ReadTrackMateData(csvfilename, istrack):

    """
    Function is not to be called externally, but by ReadTracksData or ReadSpotsData
    Read in the data file (it can be either 'tracks' or 'spots').
    Row 0 contains the header.
    Rows 1, 2 and 3 contain commentary, so skip those.
    :param csvfilename:
    :param istrack: A boolean value indicating whether it is tracks data (True) or spots data (False)
    :return: the dataframe with tracks
    """

    try:
        tmd = pd.read_csv(csvfilename, header=0, skiprows=[1, 2, 3])
    except FileNotFoundError:
        print(f'Could not open {csvfilename}')
        sys.exit()
    except:
        print(f'Problem parsing {csvfilename}')
        sys.exit()

    # Drop unused columns for 'tracks' data or 'plots' data
    try:
        if istrack:
            tmd.drop([ 'NUMBER_SPLITS', 'NUMBER_MERGES', 'TRACK_Z_LOCATION',
                      'NUMBER_COMPLEX'], axis=1, inplace=True)
        else:
            tmd.drop(['POSITION_Z', 'MANUAL_SPOT_COLOR'], axis=1, inplace=True)
        return tmd
    except KeyError:
        print(f'Unexpected column names in {csvfilename}')
        sys.exit()


def ReadTracksData(csvfilename,
                   min_spots=-1,
                   max_spots=-1,
                   min_time=-1,
                   max_time=-1):

    """

    :param csvfilename:
    :param min_spots: The smallest number of sp[ots a tracks can have
    :param max_spots: The largest number of sp[ots a tracks can have
    :param min_time: The low percentage cut-off of time, often 1 (%)
    :param max_time: The high percentage cut-off of time, ofteh 99 (%)
    :return:
    """

    tracks = ReadTrackMateData(csvfilename, istrack=True)
    if min_spots != -1 or max_spots != -1:
        tracks = RestrictTracksLength(tracks, min_spots, max_spots)
    if min_time != -1 or max_time != -1:
      tracks = RestrictTracksTime(tracks,
                                  tracks['TRACK_STOP'].max() * min_time/100,
                                  tracks['TRACK_STOP'].max() * max_time/100)
    return tracks


def ReadSpotsData(csvfilename):
    return ReadTrackMateData(csvfilename, istrack=False)


def RestrictTracksLength(tracks, minimum_track_length=-1, maximum_track_length=-1):
    """
    The function removes the tracks shorter  than minimum_track_length
    :param tracks: the datafrane containing tracks
    :param minimum_track_length (if -1 no minimum)
    :param maximum_track_length (if -1 no maximum)
    :return: the updates dataframe containing fewer tracks
    """

    old_tracks_count = tracks.shape[0]
    if minimum_track_length != -1 and maximum_track_length != -1:
        mask = (tracks['NUMBER_SPOTS'] >= minimum_track_length) & (tracks['NUMBER_SPOTS'] <= maximum_track_length)
        report = f'Tracks between {minimum_track_length} to {maximum_track_length} spots'
    elif minimum_track_length != -1:
        mask = tracks['NUMBER_SPOTS'] >= minimum_track_length
        report = f'Tracks longer than {minimum_track_length} spots'
    elif maximum_track_length != -1:
        report = f'Tracks shorter than {maximum_track_length} spots'
        mask = tracks['NUMBER_SPOTS'] <= maximum_track_length
    else:
        print(f'No length restriction applied : total tracks: {old_tracks_count}')
        return tracks

    tracks = tracks.loc[mask]
    new_tracks_count = tracks.shape[0]
    print(f"\n{report} : eliminated {old_tracks_count - new_tracks_count} : selected/total tracks: {new_tracks_count}/{old_tracks_count}")

    return tracks


def RestrictTracksTime(tracks, begin_time=-1, end_time=-1):
    """
    Only let tracks through that start later than begin time and end before end time
    :param tracks:
    :param begin_time: earliest time in sec
    :param end_time: latest time in sec
    :return: the updates dataframe containing fewer tracks
    """

    old_tracks_count = tracks.shape[0]
    if begin_time != 1 and end_time != -1:
        mask = (tracks['TRACK_START'] >= begin_time) & (tracks['TRACK_STOP'] <= end_time)
    elif begin_time != 1:
        mask = (tracks['TRACK_START'] >= begin_time)
    elif end_time != 1:
        mask = (tracks['TRACK_START'] <= end_time)
    else:
        print(f'No Time restriction applied : selected/total tracks : {old_tracks_count}/{old_tracks_count}')
        return tracks

    tracks = tracks.loc[mask]
    new_tracks_count = tracks.shape[0]

    print(f'Time restriction: selected/total tracks: {new_tracks_count}/{old_tracks_count}')

    return tracks


def RestrictTracksSpeed(tracks, min_speed=-1, max_speed=-1):
    """
    Only let tracks through where the mean speed stsb between min_speed  and max_speed
    :param tracks:
    :param min_speed:
    :param max_speed:
    :return: the updates dataframe containing fewer tracks
    """

    old_tracks_count = tracks.shape[0]
    if min_speed != -1 and max_speed != -1:
        mask = (tracks['TRACK_MEAN_SPEED'] >= min_speed) & (tracks['TRACK_MEAN_SPEED'] <= max_speed)
    elif min_speed != -1:
        mask = tracks['TRACK_MEAN_SPEED'] >= min_speed
    elif max_speed != -1:
        mask = tracks['TRACK_MEAN_SPEED'] <= max_speed
    else:
        print(f'No Speed restriction applied : selected/total tracks : {old_tracks_count}/{old_tracks_count}')
        return tracks

    tracks = tracks.loc[mask]
    new_tracks_count = tracks.shape[0]

    print(f'Speed restriction: selected/total tracks: {new_tracks_count}/{old_tracks_count}')

    return tracks


def RestrictTracksSquare(spots, x_min, y_min, x_max, y_max):

    """
    Only let tracks through that fit in a rectangle
    All parameters are needed
    :param spots: The spots dataframe containing the spots to be restricted
    :param x_min:
    :param y_min:
    :param x_max:
    :param y_max:
    :return: The updated dataframe containing only the spots in the rectangle
    """

    old_spots_count = spots.shape[0]
    mask = (spots['POSITION_X'] >= x_min) & (spots['POSITION_X'] <= x_max)
    mask = mask & (spots['POSITION_Y'] >= y_min) & (spots['POSITION_Y'] <= y_max)

    spots = spots.loc[mask]
    new_spots_count = spots.shape[0]

    print(f'Square restriction: selected/total spots: {new_spots_count}/{old_spots_count}')

    return spots


def FindSpotsForTracks(tracks, spots):
    """
    The function eliminates all the spots in the dataframe that are not part of any of the tracks in
    the tracks dataframe

    :param tracks:
    :param spots:
    :return: reduced spots dataframe
    """

    # Find all the TRACK_IDs and put them in a dataframe
    track_ids = tracks['TRACK_ID'].unique()
    track_ids = pd.DataFrame(track_ids, columns=['TRACK_ID'])

    # Now select the spots of those tracks
    reduced_spots = pd.merge(spots, track_ids, on='TRACK_ID')
    return reduced_spots

######################################################################################
# Then a set of functions to create histograms and curve fit
######################################################################################

def CompileDuration(tracks):

    """
    The function produces a histogram
    :param tracks: a dataframe containing the histogram data
    :return: a dataframe containing the histogram
    """

    duration_data = tracks.groupby('TRACK_DURATION')['TRACK_DURATION'].size()

    # histdata is returned as a Pandas Series, make histdata into a dataframe
    # The index values are the duration and the first (and only) column is 'Frequency'
    histdata = pd.DataFrame(duration_data)
    histdata.columns = ['Frequency']
    return histdata


def PlotDuration(plot_data, plot_max_x, plot_title='Duration Histogram'):

    """
    The function simply plots a histogram
    :param plot_data: the histogram data as a Pandas dataframe
    :param plot_max_x: the maximum x value visible in the plot
    :plot_title: optional title for histogram plot
    :return: nothing
    """

    # Extract the x and y data from the dataframe and convert them into Numpy arrays
    x = list(plot_data.index)
    x = np.asarray(x)

    y = list(plot_data["Frequency"])
    y = np.asarray(y)

    fig, ax = plt.subplots()

    ax.set_xlabel('Duration [in s]')  # Add an x-label to the axes.
    ax.set_ylabel('Number of tracks')  # Add a y-label to the axes.
    ax.set_title(plot_title)  # Add a title to the axes.
    plt.xlim([0, plot_max_x])

    # Make a scatter plot, but a line plots is just as easy
    scatter = True
    if scatter:
        ax.scatter(x, y, s=0.5)
    else:
        ax.plot(x, y, linewidth=1.0)

    plt.show()
    return()


def monoExp(x, m, t, b):
    # Define the exponential decay function that will be used for fitting
    return m * np.exp(-t * x) + b


def CurveFitAndPlot(plot_data, nr_tracks, plot_max_x, plot_title='Duration Histogram',file="", plot_to_screen = True):

    """
    :param plot_data:
    :param nr_tracks
    :param plot_max_x: the maximum x value visible in the plot
    :plot_title: optional title for histogram plot
    :return: nothing
    """

    # Convert the pd dataframe to Numpy arrays fur further curve fitting

    x = list(plot_data.index)
    x = np.asarray(x)

    y = list(plot_data["Frequency"])
    y = np.asarray(y)

    # Perform the fit
    p0 = (200, .1, 50)  # start with values near those we expect - original values
    p0 = (2000, 4, 10)  # this is more whar we see

    try:
        params, cv = scipy.optimize.curve_fit(monoExp, x, y, p0)
        m, t, b = params
    except ValueError:
        print('CurveFitAndPlot: ydata or xdata contain NaNs, or incompatible options are used')
        return
    except RuntimeError:
        print('CurveFitAndPlot: The least-squares optimisation fails')
        return
    except OptimizeWarning:
        print('CurveFitAndPlot: Covariance of the parameters can not be estimated')
        return

    tauSec = (1 / t)

    # Determine quality of the fit
    squaredDiffs = np.square(y - monoExp(x, m, t, b))
    squaredDiffsFromMean = np.square(y - np.mean(y))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)


    fig, ax = plt.subplots()
    ax.plot(x, y, linewidth=1.0, label="Data")
    ax.plot(x, monoExp(x, m, t, b), linewidth=1.0, label="Fitted")

    x_middle = plot_max_x/2 - plot_max_x * 0.1
    y_middle = y.max()/2
    plt.text(x_middle, y_middle, f"Tau = {tauSec * 1e3:.0f} ms")
    plt.text(x_middle, 0.8 * y_middle, f"R2 = {rSquared:.4f} ms")
    plt.text(x_middle, 0.6 * y_middle, f"Number or tracks is {nr_tracks}")
    plt.text(x_middle, 0.4 * y_middle, f"Zoomed in from 0 to {plot_max_x:.0f} s")

    plt.xlim([0, plot_max_x])

    ax.set_xlabel('Duration [in s]')
    ax.set_ylabel('Number of tracks')
    ax.set_title(plot_title)
    ax.legend()

    # Plot to screen per default, but don't when it has been overriden
    # Plot to file when a filename has been specified
    if plot_to_screen:
        plt.show()
    if file != "":
        fig.savefig(file)
        print ("\nWriting plot file: " + file)

    # Inspect the parameters
    print("")
    print(f'R² = {rSquared:.4f}')
    print(f'Y = {m:.3f} * e^(-{t:.3f} * x) + {b:.3f}')
    print(f'Tau = {tauSec * 1e3:.0f} ms')

    plt.close()
    return(tauSec*1000)


def CurveFitAndPlot_Exp(histdata, title='Duration Histogram'):
    """
    :param histdata: the histogram data as a Pandas dataframe
    :title: optional title for histogram plot
    :return: nothing
    """

    # Convert the pd dataframe to Numpy arrays fur further curve fitting

    x = list(histdata.index)
    x = np.asarray(x)

    y = list(histdata["Frequency"])
    y = np.asarray(y)

    # Perform the fit
    p0 = (200, .1, 50)  # start with values near those we expect - original values
    p0 = (2000, 4, 10)  # this is more whar we see

    try:
        params, cv = scipy.optimize.curve_fit(monoExp, x, y, p0)
        m, t, b = params
        print (p0)
        print (params)
    except ValueError:
        print('CurveFitAndPlot: ydata or xdata contain NaNs, or incompatible options are used')
        return
    except RuntimeError:
        print('CurveFitAndPlot: The least-squares optimisation fails')
        return
    except OptimizeWarning:
        print('CurveFitAndPlot: Covariance of the parameters can not be estimated')
        return

    tauSec = (1 / t)

    # Determine quality of the fit
    squaredDiffs = np.square(y - monoExp(x, m, t, b))
    squaredDiffsFromMean = np.square(y - np.mean(y))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f'R² = {rSquared}')

    fig, ax = plt.subplots()
    ax.plot(x, y, linewidth=1.0, label="Data")

    x_for_f = np.linspace(0, x.max(), 100)
    y_for_f = monoExp(x_for_f, m, t, b)
    print(x_for_f)
    print(y_for_f)

    ax.plot(x_for_f, y_for_f, linewidth=1.0, label="Fitted")

    x_middle = x.max() / 2 - x.max() * 0.1
    y_middle = y.max() / 2
    plt.text(x_middle, y_middle, f"Tau = {tauSec * 1e3:.0f} ms")
    plt.text(x_middle, 0.8 * y_middle, f"R2 = {rSquared:.4f} ms")

    ax.set_xlabel('Duration [in s]')
    ax.set_ylabel('Number of tracks')
    ax.set_title(title)
    ax.legend()

    ax.set_yscale('log')


    plt.show()



    # Inspect the parameters
    print(f'Y = {m} * e^(-{t} * x) + {b}')
    print(f'Tau = {tauSec * 1e3} ms')


######################################################################################
# Then functions to plot tracks in a Fiji like manner
######################################################################################


def PlotTracks(spots, line_width=0.5, xlim=99999, ylim=99999, title=""):

    '''
    Plot the tracks in a rectangle
    :param spots: The spots files containing the spots for the selected tracks
    :param line_width:
    :param xlim: Plot parameter will only be applied when a value is specified
    :param ylim: Plot parameter will only be applied when a value is specified
    :return:
    '''

    track_names = list(spots["TRACK_ID"].unique())
    fig, ax = plt.subplots()
    ax.invert_yaxis()
    for track_name in track_names:
        df = spots[spots['TRACK_ID'] == track_name]
        x = np.asarray(df['POSITION_X'])
        y = np.asarray(df['POSITION_Y'])
        ax.plot(x, y, linewidth=line_width)

    ax.set_xlabel('X [micrometer]')  # Add an x-label to the axes.
    ax.set_ylabel('Y [micrometer]')  # Add a y-label to the axes.
    if title == "":
        ax.set_title('Position of tracks')  # Add a default title to the axes.
    else:
        ax.set_title(title)  # Add tge specified title to the axes.

    # If no xlim or ylim has been specified the xlim and ylim values are 99999
    # If that is the case just ignore, otherwise set limits
    if xlim != 99999:
        ax.set_xlim([0, xlim])
    if ylim != 99999:
        ax.set_ylim([ylim, 0])
        #ax.invert_yaxis()
    ax.set_aspect('equal', adjustable='box')
    plt.show()
