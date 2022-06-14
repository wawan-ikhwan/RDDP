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

oldBytesFrame = np.fromfile('./waiting-server.jpg', dtype=np.uint8)

# screenSize = pag.size()
screenSize = (640, 480)

lastDelay = None
updateDelayTime = time()
with mss() as sct:
  while True:
    loopTime = time()

    UDPClientSocket.sendto(b'?', addrPortServer)
    bytesFrame = b''
    lenBytesFromServer = 508
    try:
      while lenBytesFromServer == 508:
        bytesFromServer = UDPClientSocket.recvfrom(65507)[0]
        lenBytesFromServer = len(bytesFromServer)
        bytesFrame += bytesFromServer
    except:
      bytesFrame = oldBytesFrame

    # print(len(bytesFrame))

    try:
      frame = cv.imdecode(np.frombuffer(bytesFrame, dtype=np.uint8), 1)
      frame = cv.resize(frame,screenSize)
    except Exception as e:
      print(e)
      frame = cv.imdecode(np.frombuffer(oldBytesFrame, dtype=np.uint8), 1)
      frame = cv.resize(frame, screenSize)


    # FPS Management
    currentDelay = (time() - loopTime)
    if time() - updateDelayTime > 1:
      lastDelay = currentDelay
      print(len(bytesFrame))
      updateDelayTime = time()
    frame = cv.putText(frame, 
      text = str(lastDelay)[:6], 
      org = (10,20), 
      fontFace = cv.FONT_HERSHEY_SIMPLEX, 
      fontScale = 0.6, 
      thickness = 2, 
      lineType = cv.LINE_AA,
      color = (255,255,0))

    cv.imshow('RDU Client', frame)

    if cv.waitKey(1) == ord('q'):
      cv.destroyAllWindows()
      break
      
    oldBytesFrame = bytesFrame

UDPClientSocket.sendto(b'shutdown', addrPortServer)
