"""
GOAL
----
start full pipeline from the beginning (without tests!) to the PYPI upload
"""


# =====================================================================================================================
import pathlib
from PROJECT import PROJECT
from requirements_checker import Packages
from cli_user import *


# =====================================================================================================================
# VERSION = (0, 0, 1)   # first attempt
# VERSION = (0, 0, 2)   # add commented testPypi
# VERSION = (0, 0, 3)   # fix --Verbose!
VERSION = (0, 0, 4)   # fix param Noisolation! used to be able build with any modules in root PyFiles


# =====================================================================================================================
cli = CliUser()
# del old --------------
cli.send("rd dist\ /q /s", 10)
cli.send("rd build\ /q /s", 10)

cmds_timeout = [
    # build new ------------
    ("python -m build --sdist -n", 60),
    ("python -m build --wheel -n", 60),

    # share ------------
    # ("twine upload dist/* -r testpypi", 90),  # TESTPYPI
    # ("twine upload dist/* --verbose", 90),    # DONT USE --VERBOSE!!!!
    ("twine upload dist/*", 90),
]
result = cli.send(cmds_timeout) and Packages().upgrade_prj(PROJECT)


# =====================================================================================================================
msg = f"[FINISHED] ({result=}) - press Enter to close"
print()
print()
print()
print(msg)
print(msg)
print(msg)
print(msg)
print(msg)
# ---------
input(msg)


# =====================================================================================================================
