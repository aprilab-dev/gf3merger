import numpy as np
from gf3merger.merge import get_cross_interferogram
from gf3merger.utils import _read_rslc, _read_res, find_common_overlap, plot_spectrum



def test_cross_interferogram():
    parent_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210225"
    child_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210226"
    master_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210127"

    parent_slc = _read_rslc(parent_slc_path)
    child_slc = _read_rslc(child_slc_path)
    master_slc = _read_rslc(master_slc_path)

    coors = find_common_overlap(parent_slc, child_slc)

    parent_slc = parent_slc[coors[0]:coors[1], coors[2]:coors[3]]
    plot_spectrum(parent_slc, "parent_slc.png")
    child_slc = child_slc[coors[0]:coors[1], coors[2]:coors[3]]
    plot_spectrum(child_slc, "child_slc.png")

    master_slc = master_slc[coors[0]:coors[1], coors[2]:coors[3]]
    plot_spectrum(master_slc, "master_slc.png")