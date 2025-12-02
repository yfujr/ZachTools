import time
import pyautogui
from PIL import Image
import numpy as np
import threading
import tkinter as tk

# Safety feature
pyautogui.FAILSAFE = True

# Global state
is_running = False
status_window = None
status_label = None
total_caught = 0

def create_status_window():
    global status_window, status_label, is_running
    
    window = tk.Tk()
    window.title("Arcane Odyssey Fishing Helper")
    window.attributes('-topmost', True)
    window.attributes('-alpha', 0.7)
    window.configure(bg='navy')
    
    # Position in top-right corner
    window_width = 360
    window_height = 180
    screen_width = window.winfo_screenwidth()
    window.geometry(f'{window_width}x{window_height}+{screen_width - window_width - 20}+50')
    
    # Status label
    status_label = tk.Label(
        window,
        text="PAUSED",
        font=("Montserrat", 16, "bold"),
        fg="red",
        bg="black",
        pady=10
    )
    status_label.pack()
    
    def toggle():
        global is_running
        is_running = not is_running
        update_display()
        status = "RUNNING" if is_running else "PAUSED"
        print(f"\n>>> Process {status} <<<\n")
    
    def update_display():
        if is_running:
            status_label.config(text="RUNNING", fg="lime")
            toggle_btn.config(text="⏸ STOP", bg="#c55353", activebackground="#fd7f7f")
        else:
            status_label.config(text="PAUSED", fg="red")
            toggle_btn.config(text="▶ START", bg="#316931", activebackground="#68cf68")
    
    # Toggle button
    toggle_btn = tk.Button(
        window,
        text="▶ START",
        font=("Arial", 12, "bold"),
        command=toggle,
        bg="#316931",
        fg="white",
        activebackground="#68cf68",
        activeforeground="white",
        relief="raised",
        bd=3,
        cursor="hand2",
        pady=8
    )
    toggle_btn.pack(fill='x', padx=10, pady=10)
    
    status_window = window
    window.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close button
    window.mainloop()

def check_color(screenshot, target_color, tolerance=10):
    img_array = np.array(screenshot)
    mask = np.all(np.abs(img_array - target_color) <= tolerance, axis=2)
    return np.any(mask)

def perform_action():
    click_count = 36
    click_interval = 0.05
    
    for i in range(click_count):
        if not is_running:
            print("⏸ Action interrupted.")
            return
        pyautogui.click(button='left')
        time.sleep(click_interval)
        
    global total_caught
    total_caught += 1
    print(f"Caught fish - Total: {total_caught}")
    time.sleep(2)
    if is_running:
        pyautogui.click(button='left')

def main():
    global is_running
    
    target_color = (252, 82, 83)  # RGB: Red for fishing indicator
    tolerance = 25
    interval = 1.5
    center_box = 400
    
    screen_w, screen_h = pyautogui.size()
    left = max(0, screen_w // 2 - center_box // 2)
    top = max(0, screen_h // 2 - center_box // 2)
    
    print("="*60)
    print("          ARCANE ODYSSEY FISHING HELPER")
    print("="*60)
    print(f"📺 Screen size: {screen_w}x{screen_h}")
    print(f"🎯 Monitoring region: {left},{top} to {left+center_box},{top+center_box}")
    print(f"🎨 Target color: RGB{target_color} (tolerance: {tolerance})")
    print(f"⏱️  Check interval: {interval} seconds")
    print("\n🔘 Click the START button in the popup window to begin")
    print("🚨 Emergency stop: Move mouse to top-left corner")
    print("="*60 + "\n")
    
    try:
        while True:
            if is_running:
                screenshot = pyautogui.screenshot(region=(left, top, center_box, center_box))
                
                if check_color(screenshot, target_color, tolerance):
                    perform_action()
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Start status window in background thread
    window_thread = threading.Thread(target=create_status_window, daemon=True)
    window_thread.start()
    
    # Give window time to initialize
    time.sleep(0.5)
    
    # Start main detection loop
    main()