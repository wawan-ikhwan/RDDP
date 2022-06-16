import socket
from mss import mss
import zlib
import cv2 as cv
from time import time
import numpy as np

# Server Config
addrPortServer   = ('127.0.0.1', 20001)
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(addrPortServer)
UDPServerSocket.settimeout(1)

# Optimization Config
'''
Resolution Option:
None  = (original resolution)
2160p = (3840, 2160)
1440p = (2560, 1440)
1080p = (1920, 1080)
720p  = (1280, 720)
480p  = (640, 480)
360p  = (480, 360)
240p  = (426, 240)
144p  = (256, 144)
'''
resolution = (480, 360)
jpegCompression = 50 # 1 high compression, 95 low compression, 100 means no compression
zlibLevelCompression = 9 # 1 means fast but less compression, 9 means high compression but slow, 0 means no compressed
payloadSize = 508 * 1 # 508 is safe maximum UDP payload size. (should match with client)

# Initializing
receiveCounter = 0
addrPortClient = None
encodeParam = (cv.IMWRITE_JPEG_QUALITY, jpegCompression)

print("RDDP Server is listening!")
with mss() as sct:
  while True:
    loopTime = time()
  
    try:
      if loopTime - receiveCounter > 3: # RECEIVE PERIOD (in second)
        receiveCounter = loopTime
        dataFromClient, addrPortClient = UDPServerSocket.recvfrom(3)
        print(dataFromClient)
        if dataFromClient == b'FIN':
          print('Signal finish from client!')
          addrPortClient = None
          break
    except Exception as e:
      # print(e)
      addrPortClient = None

    if addrPortClient is not None:
      t0 = time()
      ss = sct.grab(sct.monitors[1])
      currentFrame = np.asarray(ss)
      
      if resolution is not None: currentFrame = cv.resize(currentFrame, resolution)
      
      currentFrame = cv.cvtColor(currentFrame, cv.COLOR_BGRA2BGR)

      result, encImg = cv.imencode('.jpg', currentFrame, encodeParam)

      bytesToSend = zlib.compress(encImg.tobytes(), zlibLevelCompression)

      UDPServerSocket.sendto(b'SYN', addrPortClient)
      for i in range(0, len(bytesToSend), payloadSize):
        UDPServerSocket.sendto(bytesToSend[i:i+payloadSize], addrPortClient)
      print(time() - t0)