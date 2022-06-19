import time
import win32gui
import win32ui
import win32con
import win32api
import numpy as np
import cv2


def window_capture():
    hwnd = 0
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()

    MoniterDev = win32api.EnumDisplayMonitors(None, None)
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]

    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    im = saveBitMap.GetBitmapBits(True)  # Tried False also
    img = np.frombuffer(im, dtype=np.uint8).reshape((h, w, 4))

    cv2.imshow("demo", img)
    cv2.waitKey(1)


beg = time.time()
for i in range(100):
    window_capture()
end = time.time()
print(end - beg)

cv2.destroyAllWindows()