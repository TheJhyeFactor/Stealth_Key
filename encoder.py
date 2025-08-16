import base64
payload = 'your full script here'
b64 = base64.b64encode(payload.encode('utf-16le')).decode()
print(b64)
