from core import *

def bubble_sort_hor():
    global W
    for i in range(W):
        for j in range(W):
            if j < W-1 and measure('East') < measure():
                swap('East')
        move('East')

def merge_sort_ver():
    global H
    global position
    index = 0
    while index < H-1:
        index = 0
        while position[1] != H-1:
            y = position[1]
            if y < H-1 and measure('North') > measure():
                swap('North')
            else:
                index += 1
            move('North')
        index = 0
        while position[1] != 0:
            y = position[1]
            if y < H-1 and measure('North') > measure():
                swap('North')
            else:
                index += 1
            move('South')
