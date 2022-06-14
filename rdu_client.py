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
#  START OF USER CONFIG (You can edit it!)
serverAddressPort   = ('127.0.0.1', 20001)
# serverAddressPort   = ('27.112.79.120', 20001)
 # END OF USER CONFIG
payloadSize = 508 # MAX SIZE THAT UDP CAN HANDLE
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.settimeout(2)

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
oldFrames = open('waiting-server.jpg','rb').read()
# END OF INITIALIZING

print('Starting...')
isGameRunning = True
while isGameRunning:

  # REFRESH
  SCREEN.fill((255, 255, 255))
  current_ticks = pygame.time.get_ticks()
  if sendCounter <= 0:
    UDPClientSocket.sendto(b'?', serverAddressPort)
    sendCounter = 6
  currentFrames = b''
  try:
    bytesFromServer = UDPClientSocket.recvfrom(payloadSize)[0]
    currentFrames += bytesFromServer
    while len(bytesFromServer) == payloadSize:
      bytesFromServer = UDPClientSocket.recvfrom(payloadSize)[0]
      currentFrames += bytesFromServer
  except Exception as e:
    currentFrames = oldFrames
    print(e)
  print('f',len(currentFrames))
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
  try:
    im = Image.open(BytesIO(currentFrames))
    im = im.resize((WIDTH, HEIGHT))
    imBytes = im.tobytes()
  except:
    im = Image.open(BytesIO(oldFrames))
    im = im.resize((WIDTH, HEIGHT))
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
  oldFrames = currentFrames

pygame.quit()