REM # VERSION = (0, 0, 1)   # add --verbose if fail
REM -----------------------------------------------

twine upload dist/* -r testpypi || twine upload dist/* -r testpypi --verbose
pause
