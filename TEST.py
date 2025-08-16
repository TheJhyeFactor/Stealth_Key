import base64
#our data we are getting it in by say pre defining it and or via a input
sample_string = "GeeksForGeeks is the best"

#we are then enccoding our data into  
sample_string_bytes = sample_string.encode("ascii")

#we are then encoding our ascii bytes into bas64
base64_bytes = base64.b64encode(sample_string_bytes)

#Here we
base64_string = base64_bytes.decode("ascii")

decode = "U2Vzc2lvbiBTdGFydGVkIGF0OiAyMDI1LTA4LTE3IDAwOjA4OjE3LjA2NzI3Mw=="

read = base64.b64decode(decode)

print(read)