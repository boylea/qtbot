import sys
import os
import glob

from setuptools import setup, find_packages

setup(name="qtbot",
      version='0.0.1',
      description="Test automation helper for PyQt applications",
      url="https://github.com/boylea/qtbot",
      author='Amy Boyle',
      author_email="amy@amyboyle.ninja",
      license="MIT",
      packages=['.'],
      install_requires=['PyUserInput'],
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: User Interfaces",
        ]
    )
