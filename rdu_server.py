import socket
import pyautogui as pag
from time import sleep
from io import BytesIO
from hashlib import sha256

# Server Config
serverAddressPort   = ('127.0.0.1', 20001)
'''
Server Resolution:
2160p=3840x2160
1440p=2560*1440
1080p=1920*1080
720p=1280*720
480p=640*480
360p=480*360
240p=426*240
144p=256*144
'''
# serverResolution = (426, 240)

bufferSize = 65507 # MAX SIZE THAT UDP CAN HANDLE
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(serverAddressPort)
UDPServerSocket.settimeout(2)

acceptedAddr = None

print("RDU Server is listening!")
while True:
  if acceptedAddr is None:
    try:
      bytesAddressPair = UDPServerSocket.recvfrom(1024)
      dataFromClient = bytesAddressPair[0]
      address = bytesAddressPair[1]
      if dataFromClient == b'?':
        acceptedAddr = address
    except socket.timeout:
      pass
  else:
    im = pag.screenshot()
    temp = BytesIO()
    im.save(temp, format="jpeg", optimize=True, quality=10)
    bytesToSend = temp.getvalue()
    UDPServerSocket.sendto(bytesToSend,acceptedAddr)