import time
import cv2
import numpy as np
from ScreenViewer import ScreenViewer
from ScreenTrainer import *
import yaml

if __name__ == "__main__":
    config_loaded = {}
    with open("config.yaml", 'r') as stream:
        config_loaded = yaml.load(stream)
    sv = ScreenViewer()
    sv.GetHWND_desktop()
    sv.br = int(sv.r*0.5)  # border right
    sv.bb = int(sv.b*0.5)  # border bottom
    sv.Start()
    time.sleep(0.1)

    dcv = displayCV2(cfg=config_loaded)
    while dcv.loop:
        dcv.add_rectangle([(50, 50), (300, 300)])
        dcv.imshow(sv.i0)
        dcv.keyCommand()

    sv.Stop()
