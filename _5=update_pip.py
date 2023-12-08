from setuptools import find_packages
import pip

for item in find_packages():
    print(item)
    pip.main(["install", "--upgrade", item])


# EXIT PAUSE ==========================================================================================================
# input("press Enter to close")

import time
for i in range(3, 0, -1):
    print(f"exit in [{i}] seconds")
    time.sleep(1)


# =====================================================================================================================
