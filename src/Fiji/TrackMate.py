# -*- coding: utf-8 -*-

import csv
import sys

import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import java.lang
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate.action import CaptureOverlayAction
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
from fiji.plugin.trackmate.gui.displaysettings.DisplaySettings import TrackMateObject
from fiji.plugin.trackmate.tracking.jaqaman import SparseLAPTrackerFactory
from fiji.plugin.trackmate.util import LogRecorder
from ij import WindowManager
from ij.io import FileSaver


def paint_trackmate(threshold, tracks_filename, image_filename):
    print("\nProcessing: " + tracks_filename)

    # We have to do the following to avoid errors with UTF8 chars generated in
    # TrackMate that will mess with our Fiji Jython.

    reload(sys)
    sys.setdefaultencoding('utf-8')

    # ----------------------------
    # Create the model object now
    # ----------------------------

    # Some of the parameters we configure below need to have
    # a reference to the model at creation. So we create an
    # empty model now.

    model = Model()

    # Send all messages to ImageJ log window.
    model.setLogger(Logger.IJ_LOGGER)

    # Get currently selected image
    imp = WindowManager.getCurrentImage()

    # Prepare settings object
    settings = Settings(imp)

    # Configure detector - all important parameters
    settings.detectorFactory = LogDetectorFactory()
    settings.detectorSettings = {
        'DO_SUBPIXEL_LOCALIZATION': False,
        'RADIUS': 0.5,
        'TARGET_CHANNEL': 1,
        'THRESHOLD': threshold,
        'DO_MEDIAN_FILTERING': False,
    }

    # Configure spot filters - Do not filter out any spots
    filter1 = FeatureFilter('QUALITY', 0, True)
    settings.addSpotFilter(filter1)

    # Configure tracker
    settings.trackerFactory = SparseLAPTrackerFactory()
    settings.trackerSettings = settings.trackerFactory.getDefaultSettings()  # almost good enough

    # These are the important parameters
    settings.trackerSettings['MAX_FRAME_GAP'] = 3
    settings.trackerSettings['LINKING_MAX_DISTANCE'] = 0.6
    settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 1.2

    # These are default values made explicit
    settings.trackerSettings['ALTERNATIVE_LINKING_COST_FACTOR'] = 1.05
    settings.trackerSettings['SPLITTING_MAX_DISTANCE'] = 15.0
    settings.trackerSettings['ALLOW_GAP_CLOSING'] = True
    settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
    settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
    settings.trackerSettings['MERGING_MAX_DISTANCE'] = 15.0
    settings.trackerSettings['CUTOFF_PERCENTILE'] = 0.9

    # Add ALL the feature analyzers known to TrackMate.
    # They will yield numerical features for the results, such as speed, mean intensity etc.
    settings.addAllAnalyzers()

    # Configure track filters - Only consider tracks of 3 and longer.
    filter2 = FeatureFilter('NUMBER_SPOTS', 3, True)
    settings.addTrackFilter(filter2)

    # Instantiate plugin
    trackmate = TrackMate(model, settings)

    # Process
    ok = trackmate.checkInput()
    if not ok:
        # sys.exit(str(trackmate.getErrorMessage()))
        return

    ok = trackmate.process()
    if not ok:
        # sys.exit(str(trackmate.getErrorMessage()))
        return

    # ----------------
    # Display results
    # ----------------

    # A selection.
    selection_model = SelectionModel(model)

    # Read the default display settings.
    ds = DisplaySettingsIO.readUserDefault()
    ds.setTrackColorBy(TrackMateObject.TRACKS, 'TRACK_INDEX')

    displayer = HyperStackDisplayer(model, selection_model, imp, ds)
    displayer.render()
    displayer.refresh()

    # ----------------
    # Save the image file
    # ----------------

    image = trackmate.getSettings().imp
    logger = LogRecorder(Logger.VOID_LOGGER)
    capture = CaptureOverlayAction.capture(image, -1, 1, logger)

    # Save capture image with overlay as tiff
    FileSaver(capture).saveAsTiff(image_filename)

    # The feature model, that stores edge and track features.
    fm = model.getFeatureModel()

    # ----------------
    # Write the CSV file
    # ----------------

    # We only need the first three fields, the rest is added to maintain compatability
    fields = ["LABEL", "NUMBER_SPOTS", "TRACK_DURATION", 'NUMBER_SPLITS', 'NUMBER_MERGES', 'TRACK_Z_LOCATION',
              'NUMBER_COMPLEX']

    # Iterate over all the tracks that are visible.

    ver = java.lang.System.getProperty("os.name").lower()

    if ver.startswith("windows"):
        open_attribute = "wb"
    else:
        open_attribute = "w"

    with open(tracks_filename, open_attribute) as csvfile:

        # Need to write three empty line to maintain compatability with the Trackmate generated CSV file
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerow('         ')
        csvwriter.writerow('         ')
        csvwriter.writerow('         ')

        for i in model.getTrackModel().trackIDs(True):
            # Fetch the track feature from the feature model.
            label = 'Track_' + str(i)
            duration = fm.getTrackFeature(i, 'TRACK_DURATION')
            spots = fm.getTrackFeature(i, 'NUMBER_SPOTS')

            # Write the record for each track
            csvwriter.writerow([label, spots, duration])

    model.getLogger().log('Found ' + str(model.getTrackModel().nTracks(True)) + ' tracks.')

    nr_spots = model.getSpots().getNSpots(True)
    all_tracks = model.getTrackModel().nTracks(False)
    filtered_tracks = model.getTrackModel().nTracks(True)

    return nr_spots, all_tracks, filtered_tracks
