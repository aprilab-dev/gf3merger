from logging import critical
import os
from re import X
import numpy as np
import matplotlib.pyplot as plt
from gf3merger import utils


def merge_gf3(parent_slc_dir:str, child_slc_dir:str, debug:bool=False):

    """

    5. write back to disk  # dirty implementation, but let's deal with it later
    >>> write_back_to_disk()


    """

    # --------------------------------------------------
    # 1. read parent and cild slc
    # --------------------------------------------------
    parent_arr = utils._read_rslc(parent_slc_dir)
    child_arr = utils._read_rslc(child_slc_dir)

    # --------------------------------------------------
    # 2. find common overlap
    # --------------------------------------------------
    coords = utils.find_common_overlap(parent_arr, child_arr, debug=True)

    parent_arr = np.exp(1j * np.angle(parent_arr))
    child_arr = np.exp(1j * np.angle(child_arr))

    # --------------------------------------------------
    # 3. get cross interferogram (at common overlap area)
    # --------------------------------------------------
    cross_interf = parent_arr[coords[0]:coords[1], coords[2]:coords[3]] * np.conj(child_arr[coords[0]:coords[1], coords[2]:coords[3]])
    print(cross_interf.shape)

    # # --------------------------------------------------
    # # 4. compensate phase
    # # --------------------------------------------------
    wrapped_slope = np.angle(np.sum(cross_interf, axis=1, keepdims=False))
    unwrapped_slope = np.unwrap(wrapped_slope)
    if debug:
        plt.clf()
        plt.plot(wrapped_slope)
        plt.savefig("wrapped_slope.png")
        plt.clf()
        plt.plot(unwrapped_slope)
        plt.savefig("unwrapped_slope.png")

    m, b = np.polyfit(np.arange(len(unwrapped_slope)), unwrapped_slope, 1)
    if debug:
        plt.plot(np.arange(len(unwrapped_slope)) * m + b)
        plt.savefig("unwrapped_slope_check.png")

    child_corrected = child_arr.T * np.exp(1j * ((np.arange(parent_arr.shape[0]) - coords[0]) * m + b))

    cross_interf2 = parent_arr * np.conj(child_corrected.T)
    cross_interf2 = cross_interf2[coords[0]:coords[1], coords[2]:coords[3]]
    plt.clf()
    plt.imshow(np.angle(cross_interf2),vmax=0.05, vmin=-0.05)
    plt.colorbar()
    plt.savefig("sanity.png")
    print("sanity check")
    # phase_corrected = merge_slc(parent_arr, child_arr, cross_interf)


def merge_slc(parent_slc, child_slc, cross_interf):
    merged_slc = np.zeros_like(parent_slc)
    parent_slc[~parent_coords] = 0
    child_slc[~child_coords] = 0
    merged_slc = parent_slc + child_slc
    merge_slc[overlap_coords] = parent_slc[parent_coords] + child_slc[overlap_coords]
    merged_slc[slave_coords] = correct_phase(child_slc[slave_coords])
    return merged_slc

def compensate_phase(cross_interf:np.ndarray):
    pass


def get_cross_interferogram(parent_slc_dir:str, child_slc_dir:str)->np.ndarray:

    parent_slc = _read_rslc(parent_slc_dir)
    child_slc = _read_rslc(child_slc_dir)

    return parent_slc * np.conj(child_slc)



def check_amplitude(parent_slc, child_slc, debug:bool=False):

    amplitude_diff = np.abs(parent_slc) - np.abs(child_slc)
    if debug:
        plt.clf()
        plt.imshow(amplitude_diff)
        plt.savefig("amplitude_difference.png")

    P = np.abs(parent_slc)
    C = np.abs(child_slc)

    diff_ratio = P/C

    diff_ratio[diff_ratio==np.inf]=0
    diff_ratio[diff_ratio==-np.inf]=0
    diff_ratio[np.isnan(diff_ratio)]=0

    # print(np.mean(diff_ratio))
    # print(np.std(diff_ratio))

    if debug:
        plt.clf()
        plt.imshow(diff_ratio,vmin=0.4, vmax=0.8)
        plt.colorbar()
        plt.savefig("diff_ratio.png")

    return np.mean(diff_ratio)
