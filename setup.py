from setuptools import setup, find_packages


with open("README.md", "r") as f:
    readme = f.read()

# EDIT ================================================================================================================
# EDIT ================================================================================================================
# EDIT ================================================================================================================
# EDIT ================================================================================================================
# EDIT ================================================================================================================
NAME = "bus_user"

setup(
  version="0.0.1",
  description="work with equipment over buses like Serial/i2c/...",
  keywords=[
    "serial bus", "pyserial", "serial port", "com port", "comport", "rs232",
  ],
  classifiers=[
    # "Topic :: ________________",

    # EDIT ============================================================================================================
    # EDIT ============================================================================================================
    # EDIT ============================================================================================================
    # EDIT ============================================================================================================
    # EDIT ============================================================================================================

    # "Framework :: ",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.11",
    "Operating System :: OS Independent",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Typing :: Typed",
  ],

  name=NAME,
  author="Andrei Starichenko",
  author_email="centroid@mail.ru",
  long_description=readme,
  long_description_content_type="text/markdown",

  url="https://github.com/centroid457/",  # HOMEPAGE
  project_urls={
    # "Documentation": f"https://github.com/centroid457/{NAME}/blob/main/GUIDE.md",
    "Source": f"https://github.com/centroid457/{NAME}",
  },

  packages=[NAME, ],
  install_requires=[],
  python_requires=">=3.6"
)

# =====================================================================================================================
