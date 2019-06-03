import random
import textwrap
from dataclasses import dataclass
from typing import Dict, List

from grid import Position, adjacent_4_positions, SquareGrid, a_star_search, reconstruct_path


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


def generate_new_room():
    width = random.randint(MIN_SIZE, MAX_SIZE)
    height = random.randint(MIN_SIZE, MAX_SIZE)
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


def place_stairs(room: Room):
    room_half_width = int(room.width / 2)
    room_half_height = int(room.height / 2)
    stairs_x = random.randint(room_half_width - 1, room_half_width + 1)
    stairs_y = random.randint(room_half_height - 1, room_half_height + 1)
    room.entities[Position(stairs_x, stairs_y)].append(Entity(STAIRS_UP))


def find_entities(character, room: Room):
    return [key for key, val in room.entities.items() if len([en for en in val if en.character == character]) > 0]


def place_hero(character: str, room: Room):
    stairs_up_pos = find_entities(character, room)[0]
    stairs_adjacent = adjacent_4_positions(stairs_up_pos)
    stairs_adjacent_floor = [x for x in stairs_adjacent if x in room.entities and x not in room.grid.walls]
    room.entities[random.choice(stairs_adjacent_floor)].append(Entity(HERO))


def place_door(wall_index: int, character: str, room: Room):
    door_position = Position()
    # left
    if wall_index == 0:
        door_position.x = 0
        door_position.y = random.randint(1, room.height - 2)
    # top
    elif wall_index == 1:
        door_position.x = random.randint(1, room.width - 2)
        door_position.y = 0
    # right
    elif wall_index == 2:
        door_position.x = room.width - 1
        door_position.y = random.randint(1, room.height - 2)
    # bottom
    elif wall_index == 3:
        door_position.x = random.randint(1, room.width - 2)
        door_position.y = room.height - 1
    room.entities[door_position].pop(0)
    room.entities[door_position].append(Entity(character))
    room.grid.walls.remove(door_position)


def place_doors(count: int, walls: List[int], room: Room):
    doors_left = random.randint(1, count)

    while doors_left > 0:
        # pick a wall at random
        wall_index = random.choice(walls)
        walls.remove(wall_index)
        place_door(wall_index, DOOR_CLOSED, room)
        doors_left = doors_left - 1


def to_ascii(room: Room):
    result = ''
    for key in room.entities:
        result += str(room.entities[key][-1])
    return textwrap.fill(result, room.width)


def generate_room_from_scratch():
    room = generate_new_room()
    walls = list(range(4))
    place_doors(3, walls, room)
    place_stairs(room)
    place_hero(STAIRS_UP, room)
    return room


def generate_consecutive_room(exit: Position, prev_room: Room):
    room = generate_new_room()
    wall_index = 0
    print(exit)
    if exit.y == prev_room.height - 1:
        wall_index = 1
    elif exit.x == 0:
        wall_index = 2
    elif exit.y == 0:
        wall_index = 3

    place_door(wall_index, DOOR_OPEN, room)
    walls = list(range(4))
    walls.remove(wall_index)
    place_doors(2, walls, room)
    place_hero(DOOR_OPEN, room)
    return room


def generate_path(room: Room):
    doors_list = find_entities(DOOR_CLOSED, room)
    the_door = random.choice(doors_list)
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
    current = hero_path[0]
    next = hero_path[1]
    hero = room.entities[current].pop(len(room.entities[current]) - 1)
    room.entities[next].append(hero)
    hero_path.pop(0)
    return DIRECTIONS[next - current]


def open_door(door: Position, room: Room):
    room.entities[door].pop(0)
    room.entities[door].append(Entity(DOOR_OPEN))
