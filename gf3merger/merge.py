from ctypes import util
from logging import critical
import os
from re import X
from sre_compile import isstring
import numpy as np
import matplotlib.pyplot as plt
from gf3merger import utils, config

debug = config.DEBUG


def merge_gf3(parent_slc_dir:str, child_slc_dir, debug:bool=debug):

    # --------------------------------------------------
    # 1. Read Parent and Child SLC
    # --------------------------------------------------
    parent_arr = utils._read_rslc(parent_slc_dir)
    if isstring(child_slc_dir):
        child_arr = utils._read_rslc(child_slc_dir)
    else:
        child_arr = child_slc_dir

    # --------------------------------------------------
    # 2. Find Common Overlap
    # --------------------------------------------------
    coords = utils.find_common_overlap(parent_arr, child_arr, debug=True)

    # --------------------------------------------------
    # 3. Calibrate Phase
    # --------------------------------------------------
    parent_cropped = parent_arr[coords[0]:coords[1], coords[2]:coords[3]]
    child_cropped = child_arr[coords[0]:coords[1], coords[2]:coords[3]]

    m, b = calibrate_phase(
        parent = np.exp(1j * np.angle(parent_cropped)),
        child = np.exp(1j * np.angle(child_cropped)),
        debug = debug
    )

    # --------------------------------------------------
    # 4. Calibrate Amplitude
    # --------------------------------------------------
    calib_factor = calibrate_amplitude(parent_cropped, child_cropped, debug=debug)

    child_corrected = child_arr.T * np.exp(1j * ((np.arange(parent_arr.shape[0]) - coords[0]) * m + b)) * calib_factor

    # --------------------------------------------------
    # 5. Write to Disk
    # --------------------------------------------------
    merged = concatenate(parent_arr, child_corrected.T, coords[0], coords[1])
    utils._write_rslc(merged, "slave_rsmp.merged")


def calibrate_phase(parent, child, debug):

    # --------------------------------------------------
    # 1. get cross interferogram (at common overlap area)
    # --------------------------------------------------
    cross_interf = parent * np.conj(child)

    # --------------------------------------------------
    # 2. compensate phase
    # --------------------------------------------------
    azimuth_modulation = np.angle(np.sum(cross_interf, axis=1, keepdims=False))
    azimuth_modulation_unw = np.unwrap(azimuth_modulation)

    m, b = np.polyfit(np.arange(len(azimuth_modulation_unw)), azimuth_modulation_unw, 1)

    if debug:
        plt.clf()
        plt.plot(azimuth_modulation)
        plt.savefig("wrapped_slope.png")
        plt.clf()
        plt.plot(azimuth_modulation_unw)
        plt.savefig("unwrapped_slope.png")
        plt.clf()
        plt.plot(np.arange(len(azimuth_modulation_unw)) * m + b)
        plt.savefig("unwrapped_slope_check.png")

        child_corrected = child.T * np.exp(1j * (np.arange(parent.shape[0]) * m + b))
        cross_interf_corrected = parent * np.conj(child_corrected.T)
        plt.clf()
        plt.imshow(np.angle(cross_interf_corrected),vmax=0.05, vmin=-0.05)
        plt.colorbar()
        plt.savefig("sanity check.png")

    return  m, b

def calibrate_amplitude(parent, child, debug):

    # calculate the ratio of amplitude difference
    diff_ratio = np.abs(parent)/np.abs(child)
    # data clean process
    diff_ratio[diff_ratio==np.inf]=0
    diff_ratio[diff_ratio==-np.inf]=0
    diff_ratio[np.isnan(diff_ratio)]=0

    ratio_mean = np.mean(diff_ratio)
    ratio_std = np.std(diff_ratio)

    if debug:
        print(f"The Mean of the Ratio for Amplitude Difference is {ratio_mean};")
        print(f"The Standard Deviation of the Ratio for Amplitude Difference is {ratio_std};")
        plt.clf()
        plt.imshow(diff_ratio,vmin=ratio_mean-ratio_std, vmax=ratio_mean+ratio_std)
        plt.colorbar()
        plt.savefig("diff_ratio.png")

    return np.mean(diff_ratio)

def concatenate(parent, child, upper_coords, lower_coords):

    # Check if the upper part should be merged from parent or child.
    upper_line = int(upper_coords/2)
    lower_line = int((parent.shape[0] + lower_coords)/2)

    if np.mean(np.abs(parent[upper_line, :])) < np.mean(np.abs(parent[lower_line, :])):
        parent, child = child, parent  # swap

    merged = np.zeros_like(parent)

    # takes parent as the upper part for merged
    merged[0:upper_coords, :] = parent[0:upper_coords, :]
    # takes child as the lower part for merged
    merged[lower_coords:, :] = child[lower_coords:, :]

    merged[upper_coords:lower_coords, :] = 0.5 * (parent[upper_coords:lower_coords, :] + child[upper_coords:lower_coords, :])

    return merged
