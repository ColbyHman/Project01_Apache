import socket 
from time import gmtime, strftime, sleep

time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
UDP_IP = "127.0.0.1"
UDP_PORT = 25565
name = input(" Enter a name: ")
message = input("Enter a message: ")
name= str.encode(name)
message = str.encode(message)

print(name, message, time)



client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto(name, message, (UDP_IP, UDP_PORT))
client_socket.sendto(time, (UDP_IP, UDP_PORT))




server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((UDP_IP, UDP_PORT))
while True:
    data, addr = server_socket.recvfrom(1024)
    print(data) 

