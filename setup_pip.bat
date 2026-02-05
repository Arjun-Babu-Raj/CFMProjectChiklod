@echo off
echo Downloading and installing pip...
echo.

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

echo.
echo Installing project dependencies...
echo.

python -m pip install streamlit>=1.31.0
python -m pip install streamlit-authenticator>=0.2.3
python -m pip install pandas>=2.0.0
python -m pip install plotly>=5.18.0
python -m pip install Pillow>=10.0.0
python -m pip install python-dateutil>=2.8.2
python -m pip install openpyxl>=3.1.0

echo.
echo Setup complete! Cleaning up...
del get-pip.py

echo.
echo You can now run: streamlit run app.py
pause
