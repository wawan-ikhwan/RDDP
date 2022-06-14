import socket
import pyautogui as pag
from time import sleep
from io import BytesIO
from hashlib import sha256

# Server Config
serverAddressPort   = ('127.0.0.1', 20001)

bufferSize = 65507 # MAX SIZE THAT UDP CAN HANDLE
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(serverAddressPort)
UDPServerSocket.settimeout(2)

acceptedAddr = None

payloadSize = 508

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
    listBytes = [bytesToSend[i:i+payloadSize] for i in range(0, len(bytesToSend), payloadSize)]
    for i in listBytes:
      UDPServerSocket.sendto(i,acceptedAddr)