"""A module for simulating low-level keyboard and mouse key presses."""

import ctypes
import time
import win32con
import win32api
from src.common import utils
from ctypes import wintypes
from random import random
import serial


user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

MAPVK_VK_TO_VSC = 0

# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes?redirectedfrom=MSDN
KEY_MAP = {
    'left': 0x25,   # Arrow keys
    'up': 0x26,
    'right': 0x27,
    'down': 0x28,

    'backspace': 0x08,      # Special keys
    'tab': 0x09,
    'enter': 0x0D,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'caps lock': 0x14,
    'esc': 0x1B,
    'space': 0x20,
    'page up': 0x21,
    'page down': 0x22,
    'end': 0x23,
    'home': 0x24,
    'insert': 0x2D,
    'delete': 0x2E,

    '0': 0x30,      # Numbers
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,

    'a': 0x41,      # Letters
    'b': 0x42,
    'c': 0x43,
    'd': 0x44,
    'e': 0x45,
    'f': 0x46,
    'g': 0x47,
    'h': 0x48,
    'i': 0x49,
    'j': 0x4A,
    'k': 0x4B,
    'l': 0x4C,
    'm': 0x4D,
    'n': 0x4E,
    'o': 0x4F,
    'p': 0x50,
    'q': 0x51,
    'r': 0x52,
    's': 0x53,
    't': 0x54,
    'u': 0x55,
    'v': 0x56,
    'w': 0x57,
    'x': 0x58,
    'y': 0x59,
    'z': 0x5A,

    'f1': 0x70,     # Functional keys
    'f2': 0x71,
    'f3': 0x72,
    'f4': 0x73,
    'f5': 0x74,
    'f6': 0x75,
    'f7': 0x76,
    'f8': 0x77,
    'f9': 0x78,
    'f10': 0x79,
    'f11': 0x7A,
    'f12': 0x7B,
    'num lock': 0x90,
    'scroll lock': 0x91,

    ';': 0xBA,      # Special characters
    '=': 0xBB,
    ',': 0xBC,
    '-': 0xBD,
    '.': 0xBE,
    '/': 0xBF,
    '`': 0xC0,
    '[': 0xDB,
    '\\': 0xDC,
    ']': 0xDD,
    "'": 0xDE
}


#################################
#     C Struct Definitions      #
#################################
wintypes.ULONG_PTR = wintypes.WPARAM


class KeyboardInput(ctypes.Structure):
    _fields_ = (('wVk', wintypes.WORD),
                ('wScan', wintypes.WORD),
                ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD),
                ('dwExtraInfo', wintypes.ULONG_PTR))

    def __init__(self, *args, **kwargs):
        super(KeyboardInput, self).__init__(*args, **kwargs)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk, MAPVK_VK_TO_VSC, 0)


class MouseInput(ctypes.Structure):
    _fields_ = (('dx', wintypes.LONG),
                ('dy', wintypes.LONG),
                ('mouseData', wintypes.DWORD),
                ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD),
                ('dwExtraInfo', wintypes.ULONG_PTR))


class HardwareInput(ctypes.Structure):
    _fields_ = (('uMsg', wintypes.DWORD),
                ('wParamL', wintypes.WORD),
                ('wParamH', wintypes.WORD))


class Input(ctypes.Structure):
    class _Input(ctypes.Union):
        _fields_ = (('ki', KeyboardInput),
                    ('mi', MouseInput),
                    ('hi', HardwareInput))

    _anonymous_ = ('_input',)
    _fields_ = (('type', wintypes.DWORD),
                ('_input', _Input))


LPINPUT = ctypes.POINTER(Input)


def err_check(result, _, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    else:
        return args


user32.SendInput.errcheck = err_check
user32.SendInput.argtypes = (wintypes.UINT, LPINPUT, ctypes.c_int)


#################################
#           Functions           #
#################################
#
# @utils.run_if_enabled
# def key_down(key):
#     """
#     Simulates a key-down action. Can be cancelled by Bot.toggle_enabled.
#     :param key:     The key to press.
#     :return:        None
#     """
#
#     key = key.lower()
#     if key not in KEY_MAP.keys():
#         print(f"Invalid keyboard input: '{key}'.")
#     else:
#         x = Input(type=INPUT_KEYBOARD, ki=KeyboardInput(wVk=KEY_MAP[key]))
#         user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
#
#
# def key_up(key):
#     """
#     Simulates a key-up action. Cannot be cancelled by Bot.toggle_enabled.
#     This is to ensure no keys are left in the 'down' state when the program pauses.
#     :param key:     The key to press.
#     :return:        None
#     """
#
#     key = key.lower()
#     if key not in KEY_MAP.keys():
#         print(f"Invalid keyboard input: '{key}'.")
#     else:
#         x = Input(type=INPUT_KEYBOARD, ki=KeyboardInput(wVk=KEY_MAP[key], dwFlags=KEYEVENTF_KEYUP))
#         user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
#
#
# @utils.run_if_enabled
# def press(key, n, down_time=0.05, up_time=0.1):
#     """
#     Presses KEY N times, holding it for DOWN_TIME seconds, and releasing for UP_TIME seconds.
#     :param key:         The keyboard input to press.
#     :param n:           Number of times to press KEY.
#     :param down_time:   Duration of down-press (in seconds).
#     :param up_time:     Duration of release (in seconds).
#     :return:            None
#     """
#
#     for _ in range(n):
#         key_down(key)
#         time.sleep(down_time * (0.8 + 0.4 * random()))
#         key_up(key)
#         time.sleep(up_time * (0.8 + 0.4 * random()))
#
#
# @utils.run_if_enabled
# def click(position, button='left'):
#     """
#     Simulate a mouse click with BUTTON at POSITION.
#     :param position:    The (x, y) position at which to click.
#     :param button:      Either the left or right mouse button.
#     :return:            None
#     """
#
#     if button not in ['left', 'right']:
#         print(f"'{button}' is not a valid mouse button.")
#     else:
#         if button == 'left':
#             down_event = win32con.MOUSEEVENTF_LEFTDOWN
#             up_event = win32con.MOUSEEVENTF_LEFTUP
#         else:
#             down_event = win32con.MOUSEEVENTF_RIGHTDOWN
#             up_event = win32con.MOUSEEVENTF_RIGHTUP
#         win32api.SetCursorPos(position)
#         win32api.mouse_event(down_event, position[0], position[1], 0, 0)
#         win32api.mouse_event(up_event, position[0], position[1], 0, 0)
#################################
#     Pico Keyboard Sender      #
#################################

# Change this to the COM port your Pico appears on (check Device Manager)
PICO_PORT = "COM4"
PICO_BAUD = 115200


class PicoKeyboard:
    def __init__(self, port=PICO_PORT, baudrate=PICO_BAUD):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self._connect()

    def _connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            # Allow the Pico a moment to reset / be ready after opening serial
            time.sleep(2)
            print(f"[PICO] Connected on {self.port}")
        except Exception as e:
            print(f"[PICO] ERROR: Could not open Pico on {self.port} → {e}")
            self.ser = None

    def _send(self, msg: str):
        if self.ser is None or not self.ser.is_open:
            # Try to reconnect once
            self._connect()
        if self.ser is None or not self.ser.is_open:
            # Still failed – don't crash the bot, just skip the command
            return
        try:
            self.ser.write((msg + "\n").encode("utf-8"))
        except Exception as e:
            print(f"[PICO] Serial write error: {e}")
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def down(self, key_name: str):
        # e.g. DOWN:SPACE
        self._send(f"DOWN:{key_name}")

    def up(self, key_name: str):
        # e.g. UP:SPACE
        self._send(f"UP:{key_name}")

    def tap(self, key_name: str, duration_ms: int):
        # e.g. TAP:SPACE:50
        self._send(f"TAP:{key_name}:{duration_ms}")


pico = PicoKeyboard()


#################################
#   Key name normalization      #
#################################

def _normalize_key_name(key: str) -> str:
    """
    Convert Auto Maple's key string into a canonical name understood by the Pico.

    Examples:
        "a"         -> "A"
        "space"     -> "SPACE"
        "caps lock" -> "CAPS_LOCK"
        "page up"   -> "PAGE_UP"
        "left"      -> "LEFT"
        "f1"        -> "F1"
    """
    key = key.strip().lower()
    if not key:
        return ""
    # Replace spaces with underscore and uppercase
    return key.replace(" ", "_").upper()


#################################
#         Public API            #
#################################

@utils.run_if_enabled
def key_down(key):
    """
    Simulates a key-down action via the Pico.
    Can be cancelled by Bot.toggle_enabled (via run_if_enabled).
    """
    print("[PICO] key down")
    name = _normalize_key_name(key)
    if not name:
        print(f"[PICO] Invalid key_down('{key}') (empty after normalization)")
        return
    pico.down(name)


def key_up(key):
    """
    Simulates a key-up action via the Pico.
    Not wrapped with run_if_enabled so we don't leave keys held
    if the bot is disabled mid-press.
    """
    print("[PICO] key up")
    name = _normalize_key_name(key)
    if not name:
        print(f"[PICO] Invalid key_up('{key}') (empty after normalization)")
        return
    pico.up(name)


@utils.run_if_enabled
def press(key, n, down_time=0.05, up_time=0.1):
    """
    Presses KEY N times via the Pico, holding it for DOWN_TIME seconds
    (with a small randomization), and releasing for UP_TIME seconds
    (also randomized). Matches the behavior of the original implementation.

    KEY is normalized and sent as TAP:<NAME>:<MS>.
    """
    print("[PICO] Press:")
    name = _normalize_key_name(key)
    if not name:
        print(f"[PICO] Invalid press('{key}') (empty after normalization)")
        return

    for _ in range(n):
        # Mimic original randomness in hold time
        hold = down_time * (0.8 + 0.4 * random())
        duration_ms = int(hold * 1000)
        pico.tap(name, duration_ms)

        # Randomized delay between presses
        sleep_time = up_time * (0.8 + 0.4 * random())
        time.sleep(sleep_time)


#################################
#       Mouse stub              #
#################################

def click(position, button="left"):
    """
    Mouse clicks are not implemented via Pico in this version.
    Auto Maple rarely depends on mouse input, but if it does,
    you can either implement mouse HID on the Pico or reintroduce
    OS-level mouse events here.
    """
    print(f"[PICO] click({position}, button='{button}') ignored (not implemented)")