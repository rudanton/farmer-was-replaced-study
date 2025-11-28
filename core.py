import random
from Entities import Entities

# === 파일 초기화 ===
open('output.txt', 'w').close()

def print(*args):
    with open('output.txt', 'a') as f:
        f.write(' '.join(str(a) for a in args) + '\n')


# === 세그먼트 트리 (해바라기 최댓값 추적) ===
class SunflowerTree:
    """해바라기 꽃잎 수의 최댓값을 O(log n)에 추적하는 세그먼트 트리"""

    def __init__(self, size):
        self.n = size
        self.tree = [0] * (4 * size)  # 충분한 크기 확보

    def _update(self, node, start, end, idx, value):
        """내부 재귀 업데이트"""
        if start == end:
            self.tree[node] = value
            return

        mid = (start + end) // 2
        if idx <= mid:
            self._update(2 * node, start, mid, idx, value)
        else:
            self._update(2 * node + 1, mid + 1, end, idx, value)

        # 부모는 자식 중 큰 값
        self.tree[node] = max(self.tree[2 * node], self.tree[2 * node + 1])

    def update(self, idx, value):
        """인덱스 idx의 값을 value로 업데이트 - O(log n)"""
        self._update(1, 0, self.n - 1, idx, value)

    def get_max(self):
        """전체 최댓값 조회 - O(1)"""
        return self.tree[1]

    def to_index(self, x, y, width):
        """2D 좌표를 1D 인덱스로 변환"""
        return y * width + x


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
_array = [[Entities.Grass() for _ in range(_size)] for _ in range(_size)]
_inventory = {}
_tick = 0
_sunflower_count = 0
_sunflower_tree = SunflowerTree(_size * _size)  # 세그먼트 트리 인스턴스

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
    global _position, _array, _sunflower_count, _sunflower_tree

    new_crop = entity()  # 인스턴스 생성
    _array[_position[1]][_position[0]] = new_crop

    # 해바라기면 세그먼트 트리에 추가
    if type(new_crop) == Entities.Sunflower:
        _sunflower_count += 1
        idx = _sunflower_tree.to_index(_position[0], _position[1], _size)
        _sunflower_tree.update(idx, new_crop.petals)

    # 나무면 인접 수에 따라 성장 시간 설정
    elif type(new_crop) == Entities.Tree:
        adjacent = _count_adjacent_trees(_position)
        new_crop.set_effective_grow_time(adjacent)
        # 인접한 나무들의 성장 시간도 재계산
        _update_adjacent_trees(_position)

def harvest():
    _advance_time()
    global _position, _array, _inventory, _sunflower_count, _sunflower_tree

    entity = _array[_position[1]][_position[0]]
    if can_harvest():
        entity_type = type(entity)

        if entity_type == Entities.Cactus:
            # 선인장: 정렬 체크 후 재귀 수확
            count = _harvest_cactus_recursive(_position, set())
            reward = entity.harvest(neighbors_sorted=True, count=count)

        elif entity_type == Entities.Sunflower:
            # 해바라기: 최댓값이면 5배 보상 (10개 이상일 때)
            current_petals = entity.petals
            max_petals = _sunflower_tree.get_max()
            is_max = (_sunflower_count >= 10) and (current_petals == max_petals)

            reward = entity.harvest(is_max=is_max)

            # 세그먼트 트리에서 제거
            idx = _sunflower_tree.to_index(_position[0], _position[1], _size)
            _sunflower_tree.update(idx, 0)
            _sunflower_count -= 1
            _array[_position[1]][_position[0]] = Entities.Grass()

        elif entity_type == Entities.Tree:
            # 나무: 수확 후 인접 나무들의 성장 시간 재계산
            reward = entity.harvest()
            _array[_position[1]][_position[0]] = Entities.Grass()
            # 나무가 제거되었으므로 인접 나무들의 성장 시간 감소
            _update_adjacent_trees(_position)

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


# === 나무 인접 체크 함수 ===
def _count_adjacent_trees(pos):
    """인접한 나무 개수 반환 (0~4)"""
    x, y = pos
    count = 0

    for dir_name in ['North', 'South', 'East', 'West']:
        nx = (x + _direction[dir_name][0]) % _size
        ny = (y + _direction[dir_name][1]) % _size
        neighbor = _array[ny][nx]
        if type(neighbor) == Entities.Tree:
            count += 1

    return count


def _update_adjacent_trees(pos):
    """인접한 나무들의 성장 시간 재계산"""
    x, y = pos

    for dir_name in ['North', 'South', 'East', 'West']:
        nx = (x + _direction[dir_name][0]) % _size
        ny = (y + _direction[dir_name][1]) % _size
        neighbor = _array[ny][nx]

        if type(neighbor) == Entities.Tree:
            adjacent = _count_adjacent_trees((nx, ny))
            neighbor.set_effective_grow_time(adjacent)

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
