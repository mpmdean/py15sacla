#!/home/mdean/anaconda3/bin/python

from py15sacla import hdfselection
from py15sacla import ccdframes
from py15sacla.utils import getDetectorConfig
import h5py
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce

run =

ROI = np.s_[:, :]

h5file = h5py.File('/work/mdean/compressed/comp_{}.h5'.format(run), 'w')
print("\n***** Writing into h5File {} *****".format(h5file.filename))

# read data from file
run_info = hdfselection.HDFSelection('/work/mdean/h5files/run_' + str(run) + '_sig.h5')
# debug
#run_info = hdfselection.HDFSelection('/work/mdean/h5files/run_' + str(run) + '_bg.h5')
opt_delay = run_info['opt_delay'][0][:]
opt_nd = run_info['opt_nd'][0][:]
I0 = run_info['user_4'][0][:] + run_info['user_5'][0][:]
accelerator = run_info['accelerator'][0][:]

xfel_selector = run_info['xfel_pulse_selector_status'][0][:]
laser_selector = run_info['laser_pulse_selector_status'][0][:]

# what does sample theta actually correspond to in our setup?
#sample_theta = run_info['sample_theta'][0][:]
sample_theta = run_info['huber/omega'][0][:]
huber_theta = run_info['huber/theta'][0][:]
huber_phi = run_info['phi'][0][:]
huber_chi = run_info['chi'][0][:]
huber_twotheta = run_info['huber/twotheta'][0][:]
# detector_twotheta = run_info['detector_twotheta'][0][:]

# should really add energy to this, but swamped with other things to check...
#mono_theta  = 2*run_info['double_crystal_monochromator position'][0][:]
# energy =


if np.any(xfel_selector == 0):
    print("\n \n  XRAY SHUTTER CLOSED \n \n ")
if np.any(laser_selector == 0):
    print("\n \n  LASER SHUTTER CLOSED \n \n ")

h5BG = h5py.File('/home/mdean/datacompressing/BG.h5')
BGimage = h5BG['BG'].value

gain = run_info['detector_2d_1/detector_info/absolute_gain'][0].value
photon_energy = run_info['run_info/sacla_config/photon_energy_in_eV'][0].value
SILICON_GAP = 3.65

e_per_ph = photon_energy / (gain * SILICON_GAP)

#print("BGimage {}".format(np.mean(BGimage)))

def clean_image(image, BGimage):
    #print("image {}".format(np.mean(image)))
    rv = image - BGimage
    rv /= e_per_ph
    rv[rv < 0.9] = 0
    rv[rv > 3] = 0
    return rv

images_sel = run_info['detector_2d_1']['detector_data']
image = reduce(lambda a,b :a+b, [clean_image(h5im.value, BGimage) for h5im in images_sel])/len(images_sel)

#signal = ccdframes.CCDFrames(run_info['detector_2d_1']['detector_data'])
#signal.setThereshold(0.8, 3)
#signal.setROI(ROI)
#signal.setBackground(BGimage)
#image = signal.mean()

for var in ['run', 'opt_delay', 'opt_nd', 'I0', 'accelerator', 'xfel_selector',
            'laser_selector', 'sample_theta',
            'huber_theta', 'huber_phi', 'huber_chi', 'huber_twotheta',
            'image']:
    h5file.create_dataset(var, data=eval(var))

h5file.close()
