REM del dist\ /q /s
rd dist\ /q /s

python setup.py sdist bdist_wheel
pause
