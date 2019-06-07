import random
from random import Random
import textwrap
from dataclasses import dataclass
from typing import Dict, List
from grid import Position, adjacent_4_positions, SquareGrid, a_star_search, reconstruct_path
from enum import Enum


MIN_SIZE = 5
MAX_SIZE = 9
WALL = '＃'
FLOOR = '＇'
HERO = '＠'
STAIRS_DOWN = '＞'
STAIRS_UP = '＜'
DOOR_CLOSED = '＋'
DOOR_OPEN = '＂'


@dataclass
class Entity:
    character: str

    def __str__(self):
        return f'{self.character}'


@dataclass
class Room:
    width: int
    height: int
    entities: Dict[Position, List[Entity]]
    grid: SquareGrid


class Wall(Enum):
    WEST = 1
    NORTH = 2
    EAST = 3
    SOUTH = 4

    def to_room_position(self, room: Room, generator: Random):
        position = Position()
        if self == Wall.WEST:
            position.x = 0
            position.y = generator.randint(1, room.height - 2)
        elif self == Wall.NORTH:
            position.x = generator.randint(1, room.width - 2)
            position.y = 0
        elif self == Wall.EAST:
            position.x = room.width - 1
            position.y = generator.randint(1, room.height - 2)
        elif self == Wall.SOUTH:
            position.x = generator.randint(1, room.width - 2)
            position.y = room.height - 1
        return position

    def opposite_wall(self):
        if self == Wall.WEST:
            return Wall.EAST
        elif self == Wall.NORTH:
            return Wall.SOUTH
        elif self == Wall.EAST:
            return Wall.WEST
        elif self == Wall.SOUTH:
            return Wall.NORTH

    @classmethod
    def from_room_position(cls, position: Position, room: Room):
        if position.x == 0:
            return cls.WEST
        elif position.y == 0:
            return cls.NORTH
        elif position.x == room.width - 1:
            return cls.EAST
        elif position.y == room.height - 1:
            return cls.SOUTH
        return None


def generate_new_room(generator: Random):
    width = generator.randint(MIN_SIZE, MAX_SIZE)
    height = generator.randint(MIN_SIZE, MAX_SIZE)
    room_grid = SquareGrid(width, height)
    entities = {}
    for y in range(0, height):
        for x in range(0, width):
            if y == 0 or x == 0 or y == height - 1 or x == width - 1:
                wall_pos = Position(x, y)
                entities[wall_pos] = [Entity(WALL)]
                room_grid.walls.append(wall_pos)
            else:
                entities[Position(x, y)] = [Entity(FLOOR)]
    return Room(width, height, entities, room_grid)


def place_stairs(room: Room, generator: Random):
    room_half_width = int(room.width / 2)
    room_half_height = int(room.height / 2)
    stairs_x = generator.randint(room_half_width - 1, room_half_width + 1)
    stairs_y = generator.randint(room_half_height - 1, room_half_height + 1)
    room.entities[Position(stairs_x, stairs_y)].append(Entity(STAIRS_UP))


def find_entities(character, room: Room):
    return [key for key, val in room.entities.items() if len([en for en in val if en.character == character]) > 0]


def place_hero_initially(character: str, room: Room, generator: Random):
    stairs_up_pos = find_entities(character, room)[0]
    stairs_adjacent = adjacent_4_positions(stairs_up_pos)
    stairs_adjacent_floor = [x for x in stairs_adjacent if x in room.entities and x not in room.grid.walls]
    room.entities[generator.choice(stairs_adjacent_floor)].append(Entity(HERO))


def place_hero_near_the_stairs(room: Room, generator: Random):
    place_hero_initially(STAIRS_UP, room, generator)


def place_hero_near_the_door(room: Room, generator: Random):
    place_hero_initially(DOOR_OPEN, room, generator)


def place_door(wall: Wall, character: str, room: Room, generator: Random):
    door_position = wall.to_room_position(room, generator)
    room.entities[door_position].pop(0)
    room.entities[door_position].append(Entity(character))
    room.grid.walls.remove(door_position)


def place_doors(count: int, walls: List[Wall], room: Room, generator: Random):
    doors_left = generator.randint(1, count)

    while doors_left > 0:
        # pick a wall at random
        wall_index = generator.choice(walls)
        walls.remove(wall_index)
        place_door(wall_index, DOOR_CLOSED, room, generator)
        doors_left = doors_left - 1


def to_ascii(room: Room):
    result = ''
    for key in room.entities:
        result += str(room.entities[key][-1])
    return textwrap.fill(result, room.width)


def generate_room_from_scratch(generator: Random):
    room = generate_new_room(generator)
    walls = [wall for wall in Wall]
    place_doors(3, walls, room, generator)
    place_stairs(room, generator)
    return room


def generate_consecutive_room(entrance: Wall, generator: Random):
    room = generate_new_room(generator)
    place_door(entrance, DOOR_OPEN, room, generator)
    walls = [wall for wall in Wall]
    walls.remove(entrance)
    place_doors(2, walls, room, generator)
    return room


def generate_path(room: Room, generator: Random):
    doors_list = find_entities(DOOR_CLOSED, room)
    the_door = generator.choice(doors_list)
    hero = find_entities(HERO, room)[0]
    (came_from, cost_so_far) = a_star_search(room.grid, hero, the_door)
    return reconstruct_path(came_from, hero, the_door)


DIRECTIONS = {
    Position(-1, 0): 'west',
    Position(0, -1): 'north',
    Position(1, 0): 'east',
    Position(0, 1): 'south'
}


def move_hero(hero_path: List[Position], room: Room):
    current_position = hero_path[0]
    next_position = hero_path[1]
    hero = room.entities[current_position].pop(len(room.entities[current_position]) - 1)
    room.entities[next_position].append(hero)
    hero_path.pop(0)
    return DIRECTIONS[next_position - current_position]


def place_hero(position: Position, room: Room):
    room.entities[position].append(Entity(HERO))


def open_door(door: Position, room: Room):
    room.entities[door].pop(0)
    room.entities[door].append(Entity(DOOR_OPEN))
