import os 
from fcntl import ioctl
import socket
from threading import Thread
import signal
from pytun import TunTapDevice

port1=9000  # the cloud server port

# creating the TUN interface
def createTun():
    tun = TunTapDevice(name='tun0')
    print(tun.name)
    tun.addr = '192.168.0.1'
    tun.netmask = '255.255.255.0'
    tun.mtu = 508
    tun.persist(True)
    tun.up()
    return tun

# send the data to the cloud server
def worker_thread1(tun,sock):
    print("forward from ",tun.name,"to",sock)
    while(True):
        packet = tun.read(tun.mtu+4)
        sock.send(packet)
    close(sock)

# write data to the tun interface
def worker_thread2(sock,tun):
    print("forward from ",sock,"to",tun.name)
    while(True):
        packet = sock.recv(tun.mtu+4)
        if packet != '':
            tun.write(packet)
    close(sock)


if __name__ == "__main__":
    # establishing the socket connection
    sock1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock1.connect(('cloud server address',port1))
    print("connected to cloud server",sock1)

    # initiate the TUN interface
    tun = createTun()

    Thread(target=worker_thread1,args=[tun,sock1]).start()
    Thread(target=worker_thread2,args=[sock1,tun]).start()

