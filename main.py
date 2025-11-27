from core import *
from sort import *


for i in range(H):
    bubble_sort_hor()
    move('North')

for i in range(W):
    merge_sort_ver()
    move('East')