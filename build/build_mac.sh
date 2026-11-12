#!/bin/bash
# Сборка .app и .dmg. Запускать из корня проекта: bash build/build_mac.sh
set -e
pip install pyinstaller

ICON_ARG=""
if [ -f src/assets/icon.png ]; then
  rm -rf icon.iconset && mkdir icon.iconset
  for s in 16 32 128 256 512; do
    sips -z $s $s src/assets/icon.png --out icon.iconset/icon_${s}x${s}.png >/dev/null
    sips -z $((s*2)) $((s*2)) src/assets/icon.png --out icon.iconset/icon_${s}x${s}@2x.png >/dev/null
  done
  iconutil -c icns icon.iconset -o icon.icns
  ICON_ARG="--icon icon.icns"
else
  echo "Иконка src/assets/icon.png не найдена, собираю без неё"
fi

pyinstaller --noconfirm --clean --windowed --name "kanash-oil-status" $ICON_ARG \
  --add-data "src/fonts:src/fonts" \
  --add-data "src/map/map_clean.png:src/map" \
  --add-data "src/ui/styles:src/ui/styles" \
  --add-data "src/assets:src/assets" \
  kanash-oil-status.py

rm -rf dmg_src && mkdir dmg_src
cp -R dist/kanash-oil-status.app dmg_src/
ln -s /Applications dmg_src/Applications
rm -f kanash-oil-status.dmg
hdiutil create -volname "Kanash Oil Status" -srcfolder dmg_src -ov -format UDZO kanash-oil-status.dmg
rm -rf dmg_src
echo "Готово: kanash-oil-status.dmg"
