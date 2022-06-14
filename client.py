import cv2 as cv
import numpy as np
from time import time
from mss import mss
import pyautogui as pag

resolution = pag.size()
monitor = {"top": 0, "left": 0, "width": resolution[0], "height": resolution[1]}
lastDelay = None
updateDelayTime = time()
with mss() as sct:
  while True:
    loopTime = time()

    # FPS Management
    currentDelay = (time() - loopTime)
    if time() - updateDelayTime > 1:
      lastDelay = 1 / currentDelay
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

print('Done.')
print(resolution)