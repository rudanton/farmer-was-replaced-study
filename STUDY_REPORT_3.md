# "농부는 대체되었다" 리버스 엔지니어링 3탄: 해바라기 최댓값 추적 시스템

## 개요

2탄에서 선인장의 재귀 수확 시스템을 구현했다. 3탄에서는 해바라기(Sunflower)의 **최댓값 추적 시스템**을 구현하면서 어떤 자료구조가 최선인지 분석한다.

---

## 1. 해바라기 시스템 분석

### 규칙

- 해바라기 꽃잎 수: **7~15개** (랜덤)
- 농장에 **10개 이상** 있을 때, **최댓값 수확 → 5배 파워**
- 동일한 최댓값이 여러 개일 수 있음 (어느 것이든 OK)

### 필요한 연산

| 연산 | 설명 | 빈도 |
|------|------|------|
| `plant()` | 해바라기 삽입 | 자주 |
| `harvest()` | 해바라기 삭제 + 최댓값 여부 확인 | 자주 |
| `get_max()` | 현재 최댓값 조회 | 매우 자주 |

핵심: **삽입, 임의 삭제, 최댓값 조회**가 모두 빨라야 한다.

---

## 2. 자료구조 후보

### 2.1 단순 배열/리스트

```python
sunflowers = [8, 12, 15, 9, 15, 7]
max_val = max(sunflowers)  # O(n)
```

| 연산 | 시간 복잡도 |
|------|------------|
| 삽입 | O(1) |
| 삭제 | O(n) |
| 최댓값 조회 | O(n) |

**평가**: 구현은 쉽지만 비효율적. 매번 전체 순회.

---

### 2.2 정렬된 배열

```python
sunflowers = [7, 8, 9, 12, 15, 15]  # 항상 정렬 유지
max_val = sunflowers[-1]  # O(1)
```

| 연산 | 시간 복잡도 |
|------|------------|
| 삽입 | O(n) - 정렬 위치 찾고 shift |
| 삭제 | O(n) - shift 필요 |
| 최댓값 조회 | O(1) |

**평가**: 조회는 빠르지만 삽입/삭제가 느림.

---

### 2.3 힙 (Heap)

**완전 이진 트리** 기반 자료구조. 부모가 항상 자식보다 크거나(Max Heap) 작다(Min Heap). 우선순위 큐 구현에 주로 사용된다.

```python
import heapq
heap = []
heapq.heappush(heap, -15)  # max heap은 음수로
max_val = -heap[0]  # O(1)
```

| 연산 | 시간 복잡도 |
|------|------------|
| 삽입 | O(log n) |
| 최댓값 삭제 | O(log n) |
| **임의 삭제** | **O(n)** ❌ |
| 최댓값 조회 | O(1) |

**평가**: 최댓값만 삭제하면 완벽하지만, **임의 위치 삭제가 O(n)**. 최댓값이 아닌 해바라기 수확 시 문제.

---

### 2.4 세그먼트 트리 (Segment Tree)

**구간 쿼리**에 특화된 이진 트리. 배열을 반씩 나눠가며 각 구간의 대표값(합, 최댓값 등)을 저장한다. 리프 노드는 원본 데이터, 내부 노드는 자식들의 대표값을 가진다.

```
        [15]          ← 전체 최댓값
       /    \
    [12]    [15]
    / \     / \
  [8][12] [15][9]     ← 리프 = 실제 값
```

| 연산 | 시간 복잡도 |
|------|------------|
| 삽입 (업데이트) | O(log n) |
| 삭제 (업데이트) | O(log n) |
| 최댓값 조회 | O(1) |

**평가**: 모든 연산이 빠름! 단, **크기가 고정**되어야 하고 인덱스 기반.

---

### 2.5 레드-블랙 트리 (Red-Black Tree)

**자가 균형 이진 탐색 트리**. 각 노드에 빨강/검정 색상을 부여하고, 색상 규칙을 통해 트리 높이를 O(log n)으로 유지한다. 삽입/삭제 시 회전과 색상 변경으로 균형을 맞춘다. Java의 `TreeMap`, C++의 `std::map`이 이 구조를 사용한다.

```
        [12:B]
       /      \
    [8:R]    [15:B]
    / \       / \
  [7] [9]  [14] [15]
```

| 연산 | 시간 복잡도 |
|------|------------|
| 삽입 | O(log n) |
| 삭제 | O(log n) |
| 최댓값 조회 | O(log n) |

**평가**: 모든 연산이 O(log n). 가장 균형 잡힌 성능. 단, **구현이 매우 복잡**.

---

### 2.6 해시맵 + 최댓값 캐싱

```python
sunflowers = {}  # {position: petal_count}
max_cache = 15   # 최댓값 캐시

def update_max():
    global max_cache
    max_cache = max(sunflowers.values()) if sunflowers else 0
```

| 연산 | 시간 복잡도 |
|------|------------|
| 삽입 | O(1) + 캐시 갱신 |
| 삭제 | O(1) + 캐시 갱신 필요할 수도 |
| 최댓값 조회 | O(1) |
| 캐시 재계산 | O(n) - 최댓값 삭제 시에만 |

**평가**: 대부분 O(1), 최댓값 삭제 시에만 O(n). 현실적으로 최댓값 삭제가 보상이 좋으니 자주 일어남.

---

## 3. 비교 분석

### 시간 복잡도 비교

| 자료구조 | 삽입 | 임의 삭제 | 최댓값 조회 | 구현 난이도 |
|----------|------|----------|------------|------------|
| 단순 배열 | O(1) | O(n) | O(n) | ⭐ |
| 정렬 배열 | O(n) | O(n) | O(1) | ⭐⭐ |
| 힙 | O(log n) | O(n) | O(1) | ⭐⭐ |
| 세그먼트 트리 | O(log n) | O(log n) | O(1) | ⭐⭐⭐ |
| 레드-블랙 트리 | O(log n) | O(log n) | O(log n) | ⭐⭐⭐⭐⭐ |
| 해시맵+캐시 | O(1) | O(1)~O(n) | O(1) | ⭐⭐ |

### 공간 복잡도

| 자료구조 | 공간 | 비고 |
|----------|------|------|
| 단순 배열 | O(n) | |
| 정렬 배열 | O(n) | |
| 힙 | O(n) | |
| 세그먼트 트리 | O(4n) | 트리 구조 오버헤드 |
| 레드-블랙 트리 | O(n) | 노드당 색상/포인터 추가 |
| 해시맵+캐시 | O(n) | |

---

## 4. 게임 상황 분석

### 맵 크기

- 최대 32x32 = **1024칸**
- 해바라기만 심으면 최대 1024개

### 연산 패턴

1. **plant()**: 빈 칸에 심기 → 삽입
2. **harvest()**: 수확 → 삭제 + 최댓값 확인
3. 게임 특성상 **최댓값을 수확하는 게 이득** → 최댓값 삭제가 잦음

### 현실적 고려

- n = 1024는 **작은 크기**
- O(n) vs O(log n) 차이가 크지 않을 수 있음
- 1024번 순회 vs 10번 순회 (log₂1024 = 10)

---

## 5. 결론

### 최선의 선택: 세그먼트 트리

**이유:**

1. **모든 연산이 빠름**: 삽입 O(log n), 삭제 O(log n), 최댓값 조회 O(1)
2. **맵 크기 고정**: 게임 맵은 크기가 정해져 있어서 세그먼트 트리에 적합
3. **인덱스 기반**: 2D 맵의 좌표를 1D 인덱스로 변환하면 바로 적용 가능
4. **구현 난이도 적절**: 레드-블랙 트리보다 훨씬 간단

### 차선책: 힙 + Lazy Deletion

최댓값 삭제가 잦다면:

```python
# 삭제 시 실제로 지우지 않고 마킹
deleted = set()

def get_max():
    while heap and heap[0] in deleted:
        heapq.heappop(heap)
    return -heap[0]
```

- 임의 삭제를 O(1)로 처리 (마킹만)
- 최댓값 조회 시 삭제된 것들 정리

### 탈락 사유

| 자료구조 | 탈락 이유 |
|----------|----------|
| 단순 배열 | 최댓값 조회 O(n) - 매번 전체 순회 |
| 정렬 배열 | 삽입 O(n) - 매번 shift |
| 힙 | 임의 삭제 O(n) - 최댓값 아닌 것 수확 시 |
| 레드-블랙 트리 | 구현 복잡도가 너무 높음, 학습 목적 아니면 비효율 |
| 해시맵+캐시 | 최댓값 삭제 빈번 시 캐시 재계산 O(n) |

---

## 6. 실제 구현

### 세그먼트 트리 클래스

```python
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
```

### 해바라기 심기 (plant)

```python
def plant(entity):
    new_crop = entity()  # 인스턴스 생성
    _array[_position[1]][_position[0]] = new_crop

    # 해바라기면 세그먼트 트리에 추가
    if type(new_crop) == Entities.Sunflower:
        _sunflower_count += 1
        idx = _sunflower_tree.to_index(_position[0], _position[1], _size)
        _sunflower_tree.update(idx, new_crop.petals)
```

### 해바라기 수확 (harvest)

```python
elif entity_type == Entities.Sunflower:
    # 해바라기: 최댓값이면 5배 보상 (10개 이상일 때)
    current_petals = entity.petals
    max_petals = _sunflower_tree.get_max()  # O(1)!
    is_max = (_sunflower_count >= 10) and (current_petals == max_petals)

    reward = entity.harvest(is_max=is_max)

    # 세그먼트 트리에서 제거 - O(log n)
    idx = _sunflower_tree.to_index(_position[0], _position[1], _size)
    _sunflower_tree.update(idx, 0)
    _sunflower_count -= 1
```

### 작동 원리

1. **심을 때**: 세그먼트 트리에 꽃잎 수 삽입 → 부모 노드들 갱신
2. **수확할 때**: 루트(tree[1])와 비교 → 최댓값이면 5배
3. **수확 후**: 해당 인덱스를 0으로 업데이트 → 트리 재정렬

```
plant(Sunflower) 후 트리 상태:
        [15]          ← get_max() = 15
       /    \
    [12]    [15]
    / \     / \
  [8][12] [15][9]

수확 후 (15 제거):
        [12]          ← get_max() = 12 (자동 갱신!)
       /    \
    [12]    [9]
    / \     / \
  [8][12] [0][9]
```

---

## 7. 배운 점

| 주제 | 배운 내용 |
|------|----------|
| 자료구조 선택 | 연산 패턴 분석이 먼저 |
| 트레이드오프 | 시간 vs 공간 vs 구현 복잡도 |
| 실용적 판단 | n이 작으면 복잡한 구조가 오버킬일 수 있음 |
| 세그먼트 트리 | 구간 쿼리의 강력한 도구 |

---

> GitHub: [rudanton/farmer-was-replaced-study](https://github.com/rudanton/farmer-was-replaced-study)
