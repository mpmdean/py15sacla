from py15sacla import hdfselection
from py15sacla import ccdframes
from py15sacla.utils import getDetectorConfig
import h5py
import numpy as np
import matplotlib.pyplot as plt

from functools import reduce


run = 542357

ROI = np.s_[:, :]

run_info = hdfselection.HDFSelection('/work/mdean/h5files/run_' + str(run) + '_bg.h5')


BG_info = run_info['detector_2d_1']['detector_data']

BG = reduce(lambda a,b :a+b, [h5im.value for h5im in BG_info])/len(BG_info)

plt.imshow(BG, vmin=np.percentile(BG,5), vmax=np.percentile(BG,95))
plt.colorbar()

h5file = h5py.File('/home/mdean/datacompressing/BG.h5')
h5file.create_dataset('BG', data=BG)
h5file.close()
