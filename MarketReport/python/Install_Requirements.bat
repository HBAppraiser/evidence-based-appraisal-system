@echo off
set "BASE=C:\MarketReport"
cd /d "%BASE%"
IF EXIST "%BASE%\python\python.exe" (
  "%BASE%\python\python.exe" -m ensurepip --upgrade
  "%BASE%\python\python.exe" -m pip install --upgrade pip
  "%BASE%\python\python.exe" -m pip install pandas numpy matplotlib reportlab openpyxl folium branca geopy contextily pyproj
) ELSE (
  py -3 -m pip install --upgrade pip || python -m pip install --upgrade pip
  py -3 -m pip install pandas numpy matplotlib reportlab openpyxl folium branca geopy contextily pyproj ^
    || python -m pip install pandas numpy matplotlib reportlab openpyxl folium branca geopy contextily pyproj
)
echo Done.
