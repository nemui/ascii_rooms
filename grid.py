from dataclasses import dataclass
import heapq


@dataclass
class Position:
    x: int = 0
    y: int = 0

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)

    def __hash__(self):
        return hash((self.x, self.x))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __lt__(self, other):
        return (self.x, self.y) < (self.x, self.y)


ADJACENT_8 = [
    Position(-1, 0),
    Position(-1, -1),
    Position(0, -1),
    Position(1, -1),
    Position(1, 0),
    Position(1, 1),
    Position(0, 1),
    Position(-1, -1),
]


def adjacent_8_positions(position: Position):
    return [position + diff for diff in ADJACENT_8]


ADJACENT_4 = [
    Position(-1, 0),
    Position(0, -1),
    Position(1, 0),
    Position(0, 1)
]


def adjacent_4_positions(position: Position):
    return [position + diff for diff in ADJACENT_4]


class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []

    def in_bounds(self, pos: Position):
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def passable(self, pos: Position):
        return pos not in self.walls

    def neighbors(self, pos: Position):
        results = adjacent_4_positions(pos)
        # if (x + y) % 2 == 0: results.reverse()  # aesthetics
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def heuristic(pos1: Position, pos2: Position):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {start: 0}
    came_from[start] = None

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path
