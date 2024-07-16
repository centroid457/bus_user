REM VERSION = (0, 0, 1)   # add --verbose if fail
REM VERSION = (0, 0, 2)   # add testpypi (commented)
REM -----------------------------------------------

echo off
cls
echo UPLOAD TO PYPI?
echo UPLOAD TO PYPI?
echo UPLOAD TO PYPI?
echo UPLOAD TO PYPI?
echo UPLOAD TO PYPI?
pause

REM twine upload dist/* -r testpypi || twine upload dist/* -r testpypi --verbose
twine upload dist/* || twine upload dist/* --verbose
pause
