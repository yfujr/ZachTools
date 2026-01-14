import pyautogui
import time
import random
import os
import sys

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

BITE_IMAGE = get_ref("start.png")
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
missing = []
for img in [BITE_IMAGE] + CATCH_IMAGES:
    if not os.path.exists(img):
        missing.append(os.path.basename(img))

if missing:
    print(f"[ERROR] Missing images: {missing}")
else:
    print("[SUCCESS] All images loaded.")


# ================== STOP KEY LISTENER ==================

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

def validate_images():
    for img in [BITE_IMAGE] + CATCH_IMAGES:
        if not os.path.exists(img):
            print(f"[ERROR] Missing image: {img}")
            return False
    return True


def find_on_screen(image_list, confidence=CONFIDENCE_LEVEL):
    if isinstance(image_list, str):
        image_list = [image_list]

    w, h = pyautogui.size()
    cx, cy = w // 3, h // 3
    cw, ch = w // 3, h // 3

    for img in image_list:
        if not os.path.exists(img):
            continue

        try:
            loc = pyautogui.locateOnScreen(
                img,
                confidence=confidence,
                region=(cx, cy, cw, ch),
                grayscale=True
            )
            if loc:
                return True
        except Exception:
            pass

        try:
            loc = pyautogui.locateOnScreen(
                img,
                confidence=confidence,
                grayscale=True
            )
            if loc:
                return True
        except Exception:
            pass

        if OPENCV_AVAILABLE:
            try:
                screen = pyautogui.screenshot()
                screen_gray = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)
                template = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue

                for scale in [0.6, 0.7, 0.8, 0.9, 1.0, 1.1]:
                    resized = cv2.resize(
                        template,
                        None,
                        fx=scale,
                        fy=scale,
                        interpolation=cv2.INTER_AREA
                    )
                    res = cv2.matchTemplate(
                        screen_gray,
                        resized,
                        cv2.TM_CCOEFF_NORMED
                    )
                    if np.max(res) >= confidence:
                        return True
            except Exception:
                pass

    return False


def safe_click():
    try:
        w, h = pyautogui.size()
        pyautogui.click(w // 2, h // 2)
        return True
    except Exception as e:
        print(f"[ERROR] Click failed: {e}")
        return False


# ================== MAIN LOGIC ==================

def start_fishing():
    global SESSION_FISH

    print("[🎣] ArcaneTools Fishing Helper v1.2 (macOS FIXED)")
    print(f"[⚠️] Stop key: '{stopHotkey}' | Starting in 5 seconds...")

    if not validate_images():
        return

    pyautogui.FAILSAFE = True
    print("[INFO] Move mouse to corner for emergency stop")

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()

    time.sleep(5)

    try:
        while not STOP_REQUESTED:

            # Cleanup UI
            attempts = 0
            while find_on_screen(CATCH_IMAGES) and not STOP_REQUESTED:
                time.sleep(0.5)
                attempts += 1
                if attempts > 40:
                    break

            print("\n[Action] Casting line...")
            safe_click()
            time.sleep(2.5)

            print("[State] Watching for fish...")
            hooked = False
            start_wait = time.time()

            while not hooked and not STOP_REQUESTED:
                if time.time() - start_wait > 60:
                    print("[Timeout] Recasting...")
                    break

                if find_on_screen(BITE_IMAGE, confidence=0.7):
                    hooked = True
                    print("[Bite] Fish detected!")

            if not hooked:
                continue

            print("[Action] Reeling in...")
            reel_start = time.time()
            clicks = 0

            while hooked and not STOP_REQUESTED:
                safe_click()
                clicks += 1
                time.sleep(random.uniform(0.05, 0.08))

                if clicks % 5 == 0:
                    if find_on_screen(CATCH_IMAGES):
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
