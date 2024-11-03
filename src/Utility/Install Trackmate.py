import shutil



shutil.copyfile("/Users/hans/Documents/PyCharmProjects/Paint-v4/src/Fiji/Multiple_Cell_Analyis.py",
                "/Users/Applications/Fiji.app/scripts/Plugins/Multiple_Cell_Analysis.py")
print("Copied Multiple_Cell_Analysis.py to /Users/hans/Applications/Fiji.app/scripts/Plugins")

shutil.copyfile("/Users/hans/Documents/PyCharmProjects/Paint-v4/src/Fiji/Multiple_Cell_Glass.py",
                "/Users/Applications/Fiji.app/scripts/Plugins/Multiple_Cell_Glass.py")
print("Copied Multiple_Cell_Analysis.py to /Users/hans/Applications/Fiji.app/scripts/Plugins")

shutil.copyfile("/Users/hans/Documents/LST/Master Research/Trackmate Source Code/RunTrackmate.py",
                "/Users/hans/Trackmate Library/RunTrackmate.py")
print("Copied RunTrackmate.py to /Users/hans/Trackmate Library")

shutil.copyfile("/Users/hans/Documents/LST/Master Research/Trackmate Source Code/PaintTrackMateLib.py",
                "/Users/hans/Trackmate library/PaintTrackMateLib.py")
print("Copied PaintTrackMateLib.py to /Users/hans/Trackmate Library")