import rsa

hiKey, shhKey = rsa.newkeys(512)


m = input("Just say somehting lol:\n")


encm = rsa.encrypt(m.encode(),hiKey)



print(encm)


decm = rsa.decrypt(encm, shhKey).decode()

print(decm)