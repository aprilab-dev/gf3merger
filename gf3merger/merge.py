import os
import numpy as np
import matplotlib.pyplot as plt
from gf3merger.utils import _read_rslc, _read_res


def calculate_common_overlap(parent_slc_dir:str, child_slc_dir:str):

    pass

def get_cross_interferogram(parent_slc_dir:str, child_slc_dir:str)->np.ndarray:

    parent_slc = _read_rslc(parent_slc_dir)
    child_slc = _read_rslc(child_slc_dir)

    return parent_slc * np.conj(child_slc)

def compensate_phase(cross_interf:np.ndarray):
    pass


def check_amplitude(parent_slc, child_slc):

    amplitude_diff = np.abs(parent_slc) - np.abs(child_slc)
    # # generate a plot and save to disk from a numpy array
    # plt.imshow(amplitude_diff)
    # plt.savefig("amplitude_difference.png")

    P = np.abs(parent_slc)
    C = np.abs(child_slc)

    # plt.imshow(np.log(P),vmax=3)
    # plt.savefig("parent_overlap.png")
    # plt.imshow(np.log(C),vmax=3)
    # plt.savefig("child_overlap.png")

    diff_ratio = P/C

    diff_ratio[diff_ratio==np.inf]=0
    diff_ratio[diff_ratio==-np.inf]=0
    diff_ratio[np.isnan(diff_ratio)]=0

    print(np.mean(diff_ratio))
    print(np.std(diff_ratio))
    plt.imshow(diff_ratio,vmin=0.4, vmax=0.8)
    plt.colorbar()
    plt.savefig("diff_ratio.png")
    plt.clf()