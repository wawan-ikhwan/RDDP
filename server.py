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
resolution = (256, 144) # Uncomment for using common resolution
compression = 5 # 100 means no compress, 0 is highest compression!
encodeParam = (int(cv.IMWRITE_JPEG_QUALITY), compression)


# Server Config
addrPortServer = ('127.0.0.1', 20001)
addrPortServer = ('10.5.143.3', 20001)
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(addrPortServer)
UDPServerSocket.settimeout(2)
payloadSize = 508

monitor = {"top": 0, "left": 0, "width": screenSize[0], "height": screenSize[1]}

print('UDP Server is running...')
with mss() as sct:
  while True:
    loopTime = time()

    try:
      dataFromClient, addrPortClient = UDPServerSocket.recvfrom(1024)
      if dataFromClient == b'shutdown':
        exit()
    except:
      addrPortClient = None

    if addrPortClient is not None:
      frame = np.asarray(sct.grab(monitor))
      frame = cv.cvtColor(frame, cv.COLOR_BGRA2BGR)
      frame = cv.resize(frame, dsize=resolution)
      isSucceed, encImg = cv.imencode('.jpg', frame, encodeParam)
      bytesToSend = encImg.tobytes()
      for i in range(0, len(bytesToSend), payloadSize):
        UDPServerSocket.sendto(bytesToSend[i:i+payloadSize], addrPortClient)
    print(time() - loopTime)