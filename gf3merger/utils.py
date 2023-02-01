import os
import numpy as np

parent_slc_path = "/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210225"
child_slc_path = ("/data/tests/yuxiao/gf3_mosaic_test/stack/process/S01B01/20210226",)

def _read_res(slc_dir:str, query_keyword:str) -> str:
    # get values from slave.res
    fmeta = os.path.join(slc_dir, "slave.res")
    with open(fmeta, "r") as f:
        for line in f:
            if query_keyword in line:
                return line.split()[-1]

    raise ValueError(f"Cannot find {query_keyword} in {fmeta}")

def _read_rslc(slc_dir:str, lines:int, samples:int):
    # read binary slave_rsmp.raw
    frslc = os.path.join(slc_dir, "slave_rsmp.raw")

    shape = (lines, samples * 2)

    # read a binary file with numpy.memmap
    try:
        rslc_int = np.memmap(filename=frslc, dtype=np.int16, mode="r", offset=0, shape=shape)
    except ValueError as e:
        raise RuntimeError(f"Unable to read image {frslc} with dtype {np.int16}") from e

    # convert to complex64
    rslc = rslc_int[:,0::2] + 1j * rslc_int[:,1::2]

    return rslc
