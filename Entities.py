import random

class Entities:
    class Crop:
        grow_time = 1
        value = 1
        water = 1
        id = random.randint(1, 100000)

        def __init__(self):
            self._age = 0

        def grow(self, amount=1):
            self._age += amount

        def is_grown(self):
            return self._age >= self.grow_time

        def get_measure(self):
            return None  # 기본값

        def harvest(self):
            return self.value  # 기본 수확

    class Carrot(Crop):
        grow_time = 3
        value = 1

    class Pumpkin(Crop):
        grow_time = 2
        value = 1
        size = 1

        def get_measure(self):
            return self.id

        def harvest(self):
            n = self.size
            return n * n * min(n, 6)

    class Cactus(Crop):
        grow_time = 5
        measure = random.randint(1, 10)
        value = 1

        def get_measure(self):
            return self.measure

        def harvest(self, neighbors_sorted=False, count=1):
            # 정렬되어 있으면 n² 보상
            if neighbors_sorted:
                return count * count
            return self.value

    class Tree(Crop):
        grow_time = 10
        value = 5  # 목재 5개

        def __init__(self):
            super().__init__()
            self._effective_grow_time = self.grow_time

        def set_effective_grow_time(self, adjacent_count):
            """인접 나무 수에 따른 성장 시간 설정"""
            self._effective_grow_time = self.grow_time * (2 ** adjacent_count)

        def is_grown(self):
            return self._age >= self._effective_grow_time

    class Flower(Crop):
        grow_time = 1
        measure = random.randint(1, 10)
        value = 1

        def get_measure(self):
            return self.measure

    class Sunflower(Crop):
        grow_time = 2
        value = 1

        def __init__(self):
            super().__init__()
            self.petals = random.randint(7, 15)  # 꽃잎 수 7~15

        def get_measure(self):
            return self.petals

        def harvest(self, is_max=False):
            if is_max:
                return self.value * 5  # 최댓값이면 5배
            return self.value

    class Grass(Crop):
        """빈 땅 표시용"""
        grow_time = 0
        value = 0

        def is_grown(self):
            return False
