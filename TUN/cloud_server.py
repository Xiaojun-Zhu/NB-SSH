import sys,socket
from threading import Thread
import base64

port1=6000  # waiting for NAT server's connection
port2=9000  # data to this port2 are forwarded to the NAT server

# first wait for connection from the NAT server
sock1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock1.bind(('',port1))
sock1.listen()
s_sock1,addr1=sock1.accept()

print("NAT server connected@",addr1)
print("waiting for client's connection")

# then wait for connection from the NAT client
sock2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock2.bind(('',port2))
sock2.listen()
s_sock2,addr2=sock2.accept()
print("client connected@",addr2)
s_sock1.send(b's')
print("now forwarding")

# data forwarding
def worker_thread(sock_from,sock_to):
    print("forward from ",sock_from,"to",sock_to)
    while(True):
        a=sock_from.recv(2048)
        sock_to.send(a)
    close(sock_from)
    close(sock_to)

Thread(target=worker_thread,args=[s_sock1,s_sock2]).start()
Thread(target=worker_thread,args=[s_sock2,s_sock1]).start()