import os
import base64
import cryptography
from cryptography.fernet import Fernet


x = input("please enter something random")

key = Fernet.generate_key()

fernet = Fernet(key)


eX = fernet.encrypt(x.encode())

print(eX)


eXd = fernet.decrypt(eX).decode()

print(eXd)