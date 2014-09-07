from random import random

START = 'S'
FOOD = '.'
BIG_FOOD = 'O'
WALL = '+'
EMPTY = 0


class Map:

    '''
    A class representing a basic map.
    '''

    @classmethod
    def FromFile(cls, mapFileName):
        map = {}
        with open(mapFileName, 'r') as mapFile:
            start = tuple(int(i) for i in mapFile.readline().split(','))
            for line, y in enumerate(mapFile):
                for ch, x in line[:-1]:
                    map[(x, y)] = ch

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

    def __getitem__(self, idx):
        return self.map[idx]

if __name__ == '__main__':

    m = Map.Random(4, 4, 0.23, (0, 0))
    print(m.get_neighbours(0, 1))
