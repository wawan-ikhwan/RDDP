import pyautogui as pag
from io import BytesIO
im = pag.screenshot()
temp = BytesIO()
im.save(temp, format="jpeg", optimize=True, quality=10)
