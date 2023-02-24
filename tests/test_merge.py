import matplotlib.pyplot as plt
import numpy as np
from gf3merger.merge import get_cross_interferogram
from gf3merger.utils import _read_rslc, _read_res

import largestinteriorrectangle as lir

def test_cross_interferogram():
    parent_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210225"
    child_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210226"
    master_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210127"

    parent_slc = _read_rslc(parent_slc_path)
    child_slc = _read_rslc(child_slc_path)
    # master_slc = _read_rslc(master_slc_path)

    common_overlap = np.logical_and(np.abs(parent_slc) > 0, np.abs(child_slc) > 0)
    common_overlap_lines = np.sum(common_overlap, axis=1, keepdims=False)
    common_overlap_samples = np.sum(common_overlap, axis=0, keepdims=False)

    result1 = np.where(np.abs(np.diff(common_overlap_lines)) > 100)
    result2= np.where(np.abs(np.diff(common_overlap_samples)) > 100)
    print(result1)
    print(result2)

    # plt.imshow(A)
    # plt.savefig("overlap.png")
    breakpoint()



    # # plot SLC
    # plt.imshow(np.abs(master_slc), vmax=300)
    # plt.savefig("master_slc.png")

    # plt.imshow(np.abs(child_slc), vmax=300)
    # plt.savefig("child_slc.png")

    # plt.imshow(np.abs(parent_slc), vmax=300)
    # plt.savefig("parent_slc.png")

    # # cross_interf_crop = cross_interf[13000:15500, :]
    # # plt.imshow(np.angle(cross_interf), cmap="rainbow")
    # # plt.savefig("cross_interf.png")

    # plt.imshow(np.angle(master_slc*np.conj(child_slc)), vmin=-3.14, vmax=3.14, cmap="rainbow")
    # plt.savefig("interf_w_child.png")

    # plt.imshow(np.angle(master_slc*np.conj(parent_slc)),vmin=-3.14, vmax=3.14, cmap="rainbow")
    # plt.savefig("interf_w_parent.png")

    # # # generate a plot and save to disk from a numpy array
    # # plt.imshow(np.angle(cross_interf))
    # # plt.savefig("cross_interf.png")


