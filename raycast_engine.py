from map import Map
import math
import pygame as pg
from time import sleep

from collections import defaultdict

WALL_HEIGHT = 300
PLAYER_HEIGHT = 32
FOV = math.pi / 2
W = 600
H = 600
VIEW_RANGE = 20
EMPTY = float('inf')
CIRCLE = 2 * math.pi


class Player(object):

    """Handles the player's position, rotation, and control."""

    def __init__(self, x, y, direction):
        """
        The arguments x and y are floating points.  Anything between zero
        and the game map size is on our generated map.
        Choosing a point outside this range ensures our player doesn't spawn
        inside a wall.  The direction argument is the initial angle (given in
        radians) of the player.
        This class was blatantley copied from: https://github.com/Mekire/pygame-raycasting-experiment
        """
        self.keys = defaultdict(list)
        self.x = x
        self.y = y
        self.direction = direction
        self.fov = FOV
        self.view = VIEW_RANGE
        self.speed = 3  # Map cells per second.
        self.rotate_speed = CIRCLE/2  # 180 degrees in a second.

    def rotate(self, angle):
        """Change the player's direction when appropriate key is pressed."""
        self.direction = (self.direction + angle + CIRCLE) % CIRCLE

    def walk(self, distance, game_map):
        """
        Calculate the player's next position, and move if he will
        not end up inside a wall.
        """
        dx = distance * math.sin(self.direction)
        dy = distance * math.cos(self.direction)
        map_x = (math.floor(self.x + dx), math.floor(self.y))
        if game_map.get(map_x, 1) <= 0:
            self.x += dx

        map_y = (math.floor(self.x), math.floor(self.y + dy))
        if game_map.get(map_y, 1) <= 0:
            self.y += dy

    def update(self, dt, game_map):
        """Execute movement functions if the appropriate key is pressed."""
        if self.keys[pg.K_RIGHT]:
            self.rotate(-self.rotate_speed * dt)
        if self.keys[pg.K_LEFT]:
            self.rotate(self.rotate_speed * dt)
        if self.keys[pg.K_UP]:
            self.walk(self.speed * dt, game_map)
        if self.keys[pg.K_DOWN]:
            self.walk(-self.speed * dt, game_map)


class Raycast:

    ''' A class to handle ray casting, and the required calculations.'''

    def __init__(self, width, height):
        ''' initialize the class with width and height.'''
        self.width = width
        self.height = height

    def cast_rays(self, player, map):
        ''' "Casts" rays and returns the distances from walls in the map as an array.
        Rays are calculated based on player's direction, where an angle of 0 is facing down.'''

        step_size = player.fov / (self.width - 1)
        walls = []
        # Calculate starting angle based on player's facing direction and FOV
        angle = (player.direction - player.fov / 2 + CIRCLE) % CIRCLE

        # For each pixel in width
        for _ in range(self.width):
            # Get the distance from the wall at given angle
            dist = self.cast_ray((player.x, player.y), angle, map, player.view)
            # Fix the bobeye effect based on the player's angle and append it.
            walls.append((dist[0] * math.cos(abs(player.direction - angle)), dist[1]))
            # Advance the angle one tick.
            angle = (angle + step_size) % CIRCLE

        return walls

    def cast_ray(self, start, angle, map, max_distance):
        ''' Cast an individual ray from start position at given angle.
            Return the distance from the closest wall.
            Return float('inf') if no wall is found with max distance'''

        def get_vertical(start, angle, map):
            x_orig, y_orig = start

            # Will be positive for angle <  pi/2 or  angle > 3pi / 2
            ydelta = math.cos(angle)

            if ydelta > 0:
                y_next = math.ceil(y_orig)
                y_step = 1
                dist_multiplier = 1  # Used to flip the sign of distance calculations
            else:
                y_next = math.floor(y_orig) - 0.001
                y_step = -1
                dist_multiplier = -1  # Used to flip the sign of distance calculations

            # Calculate next x, knowing that tan(angle) = dx-px / dy-py
            x_next = x_orig + (y_next - y_orig) * math.tan(angle)
            # Calculate step of x the same way.
            x_step = y_step * math.tan(angle)

            for _ in range(max_distance):

                # Get the tile at the given location (The floor of x and y)
                # Return a wall if nothing is found, to create an artifical border
                tile = map.get((math.floor(x_next), math.floor(y_next)), 1)

                if tile:
                    # Get the length of the y perpendicular
                    ydist = abs(y_next - y_orig)
                    # Calculate distance using cos(angle).
                    # Using the dist multiplier to correct the sign
                    return ydist * dist_multiplier / math.cos(angle)

                # Move to the next vertical intersection.
                x_next += x_step
                y_next += y_step

            # if no wall was found in range, return infinity
            return float('inf')

        def get_horizontal(start, angle, map):
            x_orig, y_orig = start
            #print('checking horizontally from ', x_orig, y_orig, 'at', angle*180/math.pi)

            # Will be positive for angle <  pi/2 or  angle > 3pi / 2
            xdelta = math.sin(angle)

            if xdelta > 0:
                x_next = math.ceil(x_orig)
                x_step = 1
                dist_multiplier = 1  # Used to flip the sign of distance calculations
            else:
                x_next = math.floor(x_orig) - 0.001
                x_step = -1
                dist_multiplier = -1  # Used to flip the sign of distance calculations

            # Calculate next y, knowing that tan(angle) = dx-px / dy-py
            y_next = y_orig + (x_next - x_orig) / math.tan(angle)
            # Calculate step of y the same way.
            y_step = x_step / math.tan(angle)

            for _ in range(max_distance):

                # Get the tile at the given location (The floor of x and y)
                # Return a wall if nothing is found, to create an artifical border
                tile = map.get((math.floor(x_next), math.floor(y_next)), 1)
                if tile:
                    # Get the length of the y perpendicular
                    xdist = abs(x_next - x_orig)
                    # Calculate distance using cos(angle).
                    # Using the dist multiplier to correct the sign
                    return xdist * dist_multiplier / math.sin(angle)

                # Move to the next vertical intersection.
                x_next += x_step
                y_next += y_step


            # if no wall was found in range, return infinity
            return float('inf')

        vertical = (get_vertical(start, angle, map), 0)
        horizontal = (get_horizontal(start, angle, map), 1)
        # Return the minimum distance
        #input()
        return min(vertical, horizontal)


def pygame_draw(screen, dists):
    screen.fill((0, 0, 0))
    floor = pg.Rect(0, H/2, W, H/2)
    pg.draw.rect(screen, (100, 100, 100), floor)
    width = 1
    side_alpha = 50
    color = (220, 210, 255)

    for idx, dist in enumerate(dists):
        if dist[0] == float('inf'):
            continue
        z = max(dist[0], WALL_HEIGHT / H)
        wall_height = WALL_HEIGHT / (z)
        top = H / 2 - wall_height / 2
        scale_rect = pg.Rect(W - idx, top, width, wall_height)
        next_color = tuple(i - side_alpha * dist[1] for i in color)
        pg.draw.rect(screen, next_color , scale_rect)
    pg.display.flip()


def main():
    pg.init()
    screen = pg.display.set_mode((W, H))
    map = Map.Random(20, 20, 0.3, (1, 1))
    p = Player(*map.start, direction=0)
    world = Raycast(W, H)
    map.pprint()
    clock = pg.time.Clock()
    p.direction = math.pi

    while True:
        dt = clock.tick() / 1000
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.KEYDOWN:
                p.keys[event.key] = True
            elif event.type == pg.KEYUP:
                p.keys[event.key] = False
        heights = world.cast_rays(p, map)
        p.update(dt, map)
        pygame_draw(screen, heights)
        #sleep(10)

    input()

if __name__ == '__main__':
    main()
    pg.quit()
