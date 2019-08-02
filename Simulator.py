# Main class of the Simulation
class Simulator:
    def __init__(self, n):
        self.cells = [[Cell() for i in range(n)] for j in range(n)]
        self.size = n
        self.day = 1
        self.complete = False  # Become True after the 91th day is complete

    # Simulate the action of 1 day
    def simulateDay(self):
        for row in self.cells:
            for cell in row:
                cell.grow()
        self.day += 1
        if self.day == 92:
            self.complete = True
        return 0

    # Plants corn in the desired location (x,y)
    def plantCorn(self, x, y):
        return self.plant(x, y, 1)

    # Plants beans in the desired location (x,y)
    def plantBean(self, x, y):
        return self.plant(x, y, 2)

    # Plants the specified crop in the desired location (x,y)
    # Returns -1 if the action is not possible
    def plant(self, x, y, crop):
        if self.cells[x][y].crop == 0:
            self.cells[x][y].crop = crop
            return 0
        else:
            return -1

    # Harvest the desired location (x,y)
    # Returns -1 if the action is not possible
    def harvest(self, x, y):
        if self.cells[x][y].age == 90:
            if self.cells[x][y].crop == 1:
                food = 10 + self.countNeighbours(x, y, 2)
            else:
                if self.countNeighbours(x, y, 1) > 0:
                    food = 15
                else:
                    food = 10
            self.cells[x][y].reset()
            return food
        else:
            return -1

    # Count the number of neighbour cells of (x,y) containing the crop specified
    def countNeighbours(self, x, y, crop):
        counter = 0
        if x > 0 and y > 0 and self.cells[x - 1][y - 1].crop == crop:
            counter += 1
        if x > 0 and self.cells[x - 1][y].crop == crop:
            counter += 1
        if x > 0 and y < self.size - 1 and self.cells[x - 1][y + 1].crop == crop:
            counter += 1
        if y > 0 and self.cells[x][y - 1].crop == crop:
            counter += 1
        if y < self.size - 1 and self.cells[x][y + 1].crop == crop:
            counter += 1
        if x < self.size - 1 and y > 0 and self.cells[x + 1][y - 1].crop == crop:
            counter += 1
        if x < self.size - 1 and self.cells[x + 1][y].crop == crop:
            counter += 1
        if x < self.size - 1 and y < self.size - 1 and self.cells[x + 1][y + 1].crop == crop:
            counter += 1
        return counter


# Class containing the crop information of one cell
class Cell:
    def __init__(self):
        self.crop = 0  # 0 empty, 1 Corn, 2 Bean
        self.age = 0  # number of days completed after the plantation of the crop

    def grow(self):
        if self.crop != 0 and self.age < 90:
            self.age += 1

    def reset(self):
        self.crop = 0
        self.age = 0
