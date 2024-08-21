import os
from setuptools import setup, find_packages
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), fname), "r") as fin:
        return fin.read()
setup(
    name = "financial_scraper",
    version = "0.0.1",
    author = "audi0417",
    author_email = "audiaudy3030422@gmail.com",
    description = "專門用於獲取公開觀測資訊站的財務報表",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
    ],
    keywords="financial, python",  # Optional
    packages=find_packages(exclude=["*tests*"]),
    include_package_data=True,
    install_requires=_process_requirements(),)
