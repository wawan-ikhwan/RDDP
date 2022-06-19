def grabber(queue, grabArea):
  from mss import mss
  with mss() as sct:
    while 1:
      queue.put(sct.grab(grabArea))
  print('Grabber Finished!')

def imageProcessor(queueChunk, queueProcessedImage):
  from numpy import asarray, concatenate
  from cv2 import cvtColor, COLOR_BGRA2BGR
  top = queueChunk[0]
  down = queueChunk[1]
  topFrame = top.get()
  downFrame = down.get()
  while 1:
    if not top.empty(): topFrame = cvtColor(asarray(top.get_nowait()), COLOR_BGRA2BGR)
    if not down.empty(): downFrame = cvtColor(asarray(down.get_nowait()), COLOR_BGRA2BGR)
    queueProcessedImage.put(concatenate((topFrame, downFrame), axis=0))
  print('Image Processor Finished!')

def displayer(isRunning, queueProcessedImage, cltScrSize):
  import pygame
  import pygame.display
  import pygame.image
  import pygame.time
  import pygame.font
  import pygame.event
  from pygame.locals import DOUBLEBUF
  from cv2 import imdecode, resize
  from numpy import frombuffer, uint8
  pygame.init()
  SCR = pygame.display.set_mode(cltScrSize, DOUBLEBUF)
  SCR.set_alpha(None)
  clock = pygame.time.Clock()
  FONT_COMIC = pygame.font.SysFont('Cambria Math', 20)
  while isRunning.value:
    clock.tick(60)
    for EVENT in pygame.event.get():
      if EVENT.type == pygame.QUIT:
        print('Quit Game')
        isRunning.value = 0

    SCR.blit(pygame.image.frombuffer(resize(queueProcessedImage.get(), cltScrSize).tobytes(),cltScrSize,'BGR'),(0,0))  
    SCR.blit(FONT_COMIC.render(f'QUEUE: {str(queueProcessedImage.qsize())[:5]}', False, (0,255,0)),(10,30))
    SCR.blit(FONT_COMIC.render(f'FPS: {str(clock.get_fps())[:5]}', False, (0,255,0)),(10,10))

    pygame.display.update()
  print('Displayer Finished!')

# def displayer(queueTop, queueDown, isRunning):
#   from mss import mss
#   from numpy import asarray, concatenate
#   from cv2 import resize, cvtColor, COLOR_BGRA2BGR, imshow, waitKey, putText, FONT_HERSHEY_SIMPLEX, LINE_AA
#   from time import time
#   fps = 2
#   topFrame = None
#   downFrame = None
#   while 1:
#     t0 = time()
#     if not queueTop.empty(): topFrame = queueTop.get()
#     if not queueDown.empty(): downFrame = queueDown.get()
#     currentFrame = concatenate((topFrame, downFrame), axis=0) if topFrame is not None and downFrame is not None else None
#     if currentFrame is not None:
#       currentFrame = putText(currentFrame, str(fps), (10, 50), FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 2, LINE_AA)
#       currentFrame = putText(currentFrame, str(queueTop.qsize()), (10, 100), FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 2, LINE_AA)
#       imshow('test', currentFrame)
#     if waitKey(1) == ord('q'):
#       isRunning.value = 0
#       print('Displayer Finished!')
#       break
#     deltaT = time() - t0
#     if deltaT != 0:
#       fps = 1 / (deltaT)


if __name__ == "__main__":
  from multiprocessing import Process, Queue, Value
  from time import sleep
  from pyautogui import size as screenSize

  CLT_SCR_SIZE = (640, 480) # EDITABLE
  CLT_SCR_HEIGHT_HALF = CLT_SCR_SIZE[1] // 2
  CLT_SCR_SIZE_HALF = (CLT_SCR_SIZE[0], CLT_SCR_HEIGHT_HALF)

  MON_SIZE = screenSize() # (ORIGINAL SERVER MONITOR RESOLUTION)
  MON_HEIGHT_HALF = MON_SIZE[1] // 2
  MON_SIZE_HALF = (MON_SIZE[0], MON_HEIGHT_HALF)

  SRV_RES = MON_SIZE
  # SRV_RES = (256, 144)

  TOP_GRAB = {'left':0, 'top': 0, 'width': MON_SIZE_HALF[0], 'height':MON_SIZE_HALF[1]}
  DOWN_GRAB = {'left':0, 'top': MON_SIZE_HALF[1], 'width': MON_SIZE_HALF[0], 'height':MON_SIZE_HALF[1]}

  JPEG_COMPRESSION = 80 # 0 HIGH COMPRESSION, 100 NO COMPRESSION

  queueChunk = (Queue(maxsize=3), Queue(maxsize=3))
  queueProcessedImage = Queue(maxsize=1)

  isGameRunning = Value('i', 1)
  p1 = Process(target=grabber, args=(queueChunk[0], TOP_GRAB, ))
  p2 = Process(target=grabber, args=(queueChunk[1], DOWN_GRAB, ))
  p3 = Process(target=imageProcessor, args=(queueChunk, queueProcessedImage, ))
  p4 = Process(target=displayer, args=(isGameRunning, queueProcessedImage, CLT_SCR_SIZE, ))
  p1.start()
  p2.start()
  p3.start()
  p4.start()
  while isGameRunning.value:
    sleep(5)
  p1.terminate()
  p2.terminate()
  p3.terminate()
  p4.terminate()
  print('All processes terminated!')
  