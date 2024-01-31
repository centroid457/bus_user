rem ====================================
rem VERSION = (0, 0, 1)  # use new build

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
python -m build --sdist --wheel

rem FINISH =============================
pause
