import base64

id = str(input("Please enter the base64 str:\n"))
original = base64.b64decode(id)
print(original)