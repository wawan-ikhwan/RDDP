def sender():
  global isRunning, UDPClientSocket ,SRV_ADDR_PORT, CLT_DATA
  CLT_DATA = b'\x16'
  UDPClientSocket.sendto(CLT_DATA, SRV_ADDR_PORT) # SEND SYN
  while isRunning:
    CLT_DATA = b'\x07'
    UDPClientSocket.sendto(CLT_DATA, SRV_ADDR_PORT)
    sleep(3)

def receiver():
  from time import time
  global isRunning, UDPClientSocket, queuePacks, SRV_DATA
  payloadSize = 508
  SRV_DATA = b''
  while isRunning:
    try:
      bytesFromServer = UDPClientSocket.recvfrom(payloadSize)[0]
      SRV_DATA += bytesFromServer
      if bytesFromServer == b'\x16':
        SRV_DATA = b''
        continue
      elif len(bytesFromServer) != payloadSize:
        # print(len(SRV_DATA))
        queuePacks.put(SRV_DATA)
        SRV_DATA = b''
        continue
    except:
      SRV_DATA = b''

# def clientHandler(queuePacks, UDPClientSocket, SRV_ADDR_PORT):
#   from threading import Thread

#   def sender():
#     UDPClientSocket.sendto(b'\x16', SRV_ADDR_PORT) # SEND SYN
#     while 1:
#       UDPClientSocket.sendto(b'\x07', SRV_ADDR_PORT)

#   def receiver():
#     payloadSize = 508
#     totalBytesFromServer = b''
#     while 1:
#       try:
#         bytesFromServer = UDPClientSocket.recvfrom(payloadSize)[0]
#         totalBytesFromServer += bytesFromServer
#         if bytesFromServer == b'\x16':
#           totalBytesFromServer = b''
#           continue
#         elif len(bytesFromServer) != payloadSize:
#           queuePacks.put(totalBytesFromServer)
#           totalBytesFromServer = b''
#           continue
#       except:
#         totalBytesFromServer = b''
  
#   tSend = Thread(target=sender, args=())
#   tReceive = Thread(target=receiver, args=())
#   tSend.start()
#   tReceive.start()
  

def unpacker(queueUnpacks, queuePacks):
  from cv2 import imdecode
  from zlib import decompress
  from numpy import frombuffer, uint8
  from time import time
  while 1:
    t0 = time()
    try: queueUnpacks.put(imdecode(frombuffer(decompress(queuePacks.get()), uint8), 1))
    except: pass
    print(time() - t0)

# def displayer(queueUnpacks, scrSize):
#   from cv2 import imshow, waitKey, destroyAllWindows, resize, putText, FONT_HERSHEY_PLAIN, LINE_AA
#   from time import time
#   from sys import float_info
#   font = FONT_HERSHEY_PLAIN
#   fps = 1
#   while 1:
#     t0 = time()
#     currentFrame = resize(queueUnpacks.get(), scrSize)
#     putText(currentFrame, str(fps), (7, 70), font, 3, (100, 255, 0), 3, LINE_AA)
#     fps = 1 / (time() - t0)
#     print(fps)
#     imshow('RDDP CLIENT', currentFrame)
#     waitKey(1)
#   destroyAllWindows()

def displayer(queueUnpacks, scrSize):
  import pygame
  import pygame.display
  import pygame.image
  import pygame.time
  import pygame.font
  import pygame.event
  from pygame.locals import DOUBLEBUF
  from cv2 import imdecode, resize
  from numpy import frombuffer, uint8
  from zlib import decompress
  from time import time
  pygame.init()
  SCR = pygame.display.set_mode(scrSize, DOUBLEBUF)
  SCR.set_alpha(None)
  clock = pygame.time.Clock()
  FONT_COMIC = pygame.font.SysFont('Cambria Math', 20)
  while 1:
    clock.tick(144)
    for EVENT in pygame.event.get():
      if EVENT.type == pygame.QUIT:
        print('Quit Game')
        break

    # if not queueUnpacks.empty(): SCR.blit(pygame.image.frombuffer(resize(queueUnpacks.get_nowait(), scrSize).tobytes(),scrSize,'BGR'),(0,0))
    try: SCR.blit(pygame.image.frombuffer(resize(imdecode(frombuffer(decompress(queueUnpacks.get()), uint8), 1), scrSize).tobytes(),scrSize,'BGR'),(0,0))
    except: pass

    SCR.blit(FONT_COMIC.render(f'QUEUE: {str(queueUnpacks.qsize())[:5]}', False, (0,255,0)),(10,30))
    SCR.blit(FONT_COMIC.render(f'FPS: {str(clock.get_fps())[:5]}', False, (0,255,0)),(10,10))
    pygame.display.update()

  print('Displayer Finished!')

if __name__ == '__main__':
  from threading import Thread
  from multiprocessing import Process, Queue
  from socket import socket, AF_INET, SOCK_DGRAM
  from keyboard import wait
  from time import sleep


  SRV_DATA, SRV_ADDR_PORT = (None,('127.0.0.1', 20001))
  CLT_DATA, CLT_ADDR_PORT = (None, ('127.0.0.1', 40001))
  UDPClientSocket = socket(AF_INET, SOCK_DGRAM)
  UDPClientSocket.bind(CLT_ADDR_PORT)
  UDPClientSocket.settimeout(1)
  isRunning = 1

  queuePacks = Queue()
  queueUnpacks = Queue()

  tSend = Thread(target=sender, args=())
  tReceive = Thread(target=receiver, args=())
  # pClient = Process(target=clientHandler, args=(queuePacks, UDPClientSocket, SRV_ADDR_PORT))
  pUnpack = Process(target=unpacker, args=(queueUnpacks, queuePacks))
  pDisplay = Process(target=displayer, args=(queuePacks, (640, 480)))
  
  print('Starting processes...')
  tSend.start()
  tReceive.start()
  # pClient.start()
  # pUnpack.start()
  pDisplay.start()
  print('Processes started!')
  
  print('Press Q to terminate.')
  wait('w')
  isRunning = 0

  print('Terminating processes...')
  # pClient.terminate()
  # pUnpack.terminate()
  pDisplay.terminate()
  tSend.join()
  tReceive.join()
  UDPClientSocket.close()
  print('Processes terminated!')
