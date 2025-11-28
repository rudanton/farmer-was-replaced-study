# "농부는 대체되었다" 리버스 엔지니어링 4탄: 나무 체커보드 패턴

## 개요

3탄에서 해바라기의 최댓값 추적 시스템을 구현했다. 4탄에서는 나무(Tree)의 **인접 페널티 시스템**과 최적 배치인 체커보드 패턴을 분석한다.

---

## 1. 나무 시스템 분석

### 규칙

- 나무는 **공간을 좋아한다**
- 인접한 나무(북/남/동/서) 1개당 성장 시간 **2배 증가**
- 4방향 모두 나무가 있으면 **16배(2⁴)** 느림
- 수확 시 **목재 5개** 획득

### 성장 시간 계산

```
기본 성장 시간 × 2^(인접한 나무 수)
```

| 인접 나무 수 | 배수 | 예시 (기본 10틱) |
|-------------|------|-----------------|
| 0 | 1배 | 10틱 |
| 1 | 2배 | 20틱 |
| 2 | 4배 | 40틱 |
| 3 | 8배 | 80틱 |
| 4 | 16배 | 160틱 |

---

## 2. 최적 배치: 체커보드 패턴

### 왜 체커보드인가?

체스판처럼 배치하면 **어떤 나무도 인접하지 않는다**:

```
[T][ ][T][ ][T][ ][T][ ]
[ ][T][ ][T][ ][T][ ][T]
[T][ ][T][ ][T][ ][T][ ]
[ ][T][ ][T][ ][T][ ][T]
```

- T: 나무
- 빈칸: 다른 작물 또는 빈 땅

### 장점

1. **모든 나무가 최고 속도로 성장** (인접 0개)
2. **맵의 50%를 나무로 활용** 가능
3. **나머지 50%에 다른 작물** 심기 가능

---

## 3. 패턴 판별 알고리즘

### 체커보드 좌표 규칙

```
(x + y) % 2 == 0  → 흰 칸 (나무)
(x + y) % 2 == 1  → 검은 칸 (빈 칸)
```

또는 반대:

```
(x + y) % 2 == 1  → 나무
(x + y) % 2 == 0  → 빈 칸
```

### 시각화

```
좌표:
(0,0)(1,0)(2,0)(3,0)
(0,1)(1,1)(2,1)(3,1)
(0,2)(1,2)(2,2)(3,2)

x+y 값:
  0    1    2    3
  1    2    3    4
  2    3    4    5

%2 결과:
  0    1    0    1
  1    0    1    0
  0    1    0    1

→ 0인 곳에 나무 심으면 체커보드!
```

---

## 4. 실제 구현

### 나무 클래스 (Entities.py)

```python
class Tree(Crop):
    grow_time = 10
    value = 5  # 목재 5개

    def harvest(self):
        return self.value
```

### 인접 나무 체크 함수

```python
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
```

### 성장 시간 계산

```python
def _get_tree_grow_time(pos):
    """나무의 실제 성장 시간 계산"""
    base_time = Entities.Tree.grow_time
    adjacent = _count_adjacent_trees(pos)
    return base_time * (2 ** adjacent)
```

### 나무 성장 로직 (수정된 grow)

```python
class Tree(Crop):
    grow_time = 10
    value = 5

    def __init__(self):
        super().__init__()
        self._effective_grow_time = self.grow_time  # 실제 성장 시간

    def set_effective_grow_time(self, adjacent_count):
        """인접 나무 수에 따른 성장 시간 설정"""
        self._effective_grow_time = self.grow_time * (2 ** adjacent_count)

    def is_grown(self):
        return self._age >= self._effective_grow_time
```

### 심을 때 인접 체크

```python
def plant(entity):
    new_crop = entity()
    _array[_position[1]][_position[0]] = new_crop

    # 나무면 인접 수에 따라 성장 시간 설정
    if type(new_crop) == Entities.Tree:
        adjacent = _count_adjacent_trees(_position)
        new_crop.set_effective_grow_time(adjacent)

        # 인접한 나무들의 성장 시간도 재계산
        _update_adjacent_trees(_position)
```

### 인접 나무 업데이트

```python
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
```

---

## 5. 체커보드 심기 자동화

유저 스크립트에서 체커보드로 나무 심기:

```python
# 전체 맵에 체커보드 패턴으로 나무 심기
for i in range(size * size):
    x = get_pos_x()
    y = get_pos_y()

    if (x + y) % 2 == 0:
        plant(Entities.Tree)
    else:
        plant(Entities.Carrot)  # 다른 작물

    move(East)
    if get_pos_x() == 0:  # 다음 줄
        move(North)
```

---

## 6. 주의사항: 동적 업데이트

### 문제

나무를 심으면 **인접한 기존 나무의 성장 시간도 변해야 한다**.

```
Before:          After planting at (1,1):
[ ][T][ ]        [ ][T][ ]
[ ][ ][ ]   →    [ ][T][ ]    ← (1,1)에 나무 심음
[ ][T][ ]        [ ][T][ ]

(1,0)의 나무: 인접 0→1개로 변경 → 성장 시간 2배로!
(1,2)의 나무: 인접 0→1개로 변경 → 성장 시간 2배로!
```

### 해결

심을 때와 수확할 때 모두 인접 나무들의 성장 시간을 재계산해야 한다.

---

## 7. 효율성 분석

### 체커보드 vs 빽빽하게

| 배치 | 나무 수 (8x8) | 성장 시간 | 총 시간 |
|------|--------------|----------|--------|
| 체커보드 | 32개 | 10틱 | 10틱 |
| 빽빽하게 | 64개 | 160틱 (16배) | 160틱 |

체커보드가 **수확 사이클이 16배 빠르다!**

### 목재 수익 비교 (160틱 동안)

| 배치 | 수확 횟수 | 나무당 목재 | 총 목재 |
|------|----------|-----------|--------|
| 체커보드 | 16회 | 5개 × 32 | **2,560개** |
| 빽빽하게 | 1회 | 5개 × 64 | 320개 |

**체커보드가 8배 효율적!**

---

## 8. 배운 점

| 주제 | 배운 내용 |
|------|----------|
| 체커보드 패턴 | `(x + y) % 2`로 간단히 판별 |
| 지수적 증가 | 2^n의 위력 - 작은 차이가 큰 결과 |
| 동적 업데이트 | 인접 요소 변경 시 연쇄 업데이트 필요 |
| 최적화 | 때로는 적게 심는 게 더 효율적 |

---

> GitHub: [rudanton/farmer-was-replaced-study](https://github.com/rudanton/farmer-was-replaced-study)
