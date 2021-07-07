from dotenv import load_dotenv
load_dotenv()

import cv2
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import time
import random
import logging
from logging.handlers import RotatingFileHandler
import pytesseract
from pygame import mixer

from lib.img import ScreenShooter
from lib.utils import maxDiff, jaro_winkler
from lib.funcs import image_improve, image_improve_rotation, detect_text, play_audio

logging.basicConfig(format='%(message)s')
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger()

if not os.path.isfile(os.getenv('TESSERACT_PATH') if os.getenv('TESSERACT_PATH') else ''):
    error = 'OOPS - Path to Tesseract not found - Did you install it? Check the Setup Guide in the README file'
    logger.error(error)
    input("Press Enter to continue...")
    raise Exception(error)

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

INGAME_USERNAME = os.getenv('INGAME_USERNAME')
WINDOW_NAME = os.getenv('WINDOW_NAME')
TIME_INTERVAL_SECONDS = os.getenv('TIME_INTERVAL_SECONDS')
MULTI_KILL_TIMEDELTA_SECONDS = int(os.getenv('MULTI_KILL_TIMEFRAME_SECONDS'))
FORCE_WINDOW_FRONT = os.getenv("FORCE_WINDOW_FRONT", 'False').lower() in ('true', '1', 't')
AUTOREFRESH_WINDOW_POSITION = os.getenv("AUTOREFRESH_WINDOW_POSITION", 'False').lower() in ('true', '1', 't')
RANDOM_AUDIO_FOLDER = os.getenv('RANDOM_AUDIO_FOLDER')

DEBUG_SAVE_DETECTED_TEXT_IMAGES = os.getenv("DEBUG_SAVE_DETECTED_TEXT_IMAGES", 'False').lower() in ('true', '1', 't')

if DEBUG_SAVE_DETECTED_TEXT_IMAGES:
    fileHandler = RotatingFileHandler('debug.log', mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
    fileHandler.setFormatter(logging.Formatter('%(asctime)s || %(message)s'))
    logger.addHandler(fileHandler)

logger.info('(x) Booting ... Pop:ONE Kill Alerts')
logger.info('(x) Brought to you by DatByte !\n')

logger.info(f"!NOTICE - Detecting username: {INGAME_USERNAME}")
logger.info(f"!NOTICE - Waiting {TIME_INTERVAL_SECONDS} seconds between reads")
logger.info(f"!NOTICE - Multikill timedelta is {MULTI_KILL_TIMEDELTA_SECONDS} seconds")
logger.info(f"!NOTICE - Force window to front {'enabled' if FORCE_WINDOW_FRONT else 'disabled'}")
logger.info(f"!NOTICE - Autorefresh window position {'enabled' if AUTOREFRESH_WINDOW_POSITION else 'disabled'}\n")
if DEBUG_SAVE_DETECTED_TEXT_IMAGES:
    os.makedirs("DEBUG_images", exist_ok=True)
    logger.info("! DEBUGGING MODE ! Saving detections to img files enabled\n")

try:
    sct = ScreenShooter(force_window_front=FORCE_WINDOW_FRONT,
                        window_name=WINDOW_NAME,
                        autorefresh_window_position=AUTOREFRESH_WINDOW_POSITION)

    # Init audio for windows
    if os.name == 'nt':
        mixer.init()

    kill_ts_list = []
    # kill_ts_list = [{'time': time.time(), 'name': 'BobbyBoyy'}]
    DEBUG_detected_list = []

    logger.info('(x) Everything looks good, initialized. Running ...\n')

    while True:
        last_read_delay = 0
        time.sleep(float(TIME_INTERVAL_SECONDS) - last_read_delay)
        start_ts = time.time()

        img = None
        try:
            img = sct.take_screenshot()
        except Exception as e:
            logger.error(e)
            logger.info('no window found')
            continue

        # Debug mode, always store last 3 images and save them when detection occurs
        # (save detection image and the two previous images leading up to it)
        if DEBUG_SAVE_DETECTED_TEXT_IMAGES:
            DEBUG_detected_list.append(img)
            if len(DEBUG_detected_list) > 3:
                DEBUG_detected_list = DEBUG_detected_list[-3:]

        img_opti = image_improve(img)
        try:# Try improving detection by rotating image so text is horizontal
            img_rotated, rotation_degree = image_improve_rotation(img_opti)
            if abs(rotation_degree) > 1.5:
                img_opti = img_rotated
        except:
            pass
        # Detect text
        lines = detect_text(img_opti)

        # Clean old entries
        kill_ts_list = [x for x in kill_ts_list if x['time'] >= time.time() - MULTI_KILL_TIMEDELTA_SECONDS * 4]
        logger.info(f'Recent kills: {kill_ts_list}')

        for line in lines:

            # Check if knocked down appears in current line - or very similar
            max_distance_knocked_down = 0 # Distance value between 'knocked down' and very similar string
            knocked_down_typo_str = '' # Holds the very similar 'knocked down' string

            if 'knocked down' in line:
                max_distance_knocked_down = 1
                knocked_down_typo_str = 'knocked down'
            else:
                # Search for OCR error in 'knocked down'
                line_each_word = line.split(' ')
                pairs_of_two_words = zip(line_each_word, line_each_word[1:])
                for pair in pairs_of_two_words:
                    if len(pair) == 2:
                        knocked_down_typo = f'{pair[0]} {pair[1]}'
                        distance = jaro_winkler(knocked_down_typo, 'knocked down')
                        if distance > max_distance_knocked_down:
                            max_distance_knocked_down = distance
                            knocked_down_typo_str = knocked_down_typo

            if "remaining" in line:
                logger.info(repr(line))
            elif 'knocked down' in line or max_distance_knocked_down > 0.9:
                logger.info(f'Detected:\t{line}')
                splitted = line.split(knocked_down_typo_str)
                splitted[0] = splitted[0].strip()
                # If kill is done by our username
                if INGAME_USERNAME.lower() in splitted[0].lower() or jaro_winkler(INGAME_USERNAME.lower(), splitted[0].lower()) > 0.85:
                    # Get parsed enemy name
                    enemy_name = splitted[1].replace('|', '').strip()
                    if enemy_name == '':
                        continue

                    # Check if known kill - already announced? via name
                    known = False
                    for kill in kill_ts_list:
                        s = jaro_winkler(enemy_name, kill['name'])

                        if s > 0.65 and time.time() < kill['time'] + MULTI_KILL_TIMEDELTA_SECONDS:
                            known = True

                    # If new kill
                    if not known:
                        kill_ts_list.append({
                            'time': time.time(),
                            'name': enemy_name
                        })

                        if DEBUG_SAVE_DETECTED_TEXT_IMAGES:
                            curr_folder = f'DEBUG_images\\{int(time.time())}'
                            os.makedirs(curr_folder, exist_ok=True)
                            log = open(f'{curr_folder}\\debug.txt', 'w')
                            log.write(line)
                            log.close()
                            cv2.imwrite(f'{curr_folder}\\optimized.png', img_opti)
                            for idx, img in enumerate(DEBUG_detected_list):
                                cv2.imwrite(f'{curr_folder}\\{idx}.png', img)

                        timestamps = [x['time'] for x in kill_ts_list]

                        if len(kill_ts_list) > 2 and maxDiff(timestamps[-3:]) <= MULTI_KILL_TIMEDELTA_SECONDS:
                            play_audio(os.getenv('THREE_KILLS_AUDIO'))
                        elif len(kill_ts_list) > 1 and maxDiff(timestamps[-2:]) <= MULTI_KILL_TIMEDELTA_SECONDS:
                            play_audio(os.getenv('TWO_KILLS_AUDIO'))
                        else:
                            if os.path.isdir(RANDOM_AUDIO_FOLDER if RANDOM_AUDIO_FOLDER is not None else ''):
                                audio = random.choice([x for x in os.listdir(RANDOM_AUDIO_FOLDER) if os.path.isfile(os.path.join(RANDOM_AUDIO_FOLDER, x))])
                                play_audio(os.path.join(RANDOM_AUDIO_FOLDER, audio))
                            else:
                                play_audio(os.getenv('ONE_KILL_AUDIO'))

        end_ts = time.time()
        last_read_delay = end_ts - start_ts
        logger.info(f"----------- Cycle took {last_read_delay} seconds")

except Exception as e:
    logger.error(e)
    pass

input("Press Enter to continue...")