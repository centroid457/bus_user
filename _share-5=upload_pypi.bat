REM # VERSION = (0, 0, 1)   # add --verbose if fail
REM -----------------------------------------------

echo off
cls
echo UPLOAD TO PYPI?
echo UPLOAD TO PYPI?
echo UPLOAD TO PYPI?
echo UPLOAD TO PYPI?
echo UPLOAD TO PYPI?
pause

twine upload dist/* || twine upload dist/* --verbose
pause
