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
            return type(self._entity) == type(other._entity)
        return type(self._entity) == other  # 인스턴스의 클래스 vs 클래스


# === Private 영역 (유저 접근 불가) ===
_direction = {"North": (0, 1), "South": (0, -1), "East": (1, 0), "West": (-1, 0)}
_position = (0, 0)
_size = 16
_array = [[Entities.Crop() for _ in range(_size)] for _ in range(_size)]
_inventory = {Entities.Crop: 0}
_tick = 0

# === 밸런스 변수 ===
_tick_speed = 1      # 틱 증가량 (레벨업 시 증가 가능)
_grow_speed = 1      # 작물 성장 속도 (레벨업 시 증가 가능)


def _advance_time():
    """틱 증가 및 작물 성장 처리"""
    global _tick
    _tick += _tick_speed
    for y in range(_size):
        for x in range(_size):
            crop = _array[y][x]
            if hasattr(crop, 'grow'):
                crop.grow(_grow_speed)


# === 게임 API 함수 ===
def move(dir):
    _advance_time()
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
    _advance_time()
    global _position, _array
    _array[_position[1]][_position[0]] = entity()  # 인스턴스 생성

def harvest():
    _advance_time()
    global _position, _array, _inventory
    entity = _array[_position[1]][_position[0]]
    if can_harvest():
        entity_type = type(entity)

        if entity_type == Entities.Cactus:
            # 선인장: 정렬 체크 후 재귀 수확
            count = _harvest_cactus_recursive(_position, set())
            reward = entity.harvest(neighbors_sorted=True, count=count)
        else:
            # 일반 작물
            reward = entity.harvest()
            _array[_position[1]][_position[0]] = Entities.Grass()

        if entity_type not in _inventory:
            _inventory[entity_type] = 0
        _inventory[entity_type] += reward


def _is_cactus_sorted(pos):
    """해당 위치의 선인장이 정렬 조건을 만족하는지 체크"""
    x, y = pos
    crop = _array[y][x]

    if type(crop) != Entities.Cactus or not crop.is_grown():
        return False

    current_measure = crop.get_measure()

    # 북쪽, 동쪽: 같거나 커야 함
    for dir_name in ['North', 'East']:
        nx = (x + _direction[dir_name][0]) % _size
        ny = (y + _direction[dir_name][1]) % _size
        neighbor = _array[ny][nx]
        if type(neighbor) == Entities.Cactus and neighbor.is_grown():
            if neighbor.get_measure() < current_measure:
                return False

    # 남쪽, 서쪽: 같거나 작아야 함
    for dir_name in ['South', 'West']:
        nx = (x + _direction[dir_name][0]) % _size
        ny = (y + _direction[dir_name][1]) % _size
        neighbor = _array[ny][nx]
        if type(neighbor) == Entities.Cactus and neighbor.is_grown():
            if neighbor.get_measure() > current_measure:
                return False

    return True


def _harvest_cactus_recursive(pos, visited):
    """정렬된 선인장을 재귀적으로 수확하고 개수 반환"""
    x, y = pos

    if pos in visited:
        return 0

    if not _is_cactus_sorted(pos):
        return 0

    visited.add(pos)
    count = 1
    _array[y][x] = Entities.Grass()

    # 이웃 선인장도 재귀 수확
    for dir_name in ['North', 'South', 'East', 'West']:
        nx = (x + _direction[dir_name][0]) % _size
        ny = (y + _direction[dir_name][1]) % _size
        count += _harvest_cactus_recursive((nx, ny), visited)

    return count


def can_harvest():
    global _position, _array
    crop = _array[_position[1]][_position[0]]
    return hasattr(crop, 'is_grown') and crop.is_grown()

def swap(dir):
    _advance_time()
    global _position, _array
    target = ((_direction[dir][0] + _position[0]) % _size, (_direction[dir][1] + _position[1]) % _size)

    current = _array[_position[1]][_position[0]]
    target_entity = _array[target[1]][target[0]]

    # 둘 다 같은 Entity일 때만 swap
    if  current != Entities.Cactus or current != target_entity :
        return

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
        'harvest': harvest,
        'can_harvest': can_harvest,
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
