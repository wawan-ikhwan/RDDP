import pygame
import pygame.draw # https://www.pygame.org/docs/ref/draw.html
import pygame.display # https://www.pygame.org/docs/ref/display.html
import pygame.event # https://www.pygame.org/docs/ref/event.html
import pygame.mouse # https://www.pygame.org/docs/ref/mouse.html
import pygame.key # https://www.pygame.org/docs/ref/key.html
import pygame.time # https://www.pygame.org/docs/ref/time.html
import pygame.font # https://www.pygame.org/docs/ref/font.html
import pygame.image # https://www.pygame.org/docs/ref/image.html
from pygame.locals import *

import socket
import zlib
import numpy as np
import cv2 as cv
import pyautogui as pag

SYS_MONITOR_SIZE = pag.size()

pygame.init()

# NETWORK SETUP
#  START OF USER CONFIG (You can edit it!)
addrPortServer   = ('127.0.0.1', 20001)
 # END OF USER CONFIG
payloadSize = 508 * 1 # 508 is safe maximum payload size. (should match with server)
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.settimeout(1)

# START OF GAME SETUP
pygame.display.set_caption('RDDP Client')
FONT_COMIC = pygame.font.SysFont('Cambria Math', 20)
# SCREEN_SIZE = (640, 480) # use specific monitor
SCREEN_SIZE = (SYS_MONITOR_SIZE[0]//2, SYS_MONITOR_SIZE[1]//2) # or system monitor
WIDTH, HEIGHT = (SCREEN_SIZE[0], SCREEN_SIZE[1])
SCREEN = pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF) # surface
SCREEN.set_alpha(None)
# END OF GAME SETUP

# START OF INITIALIZING
oldFrame = cv.resize(cv.imread('./waiting-server.jpg'), SCREEN_SIZE).tobytes()
# END OF INITIALIZING

# TIME VAR
sendTicker = 0
displayTicker = 0
clock = pygame.time.Clock()

print('Running...')
isGameRunning = True
while isGameRunning:

  # REFRESH
  clock.tick(60)
  currentTick = pygame.time.get_ticks()

  # START OF EVENT
  for EVENT in pygame.event.get():
    if EVENT.type == pygame.QUIT:
      isGameRunning = False
  # END OF EVENT


  # RECEIVING DATA FROM SERVER
  if currentTick - sendTicker > 3000: # RECEIVE PERIOD (in ms)
    UDPClientSocket.sendto(b'TRX', addrPortServer)
    sendTicker = currentTick
  try: # GETTING FRAME
    bytesReceived = b''
    latency = pygame.time.get_ticks()
    while True:
      bytesFromServer = UDPClientSocket.recvfrom(payloadSize)[0]
      bytesReceived += bytesFromServer
      if bytesFromServer == b'SYN':
        bytesReceived = b''
        continue
      elif len(bytesFromServer) != payloadSize:
        decompressedBytes = zlib.decompress(bytesReceived)
        currentFrame = cv.imdecode(np.frombuffer(decompressedBytes, dtype=np.uint8), 1)
        currentFrame = cv.resize(currentFrame, SCREEN_SIZE)
        currentFrame = currentFrame.tobytes()
        break
    latency = pygame.time.get_ticks() - latency
  except Exception as e:
    latency = None
    currentFrame = oldFrame
    print(e)

  # START OF USER INPUT
  mouse_pos = pygame.mouse.get_pos()
  mouse_pressed = pygame.mouse.get_pressed()
  key_pressed = pygame.key.get_pressed()
  # END OF USER INPUT
  
  #START OF UPDATING
  # END OF UPDATING
  
  # # START OF DRAWING
  SCREEN.blit(pygame.image.frombuffer(currentFrame, SCREEN_SIZE, 'BGR'), (0,0))
  SCREEN.blit(FONT_COMIC.render('FPS:'+str(clock.get_fps())[:5], False, (0,255,0)),(10,10*1))
  SCREEN.blit(FONT_COMIC.render('Latency:'+str(latency), False, (0,255,0)),(10,10*2))
  SCREEN.blit(FONT_COMIC.render('BytesReceived:'+str(len(bytesReceived)), False, (0,255,0)),(10,10*3))
  # END OF DRAWING

  # END LOOP
  oldFrame = currentFrame
  pygame.display.update()
UDPClientSocket.sendto(b'FIN', addrPortServer)
pygame.quit()