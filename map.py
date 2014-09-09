from random import random

START = 4
FOOD = 3
BIG_FOOD = 2
WALL = 1
EMPTY = 0


class Map:

    '''
    A class representing a basic map.
    '''

    @classmethod
    def FromFile(cls, mapFileName):
        map = {}
        start = (0, 0)
        with open(mapFileName, 'r') as mapFile:
            for y, line in enumerate(mapFile):
                for x, ch in enumerate(line[:-1]):
                    if int(ch) == START:
                        ch = EMPTY
                        start = (x, y)
                    map[(x, y)] = int(ch)

        return cls(map, start)

    @classmethod
    def Random(cls, width, height, ratio, start=(0, 0)):
        ''' Generate a map randomly if given width and height.
            Higher ratio = more walls. '''

        map = {}
        for y in range(height):
            for x in range(width):
                if random() < ratio:
                    map[(x, y)] = WALL
                else:
                    map[(x, y)] = EMPTY

        map[(start[0], start[1])] = EMPTY

        return cls(map, start)

    def __init__(self, map, start, end=None):
        '''
        Initialize a map using a 2 dimensional list
        where '+' marks an obstacle, a start location and an end location.
        Assumes all inner lists are the same size.
        '''

        self.map = map
        self.rows = abs(max(loc[0] for loc in map) - min(loc[0] for loc in map)) + 1
        self.cols = abs(max(loc[1] for loc in map) - min(loc[1] for loc in map)) + 1
        self.start = start

    def is_valid_tile(self, row, col):
        '''
        return True if map[row][col] is inside the map
        and is not a wall.
        '''
        print(self.rows, self.cols)
        if row >= self.rows or row < 0:
            return False
        if col >= self.cols or col < 0:
            return False
        if self[(row, col)] == WALL:
            return False
        return True

    def get_neighbours(self, *loc):
        ''' Returns all neighbours of loc that aren't walls.'''
        row, col = loc
        neighbours = []
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dir in dirs:
            neighbour = (row + dir[0], col + dir[1])
            if self.is_valid_tile(*neighbour):
                neighbours.append(neighbour)

        return neighbours

    def get(self, key, default=None):
        return self.map.get(key, default)

    def __getitem__(self, key):
        return self.map[key]

    def pprint(self):
        for y in range(self.rows):
            for x in range(self.cols):
                ch = self.get((x, y), ' ')
                print(ch, end='')
            print()

if __name__ == '__main__':

    m = Map.Random(4, 4, 0.23, (0, 0))
    print(m.get_neighbours(0, 1))
