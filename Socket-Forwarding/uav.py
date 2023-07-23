import RPi.GPIO as GPIO
import os,time,sys,json
import signal,socket
import serial
import numpy as np
import signal
import socket
import serial
import time

port1=6000  # the cloud server port
port2=22  # the local port
address="cloud server address"

ser = serial.Serial('/dev/ttyAMA0',115200)
ser.flushInput()
rec_buff = ''
judge2 = ''
powerKey = 4
errConn = 0

sock2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# activate the sim7020c
def powerOn(powerKey):
	print('SIM7020X is starting:')
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(powerKey,GPIO.OUT)
	time.sleep(0.1)
	GPIO.output(powerKey,GPIO.HIGH)
	time.sleep(1)
	GPIO.output(powerKey,GPIO.LOW)
	time.sleep(2)
	ser.flushInput()

# close the sim7020c
def powerDown(powerKey):
	print('SIM7020X is loging off:')
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(powerKey,GPIO.OUT)
	GPIO.output(powerKey,GPIO.HIGH)
	time.sleep(2)
	GPIO.output(powerKey,GPIO.LOW)
	time.sleep(3)
	print('Good bye')


# send the AT command
def send_simple_at(command,back,timeout):
	rec_buff = ''
	errConn = 0
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	if ser.inWaiting():
		time.sleep(0.1 )
		rec_buff = ser.read(ser.inWaiting())
	if rec_buff != '':
		if back not in rec_buff.decode():
			print(command + ' ERROR')
			while(True):
				errConn += 1
				if errConn >= 5:
					sys.exit(0)
				send_simple_at(command,back,timeout)
		else:
			print(rec_buff.decode())
	else:
		print(command + ' no responce')

# check if sim7020c is started
def check_start():
	global rec_buff
	while True:
		ser.write( 'AT\r\n'.encode())
		time.sleep(1)
		ser.write( 'AT\r\n'.encode())
		time.sleep(1)
		if ser.inWaiting():
			time.sleep(0.01)
			rec_buff = ser.read(ser.inWaiting()).decode()
		if 'OK' in rec_buff:
			rec_buff = ''
			print('SOM7020X is Start!')
			break
		else:
			powerOn(powerKey)

# check if the network has been successfully registered
def check_network():
	while(True):
		ser.write(('AT+CEREG?'+'\r\n').encode())
		time.sleep(1)
		recv = ser.readline().decode()
		print(recv)
		if '+CEREG: 0,1' in recv:
			break

# get the allocated socketId
def curr_socketId():
	global judge2
	ser.write(('AT+CSOC=1,1,1'+'\r\n').encode())
	while(True):
		print('start to check whether a TCP connection is created ')
		time.sleep(1)
		if ser.inWaiting():
			time.sleep(0.1)
			recv = ser.read(ser.inWaiting()).decode() 
		judge2 = recv[recv.find(':')+1:recv.find(':')+3].strip()
		if int(judge2) >= 0 and int(judge2) <= 4:
			break

# establish a tcp connection with the cloud server
def tcp_connect():
	print('created the TCP socket id '+ judge2 +' successfully!')
	send_simple_at('AT+CSOCON='+ str(judge2) +','+str(port1)+',\"'+ address +'\"','OK',2)
	send_simple_at('AT+CSORCVFLAG=0','OK',1)
	print("connected to relay server,socket id：",judge2)
	rec_buff = ser.read(18)
	if rec_buff != '':
		print("tcpConnect s:" + rec_buff.decode())
	print("build a socket to local port")
	sock2.connect(('127.0.0.1',port2))
	print("connected")
	print("now forwarding")

# receive from cloud, and send to local 22
def worker_thread1(sock_from,sock_to):
	print("forward from ",sock_from,"to",sock_to)
	while(True):
		rec_buff = ser.readline()
		message=""
		if b'+CSONMI: 0' in rec_buff:
			message = rec_buff.split(b',')[2]
			message_bytes = bytes.fromhex(message.decode())
			sock2.send(message_bytes)

# receive from local 22, and send to cloud
def worker_thread2(sock_from,sock_to):
	print("forward from ",sock_from,"to",sock_to)
	while(True):
		data = sock2.recv(512)
		data_hex = data.hex()
		if data:
			command = 'AT+CSOSEND='+ str(judge2) +','+ str(len(data_hex)) +','+ data_hex
			ser.write((command+'\r\n').encode())
			time.sleep(0.1) # add a small delay to avoid packet loss

def main():
	try:
		check_start()
		check_network()
		ser.flushInput()
		time.sleep(0.5)
		curr_socketId()
		tcp_connect()
		time.sleep(0.5)
		t1 = threading.Thread(target=worker_thread1,args=[address, sock2])
		t2 = threading.Thread(target=worker_thread2,args=[sock2, address])
		t1.start()
		t2.start()
		t1.join()
		t2.join()
	except Exception as e:
		send_simple_at('AT+CSOCL='+ str(judge2),'OK',1)
		if ser != None:
			ser.close()
		print(e)

if __name__ == '__main__':
	main()





