echo version 0.0.2

echo off
cls || clear


echo =====================================================
echo =====================================================
echo =====================================================
echo =============2[UPDATE PIP REQUIREMENTS]==============
pip install --upgrade -r requirements.txt || pip3 install --upgrade -r requirements.txt || python -m pip install --upgrade -r requirements.txt || python3 -m pip install --upgrade -r requirements.txt || echo [ERROR] REQUIREMENTS UPDATE
echo _
echo _
echo _
echo _
echo _
echo _
echo _

echo =====================================================
echo =====================================================
echo =====================================================
echo =============4[FINISH]===============================
pause
