def grabber_top(queueTop, isRunning, topGrab, jpegCompression, srvRes):
  from mss import mss
  from cv2 import resize, cvtColor, COLOR_BGRA2BGR, imencode, IMWRITE_JPEG_QUALITY
  from numpy import asarray
  with mss() as sct:
    while isRunning.value:
      queueTop.put(imencode('.jpg', cvtColor(resize(asarray(sct.grab(topGrab)), srvRes), COLOR_BGRA2BGR), (IMWRITE_JPEG_QUALITY, jpegCompression))[1].tobytes())
  print('Top Grabber Finished!')

def grabber_down(queueDown, isRunning, downGrab, jpegCompression, srvRes):
  from mss import mss
  from cv2 import resize, cvtColor, COLOR_BGRA2BGR, imencode, IMWRITE_JPEG_QUALITY
  from numpy import asarray
  with mss() as sct:
    while isRunning.value:
      queueDown.put(imencode('.jpg', cvtColor(resize(asarray(sct.grab(downGrab)),srvRes), COLOR_BGRA2BGR), (IMWRITE_JPEG_QUALITY, jpegCompression))[1].tobytes())
  print('Down Grabber Finished!')

def displayer(queueTop, queueDown, isRunning, cltScrSize, cltScrSizeHalf):
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

    if not queueTop.empty(): SCR.blit(pygame.image.frombuffer(resize(imdecode(frombuffer(queueTop.get_nowait(), uint8), 1), cltScrSizeHalf), cltScrSizeHalf, 'BGR'), (0,0))
    if not queueDown.empty(): SCR.blit(pygame.image.frombuffer(resize(imdecode(frombuffer(queueDown.get_nowait(), uint8), 1), cltScrSizeHalf), cltScrSizeHalf, 'BGR'), (0, cltScrSizeHalf[1]))

    SCR.blit(FONT_COMIC.render(f'QUEUE: {str(queueTop.qsize())[:5]}, {str(queueDown.qsize())[:5]}', False, (0,255,0)),(10,30))
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

  CLT_SCR_SIZE = (1280, 720) # EDITABLE
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

  queueTop = Queue(maxsize=5)
  queueDown = Queue(maxsize=5)

  isGameRunning = Value('i', 1)
  p1 = Process(target=grabber_top, args=(queueTop,isGameRunning, TOP_GRAB, JPEG_COMPRESSION, SRV_RES))
  p2 = Process(target=grabber_down, args=(queueDown,isGameRunning, DOWN_GRAB, JPEG_COMPRESSION, SRV_RES))
  p3 = Process(target=displayer, args=(queueTop, queueDown,isGameRunning, CLT_SCR_SIZE, CLT_SCR_SIZE_HALF))
  p1.start()
  p2.start()
  p3.start()
  while isGameRunning.value:
    sleep(5)
  p1.terminate()
  p2.terminate()
  p3.terminate()
  print('All processes terminated!')
  