import pyautogui
import time
import random
import os
from pynput import keyboard as pynput_keyboard

# Optional OpenCV/Numpy fallback
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except Exception:
    OPENCV_AVAILABLE = False


# ================== PATH SETUP ==================

REF_FOLDER = "ref"
script_dir = os.path.dirname(os.path.abspath(__file__))

def get_ref(filename):
    return os.path.join(script_dir, REF_FOLDER, filename)

BITE_IMAGE = get_ref("start.png")  # ❗ exclamation
CATCH_IMAGES = [
    get_ref("junk.png"),
    get_ref("treasure.png"),
    get_ref("sunken.png"),
    get_ref("fish.png")
]


# ================== CONFIG ==================

stopHotkey = 'q'
fishingRodSlot = '6'
temp_switch_slot = '1'
switch_delay = 0.12

CONFIDENCE_LEVEL = 0.8
SESSION_FISH = 0
STOP_REQUESTED = False


# ================== STARTUP CHECK ==================

print("Checking image files...")
missing = [os.path.basename(i) for i in [BITE_IMAGE] + CATCH_IMAGES if not os.path.exists(i)]

if missing:
    print(f"[ERROR] Missing images: {missing}")
    exit(1)
else:
    print("[SUCCESS] All images loaded.")


# ================== STOP KEY ==================

def on_press(key):
    global STOP_REQUESTED
    try:
        if key.char == stopHotkey:
            STOP_REQUESTED = True
            print("\n[Stop] User requested stop.")
            return False
    except AttributeError:
        pass


# ================== HELPERS ==================

def find_on_screen(images, confidence=CONFIDENCE_LEVEL):
    if isinstance(images, str):
        images = [images]

    for img in images:
        try:
            if pyautogui.locateOnScreen(img, confidence=confidence, grayscale=True):
                return True
        except Exception:
            pass

        if OPENCV_AVAILABLE:
            try:
                screen = pyautogui.screenshot()
                gray = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)
                template = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue

                res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                if np.max(res) >= confidence:
                    return True
            except Exception:
                pass

    return False


def safe_click():
    w, h = pyautogui.size()
    pyautogui.click(w // 2, h // 2)


# ================== MAIN LOGIC ==================

def start_fishing():
    global SESSION_FISH

    print("[🎣] ArcaneTools Fishing Helper v1.2 — STRICT ❗ MODE")
    print(f"[⚠️] Stop key: '{stopHotkey}' | Starting in 5 seconds...")
    pyautogui.FAILSAFE = True

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()

    time.sleep(5)

    try:
        while not STOP_REQUESTED:

            # Clear catch UI
            while find_on_screen(CATCH_IMAGES) and not STOP_REQUESTED:
                time.sleep(0.4)

            print("\n[Action] Casting line...")
            safe_click()
            time.sleep(2.5)

            # ========= WAIT FOR ❗ ONLY =========
            print("[State] Waiting for ❗ exclamation...")
            hooked = False
            start_wait = time.time()

            while not STOP_REQUESTED:
                if find_on_screen(BITE_IMAGE, confidence=0.7):
                    hooked = True
                    print("[❗] VALID BITE DETECTED")
                    time.sleep(0.3)  # allow reel window
                    break

                if time.time() - start_wait > 60:
                    print("[Timeout] No ❗ detected — recasting.")
                    break

            # 🚫 ABSOLUTE BLOCK
            if not hooked:
                continue

            # ========= REEL =========
            print("[Action] Reeling in...")
            reel_start = time.time()
            clicks = 0

            while hooked and not STOP_REQUESTED:
                safe_click()
                clicks += 1
                time.sleep(random.uniform(0.05, 0.08))

                if clicks % 5 == 0 and find_on_screen(CATCH_IMAGES):
                    SESSION_FISH += 1
                    print(f"[🐟] Catch #{SESSION_FISH}")
                    hooked = False
                    time.sleep(2)

                    print("[Action] Re-equipping rod...")
                    pyautogui.press(temp_switch_slot)
                    time.sleep(switch_delay)
                    pyautogui.press(fishingRodSlot)
                    time.sleep(1)

                if time.time() - reel_start > 60:
                    break

    finally:
        print(f"\n[Session End] Total fish caught: {SESSION_FISH}")


if __name__ == "__main__":
    start_fishing()

