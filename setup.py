from setuptools import setup
from PROJECT import PROJECT


# =====================================================================================================================
with open("README.md", "r") as f:
    readme = f.read()


# =====================================================================================================================
setup(
  version=PROJECT.VERSION_STR,
  description=PROJECT.DESCRIPTION_SHORT,
  keywords=PROJECT.KEYWORDS,
  classifiers=[
    # "Topic :: ________________",
    *PROJECT.CLASSIFIERS_TOPICS_ADD,

    # "Framework :: ",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.11",
    "Operating System :: OS Independent",
    # "Environment :: Console",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Typing :: Typed",
  ],

  name=PROJECT.NAME_IMPORT,
  author=PROJECT.AUTHOR_NAME,
  author_email=PROJECT.AUTHOR_EMAIL,
  long_description=readme,
  long_description_content_type="text/markdown",

  url=PROJECT.AUTHOR_HOMEPAGE,  # HOMEPAGE
  project_urls={
    # "Documentation": f"https://github.com/centroid457/{NAME}/blob/main/GUIDE.md",
    "Source": f"https://github.com/centroid457/{PROJECT.NAME_IMPORT}",
  },

  packages=[PROJECT.NAME_IMPORT, ],
  install_requires=[],
  python_requires=">=3.6"
)


# =====================================================================================================================
