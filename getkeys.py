# Citation: Box Of Hats (https://github.com/Box-Of-Hats )

import random as rd
import win32api as wapi
import win32con
import time
keyList = ["\b"]
LSHIFT = chr(win32con.VK_LSHIFT)
CONTROL = chr(win32con.VK_CONTROL)
for char in LSHIFT+CONTROL+"ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789,.'£$/\\":
    keyList.append(char)


def key_check():
    keys = []
    for key in keyList:
        if wapi.GetAsyncKeyState(ord(key)):
            keys.append(key)
    if keys == []:
        keys = [-1]
    # time.sleep(0.1)
    return keys


if __name__ == "__main__":
    while True:
        k = key_check()
        print(k)
