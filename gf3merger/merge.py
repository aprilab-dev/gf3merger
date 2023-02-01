import os
import numpy as np
from gf3merger.utils import _read_rslc, _read_res

def cross_interferogram(parent_slc_path:str, child_slc_path:str)->np.ndarray:

    lines  = int(_read_res(parent_slc_path, "Last_line (w.r.t. original_master)"))
    samples  = int(_read_res(parent_slc_path, "Last_pixel (w.r.t. original_master)"))

    parent_slc = _read_rslc(parent_slc_path, lines=lines, samples=samples)
    child_slc = _read_rslc(child_slc_path, lines=lines, samples=samples)

    return parent_slc * np.conj(child_slc)
