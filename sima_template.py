
from __future__ import print_function
from builtins import input
from builtins import range
import scipy
import matplotlib.pyplot as plt

##############################################################################
#                                                                            #
#   PART 0: Import SIMA and necessary submodules.                            #
#                                                                            #
##############################################################################

import sima
import sima.motion
import sima.segment
from sima.segment import ROIFilter


##############################################################################
#                                                                            #
#   PART 1: Preparing the iterables.                                         #
#                                                                            #
##############################################################################

NUM_FRAMES = 150
SIGNAL_CHANNEL = 'test'
SIGNAL_CHAN_LABEL = 'test_channel'
# Generate the filenames with Python list comprehensions.
# BC: the test data from Piggy - C:\Users\Brendan\Dropbox\BrendanShared\in vivo vision\6-25-2015\2P-76--800--800
#  ['C:\Users\Brendan\Dropbox\BrendanShared\in vivo vision\6-25-2015\2P-{n1}--800--800'.format(n1=cycle, n2=channel)
#    for channel in range(1,1)] for cycle in range(0, NUM_FRAMES-1)
#
#

'''
# version from the tutorial:
tiff_filenames = [
    ['workflow_data/Cycle{n1:02d}_Ch{n2}.tif'.format(n1=cycle, n2=channel)
     for channel in range(1, 3)] for cycle in range(1, 16) # max 16)
]
'''
# tiff stack from test-day V1 raster scan:
tiff_filenames = [
    ['C:/Users/Brendan/Dropbox/BrendanShared/in vivo vision/7-1-2015/2P-{n1}--800--800.tif'.format(n1=cycle,n2=cycle)
     for channel in range(1,2)] for cycle in range(0, NUM_FRAMES)
]

# The resulting filenames are printed for clarification.
print("TIFF filenames:\n", tiff_filenames)

# from tutorial: construct a MultiPageTIFF iterable using each of the filenames
sequences = [
    sima.Sequence.join(*[sima.Sequence.create('TIFF', chan) for chan in cycle])
    for cycle in tiff_filenames]

##############################################################################
#                                                                            #
#   PART 2: Running motion correction to create the dataset, and exporting   #
#           the corrected image data.                                        #
#                                                                            #
##############################################################################

dataset_path = 'workflow_data/dataset.sima'
correction_approach = sima.motion.HiddenMarkov2D(num_states_retained=30,
                                                 max_displacement=[20, 30])
dataset = correction_approach.correct(
    sequences, dataset_path, channel_names=[SIGNAL_CHANNEL],
    trim_criterion=0.95)
'''
displacement_estimation = correction_approach.estimate(dataset) # this is a list of ndarrays
print('plot displacement')
print(len(displacement_estimation))
print(displacement_estimation[1].shape)
displacement_test = []
for i in range(0,3):  # plot data from the first 3 cycles
    print(i)
    print(displacement_estimation[i].shape)
    print(displacement_estimation[i][:,:,:,:])

    #plt.plot(np.squeeze(displacement_estimation[i][:,:,:,0]))
    #plt.ylabel('displacement estimation (x)')
    #plt.show()
    displacement_test = displacement_estimation[i][0,0,1,0]  # plot the data from ROI #3
    #displacement_x = [coord[0] for coord in displacement_estimation]

plt.plot(displacement_test)
plt.ylabel('displacement estimation (0th)')
plt.show()
'''


'''
# Export the time averages for a manuscript figure.
dataset.export_averages(['workflow_data/tdTomato.tif',
                         'workflow_data/GCaMP.tif'])
'''
# Export the time averages for a manuscript figure.
dataset.export_averages(['workflow_data/test.tif'])

# Generate the output filenames with Python list comprehensions.
output_filenames = [
    [[channel.replace('.tif', '_corrected.tif') for channel in cycle]]
    for cycle in tiff_filenames
]

# The resulting filenames are printed for clarification.
print("Output filenames:\n", output_filenames)

# Export the corrected frames for a presentation.
dataset.export_frames(output_filenames, fill_gaps=True)

# At this point, one may wish to inspect the exported image data to evaluate
# the quality of the motion correction before continuing.
'''
while True:
    input_ = input("Continue? (y/n): ")
    if input_ == 'n':
        exit()
    elif input_ == 'y':
        break
        '''

##############################################################################
#                                                                            #
#   PART 3: Running automated segmentation and editing results with the ROI  #
#           Buddy GUI.                                                       #
#                                                                            #
##############################################################################

print('segmenting...')
# Segment the field of view into ROIs using the method for CA1 pyramidal cells
# and parameters that were determined based on the imaging magnification.

segmentation_approach = sima.segment.STICA(channel=SIGNAL_CHANNEL, mu=0.01, verbose=True)
#segmentation_approach = sima.segment.NormalizedCuts(  )
segmentation_approach.append(sima.segment.SparseROIsFromMasks(min_size=50, static_threshold=0.5, smooth_size=0, sign_split=False)) # turn up smooth size to get prettier ROIs default=4
#segmentation_approach.append(sima.segment.SmoothROIBoundaries())
# segmentation_approach.append(sima.segment.Circularity(0)) # throws out ROIs below threshold in [0 1]
segmentation_approach.append(sima.segment.MergeOverlapping(threshold=0))

#segmentation_approach.append(ROIFilter(lambda roi: roi.size >= 30 and roi.size <= 300))
'''
# tutorial used CA1 pyramidal optimized method...above, trying spatio-temporal ICA
segmentation_approach = sima.segment.PlaneCA1PC(
    channel=SIGNAL_CHANNEL,
    num_pcs=30,
    max_dist=(3, 6),
    spatial_decay=(3, 6),
    cut_max_pen=0.10,
    cut_min_size=50,
    cut_max_size=150,
    x_diameter=14,
    y_diameter=7,
    circularity_threhold=.5,
    min_roi_size=20,
    min_cut_size=40
)
'''
dataset.segment(segmentation_approach, 'auto_ROIs')

'''
# At this point, one may wish to edit the automatically segmented ROIs using
# the ROI Buddy GUI before performing signal extraction.
# find the script's directory and then run with python roi_buddy.py
while True:
    input_ = input("Continue? (y/n): ")
    if input_ == 'n':
        exit()
    elif input_ == 'y':
        break
'''
##############################################################################
#                                                                            #
#   PART 4: Extracting fluorescence signals from the ROIs.                   #
#                                                                            #
##############################################################################

# Reload the dataset in case any changes have been made with ROI Buddy
dataset = sima.ImagingDataset.load(dataset_path)

# Extract the signals. By default, the most recently created ROIs are used.
dataset.extract(signal_channel=SIGNAL_CHANNEL, label=SIGNAL_CHAN_LABEL)

# Export the extracted signals to a CSV file.
dataset.export_signals('example_signals.csv', channel=SIGNAL_CHANNEL,
                       signals_label=SIGNAL_CHAN_LABEL)

##############################################################################
#                                                                            #
#   PART 5: Visualizing data using Python.                                   #
#                                                                            #
##############################################################################

'''
# from the tutorial:
# this isn't working, not sure why
print('plotting...')
# import necessary functions from matplotlib
from matplotlib.pyplot import plot, show

# plot the signal from an ROI object, with a different color for each cycle
raw_signals = dataset.signals(SIGNAL_CHANNEL)[SIGNAL_CHAN_LABEL]['raw']
for sequence in range(3):  # plot data from the first 3 cycles
    plot(raw_signals[sequence][3])  # plot the data from ROI #3
show(block=True)
'''