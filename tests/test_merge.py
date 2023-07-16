import pytest
import numpy as np
from gf3merger.merge import GF3Merger
from gf3merger import config

@pytest.mark.parametrize("input_dates", [
    ("20201003","20201004"),
    ("20201101","20201102"),
    ("20201130","20201201"),
    ("20210225","20210226"),
    ("20221027","20221028"),
    ("20221125","20221126"),
    ("20230122","20230123"),
])
def test_GF3Merger(input_dates):

    dir_slc = "fakepath"
    parent_date, child_date = input_dates

    config.DEBUG = True
    config.DRYRUN = False

    GF3Merger(dir_slc=dir_slc, parent_date=parent_date, child_date=child_date).merge()

