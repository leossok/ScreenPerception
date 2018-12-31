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
    dcv = displayCV2(cfg=config_loaded)
    # dcv.sv.GetHWND('Steam')
    dcv.sv.GetHWND_desktop()
    dcv.sv.br = int(dcv.sv.r*0.6)  # border right
    dcv.sv.bb = int(dcv.sv.b*0.5)  # border bottomq
    dcv.sv.Start()
    time.sleep(0.1)

    while dcv.loop:

        dcv.imshow()
        dcv.keyCommand()
    dcv.sv.Stop()
