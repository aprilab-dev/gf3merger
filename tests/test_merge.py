import pytest
import os
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
def test__cleanup(tmp_path, input_dates):

    dir_slc = tmp_path
    parent_date, child_date = input_dates

    for date in input_dates:
    
        # create a temporary directory in the temporary directory
        tmp_dir = tmp_path / date
        tmp_dir.mkdir()

        # create a fake file in the temporary directory
        tmp_file = tmp_dir / "slave_rsmp.raw"
        tmp_file.write_text("GF3Merger test example.")

        # create a fake "merged" file in the temporary directory
        tmp_file2 = tmp_dir / "slave_rsmp.merged"
        tmp_file2.write_text("Merged example")

    gf3merge = GF3Merger(dir_slc=dir_slc, parent_date=parent_date, child_date=child_date)

    if gf3merge._sanity_check():
        gf3merge._cleanup()

    assert os.path.exists(tmp_path / parent_date / "original_slave_rsmp.raw")
    # check if the content of the file is correct
    assert (tmp_path / parent_date / "original_slave_rsmp.raw").read_text() == "GF3Merger test example."
    # check if the content of new "slave_rsmp.raw" is correct
    assert (tmp_path / parent_date / "slave_rsmp.raw").read_text() == "Merged example"
    assert os.path.exists(tmp_path / f"original_{child_date}" )


@pytest.mark.parametrize("input_dates", [
    ("20201003","20201004"),
    ("20201101","20201102"),
    ("20201130","20201201"),
    ("20210225","20210226"),
    ("20221027","20221028"),
    ("20221125","20221126"),
    ("20230122","20230123"),
])
def test__restore(tmp_path, input_dates):

    dir_slc = tmp_path
    parent_date, child_date = input_dates

    for date in input_dates:
    
        # create a temporary directory in the temporary directory
        tmp_dir = tmp_path / date
        tmp_dir.mkdir()

        # create a fake file in the temporary directory
        tmp_file = tmp_dir / "slave_rsmp.raw"
        tmp_file.write_text("GF3Merger test example.")

        # create a fake "merged" file in the temporary directory
        tmp_file2 = tmp_dir / "slave_rsmp.merged"
        tmp_file2.write_text("Merged example")

    gf3merge = GF3Merger(dir_slc=dir_slc, parent_date=parent_date, child_date=child_date)

    if not gf3merge._sanity_check():
        gf3merge._cleanup()
        gf3merge._restore()

    # check if the content of new "slave_rsmp.raw" is correct
    assert (tmp_path / parent_date / "slave_rsmp.raw").read_text() == "GF3Merger test example."


@pytest.mark.parametrize("input_dates", [
    ("20201003","20201004"),
    ("20201101","20201102"),
    ("20201130","20201201"),
    ("20210225","20210226"),
    ("20221027","20221028"),
    ("20221125","20221126"),
    ("20230122","20230123"),
])
def test__sanity_check(tmp_path, input_dates):

    dir_slc = tmp_path
    parent_date, child_date = input_dates

    for date in input_dates:
    
        # create a temporary directory in the temporary directory
        tmp_dir = tmp_path / date
        tmp_dir.mkdir()

        # create a fake file in the temporary directory
        tmp_file = tmp_dir / "slave_rsmp.raw"
        tmp_file.write_text("GF3Merger test example.")

        # create a fake "merged" file in the temporary directory
        tmp_file2 = tmp_dir / "slave_rsmp.merged"
        tmp_file2.write_text("Merged example")

    gf3merge = GF3Merger(dir_slc=dir_slc, parent_date=parent_date, child_date=child_date)

    gf3merge._cleanup()
    assert gf3merge._sanity_check() == False    
    gf3merge._restore()
    assert gf3merge._sanity_check() == True