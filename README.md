# POP:ONE Kill Alerts

This tool will play user-provided sound files when a kill in Pop:One is detected.

Kills are being detected via OCR text recognition on the game window.

The game window has to be open and visible on the desktop! Make it as large as possible.

# Setup

* Install Tesseract (from Google) for text detection

    For a pre-built installer of Tesseract for Windows go here:
    https://github.com/UB-Mannheim/tesseract/wiki
  
* Copy the file `.env.example` to `.env` and open it in Notepad
* Edit `.env` and adjust the variables to your preferences

Explanation of the variables in `.env`:

| Variable                       | Description                                                                                        |
|--------------------------------|----------------------------------------------------------------------------------------------------|
| `INGAME_USERNAME`              | Your in-game username                                                                              |
| `WINDOW_NAME`                  | Name of game window. The window has to be in the front and un-minimized. Usually `Population: ONE` |
| `TESSERACT_PATH`               | Path to your install of tesseract, probably `C:\Program Files\Tesseract-OCR\tesseract.exe`         |
| `TIME_INTERVAL_SECONDS`        | Time in seconds between individual screen reads. Set this to `1` or `2`                            |
| `FORCE_WINDOW_FRONT`           | Force window to be on top before every cycle - Set to `True`/`False`                               |
| `MULTI_KILL_TIMEFRAME_SECONDS` | How long do kills stack? In seconds - `15` to `20` seconds seems nice                              |
| `ONE_KILL_AUDIO`               | Path to your audio file for doing one kill                                                         |
| `TWO_KILLS_AUDIO`              | Path to your audio file for doing two kills                                                        |
| `THREE_KILLS_AUDIO`            | Path to your audio file for doing three kills                                                      |
| `RANDOM_AUDIO_FOLDER`          | Optional - play a random file from this folder instead of `ONE_KILL_AUDIO`                         |
| `AUTOREFRESH_WINDOW_POSITION`  | Recalculate window position before each cycle - Set to `True`/`False`                              |

# How to run
You can simply grab the binary executable from the [releases page](https://github.com/lacksfish/popOne-kill-alerts/releases).

Alternatively do this:

* Install python3 and pip
* Run `pip install -r requirements.txt`
* Run `python src/main.py`

# Extra: How to build executable
    pip install pyinstaller
    pyinstaller -F --icon=icon.ico --paths venv/lib/site-packages src/main.py

Executable will be in the folder `dist`

An already built binary is available from the [releases page](https://github.com/lacksfish/popOne-kill-alerts/releases).
