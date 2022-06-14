import cv2 as cv
import numpy as np
from time import time
from mss import mss
import pyautogui as pag
import socket

# Client Config
# addrPortServer = ('127.0.0.1', 20001)
addrPortServer = ('27.112.79.120', 20001)
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.settimeout(1)
payloadSize = 1357
recvFromSize = payloadSize * 2

defaultFrame = np.fromfile('./waiting-server.jpg', dtype=np.uint8)
oldBytesFrame = defaultFrame
# screenSize = pag.size() # uncomment for full screen
screenSize = (640, 480) # uncomment for windowed mode

sendPeriode = 0

currentDelay = []
avgDelay = 0
updateDelayTime = time()
with mss() as sct:
  while True:
    loopTime = time()

    if loopTime - sendPeriode > 3: 
      UDPClientSocket.sendto(b'?', addrPortServer)
      sendPeriode = loopTime
    bytesFrame = b''
    lenBytesFromServer = payloadSize
    try:
      while lenBytesFromServer == payloadSize:
        bytesFromServer = UDPClientSocket.recvfrom(recvFromSize)[0]
        lenBytesFromServer = len(bytesFromServer)
        bytesFrame += bytesFromServer
    except:
      bytesFrame = oldBytesFrame

    try:
      frame = cv.imdecode(np.frombuffer(bytesFrame, dtype=np.uint8), 1)
      frame = cv.resize(frame, screenSize)
    except Exception as e:
      print(e)
      frame = cv.imdecode(np.frombuffer(oldBytesFrame, dtype=np.uint8), 1)
      frame = cv.resize(frame, screenSize)

    # FPS Management
    currentDelay.append(time() - loopTime)
    if time() - updateDelayTime > 1:
      avgDelay = sum(currentDelay) / len(currentDelay)
      currentDelay = []
      print(len(bytesFrame))
      updateDelayTime = time()
    frame = cv.putText(frame, 
      text = str(avgDelay), 
      org = (10,40), 
      fontFace = cv.FONT_HERSHEY_SIMPLEX, 
      fontScale = 1, 
      thickness = 2, 
      lineType = cv.LINE_AA,
      color = (0,0,255))

    try:
      cv.imshow('RDU Client', frame)
    except:
      cv.imshow('RDU Client', cv.imdecode(defaultFrame,1))

    if cv.waitKey(1) == ord('q'):
      cv.destroyAllWindows()
      break
      
    oldBytesFrame = bytesFrame

UDPClientSocket.sendto(b'shutdown', addrPortServer)
