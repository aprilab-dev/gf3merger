
import os
from gf3merger import config, utils

dir_slc = "/data/tests/yuxiao/fc1_coreg_test/stack/process/S01B01"
mother_date = "20231126"
daughter_date = "20231207"

mother = utils.read_rslc(os.path.join(dir_slc, mother_date))
daughter = utils.read_rslc(os.path.join(dir_slc, daughter_date))

cross_interf = mother * np.conj(daughter

plt.rcParams['figure.figsize'] = [20, 10]
plt.imshow(np.angle(cross_interf))
plt.colorbar(shrink=0.2)