# Art Maker Studio

`Art Maker Studio` on Pythonilla tehty työpöytäsovellus, joka luo kuvaan perustuvaa generatiivista taidetta kolmella moodilla:

- `Dot Art`
- `Random Walk Art`
- `Circle Art`

Sovellus käyttää `tkinter`- ja `turtle`-kirjastoja käyttöliittymään ja piirtämiseen. Valmiit työt tallennetaan automaattisesti käyttäjän kotihakemistoon kansioon `ArtMakerStudioExports`.

## Kehityskäyttö

1. Luo virtuaaliympäristö:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Asenna riippuvuudet:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Käynnistä sovellus:

```bash
python main.py
```

## Rakentaminen macOS:lle

Rakenna macOS-versio macOS-koneella:

```bash
chmod +x build_mac.sh
./build_mac.sh
```

Valmis sovellus löytyy:

```text
dist/ArtMakerStudio.app
```

Varsinainen app-bundle on `onedir`-muodossa, joten sen sisäinen sisältö kuuluu pitää yhdessä appin kanssa normaalin macOS-jakelun tapaan.

## Rakentaminen Windowsille

Rakenna Windows-versio Windows-koneella:

```bat
build_windows.bat
```

Valmis sovellus löytyy:

```text
dist\ArtMakerStudio
```

Windowsissa tulos on hakemisto, jonka koko sisältö pitää toimittaa yhdessä.

## Tärkeää paketoinnista

- Windows-build pitää tehdä Windowsissa.
- macOS-build pitää tehdä macOS:ssä.
- `PyInstaller` ei käytännössä tee luotettavaa Windows-pakettia macOS:stä tai toisin päin.
- macOS voi kysyä ensimmäisellä tallennuskerralla ruudunkaappausoikeutta, koska `JPG`- ja `PNG`-export käyttää canvasista kuvankaappausta.

## Projektin tiedostot

- `main.py`: käyttöliittymä, kuvan lataus, artin luonti ja export
- `dot_art.py`: dot art -piirto
- `random_walk_art.py`: random walk -piirto
- `circle_art.py`: circle art -piirto
- `art_maker_studio.spec`: PyInstaller-määritys
- `build_mac.sh`: macOS build-scripti
- `build_windows.bat`: Windows build-scripti
