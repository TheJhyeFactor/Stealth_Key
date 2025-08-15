import socket


tcp_soc = socket.socket()
print("Socket Created: No Issues")


port_input = int(input(f"Please enter the socket you want to listen on: "))


tcp_soc.bind(('', port))
print("Sokcet binded to %s" %(port))

tcp_soc.listen(5)
print("Socket is listening")


while True:
    c, addr  = tcp_soc.accept()
    print('Got connection from ', addr)
    
    c.send('Thanking you for connecting' .encode())
    
    c.close
    
    break