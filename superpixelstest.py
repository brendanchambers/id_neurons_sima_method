# from http://www.pyimagesearch.com/2014/07/28/a-slic-superpixel-tutorial-using-python/

# import the necessary packages
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage import io
import matplotlib.pyplot as plt
import numpy as np
import argparse
from PIL import Image
from pylab import *

IMAGE = 'C:/Users/Brendan/Dropbox/BrendanShared/in vivo vision/6-25-2015/2P-0--800--800.png'

 
# load the image and convert it to a floating point data type
image = Image.open(IMAGE)
imshow(image)
image = image.convert('RGB')
imshow(image)
image = img_as_float(image)

#image = img_as_float(io.imread(IMAGE))
 
# loop over the number of segments
for numSegments in (500, 900, 1300, 2000, 3000):  # 900 seems about right but we could get by with fewer, I think
	# apply SLIC and extract (approximately) the supplied number
	# of segments
	segments = slic(image, n_segments = numSegments, sigma = 0)

	# show the output of SLIC
	fig = plt.figure("Superpixels -- %d segments" % (numSegments))
	ax = fig.add_subplot(1, 1, 1)
	ax.imshow(mark_boundaries(image, segments))
	plt.axis("off")

    # try using superpixels to simplify the ICA problem? http://www.sciencedirect.com/science/article/pii/S0896627309006199

 
# show the plots
plt.show()