def receiver(queueChunk ,addrPortServer):
  from time import sleep, time
  from socket import socket, AF_INET, SOCK_DGRAM
  UDPClientSocket = socket(family=AF_INET, type=SOCK_DGRAM)
  UDPClientSocket.settimeout(1)
  payloadSize = 508
  sendCounter = 0
  print('Starting receiver...')
  while 1:
    # SEND ACK
    if time() - sendCounter > 3:
      print('Acked!')
      sendCounter = time()
      UDPClientSocket.sendto(b'\x06', addrPortServer)

    # RECEIVING DATA FROM SERVER
    try: # GETTING FRAME
      bytesReceived = b''
      latency = time()
      while 1:
        bytesFromServer = UDPClientSocket.recvfrom(payloadSize)[0]
        bytesReceived += bytesFromServer
        if bytesFromServer == b'\x16': # IF SYN
          bytesReceived = b''
          continue
        elif len(bytesFromServer) != payloadSize:
          print(len(bytesReceived))
          queueChunk.put(bytesReceived)
          break
      latency = time() - latency
    except Exception as e:
      latency = None
      # print(e)

def displayer(queueChunk):
  from zlib import decompress
  from numpy import frombuffer, uint8
  from cv2 import imdecode, resize, imshow, destroyAllWindows, imread
  from PIL import Image
  from time import sleep
  currentFrame = imread('./waiting-server.jpg')
  print('Starting displayer...')
  while 1:
    try:
      currentFrame = resize(imdecode(frombuffer(decompress(queueChunk.get()),dtype=uint8),1), (640, 480))
      break
    except Exception as e:
      sleep(0.001)
  Image.fromarray(currentFrame).show()
  destroyAllWindows()

if __name__ == '__main__':
  from multiprocessing import Process, Queue, Value
  from keyboard import wait

  TOP_ADDR_PORT = ('127.0.0.1', 20001)
  DOWN_ADDR_PORT = ('127.0.0.1', 20002)

  queueTop = Queue()
  queueDown = Queue()

  pTopReceive = Process(target=receiver, args=(queueTop, TOP_ADDR_PORT,))
  pDisplay = Process(target=displayer, args=(queueTop,))
  pTopReceive.start()
  pDisplay.start()
  wait('q')
  print('Terminating processes...')
  pTopReceive.terminate()
  pDisplay.terminate()
  print('All processes terminated!')