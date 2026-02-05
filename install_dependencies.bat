@echo off
echo Installing Python dependencies...
echo.

pip install streamlit>=1.31.0
pip install streamlit-authenticator>=0.2.3
pip install pandas>=2.0.0
pip install plotly>=5.18.0
pip install Pillow>=10.0.0
pip install python-dateutil>=2.8.2
pip install openpyxl>=3.1.0

echo.
echo Installation complete!
echo.
echo You can now run the app with: streamlit run app.py
pause
