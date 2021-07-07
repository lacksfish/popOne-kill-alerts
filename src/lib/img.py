import cv2
import numpy
import logging
import win32gui
import win32con
import ctypes

from ctypes import wintypes
from mss import mss


class ScreenShooter:
    def __init__(self, window_name='population: one', force_window_front=False, autorefresh_window_position=True):
        self.window_name = window_name
        self.force_win_front = force_window_front

        # get window
        toplist, winlist = [], []

        def enum_cb(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

        win32gui.EnumWindows(enum_cb, toplist)
        window = [(hwnd, title) for hwnd, title in winlist if title.lower().startswith(window_name.lower())]

        if len(window) == 0:
            error = f'No window with the name "{window_name}" detected'
            print(error)
            raise Exception(error)

        hwnd = window[0][0]
        self.hwnd = hwnd

        # this gets the window size, comparing it to `dimensions` will show a difference
        winsize = win32gui.GetClientRect(self.hwnd)
        self.winsize = winsize

        logging.getLogger().info(f"Detected Window Name: {window[0][1]}")
        logging.getLogger().info(f"Detected Window Size: {winsize[2]}x{winsize[3]}")

        if winsize[2] == 0 or winsize[3] == 0:
            error = 'Window size is zero - un-minimize the game window and restart this tool'
            logging.getLogger().error(error)
            raise Exception(error)

        if self.force_win_front:
            # this sets window to front if it is not already
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        self.refresh_window_size_and_position()
        self.autorefresh_window_position = autorefresh_window_position

    def refresh_window_size_and_position(self):
        # this gets the window size, comparing it to `dimensions` will show a difference
        winsize = win32gui.GetClientRect(self.hwnd)
        self.winsize = winsize

        if winsize[2] == 0 or winsize[3] == 0:
            error = 'Window size is zero - un-minimize the game window ?!'
            logging.getLogger().error(error)
            raise Exception(error)

        # `rect` is for the window coordinates (has top, left, right, bottom)
        rect = ctypes.wintypes.RECT()
        # and then the coordinates of the window go into `rect`
        ctypes.windll.dwmapi.DwmGetWindowAttribute(ctypes.wintypes.HWND(self.hwnd),
                                                   ctypes.wintypes.DWORD(9),
                                                   ctypes.byref(rect),
                                                   ctypes.sizeof(rect)
                                                   )
        self.rect = rect

        self.dims = {
            # These are sort of magic estimations - feel free to experiment here
            "top": int(rect.top) + int(winsize[3] * 0.6),
            "left": int(rect.left) + int(winsize[2] * 0.25),
            "width": int(winsize[2] * 0.5),
            "height": winsize[3] - int(winsize[3] * 0.6)
        }

    def take_screenshot(self):
        hwnd = self.hwnd

        if self.autorefresh_window_position:
            self.refresh_window_size_and_position()

        if self.force_win_front:
            # this sets window to front if it is not already
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        with mss() as sct:
            image = sct.grab(self.dims)
            open_cv_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGRA2BGR) # https://stackoverflow.com/a/14140796

            # If you want to debug - write the screenshot to file to see what you're capturing
            #cv2.imwrite('screenshot.png', open_cv_image)

            return open_cv_image
