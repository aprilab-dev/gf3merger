import os
import pytest
import numpy as np
from gf3merger.utils import read_res, read_rslc, write_rslc


@pytest.mark.parametrize(
    "test_input, desired",
    [
        ("Last_line (w.r.t. original_master)", "23292"),
        ("Last_pixel (w.r.t. original_master)", "21888"),
    ],
)
def test___read_res(test_input, desired):
    """Unittest for _read_res()"""

    assert (
        read_res(
            slc_dir=os.path.join(os.path.dirname(__file__), "data"),
            query_keyword=test_input,
        )
        == desired
    )


def test__read_rslc(tmpdir):
    """Unittest for _read_rslc()"""

    # construct a fake slave_rsmp.raw
    lines = 2000
    pixels = 1000
    input_real = np.random.randint(-2**15, 2**15-1, size=(lines, pixels), dtype=np.int16)
    input_imag = np.random.randint(-2**15, 2**15-1, size=(lines, pixels), dtype=np.int16)
    input = np.empty((lines, pixels*2), dtype=np.int16)
    input[:, 0::2] = input_real
    input[:, 1::2] = input_imag

    # write to disk
    temppath = os.path.join(tmpdir, "slave_rsmp.raw")
    with open(temppath, "wb") as f:
        f.write(input.tobytes())

    actual = read_rslc(tmpdir, lines, pixels)
    desired = input_real + 1j * input_imag

    assert actual.all() == desired.all()

def test__write_rslc(tmpdir):
    """Unittest for _read_rslc()"""

    # construct a fake slave_rsmp.raw
    lines = 2000
    pixels = 1000
    input_real = np.random.randint(-2**15, 2**15-1, size=(lines, pixels), dtype=np.int16)
    input_imag = np.random.randint(-2**15, 2**15-1, size=(lines, pixels), dtype=np.int16)

    input = input_real + 1j * input_imag
    input = input.astype(np.complex128)

    # write to disk
    temppath = os.path.join(tmpdir, "slave_rsmp.raw")
    write_rslc(input, temppath)

    actual = read_rslc(tmpdir, lines, pixels)

    assert actual.all() == input.all()
