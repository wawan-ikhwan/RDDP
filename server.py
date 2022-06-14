import cv2 as cv
import numpy as np
from time import time
from mss import mss
import pyautogui as pag
import socket

# Server Config
addrPortServer = ('127.0.0.1', 20001)
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(addrPortServer)
UDPServerSocket.settimeout(2)

resolution = pag.size()
monitor = {"top": 0, "left": 0, "width": resolution[0], "height": resolution[1]}

print('UDP Server is running...')
with mss() as sct:
  while True:
    loopTime = time()

    try:
      dataFromClient, addrPortClient = UDPServerSocket.recvfrom(1024)
    except:
      addrPortClient = None

    if addrPortClient is not None:
      frame = np.asarray(sct.grab(monitor))
      frame = cv.cvtColor(frame, cv.COLOR_BGRA2BGR)
      encodeParam = (int(cv.IMWRITE_JPEG_QUALITY), 25)
      isSucceed, encImg = cv.imencode('.jpg', frame, encodeParam)
      UDPServerSocket.sendto(encImg.tobytes(), addrPortClient)

    if cv.waitKey(1) == ord('q'):
      break

print('Done.')
print(resolution)