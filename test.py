from mss import mss
from PIL import Image
from numpy import asarray, concatenate, zeros, zeros_like

MON_SIZE = (1366, 768)
HALF_SIZE = (1366, 384)
TOP_GRAB = {'left':0, 'top': 0, 'width': HALF_SIZE[0], 'height':HALF_SIZE[1]}
DOWN_GRAB = {'left':0, 'top': HALF_SIZE[1], 'width': HALF_SIZE[0], 'height':HALF_SIZE[1]}

with mss() as sct:
    topped = asarray(sct.grab(TOP_GRAB))
    downed = asarray(sct.grab(DOWN_GRAB))
    joined = concatenate((topped, zeros_like(downed)), axis=0)
    im = Image.fromarray(joined)
    im.show()