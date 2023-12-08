import pip

pip.main(["install", "--upgrade", "pip"])
pip.main(["install", "-r", "requirements.txt"])


# EXIT PAUSE ==========================================================================================================
# input("press Enter to close")

import time
for i in range(3, 0, -1):
    print(f"exit in [{i}] seconds")
    time.sleep(1)


# =====================================================================================================================
