import random
from Entities import Entities

# === 파일 초기화 ===
open('output.txt', 'w').close()

def print(*args):
    with open('output.txt', 'a') as f:
        f.write(' '.join(str(a) for a in args) + '\n')


# === 래퍼 클래스 ===
class EntityRef:
    """비교만 가능한 래퍼"""
    def __init__(self, entity):
        self._entity = entity

    def __eq__(self, other):
        if isinstance(other, EntityRef):
            return self._entity == other._entity
        return self._entity == other


# === Private 영역 (유저 접근 불가) ===
_direction = {"North": (0, 1), "South": (0, -1), "East": (1, 0), "West": (-1, 0)}
_position = (0, 0)
_size = 16
_array = [[Entities.Crop() for _ in range(_size)] for _ in range(_size)]



# === 게임 API 함수 ===
def move(dir):
    global _position
    x = _position[0] + _direction[dir][0]
    y = _position[1] + _direction[dir][1]
    if x < 0:
        x+=_size
    if y < 0:
        y+=_size
    x %= _size
    y %= _size
    _position = (x, y)


def get_pos_x():
    return _position[0]

def get_pos_y():
    return _position[1]

def get_entity():
    global _position, _array
    crop = _array[_position[1]][_position[0]]
    return EntityRef(crop)

def plant(entity: Entities.Crop):
    global _position, _array
    _array[_position[1]][_position[0]] = entity

def swap(dir):
    global _position, _array
    dir_pos = _direction[dir]
    target = ((dir_pos[0] + _position[0]) % _size, (dir_pos[1] + _position[1]) % _size)
    _array[_position[1]][_position[0]], _array[target[1]][target[0]] = \
        _array[target[1]][target[0]], _array[_position[1]][_position[0]]


def measure(dir=None):
    global _position, _array
    if dir:
        dir_pos = ((_direction[dir][0] + _position[0]) % _size, (_direction[dir][1] + _position[1]) % _size)
    else:
        dir_pos = _position
    return _array[dir_pos[1]][dir_pos[0]].get_measure()

def print_map():
    for row in _array:
        print(''.join(str(x) for x in row))


# === 유저 코드 실행 ===
def run_user_code(code):
    """유저 코드를 제한된 환경에서 실행"""
    allowed = {
        # 방향 상수
        'North': 'North',
        'South': 'South',
        'East': 'East',
        'West': 'West',
        # API 함수
        'move': move,
        'swap': swap,
        'measure': measure,
        'get_pos_x': get_pos_x,
        'get_pos_y': get_pos_y,
        'get_entity': get_entity,
        'plant': plant,
        'print_map': print_map,
        'Entities': Entities,
        # 기본 내장 함수
        'print': print,
        'range': range,
        'len': len,
    }
    exec(code, allowed)


# 파일에서 유저 코드 실행
def run_file(filename):
    with open(filename, 'r') as f:
        code = f.read()
    run_user_code(code)
