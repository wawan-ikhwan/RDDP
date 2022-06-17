import socket
from mss import mss
import zlib
import cv2 as cv
from time import time
import numpy as np
import pyautogui as pag

SYS_MONITOR_SIZE = pag.size()

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
resolution = (640, 480)
isJpg = True # True means JPG, False means PNG
jpegCompression = 45 # 1 high compression, 95 low compression, 100 means no compression
pngCompression = 9 # 0 means no compression 9 means high compression
zlibLevelCompression = 9 # 1 means fast but less compression, 9 means high compression but slow, 0 means no compressed
payloadSize = 508 * 1 # 508 is safe maximum UDP payload size. (should match with client)
regionOfInterest = {'left': (SYS_MONITOR_SIZE[0]//2)-100, 'top': (SYS_MONITOR_SIZE[1]//2)-100, 'width': 100, 'height': 100} # set none for full screen
regionOfInterest = None

# Initializing
receiveCounter = 0
addrPortClient = None
if isJpg:
  encodeParam = (cv.IMWRITE_JPEG_QUALITY, jpegCompression)
  ext = '.jpg'
else:
  encodeParam = (cv.IMWRITE_PNG_COMPRESSION, pngCompression)
  ext = '.png'

print("RDDP Server is listening!")
with mss() as sct:
  monitor = regionOfInterest if regionOfInterest is not None else sct.monitors[1]
  while True:
    loopTime = time()
  
    try:
      if loopTime - receiveCounter > 3: # RECEIVE PERIOD (in second)
        receiveCounter = loopTime
        dataFromClient, addrPortClient = UDPServerSocket.recvfrom(3)
        # print(dataFromClient)
        if dataFromClient == b'\x1b': # ESC (ESCAPE ASCII)
          print('Signal ESC from client!')
          addrPortClient = None
          break
    except Exception as e:
      # print(e)
      addrPortClient = None

    if addrPortClient is not None:
      currentFrame = np.asarray(sct.grab(monitor))
      currentFrame = cv.cvtColor(currentFrame, cv.COLOR_BGRA2BGR)
      if resolution is not None: currentFrame = cv.resize(currentFrame, resolution)
      result, encImg = cv.imencode(ext, currentFrame, encodeParam)
      bytesToSend = zlib.compress(encImg.tobytes(), zlibLevelCompression)
      UDPServerSocket.sendto(b'\x16', addrPortClient) # SEND SYN ASCII
      for i in range(0, len(bytesToSend), payloadSize):
        UDPServerSocket.sendto(bytesToSend[i:i+payloadSize], addrPortClient)