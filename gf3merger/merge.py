import logging
import os

import largestinteriorrectangle as lir
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import medfilt2d

from gf3merger import config, utils

logger = logging.getLogger("sLogger")

class GF3Merger:

    def __init__(self, dir_slc:str, parent_date:str, child_date:str) -> None:

        self.parent_date = parent_date
        self.child_date = child_date
        self.dir_slc = dir_slc
        self.debug = config.DEBUG

    @property
    def export_dir(self):
        return os.path.join(self.dir_slc, self.parent_date)

    def merge(self):

        # --------------------------------------------------
        # 1. Read Parent and Child SLC
        # --------------------------------------------------
        logger.info(f"Reading SLCs for date {self.parent_date}.")
        parent_arr = utils.read_rslc(os.path.join(self.dir_slc, self.parent_date))
        child_arr = utils.read_rslc(os.path.join(self.dir_slc, self.child_date))

        # --------------------------------------------------
        # 2. Find Common Overlap
        # --------------------------------------------------
        logger.info(f"Finding common overlap area for images on date {self.parent_date}.")
        coords = self._find_common_overlap(parent_arr, child_arr)

        # --------------------------------------------------
        # 3. Calibrate Phase
        # --------------------------------------------------
        logger.info(f"Calculate Phase Calibration.")
        parent_cropped = parent_arr[coords[0]:coords[1], coords[2]:coords[3]]
        child_cropped = child_arr[coords[0]:coords[1], coords[2]:coords[3]]

        m, b = self._calibrate_phase(
            parent = np.exp(1j * np.angle(parent_cropped)),
            child = np.exp(1j * np.angle(child_cropped)),
        )

        # --------------------------------------------------
        # 4. Calibrate Amplitude
        # --------------------------------------------------
        logger.info(f"Calculate Amplitude Calibration.")
        calib_factor = self._calibrate_amplitude(parent_cropped, child_cropped)

        child_corrected = child_arr.T * np.exp(1j * ((np.arange(parent_arr.shape[0]) - coords[0]) * m + b)) * calib_factor

        # --------------------------------------------------
        # 5. Write to Disk
        # --------------------------------------------------
        logger.info(f"Merging adjacent images after calibration.")
        merged = self._concatenate(parent_arr, child_corrected.T, coords[0], coords[1])
        fout = os.path.join(self.export_dir, "slave_rsmp.merged")
        logger.info(f"Writing merged image to back to {fout}.")
        utils.write_rslc(merged, fout)

    def _calibrate_phase(self, parent, child):

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

        if self.debug:
            plt.clf()
            plt.plot(azimuth_modulation)
            plt.savefig(os.path.join(self.export_dir, "wrapped_slope.png"))
            plt.clf()
            plt.plot(azimuth_modulation_unw)
            plt.savefig(os.path.join(self.export_dir, "unwrapped_slope.png"))
            plt.clf()
            plt.plot(np.arange(len(azimuth_modulation_unw)) * m + b)
            plt.savefig(os.path.join(self.export_dir, "unwrapped_slope_check.png"))

            child_corrected = child.T * np.exp(1j * (np.arange(parent.shape[0]) * m + b))
            cross_interf_corrected = parent * np.conj(child_corrected.T)
            plt.clf()
            plt.imshow(np.angle(cross_interf_corrected),vmax=0.05, vmin=-0.05)
            plt.colorbar()
            plt.savefig(os.path.join(self.export_dir, "sanity check.png"))

        return  m, b

    def _calibrate_amplitude(self, parent, child):

        # calculate the ratio of amplitude difference
        diff_ratio = np.abs(parent)/np.abs(child)
        # data clean process
        diff_ratio[diff_ratio==np.inf]=0
        diff_ratio[diff_ratio==-np.inf]=0
        diff_ratio[np.isnan(diff_ratio)]=0

        ratio_mean = np.mean(diff_ratio)
        ratio_std = np.std(diff_ratio)

        if self.debug:
            logger.info(f"The Mean of the Ratio for Amplitude Difference is {ratio_mean};")
            logger.info(f"The Standard Deviation of the Ratio for Amplitude Difference is {ratio_std};")
            plt.clf()
            plt.imshow(diff_ratio,vmin=ratio_mean-ratio_std, vmax=ratio_mean+ratio_std)
            plt.colorbar()
            plt.savefig(os.path.join(self.export_dir, "diff_ratio.png"))

        return np.mean(diff_ratio)

    def _concatenate(self, parent, child, upper_coords, lower_coords):

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

    def _find_common_overlap(
        self,
        parent: np.ndarray,
        child: np.ndarray,
        downsample_factor: int = 20,
    ) -> tuple[int, int, int, int]:
        """FIND_COMMON_OVERLAP() is a function to find the largest common overlap
        between two adjacent SLC images.

        Parameters
        ----------
        parent : np.ndarray
        child : np.ndarray
        downsample_factor : int, optional
            add a downsample factor to accelerate estimation process, by default 20
        debug : bool, optional

        Returns
        -------
        tuple[int, int, int, int]
            The (top, bottom, left, right) of the largest common overlap area.
        """

        buffer = 10

        # construct a mask of common overlap area
        common_overlap = np.logical_and(np.abs(parent) > 0, np.abs(child) > 0)
        # cpoy() is required to save array in contiguous memory
        common_overlap = np.copy(common_overlap[::downsample_factor, ::downsample_factor])
        # data-wash: filter out speckles in common overlap area
        common_overlap = medfilt2d(common_overlap.astype(int), kernel_size=11)
        # find largest interior rectangle
        corners = lir.lir(common_overlap.astype(bool))
        # take buffer into consideration
        corners = corners[0] + buffer, corners[1] + buffer, corners[2] - 2 * buffer, corners[3] - 2 * buffer

        if self.debug:
            plt.imshow(common_overlap)
            plt.savefig(os.path.join(self.export_dir,"common_overlap.png"))

            largest_interior_rect = common_overlap * 0
            largest_interior_rect[
                corners[1] : corners[1] + corners[3], corners[0] : corners[0] + corners[2]
            ] = 10
            plt.imshow(largest_interior_rect)
            plt.savefig(os.path.join(self.export_dir,"largest_interior_rectangle.png"))

        # upscale the corners back to original resolution
        corners = tuple(c * downsample_factor for c in corners)

        return corners[1], corners[1] + corners[3], corners[0], corners[0] + corners[2]
