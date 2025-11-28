# "농부는 대체되었다" 리버스 엔지니어링 2탄: 선인장 재귀 수확 시스템

## 개요

1탄에서 게임 API의 샌드박스 구조를 구현했다. 2탄에서는 선인장(Cactus)의 **재귀 수확 시스템**을 구현하면서 마주친 문제들과 해결 과정을 다룬다.

---

## 1. 선인장 수확 시스템

선인장은 게임에서 가장 복잡한 수확 로직을 가진다.

### 핵심 규칙
- **n개 동시 수확 → n² 획득**
- 정렬된 선인장끼리 **재귀적으로 연쇄 수확**
- 정렬 조건: 북/동은 크거나 같음, 남/서는 작거나 같음

### 예시
```
정렬된 3x3 선인장:
[1][2][3]
[2][3][4]
[3][4][5]

→ 한 번에 9개 수확 → 81 보상 (9²)
```

---

## 2. 문제: 상호참조 (Circular Import)

처음에는 `Entities.py`의 `Cactus.harvest()` 안에서 재귀 수확을 구현하려 했다.

```python
# Entities.py
class Cactus(Crop):
    def harvest(self):
        # 이웃 선인장 확인하려면 _array 필요
        # _array는 core.py에 있음
        from core import _array  # 💥 순환 참조!
```

### Python 순환 참조란?

```python
# a.py
from b import B
class A: ...

# b.py
from a import A  # ImportError!
class B: ...
```

`a`가 `b`를 import하고, `b`가 `a`를 import하면 에러가 발생한다.

### 해결 방법들

1. **지연 import** - 함수 안에서 import
   ```python
   def some_func():
       from core import something
   ```

2. **TYPE_CHECKING** - 타입 힌트용으로만
   ```python
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from core import Core
   ```

3. **구조 변경** - 책임 분리

---

## 3. 해결: 책임 분리

**보상 계산**과 **맵 탐색**을 분리했다.

### Entities.py - 보상 계산만
```python
class Cactus(Crop):
    def harvest(self, neighbors_sorted=False, count=1):
        if neighbors_sorted:
            return count * count  # n² 보상
        return self.value
```

### core.py - 맵 탐색 담당
```python
def harvest():
    entity = _array[_position[1]][_position[0]]

    if type(entity) == Entities.Cactus:
        count = _harvest_cactus_recursive(_position, set())
        reward = entity.harvest(neighbors_sorted=True, count=count)
    else:
        reward = entity.harvest()
```

이렇게 하면:
- `Entities`는 `core`를 모름 (의존성 없음)
- `core`만 `Entities`를 import
- 순환 참조 해결!

---

## 4. 재귀 탐색 구현 (2D DFS)

### 정렬 조건 체크

```python
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
```

### 재귀 수확 (DFS)

```python
def _harvest_cactus_recursive(pos, visited):
    """정렬된 선인장을 재귀적으로 수확하고 개수 반환"""
    x, y = pos

    # 이미 방문했거나 정렬 안 됐으면 스킵
    if pos in visited:
        return 0
    if not _is_cactus_sorted(pos):
        return 0

    # 현재 위치 수확
    visited.add(pos)
    count = 1
    _array[y][x] = Entities.Grass()

    # 4방향 이웃 재귀 탐색
    for dir_name in ['North', 'South', 'East', 'West']:
        nx = (x + _direction[dir_name][0]) % _size
        ny = (y + _direction[dir_name][1]) % _size
        count += _harvest_cactus_recursive((nx, ny), visited)

    return count
```

### 핵심 포인트

1. **visited set**: 이미 수확한 위치 재방문 방지
2. **4방향 탐색**: 2D 맵에서 상하좌우 모두 탐색
3. **재귀 종료 조건**: 방문함 or 정렬 안 됨 or 선인장 아님
4. **count 누적**: 수확한 선인장 개수를 반환값으로 전달

---

## 5. 2D DFS vs BFS

이 구현은 **DFS (깊이 우선 탐색)**이다.

```
시작점에서 DFS:
[1] → [2] → [3]
            ↓
      [5] ← [4]
```

BFS로도 구현 가능하지만, 이 경우 DFS가 더 간단하다.

```python
# BFS 버전 (참고용)
from collections import deque

def _harvest_cactus_bfs(start_pos):
    queue = deque([start_pos])
    visited = set()
    count = 0

    while queue:
        pos = queue.popleft()
        if pos in visited or not _is_cactus_sorted(pos):
            continue

        visited.add(pos)
        count += 1
        _array[pos[1]][pos[0]] = Entities.Grass()

        for dir_name in ['North', 'South', 'East', 'West']:
            # 이웃 추가...
            queue.append((nx, ny))

    return count
```

---

## 6. 설계 원칙: 단일 책임

이번 구현에서 적용한 설계 원칙:

| 모듈 | 책임 |
|------|------|
| `Entities.py` | 작물 속성, 보상 계산 |
| `core.py` | 맵 관리, 탐색, 게임 로직 |

**장점:**
- 순환 참조 방지
- 테스트 용이 (보상 계산만 따로 테스트 가능)
- 확장성 (새 작물 추가 시 Entities만 수정)

---

## 7. 배운 점

| 주제 | 배운 내용 |
|------|----------|
| 순환 참조 | Python에서도 발생, 구조 설계로 해결 |
| 책임 분리 | 보상 계산 vs 맵 탐색 역할 분리 |
| 2D DFS | visited set으로 재방문 방지 |
| 재귀 함수 | 종료 조건과 반환값 설계 |

---

## 8. 다음 과제

- [ ] 호박 크기 시스템 구현 (인접한 호박끼리 합체)
- [ ] 나무 목재 수확 시스템
- [ ] 해바라기 최댓값 탐색 시스템

게임을 분석하면 할수록 흥미로운 알고리즘 문제들이 나온다!

---

> GitHub: [rudanton/farmer-was-replaced-study](https://github.com/rudanton/farmer-was-replaced-study)
