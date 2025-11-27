import random

class Entities:
    class Crop:
        grow_time = 1
        value = 1
        water = 1
        id = random.randint(1, 100000)

        def get_measure(self):
            return None  # 기본값

    class Carrot(Crop):
        grow_time = 3
        value = 1

    class Pumpkin(Crop):
        grow_time = 2
        value = 1
        size = 1

        def get_measure(self):
            return self.id

    class Cactus(Crop):
        grow_time = 5
        measure = random.randint(1, 10)
        value = 1

        def get_measure(self):
            return self.measure

    class Tree(Crop):
        grow_time = 10
        value = 1

    class Flower(Crop):
        grow_time = 1
        measure = random.randint(1, 10)
        value = 1

        def get_measure(self):
            return self.measure
