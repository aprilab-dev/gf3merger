import numpy as np
from gf3merger.merge import get_cross_interferogram
from gf3merger.utils import _read_rslc, _read_res



def test_cross_interferogram():
    parent_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210225"
    child_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210226"
    master_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210127"

    parent_slc = _read_rslc(parent_slc_path)
    child_slc = _read_rslc(child_slc_path)
    # master_slc = _read_rslc(master_slc_path)

