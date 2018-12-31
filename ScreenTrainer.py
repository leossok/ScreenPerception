import cv2
import numpy as np
import yaml
import os
from collections import defaultdict
import win32gui
import win32con
import win32ui
import win32api
import time
from ScreenViewer import ScreenViewer
from keys import Keys


class putText():
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.fontScale = 0.5
        self.fontColor = (255, 255, 255)
        self.lineType = 1

    def add_text(self, img, s, pos=(10, 500)):
        cv2.putText(img, s,
                    pos,
                    self.font,
                    self.fontScale,
                    self.fontColor,
                    self.lineType)


class displayCV2():
    def __init__(self, nameWindow='image', cfg=defaultdict()):
        self.cfg = cfg
        # ScreenViewer
        self.sv = ScreenViewer()

        # mouse clicked point
        self.ix = 0
        self.iy = 0
        self.cropping = False
        self.draw_rect = []
        for i in ['refPt', 'refCircle', 'refCircleclr']:
            if i not in self.cfg.keys():
                self.cfg[i] = []

        self.refPt = cfg['refPt']
        self.refCircle = cfg['refCircle']
        self.refCircle_clr = cfg['refCircleclr']
        self.T_refPt = []
        self.T_refCircle = []
        self.T_refCircle_clr = []
        self.nameWindow = nameWindow
        self.last_command = ""
        # set texter
        self.txt = putText()
        self.txt_h = putText()
        self.txt_h.fontColor = (255, 255, 0)
        self.txt_h.fontScale = 0.8
        self.txt_draw = putText()
        self.txt_draw.fontColor = (255, 0, 0)
        self.txt_crop = putText()
        self.txt_crop.fontColor = (0, 255, 0)
        self.txt_circle = putText()
        self.txt_circle.fontColor = (0, 0, 255)

        self.k = 0
        cv2.namedWindow(self.nameWindow)
        cv2.setMouseCallback(self.nameWindow, self.mouse)
        self.keys = Keys()
        self.loop = True
        self.info = True
        self.image = None
        self.image_info = None
        self.help = False

        self.height, self.width, self.channels = 0, 0, 0

    def mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONDBLCLK:
            self.ix, self.iy = x, y

        elif event == cv2.EVENT_LBUTTONDOWN:
            self.refPt += [[(x, y), (x, y)]]
            self.cropping = True
        elif event == cv2.EVENT_LBUTTONUP and self.cropping:
            self.refPt[-1][1] = (x, y)
            self.cropping = False
            h, w, ch = self.image[self.refPt[-1][0][1]:self.refPt[-1]
                                  [1][1], self.refPt[-1][0][0]:self.refPt[-1][1][0]].shape
            if h < 1 or w < 1:
                del self.refPt[-1]
        elif event == cv2.EVENT_MBUTTONDOWN:
            self.refCircle += [(x, y)]
            self.refCircle_clr += [tuple(self.image[y][x])]

    def add_rectangle(self, pts):
        self.draw_rect += [pts]

    def reset_rectangle(self):
        self.draw_rect = []

    def Draw_rectangle(self):
        for idx, pt in enumerate(self.draw_rect):
            self.txt_draw.add_text(self.image_info, str(
                idx), pos=(pt[0][0], pt[0][1]-10))
            cv2.rectangle(self.image_info, pt[0], pt[1], (255, 0, 0), 2)

    def crop_rectangle(self):
        for idx, pt in enumerate(self.refPt):
            self.txt_crop.add_text(self.image_info, str(
                idx), pos=(pt[0][0], pt[0][1]-10))
            cv2.rectangle(
                self.image_info, pt[0], pt[1], (0, 255, 0), 1)

    def Draw_circle(self):
        for idx, pt in enumerate(self.refCircle):
            self.txt_circle.add_text(self.image_info, str(
                idx), pos=(pt[0], pt[1]-10))
            cv2.circle(self.image_info, pt, 2, (0, 0, 255), -1)

    def imshow(self):
        self.image = self.image_info = self.sv.i0.copy()
        self.height, self.width, self.channels = self.image_info.shape
        self.show_info()
        self.show_help()
        cv2.imshow(self.nameWindow, self.image_info)
        self.reset_rectangle()

    def show_info(self):
        if self.info:
            self.crop_rectangle()
            self.Draw_rectangle()
            self.Draw_circle()
            self.txt.add_text(
                self.image_info, self.last_command, pos=(10, 40))
            self.txt.add_text(self.image_info, "({}, {})".format(
                self.ix, self.iy), pos=(10, self.height-40))
            self.txt.add_text(self.image_info, "{}".format(
                self.image[self.iy, self.ix]), pos=(10, self.height-20))

    def show_help(self):
        if self.help:
            self.txt_h.add_text(
                self.image_info, "i - infomation", pos=(int(self.width/2), 30))
            self.txt_h.add_text(
                self.image_info, "h - help", pos=(int(self.width/2), 60))
            self.txt_h.add_text(
                self.image_info, "s - save crop", pos=(int(self.width/2), 90))
            self.txt_h.add_text(
                self.image_info, "c - clear crop", pos=(int(self.width/2), 120))
            self.txt_h.add_text(
                self.image_info, "q - quit", pos=(int(self.width/2), 150))
            self.txt_h.add_text(
                self.image_info, "D - dump config.yaml", pos=(int(self.width/2), 180))
            self.txt_h.add_text(
                self.image_info, "u/U - undo rect, circle", pos=(int(self.width/2), 210))
            self.txt_h.add_text(
                self.image_info, "r/R - redo rect, circle", pos=(int(self.width/2), 240))

    def save_image(self):
        for idx, pt in enumerate(self.refPt):
            dir_name = 'data/cat_{}/'.format(idx)

            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            i = len([name for name in os.listdir(dir_name)
                     if os.path.isfile(os.path.join(dir_name, name))])
            cv2.imwrite(
                '{}cat_{}_no_{}.png'.format(dir_name, idx, i), self.image[pt[0][1]:pt[1][1], pt[0][0]:pt[1][0]])

    def keyCommand(self):
        self.k = cv2.waitKey(1)
        if self.k == ord('q'):
            cv2.destroyAllWindows()
            self.loop = False
        elif self.k == ord('i'):
            self.last_command = "info"
            self.info = not self.info
        elif self.k == ord('h'):
            self.last_command = "help"
            self.help = not self.help
        elif self.k == ord('s'):
            self.last_command = "save"
            self.save_image()
        elif self.k == ord('c'):
            self.last_command = "clear"
            self.refPt = []
            self.refCircle = []
            self.refCircle_clr = []
        elif self.k == ord('u'):
            self.last_command = "undo rect"
            try:
                self.T_refPt += [self.refPt[-1]]
                del self.refPt[-1]
            except IndexError:
                print("Warning :: {} index out of range!".format(self.last_command))
        elif self.k == ord('U'):
            self.last_command = "undo circle"
            try:
                self.T_refCircle += [self.refCircle[-1]]
                self.T_refCircle_clr += [self.refCircle_clr[-1]]
                del self.refCircle[-1]
                del self.refCircle_clr[-1]
            except IndexError:
                print("Warning :: {} index out of range!".format(self.last_command))
        elif self.k == ord('r'):
            self.last_command = "redo rect"
            try:
                self.refPt += [self.T_refPt.pop()]
            except IndexError:
                print("Warning :: {} index out of range!".format(self.last_command))
        elif self.k == ord('R'):
            self.last_command = "redo circle"

            try:
                self.refCircle += [self.T_refCircle.pop()]
                self.refCircle_clr += [self.T_refCircle_clr.pop()]
            except IndexError:
                print("Warning :: {} index out of range!".format(self.last_command))

        elif self.k == ord('D'):
            self.last_command = "dump"
            self.cfg['refPt'] = self.refPt
            self.cfg['refCircle'] = self.refCircle
            self.cfg['refCircleclr'] = self.refCircle_clr
            with open('config.yaml', 'w') as outfile:
                yaml.dump(self.cfg, outfile)

        elif self.k == ord('T'):         # wait for ESC key to exit
            self.last_command = "Test"
            print("=====Debug=====")
            lParam = win32api.MAKELONG(self.ix, self.iy)
            b = win32gui.PostMessage(
                self.sv.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            a = win32gui.PostMessage(
                self.sv.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, lParam)
            print(b, a)


def isEqual(a, b):
    """ a,b should be (b,g,r) or image (numpy.array)
    """
    if len(a) == 3 and len(b) == 3:
        if a == b:
            return True
        else:
            return False
    else:
        b = np.array_equal(a, b)
        return b


def crop_img(img, pt):
    """ img : image
        pt : [(x1,y1), (x2,y2)]
    """
    return img[pt[0][1]:pt[1][1], pt[0][0][0]:pt[0][1][0]]
