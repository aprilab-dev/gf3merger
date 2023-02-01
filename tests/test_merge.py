import matplotlib.pyplot as plt
import numpy as np
from gf3merger.merge import cross_interferogram

def test_cross_interferogram():
    parent_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210225"
    child_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210226"


    cross_interf = cross_interferogram(parent_slc_path, child_slc_path)
    # generate a plot and save to disk from a numpy array
    plt.imshow(np.angle(cross_interf))
    plt.savefig("cross_interf.png")
