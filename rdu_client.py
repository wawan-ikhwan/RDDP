import pygame
import pygame.draw # https://www.pygame.org/docs/ref/draw.html
import pygame.display # https://www.pygame.org/docs/ref/display.html
import pygame.event # https://www.pygame.org/docs/ref/event.html
import pygame.mouse # https://www.pygame.org/docs/ref/mouse.html
import pygame.key # https://www.pygame.org/docs/ref/key.html
import pygame.time # https://www.pygame.org/docs/ref/time.html
import pygame.font # https://www.pygame.org/docs/ref/font.html
import pygame.image # https://www.pygame.org/docs/ref/image.html

from PIL import Image
import pyautogui as pag
import socket
from time import sleep
from hashlib import sha256
from io import BytesIO

pygame.init()

# NETWORK SETUP
 # START OF USER CONFIG (You can edit it!)
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
 # END OF USER CONFIG
bufferSize = 65507 # MAX SIZE THAT UDP CAN HANDLE
# repeatReceive = ((serverResolution[0] * serverResolution[1] * 3) // bufferSize) + 1
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.settimeout(2)

# print(len(byteFromServer))
# print(sha256(byteFromServer).hexdigest())

# START OF GAME SETUP
pygame.display.set_caption('RDU')
FONT_COMIC = pygame.font.SysFont("Comic Sans MS", 20)
WIDTH, HEIGHT = (640, 480)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT)) # surface
# END OF GAME SETUP

# START OF INITIALIZING
avgBuff = []
lastAvgBuff = 0
sendCounter = 0
oldByteFromServer = open('hoho.jpg','rb').read()
# END OF INITIALIZING

print('Starting...')
isGameRunning = True
while isGameRunning:

  # REFRESH
  SCREEN.fill((255, 255, 255))
  current_ticks = pygame.time.get_ticks()
  if sendCounter <= 0:
    UDPClientSocket.sendto(b'?', serverAddressPort)
    sendCounter = 3
  byteFromServer = oldByteFromServer
  try:
    byteFromServer = UDPClientSocket.recvfrom(bufferSize)[0]
  except Exception as e:
    print(e)
  oldByteFromServer = byteFromServer
  sendCounter -= 1

  # START OF EVENT
  for EVENT in pygame.event.get():
    if EVENT.type == pygame.QUIT:
      isGameRunning = False
  # END OF EVENT

  # START OF USER INPUT
  mouse_pos = pygame.mouse.get_pos()
  mouse_pressed = pygame.mouse.get_pressed()
  key_pressed = pygame.key.get_pressed()
  # END OF USER INPUT
  
  # START OF UPDATING
  # im = pag.screenshot()
  im = Image.open(BytesIO(byteFromServer))
  # im = Image.frombuffer('RGB', serverResolution, byteFromServer)
  im = im.resize((WIDTH, HEIGHT))
  # im = im.resize((480, 360))
  imBytes = im.tobytes()
  # END OF UPDATING
  
  # START OF DRAWING
  fb = pygame.image.frombuffer(imBytes, im.size, im.mode)
  SCREEN.blit(fb, (0,0))
  if (len(avgBuff) > 100):
    lastAvgBuff = sum(avgBuff) // 100
    avgBuff = []
  else:
    SCREEN.blit(FONT_COMIC.render(str(lastAvgBuff), False, (0,255,0)),(10,10))
  SCREEN.blit(FONT_COMIC.render(str(len(imBytes)), False, (0,255,0)),(10,30))
  # END OF DRAWING

  # END LOOP
  pygame.display.update()
  avgBuff.append(pygame.time.get_ticks() - current_ticks)
  


pygame.quit()