
from setuptools import setup, find_packages

with open("README.md") as fp:
    readme = fp.read()

# https://packaging.python.org/guides/single-sourcing-package-version/
version_info = {}
with open("gf3merger/version.py") as fp:
    exec(fp.read(), version_info)

# dependencies
with open("requirements.txt") as fp:
    install_requires = fp.read()
tests_require = [   # tests
    "pytest",
    "pytest-cov"
]
docs_require = [  # docs
    "sphinx",
]

setup(
    name="gf3merger",
    version=version_info["__version__"],
    description="A simple tool for mergering adjacent GF3 images after coregistration in doris.",
    long_description=readme,
    author="Yuxiao QIN",
    url="https://github.com/yuxiao-qin/gf3merger",
    packages=find_packages(),
    python_requires=">=3.8, <3.11",  # 3.10 is the numba requirement
    install_requires=install_requires,
    # entry_points="""
    #     [console_scripts]
    #     gf3merger=gf3merger.cli:main
    # """,
    setup_requires=["pytest-runner", "pylint", "black"],
    tests_require=tests_require,
    extras_require={
        "test": tests_require,
        "doc": docs_require
    },
)