#this is going to be the translator for the encrypted messages we get weather it be ASE or Base64
import base64, socket


def base64():
    incoming = input("")
    original = base64.b64decode(incoming[::-1].encode()).decode()
    print(original)
    
    import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(s.getsockname()[0])
s.close()