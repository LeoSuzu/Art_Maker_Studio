#!/bin/zsh
set -e

python3 -m venv .venv-build
source .venv-build/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean art_maker_studio.spec

echo ""
echo "macOS build valmis."
echo "Sovellus löytyy: dist/ArtMakerStudio.app"
