@echo off
rem Сборка exe. Запускать из корня проекта: build\build_windows.bat
pip install pyinstaller pillow || exit /b 1

set ICON_ARG=
if exist src\assets\icon.png (
  python -c "from PIL import Image; Image.open('src/assets/icon.png').save('icon.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
  set ICON_ARG=--icon icon.ico
) else (
  echo Иконка src\assets\icon.png не найдена, собираю без неё
)

pyinstaller --noconfirm --clean --windowed --onefile --name "kanash-oil-status" %ICON_ARG% ^
  --add-data "src/fonts;src/fonts" ^
  --add-data "src/map/map_clean.png;src/map" ^
  --add-data "src/ui/styles;src/ui/styles" ^
  --add-data "src/assets;src/assets" ^
  kanash-oil-status.py

echo Готово: dist\kanash-oil-status.exe
