# POP:ONE Kill Alerts

This tool can do a few things for you when a kill in Pop:One is detected. Kills are being detected via OCR text recognition on the game window.

This tool can:

* Play audio files (randomly or specific files)
* Trigger keyboard hotkeys
* Add Stream markers or create clips on Twitch

Hotkeys can then be used in other applications such as OBS Studio, to trigger replays or animations.

**IMPORTANT**: The game window has to be open and visible on the desktop! Make it as large as possible.

# Setup

* Install Tesseract (from Google) for text detection

    For a pre-built installer of Tesseract for Windows go here:
    https://github.com/UB-Mannheim/tesseract/wiki
  
* Copy the file `.env.example` to `.env` and open it in Notepad
* Edit `.env` and adjust the variables to your preferences

## Explanation of the variables in `.env`

### General settings
| Variable                       | Description                                                                                          |
|--------------------------------|------------------------------------------------------------------------------------------------------|
| `INGAME_USERNAME`              | Your in-game username                                                                                |
| `WINDOW_NAME`                  | Name of game window. The window has to be in the front and un-minimized. Usually `Population: ONE`   |
| `TESSERACT_PATH`               | Path to your install of tesseract, probably `C:\Program Files\Tesseract-OCR\tesseract.exe`           |
| `TIME_INTERVAL_SECONDS`        | Time in seconds between individual screen reads. Set this to `1.5` or `2`                              |
| `FORCE_WINDOW_FRONT`           | Force window to be on top before every cycle - Set to `True`/`False`                                 |
| `MULTI_KILL_TIMEFRAME_SECONDS` | How long do kills stack? In seconds - `15` to `20` seconds seems nice                                |
| `AUTOREFRESH_WINDOW_POSITION`  | Recalculate window position before each cycle - Set to `True`/`False`                                |
| `DEBUG_SAVE_DETECTED_TEXT_IMAGES`| Save image, previous 2 images and detected text in a debug folder - Set to `True`/`False`          |

### Audio playback options (optional)
| Variable                       | Description                                                                                          |
|--------------------------------|------------------------------------------------------------------------------------------------------|
| `ONE_KILL_AUDIO`               | Path to your audio file for doing one kill                                                           |
| `TWO_KILLS_AUDIO`              | Path to your audio file for doing two kills                                                          |
| `THREE_KILLS_AUDIO`            | Path to your audio file for doing three kills                                                        |
| `RANDOM_AUDIO_FOLDER`          | Optional - play a random file from this folder instead of `ONE_KILL_AUDIO`                           |

### Keyboard hotkey options (optional)
| Variable                       | Description                                                                                          |
|--------------------------------|------------------------------------------------------------------------------------------------------|
| `ONE_KILL_KEYSTROKE`           | Keys to press for doing one kill. Single key (`tab`), combo (`alt+f4`), or series (`ctrl+c, ctrl+v`) |
| `TWO_KILLS_KEYSTROKE`          | Keys to press for doing two kills                                                                    |
| `THREE_KILLS_KEYSTROKE`        | Keys to press for doing three kills                                                                  |
| `KEYSTROKE_DELAY`              | Time in seconds to delay a keypress after a kill. Set this to `0` to press immediately               |

### Twitch options (optional)
| Variable                       | Description                                                                                          |
|--------------------------------|------------------------------------------------------------------------------------------------------|
| `TWITCH_USERNAME`              | Your Twitch Username                                                                                 |
| `TWITCH_ACCESS_TOKEN`          | Twitch access token - use https://twitchtokengenerator.com                                           |
| `TWITCH_CLIENT_ID`             | Twitch client id - use https://twitchtokengenerator.com                                              |
| `ENABLE_AUTO_STREAM_MARKERS`   | Enable automatic stream markers on kills - Set to `True`/`False`                                     |
| `ENABLE_AUTO_CREATE_CLIPS`     | Enable automatic clips creation on kills - Set to `True`/`False`                                     |

### ! Important if using Twitch options !
**DO NOT USE YOUR OWN CLIENT ID AND CLIENT SECRET!**

Because if you do, your access token will only be valid for 4 hours (because of the `channel:manage:broadcast` scope)

If you use `twitchtokengenerator.com`, your token will be valid for about 2 months!
On the token generator webpage, you need to allow the scopes 'clips:edit' and 'channel:manage:broadcast' for the Twitch Helix API

After two months you will need to generate a new token most likely.

### Optional Tips & Tricks

For triggering instant replays automatically, I recommend [following this tutorial](https://garlic-armadillo-pjks.squarespace.com/articles/2019/10/4/b6zieupip1h45bgewyvp6gamwube7g)

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
