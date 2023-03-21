from re import I
import numpy as np
from gf3merger.merge import GF3Merger

def test_GF3Merger():

    dir_slc = "fakepath"
    parent_date = "20210225"
    child_date = "20210226"

    GF3Merger(dir_slc=dir_slc, parent_date=parent_date, child_date=child_date).merge()

