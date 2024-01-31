rem ====================================
rem VERSION = (0, 0, 1)  # use new build
rem VERSION = (0, 0, 2)  # separate build/dist cmds

rem ====================================
echo off
cls

rem DEL OLD DIST =======================
REM del dist\ /q /s
rd dist\ /q /s
rd build\ /q /s
cls

rem BUILD ==============================
rem old ---------------
rem python setup.py sdist bdist_wheel

rem new ---------------
rem python -m build     # this is from docs but NOT WORKING (/build/* creation has ERROR)
rem python -m build --sdist --wheel     # it will definitely start parts by pipe!

echo ------------------------------------
echo ------------------------------------
echo ------------------------------------
echo --------- create [DIST/*] ----------
python -m build --sdist

echo ------------------------------------
echo ------------------------------------
echo ------------------------------------
echo --------- create [BUILD/*] ---------
python -m build --wheel

rem FINISH =============================
pause
