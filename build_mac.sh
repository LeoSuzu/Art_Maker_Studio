#!/bin/zsh
set -e
cd "${0:A:h}"

# Pick the build interpreter.
# Tk 8.6.x (bundled with older python.org installers) crashes with a Bus error
# on recent macOS when windows are re-laid-out (e.g. switching art modes or
# reopening the drawing window). Tk 9 does not, so prefer a Python with Tk 9.
# `uv python install 3.13` provides one (python-build-standalone ships Tk 9).
has_tk9() { "$1" -c 'import sys, tkinter; sys.exit(0 if sys.version_info >= (3, 10) and tkinter.TkVersion >= 9 else 1)' 2>/dev/null; }
has_py310() { "$1" -c 'import sys, tkinter; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; }

PYTHON=""
if command -v uv >/dev/null 2>&1; then
    # Ask for the native architecture explicitly; otherwise uv may hand back
    # an x86_64 build that would run under Rosetta on Apple Silicon.
    case "$(uname -m)" in arm64) ARCH=aarch64 ;; *) ARCH=x86_64 ;; esac
    UV_REQ="cpython-3.13-macos-${ARCH}-none"
    uv python install "$UV_REQ" >/dev/null 2>&1 || true
    UV_PY="$(uv python find "$UV_REQ" 2>/dev/null || true)"
    if [[ -n "$UV_PY" ]] && has_tk9 "$UV_PY"; then PYTHON="$UV_PY"; fi
fi
if [[ -z "$PYTHON" ]]; then
    for candidate in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" >/dev/null 2>&1 && has_tk9 "$(command -v "$candidate")"; then
            PYTHON="$(command -v "$candidate")"; break
        fi
    done
fi
if [[ -z "$PYTHON" ]]; then
    for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" >/dev/null 2>&1 && has_py310 "$(command -v "$candidate")"; then
            PYTHON="$(command -v "$candidate")"; break
        fi
    done
    [[ -n "$PYTHON" ]] && echo "VAROITUS: Tk 9 -Pythonia ei löytynyt; Tk 8.6 voi kaatua uusissa macOS-versioissa. Asenna: uv python install 3.13" >&2
fi
if [[ -z "$PYTHON" ]]; then
    echo "Python 3.10+ (with tkinter) tarvitaan buildiin." >&2
    exit 1
fi
echo "Käytetään: $PYTHON ($("$PYTHON" --version), Tk $("$PYTHON" -c 'import tkinter; print(tkinter.Tcl().eval("info patchlevel"))'))"

# Recreate the build venv whenever it was made from a different interpreter.
WANT="$("$PYTHON" -c 'import sys; print(sys.version)')"
HAVE="$(.venv-build/bin/python -c 'import sys; print(sys.version)' 2>/dev/null || true)"
if [[ "$WANT" != "$HAVE" ]]; then
    rm -rf .venv-build
    "$PYTHON" -m venv .venv-build
fi
source .venv-build/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean art_maker_studio.spec

# Package the .app into a drag-to-install disk image.
VERSION="$(date +%Y%m%d)"
DMG="dist/ArtMakerStudio-${VERSION}.dmg"
STAGING="$(mktemp -d)"
cp -R dist/ArtMakerStudio.app "$STAGING/"
ln -s /Applications "$STAGING/Applications"
rm -f "$DMG"
hdiutil create -volname "Art Maker Studio" -srcfolder "$STAGING" -ov -format UDZO "$DMG"
rm -rf "$STAGING"

echo ""
echo "macOS build valmis."
echo "Sovellus löytyy: dist/ArtMakerStudio.app"
echo "Levykuva löytyy: $DMG"
