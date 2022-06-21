def grabber(queueChunks , grabArea):
  from mss import mss
  from time import time
  with mss() as sct:
    while 1:
      queueChunks.put(sct.grab(grabArea))


def combiner(queueScr, queueTopChunk, queueBotChunk):
  from numpy import asarray, concatenate
  from time import time
  currentTop = queueTopChunk.get()
  currentBot = queueBotChunk.get()
  while 1:
    if not queueTopChunk.empty(): currentTop = asarray(queueTopChunk.get_nowait())
    if not queueBotChunk.empty(): currentBot = asarray(queueBotChunk.get_nowait())
    queueScr.put(concatenate((currentTop,currentBot), 0))

def packer(queuePacks, queueScr, srvRes, jpegCompression, zlibLevel):
  from cv2 import resize, cvtColor, COLOR_BGRA2BGR, imencode, IMWRITE_JPEG_QUALITY
  from zlib import compress
  from time import time
  while 1:
    # t0 = time()
    queuePacks.put(compress(imencode('.jpg', cvtColor(resize(queueScr.get(), srvRes), COLOR_BGRA2BGR), (IMWRITE_JPEG_QUALITY, jpegCompression))[1].tobytes(), zlibLevel))
    # print(time() - t0)

def serverHandler(queuePacks, UDPServerSocket):
  from threading import Thread
  from time import time
  global cltValidAddrPort
  cltValidAddrPort = None

  def receiver(UDPServerSocket):
    global cltValidAddrPort
    cltData, cltAddrPort = None, None
    while 1:
      try: cltData, cltAddrPort = UDPServerSocket.recvfrom(3)
      except: pass
      if cltData == b'\x16':
        cltData = None
        cltValidAddrPort = cltAddrPort
        print('SYNED', cltValidAddrPort)

  def sender(queuePacks, UDPServerSocket):
    global cltValidAddrPort
    payloadSize = 508
    while 1:
      if cltValidAddrPort:
        # t0 = time()
        bytesToSend = queuePacks.get()
        UDPServerSocket.sendto(b'\x16', cltValidAddrPort)
        for i in range(0, len(bytesToSend), payloadSize):
          UDPServerSocket.sendto(bytesToSend[i:i+payloadSize], cltValidAddrPort)
        # print(time() - t0)
    return

  tReceiver = Thread(target=receiver, args=(UDPServerSocket,))
  tSend = Thread(target=sender, args=(queuePacks, UDPServerSocket,))
  tReceiver.start()
  tSend.start()
  
if __name__ == '__main__':
  from multiprocessing import Process, Queue
  from socket import socket, AF_INET, SOCK_DGRAM
  from pyautogui import size as screenSize
  from keyboard import wait

  # NETWORK CONFIG
  SRV_ADDR_PORT = ('127.0.0.1', 20001)
  UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
  UDPServerSocket.bind(SRV_ADDR_PORT)
  UDPServerSocket.settimeout(0.5)

  # MONITOR CONFIG
  MON_SIZE = screenSize() # (ORIGINAL SERVER MONITOR RESOLUTION)
  MON_HEIGHT_HALF = MON_SIZE[1] // 2
  MON_SIZE_HALF = (MON_SIZE[0], MON_HEIGHT_HALF)

  # GRAB CONFIG
  TOP_GRAB = {'left':0, 'top': 0, 'width': MON_SIZE_HALF[0], 'height':MON_SIZE_HALF[1]}
  BOT_GRAB = {'left':0, 'top': MON_SIZE_HALF[1], 'width': MON_SIZE_HALF[0], 'height':MON_SIZE_HALF[1]}

  # RESOLUTION CONFIG
  SRV_RES = MON_SIZE
  SRV_RES = (640, 480)

  # OPTIMIZATION CONFIG
  JPEG_COMPRESSION = 75 # 0 HIGH COMPRESSION, 100 NO COMPRESSION
  ZLIB_LEVEL = -1 # -1 default (about 6), 0 no compression, 1 fast less compression, 9 high compression slow

  queueTopGrab = Queue()
  queueBotGrab = Queue()
  queueScr = Queue()
  queuePacks = Queue()

  pTopGrab = Process(target=grabber, args=(queueTopGrab, TOP_GRAB,))
  pBotGrab = Process(target=grabber, args=(queueBotGrab, BOT_GRAB,))
  pCombine = Process(target=combiner, args=(queueScr, queueTopGrab, queueBotGrab,))
  pPack = Process(target=packer, args=(queuePacks, queueScr, SRV_RES, JPEG_COMPRESSION, ZLIB_LEVEL,))
  pServer = Process(target=serverHandler, args=(queuePacks, UDPServerSocket,))

  print('Starting processes...')
  pTopGrab.start()
  pBotGrab.start()
  pCombine.start()
  pPack.start()
  pServer.start()
  print('Processes started!')

  print('Press Q to terminate.')
  wait('q')

  print('Terminating processes...')
  pTopGrab.terminate()
  pBotGrab.terminate()
  pCombine.terminate()
  pPack.terminate()
  pServer.terminate()
  UDPServerSocket.close()
  print('Processes terminated!')
