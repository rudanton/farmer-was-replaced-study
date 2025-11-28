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
        value = 1

    class Flower(Crop):
        grow_time = 1
        measure = random.randint(1, 10)
        value = 1

        def get_measure(self):
            return self.measure
