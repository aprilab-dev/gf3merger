from re import I
import numpy as np
from gf3merger.merge import GF3Merger
from gf3merger.utils import read_rslc, read_res, find_common_overlap, plot_spectrum

def test_GF3Merger():

    dir_slc = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01"
    parent_date = "20201129"
    child_date = "20201130"

    GF3Merger(dir_slc=dir_slc, parent_date=parent_date, child_date=child_date).merge()

