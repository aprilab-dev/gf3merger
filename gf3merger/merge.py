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
        self.dryrun = config.DRYRUN  # if True, do not write result to disk.

    @property
    def export_dir(self):
        return os.path.join(self.dir_slc, self.parent_date)

    def merge(self):
        logger.info("")
        logger.info("=============================================")
        logger.info(f"=             Merging {self.parent_date}              =")
        logger.info("=============================================")
        logger.info("")

        # --------------------------------------------------
        #  Sanity Check
        # --------------------------------------------------
        if self._sanity_check() is False:
            return

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
        logger.info(f"Common overlap lines ranging from {coords[0]} to {coords[1]}.")

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
        del child_arr, parent_cropped, child_cropped  # release some memory

        # """ Add another debug session here: check the amplitude bias between MASTER and parent/child?
        # """
        # if self.debug:
        #     master_arr = utils.read_rslc(os.path.join(self.dir_slc, "20210127"))
        #     master_cropped = master_arr[coords[0]:coords[1], coords[2]:coords[3]]
        #     self._calibrate_amplitude(master_cropped, parent_cropped, fout="master_vs_parent.png")
        #     self._calibrate_amplitude(master_cropped, child_cropped, fout="master_vs_child.png")

        # --------------------------------------------------
        # 5. Write to Disk
        # --------------------------------------------------
        if not self.dryrun:
            logger.info(f"Merging adjacent images after calibration.")
            merged = self._concatenate(parent_arr, child_corrected.T, coords[0], coords[1])
            del parent_arr, child_corrected  # release some memory
            fout = os.path.join(self.export_dir, "slave_rsmp.merged")
            logger.info(f"Writing merged image to back to {fout}.")
            utils.write_rslc(merged, fout)
            self._cleanup()
        logger.info("")
        logger.info(f"Merging for date {self.parent_date} completed.")

    def _sanity_check(self):

        # if there is "original_slave_rsmp.raw" in the parent directory, it means the merging process has been done, then abort the process. 
        if os.path.exists(os.path.join(self.dir_slc, self.parent_date, "original_slave_rsmp.raw")):
            logger.info(f"Skipping {self.parent_date} because it has been merged.")
            return False
        return True

    def _cleanup(self):

        # rename child directory to ~child
        cur_child_dir = os.path.join(self.dir_slc, self.child_date)
        new_child_dir = os.path.join(self.dir_slc, f"original_{self.child_date}")
        os.rename(cur_child_dir, new_child_dir)
        logger.info(f"Renamed {cur_child_dir} to {new_child_dir}.")

        # rename parent slave_rsmp.raw to slave_rsmp.raw.orig
        cur_parent_rslc = os.path.join(self.dir_slc, self.parent_date, 'slave_rsmp.raw')
        new_parent_rslc = os.path.join(self.dir_slc, self.parent_date, 'original_slave_rsmp.raw')
        os.rename(cur_parent_rslc,new_parent_rslc)
        logger.info(f"Renamed {cur_parent_rslc} to {new_parent_rslc}.")

        # rename parent slave_rsmp.merged to slave_rsmp.raw
        cur_parent_merged = os.path.join(self.dir_slc, self.parent_date, 'slave_rsmp.merged')
        os.rename(cur_parent_merged, cur_parent_rslc)
        logger.info(f"Renamed {cur_parent_merged} to {cur_parent_rslc}")

    def _restore(self):
        
        # rename child directory back to child
        cur_child_dir = os.path.join(self.dir_slc, f"original_{self.child_date}")
        new_child_dir = os.path.join(self.dir_slc, self.child_date)
        os.rename(cur_child_dir, new_child_dir)
        logger.info(f"Restored {cur_child_dir} to {new_child_dir}.")

        # rename parent slave_rsmp.raw to slave_rsmp.merged
        # delete the current slave_rsmp.raw file
        orig_parent_rslc = os.path.join(self.dir_slc, self.parent_date, 'slave_rsmp.raw')
        os.remove(orig_parent_rslc)
        logger.info(f"Removed merged file: {orig_parent_rslc}")

        # rename parent slave_rsmp.raw.orig to slave_rsmp.raw
        cur_parent_rslc = os.path.join(self.dir_slc, self.parent_date, 'original_slave_rsmp.raw')
        os.rename(cur_parent_rslc, orig_parent_rslc)
        logger.info(f"Renamed {cur_parent_rslc} to {orig_parent_rslc}.")


    def _calibrate_phase(self, parent, child, fout=None):

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
            fout = f"sanity check {self.parent_date} {self.child_date}.png" if fout is None else fout
            plt.savefig(os.path.join(self.export_dir, fout))

        return  m, b

    def _calibrate_amplitude(self, parent, child, fout=None):

        # calculate the ratio of amplitude difference
        diff_ratio = np.abs(parent)/np.abs(child)
        # data clean process
        diff_ratio[diff_ratio==np.inf]=0
        diff_ratio[diff_ratio==-np.inf]=0
        diff_ratio[np.isnan(diff_ratio)]=0

        ratio_mean = np.mean(diff_ratio)
        ratio_std = np.std(diff_ratio)

        # This is also a debug session
        if fout is not None:
            diff_ratio[diff_ratio<ratio_mean - 0.2] = 100  # a normalization

        if self.debug:
            logger.info(f"The Mean of the Ratio for Amplitude Difference is {ratio_mean};")
            logger.info(f"The Standard Deviation of the Ratio for Amplitude Difference is {ratio_std};")
            plt.clf()
            plt.rcParams['figure.figsize'] = [20, 10]
            # plt.imshow(diff_ratio,vmin=ratio_mean-ratio_std, vmax=ratio_mean+ratio_std)
            plt.imshow(diff_ratio,vmin=ratio_mean-0.1, vmax=ratio_mean+0.1)
            plt.colorbar()
            fout = f"diff_ratio {self.parent_date} {self.child_date}.png" if fout is None else fout
            plt.savefig(os.path.join(self.export_dir, fout))

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
