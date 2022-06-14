import cv2 as cv
import numpy as np
from time import time
from mss import mss
import pyautogui as pag
import socket

screenSize = pag.size()

# Optimization Config
'''
2160p = (3840, 2160)
1440p = (2560, 1440)
1080p = (1920, 1080)
720p  = (1280, 720)
480p  = (640, 480)
360p  = (480, 360)
240p  = (426, 240)
144p  = (256, 144)
'''
# resolution = screenSize # Uncomment for using server resolution
resolution = (640, 480) # Uncomment for using common resolution
compression = 5 # 100 means no compress, 0 is highest compression!
encodeParam = (int(cv.IMWRITE_JPEG_QUALITY), compression)


# Server Config
addrPortServer = ('0.0.0.0', 20001)
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(addrPortServer)
UDPServerSocket.settimeout(0.5)
payloadSize = 508

monitor = {"top": 0, "left": 0, "width": screenSize[0], "height": screenSize[1]}

receivePeriode = time()

addrPortClient = None

print('RDU Server is running...')
with mss() as sct:
  while True:
    loopTime = time()

    if loopTime - receivePeriode > 3:
      try:
        dataFromClient, addrPortClient = UDPServerSocket.recvfrom(1024)
        if b'shutdown' in dataFromClient:
          print('Shutdown from client!')
          break
      except:
        addrPortClient = None
      receivePeriode = loopTime
      

    if addrPortClient is not None:
      frame = np.asarray(sct.grab(monitor))
      frame = cv.cvtColor(frame, cv.COLOR_BGRA2BGR)
      frame = cv.resize(frame, dsize=resolution)
      isSucceed, encImg = cv.imencode('.jpg', frame, encodeParam)
      bytesToSend = encImg.tobytes()
      for i in range(0, len(bytesToSend), payloadSize):
        UDPServerSocket.sendto(bytesToSend[i:i+payloadSize], addrPortClient)
    # print(time() - loopTime)