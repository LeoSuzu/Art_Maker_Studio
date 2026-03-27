@echo off
setlocal

py -m venv .venv-build
call .venv-build\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean art_maker_studio.spec

echo.
echo Windows build valmis.
echo Sovellus loytyy: dist\ArtMakerStudio
